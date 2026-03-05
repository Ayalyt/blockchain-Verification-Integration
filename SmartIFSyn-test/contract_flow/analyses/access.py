# Accesses in the contract
from ..core.enums.function_call_enum import FunctionCallEnum
from ..utils import ir_util, ir_check_util


# handle index access in mapping assignment
# such as a[b] = c
def index_equal(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []
    # rvalues = []
    # lvalue_checked = False
    # vulnerable_type = VulnerabilityEnum.none
    # security_lvalue = None
    # rvalue_security_level = None
    # mapping_list = ['mapping(', 'uint256[]']

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
            # if not str(ir.variable_left.type).startswith(tuple(mapping_list)):
            #     ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
            # else:
            #     if not lvalue_checked and str(ir.variable_left.type).startswith(tuple(mapping_list)):
            #         lvalue_checked = True
            #         for variable in security_variables:
            #             if variable.name == str(ir.variable_left) and variable.line_number == line_number:
            #                 security_lvalue = variable
            #     for variable in security_variables:
            #         if (variable.name == str(ir.variable_right) and variable.line_number == line_number and
            #                 f"[{str(ir.variable_right)}]" in str(node.expression.expression_left)):
            #             rvalues.append(variable)
            #             ir_dict[variable.name] = IRVariable(variable, True)
            #             if rvalue_security_level != SecurityEnum.H:
            #                 rvalue_security_level = variable.security_level
            #     if str(ir.variable_right) not in ir_dict:
            #         security_variable = SecurityVariable(str(ir.variable_right), SecurityEnum.L, line_number, None, False)
            #         ir_dict[str(ir.variable_right)] = IRVariable(security_variable, False)
            #
            #     if rvalue_security_level is None:
            #         rvalues.extend([value.security_variable for value in analyse_util.traverse_ir_variable(ir_dict[str(ir.variable_right)]) if value.is_security_variable])
            #         for rvalue in rvalues:
            #             if rvalue_security_level != SecurityEnum.H:
            #                 rvalue_security_level = rvalue.security_level


        elif ir_type == 'Binary':
            ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Assignment':
            ir_dict, vuln = ir_util.assignment(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'NewStructure':
            ir_dict = ir_util.new_structure(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, FunctionCallEnum.internal)
            vulnerabilities.extend(vuln)

    # if security_lvalue is not None and rvalue_security_level is not None:
    #     if security_lvalue.security_level == SecurityEnum.L and rvalue_security_level == SecurityEnum.H:
    #         vulnerable_type = analyser.vuln_mode
    #     rvalues = list(set(rvalues))
    #     vulnerability_variable = Vulnerability([security_lvalue], rvalues, str(node.expression), line_number,
    #                                            vulnerable_type, ExpressionEnum.access)
    #     vulnerabilities.append(vulnerability_variable)

    return vulnerabilities


# member access
def member(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []
    call_type = FunctionCallEnum.internal if ir_check_util.check_return(node) else FunctionCallEnum.none
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Member':
            ir_dict = ir_util.member(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Return':
            ir_dict, vuln = ir_util.ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'TypeConversion':
            ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'SolidityCall':
            ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
        elif ir_type == 'Length':
            ir_dict = ir_util.length(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'InternalCall':
            ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                  analyser, call_type)
            vulnerabilities.extend(vuln)

    return vulnerabilities


# index access
def index(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Index':
            ir_dict = ir_util.index(security_variables, line_number, ir, ir_dict)
        elif ir_type == 'Return':
            ir_dict, vuln = ir_util.ir_return(function, node, security_variables, line_number, ir, ir_dict, analyser)
            vulnerabilities.extend(vuln)
    return vulnerabilities

