import json
import os
import shutil
import subprocess
import re
import time

from cvc5 import Kind

from ..CPPWitnessCalculator.CPPModeler import CPPModeler
from ..CircomSourceCode.CircomBuildinWords import CBW
from ..CircomSourceCode.Component import Component
from ..CircomSourceCode.Function import Function
from ..CircomSourceCode.Signal import SignalTypes, Signal
from ..CircomSourceCode.Template import Template
from .DealCircomRaw import get_public_input
from ..R1CS.R1CSBinaryDealer import parse_r1cs_header
from ..R1CS.R1CSDealer import R1CSDealer
from ..Setting import ModelingSettings
from ...Tools.ColorPrint import colorPrint, COLOR
from .DealSym import SymDataDic
from ...Tools.Errors import MyUnCompiledError, MyEnumError
from ...Tools.ExpandedCVC5 import ExpandedCVC5
from ...Tools.WriteToFile import save_string_to_file


def compare_versions(v1: str, v2: str) -> int:
    """
    :return: -1 if v1 < v2，0 if v1 == v2，1 if v1 > v2
    """
    nums1 = [int(x) for x in v1.split('.')]
    nums2 = [int(x) for x in v2.split('.')]

    max_len = max(len(nums1), len(nums2))
    nums1.extend([0] * (max_len - len(nums1)))
    nums2.extend([0] * (max_len - len(nums2)))

    for a, b in zip(nums1, nums2):
        if a < b:
            return -1
        elif a > b:
            return 1
    return 0

class CircuitTerms:
    def __init__(self, main_component, compiled_calculate_terms, compiled_constraint_terms,
                 compiled_constraint_terms_independent, variable_dic):
        self.main_component = main_component
        self.input_signals_dic = main_component.get_input_signals_dic()
        self.output_signals_dic = main_component.get_output_signals_dic()
        self.all_signals_dic = main_component.get_all_signals_dic()
        self.calculate_terms = main_component.get_all_calculate_terms()
        self.constraint_terms = main_component.get_all_constraint_terms()
        self.compiled_calculate_terms = compiled_calculate_terms
        self.compiled_constraint_terms = compiled_constraint_terms
        self.compiled_constraint_terms_independent = compiled_constraint_terms_independent
        self.variable_dic = variable_dic

'''
a class to manage a circom circuit, each object maintains an instance of a circom circuit
includes：
raw_path
circuit_name
case_temp_path
exp_slv
information
'''


class CircuitManager:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ast_builder_path = os.path.join(base_dir, '..', '..', 'dependence', 'AstBuilder')
    compiler_path = os.path.join(base_dir, '..', '..', 'dependence', 'circom')
    temp_file_dir = os.path.join(base_dir, '..', '..', 'temp_file')

    polish_list = ['O0', 'O1', '02', 'O3']

    @staticmethod
    def set_temp_file_dir(path):
        CircuitManager.temp_file_dir = path

    @staticmethod
    def set_ast_builder_path(path):
        CircuitManager.ast_builder_path = path

    @staticmethod
    def set_compiler_path(path):
        CircuitManager.compiler_path = path

    def __init__(self, raw_path, exp_slv, artifacts_path):
        self.__raw_path = raw_path
        self.__circuit_name = os.path.splitext(os.path.basename(raw_path))[0]
        self.__case_temp_path = artifacts_path
        self.__exp_slv = exp_slv
        if not os.path.exists(CircuitManager.temp_file_dir) or not os.path.isdir(CircuitManager.temp_file_dir):
            os.makedirs(CircuitManager.temp_file_dir)
        self.__compile_pass = False
        self.__information = None
        self.__input_signals = None
        self.__output_signals = None
        self.__inter_signals = None
        self.__public_IO_signals = None
        self.__cpp_signals = None
        self.__all_smt = set()
        self.__sym_data = None
        self.__R1CS_head_info = None
        self.component_num = None
        self.constraints_num = None
        self.perf_data = {}
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['File Name'] = self.__circuit_name
            self.perf_data['signal num'] = 'N/A' 
        colorPrint(f'=============== {self.__circuit_name} ===============', COLOR.GREEN)

    @property
    def name(self):
        return self.__circuit_name

    def comp_constraint_num(self, cpp_path):
        with open(cpp_path, 'r') as file:
            for line in file:
                match_components = re.match(r'uint get_number_of_components\(\) \{return (\d+);\}', line)
                if match_components:
                    self.component_num = int(match_components.group(1))

                match_constants = re.match(r'uint get_size_of_constants\(\) \{return (\d+);\}', line)
                if match_constants:
                    self.constraints_num = int(match_constants.group(1))
                    break

    def generate_AST(self):
        pass

    def pick_information(self, run_time_data=None):
        if run_time_data is None:
            run_time_data = list()

        if not os.path.exists(self.__case_temp_path):
            os.makedirs(self.__case_temp_path)

        colorPrint('-- GENERATING AST FILE --', COLOR.YELLOW)
        start_time = time.time() 
        ast_path = f'{self.__case_temp_path}/ast.json'
        build_ast_cmd = [CircuitManager.ast_builder_path, self.__raw_path, ast_path]
        result = subprocess.run(build_ast_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            colorPrint(f"AstBuilder failed with return code {result.returncode}", COLOR.RED)
            colorPrint(f"Stderr: {result.stderr}", COLOR.RED)
            colorPrint(f"Stdout: {result.stdout}", COLOR.RED)
        end_time = time.time()
        AST_generate_time = end_time - start_time
        print(f'AST Generating Time: {AST_generate_time:.4f} s')
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['AST Generating Time'] = f"{AST_generate_time:.4f}"


        start_time = time.time() 

        main_component = CircuitManager.deal_ast(ast_path, self.__exp_slv)
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['signal num'] = len(main_component.get_all_signals_dic())

        self.__input_signals = set(main_component.get_input_signals_dic().values())
        self.__output_signals = set(main_component.get_output_signals_dic().values())
        self.__inter_signals = set(main_component.get_all_signals_dic().values()) - self.__input_signals - self.__output_signals

        self.__public_IO_signals = dict(main_component.get_output_signals_dic())
        public_input_signal_name_list = get_public_input(self.__raw_path)
        input_signal_dict = main_component.get_input_signals_dic()
        for signal_name in public_input_signal_name_list:
            signal = input_signal_dict.get(signal_name, None)
            if signal is not None:
                self.__public_IO_signals[signal_name] = signal

        end_time = time.time() 
        AST_processing_time = end_time - start_time
        print(f'AST Processing Time: {AST_processing_time:.4f} s')
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['AST Processing Time'] = f"{AST_processing_time:.4f}"

        # colorPrint(f'-- DEALING SYM FILE --', COLOR.YELLOW)
        sym_path = f'{self.__case_temp_path}/{self.__circuit_name}.sym'
        all_signals = list(main_component.get_all_signals_dic().values())
        sym_data_dic = SymDataDic(sym_path, all_signals, self.__exp_slv.FF_number(1))


        start_time = time.time() 
        cons_path = f'{self.__case_temp_path}/{self.__circuit_name}_constraints.json'
        R1CS_binary_path = f'{self.__case_temp_path}/{self.__circuit_name}.r1cs'
        cons_dealer = R1CSDealer(cons_path, self.__exp_slv, sym_data_dic)

        colorPrint(f'-- DEALING R1CS FILE --', COLOR.YELLOW)
        compiled_constraint_terms = cons_dealer.get_all_terms()
        compiled_constraint_terms_independent, variable_dic = cons_dealer.get_independent_terms()

        end_time = time.time()
        R1CS_processing_time = end_time - start_time
        print(f'R1CS Processing Time: {R1CS_processing_time:.4f} s')
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['R1CS Processing Time'] = f"{R1CS_processing_time:.4f}"

        # colorPrint(f'-- DEALING C++ FILE --', COLOR.YELLOW)
        start_time = time.time()
        if ModelingSettings.CHECK_CALCULATION:
            cpp_path = f'{self.__case_temp_path}/{self.__circuit_name}_cpp/{self.__circuit_name}.cpp'
            dat_path = f'{self.__case_temp_path}/{self.__circuit_name}_cpp/{self.__circuit_name}.dat'
            colorPrint(f'-- DEALING CPP FILES --', COLOR.YELLOW)

            CPP_Json_path = f'{self.__case_temp_path}/{self.__circuit_name}_cpp/{self.__circuit_name}.json'
            cppModeler = CPPModeler(cpp_path, dat_path, self.__exp_slv, CPP_Json_path)
            cppModeler.saveCPPData(cpp_path)
            cppModeler.build()

            compiled_calculate_terms = cppModeler.get_terms()
            self.__cpp_signals = cppModeler.get_signals()
        else:
            compiled_calculate_terms = []
            # colorPrint('KIPPED', COLOR.GREEN)

        end_time = time.time()
        Cpp_Processing_Time = end_time - start_time
        print(f'C++ Processing Time: {Cpp_Processing_Time:.4f} s')
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['C++ Processing Time'] = f"{Cpp_Processing_Time:.4f}"


        colorPrint(f'-- DEALING SIGNAL CLASSIFICATION --', COLOR.YELLOW)
        start_time = time.time()

        self.__sym_data = self._deal_sym_info()
        self.__R1CS_head_info = parse_r1cs_header(R1CS_binary_path, self.__exp_slv.prime())

        end_time = time.time()
        signal_classification_processing_Time = end_time - start_time
        print(f'Signal Classification Processing Time: {signal_classification_processing_Time:.4f} s')
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['Signal Classification Processing Time'] = f"{signal_classification_processing_Time:.4f}"

        # f"{a:.4f}\t{b:.4f}\t{c:.4f}"
        # print(f"{AST_generate_time:.4f}\t{AST_generate_time:.4f}\t{R1CS_processing_time:.4f}\t{Cpp_Processing_Time:.4f}")
        run_time_data.append(
            f"{AST_generate_time:.4f}\t{AST_processing_time:.4f}\t{R1CS_processing_time:.4f}\t{Cpp_Processing_Time:.4f}\t{signal_classification_processing_Time:.4f}")


        # for term in compiled_calculate_terms:
        #     print(term)

        # self.__fr_element_dic = ccp_dealer.element_dict

        self.__all_smt.update(set(variable_dic.values()))
        self.__all_smt.update(set(variable_dic.keys()))

        self.__information = CircuitTerms(main_component,
                                          compiled_calculate_terms,
                                          compiled_constraint_terms,
                                          compiled_constraint_terms_independent,
                                          variable_dic)
        return self.__information

    def _deal_sym_info(self):
        sym_path = f'{self.__case_temp_path}/{self.__circuit_name}.sym'
        result = dict()
        with open(sym_path, 'r', encoding='utf-8') as f:
            for lineno, raw in enumerate(f, 1):
                line = raw.strip()
                if not line:
                    continue
                line = line.replace('，', ',') 
                parts = [p.strip() for p in line.split(',') if p.strip() != '']
                if len(parts) < 4:
                    raise ValueError(f"line {lineno} has less than 4 columns: {raw!r}")
                key = parts[-1]
                try:
                    a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
                except ValueError as e:
                    raise ValueError(f"line {lineno} has non-integer in first three columns: {raw!r}") from e
                result[key] = (a, b, c)
        return result

    @property
    def circuitTerms(self):
        if self.__compile_pass:
            return self.__information
        else:
            raise MyUnCompiledError(self.__circuit_name)

    def set_polish_level(self, polish):
        self.__polish_level = polish

    def compile_case(self, version, polish, prime_name):
        self.__polish_level = polish
        if os.path.exists(self.__case_temp_path) and os.path.isdir(self.__case_temp_path):
            shutil.rmtree(self.__case_temp_path)
        os.makedirs(self.__case_temp_path)

        colorPrint('-- COMPILING CIRCUIT --', COLOR.YELLOW)

        # version < 2.0.6 does not support prime other than bn128
        if compare_versions(version, '2.0.6') == -1:
            compile_cmd = [CircuitManager.compiler_path + version, f'--{polish}', self.__raw_path, '--r1cs',
                           '--sym',
                           '--c', '--json', '-o', self.__case_temp_path]
        else:
            compile_cmd = [CircuitManager.compiler_path + version, f'--{polish}', self.__raw_path, '--prime',
                           prime_name, '--r1cs',
                           '--sym',
                           '--c', '--json', '-o', self.__case_temp_path]

        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout, end='')
            self.__compile_pass = True
            return True
        else:
            print(result.stderr, end='')
            return False

    def generate_mapping_property(self):
        input_terms = list()
        other_terms = list()
        for signal in self.__information.all_signals_dic.values():
            cpp_signal_info = self.__sym_data[signal.sym_name]
            if cpp_signal_info is None:
                raise KeyError(f'can not find signal {signal.sym_name} in cpp!')
            cpp_signal = self.__cpp_signals[cpp_signal_info[0]]
            term = self.__exp_slv.mkFFTerm_Eq(signal.toSmt(), cpp_signal.toSmt())

            if signal.is_main_input:
                input_terms.append(term)
                if ModelingSettings.BINARY_INPUT:
                    eq_zero = self.__exp_slv.mkFFTerm_Eq(signal.toSmt(), self.__exp_slv.FF_zero())
                    eq_one = self.__exp_slv.mkFFTerm_Eq(signal.toSmt(), self.__exp_slv.FF_one())
                    binary_require = self.__exp_slv.mkBool_Or(eq_zero, eq_one)
                    input_terms.append(binary_require)
            else:
                if signal.is_assigned != cpp_signal.is_assigned():
                    if ModelingSettings.ASSIGNMENT_CONSISTENT:
                        raise ValueError(f'assignment situation for signal {signal.sym_name} is not instant in Circom and Witness calculator')
                if signal.is_assigned and cpp_signal.is_assigned():
                    other_terms.append(term)
        return input_terms, other_terms

    def get_main_info(self):
        return [len(self.__information.constraint_terms),
                len(self.__information.compiled_constraint_terms),
                len(self.__information.calculate_terms),
                len(self.__information.compiled_calculate_terms)]

    def check_constraint_equality(self):

        num1 = len(self.__information.constraint_terms)
        num2 = len(self.__information.compiled_constraint_terms)
        # print(f'====================================')
        print(f'circom code constraint num : {num1}')
        print(f'R1CS constraint num : {num2}')
        # print(f'====================================')
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['Circom Code Constraint Num'] = num1
            self.perf_data['R1CS Constraint Num'] = num2
            start_time = time.time()

        circom_constraint = self.__exp_slv.associativeForm(self.__information.constraint_terms)
        compiled_constraint = self.__exp_slv.associativeForm(self.__information.compiled_constraint_terms)


        if self.__polish_level == self.polish_list[0]:
            result = self.__exp_slv.check_equality(circom_constraint,
                                                 compiled_constraint,
                                                 list(self.__information.all_signals_dic.values())
                                                 )
        else:
            result = self.__exp_slv.check_implies(circom_constraint,
                                                compiled_constraint,
                                                list(self.__information.all_signals_dic.values())
                                                )
        if ModelingSettings.TABLE_OUTPUT:
            end_time = time.time()
            self.perf_data['Constraint Equality Checking Time'] = f"{end_time - start_time:.4f}"
            self.perf_data['Constraint Equivalence'] = result

        return result

    def check_calculate_equality(self):
        input_terms, other_terms = self.generate_mapping_property()

        input_equal = self.__exp_slv.associativeForm(input_terms)
        witness_equal = self.__exp_slv.associativeForm(other_terms)
        circom_calculate = self.__exp_slv.associativeForm(self.__information.calculate_terms)
        compiled_calculate = self.__exp_slv.associativeForm(self.__information.compiled_calculate_terms)

        # print(circom_calculate)
        # print(compiled_calculate)

        num1 = len(self.__information.calculate_terms)
        num2 = len(self.__information.compiled_calculate_terms)

        # print(f'====================================')
        print(f'circom code calculate num : {num1}')
        print(f'C++ calculate num : {num2}')
        # print(f'====================================')

        # colorPrint('--- detailed constraints ---', COLOR.GREEN)
        # print(input_equal)
        # print()
        # print(witness_equal)
        # print()
        # print(circom_calculate)
        # print()
        # print(compiled_calculate)

        # colorPrint('--- detailed constraints ---', COLOR.GREEN)
        
        if ModelingSettings.TABLE_OUTPUT:
            self.perf_data['Circom Code Calculate Num'] = num1
            self.perf_data['C++ Calculate Num'] = num2
            start_time = time.time()

        all_SMTs = list()
        for signal in self.__information.all_signals_dic.values():
            all_SMTs.append(signal.toSmt())
        for signal in self.__cpp_signals:
            all_SMTs.append(signal.toSmt())

        not_witness_eq = self.__exp_slv.mkTerm(Kind.NOT, witness_equal)

        # print(temp_eq)
        # temp_exp = self.__exp_slv.mkTerm(Kind.AND, compiled_calculate, self.__exp_slv.mkTerm(Kind.NOT, not_witness_eq))
        # print(temp_exp)
        # return self.__exp_slv.check_satisfy(temp_exp, smt_list)

        exp = self.__exp_slv.mkTerm(Kind.AND, input_equal, circom_calculate, compiled_calculate, not_witness_eq)

        is_satisfy = self.__exp_slv.check_satisfy(exp, all_SMTs) 
        result = not is_satisfy

        if ModelingSettings.TABLE_OUTPUT:
            end_time = time.time()
            self.perf_data['Calculate Equality Checking Time'] = f"{end_time - start_time:.4f}"
            self.perf_data['Calculation Equivalence'] = result

        return result

    def check_signal_tag_equality(self):
        if ModelingSettings.TABLE_OUTPUT:
            start_time = time.time()
            
        public_num = self.__R1CS_head_info['n_public_signals']
        record = list(range(0, public_num+1))
        for signal in self.__public_IO_signals.values():
            data = self.__sym_data[signal.sym_name][1]
            if data == -1:
                continue
            else:
                if data <= public_num:
                    record[data] = 0

        result = all(x == 0 for x in record)
        if ModelingSettings.TABLE_OUTPUT:
            end_time = time.time()
            self.perf_data['Signal Classification Consistency Checking Time'] = f"{end_time - start_time:.4f}"
            self.perf_data['Signal Classification Consistency'] = result
        return result

    @staticmethod
    def deal_ast(ast_path, exp_slv):
        with open(ast_path, 'r') as f:
            data = json.load(f)

        js_definitions = data[CBW.definitions.value]
        Template.init_definitions(js_definitions)
        Function.init_definitions(js_definitions)

        colorPrint('-- DEALING AST FILE --', COLOR.YELLOW)
        # colorPrint(f'Signals and Vars:')

        js_main_component = data[CBW.main_component.value]
        main_component = Component.main_component(js_main_component, exp_slv)

        return main_component

    @staticmethod
    def try_deal_ast(ast_path, exp_slv):
        outcome = True
        colorPrint('=========== DEALING AST FILE ===========', COLOR.GREEN)
        colorPrint(f'AST PATH : {ast_path}', COLOR.YELLOW)

        try:
            CircuitManager.deal_ast(ast_path, exp_slv)
        except Exception as e:
            colorPrint('!!!!!!!! Exception Happened !!!!!!!!', COLOR.RED)
            colorPrint(e.with_traceback(None))
            outcome = False

        # colorPrint('=========== DEALING ENDS ===========', COLOR.GREEN)
        colorPrint()
        return outcome

    def print_table_output(self):
        if not ModelingSettings.TABLE_OUTPUT:
            return

        print_order = [
            'File Name',
            'AST Generating Time',
            'AST Processing Time',
            'R1CS Processing Time',
            'C++ Processing Time',
            'Signal Classification Processing Time',
            'signal num',
            'Signal Classification Consistency Checking Time',
            'Signal Classification Consistency',
            'Circom Code Constraint Num',
            'R1CS Constraint Num',
            'Constraint Equality Checking Time',
            'Constraint Equivalence',
            'Circom Code Calculate Num',
            'C++ Calculate Num',
            'Calculate Equality Checking Time',
            'Calculation Equivalence'
        ]

        # headers = [h for k, h in print_order]

        data_row = [str(self.perf_data.get(key, 'N/A')) for key in print_order]
        
        print("\t".join(data_row))
