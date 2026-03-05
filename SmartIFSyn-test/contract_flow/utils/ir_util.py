# ir utils
import copy

from ..analyses import information_flow_analysis
from ..analyses.ir_analysis import solidity_call_ir
from ..analyses.ir_analysis import internal_call_ir
from ..utils import lattice_util, expression_util
from ..utils import analyse_util
from ..core.analyser import analyse
from ..core.enums.function_call_enum import FunctionCallEnum
from ..core.variables.ir_variable import IRVariable
from ..core.enums.constant_enum import ConstantEnum
from ..core.enums.location_enum import LocationEnum
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.expression_enum import ExpressionEnum
from ..core.enums.vulnerablity_enum import VulnerabilityEnum
from ..core.vulnerability.vulnerability import Vulnerability
from ..core.variables.security_variable import SecurityVariable


# ir_type == 'Binary'
def binary(node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none
    expression_type = ExpressionEnum.assignment

    for variable in security_variables:
        if variable.name == str(ir.variable_left) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.variable_right) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    if str(ir.variable_left) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable_left), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable_left)] = IRVariable(security_variable, False)

    if str(ir.variable_right) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable_right), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable_right)] = IRVariable(security_variable, False)

    if str(ir.lvalue) not in ir_dict:
        variable_left = ir_dict[str(ir.variable_left)]
        variable_right = ir_dict[str(ir.variable_right)]
        lub_list = [variable_left.security_variable, variable_right.security_variable]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    if ir.lvalue != ir.variable_left:
        ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.variable_left)])
        ir_dict[str(ir.lvalue)].set_right_variable(ir_dict[str(ir.variable_right)])
    else:
        lvalue = None
        rvalue = None
        for variable in security_variables:
            if variable.name == str(ir.lvalue) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
            if variable.name == str(ir.variable_right) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
        if str(ir.lvalue) in ir_dict:
            lvalue = ir_dict[str(ir.lvalue)]
        if str(ir.variable_right) in ir_dict:
            rvalue = ir_dict[str(ir.variable_right)]

        if lvalue is not None and rvalue is not None:
            security_lvalue = lvalue.security_variable
            security_rvalue = rvalue.security_variable
            lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(lvalue) if
                       value.is_security_variable]
            rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(rvalue) if
                       value.is_security_variable]

            # control flow
            control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
            rvalues.extend(control_flows)
            if security_lvalue.security_level == SecurityEnum.L and lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
                vulnerable_type = analyser.vuln_mode
            if security_lvalue.defined:
                expression_type = ExpressionEnum.local_define
                lvalues[0].set_rvalues(rvalues)
            vulnerability_variable = Vulnerability(lvalues, rvalues, str(node.expression),
                                                   line_number, vulnerable_type, expression_type)
            vulnerability_variable.set_define_type(ExpressionEnum.binary_define)
            vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'TypeConversion'
def type_conversion(security_variables, line_number, ir, ir_dict):
    for variable in security_variables:
        if variable.name == str(ir.variable) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
    if str(ir.variable) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable)] = IRVariable(security_variable, False)

    if str(ir.lvalue) not in ir_dict:
        variable = ir_dict[str(ir.variable)]
        security_variable = SecurityVariable(str(ir.lvalue), variable.security_variable.security_level, line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.variable)])

    return ir_dict


# ir_type == 'Index'
def index(security_variables, line_number, ir, ir_dict):
    for variable in security_variables:
        if variable.name == str(ir.variable_left) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.variable_right) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
    if str(ir.variable_left) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable_left), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable_left)] = IRVariable(security_variable, False)
    if str(ir.variable_right) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable_right), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable_right)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        variable_left = ir_dict[str(ir.variable_left)]
        variable_right = ir_dict[str(ir.variable_right)]
        lub_list = [variable_left.security_variable, variable_right.security_variable]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.variable_left)])
    ir_dict[str(ir.lvalue)].set_right_variable(ir_dict[str(ir.variable_right)])
    ir_dict[str(ir.lvalue)].security_variable.set_defined(ir_dict[str(ir.variable_left)].security_variable.defined)

    return ir_dict


# ir_type == 'assignment'
def assignment(node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    expression_type = ExpressionEnum.assignment
    vulnerable_type = VulnerabilityEnum.none

    lvalue = None
    rvalue = None
    for variable in security_variables:
        if variable.name == str(ir.lvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.rvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    if str(ir.lvalue) in ir_dict:
        lvalue = ir_dict[str(ir.lvalue)]
    if str(ir.rvalue) in ir_dict:
        rvalue = ir_dict[str(ir.rvalue)]

    # if lvalue is not None and rvalue is not None:
    if (lvalue is not None and rvalue is not None) or (lvalue is not None and rvalue is None and ir.rvalue.__class__.__name__ == 'Constant'):
        security_lvalue = lvalue.security_variable
        lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(lvalue) if
                   value.is_security_variable]
        rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(rvalue) if
                   value.is_security_variable] if rvalue is not None else []
        # control flow
        control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
        rvalues.extend(control_flows)
        if security_lvalue.defined:
            expression_type = ExpressionEnum.local_define
            lvalues[0].set_rvalues(rvalues)
        else:
            if security_lvalue.security_level == SecurityEnum.L and lattice_util.lowest_upper_bound(
                    rvalues) == SecurityEnum.H:
                vulnerable_type = analyser.vuln_mode

        vulnerability_variable = Vulnerability(lvalues, rvalues, str(node.expression), line_number,
                                               vulnerable_type, expression_type)
        vulnerability_variable.set_define_type(ExpressionEnum.assignment_define)
        vulnerabilities.append(vulnerability_variable)
    else:
        if str(ir.lvalue) not in ir_dict:
            security_variable = SecurityVariable(str(ir.lvalue), SecurityEnum.L, line_number, None, False)
            ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
        if str(ir.rvalue) not in ir_dict:
            security_variable = SecurityVariable(str(ir.rvalue), SecurityEnum.L, line_number, None, False)
            ir_dict[str(ir.rvalue)] = IRVariable(security_variable, False)

        ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.rvalue)])

    return ir_dict, vulnerabilities


# assignment in push expression
def push_assignment(security_variables, line_number, ir, ir_dict):
    for variable in security_variables:
        if variable.name == str(ir.lvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.rvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    if str(ir.lvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.lvalue), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
    if str(ir.rvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.rvalue), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.rvalue)] = IRVariable(security_variable, False)

    return ir_dict


# ir_type == 'SolidityCall'
def solidity_call(node, security_variables, line_number, ir, ir_dict, analyser):
    call_function_name = ir.function.name
    vulnerabilities = []
    if call_function_name == 'balance(address)':
        ir_dict = solidity_call_ir.balance(security_variables, line_number, ir, ir_dict)
    elif call_function_name == 'abi.encode()':
        ir_dict = solidity_call_ir.argument_solidity_call(security_variables, line_number, ir, ir_dict)
    elif call_function_name == 'keccak256()' or call_function_name == 'keccak256(bytes)':
        ir_dict = solidity_call_ir.argument_solidity_call(security_variables, line_number, ir, ir_dict)
    elif call_function_name == 'abi.encodeWithSignature()':
        ir_dict = solidity_call_ir.argument_solidity_call(security_variables, line_number, ir, ir_dict)
    elif call_function_name == 'blockhash(uint256)':
        ir_dict = solidity_call_ir.argument_solidity_call(security_variables, line_number, ir, ir_dict)
    elif call_function_name == 'sha3()':
        ir_dict = solidity_call_ir.argument_solidity_call(security_variables, line_number, ir, ir_dict)
    elif call_function_name == 'abi.encodePacked()':
        ir_dict = solidity_call_ir.argument_solidity_call(security_variables, line_number, ir, ir_dict)
    # may have vulnerabilities
    elif call_function_name == 'require(bool,string)':
        ir_dict, vuln = solidity_call_ir.require_assert(node, security_variables, line_number, ir, ir_dict, analyser)
        vulnerabilities.extend(vuln)
    elif call_function_name.startswith('sload'):
        ir_dict = solidity_call_ir.load(security_variables, line_number, ir, ir_dict)
    elif call_function_name.startswith('sstore'):
        ir_dict, vuln = solidity_call_ir.store(node, security_variables, line_number, ir, ir_dict, analyser)
        vulnerabilities.extend(vuln)

    return ir_dict, vulnerabilities


# ir_type == 'Send'
def send(node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none

    call_value = None
    destination = None
    for variable in security_variables:
        if variable.name == str(ir.call_value) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.destination) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
    if str(ir.call_value) in ir_dict:
        call_value = ir_dict[str(ir.call_value)]
    if str(ir.destination) in ir_dict:
        destination = ir_dict[str(ir.destination)]

    if call_value is not None and destination is not None:
        security_lvalue = destination.security_variable
        security_rvalue = call_value.security_variable
        rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(destination) if
                   value.is_security_variable]
        rvalues.extend([value.security_variable for value in analyse_util.traverse_ir_variable(call_value)
                        if value.is_security_variable])

        # control flow
        control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
        rvalues.extend(control_flows)
        if security_lvalue.security_level == SecurityEnum.H or lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
            vulnerable_type = analyser.vuln_mode

        vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number,
                                               vulnerable_type, ExpressionEnum.transfer)
        vulnerabilities.append(vulnerability_variable)
    elif destination is not None and call_value is None and ir.call_value.__class__.__name__ == 'Constant':
        security_lvalue = destination.security_variable
        rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(destination) if
                   value.is_security_variable]
        rvalues.extend([])

        if security_lvalue.security_level == SecurityEnum.H:
            vulnerable_type = analyser.vuln_mode

        vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number,
                                               vulnerable_type, ExpressionEnum.transfer)
        vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'Length'
def length(security_variables, line_number, ir, ir_dict):
    for variable in security_variables:
        if variable.name == str(ir.value) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    if str(ir.value) not in ir_dict:
        security_variable = SecurityVariable(str(ir.value), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.value)] = IRVariable(security_variable, False)

    if str(ir.lvalue) not in ir_dict:
        variable_right = ir_dict[str(ir.value)]
        security_variable = SecurityVariable(str(ir.lvalue), variable_right.security_variable.security_level,
                                             line_number, None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.value)])

    return ir_dict


# ir_type == 'Member'
def member(security_variables, line_number, ir, ir_dict):
    for variable in security_variables:
        if variable.name == str(ir.variable_left) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
    if str(ir.variable_left) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable_left), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable_left)] = IRVariable(security_variable, False)
    if str(ir.variable_right) not in ir_dict:
        security_variable = SecurityVariable(str(ir.variable_right), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.variable_right)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        variable_left = ir_dict[str(ir.variable_left)]
        variable_right = ir_dict[str(ir.variable_right)]
        lub_list = [variable_left.security_variable, variable_right.security_variable]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        if ir_dict[str(ir.variable_left)].security_variable.location != LocationEnum.storage:
            security_variable.set_defined(ir_dict[str(ir.variable_left)].security_variable.defined)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.variable_left)])
    ir_dict[str(ir.lvalue)].set_right_variable(ir_dict[str(ir.variable_right)])

    return ir_dict


# ir_type == 'NewStructure'
def new_structure(security_variables, line_number, ir, ir_dict):
    for argument in ir.arguments:
        for variable in security_variables:
            if variable.name == str(argument) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        lub_list = [ir_dict[str(argument)].security_variable for argument in ir.arguments]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable([ir_dict[str(argument)] for argument in ir.arguments])

    return ir_dict


# ir_type == 'NewArray'
def new_array(security_variables, line_number, ir, ir_dict):
    for argument in ir.arguments:
        for variable in security_variables:
            if variable.name == str(argument) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        lub_list = [ir_dict[str(argument)].security_variable for argument in ir.arguments]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
    ir_dict[str(ir.lvalue)].set_left_variable([ir_dict[str(argument)] for argument in ir.arguments])
    return ir_dict


# ir_type == 'NewContract'
def new_contract(node, security_variables, line_number, ir, ir_dict, analyser):
    rvalues = []
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none

    for argument in ir.arguments:
        for variable in security_variables:
            if variable.name == str(argument) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)
        rvalues.extend(
            [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(argument)]) if
             value.is_security_variable])

    # control flow
    control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
    rvalues.extend(control_flows)

    if str(ir.lvalue) not in ir_dict:
        lub_list = [ir_dict[str(argument)].security_variable for argument in ir.arguments]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
    ir_dict[str(ir.lvalue)].set_left_variable([ir_dict[str(argument)] for argument in ir.arguments])

    if lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
        vulnerable_type = analyser.vuln_mode

    vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number, vulnerable_type,
                                           ExpressionEnum.sol_assert)
    vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'NewElementaryType'
def new_elementary_type(security_variables, line_number, ir, ir_dict):
    for argument in ir.arguments:
        for variable in security_variables:
            if variable.name == str(argument) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        lub_list = [ir_dict[str(argument)].security_variable for argument in ir.arguments]
        security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(lub_list), line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
    ir_dict[str(ir.lvalue)].set_left_variable([ir_dict[str(argument)] for argument in ir.arguments])
    return ir_dict


# ir_type == 'InitArray
def init_array(node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    expression_type = ExpressionEnum.local_define
    vulnerable_type = VulnerabilityEnum.none

    for init_value in ir.init_values:
        for variable in security_variables:
            if variable.name == str(init_value) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for init_value in ir.init_values:
        if str(init_value) not in ir_dict:
            security_variable = SecurityVariable(str(init_value), SecurityEnum.L, line_number, None, False)
            ir_dict[str(init_value)] = IRVariable(security_variable, False)
    for variable in security_variables:
        if variable.name == str(ir.lvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    lvalue = ir_dict[str(ir.lvalue)]
    rvalue = [ir_dict[str(init_value)].security_variable for init_value in ir.init_values]
    lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(lvalue) if
               value.is_security_variable]
    rvalues = []
    for var in rvalue:
        rvalues.extend([value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[var.name])
                        if value.is_security_variable])

    # control flow
    control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
    rvalues.extend(control_flows)

    vulnerability_variable = Vulnerability(lvalues, rvalues, str(node.expression), line_number,
                                           vulnerable_type, expression_type)
    vulnerabilities.append(vulnerability_variable)
    return ir_dict, vulnerabilities


# ir_type = 'EventCall'
def event_call(node, security_variables, line_number, ir, ir_dict, analyser):
    rvalues = []
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none

    for argument in ir.arguments:
        for variable in security_variables:
            if variable.name == str(argument) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)

    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number, None, False)
            ir_dict[str(argument)] = IRVariable(security_variable, False)

    for argument in ir.arguments:
        rvalues.extend(
            [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(argument)]) if
             value.is_security_variable])

    # control flow
    control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
    rvalues.extend(control_flows)

    if lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
        vulnerable_type = analyser.vuln_mode

    vulnerability_variable = Vulnerability([], rvalues, f"emit {node.expression}", line_number, vulnerable_type,
                                           ExpressionEnum.event)
    vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'Transfer'
def transfer(node, security_variables, line_number, ir, ir_dict, analyser):
    rvalues = []
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none
    destination = None
    call_value = None

    for variable in security_variables:
        if variable.name == str(ir.destination) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.call_value) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    if str(ir.destination) in ir_dict:
        destination = ir_dict[str(ir.destination)]
    if str(ir.call_value) in ir_dict:
        call_value = ir_dict[str(ir.call_value)]

    if destination is not None and call_value is not None:
        security_destination = destination.security_variable
        security_call_value = call_value.security_variable
        lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(destination) if
                   value.is_security_variable]
        rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(call_value) if
                   value.is_security_variable]
        rvalues.extend(lvalues)
        # control flow
        control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
        rvalues.extend(control_flows)
        if lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
            vulnerable_type = analyser.vuln_mode

    elif destination is not None and call_value is None and ir.call_value.__class__.__name__ == 'Constant':
        security_destination = destination.security_variable
        lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(destination) if
                   value.is_security_variable]
        rvalues = lvalues
        # control flow
        control_flows = analyser.control_flows[-1].security_variables if (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
        rvalues.extend(control_flows)
        if lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
            vulnerable_type = analyser.vuln_mode


    vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number,
                                           vulnerable_type, ExpressionEnum.transfer)
    vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'Return'
def ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser):
    return_num = 0
    vulnerable_type = VulnerabilityEnum.none
    vulnerabilities = []

    function_line_number = expression_util.get_line_number(function)

    for fun_node in function.nodes:
        for node_ir in fun_node.irs:
            if node_ir.__class__.__name__ == 'Return':
                return_num += 1

    for variable in security_variables:
        if variable.name == function.name and variable.line_number == function_line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    for value in ir.values:
        for variable in security_variables:
            if variable.name == str(value) and variable.line_number == line_number:
                ir_dict[variable.name] = IRVariable(variable, True)
    for value in ir.values:
        if str(value.name) not in ir_dict:
            security_variable = SecurityVariable(str(value), SecurityEnum.L, line_number, None, False)
            ir_dict[str(value)] = IRVariable(security_variable, False)

    return_variables = [ir_dict[str(value)].security_variable for value in ir.values]
    # control flow
    control_flows = analyser.control_flows[-1].security_variables if (
                analyser.control_flows and analyser.control_flows[-1].security_variables) else []
    return_variables.extend(control_flows)

    if return_variables:
        if not (return_num > 1 and line_number in [expression_util.get_line_number(returns) for returns in
                                                   function.returns]):
            rvalues = []
            vuln_rvalues = []
            for ir_value in ir.values:
                rvalues.extend(
                    value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(ir_value)])
                    if value.is_security_variable)

            for rvalue in rvalues:
                if rvalue.rvalues:
                    vuln_rvalues.extend(rvalue.rvalues)
                else:
                    vuln_rvalues.append(rvalue)
            # control flow
            control_flows = analyser.control_flows[-1].security_variables if (
                        analyser.control_flows and analyser.control_flows[-1].security_variables) else []
            vuln_rvalues.extend(control_flows)
            vulnerability_variable = Vulnerability([], vuln_rvalues,
                                                   f"return {node.expression}", line_number, vulnerable_type,
                                                   ExpressionEnum.identifier_return)
            vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'InternalCall'
def internal_call(caller_function, node, security_variables, line_number, ir, ir_dict, analyser,
                  call_type=FunctionCallEnum.none):
    argument_list = []
    constant_list = []
    vulnerabilities = []
    internal_rvalues = []
    internal_lvalues = []
    sub_vulnerabilities = []
    is_vulnerable = False
    ir_function = ir.function
    internal_call_function = None
    multi_return_type = SecurityEnum.L
    vulnerable_type = VulnerabilityEnum.none
    scope_start, scope_end = expression_util.get_scope(ir_function)

    # update ir_dict
    for argument in ir.arguments:
        if str(argument) in ir_dict:
            argument_list.append(ir_dict[str(argument)].security_variable)
        else:
            for security_variable in security_variables:
                if str(argument) == security_variable.name and security_variable.line_number == line_number:
                    argument_list.append(security_variable)
                    ir_dict[str(argument)] = IRVariable(security_variable, True)

            if str(argument) not in ir_dict:
                security_variable = SecurityVariable(argument.name, SecurityEnum.L, line_number)
                argument_list.append(security_variable)
                ir_dict[str(argument)] = IRVariable(security_variable, False)

    # find called function
    library_functions = [call[1] for call in analyser.target_contract.all_library_calls]
    contract_functions = analyser.target_contract.functions
    contract_modifiers = analyser.target_contract.modifiers
    contract_functions.extend(library_functions)
    contract_functions.extend(contract_modifiers)
    for function in contract_functions:
        if (function.name == ir.function.name and expression_util.get_line_number(function) == expression_util.
                get_line_number(ir.function)):
            internal_call_function = function

    # update the security type of called function
    if internal_call_function:
        internal_vuln = []
        internal_security_variables = copy.deepcopy(security_variables)
        for argument, f_argument in zip(argument_list, internal_call_function.parameters):
            for i in range(len(internal_security_variables)):
                internal_variable = internal_security_variables[i]
                if internal_variable.name == f_argument.name and scope_start <= internal_variable.line_number <= scope_end:
                    internal_security_variables[i].security_level = argument.security_level

        # update constant security_level
        constant_dict = {member.value: SecurityEnum.L if analyser.vuln_mode == VulnerabilityEnum.confidentiality else SecurityEnum.H for member in ConstantEnum}


        caller_start, caller_end = expression_util.get_scope(caller_function)
        for security_variable in security_variables:
            if security_variable.name in constant_dict and caller_start <= security_variable.line_number <= caller_end:
                constant_dict[security_variable.name] = security_variable.security_level
                constant_list.append(security_variable)
        for i in range(len(internal_security_variables)):
            internal_variable = internal_security_variables[i]
            if internal_variable.name in constant_dict and scope_start <= internal_variable.line_number <= scope_end:
                internal_security_variables[i].security_level = constant_dict[internal_variable.name]
        for constant in constant_list:
            in_internal_function = False
            for security_variable in internal_security_variables:
                if security_variable.name == constant.name and scope_start <= security_variable.line_number <= scope_end:
                    in_internal_function = True
            if not in_internal_function:
                new_constant = copy.deepcopy(constant)
                new_constant.line_number = scope_start
                internal_security_variables.append(new_constant)

        # update local variable
        for i in range(len(internal_security_variables)):
            internal_variable = internal_security_variables[i]
            if internal_variable.defined:
                internal_security_variables[i].security_level = SecurityEnum.L
                if internal_variable.rvalues:
                    for j in range(len(internal_variable.rvalues)):
                        if internal_security_variables[i].rvalues[j].defined:
                            internal_security_variables[i].rvalues[j].security_level = SecurityEnum.L

        # generate vuln
        for ir_node in ir_function.nodes:
            internal_vuln.extend(analyse.analyse_node(ir_function, ir_node, internal_security_variables, analyser))

        # update the local defined variables' security type
        for i in range(len(internal_vuln)):
            vuln = internal_vuln[i]
            if vuln.expression_type == ExpressionEnum.local_define:
                lub = lattice_util.lowest_upper_bound(vuln.rvalues)
                internal_vuln[i].lvalues[0].security_level = lub
                lvalue = vuln.lvalues[0]
                returns_nums = [expression_util.get_line_number(returns) for returns in internal_call_function.returns]
                returns_nums.append(expression_util.get_line_number(internal_call_function))
                for inter_index in range(len(internal_security_variables)):
                    inter_variable = internal_security_variables[inter_index]
                    if inter_variable.name == lvalue.name and lvalue.line_number < inter_variable.line_number <= scope_end:
                        internal_security_variables[inter_index].security_level = lvalue.security_level
                    elif inter_variable.name == lvalue.name and inter_variable.line_number in returns_nums:
                        internal_security_variables[inter_index].security_level = lvalue.security_level
        internal_vuln = []
        for ir_node in ir_function.nodes:
            internal_vuln.extend(analyse.analyse_node(ir_function, ir_node, internal_security_variables, analyser))

        # update values in lvalues, rvalues and sub_vulnerabilities
        internal_vuln, local_defined_variables = internal_call_ir.update_internal_call_vulnerabilities(
            internal_vuln, argument_list, internal_call_function, constant_list, constant_dict, scope_start, scope_end,
            call_type)

        for vuln_index in range(len(internal_vuln)):
            vuln = internal_vuln[vuln_index]
            if vuln.expression_type == ExpressionEnum.local_define and call_type == FunctionCallEnum.internal:
                for j in range(vuln_index, len(internal_vuln)):
                    v = internal_vuln[j]
                    if v.expression_type == ExpressionEnum.identifier_return and call_type == FunctionCallEnum.internal and \
                            vuln.lvalues[0] in vuln.rvalues:
                        internal_vuln[j].rvalues = [value for value in internal_vuln[j].rvalues if
                                                    value not in vuln.lvalues]
            if vuln.expression_type == ExpressionEnum.identifier_return and call_type == FunctionCallEnum.internal:
                if lattice_util.lower(lattice_util.lowest_upper_bound(vuln.rvalues), multi_return_type):
                    continue
                internal_rvalues = []
                multi_return_type = lattice_util.lowest_upper_bound(vuln.rvalues)
                if str(ir.lvalue) not in ir_dict:
                    security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(vuln.rvalues),
                                                         line_number, None, False)
                    ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
                    for return_rvalue in vuln.rvalues:
                        for security_variable in internal_security_variables:
                            if (return_rvalue.name not in ir_dict and return_rvalue.name == security_variable.name and
                                    return_rvalue.line_number == security_variable.line_number):
                                security_variable.security_level = return_rvalue.security_level
                                ir_dict[return_rvalue.name] = IRVariable(security_variable, True)
                    for return_rvalue in vuln.rvalues:
                        if return_rvalue.name not in ir_dict:
                            security_variable = SecurityVariable(return_rvalue.name, SecurityEnum.L, vuln.line_number,
                                                                 None, False)
                            ir_dict[return_rvalue.name] = IRVariable(security_variable, False)
                else:
                    lub = lattice_util.lowest_upper_bound(vuln.rvalues)
                    if not ir_dict[str(ir.lvalue)].is_security_variable:
                        if lattice_util.upper(lub, ir_dict[str(ir.lvalue)].security_variable.security_level):
                            ir_dict[str(ir.lvalue)].security_variable.security_level = lub

                for v_rvalue in vuln.rvalues:
                    if v_rvalue.name not in ir_dict:
                        for internal_value in internal_security_variables:
                            if internal_value.name == v_rvalue.name and v_rvalue.line_number == internal_value.line_number:
                                internal_value.security_level = v_rvalue.security_level
                                ir_dict[internal_value.name] = IRVariable(internal_value, True)


                ir_dict[str(ir.lvalue)].set_left_variable([ir_dict[value.name] for value in vuln.rvalues])

                for rvalue in vuln.rvalues:
                    internal_rvalues.extend(
                        [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[rvalue.name]) if
                         value.is_security_variable])

        internal_vuln = [vuln for vuln in internal_vuln if vuln.expression_type != ExpressionEnum.identifier_return]
        for vuln in internal_vuln:
            if vuln.vulnerable_type == analyser.vuln_mode:
                is_vulnerable = True
            if vuln.expression_type == ExpressionEnum.local_define:
                vuln.set_shown(False)
            sub_vulnerabilities.append(vuln)
        if is_vulnerable:
            vulnerable_type = analyser.vuln_mode
    for vuln in sub_vulnerabilities:
        if vuln.vulnerable_type == analyser.vuln_mode:

            for lvalue in vuln.lvalues:
                if lvalue.name not in ir_dict:
                    internal_lvalues.append(lvalue)
                else:
                    internal_rvalues.extend(
                        [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[lvalue.name]) if
                         value.is_security_variable])

            for rvalue in vuln.rvalues:
                if rvalue.name not in ir_dict:
                    internal_rvalues.append(rvalue)
                else:
                    internal_rvalues.extend(
                        [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[rvalue.name]) if
                         value.is_security_variable])

    vulnerability_variable = Vulnerability(internal_lvalues, internal_rvalues, str(node.expression), line_number,
                                           vulnerable_type, ExpressionEnum.internal_call, True,
                                           sub_vulnerabilities)
    vulnerability_variable, ir_dict = internal_call_ir.update_sub_vulnerabilities(vulnerability_variable, ir_dict)
    vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'Unary'
def unary(security_variables, line_number, ir, ir_dict):
    for variable in security_variables:
        if variable.name == str(ir.lvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.rvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
    if str(ir.rvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.rvalue), SecurityEnum.L, line_number, None, False)
        ir_dict[str(ir.rvalue)] = IRVariable(security_variable, False)
    if str(ir.lvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.lvalue), ir_dict[str(ir.rvalue)].security_variable.security_level,
                                             line_number, None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.rvalue)])

    return ir_dict


# ir_type == 'HighLevelCall'
def high_level_call(caller_function, node, security_variables, line_number, ir, ir_dict, analyser,
                    call_type=FunctionCallEnum.none):
    is_vulnerable = False
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none
    sub_vulnerabilities = []
    argument_list = []
    constant_list = []
    ir_function = ir.function
    high_level_contract = None
    high_level_rvalues = []
    scope_start, scope_end = expression_util.get_scope(ir_function)

    for argument in ir.arguments:
        if str(argument) in ir_dict:
            argument_list.append(ir_dict[str(argument)].security_variable)
        else:
            for security_variable in security_variables:
                if argument.name == security_variable.name and security_variable.line_number == line_number:
                    argument_list.append(security_variable)
                    ir_dict[str(argument)] = IRVariable(security_variable, True)
            if str(argument) not in ir_dict:
                security_variable = SecurityVariable(argument.name, SecurityEnum.L, line_number)
                argument_list.append(security_variable)
                ir_dict[str(argument)] = IRVariable(security_variable, False)

    for security_variable in security_variables:
        if str(ir.destination) == security_variable.name and security_variable.line_number == line_number:
            ir_dict[str(ir.destination)] = IRVariable(security_variable, True)
    if str(ir.destination) not in ir_dict:
        security_variable = SecurityVariable(str(ir.destination), SecurityEnum.L, line_number)
        ir_dict[str(ir.destination)] = IRVariable(security_variable, False)

    for contract in analyser.slither.contracts:
        for function in contract.functions:
            # make sure to get the correct contract
            if (function.name == ir.function.name and expression_util.get_line_number(ir_function) ==
                    expression_util.get_line_number(function) and contract.name == ir.destination.signature[2][0]):
                high_level_contract = contract
    if high_level_contract:
        high_level_vuln = []
        annotated, high_core_variables, high_security_variables = information_flow_analysis.get_variable_info(
            high_level_contract, analyser.sol_name, analyser)
        if not annotated:
            analyser.core_variables.extend(high_core_variables)
            analyser.core_variables = list(set(analyser.core_variables))
        else:
            for core_variable in analyser.core_variables:
                for security_variable in high_security_variables:
                    source = security_variable.source
                    if source and source.name == core_variable.name and source.line_number == core_variable.line_number:
                        security_variable.set_source(core_variable)

        for function in high_level_contract.functions:
            if function.name == ir.function.name and expression_util.get_line_number(function) == scope_start:
                for i in range(len(function.parameters)):
                    for core_variable in high_core_variables:
                        if core_variable.name == function.parameters[i].name and core_variable.line_number == scope_start:
                            argument_list[i] = (argument_list[i], core_variable)
        for i in range(len(argument_list)):
            for j in range(len(high_security_variables)):
                security_variable = high_security_variables[j]
                # parameter of a function can be empty
                if not isinstance(argument_list[i], tuple):
                    break
                argument = argument_list[i][0]
                core_variable = argument_list[i][1]
                if security_variable.name == core_variable.name and scope_start <= security_variable.line_number <= scope_end:
                    high_security_variables[j].security_level = argument.security_level
        # update constant security_level
        constant_dict = {member.value: SecurityEnum.L for member in ConstantEnum}
        caller_start, caller_end = expression_util.get_scope(caller_function)
        for security_variable in security_variables:
            if security_variable.name in constant_dict and caller_start <= security_variable.line_number <= caller_end:
                constant_dict[security_variable.name] = security_variable.security_level
                constant_list.append(security_variable)
        for i in range(len(high_security_variables)):
            high_level_variable = high_security_variables[i]
            if high_level_variable.name in constant_dict and scope_start <= high_level_variable.line_number <= scope_end:
                high_security_variables[i].security_level = constant_dict[high_level_variable.name]

        for ir_node in ir_function.nodes:
            high_level_vuln.extend(analyse.analyse_node(ir_function, ir_node, high_security_variables, analyser))

        # update the local defined variables' security type
        for i in range(len(high_level_vuln)):
            vuln = high_level_vuln[i]
            if vuln.expression_type == ExpressionEnum.local_define:
                lub = lattice_util.lowest_upper_bound(vuln.rvalues)
                high_level_vuln[i].lvalues[0].security_level = lub
                lvalue = vuln.lvalues[0]
                for inter_index in range(len(high_security_variables)):
                    inter_variable = high_security_variables[inter_index]
                    if inter_variable.name == lvalue.name and lvalue.line_number < inter_variable.line_number <= scope_end:
                        high_security_variables[inter_index].security_level = lvalue.security_level

        high_level_vuln = []
        for ir_node in ir_function.nodes:
            high_level_vuln.extend(analyse.analyse_node(ir_function, ir_node, high_security_variables, analyser))

            # for vuln in high_level_vuln:
        for vuln_index in range(len(high_level_vuln)):
            vuln = high_level_vuln[vuln_index]
            for i in range(len(argument_list)):
                for j in range(len(vuln.lvalues)):
                    lvalue = vuln.lvalues[j]
                    argument = argument_list[i][0]
                    core_variable = argument_list[i][1]
                    if lvalue.name == core_variable.name and scope_start <= lvalue.line_number <= scope_end:
                        high_level_vuln[vuln_index].lvalues[j] = argument
                for j in range(len(vuln.rvalues)):
                    rvalue = vuln.rvalues[j]
                    argument = argument_list[i][0]
                    core_variable = argument_list[i][1]
                    if rvalue.name == core_variable.name and scope_start <= rvalue.line_number <= scope_end:
                        high_level_vuln[vuln_index].rvalues[j] = argument
            for constant in constant_list:
                for i in range(len(vuln.lvalues)):
                    lvalue = vuln.lvalues[i]
                    if lvalue.name == constant.name and constant.name in constant_dict and scope_start <= lvalue.line_number <= scope_end:
                        high_level_vuln[vuln_index].lvalues[i] = constant
                for i in range(len(vuln.rvalues)):
                    rvalue = vuln.rvalues[i]
                    if rvalue.name == constant.name and constant.name in constant_dict and scope_start <= rvalue.line_number <= scope_end:
                        high_level_vuln[vuln_index].rvalues[i] = constant
            if vuln.expression_type == ExpressionEnum.identifier_return and call_type == FunctionCallEnum.high_level:
                rvalues = copy.deepcopy(vuln.rvalues)
                high_level_rvalues = rvalues
                rvalues.append(ir_dict[str(ir.destination)].security_variable)
                if str(ir.lvalue) not in ir_dict:
                    security_variable = SecurityVariable(str(ir.lvalue), lattice_util.lowest_upper_bound(rvalues),
                                                         line_number, None, False)
                    ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
                    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.destination)])
                else:
                    lub = lattice_util.lowest_upper_bound(rvalues)
                    if not ir_dict[str(ir.lvalue)].is_security_variable:
                        if lattice_util.upper(lub, ir_dict[str(ir.lvalue)].security_variable.security_level):
                            ir_dict[str(ir.lvalue)].security_variable.security_level = lub

        high_level_vuln = [vuln for vuln in high_level_vuln if vuln.expression_type != ExpressionEnum.identifier_return]

        for vuln in high_level_vuln:
            if vuln.vulnerable_type == analyser.vuln_mode:
                is_vulnerable = True
            if vuln.expression_type == ExpressionEnum.local_define:
                vuln.set_shown(False)
            sub_vulnerabilities.append(vuln)

        if is_vulnerable:
            vulnerable_type = analyser.vuln_mode

    if str(ir.lvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.lvalue),
                                             ir_dict[str(ir.destination)].security_variable.security_level, line_number,
                                             None, False)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)
        ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.destination)])
    lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(ir.destination)]) if
               value.is_security_variable]
    vulnerability_variable = Vulnerability(lvalues, high_level_rvalues, str(node.expression), line_number,
                                           vulnerable_type,
                                           ExpressionEnum.high_level_call, True, sub_vulnerabilities)
    vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


# ir_type == 'LowLevelCall'
def low_level_call(caller_function, node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none

    # argument
    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            for security_variable in security_variables:
                if security_variable.name == str(argument) and security_variable.line_number == line_number:
                    ir_dict[security_variable.name] = IRVariable(security_variable, True)

    for argument in ir.arguments:
        if str(argument) not in ir_dict:
            security_variable = SecurityVariable(str(argument), SecurityEnum.L, line_number)
            ir_dict[str(argument)] = IRVariable(security_variable, False)

    # destination
    for security_variable in security_variables:
        if str(ir.destination) == security_variable.name and security_variable.line_number == line_number:
            ir_dict[str(ir.destination)] = IRVariable(security_variable, True)

    if str(ir.destination) not in ir_dict:
        security_variable = SecurityVariable(str(ir.destination), SecurityEnum.L, line_number)
        ir_dict[str(ir.destination)] = IRVariable(security_variable, False)

    # lvalue
    if str(ir.lvalue) not in ir_dict:
        security_variable = SecurityVariable(str(ir.lvalue),
                                             ir_dict[str(ir.destination)].security_variable.security_level, line_number)
        ir_dict[str(ir.lvalue)] = IRVariable(security_variable, False)

    ir_dict[str(ir.lvalue)].set_left_variable(ir_dict[str(ir.destination)])
    ir_dict[str(ir.lvalue)].set_right_variable([ir_dict[str(argument)] for argument in ir.arguments])

    # check vulnerability
    lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(ir.destination)]) if
               value.is_security_variable]
    rvalues = []
    for argument in ir.arguments:
        rvalues.extend(
            [value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(argument)]) if
             value.is_security_variable])

    # control flow
    control_flows = [] if not (analyser.control_flows and analyser.control_flows[-1].security_variables) else analyser.control_flows[-1].security_variables
    rvalues.extend(control_flows)

    left_security_level = lattice_util.lowest_upper_bound(lvalues)
    right_security_level = lattice_util.lowest_upper_bound(rvalues)

    if left_security_level == SecurityEnum.H or right_security_level == SecurityEnum.H:
        vulnerable_type = analyser.vuln_mode

    vulnerability_variable = Vulnerability(lvalues, rvalues, str(node.expression), line_number,
                                           vulnerable_type, ExpressionEnum.low_level_call, True)
    vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities


def unpack(node, security_variables, line_number, ir, ir_dict, analyser):
    vulnerabilities = []
    expression_type = ExpressionEnum.assignment
    vulnerable_type = VulnerabilityEnum.none

    lvalue = None
    rvalue = None

    for variable in security_variables:
        if variable.name == str(ir.lvalue) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)
        if variable.name == str(ir.tuple) and variable.line_number == line_number:
            ir_dict[variable.name] = IRVariable(variable, True)

    if str(ir.lvalue) in ir_dict:
        lvalue = ir_dict[str(ir.lvalue)]
    if str(ir.tuple) in ir_dict:
        rvalue = ir_dict[str(ir.tuple)]

    if lvalue is not None and rvalue is not None:
        security_lvalue = lvalue.security_variable
        security_rvalue = rvalue.security_variable
        lvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(lvalue) if
                   value.is_security_variable]
        rvalues = [value.security_variable for value in analyse_util.traverse_ir_variable(rvalue) if
                   value.is_security_variable]

        # control flow
        control_flows = [] if not (analyser.control_flows and analyser.control_flows[-1].security_variables) else \
        analyser.control_flows[-1].security_variables
        rvalues.extend(control_flows)
        if security_lvalue.security_level == SecurityEnum.L and lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
            vulnerable_type = analyser.vuln_mode
        if security_lvalue.defined:
            expression_type = ExpressionEnum.local_define
            lvalues[0].set_rvalues(rvalues)
        vulnerability_variable = Vulnerability(lvalues, rvalues, str(node.expression), line_number,
                                               vulnerable_type, expression_type)
        vulnerability_variable.set_define_type(ExpressionEnum.unpack_define)
        vulnerabilities.append(vulnerability_variable)

    return ir_dict, vulnerabilities
