import tree_sitter
from tree_sitter_languages import get_parser
from .CircuitElement import *
from .Interpreter import *
from ..Main.DealDat import *
import json
import os

from ..Setting import ModelingSettings
from ...Tools.ExpandedCVC5 import ExpandedCVC5


class CPPModeler:
    def __init__(self, cpp_path: str, dat_path: str, solver: ExpandedCVC5, cpp_json_path: str=None):
        self.solver = solver
        self.P = solver.prime()
        self.Rr = solver.Rr()

        with open(cpp_path, "rb") as f:
            src = f.read()

        parser = get_parser("cpp")
        tree = parser.parse(src)

        self.__ast_json = self.__node_to_dict(tree.root_node)

        if ModelingSettings.RECORD_CPP_JSON:
            if cpp_json_path is not None:
                with open(cpp_json_path, "w", encoding="utf-8") as f:
                    json.dump(self.__ast_json, f, ensure_ascii=False, indent=2)

        self.cppTerms = list()
        self.signalList = list()
        self.circuitConstants = list()
        self.functionTable = None 
        self.templateInsId2IOSignalInfo = None
        self.listOfTemplateMessages = list() # circom log
        # self.templateInsId2IOSignalInfo: dict[int, IODefPair] = {}
        self.init_function_data()
        self.init_signal_data()
        self.init_data(dat_path)
        self.init_component_memory()
        self.init_function_table()
        self.interpreter = Interpreter(self)

    def mk_signal_assignment_trem(self, signal: CPPSignal, value):
        term = self.solver.mkFFTerm_Eq(signal.toSmt(), value)
        self.cppTerms.append(term)

    def add_term(self, term):
        self.cppTerms.append(term)

    def build(self):
        self.interpreter.run_simulation()

    def get_terms(self):
        return self.cppTerms

    def get_signals(self):
        return self.signalList

    def init_signal_data(self):
        if not self.functionDict:
            print("warning: Please run init_function_data() before init_signal_data().")
            return

        total_signals = self._get_return_value_from_function('get_total_signal_no', 0)
        input_start = self._get_return_value_from_function('get_main_input_signal_start', 0)
        input_count = self._get_return_value_from_function('get_main_input_signal_no', 0)


        self.signalList = list()
        CPPSignal.set_solver(self.solver)
        for i in range(total_signals):
            is_input = False
            if input_start <= i < input_start + input_count:
                is_input = True
            signal = CPPSignal(i, is_input, self)
            self.signalList.append(signal)


    def init_data(self, dat_path: str):
        hash_num = self._get_return_value_from_function("get_size_of_input_hashmap", 0)
        witness_num = self._get_return_value_from_function("get_size_of_witness", 0)
        constant_num = self._get_return_value_from_function("get_size_of_constants", 0)
        io_map_size = self._get_return_value_from_function("get_size_of_io_map", 0)
        constantList, templateInsId2IOSignalInfo = deal_dat(dat_path, hash_num, witness_num, constant_num, io_map_size, self.P, self.Rr)
        for value in constantList:
            constant = CPPConstant(value)
            self.circuitConstants.append(constant)
        self.templateInsId2IOSignalInfo = templateInsId2IOSignalInfo
        # print(self.templateInsId2IOSignalInfo)

    def init_component_memory(self):
        if not self.functionDict:
            print("warning: Please run init_function_data() before init_component_memory().")
            return

        num_components = self._get_return_value_from_function('get_number_of_components', 0)
    
        self.componentMemory = [None] * num_components
        # print(f"init componentMemory with size {num_components}")
        # print(self.componentMemory)
    
    def init_function_table(self):
        if not self.__ast_json:
            print("AST JSON not available for _functionTable parsing.")
            return

        for top_level_node in self.__ast_json.get("children", []):
            if top_level_node.get("type") == "declaration":
                

                init_declarator = self._find_node_by_type(top_level_node, "init_declarator")
                if not init_declarator:
                    continue
                array_declarator = self._find_node_by_type(init_declarator, "array_declarator")
                if not array_declarator:
                    continue
                
                identifier_node = self._find_node_by_type(array_declarator, "identifier")
        
                if identifier_node and identifier_node.get("text") == "_functionTable":
                    initializer_list = self._find_node_by_type(init_declarator, "initializer_list")
                    
                    if initializer_list:
                        func_names = []
                        for item_node in initializer_list.get("children", []):
                            if item_node.get("type") == "identifier":
                                func_names.append(item_node.get("text"))
                        
                        self.functionTable = func_names
                        # print(f"init functionTable with size {len(self.functionTable)}, functions: {self.functionTable}")
                        return

    def _get_return_value_from_function(self, func_name: str, default_value: int) -> int:
        func_node = self.functionDict.get(func_name)
        if not func_node:
            print(f"fail to get return value from function '{func_name}', use default {default_value}")
            return default_value

        return_value_node = self._find_return_value(func_node)
        if return_value_node and return_value_node.get("type") == "number_literal":
            try:
                return int(return_value_node.get("text", str(default_value)))
            except (ValueError, TypeError):
                return default_value
        return default_value

    def _find_main_component_soffset(self) -> int | None:
        run_node = self.functionDict.get('run')
        if not run_node:
            return None

        create_call_node = self._find_node_by_type(run_node, "call_expression")
        if create_call_node:

            children = create_call_node.get("children", [])
            if len(children) > 1 and children[1].get("type") == "argument_list":
                arg_list = children[1].get("children", [])

                args = [arg for arg in arg_list if arg.get("is_named")]
                if args and args[0].get("type") == "number_literal":
                    try:
                        return int(args[0].get("text"))
                    except (ValueError, TypeError):
                        return None
        return None

    def _find_node_by_type(self, start_node: dict, target_type: str) -> dict | None:

        if start_node is None: return None
        if start_node.get("type") == target_type:
            return start_node
        for child in start_node.get("children", []):
            found = self._find_node_by_type(child, target_type)
            if found: return found
        return None

    def _find_return_value(self, node_json: dict) -> dict | None:
        if node_json is None: return None
        if node_json.get("type") == "return_statement":
            children = node_json.get("children", [])
            if len(children) > 1 and children[0].get("type") == "return":
                return children[1]
            elif len(children) > 0:
                return children[0]
        for child in node_json.get("children", []):
            found_node = self._find_return_value(child)
            if found_node: return found_node
        return None

    def __node_to_dict(
        self,
        node: tree_sitter.Node,
        *, 
        include_positions: bool = False,
        include_is_named: bool = True,
        include_text_for_leaf_nodes: bool = True
    ) -> dict:
        """
        Recursive function to convert a tree-sitter AST node into a JSON-compatible dictionary.
        
        Args:
            node: The tree-sitter node to convert.
            include_positions: Whether to include start_point and end_point in the output.
            include_is_named: Whether to include the is_named field in the output.
            include_text_for_leaf_nodes: Whether to add a text field for leaf nodes (nodes without children).
        
        Returns:
            A dictionary representing the node.
        """

        result = {
            "type": node.type,
            # "byte_range": node.byte_range,
            "child_count": node.child_count,
            # "children": node.children,
            # "descendant_count": node.descendant_count,
            # "end_byte": node.end_byte,
            # "end_point": node.end_point,
            # "grammar_id": node.grammar_id,
            # "grammar_name": node.grammar_name,
            # "has_changes": node.has_changes,
            # "has_error": node.has_error,
            # "id": node.id,
            # "is_error": node.is_error,
            # "is_extra": node.is_extra,
            # "is_missing": node.is_missing,
            # "is_named": node.is_named,
            # "kind_id": node.kind_id,
            "named_child_count": node.named_child_count,
            # "named_children": node.named_children,
            # "next_named_sibling": node.next_named_sibling,
            # "next_parse_state": node.next_parse_state,
            # "next_sibling": node.next_sibling,
            # "parent": node.parent,
            # "parse_state": node.parse_state,
            # "prev_named_sibling": node.prev_named_sibling,
            # "prev_sibling": node.prev_sibling,
            # "range": node.range,
            # "start_byte": node.start_byte,
            # "start_point": node.start_point,
            "text": node.text.decode('utf8', 'ignore'),
        }

        if include_is_named:
            result["is_named"] = node.is_named
            # if not node.is_named:
            #     return None

        if include_positions:
            result["start_point"] = node.start_point
            result["end_point"] = node.end_point

        if node.children:
            recursive_call = lambda n: self.__node_to_dict(
                n,
                include_positions=include_positions,
                include_is_named=include_is_named,
                include_text_for_leaf_nodes=include_text_for_leaf_nodes
            )
            result["children"] = [recursive_call(child) for child in node.children]
        elif include_text_for_leaf_nodes:
            result["text"] = node.text.decode('utf8', 'ignore')
                
        return result

    def init_function_data(self):
        self.functionDict = dict()
        if self.__ast_json:
            self._traverse_for_functions(self.__ast_json)
        else:
            print("AST JSON is empty, cannot init function data. Please run buildCPP first.")
        # print(self.functionDict)

    def _traverse_for_functions(self, node_json):

        if node_json is None:
            return

        if node_json.get("type") == "function_definition":
            function_name = None
            for child in node_json.get("children", []):
                if child and child.get("type") == "function_declarator":
                    for decl_child in child.get("children", []):
                        if decl_child and decl_child.get("type") == "identifier":
                            function_name = decl_child.get("text")
                            break
                if function_name:
                    break
            
            if function_name:
                self.functionDict[function_name] = node_json

        for child in node_json.get("children", []):
            self._traverse_for_functions(child)

    def saveCPPData(self, CPP_path: str):
        dir_name = os.path.basename(os.path.dirname(CPP_path))
        output_dir = os.path.join(os.path.dirname(CPP_path), dir_name)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{dir_name}{len(os.listdir(output_dir))+1}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            # print(output_file)
            json.dump(self.__ast_json, f, ensure_ascii=False, indent=2)
        print("CPP AST is saved!")

    def __str__(self):
        return 'CPPModeler'


if __name__ == '__main__':
    exp_slv = ExpandedCVC5('bn128')
    ModelingSettings.CIRCOM_VERSION = '2.2.2'

    P = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    Rr = 9915499612839321149637521777990102151350674507940716049588462388200839649614

    cpp_path = './../../temp_file/Pedersen@pedersen_old@circomlib_8/Pedersen@pedersen_old@circomlib_8_cpp/Pedersen@pedersen_old@circomlib_8.cpp'
    dat_path = './../../temp_file/Pedersen@pedersen_old@circomlib_8/Pedersen@pedersen_old@circomlib_8_cpp/Pedersen@pedersen_old@circomlib_8.dat'

    cppModeler = CPPModeler(cpp_path, dat_path, exp_slv)

    cppModeler.build()

    for term in cppModeler.cppTerms:
        print(term)

    pass