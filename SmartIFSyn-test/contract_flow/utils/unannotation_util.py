# variable utils
import re

from ..utils import expression_util
from ..utils import annotation_util
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.constant_enum import ConstantEnum
from ..core.enums.vulnerablity_enum import VulnerabilityEnum
from ..core.variables.security_variable import SecurityVariable


# construct security variables with unannotated variables
def generate_security_variables(target_contract, analyser):
    security_variables = []
    core_variables = []
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)

    core_vars, sec_vars = generate_variables(contracts, analyser)
    core_paras, sec_paras = generate_parameters(contracts, analyser)
    core_enums, sec_enums = generate_enums(contracts)
    core_consts, sec_consts = generate_constants(contracts, analyser)

    core_variables.extend(core_vars)
    core_variables.extend(core_paras)
    core_variables.extend(core_enums)
    core_variables.extend(core_consts)
    security_variables.extend(sec_vars)
    security_variables.extend(sec_paras)
    security_variables.extend(sec_enums)
    security_variables.extend(sec_consts)
    security_variables.extend(annotation_util.generate_variables_defined_in_function(contracts, security_variables, analyser))

    return list(set(core_variables)), list(set(security_variables))


# generate variables defined in the contract
def generate_variables(contracts, analyser):
    security_variables = []
    core_variables = []
    for contract in contracts:
        variables = contract.variables
        analyser.state_variables_num += len(variables)
        for variable in variables:
            if analyser.vuln_mode == VulnerabilityEnum.confidentiality:
                keywords = ['guess', 'key', 'password', 'secret']
                security_level = SecurityEnum.H if ((variable.visibility == 'private' or variable.visibility == 'external')
                                                   and any(k in variable.name for k in keywords)) else SecurityEnum.L
            else:
                security_level = SecurityEnum.L
            line_number = expression_util.get_line_number(variable)
            unannotated_variable = SecurityVariable(str(variable.name), security_level, line_number, None, False)
            unannotated_variable.set_is_storage(True)
            core_variables.append(unannotated_variable)
            reference_number_list = []
            for reference in variable.references:
                reference_number = int(str(reference).split('#')[1])
                reference_number_list.append(reference_number)
            reference_number_list = list(set(reference_number_list))
            for reference_number in reference_number_list:
                security_variable = SecurityVariable(str(variable.name), security_level, reference_number,
                                                     unannotated_variable, False)
                security_variable.set_is_storage(True)
                security_variables.append(security_variable)
            security_variable = unannotated_variable.copy()
            security_variable.set_source(unannotated_variable)
            security_variables.append(security_variable)

    return list(set(core_variables)), list(set(security_variables))


# generate parameters defined in the contract
def generate_parameters(contracts, analyser):
    security_variables = []
    core_variables = []
    for contract in contracts:
        library_functions = [call[1] for call in contract.all_library_calls]
        contract_functions = contract.functions
        contract_modifiers = contract.modifiers
        contract_functions.extend(library_functions)
        contract_functions.extend(contract_modifiers)
        for function in contract_functions:
            for parameter in function.parameters:
                if parameter.name == '':
                    continue
                line_number = expression_util.get_line_number(parameter)
                if analyser.vuln_mode == VulnerabilityEnum.confidentiality:
                    keywords = ['guess', 'key', 'password', 'secret']
                    security_level = SecurityEnum.H if ((function.visibility == 'public' or function.visibility == 'external')
                                                       and any(k in parameter.name for k in keywords)) else SecurityEnum.L
                elif function.is_constructor:
                    security_level = SecurityEnum.L
                else:
                    security_level = SecurityEnum.H if function.visibility == 'public' or function.visibility == 'external' \
                        else SecurityEnum.L
                unannotated_variable = SecurityVariable(str(parameter.name), security_level, line_number, None, False)
                unannotated_variable.set_is_storage(parameter.is_storage)
                core_variables.append(unannotated_variable)
                reference_number_list = []
                for reference in parameter.references:
                    reference_number = int(str(reference).split('#')[1])
                    reference_number_list.append(reference_number)
                reference_number_list = list(set(reference_number_list))
                for reference_number in reference_number_list:
                    security_variable = SecurityVariable(str(parameter.name), security_level, reference_number,
                                                         unannotated_variable, False)
                    security_variable.set_is_storage(parameter.is_storage)
                    security_variables.append(security_variable)

    return list(set(core_variables)), list(set(security_variables))


# generate enums in the contract
def generate_enums(contracts):
    security_variables = []
    core_variables = []
    for contract in contracts:
        enums = contract.enums
        for enum in enums:
            security_level = SecurityEnum.L
            line_number = expression_util.get_line_number(enum)
            unannotated_variable = SecurityVariable(str(enum.name), security_level, line_number, None)
            core_variables.append(unannotated_variable)
            reference_number_list = []
            for reference in enum.references:
                reference_number = int(str(reference).split('#')[1])
                reference_number_list.append(reference_number)
            reference_number_list = list(set(reference_number_list))
            for reference_number in reference_number_list:
                security_variable = SecurityVariable(str(enum.name), security_level, reference_number,
                                                     unannotated_variable, False)
                security_variables.append(security_variable)
            security_variable = unannotated_variable.copy()
            security_variable.set_source(unannotated_variable)
            security_variables.append(security_variable)

    return list(set(core_variables)), list(set(security_variables))


# generate constants defined in the contract
def generate_constants(contracts, analyser):
    security_variables = []
    core_variables = []
    security_level = SecurityEnum.L if analyser.vuln_mode == VulnerabilityEnum.confidentiality else (
        SecurityEnum.H)
    for contract in contracts:
        library_functions = [call[1] for call in contract.all_library_calls]
        contract_functions = contract.functions
        contract_modifiers = contract.modifiers
        contract_functions.extend(library_functions)
        contract_functions.extend(contract_modifiers)
        for function in contract_functions:
            first_occurrences = {constant: -1 for constant in ConstantEnum}
            for node in function.nodes:
                for constant in ConstantEnum:
                    if check_expression(str(node.expression), constant.value) and first_occurrences[constant] == -1:
                        first_occurrences[constant] = expression_util.get_line_number(node.expression)

            if not all(value == -1 for value in first_occurrences.values()):
                for constant, line_number in first_occurrences.items():
                    if line_number != -1:
                        reference_number_list = []
                        first_security_level = SecurityEnum.L if get_constant_security_level(contract, function, constant, line_number) else security_level
                        unannotated_variable = SecurityVariable(constant.value, first_security_level, line_number, None,
                                                                False)
                        core_variables.append(unannotated_variable)
                        for node in function.nodes:
                            if node.expression and bool(re.findall(rf'\b{constant.value}\b', str(node.expression))):
                                reference_number = expression_util.get_line_number(node.expression)
                                if not (constant.value == ConstantEnum.balance.value and 'address(this).balance' not in str(node.expression)):
                                    reference_number_list.append(reference_number)
                            reference_number_list = list(set(reference_number_list))
                        for reference_number in reference_number_list:
                            reference_security_level = SecurityEnum.L if get_constant_security_level(contract, function, constant, line_number) else security_level
                            security_variable = SecurityVariable(constant.value, reference_security_level,
                                                                 reference_number, unannotated_variable, False)
                            security_variables.append(security_variable)

    return list(set(core_variables)), list(set(security_variables))


# generate functions
def generate_functions(contracts, analyser):
    slither_function_list = ['slitherConstructorConstantVariables', 'slitherConstructorVariables']
    security_variables = []
    core_variables = []
    for contract in contracts:
        library_functions = [call[1] for call in contract.all_library_calls]
        contract_functions = contract.functions
        contract_functions.extend(library_functions)
        for function in contract_functions:
            if function.name not in slither_function_list:
                if analyser.vuln_mode == VulnerabilityEnum.confidentiality:
                    security_level = SecurityEnum.L if (function.visibility == 'public' or function.visibility ==
                                                       'external') else SecurityEnum.H
                elif not function.parameters:
                    security_level = SecurityEnum.L
                else:
                    security_level = SecurityEnum.H if (function.visibility == 'public' or function.visibility ==
                                                       'external') else SecurityEnum.L
                line_number = expression_util.get_line_number(function)
                unannotated_variable = SecurityVariable(str(function.name), security_level, line_number, None, False)
                core_variables.append(unannotated_variable)
                reference_number_list = []
                for reference in function.references:
                    reference_number = int(str(reference).split('#')[1])
                    reference_number_list.append(reference_number)
                reference_number_list = list(set(reference_number_list))
                for reference_number in reference_number_list:
                    security_variable = SecurityVariable(str(function.name), security_level, reference_number,
                                                         unannotated_variable, False)
                    security_variables.append(security_variable)

    for core_var in core_variables:
        security_variable = SecurityVariable(core_var.name, core_var.security_level, core_var.line_number, core_var,
                                             False)
        security_variables.append(security_variable)

    return list(set(core_variables)), list(set(security_variables))


# check bool expression
def check_expression(expression, value):
    found = False
    exist_pattern = rf'\b{value}\b'
    bool_patterns = [
        rf'\b{value}\b\s*<=\s*[\w\[\]\.]+',  # variable <= something
        rf'[\w\[\]\.]+\s*<=\s*\b{value}\b',  # something <= variable
        rf'\b{value}\b\s*>=\s*[\w\[\]\.]+',  # variable >= something
        rf'[\w\[\]\.]+\s*>=\s*\b{value}\b',  # something >= variable
        rf'\b{value}\b\s*==\s*[\w\[\]\.]+',  # variable == something
        rf'[\w\[\]\.]+\s*==\s*\b{value}\b',  # something == variable
        rf'\b{value}\b\s*!=\s*[\w\[\]\.]+',  # variable != something
        rf'[\w\[\]\.]+\s*!=\s*\b{value}\b',  # something != variable
        rf'\b{value}\b\s*<\s*[\w\[\]\.]+',   # variable < something
        rf'[\w\[\]\.]+\s*<\s*\b{value}\b',   # something < variable
        rf'\b{value}\b\s*>\s*[\w\[\]\.]+',   # variable > something
        rf'[\w\[\]\.]+\s*>\s*\b{value}\b'    # something > variable
    ]

    if re.search(exist_pattern, expression):
        if not expression.startswith('require(bool)'):
            found = True
            for pattern in bool_patterns:
                if re.search(pattern, expression) and not value.startswith('block.'):
                    found = False
            if value == 'balance' and 'address(this).balance' not in expression:
                found = False
        else:
            found = True

    return found


def get_constant_security_level(contract, function, constant, line_number):
    if constant == ConstantEnum.balance or constant == ConstantEnum.this:
        is_low = True
    elif constant.value.startswith('block') or constant == ConstantEnum.now:
        is_low = False
    elif function.is_constructor:
            is_low = True
    elif str(function.visibility) == 'internal' or str(function.visibility) == 'private':
        is_low = True
    else:
        is_low = False
        for variable in contract.variables:
            if expression_util.get_line_number(variable) == line_number:
                is_low = True
                break


    return is_low
