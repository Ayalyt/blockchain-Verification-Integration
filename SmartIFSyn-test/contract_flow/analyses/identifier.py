# Identifiers in the smart contract
from ..core.enums.function_call_enum import FunctionCallEnum
from ..utils import ir_util


# return identifier
def identifier_return(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    ir_dict = {}
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Return':
            ir_dict, vuln = ir_util.ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict, analyser,
                                                  FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'LibraryCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)

    return vulnerabilities
