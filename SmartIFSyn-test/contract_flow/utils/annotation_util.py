# functions of annotation
import re
import copy
from ..core.analyser import analyse
from ..core.enums.expression_enum import ExpressionEnum
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.constant_enum import ConstantEnum
from ..core.enums.location_enum import LocationEnum
from ..core.variables.security_variable import SecurityVariable
from ..utils import analyse_util
from ..utils import lattice_util
from ..utils import expression_util


# get the annotated variables
def get_annotated_variables(sol_name):
    annotated_variables = []
    anno_pattern = r'@name\s+(.*?)\s+@anno\s+(.*?)$'
    re_pattern = r'@reserved'

    with open(sol_name) as sol_file:
        for line_number, line in enumerate(sol_file, 1):
            line = line.strip()
            if len(line.split('//')) > 1:
                annotations = line.split('//')[1].split(',')
                for annotation in annotations:
                    reserved = False
                    if re.search(re_pattern, annotation):
                        annotation = re.sub(re_pattern, '', annotation)
                        reserved = True

                    anno_match = re.search(anno_pattern, annotation)
                    if anno_match:
                        variable_name = anno_match.group(1)
                        security_level = SecurityEnum.H if anno_match.group(2).replace(" ",
                                                                                      "") == 'H' else SecurityEnum.L
                        security_variable = SecurityVariable(variable_name, security_level, line_number, None, reserved, True)
                        annotated_variables.append(security_variable)

    return annotated_variables


# construct security variables with annotated variables
def generate_security_variables(target_contract, annotated_variables, analyser):
    security_variables = []
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)

    security_variables.extend(generate_variables(contracts, annotated_variables))
    security_variables.extend(generate_parameters(contracts, annotated_variables))
    security_variables.extend(generate_enums(contracts, annotated_variables))
    security_variables.extend(generate_constants(contracts, annotated_variables))
    security_variables.extend(generate_variables_defined_in_function(contracts, security_variables, analyser))
    security_variables = update_rvalues_security_level(security_variables)

    return list(set(security_variables))


# generate variables defined in the contract
def generate_variables(contracts, annotated_variables):
    security_variables = []
    for annotated_variable in annotated_variables:
        for contract in contracts:
            for variable in contract.variables:
                line_number = expression_util.get_line_number(variable)
                if annotated_variable.line_number == line_number and annotated_variable.name == variable.name:
                    reference_number_list = []
                    for reference in variable.references:
                        reference_number = int(str(reference).split('#')[1])
                        reference_number_list.append(reference_number)
                    reference_number_list = list(set(reference_number_list))
                    for reference_number in reference_number_list:
                        security_variable = SecurityVariable(annotated_variable.name, annotated_variable.security_level,
                                                             reference_number, annotated_variable,
                                                             annotated_variable.reserved, annotated_variable.annotated)
                        security_variable.set_is_storage(True)
                        security_variables.append(security_variable)
                    security_variable = annotated_variable.copy()
                    security_variable.set_source(annotated_variable)
                    security_variables.append(security_variable)

    return list(set(security_variables))


# generate parameters defined in the contract
def generate_parameters(contracts, annotated_variables):
    security_variables = []
    for annotated_variable in annotated_variables:
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
                    if annotated_variable.line_number == line_number and annotated_variable.name == parameter.name:
                        reference_number_list = []
                        for reference in parameter.references:
                            reference_number = int(str(reference).split('#')[1])
                            reference_number_list.append(reference_number)
                        reference_number_list = list(set(reference_number_list))
                        for reference_number in reference_number_list:
                            security_variable = SecurityVariable(annotated_variable.name,
                                                                 annotated_variable.security_level, reference_number,
                                                                 annotated_variable, annotated_variable.reserved, annotated_variable.annotated)
                            security_variable.set_is_storage(parameter.is_storage)
                            security_variables.append(security_variable)

    return list(set(security_variables))


# generate enums defined in the contract by users
def generate_enums(contracts, annotated_variables):
    security_variables = []
    for annotated_variable in annotated_variables:
        for contract in contracts:
            for enum in contract.enums:
                line_number = expression_util.get_line_number(enum)
                if annotated_variable.line_number == line_number and annotated_variable.name == enum.name:
                    reference_number_list = []
                    for reference in enum.references:
                        reference_number = int(str(reference).split('#')[1])
                        reference_number_list.append(reference_number)
                    reference_number_list = list(set(reference_number_list))
                    for reference_number in reference_number_list:
                        security_variable = SecurityVariable(annotated_variable.name, annotated_variable.security_level,
                                                             reference_number, annotated_variable,
                                                             annotated_variable.reserved, annotated_variable.annotated)
                        security_variables.append(security_variable)
                    security_variable = annotated_variable.copy()
                    security_variable.set_source(annotated_variable)
                    security_variables.append(security_variable)

    return list(set(security_variables))


# generate constants defined in the contract by users
def generate_constants(contracts, annotated_variables):
    security_variables = []
    for annotated_variable in annotated_variables:
        for contract in contracts:
            library_functions = [call[1] for call in contract.all_library_calls]
            contract_functions = contract.functions
            contract_modifiers = contract.modifiers
            contract_functions.extend(library_functions)
            contract_functions.extend(contract_modifiers)
            for function in contract_functions:
                in_function = False
                for node in function.nodes:
                    if node.expression:
                        line_number = expression_util.get_line_number(node.expression)
                        for constant in ConstantEnum:
                            if annotated_variable.line_number == line_number and constant.value == annotated_variable.name:
                                in_function = True
                                if constant.value == 'balance' and 'address(this).balance' not in str(node.expression):
                                    in_function = False
                if in_function:
                    reference_number_list = []
                    for node in function.nodes:
                        if node.expression and bool(
                                re.findall(rf'\b{annotated_variable.name}\b', str(node.expression))):
                            reference_number = expression_util.get_line_number(node.expression)
                            reference_number_list.append(reference_number)
                        reference_number_list = list(set(reference_number_list))
                    if not reference_number_list:
                        reference_number_list.append(annotated_variable.line_number)
                    for reference_number in reference_number_list:
                        security_variable = SecurityVariable(annotated_variable.name, annotated_variable.security_level,
                                                             reference_number, annotated_variable,
                                                             annotated_variable.reserved, annotated_variable.annotated)
                        security_variables.append(security_variable)

    return list(set(security_variables))


# generate user define variable
def generate_variables_defined_in_function(contracts, sec_variables, analyser):
    slither_function_list = ['slitherConstructorConstantVariables', 'slitherConstructorVariables']

    security_variables = []
    for contract in contracts:
        variables = copy.deepcopy(sec_variables)
        # get user defined variables
        library_functions = [call[1] for call in contract.all_library_calls]
        contract_functions = contract.functions
        contract_modifiers = contract.modifiers
        contract_functions.extend(library_functions)
        contract_functions.extend(contract_modifiers)
        contract_functions = sorted(contract_functions, key=expression_util.get_line_number)
        for function in contract_functions:
            vulnerabilities = []
            return_first = []
            defined_variables = []
            defined_security_variables = []
            if_nodes = expression_util.line_number_in_if(function)
            if_line_numbers = if_nodes.keys()
            if function.name in slither_function_list:
                continue
            for variable in function.variables:
                if str(variable.name) == '':
                    continue
                is_parameter = False
                line_number = expression_util.get_line_number(variable)
                for parameter in function.parameters:
                    parameter_line_number = expression_util.get_line_number(parameter)
                    if variable.name == parameter.name and line_number == parameter_line_number:
                        is_parameter = True
                        break
                if not is_parameter:
                    defined_variable = SecurityVariable(str(variable.name), SecurityEnum.L, line_number, None, False, False,
                                                        True,
                                                        (function.name, expression_util.get_line_number(function)))
                    defined_variable.set_location(
                        LocationEnum.storage if str(variable.location) == 'storage' else LocationEnum.memory)
                    defined_variables.append(defined_variable)
            variables.extend(defined_variables)

            # generate temp security variables by reference
            for defined_variable in defined_variables:
                reference_number_list = []
                for node in function.nodes:
                    if node.expression and bool(re.findall(rf'\b{defined_variable.name}\b', str(node.expression))):
                        reference_number = expression_util.get_line_number(node.expression)
                        reference_number_list.append(reference_number)
                    reference_number_list = list(set(reference_number_list))
                for reference_number in reference_number_list:
                    security_variable = SecurityVariable(defined_variable.name, defined_variable.security_level,
                                                         reference_number, None, False, False, True,
                                                         (function.name, expression_util.get_line_number(function)),
                                                         defined_variable.rvalues, defined_variable.location)
                    defined_security_variables.append(security_variable)
            variables.extend(defined_security_variables)
            # generate security variables
            for defined_variable in defined_variables:
                for security_variable in defined_security_variables:
                    for node in function.nodes:
                        expression_type = node.expression.__class__.__name__
                        if (expression_type == 'AssignmentOperation' and security_variable.line_number ==
                                expression_util.get_line_number(node.expression) and
                                security_variable.name == defined_variable.name):
                            expression_left_type = node.expression.expression_left.__class__.__name__
                            vuln = analyse.analyse_assignment(function, node, variables, analyser)
                            if vuln:
                                for v_index in range(len(vuln)):
                                    v = vuln[v_index]
                                    if v.lvalues and v.rvalues and v.expression_type == ExpressionEnum.local_define:
                                        lvalue = v.lvalues[0]
                                        rvalues = v.rvalues
                                        if security_variable.line_number == lvalue.line_number:
                                            v.set_left_expression_type(expression_left_type)
                                            if expression_left_type == 'MemberAccess' and lattice_util.upper(
                                                    lvalue.security_level, lattice_util.lowest_upper_bound(rvalues)):
                                                continue
                                            lub = lattice_util.lowest_upper_bound(rvalues)

                                            if lub != lvalue.security_level:
                                                vuln[v_index].lvalues[0].set_security_level(lub)
                                                security_variable.set_security_level(lub)

                                            if security_variable.location != LocationEnum.storage or len(
                                                    vulnerabilities) == 0 or v.define_type == ExpressionEnum.unpack_define:
                                                vulnerabilities.append(v)
                                            for i in range(len(variables)):
                                                var = variables[i]
                                                if var.name == security_variable.name and var.line_number >= security_variable.line_number \
                                                        and var.function == security_variable.function and var.function[0] == function.name:
                                                    variables[i].set_security_level(security_variable.security_level)
                                                    variables[i].set_source(security_variable)
                                                    variables[i].set_rvalues(security_variable.rvalues)
                        elif expression_type == 'Identifier' and security_variable.line_number == expression_util.get_line_number(
                                function):
                            return_first.append(security_variable)
                    if security_variable.name == defined_variable.name:
                        if security_variable.line_number in if_line_numbers:
                            security_variable.set_in_if(True)
                        security_variables.append(copy.deepcopy(security_variable))
                        security_variables = sorted(list(set(security_variables)),
                                                    key=lambda obj: getattr(obj, 'line_number'))

                vulnerabilities = analyse_util.vulnerability_branch_merge(vulnerabilities)
                vulnerabilities = sorted(vulnerabilities, key=lambda obj: getattr(obj, 'line_number'))
                for vuln in vulnerabilities:
                    if (vuln.lvalues[0].location != LocationEnum.storage and len(vuln.lvalues) > 1
                            and re.search(r'\w+\[[^]]+]', str(vuln.expression)) is not None):
                        is_local_array = False
                        for sec_variable in security_variables:
                            if sec_variable.name == vuln.lvalues[0].name and sec_variable.line_number == vuln.lvalues[
                                0].line_number and lattice_util.upper(sec_variable.security_level,
                                                                      lattice_util.lowest_upper_bound(vuln.rvalues)):
                                is_local_array = True
                                break
                        if is_local_array:
                            continue

                    for security_variable in security_variables:
                        lvalue = vuln.lvalues[0]

                        for r_index in range(len(vuln.rvalues)):
                            rvalue = vuln.rvalues[r_index]
                            for variable in security_variables:
                                if (variable.name == rvalue.name and variable.line_number == rvalue.line_number and
                                        variable.if_set and rvalue.function == lvalue.function):
                                    vuln.rvalues[r_index].set_security_level(variable.security_level)
                                if (variable.name == rvalue.name and variable.line_number == rvalue.line_number and
                                        variable.if_source and rvalue.function == lvalue.function):
                                    vuln.rvalues[r_index].set_security_level(variable.security_level)

                        rvalues = vuln.rvalues
                        if lvalue.name == security_variable.name and lvalue.line_number == security_variable.line_number:
                            lub = lattice_util.lowest_upper_bound(rvalues)

                            if lub != lvalue.security_level:
                                if not (vuln.left_expression_type == 'MemberAccess' and lattice_util.upper(
                                        lvalue.security_level, lub)):
                                    security_variable.set_security_level(lub)
                                    lvalue.set_security_level(lub)
                            for rvalue in rvalues:
                                if rvalue.rvalues:
                                    if not security_variable.rvalues:
                                        security_variable.rvalues = []
                                    security_variable.rvalues.extend(rvalue.rvalues)
                                    security_variable.rvalues = list(set(security_variable.rvalues))
                            for i in range(len(security_variables)):
                                if_branch_num = 0
                                var = security_variables[i]
                                if var.name == security_variable.name and var.line_number >= security_variable.line_number \
                                        and var.function == security_variable.function:
                                    # on difference branch
                                    if security_variable.in_if and var.in_if and var.line_number > security_variable.line_number \
                                            and not expression_util.is_line_number_in_descendants(if_nodes[security_variable.line_number], var.line_number):
                                        continue
                                    # choose H branch
                                    if security_variable.in_if and not var.in_if:
                                        security_variables[i].append_if_source(security_variable)
                                        if_branch_num += 1
                                        if lattice_util.upper(security_variable.security_level, var.security_level):
                                            security_variables[i].set_security_level(security_variable.security_level)
                                            security_variables[i].set_source(security_variable)
                                            security_variables[i].set_rvalues(security_variable.rvalues)
                                            security_variables[i].set_if_set(True)
                                        if not security_variables[i].if_set and if_branch_num > 1:
                                            security_variables[i].set_security_level(lvalue.security_level)
                                            security_variables[i].set_source(security_variable)
                                            security_variables[i].set_rvalues(security_variable.rvalues)
                                    else:
                                        if vuln.define_type == ExpressionEnum.binary_define:
                                            security_variables[i].security_level = lattice_util.lowest_upper_bound([security_variables[i], lvalue])
                                        else:
                                            security_variables[i].set_security_level(lvalue.security_level)
                                        # index
                                        if len(vuln.lvalues) != 1:
                                            continue
                                        # binary define
                                        if vuln.define_type == ExpressionEnum.binary_define:
                                            continue
                                        security_variables[i].set_source(security_variable)
                                        security_variables[i].set_rvalues(security_variable.rvalues)
                                        var = security_variables[i]
                                        for v_i in range(len(vulnerabilities)):
                                            v_vuln = vulnerabilities[v_i]
                                            if v_vuln.line_number == var.line_number:
                                                for r_i in range(len(v_vuln.rvalues)):
                                                    if v_vuln.rvalues[r_i].name == var.name:
                                                        vulnerabilities[v_i].rvalues[r_i].set_security_level(var.security_level)

                for var in return_first:
                    for i in range(len(security_variables)):
                        variable = security_variables[i]
                        lub = SecurityEnum.L
                        if variable.name == var.name and variable.line_number == var.line_number and \
                                var.function[0] == function.name and var.function[1] == expression_util.get_line_number(
                            function):
                            last_sec_variable = None
                            for sec_variable in security_variables:
                                if sec_variable.name == var.name and sec_variable.function[0] == function.name:
                                    last_sec_variable = sec_variable
                                    if lattice_util.upper(sec_variable.security_level, lub):
                                        lub = SecurityEnum.H
                            security_variables[i].set_source(last_sec_variable)
                            security_variables[i].set_rvalues(last_sec_variable.rvalues)
                            security_variables[i].set_security_level(lub)

    return list(set(security_variables))


# generate functions
def generate_functions(contracts, annotated_variables):
    security_variables = []

    for annotated_variable in annotated_variables:
        for contract in contracts:
            library_functions = [call[1] for call in contract.all_library_calls]
            contract_functions = contract.functions
            contract_functions.extend(library_functions)
            for function in contract_functions:
                line_number = expression_util.get_line_number(function)
                if function.name == annotated_variable.name and line_number == annotated_variable.line_number:
                    security_variables.append(
                        SecurityVariable(annotated_variable.name, annotated_variable.security_level, line_number,
                                         annotated_variable, annotated_variable.reserved, annotated_variable.annotated))
                    reference_number_list = []
                    for reference in function.references:
                        reference_number = int(str(reference).split('#')[1])
                        reference_number_list.append(reference_number)
                    reference_number_list = list(set(reference_number_list))
                    for reference_number in reference_number_list:
                        security_variable = SecurityVariable(annotated_variable.name, annotated_variable.security_level,
                                                             reference_number, annotated_variable,
                                                             annotated_variable.reserved, annotated_variable.annotated)
                        security_variables.append(security_variable)

    return list(set(security_variables))


def update_rvalues_security_level(security_variables):
    variable_dir = {}
    for variable in security_variables:
        variable_dir[variable.name+str(variable.line_number)] = variable
    for i in range(len(security_variables)):
        variable = security_variables[i]
        if variable.rvalues:
            for j in range(len(variable.rvalues)):
                rvalue = variable.rvalues[j]
                if rvalue.function == variable.function:
                    security_variables[i].rvalues[j].security_level = variable_dir[rvalue.name + str(rvalue.line_number)].security_level

    return security_variables

