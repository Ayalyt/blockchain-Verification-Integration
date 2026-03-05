# class analyser
import time
from . import verify, synthesizer
from . import analyse
from ..enums.mode_enum import ModeEnum
from ..enums.security_enum import SecurityEnum
from ..enums.vulnerablity_enum import VulnerabilityEnum
from ..variables.control_flow import ControlFlow
from ...output.OutputManager import OutputManager


class Analyser:
    def __init__(self, slither):
        self.annotated = False
        self.slither = slither
        self.sol_name = ''
        self.target_contract = None
        self.security_variables = []
        self.core_variables = []
        self.output_manager = OutputManager()
        self.vulnerabilities = []
        self.solutions = []
        self.mode = ModeEnum.normal
        self.vuln_mode = VulnerabilityEnum.confidentiality
        self.loop_numbers = []
        self.control_flows = [ControlFlow(SecurityEnum.L)]
        self.check_vuln_time = 0.0
        self.verify_time = 0.0
        self.compared_time = 0.0
        self.compared_timeout = False
        self.z3_vars = {}
        self.state_variables_num = 0
        self.unused_state_variables_num = 0
        self.parameters_num = 0
        self.unused_parameters_num = 0
        self.functions_num = 0
        self.solver = None


    # set mode
    def set_mode(self, mode):
        self.mode = mode

    # set target contract_name
    def set_target_contract(self, target_contract):
        self.target_contract = target_contract

    # set sol_name
    def set_sol_name(self, sol_name):
        self.sol_name = sol_name

    # set security variables
    def set_security_variables(self, security_variables):
        self.security_variables = security_variables

    # set output manager
    def set_output_manager(self, output_manager):
        self.output_manager = output_manager

    # set annotated
    def set_annotated(self, annotated):
        self.annotated = annotated

    # set core_variables
    def set_core_variables(self, core_variables):
        self.core_variables = core_variables

    # set vulnerabilities
    def set_vulnerabilities(self, vulnerabilities):
        self.vulnerabilities = vulnerabilities
        self.output_manager.set_vulnerabilities(vulnerabilities)

    # set solutions
    def set_solutions(self, solutions):
        self.solutions = solutions
        self.output_manager.solutions = solutions

    # set vuln mode
    def set_vuln_mode(self, vuln_mode):
        self.vuln_mode = vuln_mode
        self.output_manager.vuln_mode = vuln_mode

    # set loop numbers
    def set_loop_numbers(self, loop_numbers):
        self.loop_numbers = loop_numbers

    # set time
    def set_check_vuln_time(self, check_vuln_time):
        self.check_vuln_time = check_vuln_time

    # set verify_time
    def set_verify_time(self, verify_time):
        self.verify_time = verify_time


    # set state variables num
    def set_state_variables_num(self, var_num):
        self.state_variables_num = var_num

    # set unused state variables num
    def set_unused_state_variables_num(self, var_num):
        self.unused_state_variables_num = var_num

    # set parameters num
    def set_parameters_num(self, para_num):
        self.parameters_num = para_num

    # set unused parameters num
    def set_unused_parameters_num(self, para_num):
        self.unused_parameters_num = para_num

    # set function num
    def set_functions_num(self, fun_num):
        self.functions_num = fun_num

    # set solver
    def set_solver(self, solver):
        self.solver = solver

    # check the vulnerability of information flow
    def check_vulnerability(self):
        # configuration
        start_time = time.time()
        vulnerabilities = analyse.check_vulnerability(self)
        end_time = time.time()
        self.set_vulnerabilities(vulnerabilities)
        self.set_check_vuln_time(end_time - start_time)
        if self.mode == ModeEnum.normal:
            self.output_manager.print_vulnerabilities()

    # verify solutions
    def verify_solutions(self):
        start_time = time.time()
        solutions, z3_vars = verify.verify_vulnerability(self)
        end_time = time.time()
        self.z3_vars = z3_vars
        self.set_solutions(solutions)
        self.set_verify_time(end_time - start_time)
        if self.mode == ModeEnum.normal:
            self.output_manager.print_solutions()

    # print time
    def print_time(self):
        self.output_manager.set_total_time(self)
        self.output_manager.set_compared_time(self)
        self.output_manager.set_compared_timeout(self)
        self.output_manager.print_analyse_time(self.mode)


    # synthesize contract
    def synthesize(self):
        if self.mode == ModeEnum.normal:
            total_num = 0
            for vuln in self.vulnerabilities:
                total_num += 1 if vuln.vulnerable_type != VulnerabilityEnum.none and vuln.shown else 0
            if total_num > 0 :
                syn_contract_path = synthesizer.generate_secure_contract(self)
                self.output_manager.set_syn_contract_path(syn_contract_path)
                self.output_manager.print_syn_contract()
