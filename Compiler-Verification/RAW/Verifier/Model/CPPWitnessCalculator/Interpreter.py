from typing import Any
import json

import cvc5

from . import CPPModeler
from .CPPBuildinWords import CPPBuildinWords
from .CircuitElement import CPPSignal, CircuitElement
from .ComponentMemory import ComponentMemory
from .ModelingState import ModelingState
from .SimulatedPointer import SimulatedPointer
from ..Setting import ModelingSettings
from ..Main.OperatorSemantics import calculate_deterministic_infixOp, calculate_deterministic_prefixOp, generate_infix_term, generate_prefix_term


class Interpreter:
    def __init__(self, modeler_context: CPPModeler):
        """
        Args:
                             a context object that contains global information... expected to be a CPPModeler instance itself,
                                from which .signalList, .constantList, .functionDict, etc. can be accessed.
        """
        self.modeler_context: CPPModeler = modeler_context
        self._param_cache = {}
        # self.run_when_create = False
        self.context_functions = {
            # for cpp library functions and circom built-in functions
            "generate_position_array",
        }

    def run_simulation(self):
        run_func_node = self.modeler_context.functionDict['run']
        if not run_func_node:
            print("error: 'run' function entry point not found.")
            return []
        initial_state = ModelingState(is_function_root=True, name='run')
        body = self._find_node_by_type(run_func_node, "compound_statement")
        # if body['children'][2].get("type") == "comment":
        #     self.run_when_create = True
        # print(f"current cppsignals: {self.modeler_context.get_signals()}")
        self.execute_node(body, initial_state)

    def execute_node(self, node: dict, state: ModelingState, if_log: bool = False) -> None:
        """General dispatcher: Calls the corresponding execute_ method to handle statements based on node type."""
        if not node or not node.get("is_named", True):
            return

        node_type = node.get("type")

        # handler_map = {
        #     "compound_statement": self.execute_compound_statement,
        #     "expression_statement": self.execute_expression_statement,
        #     "declaration": self.execute_declaration,
        #     "for_statement": self.execute_for_statement,
        #     "if_statement": self.execute_if_statement,
        #     "return_statement": self.execute_return_statement,
        # }

        # handler = handler_map.get(node_type)
        if node_type == "compound_statement":
            if if_log:
                print(f"DEBUG: go compound_statement")
            self.execute_compound_statement(node, state, if_log)
        elif node_type == "expression_statement":
            if if_log:
                print(f"DEBUG: go expression_statement")
            self.execute_expression_statement(node, state)
        elif node_type == "declaration":
            if if_log:
                print(f"DEBUG: go declaration")
            self.execute_declaration(node, state, if_log)
        elif node_type == "for_statement":
            if if_log:
                print(f"DEBUG: go for_statement")
            self.execute_for_statement(node, state)
        elif node_type == "while_statement":
            if if_log:
                print(f"DEBUG: go while_statement")
            self.execute_while_statement(node, state)
        elif node_type == "if_statement":
            if if_log:
                print(f"DEBUG: go if_statement")
            self.execute_if_statement(node, state, if_log)
        elif node_type == "return_statement":
            if if_log:
                print(f"DEBUG: go return_statement")
            self.execute_return_statement(node, state)
        elif node_type == "ERROR":
            print(f"ERROR: {node.get('text')}")
        elif node_type == "comment":
            pass
        else:
            raise NotImplementedError(f"Statement type '{node_type}' is not implemented.")

    def evaluate_expression(self, node: dict, state: ModelingState, if_log: bool = False):
        """Calculate dispatcher: Calls the corresponding evaluate_ method to handle expressions based on node type."""
        if not node: return None
        node_type = node.get("type")

        result = None

        if node_type == "assignment_expression":
            if if_log:
                print(f"DEBUG: go assignment_expression")
            result = self.evaluate_assignment(node, state, if_log)
        elif node_type == "binary_expression":
            if if_log:
                print(f"DEBUG: go binary_expression")
            result = self.evaluate_binary_expression(node, state, if_log)
        elif node_type == "unary_expression":
            if if_log:
                print(f"DEBUG: go unary_expression")
            result = self.evaluate_unary_expression(node, state, if_log)
        elif node_type == "update_expression":
            if if_log:
                print(f"DEBUG: go update_expression")
            result = self.evaluate_update_expression(node, state, if_log)
        elif node_type == "call_expression":
            if if_log:
                print(f"DEBUG: go call_expression")
            result = self.evaluate_function_call(node, state, if_log)
        elif node_type == "field_expression":
            if if_log:
                print(f"DEBUG: go field_expression")
            result = self.evaluate_field_expression(node, state, if_log)
        elif node_type == "subscript_expression":
            if if_log:
                print(f"DEBUG: go subscript_expression")
            result = self.evaluate_subscript_expression(node, state, if_log)
        elif node_type == "new_expression":
            if if_log:
                print(f"DEBUG: go new_expression")
            result = self.evaluate_new_expression(node, state, if_log)
        elif node_type == "pointer_expression":
            if if_log:
                print(f"DEBUG: go pointer_expression")
            result = self.evaluate_pointer_expression(node, state, if_log)
        elif node_type == "parenthesized_expression":
            if if_log:
                print(f"DEBUG: go parenthesized_expression")

            named_children = [c for c in node.get("children", []) if c.get("is_named")]

            if (len(named_children) == 2 and
                named_children[0].get("type") == "field_expression" and
                named_children[1].get("type") == "ERROR"):
                
                lhs_node = named_children[0]
                error_node = named_children[1]
                
                error_children = error_node.get("children", [])
                # print("tree-sitter error handling triggered")
                if len(error_children) >= 2:
                    op_node = error_children[0] 
                    rhs_node = error_children[1]

                    corrected_assignment_node = {
                        "type": "assignment_expression",
                        "children": [lhs_node, op_node, rhs_node]
                    }
                    
                    return self.evaluate_assignment(corrected_assignment_node, state, if_log)
            result = self.evaluate_expression(node['children'][1], state, if_log)

        elif node_type == "conditional_expression":
            if if_log:
                print(f"DEBUG: go conditional_expression")
            result = self.evaluate_conditional_expression(node, state, if_log)  
        elif node_type == "initializer_list":
            if if_log:
                print(f"DEBUG: go initializer_list")
            result = self.evaluate_initializer_list(node, state, if_log)

        # atomic_expression
        elif node_type == "identifier":
            if if_log:
                print(f"DEBUG: go identifier")
            result = self.evaluate_identifier(node, state, if_log)
        elif node_type == "number_literal":
            if if_log:
                print(f"DEBUG: go number_literal")
            result = int(node.get("text"))
        elif node_type == "string_literal":
            if if_log:
                print(f"DEBUG: go string_literal")
            # result = self._find_child_by_type(node, "string_content").get("text")
            result = node.get('text').strip('"')
        # irrelevants
        elif node_type == "delete_expression":
            if if_log:
                print(f"DEBUG: go delete_expression")
            result = None
        elif node_type == "null":
            if if_log:
                print(f"DEBUG: go null")
            result = None
        else:
            raise Exception(f"Unknown node type: {node_type}")

        return result

    def execute_compound_statement(self, node: dict, state: ModelingState, if_log: bool = False):
        """
        { statement1; statement2; ... }
        """
        # if-else
        # # print(f"DEBUG: Entering compound_statement for node: {node.get('text', 'No text')}......")
        # print("---------------------------------")
        for i, child in enumerate(node['children']):
            if not child.get('is_named'):
                continue
            # # print(f"DEBUG: Executing child {i} of type {child.get('type')}: {child.get('text', 'No text')[:50]}...")
            self.execute_node(child, state, if_log)
        # # print(f"DEBUG: Exiting compound_statement.")
        # print("---------------------------------")

    def execute_expression_statement(self, node: dict, state: ModelingState, if_log: bool = False):
        """expr;"""
        children = node['children']
        for child in children:
            if child['is_named']:
                self.evaluate_expression(child, state, if_log)

    def execute_declaration(self, node: dict, state: ModelingState, if_log: bool = False):
        """
        process variable or array declarations, with improved support for pointers and complex declarations.
        
        options:
        - simple variable initialization: `uint myVar = value;`
        - pointer variable initialization: `FrElement* ptr = &signalValues[0];`
        - array declaration: `FrElement expaux[2];`
        - declaration without initialization: `uint myVar;`
        """
        
        # 1. Find the core declarator node.
        #    it could be init_declarator, array_declarator, identifier, or pointer_declarator
        declarator = next((c for c in node.get("children", []) if c.get("is_named") and c.get("type").endswith("declarator")), None)

        if not declarator:
            declarator = next((c for c in node.get("children", []) if c.get("type") == "identifier"), None)
            return

        declarator_type = declarator.get("type")
        var_name = None
        initial_value = None

        if declarator_type == "init_declarator":
            # [lhs_declarator, '=', rhs_expression]
            lhs_declarator = declarator["children"][0]
            rhs_node = declarator["children"][2]

            var_name = self._get_var_name_from_declarator(lhs_declarator)
            initial_value = self.evaluate_expression(rhs_node, state)

        elif declarator_type == "array_declarator":
            # FrElement expaux[2];
            var_name = self._get_var_name_from_declarator(declarator)
            size_node = declarator["children"][2] # [identifier, '[', size_node, ']']

            array_size = int(size_node.get("text"))

            initial_value = [0] * array_size

        elif declarator_type in ["identifier", "pointer_declarator"]:
            # uint i; or Circom_CalcWit* ctx;
            var_name = self._get_var_name_from_declarator(declarator)
            initial_value = None

        else:
            raise NotImplementedError(f"unsupported type: '{declarator_type}'")

        # 3. obtain var_name from declarator and store it in the current state
        if var_name:
            if var_name == 'expaux':
                state.set_expaux(initial_value)
            elif var_name == 'lvar':
                state.set_lvar(initial_value)
            else:
                state.define_local_var(var_name, initial_value)
        
        if if_log:
            print(f"DEBUG: go declaration, var_name: {var_name}, initial_value: {initial_value}")

    def execute_for_statement(self, node: dict, state: ModelingState, if_log: bool = False):
        """
        for (initializer; condition; update) { body }
        """
        children = [c for c in node.get("children", []) if c.get("is_named")]
        init_node, cond_node, update_node, body_node = children

        # loop_state = state.fork(name='for_loop')

        self.execute_node(init_node, state)

        for _ in range(ModelingSettings.MAX_LOOP_DEPTH):
            condition_result = self.evaluate_expression(cond_node, state)
            if isinstance(condition_result, cvc5.Term):
                raise TypeError(
                    f"error: for loop condition: '{cond_node.get('text')}' "
                    f"expression condition is not supported"
                )

            if not isinstance(condition_result, bool):
                raise TypeError(
                    f"error: for loop condition: '{cond_node.get('text')}' "
                    f"condition is not a Boolean"
                )

            if condition_result:
                self.execute_node(body_node, state)
                self.evaluate_expression(update_node, state)
            else:
                return

        raise RecursionError(f"error: for loop exceeds maximum iteration ({ModelingSettings.MAX_LOOP_DEPTH})")


    def execute_while_statement(self, node: dict, state: ModelingState):
        """
        while (condition) { body }
        """
        # 1. parse out the condition clause and body statement
        named_children = [c for c in node.get("children", []) if c.get("is_named")]
        if len(named_children) < 2:
            raise ValueError(f"Invalid while_statement structure: {named_children}")
        
        condition_clause_node = named_children[0]
        body_node = named_children[1]

        condition_expression_node = condition_clause_node['children'][1]

        # 2. Loop until the condition is false
        for _ in range(ModelingSettings.MAX_LOOP_DEPTH):
            # 2.1 check the condition
            condition_result = self.evaluate_expression(condition_expression_node, state, False)
            # # print(f"DEBUG: while_cond: {condition_expression_node.get('text')}, value: {condition_result}")
            # 2.2 check the condition type
            if isinstance(condition_result, cvc5.Term):
                raise TypeError(
                    f"error: while loop condition: '{condition_expression_node.get('text')}' "
                    f"is not a Boolean expression, which may cause path explosion."
                )
            if not isinstance(condition_result, bool):
                raise TypeError(
                    f"error: while loop condition: '{condition_expression_node.get('text')}' "
                    f"condition is not a Boolean."
                )

            if condition_result:
                self.execute_node(body_node, state, False)
            else:
                return
        raise RecursionError(f"error: while loop exceeds maximum iteration ({ModelingSettings.MAX_LOOP_DEPTH})")

    def execute_if_statement(self, node: dict, state: ModelingState, if_log: bool = False):
        children = node['children']
        have_else = len(children) > 3
        if_node = children[2]
        condition_clause = children[1]
        condition_term = self.evaluate_expression(condition_clause["children"][1], state, if_log)
        # print(f"DEBUG: if_cond: {condition_clause.get('text')}, value: {condition_term}")
        if isinstance(condition_term, bool):
            if condition_term:
                # self.execute_node(if_node["children"][1], state)
                self.execute_node(if_node, state, False)
            elif have_else:
                else_node = children[3]
                # self.execute_node(else_node["children"][1], state)
                self.execute_node(else_node["children"][1], state, False)
        else:
            if_cond = condition_term
            else_cond = self.modeler_context.solver.mkBool_Not(if_cond)
            if_state = state.fork(name='if_branch')
            if have_else:
                else_node = children[3]
                else_state = state.fork(name='else_branch')
                self.execute_node(if_node["children"][1], if_state, False)
                self.execute_node(else_node["children"][1], else_state, False)
                self._merge_if_else_states(if_state, else_state, state, if_cond, else_cond)
            else:
                self.execute_node(if_node["children"][1], if_state, False)
                self._merge_if_else_states(if_state, state, state, if_cond, else_cond)

    # if there's no else branch, father is treated as the else branch state
    # currently only merge lvar and expaux, other things should be generated on the fly or unchanged, of course some checks can be done here
    def _merge_if_else_states(self, if_s, else_s, father, if_cond, else_cond):
        if not ModelingSettings.IF_UNDEFINED_BEHAVIOR:
            if if_s.assigned_signals != else_s.assigned_signals:
                raise SyntaxError('Assignment for in If-Then-Else will leads to undefined behavior')

        merged_lvar = self._merge_array(if_s.get_lvar(), else_s.get_lvar(), if_cond, else_cond)
        father.set_lvar(merged_lvar, is_merging=True)
        if ModelingSettings.CPP_MORE_MERGE:
            merged_expaux = self._merge_array(if_s.get_expaux(), else_s.get_expaux(), if_cond, else_cond)
            father.set_expaux(merged_expaux, is_merging=True)

        # merge deferred_writes
        all_written_locations = set(if_s.deferred_writes.keys()) | set(else_s.deferred_writes.keys())

        NO_WRITE = object()
        
        for container_name, key in all_written_locations:
            # 1. container and original item
            container = None
            if container_name == "signalValues":
                container = self.modeler_context.signalList
            elif container_name == "componentMemory":
                container = self.modeler_context.componentMemory
            elif container_name == "circuitConstants":
                container = self.modeler_context.constantList
            else:
                try:
                    container = father.get_local_var(container_name)
                except KeyError:
                    raise KeyError(f"container {container_name} can't be found in current field")

            original_item = container[key]
            
            # 2. get the written values in if/else branches
            val_if = if_s.deferred_writes.get((container_name, key), NO_WRITE)
            val_else = else_s.deferred_writes.get((container_name, key), NO_WRITE)

            if val_if is NO_WRITE and val_else is NO_WRITE:
                continue

            # 3. merge the written values
            final_val_if = None
            final_val_else = None
            is_originally_assigned = not (isinstance(original_item, CPPSignal) and not original_item._CPPSignal__is_assigned)

            if val_if is not NO_WRITE and val_else is not NO_WRITE:
                final_val_if = val_if
                final_val_else = val_else
            
            elif val_if is NO_WRITE:
                final_val_else = val_else
                if is_originally_assigned:
                    final_val_if = self.get_value_from_ref(original_item, father)
                else:
                    if ModelingSettings.IF_UNDEFINED_BEHAVIOR:
                        final_val_if = 0
                    else:
                        raise ValueError(f"if branch has no written value, but the original item {original_item} is not assigned.")

            elif val_else is NO_WRITE:
                final_val_if = val_if
                if is_originally_assigned:
                    final_val_else = self.get_value_from_ref(original_item, father)
                else:
                    if ModelingSettings.IF_UNDEFINED_BEHAVIOR:
                        final_val_else = 0
                    else:
                        raise ValueError(f"else branch has no written value, but the original item {original_item} is not assigned.")

            # 4. merge the values
            merged_value, term = self.modeler_context.solver.mergeIfElseValue(final_val_if, final_val_else, if_cond, else_cond)
            if term: self.modeler_context.add_term(term)

            # 5. assign the merged value to the original item
            if isinstance(original_item, CPPSignal):
                original_item.assign_value(merged_value)
            else:
                container[key] = merged_value

    def _merge_array(self, arrayA, arrayB, if_cond, else_cond):
        if len(arrayA) != len(arrayB):
            raise TypeError('can not merge two array with different length!')

        def same_obj_or_value(x, y):
            # int/str/float/tuple/bool
            if isinstance(x, (int, float, str, bool, tuple)):
                return x == y
            else:
                return x is y

        outcome = list()
        for i in range(len(arrayA)):
            a = arrayA[i]
            b = arrayB[i]
            if same_obj_or_value(a, b):
                outcome.append(a)
            else:
                result, term = self.modeler_context.solver.mergeIfElseValue(a, b, if_cond, else_cond)
                outcome.append(result)
                self.modeler_context.add_term(term)
        return outcome


    def _execute_generate_position_array(self, arg_values: list, state: ModelingState) -> str:
        if len(arg_values) != 3:
            raise TypeError("generate_position_array expects 3 arguments.")

        linear_index = self.get_value_from_ref(arg_values[2], state)

        if not isinstance(linear_index, int):
            raise TypeError(f"The index for generate_position_array must be a concrete integer, not {type(linear_index)}")

        return f"[{linear_index}]"

    def _execute_function_body(self, func_def_node: dict, arg_map: dict, caller_state: ModelingState):
        """
        general dispatcher for function execution
        """
        func_name = func_def_node['children'][1]['children'][0]['text']
        function_state = caller_state.fork(is_function_root=True, arg_map=arg_map, name=func_name)

        body_node = self._find_node_by_type(func_def_node, "compound_statement")
        if not body_node:
            raise ValueError(f"Function {func_name} has no body.")
        try:
            if func_name.endswith("_create"):
                # if if_log:
                self._execute_create_function(body_node, function_state)
            elif func_name.endswith('_run'):
                self._execute_run_function(body_node, function_state)
                # print(func_name + " executed.")
            else:
                self._execute_plant_function(body_node, function_state)    
        except ReturnException as e:
            return e.value

    def _execute_create_function(self, body_node: dict, state: ModelingState):
        children = body_node['children']

        templateId = self.evaluate_expression(children[1]['children'][0]['children'][2], state)
        templateName = self.evaluate_expression(children[2]['children'][0]['children'][2], state)
        signalStart = state.get_local_var('soffset')
        inputCounter = self.evaluate_expression(children[4]['children'][0]['children'][2], state)
        componentName = state.get_local_var('componentName')
        idFather = state.get_local_var('componentFather')
        subcomponents = self.evaluate_expression(children[7]['children'][0]['children'][2], state)

        coffset = state.get_local_var('coffset')

        new_component = ComponentMemory(templateId, templateName, signalStart, inputCounter, componentName, idFather, subcomponents)
        # print(f"DEBUG: create component{componentName}, template {templateName}, signalStart {signalStart}, inputCounter {inputCounter}, subcomponents {subcomponents}")
        self.modeler_context.componentMemory[coffset] = new_component

        # if self.run_when_create:
        #     self.execute_node(children[8], state)
        #     self.run_when_create = False

        if state.get_father().name == 'run' and ModelingSettings.old_version():
            return

        named_children = [c for c in children if c.get("is_named")]
    
        if len(named_children) > 7:
            next_statement_node = named_children[7]

            if next_statement_node.get("type") == "expression_statement":
                call_expr_node = self._find_node_by_type(next_statement_node, "call_expression")
                
                if call_expr_node:
                    func_name_node = call_expr_node['children'][0]
                    if func_name_node.get("type") == "identifier" and func_name_node.get("text").endswith("_run"):
                        # print(f"DEBUG: finded _run call in _create: {next_statement_node.get('text')}")
                        self.execute_node(next_statement_node, state)

    def _execute_run_function(self, body_node: dict, state: ModelingState):
        for node in body_node.get("children", []):
            if node.get("type") == "declaration":
                self.execute_declaration(node, state)

        ctx_index = state.get_local_var('ctx_index')
        componentMemory = self.modeler_context.componentMemory[ctx_index]
        state.define_local_var('mySignalStart', componentMemory.signalStart)
        state.define_local_var('myTemplateName', componentMemory.templateName)
        state.define_local_var('myComponentName', componentMemory.componentName)
        state.define_local_var('myFather', componentMemory.idFather)
        state.define_local_var('myId', ctx_index)
        state.define_local_var('mySubcomponents', componentMemory.subcomponents)

        if not ModelingSettings.old_version():
            try:
                state.get_local_var('cmp_index_ref_load')
            except:
                state.define_local_var('cmp_index_ref_load', -1)

        for node in body_node.get("children", []):
            if not node.get("is_named") or node.get("type") == "declaration":
                continue
            is_component_instantiation = False

            # 2.1.8: create components in for loop
            if ModelingSettings.old_version() and node.get("type") == "for_statement":
                call_expr = self._find_nodes_by_type_recursive(node, "call_expression")
                if call_expr and call_expr[0]['children'][0]['text'].endswith("_create"):
                    is_component_instantiation = True

            # 2.2.2: call _create in compound_statement ({})
            elif not ModelingSettings.old_version() and node.get("type") == "compound_statement":
                expr_stmt = self._find_node_by_type(node, "expression_statement")
                if expr_stmt:
                    call_expr = self._find_node_by_type(expr_stmt, "call_expression")
                    if call_expr and call_expr['children'][0]['text'].endswith("_create"):
                        is_component_instantiation = True

            if is_component_instantiation:
                # print(f"DEBUG: Executing component instantiation node of type {node.get('type')}")
                self.execute_node(node, state)
            else:
                self.execute_node(node, state)


    def _execute_plant_function(self, body_node: dict, state: ModelingState):
        # print('DEBUG: execute_plant_function start')
        i = 0
        for statement_node in body_node.get("children", []):
            if i == 32:
                pass
            i += 1
            # if not statement_node.get("is_named") or "myId" in statement_node.get("text") or "myTemplateName" in statement_node.get("text"):
            #     continue
            if not statement_node.get("is_named"):
                continue
            self.execute_node(statement_node, state)
        # print('DEBUG: execute_plant_function end')


    def _execute_printf(self, func_name: str, arg_values: list, state: ModelingState) -> None:
        """
        printf
        """
        # # print(f"DEBUG: Ignored printf call with {len(arg_values)} arguments.")
        return None

    def _execute_std_min(self, arg_values: list, state: ModelingState):
        if len(arg_values) != 2:
            raise ValueError(f"std::min expects 2 arguments, but got {len(arg_values)}.")

        val_a = self.get_value_from_ref(arg_values[0], state)
        val_b = self.get_value_from_ref(arg_values[1], state)

        if isinstance(val_a, int) and isinstance(val_b, int):
            return min(val_a, val_b)

        term_a = self.modeler_context.solver.FF_number(val_a) if isinstance(val_a, int) else val_a
        term_b = self.modeler_context.solver.FF_number(val_b) if isinstance(val_b, int) else val_b

        condition = self.modeler_context.solver.mkFFTerm_Gt(term_b, term_a)

        # solver.mkTerm(Kind.ITE, condition, if_true_term, if_false_term)
        min_term = self.modeler_context.solver.mkTerm(self.modeler_context.solver.ITE, condition, term_a, term_b)

        return min_term

    def _stateful_write(self, dest_ref: Any, value: Any, state: ModelingState, func_name_for_error: str = "operation"):
        if not isinstance(dest_ref, SimulatedPointer):
            raise TypeError(f"Destination for {func_name_for_error} must be a pointer, but got {type(dest_ref)}.")
        dest_ref.set_value(value, state)

    def execute_return_statement(self, node: dict, state: ModelingState):
        """
        handle return statement. Calculate the return value (if any) and raise ReturnException to interrupt the flow.s
        """
        return_value = None
        # the children of return_statement may include non-named nodes like 'return' keyword and ';'
        # if only return; is present, there will be no named children
        named_children = [c for c in node.get("children", []) if c.get("is_named")]

        if named_children:
            return_value_node = named_children[0]
            return_value = self.evaluate_expression(return_value_node, state)

        raise ReturnException(return_value)

    def evaluate_assignment(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """lhs op rhs"""
        lhs_node = node["children"][0]
        operator = node["children"][1].get("type") # '=', '+=', '-=', etc.
        rhs_node = node["children"][2]

        rhs_value = self.evaluate_expression(rhs_node, state, if_log)

        new_value = None

        if operator == "=":
            new_value = rhs_value
        else:
            lhs_current_value = self.evaluate_expression(lhs_node, state, if_log)

            if operator == "+=":
                new_value = lhs_current_value + rhs_value
            elif operator == "-=":
                new_value = lhs_current_value - rhs_value
            elif operator == "*=":
                new_value = lhs_current_value * rhs_value
            elif operator == "/=":
                new_value = lhs_current_value / rhs_value
            elif operator == "%=":
                new_value = lhs_current_value % rhs_value
            else:
                raise NotImplementedError(f"Unsupported assignment operator: '{operator}'")
        if if_log:
            print(f"DEBUG: assign {lhs_node.get('text')} {operator} {rhs_value}")
        self._assign_to_lhs(lhs_node, new_value, state)

        return new_value

    def evaluate_binary_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """left op right"""
        left_node = node["children"][0]
        op_text = node["children"][1].get("text")
        right_node = node["children"][2]

        left_value = self.evaluate_expression(left_node, state, if_log)
        right_value = self.evaluate_expression(right_node, state, if_log)

        if if_log:
            print(f"DEBUG: binary {op_text} {left_value} {right_value}")

        if op_text == '+':
            return left_value + right_value
        elif op_text == '-':
            return left_value - right_value
        elif op_text == '*':
            return left_value * right_value
        elif op_text == '/':
            return left_value // right_value
        elif op_text == '<':
            return left_value < right_value
        elif op_text == '>':
            return left_value > right_value
        elif op_text == '==':
            return left_value == right_value
        elif op_text == '!=':
            return left_value != right_value
        else:
            raise NotImplementedError(f"Unsupported binary operator: '{op_text}'")

    def evaluate_unary_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """
        op operand (!condition, -value之类的)
        """
        if not node or node.get("type") != "unary_expression":
            return None

        children = node.get("children", [])
        if len(children) < 2:
            raise ValueError("Invalid unary_expression structure: missing children nodes")

        operator_node = children[0]
        operand_node = children[1]

        op_text = operator_node.get("text")

        operand_value = self.evaluate_expression(operand_node, state, if_log)

        result = None

        if op_text == '!':
            result = not operand_value

        elif op_text == '-':
            result = -operand_value

        elif op_text == '+':
            result = +operand_value

        else:
            raise NotImplementedError(f"Unsupported unary operator: '{op_text}'")
        if if_log:
            print(f"DEBUG: unary {op_text} {operand_value} = {result}")
            
        return result
    
    def evaluate_conditional_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """condition ? true_expr : false_expr"""
        condition_node = node["children"][0]
        true_expr_node = node["children"][2]
        false_expr_node = node["children"][4]

        condition_value = self.evaluate_expression(condition_node, state)
        if condition_value:
            return self.evaluate_expression(true_expr_node, state)
        else:
            return self.evaluate_expression(false_expr_node, state)

    def evaluate_update_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """i++ or ++i"""
        var_node = node["children"][0] if node["children"][0].get("type") == "identifier" else node["children"][1]
        op_node = node["children"][1] if node["children"][0].get("type") == "identifier" else node["children"][0]

        var_name = var_node.get("text")

        current_value = state.get_local_var(var_name)
        if current_value is None:
            raise NameError(f"Variable '{var_name}' is not defined")

        new_value = current_value + 1 if op_node.get("type") == '++' else current_value - 1

        state.update_local_var_or_circuitElement(var_name, new_value)
        if if_log:
            print(f"DEBUG: update {var_name} from {current_value} to {new_value}")
        if node["children"][0].get("type") == "identifier":
            return current_value
        else: 
            return new_value

    def evaluate_function_call(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        func_expr_node = node["children"][0]

        while func_expr_node.get("type") == "parenthesized_expression":
            inner_node = next((c for c in func_expr_node.get("children", []) if c.get("is_named")), None)
            if inner_node:
                func_expr_node = inner_node
            else:
                raise ValueError("Invalid parenthesized_expression in function call")
            
        func_expr_type = func_expr_node.get("type")
        func_name = None
            
        if func_expr_type == "identifier":
            func_name = func_expr_node.get("text")
            
        elif func_expr_type == "qualified_identifier":
            func_name = func_expr_node.get("text")

        elif func_expr_type == "field_expression":
            children = [c for c in func_expr_node.get("children", []) if c.get("is_named")]
            base_node = children[0]
            field_node = children[-1]
            
            if base_node.get("text") == "ctx" and field_node.get("text") in self.context_functions:
                func_name = field_node.get("text")
            else:
                raise NotImplementedError(
                    f"unsupported method call on object '{base_node.get('text')}' for method '{field_node.get('text')}'"
                )

        elif func_expr_type == "pointer_expression":
            evaluated_func = self.evaluate_expression(func_expr_node, state)
            if isinstance(evaluated_func, str):
                func_name = evaluated_func
            else:
                raise TypeError(f"expected function name string from pointer_expression, but got {type(evaluated_func)}")
        
        else:
            raise NotImplementedError(f"Unsupported function call expression type: {func_expr_type}")

        arg_list_node = node["children"][1]
        arg_values = []
        for arg in arg_list_node.get("children", []):
            if arg.get("is_named"):
                value = self.evaluate_expression(arg, state)
                arg_values.append(value)
        if if_log:
            print(f"DEBUG: call {func_name} with args {arg_values}")
        if func_name == "printf":
            self._execute_printf(func_name, arg_values, state)
        elif func_name.startswith("std::"):
            if func_name.endswith("min"):
                return self._execute_std_min(arg_values, state)
        elif func_name == "release_memory_component":
            pass
        elif func_name.startswith("Fr_"):
            if func_name == 'Fr_toInt' and ModelingSettings.compare_versions(ModelingSettings.CIRCOM_VERSION, '2.1.1') < 0:
                raise Exception('call buggy assembly function Fr_toInt !!')
            return self._execute_fr_operation(func_name, arg_values, state)
        elif func_name.endswith("assert"):
            pass
            # return self._execute_assertion(func_name, arg_values, state)
        # elif func_name == "generate_position_array" or func_name == "ctx->generate_position_array":
        #     return self._execute_generate_position_array(arg_values, state)
        elif func_name == "generate_position_array":
            return self._execute_generate_position_array(arg_values, state)
        else:
            # "_create", "_run"
            return self._execute_circom_func(func_name, arg_values, state)

    def evaluate_field_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        
        children = node.get("children", [])
        base_object_node = children[0]
        operator_node = children[1]
        field_name_node = children[2]
        
        
        operator_text = operator_node.get("text")
        field_name = field_name_node.get("text")
        
        base_name = base_object_node.get("text")
        if base_name == 'ctx':
            if field_name == 'signalValues':
                return self.modeler_context.signalList
            if field_name == 'componentMemory':
                return self.modeler_context.componentMemory
            if field_name == 'circuitConstants':
                return self.modeler_context.circuitConstants
            if field_name == 'listOfTemplateMessages':
                return self.modeler_context.listOfTemplateMessages
            if field_name == 'functionTable':
                return self.modeler_context.functionTable
            if field_name == 'templateInsId2IOSignalInfo':
                return self.modeler_context.templateInsId2IOSignalInfo

        base_object = self.evaluate_expression(base_object_node, state)

        if base_object is None:
            base_object_text = base_object_node.get("text", f"[complex_expression_of_type_{base_object_node.get('type')}]")
            raise AttributeError(
                f"run-time error: trying to access field '{field_name}' of base object '{base_object_text}' which is None. "
                "possibly due to uninitialized variable or null pointer dereference."
            )

        target_object = None
        if operator_text == '->':
            if not isinstance(base_object, SimulatedPointer):
                raise TypeError(
                    f"syntax error: trying to access field of non-pointer type '{type(base_object).__name__}' "
                )
            target_object = base_object.get_value(state)
            if target_object is None:
                raise AttributeError(f"runtime error: trying to access field '{field_name}' through a null pointer.")
        
        elif operator_text == '.':
            if isinstance(base_object, SimulatedPointer):
                raise TypeError(
                    f"syntax error: try to access field of pointer with '.', "
                    f"please use '->' instead."
                )
            target_object = base_object
        
        else:
            raise NotImplementedError(f"unsupported field access operator: '{operator_text}'")
                
        try:
            return getattr(target_object, field_name)
        except AttributeError:
            if isinstance(target_object, dict):
                if field_name in target_object:
                    return target_object[field_name]
                else:
                    raise KeyError(f"no such key '{field_name}' in dict.")

            base_object_text = base_object_node.get("text", f"[type_{type(base_object).__name__}]")
            raise AttributeError(f"object of type '{type(target_object).__name__}' has no attribute '{field_name}'")


    def evaluate_subscript_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """
        array[index]
        """
        if not node or node.get("type") != "subscript_expression":
            return None

        children = node.get("children", [])
        if len(children) < 2:
            raise ValueError("Invalid subscript_expression structure: insufficient children")

        array_node = children[0]
        subscript_arg_list = children[1]

        if subscript_arg_list.get("type") != "subscript_argument_list":
            raise ValueError("Invalid subscript_expression structure: missing subscript_argument_list") 

        index_node = subscript_arg_list["children"][1]

        array_object = self.evaluate_expression(array_node, state)
        index_value = self.evaluate_expression(index_node, state)

        if array_object is None:
            raise NameError(f"尝试对未定义的数组 '{array_node.get('text')}' 进行下标访问")

        try:
            # if if_log:
            # print(f"DEBUG: access array {array_node.get('text')} with index {index_value}")
            return array_object[index_value]
        except IndexError:
            print(f"Runtime Error: Array index out of bounds! Accessing index {index_value}, but array size is {len(array_object)}")
            raise
        except TypeError:
            print(f"Runtime Error: Object '{array_object}' does not support subscript access")
            raise

    def evaluate_new_expression(self, node: dict, state: ModelingState, if_log: bool = False) -> list[Any]:
        type_node = self._find_node_by_type(node, "type_identifier")
        declarator_node = self._find_node_by_type(node, "new_declarator")
        initializer_list_node = self._find_node_by_type(node, "initializer_list")

        if not declarator_node:
            raise NotImplementedError("Only array types are supported in `new` expressions.")
        

        # ['[', size_node, ']']
        size_node = declarator_node["children"][1]

        array_size = self.evaluate_expression(size_node, state)

        if initializer_list_node:
            init_values_nodes = [
                child for child in initializer_list_node.get("children", [])
                if child.get("is_named")
            ]

            initial_values = [self.evaluate_expression(val_node, state) for val_node in init_values_nodes]

            if len(initial_values) > array_size:
                raise ValueError(
                    f"new expression initializer list size ({len(initial_values)}) "
                    f"exceeds the specified array size ({array_size})."
                )

            padding = [0] * (array_size - len(initial_values))
            return initial_values + padding

        else:
            return [0] * array_size

    def evaluate_initializer_list(self, node: dict, state: ModelingState, if_log: bool = False) -> list[Any]:
        if not node or node.get("type") != "initializer_list":
            return None

        init_values_nodes = [
            child for child in node.get("children", [])
            if child.get("is_named")
        ]

        initial_values = [self.evaluate_expression(val_node, state) for val_node in init_values_nodes]
        return initial_values

    def _find_node_by_type(self, start_node: dict, target_type: str) -> dict | None:
        if not start_node:
            return None
        for child in start_node.get("children", []):
            if child.get("type") == target_type:
                return child
        return None

    def evaluate_pointer_expression(self, node: dict, state: ModelingState, if_log: bool = False):
        # pointer_expression  operator_node, operand_node
        operator_node = node["children"][0]
        operand_node = node["children"][1]
        op_text = operator_node.get("text")

        if op_text == '&':
            while operand_node.get("type") == "parenthesized_expression":
                if len(operand_node.get("children", [])) > 1:
                    operand_node = operand_node['children'][1]
                else:
                    raise ValueError("Malformed parenthesized_expression encountered while taking address.")
                
            operand_type = operand_node.get("type")

            if operand_type == "subscript_expression":
                # &Array[i]
                array_node = operand_node["children"][0]
                index_node = operand_node["children"][1]["children"][1]

                container = self.evaluate_expression(array_node, state)
                key = self.evaluate_expression(index_node, state)
                return SimulatedPointer(container, key, array_node['text'])

            elif operand_type == "field_expression":
                # &obj.member
                base_object_node = operand_node["children"][0]
                field_name = operand_node["children"][-1].get("text")

                container = self.evaluate_expression(base_object_node, state)
                key = field_name
                return SimulatedPointer(container, key)

            elif operand_type == "identifier":
                # &my_local_var
                var_name = operand_node.get("text")
                container = state.get_local_vars()
                key = var_name
                return SimulatedPointer(container, key)
            else:
                raise NotImplementedError(f"unsupported operand type '{operand_type}' for '&' operator in pointer_expression")

        elif op_text == '*':
            pointer_object = self.evaluate_expression(operand_node, state)

            if isinstance(pointer_object, str):
                return pointer_object
            if not isinstance(pointer_object, SimulatedPointer):
                raise TypeError(f"unary '*' operator requires a SimulatedPointer, got {type(pointer_object).__name__}")

            return pointer_object.get_value(state)

        else:
            raise NotImplementedError(f"unsupported operator '{op_text}' in pointer_expression")

    def evaluate_identifier(self, node: dict, state: ModelingState, if_log: bool = False) -> Any:
        """myVariable"""
        var_name = node['text']
        if if_log:
            print(f"DEBUG: identifier {var_name}")
 
        if var_name == "ctx":
            return self.modeler_context
        elif var_name == "circuitConstants":
            return self.modeler_context.circuitConstants
        elif var_name == "signalValues":
            return self.modeler_context.signalList
        elif var_name == "_functionTable":
            return self.modeler_context.functionTable


        try:
            if var_name == "cur_def" and if_log:
                value = state.get_local_var(var_name)
                print("\n---[ DEBUGGER: Inspecting 'cur_def' ]---")
                print(f"  - Variable Name: {var_name}")
                print(f"  - Raw Value (in state): {value}")
                print(f"  - Value Type: {type(value)}")

                if isinstance(value, SimulatedPointer):
                    try:
                        pointed_to_object = value.get_value(state)
                        print(f"  - Points to Object: {pointed_to_object}")
                        print(f"  - Pointed Object Type: {type(pointed_to_object)}")
                        
                        if hasattr(pointed_to_object, 'offset'):
                            print(f"    -> offset: {pointed_to_object.offset}")
                        if hasattr(pointed_to_object, 'len'):
                            print(f"    -> len (from size): {pointed_to_object.len}") 
                        if hasattr(pointed_to_object, 'lengths'):
                            print(f"    -> lengths: {pointed_to_object.lengths}")
                            
                    except Exception as e:
                        print(f"  - FAILED to dereference pointer: {e}")
                print("---[ END DEBUGGER ]---\n")
            return state.get_local_var(var_name)
        except (KeyError, NameError):
            if var_name in self.modeler_context.functionDict:
                return self.modeler_context.functionDict[var_name]
            else:
                raise NameError(f"undifined variable or function: '{var_name}'")
                

    def get_value_from_ref(self, ref: Any, current_state: ModelingState) -> Any:
        """
        A helper function to extract the underlying value (int or Term) from any reference.
        It handles SimulatedPointer and CircuitElement unpacking.
        """
        # 1: if ref is SimulatedPointer, then get the value it points to
        if isinstance(ref, SimulatedPointer):
            pointed_to_value = ref.get_value(current_state)
        else:
            # if not, then it is the value itself
            pointed_to_value = ref

        # 2: if the value is CircuitElement, then get the value it holds
        if isinstance(pointed_to_value, CircuitElement):
            return pointed_to_value.get_value()
        else:
            # if not, then it is the value itself
            return pointed_to_value

    def _find_nodes_by_type_recursive(self, start_node: dict, target_type: str) -> list[dict]:
        nodes = []
        if start_node.get("type") == target_type:
            nodes.append(start_node)
        for child in start_node.get("children", []):
            nodes.extend(self._find_nodes_by_type_recursive(child, target_type))
        return nodes

    def _get_rhs_value(self, rhs_node: dict, arg_map: dict):
        node_type = rhs_node.get("type")
        if node_type == "number_literal":
            text = rhs_node.get("text")
            try:
                return int(text)
            except ValueError:
                return float(text)
        elif node_type == "string_literal":
            if len(rhs_node.get("children", [])) > 1:
                return rhs_node["children"][1].get("text")
            return ""
        elif node_type == "identifier":
            param_name = rhs_node.get("text")
            return arg_map.get(param_name, f"UNRESOLVED_IDENTIFIER:{param_name}")
        else:
            return rhs_node.get("text")

    def _assign_to_lhs(self, lhs_node: dict, value: Any, state: ModelingState):
        lhs_type = lhs_node.get("type")

        if lhs_type == "identifier":
            var_name = lhs_node.get("text")
            state.update_local_var_or_circuitElement(var_name, value)

        elif lhs_type == "subscript_expression":
            array_node = lhs_node["children"][0]
            index_node = lhs_node["children"][1]["children"][1]

            array_obj = self.evaluate_expression(array_node, state)
            index = self.evaluate_expression(index_node, state)

            if array_obj is None:
                raise ValueError(f"can not subscript assign to None. expression: {array_node.get('text')}")

            try:
                array_obj[index] = value
            except IndexError:
                raise IndexError(f"array index out of bounds: accessing index {index}, but array size is {len(array_obj)}")
            except TypeError:
                raise TypeError(f"object of type '{type(array_obj).__name__}' does not support subscript assignment")

        elif lhs_type == "field_expression":
            base_object_node = lhs_node["children"][0]
            field_name = lhs_node["children"][-1].get("text")

            base_object = self.evaluate_expression(base_object_node, state)

            if base_object is None:
                raise AttributeError(f"can not set attribute '{field_name}' on None. expression: {base_object_node.get('text')}")

            try:
                setattr(base_object, field_name, value)
            except AttributeError:
                raise AttributeError(f"Object of type '{type(base_object).__name__}' has no attribute '{field_name}', cannot assign value.")

        elif lhs_type == "pointer_expression":
            operator_node = lhs_node["children"][0]
            operand_node = lhs_node["children"][1]

            if operator_node.get("text") != '*':
                raise NotImplementedError(f"unsupported pointer operator '{operator_node.get('text')}' in assignment.")

            pointer_obj = self.evaluate_expression(operand_node, state)
            if isinstance(pointer_obj, SimulatedPointer):
                pointer_obj.set_value(value, state)
            else:
                raise TypeError(f"cannot dereference and assign to non-pointer type '{type(pointer_obj).__name__}'.")
        else:
            raise NotImplementedError(f"unsupported lhs type '{lhs_type}' in assignment.")

    def _execute_circom_func(self, func_name: str, arg_values: list, state: ModelingState) -> Any:
        func_def_node = self.modeler_context.functionDict[func_name]
        if not func_def_node:
            raise NameError(f"Function '{func_name}' is not defined in the current context.")

        if func_name not in self._param_cache:
            self._param_cache[func_name] = self._parse_param_names(func_def_node)
        param_names = self._param_cache[func_name]

        arg_map = dict(zip(param_names, arg_values))

        self._execute_function_body(func_def_node, arg_map, state)

    def _assign_signal(self, dest: CPPSignal, value):
        if isinstance(value, int):
            dest.assign_constant(value)
        elif isinstance(value, cvc5.Term):
            dest.assign_constant()


    def _execute_fr_operation(self, func_name: str, arg_values: list[Any], state: ModelingState):
        """
        Orchestrates the execution of Fr_ operations.

        Args:
            func_name: The name of the Fr_ operation to execute.
            arg_values: A list of argument values, each being a reference to a signal or constant.
            state: The current modeling state, used to resolve references and manage side effects.
        """
        # if if_log:
        # print(f"execute_fr_operation: {func_name} with args {arg_values}")
        if func_name in ["Fr_isTrue", "Fr_toInt"]:
            value = self.get_value_from_ref(arg_values[0], state)
            if func_name == "Fr_isTrue":
                if isinstance(value, int):
                    return value != 0
                else:
                    return value
            if func_name == "Fr_toInt":
                if isinstance(value, int):
                    prime = self.modeler_context.P
                    if value > prime // 2:
                        return value - prime
                    else:
                        return value
                else: raise TypeError('Cannot convert symbolic value to int')
            return
        elif func_name == "Fr_element2str":
            return

        dest_ref = arg_values[0]
        src_args = arg_values[1:]

        # if not ModelingSettings.IF_UNDEFINED_BEHAVIOR and not state.is_function_root():
        #     if dest_ref.containerName == 'signalValues':
        #         raise SyntaxError('Assignment for in If-Then-Else will leads to undefined behavior')
        # if dest_ref.containerName == 'signalValues' or dest_ref.containerName == 'ctx->signalValues':
        #     state.assigned_signals.add(dest_ref.key)

        result = self._calculate_fr_result(func_name, src_args, state)

        self._write_fr_result(dest_ref, result, state)

    def _calculate_fr_result(self, func_name: str, src_args: list[Any], state: ModelingState) -> Any:
        """
        Calculate the result of a finite field operation without side effects.

        Args:
            func_name: The name of the finite field operation (e.g., "Fr_copy").
            src_args: A list of source arguments, each being a reference to a signal or constant.
            state: The current modeling state, used to resolve references.

        Returns:
            The result of the operation, either as an integer or a cvc5.Term.
        """
        if func_name == "Fr_copy":
            return self.get_value_from_ref(src_args[0], state)
        
        if func_name == "Fr_copyn":
            source_ptr = src_args[0]  # 'a'
            count_ref = src_args[1]   # 'n'

            if not isinstance(source_ptr, SimulatedPointer):
                raise TypeError(f"Source argument 'a' for Fr_copyn must be a pointer, but got {type(source_ptr)}")

            count = self.get_value_from_ref(count_ref, state)
            if not isinstance(count, int):
                raise TypeError(f"Count 'n' for Fr_copyn must be a concrete integer, but got {type(count)}")

            values_to_copy = []
            for i in range(count):
                current_source_ptr = SimulatedPointer(
                    source_ptr.container,
                    source_ptr.key + i,
                    source_ptr.containerName
                )
                value = self.get_value_from_ref(current_source_ptr, state)
                values_to_copy.append(value)
            
            return values_to_copy

        if func_name in CPPBuildinWords.binary_op_map:
            val1 = self.get_value_from_ref(src_args[0], state)
            val2 = self.get_value_from_ref(src_args[1], state)
            opcode = CPPBuildinWords.binary_op_map[func_name].value
            # if if_log:
            # print(f"execute_fr_operation: {func_name} with args {src_args}")
            # print(f"current signals: {self.modeler_context.get_signals()}")
            if isinstance(val1, int) and isinstance(val2, int):
                return calculate_deterministic_infixOp(val1, opcode, val2, self.modeler_context.solver.prime())
            else:
                if isinstance(val1, int): val1 = self.modeler_context.solver.FF_number(val1)
                if isinstance(val2, int): val2 = self.modeler_context.solver.FF_number(val2)
                result, term = generate_infix_term(val1, opcode, val2, self.modeler_context.solver)
                if term: self.modeler_context.add_term(term)
                return result

        if func_name in CPPBuildinWords.unary_op_map:
            val = self.get_value_from_ref(src_args[0], state)
            opcode = CPPBuildinWords.unary_op_map[func_name].value

            if isinstance(val, int):
                return calculate_deterministic_prefixOp(opcode, val, self.modeler_context.solver.prime())
            else:
                return generate_prefix_term(opcode, val, self.modeler_context.solver)
        
        raise NotImplementedError(f"Calculation for '{func_name}' is not implemented.")

    def _write_fr_result(self, dest_ref: SimulatedPointer, result: Any, state: ModelingState):
        """
        Distributes write operations for single values or lists of values.
        It does not perform actual writes but delegates to a helper function for each memory location.
        """
        if isinstance(result, list):
            # Distribute write operations for each value in the list.
            for i, value in enumerate(result):
                # Calculate the target pointer for each value in the list.
                current_dest_ptr = SimulatedPointer(
                    dest_ref.container,
                    dest_ref.key + i,
                    dest_ref.containerName
                )
                # Perform a stateful write for each element.
                self._perform_stateful_write(current_dest_ptr, value, state)
        else:
            # Single value result for standard operations like Fr_copy, Fr_add.
            # Perform a stateful write for the single value.
            self._perform_stateful_write(dest_ref, result, state)
            if dest_ref.containerName == 'signalValues' or dest_ref.containerName == 'ctx->signalValues':
                state.assigned_signals.add(dest_ref.key)

    def _perform_stateful_write(self, ptr: SimulatedPointer, value: Any, state: ModelingState):
        """
        Executes a stateful write to a single memory location.
        - If in a branch state, records the deferred write.
        - Otherwise, directly modifies the container.
        This method is the only point where all Fr_ operations write to memory.
        """
        is_branch_state = state.get_father() is not None and not state.is_function_root()

        if is_branch_state:
            # In a branch state, only record the write operation.
            state.record_write(ptr.containerName, ptr.key, value)
        else:
            # In the main flow or function root scope, directly execute the write.
            try:
                # Must first get the original item to be overwritten, to check if it's a CPPSignal.
                original_item = ptr.container[ptr.key]

                if isinstance(original_item, CPPSignal):
                    original_item.assign_value(value)
                    state.assigned_signals.add(ptr.key)
                else:
                    ptr.container[ptr.key] = value

            except (IndexError, KeyError) as e:
                print(f"Pointer assignment error: Failed to set key/index '{ptr.key}' in container '{ptr.containerName}'.")
                raise e

    def _execute_assertion(self, func_name: str, arg_values: list[Any], state: ModelingState):
        assert len(arg_values) == 1, f"{func_name} requires one parameter"
        assert arg_values[0], f"{func_name} assertion failed"
        return

    def _parse_param_names(self, func_def_node: dict) -> list[str]:
        names = list()
        declarator = self._find_node_by_type(func_def_node, "function_declarator")
        param_list = self._find_node_by_type(declarator, "parameter_list")
        for child in param_list.get("children", []):
            if child.get("type") == "parameter_declaration":
                last_id = self._find_last_identifier(child)
                if last_id:
                    names.append(last_id["text"])
        return names

    def _find_last_identifier(self, node: dict):
        result = None
        for child in node['children']:
            if child['type'] == 'identifier':
                result = child
            elif child['type'] == 'pointer_declarator':
                result = self._find_last_identifier(child)
        return result

    def _get_var_name_from_declarator(self, declarator_node: dict) -> str | None:
        if not declarator_node:
            return None

        node_type = declarator_node.get("type")

        if node_type == "identifier":
            return declarator_node.get("text")

        for child in declarator_node.get("children", []):
            if child.get("type") == "identifier":
                return child.get("text")

        return None


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value