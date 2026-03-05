# Assignments in the contract
from ..utils import ir_util
from ..core.enums.function_call_enum import FunctionCallEnum


# handle assignment
def handle_assignment(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Assignment':
            ir_dict, vuln = ir_util.assignment(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Length':
            ir_dict = ir_util.length(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Send':
            ir_dict, vuln = ir_util.send(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)
        elif ir_type == 'NewStructure':
            ir_dict = ir_util.new_structure(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'HighLevelCall':
            ir_dict, vuln = ir_util.high_level_call(function, node, security_variables, line_number, ir, ir_dict,
                                                    analyser, FunctionCallEnum.high_level)
            vulnerabilities.extend(vuln)
        elif ir_type == 'LibraryCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Unary':
            ir_dict = ir_util.unary(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'LowLevelCall':
            ir_dict, vuln = ir_util.low_level_call(function, node, security_variables, line_number, ir, ir_dict,
                                                   analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'NewArray':
            ir_dict = ir_util.new_array(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'InitArray':
            ir_dict, vuln = ir_util.init_array(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Unpack':
            ir_dict, vuln = ir_util.unpack(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'NewContract':
            ir_dict, vuln = ir_util.new_contract(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'NewElementaryType':
            ir_dict = ir_util.new_elementary_type(security_variables, line_number, ir, ir_dict)

    return vulnerabilities
