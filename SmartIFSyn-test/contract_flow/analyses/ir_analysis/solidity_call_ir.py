# different ir functions of ir_type 'SolidityCall'
from ...core.enums.expression_enum import ExpressionEnum
from ...core.enums.security_enum import SecurityEnum
from ...core.enums.vulnerablity_enum import VulnerabilityEnum
from ...core.variables.ir_variable import IRVariable
from ...core.variables.security_variable import SecurityVariable
from ...core.vulnerability.vulnerability import Vulnerability
from ...utils import lattice_util, analyse_util


# ir_function_name == 'balance(address)'
def balance(security_variables, line_number, ir, ir_dict):
    argument_list = ['balance']
    argument_list.extend(ir.arguments)


    for argument in argument_list:
        for variable in security_variables:
            if variable.name == str(argument) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for argument in argument_list:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)

    if str(ir.lvalue) not in ir_dict:
        arguments = [ir_dict[str(argument)].security_variable for argument in argument_list]
        lub = lattice_util.lowest_upper_bound(arguments)
        security_variable = SecurityVariable(str(ir.lvalue), lub, line_number, None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable([ir_dict[str(argument)] for argument in argument_list])

    return ir_dict


# ir_function_name == 'abi.encode', 'keccak256', 'abi.encodeWithSignature', 'blockhash', 'sha3'
# 'abi.encodePacked()'
def argument_solidity_call(security_variables, line_number, ir, ir_dict):
    for argument in ir.arguments:
        for security_variable in security_variables:
            if argument.name == security_variable.name and security_variable.line_number == line_number:
                ir_dict[str(argument)] = IRVariable(security_variable, True)
    for argument in ir.arguments:
        if argument.name not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        security_arguments = [ir_dict[str(argument)] for argument in ir.arguments]
        lub_list = [ir_dict[str(argument)].security_variable for argument in ir.arguments]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
        ir_dict[str(ir.lvalue)].set_left_variable(security_arguments)


    return ir_dict


# ir_function_name == 'assert' or 'require'
def require_assert(node, security_variables, line_number, ir, ir_dict, analyser):
    rvalues = []
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none

    for argument in ir.arguments:
        for security_variable in security_variables:
            if argument.name == security_variable.name and security_variable.line_number == line_number:
                ir_dict[str(argument)] = IRVariable(security_variable, True)
    for argument in ir.arguments:
        if argument.name not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)

    for argument in ir.arguments:
        rvalues.extend(
            [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(argument)]) if
             value.is_security_variable])

    control_flows = [] if not (analyser.control_flows and analyser.control_flows[-1].security_variables) else analyser.control_flows[-1].security_variables
    rvalues.extend(control_flows)

    if lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H and analyser.vuln_mode == VulnerabilityEnum.confidentiality:
        vulnerable_type = analyser.vuln_mode

    vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number, vulnerable_type,
                                           ExpressionEnum.sol_assert)
    vulnerabilities.append(vulnerability_variable)


    return ir_dict, vulnerabilities


# ir_function_name == 'sload'
def load(security_variables, line_number, ir, ir_dict):
    rvalues = []

    for argument in ir.arguments:
        for security_variable in security_variables:
            if argument.name == security_variable.name and security_variable.line_number == line_number:
                ir_dict[str(argument)] = IRVariable(security_variable, True)
    for argument in ir.arguments:
        if argument.name not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)

    rvalues.extend([value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(ir.arguments[0])])
                    if value.is_security_variable])

    if str(ir.lvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(rvalues), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.arguments[0])])


    return ir_dict




# ir_function_name == 'sstore'
def store(node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none

    for argument in ir.arguments:
        for security_variable in security_variables:
            if argument.name == security_variable.name and security_variable.line_number == line_number:
                ir_dict[str(argument)] = IRVariable(security_variable, True)
    for argument in ir.arguments:
        if argument.name not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)



    from_value = ir_dict[str(ir.arguments[1])].security_variable
    to_value = ir_dict[str(ir.arguments[0])].security_variable

    lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[to_value.name]) if
             value.is_security_variable]
    rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[from_value.name]) if
             value.is_security_variable]

    if from_value.security_level == SecurityEnum.H and to_value.security_level == SecurityEnum.L:
            vulnerable_type = analyser.vuln_mode

    vulnerability_variable = Vulnerability(lvalues, rvalues, str(node.expression), line_number, vulnerable_type,
                                           ExpressionEnum.assignment)
    vulnerabilities.append(vulnerability_variable)


    return ir_dict, vulnerabilities
