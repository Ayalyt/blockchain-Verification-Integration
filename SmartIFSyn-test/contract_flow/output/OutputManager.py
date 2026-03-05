# class OutputManager
from ..output import output
from ..core.enums.vulnerablity_enum import VulnerabilityEnum


class OutputManager:
    def __init__(self):
        self.vulnerabilities = []
        self.solutions = []
        self.syn_contract_path = ''
        self.total_time = 0.0
        self.compared_time = 0.0
        self.compared_timeout = False
        self.vuln_mode = VulnerabilityEnum.confidentiality

    # set vulnerabilities
    def set_vulnerabilities(self, leaks):
        self.vulnerabilities = leaks

    # set  solutions
    def set_solutions(self, solutions):
        self.solutions = solutions

    # set syn contract path
    def set_syn_contract_path(self, syn_contract_path):
        self.syn_contract_path = syn_contract_path

    # set vuln_mode
    def set_vuln_mode(self, vuln_time):
        self.vuln_mode = vuln_time

    # get total number of vulnerabilities
    def get_vulnerability_num(self):
        total_num = 0
        for vuln in self.vulnerabilities:
            total_num += 1 if vuln.vulnerable_type != VulnerabilityEnum.none and vuln.shown else 0
        return total_num

    # print the leaks
    def print_vulnerabilities(self):
        output.print_vulnerabilities(self)

    # print solutions
    def print_solutions(self):
        output.print_solutions(self)

    # print syn contract
    def print_syn_contract(self):
        output.print_syn_contract(self)

    # print analyse time
    def print_analyse_time(self, mode):
        output.print_analyse_time(self, mode)

    # set total time
    def set_total_time(self, analyser):
        self.total_time = analyser.check_vuln_time + analyser.verify_time

    # set compared time
    def set_compared_time(self, analyser):
        self.compared_time =  analyser.check_vuln_time + analyser.compared_time

    # set compared timeout
    def set_compared_timeout(self, analyser):
        self.compared_timeout = analyser.compared_timeout
