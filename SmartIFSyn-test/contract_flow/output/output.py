# implementation of OutputManager functions
from ..core.enums.color_enum import ColorEnum
from ..core.enums.expression_enum import ExpressionEnum
from ..core.enums.mode_enum import ModeEnum
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.vulnerablity_enum import VulnerabilityEnum


# print the vulnerabilities
def print_vulnerabilities(output_manager):
    vuln_num = output_manager.get_vulnerability_num()
    vuln_mode = output_manager.vuln_mode
    vuln_str = 'confidentiality' if vuln_mode == VulnerabilityEnum.confidentiality else 'integrity'
    # Total
    print("--------------------------------------------")
    if vuln_num > 0:
        print(
            f"The total number of vulnerabilities is: {vuln_num}.")
        print("--------------------------------------------")
    else:
        print(f"No vulnerabilities detected.")
        print("--------------------------------------------")
        return
    # vulnerabilities
    print("--------------------------------------------")
    if len(output_manager.vulnerabilities) >= 0:
        vuln_num = 0
        for vuln in output_manager.vulnerabilities:
            vuln_num += 1 if vuln.vulnerable_type == vuln_mode and vuln.shown else 0
        print(
            f"{vuln_num} {vuln_str} vulnerabilities "
            f"detected:")
        for vuln in output_manager.vulnerabilities:
            if vuln.vulnerable_type == vuln_mode and vuln.shown and vuln.expression_type != ExpressionEnum.local_define:
                print(
                    f"(line {vuln.line_number}):\t{vuln.expression}")
                if vuln.sub_vulnerabilities is not None:
                    for sub_vuln in vuln.sub_vulnerabilities:
                        if sub_vuln.shown and sub_vuln.vulnerable_type == vuln_mode:
                            print(f"--------------->(line {sub_vuln.line_number}): "
                                  f"{sub_vuln.expression}")
    else:
        print(f"No {vuln_str} vulnerabilities detected.")
    print("--------------------------------------------")


# print solutions
def print_solutions(output_manager):
    vuln_num = output_manager.get_vulnerability_num()
    vuln_mode = output_manager.vuln_mode
    vuln_str = 'confidentiality' if vuln_mode == VulnerabilityEnum.confidentiality else 'integrity'
    if vuln_num == 0:
        return
    print("--------------------------------------------")
    solutions = output_manager.solutions
    if solutions:
        print(f"One optimal solution:")
        optimal_solution = solutions[0]
        optimal_solution = {k: optimal_solution[k] for k in sorted(optimal_solution, key=lambda obj: obj.line_number)}
        max_name_length = max(len(obj.name) for obj in optimal_solution) + 5
        for obj, value in optimal_solution.items():
            if not obj.defined:
                aligned_value = obj.name.ljust(max_name_length)
                security_level = SecurityEnum.H.value if value else SecurityEnum.L.value
                print(f"(line {obj.line_number}):\t{aligned_value}"
                      f"{security_level}")
    else:
        print(f"No {vuln_str} solutions found.")

    print("--------------------------------------------")


# print total analyse time
def print_analyse_time(output_manager, mode):
    if mode == ModeEnum.normal:
        print(f"Time: {round(output_manager.total_time, 4)}")
        print("--------------------------------------------")
    elif mode == ModeEnum.compare:
        print("--------------------------------------------")
        print(f"Analyse time: {round(output_manager.total_time, 4)}")
        print("--------------------------------------------")




# print synthesized contract
def print_syn_contract(output_manager):
    print(f"Modified contract saved as {output_manager.syn_contract_path}")
    print("--------------------------------------------")