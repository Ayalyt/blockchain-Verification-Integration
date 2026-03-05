import sys
from slither import Slither

from ..core.analyser import synthesizer
from ..utils import expression_util, variable_util
from ..utils import unannotation_util
from ..core.enums.mode_enum import ModeEnum
from ..utils import contract_util, annotation_util
from ..core.analyser.analyser import Analyser
from ..core.enums.vulnerablity_enum import VulnerabilityEnum


# analyse the hole contract_name
def analyse_contract(sol_name, contract_name, vuln_mode = VulnerabilityEnum.confidentiality, mode=ModeEnum.normal, mode2=ModeEnum.normal):
    # init slither and target contract_name
    slither = Slither(sol_name)
    target_contract = contract_util.get_target_contract(slither, contract_name)

    # check whether synthesized before
    if mode == ModeEnum.normal and synthesizer.check_synthesized(sol_name):
        return


    # analyser configuration
    analyser = Analyser(slither)
    analyser.set_mode(mode)
    analyser.set_sol_name(sol_name)
    analyser.set_target_contract(target_contract)
    analyser.set_vuln_mode(vuln_mode)

    annotated, core_variables, security_variables = get_variable_info(target_contract, sol_name, analyser)

    analyser.set_annotated(annotated)
    analyser.set_core_variables(core_variables)
    analyser.set_security_variables(security_variables)
    analyser.set_loop_numbers(get_loop_number(target_contract, sol_name))
    analyser.set_state_variables_num(variable_util.get_state_variables_num(target_contract))
    analyser.set_unused_state_variables_num(variable_util.get_unused_state_variables_num(target_contract))
    analyser.set_parameters_num(variable_util.get_parameters_num(target_contract))
    analyser.set_unused_parameters_num(variable_util.get_unused_parameters_num(target_contract))
    analyser.set_functions_num(variable_util.get_functions_num(target_contract))


    # analyse
    analyser.check_vulnerability()
    analyser.verify_solutions()

    # synthesize
    if mode2 != ModeEnum.function1:
        analyser.synthesize()

    # compare (optional)
    analyser.print_time()
    return analyser


# get analysis variables
def get_variable_info(target_contract, sol_name, analyser):
    # get the annotated variables
    annotated_core_variables = annotation_util.get_annotated_variables(sol_name)
    # whether the contract is annotated
    annotated = False
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    scope_start = sys.maxsize
    scope_end = -sys.maxsize - 1
    for contract in contracts:
        contract_start, contract_end = expression_util.get_scope(contract)
        scope_start = min(scope_start, contract_start)
        scope_end = max(scope_end, contract_end)

    for annotated_variable in annotated_core_variables:
        if scope_start <= annotated_variable.line_number <= scope_end:
            annotated = True
            break

    if annotated:
        unannotated_core_variables, unannotated_security_variables = unannotation_util.generate_security_variables(
            target_contract, analyser)
        for i in range(len(unannotated_core_variables)):
            unannotated_core_variable = unannotated_core_variables[i]
            if not unannotated_core_variable.defined:
                for variable in annotated_core_variables:
                    if unannotated_core_variable.name == variable.name and unannotated_core_variable.line_number == variable.line_number:
                        unannotated_core_variables[i] = variable

        core_variables = annotated_core_variables.copy()
        core_variables.extend(list(set(unannotated_core_variables)-set(core_variables)))
        security_variables = annotation_util.generate_security_variables(target_contract, core_variables, analyser)
    else:
        core_variables, security_variables = unannotation_util.generate_security_variables(target_contract, analyser)

    core_variables = sorted(list(set(core_variables)), key=lambda obj: getattr(obj, 'line_number'))
    security_variables = sorted(list(set(security_variables)), key=lambda obj: getattr(obj, 'line_number'))

    return annotated, core_variables, security_variables



# get line number of loops
def get_loop_number(target_contract, sol_name):
    loop_numbers = []

    with open(sol_name) as sol_file:
        for line_number, line in enumerate(sol_file, 1):
            line = line.strip()
            if line.startswith('for') or line.startswith('while'):
                loop_numbers.append(line_number)

    return loop_numbers
