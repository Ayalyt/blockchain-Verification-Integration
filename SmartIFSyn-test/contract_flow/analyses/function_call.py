# functionCalls in the smart contract
from ..core.analyser import analyse
from ..utils import ir_util, lattice_util
from ..utils import ir_check_util
from ..analyses import type_conversion
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.expression_enum import ExpressionEnum
from ..core.enums.vulnerablity_enum import VulnerabilityEnum
from ..core.vulnerability.vulnerability import Vulnerability
from ..core.enums.function_call_enum import FunctionCallEnum


# push function
def push(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}

    for index, ir in enumerate(node.irs):
        ir_type = ir.__class__.__name__
        if ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Length':
            ir_dict = ir_util.length(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Assignment':
            if index != len(node.irs) - 1:
                ir_dict = ir_util.push_assignment(security_variables, line_number, ir, ir_dict)
            else:
                ir_dict, vuln = ir_util.assignment(node, security_variables, line_number, ir, ir_dict, analyser)
                vulnerabilities.extend(vuln)
        elif ir_type == 'NewStructure':
            ir_dict = ir_util.new_structure(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)

    return vulnerabilities


# Event
def event(node, security_variables, line_number, analyser):
    if analyser.vuln_mode is not VulnerabilityEnum.confidentiality:
        return []
    vulnerabilities = []
    ir_dict = {}

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'EventCall':
            ir_dict, vuln = ir_util.event_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)

    return vulnerabilities


# Transfer
def transfer(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}

    for ir in node.irs:
        ir_type = ir.__class__.__name__

        if ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Transfer':
            ir_dict, vuln = ir_util.transfer(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)
    return vulnerabilities


# self_destruct
def self_destruct(node, security_variables, line_number, analyser):
    vulnerabilities = []
    vulnerable_type = VulnerabilityEnum.none
    is_vulnerable = False
    arguments = []
    rvalues = []

    if ir_check_util.check_type_conversion(node):
        arguments = type_conversion.unary_convert(node)

    for ir in node.irs:
        if 'selfdestruct' in str(ir):
            argument = arguments[0] if arguments else ir.arguments[0]
            for security_variable in security_variables:
                if argument.name == security_variable.name and security_variable.line_number == line_number:
                    rvalues.append(security_variable)

            # control flow
            control_flows = analyser.control_flows[-1].security_variables if \
                (analyser.control_flows and analyser.control_flows[-1].security_variables) else []
            rvalues.extend(control_flows)
            if lattice_util.lowest_upper_bound(rvalues) == SecurityEnum.H:
                is_vulnerable = True

    if is_vulnerable:
        vulnerable_type = analyser.vuln_mode
    vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number, vulnerable_type,
                                           ExpressionEnum.event)
    vulnerabilities.append(vulnerability_variable)

    return vulnerabilities


# high level call
def high_level_call(function, analyser, node, security_variables, line_number):
    vulnerabilities = []
    ir_dict = {}
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'HighLevelCall':
            ir_dict, vuln = ir_util.high_level_call(function, node, security_variables, line_number, ir, ir_dict,
                                                    analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Return':
            ir_dict = ir_util.ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)

    return vulnerabilities


# internal call
def internal_call(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}
    call_type = FunctionCallEnum.internal if ir_check_util.check_return(node) else FunctionCallEnum.none
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict, analyser
                                                  , call_type)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Return':
            ir_dict = ir_util.ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Unary':
            ir_dict = ir_util.unary(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)

    return vulnerabilities


# send
def send(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)

        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)

        elif ir_type == 'Send':
            ir_dict, vuln = ir_util.send(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'LibraryCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Unary':
            ir_dict = ir_util.unary(security_variables, line_number, ir, ir_dict)

    return vulnerabilities


# function calls in require
def require(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []

    # propagate control flow
    analyser.control_flows.append(analyse.analyse_control_flow(security_variables, line_number, analyser))

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Length':
            ir_dict = ir_util.length(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Send':
            ir_dict, vuln = ir_util.send(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'LowLevelCall':
            ir_dict, vuln = ir_util.low_level_call(function, node, security_variables, line_number, ir, ir_dict,
                                                   analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Unary':
            ir_dict = ir_util.unary(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'LibraryCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)

    return vulnerabilities


# low level call
def low_level_call(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'LowLevelCall':
            ir_dict, vuln = ir_util.low_level_call(function, node, security_variables, line_number, ir, ir_dict,
                                                   analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Return':
            ir_dict = ir_util.ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser)
        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Unary':
            ir_dict = ir_util.unary(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)

    return vulnerabilities


# revert
def revert(function, node, security_variables, line_number, analyser):
    if analyser.vuln_mode is not VulnerabilityEnum.confidentiality:
        return []
    vulnerabilities = []
    ir_dict = {}
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)

    return  vulnerabilities


# assert
def sol_assert(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}

    # propagate control flow
    analyser.control_flows.append(analyse.analyse_control_flow(security_variables, line_number, analyser))

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Length':
            ir_dict = ir_util.length(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)

    return  vulnerabilities

# load_store
def store(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)

    return  vulnerabilities
