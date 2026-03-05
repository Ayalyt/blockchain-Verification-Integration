# tuple expression in the smart contract_name
from ..core.enums.function_call_enum import FunctionCallEnum
from ..utils import expression_util, ir_util
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.expression_enum import ExpressionEnum
from ..core.vulnerability.vulnerability import Vulnerability
from ..core.enums.vulnerablity_enum import VulnerabilityEnum


# tuple identifier
def tuple_return(function, node, security_variables, line_number, analyser):
    ir_dict = {}
    vulnerabilities = []
    return_num = 0
    security_level = SecurityEnum.L
    vulnerable_type = VulnerabilityEnum.none

    for fun_node in function.nodes:
        for node_ir in fun_node.irs:
            if node_ir.__class__.__name__ == 'Return':
                return_num += 1

    returns_nums = [expression_util.get_line_number(returns) for returns in function.returns]
    returns_nums.append(expression_util.get_line_number(function))
    if return_num == 1 and line_number in returns_nums:
        return function_returns_tuple(function, node, security_variables, line_number, analyser)
    elif return_num > 1 and line_number in returns_nums:
        pass
    else:
        start_scope, end_scope = expression_util.get_scope(node)
        if end_scope is None:
            end_scope = start_scope

        for line in range(start_scope, end_scope+1):
            for ir in node.irs:
                ir_type = ir.__class__.__name__
                if ir_type == 'Return':
                    ir_dict, vuln = ir_util.ir_return(function, node, security_variables, line, ir, ir_dict, analyser)
                    vulnerabilities.extend(vuln)
                elif ir_type == 'Length':
                    ir_dict = ir_util.length(security_variables, line, ir, ir_dict)
                elif ir_type == 'Member':
                    ir_dict = ir_util.member(security_variables, line, ir, ir_dict)
                elif ir_type == 'Index':
                    ir_dict = ir_util.index(security_variables, line, ir, ir_dict)
                elif ir_type == 'SolidityCall':
                    ir_dict, vuln = ir_util.solidity_call(node, security_variables, line_number, ir, ir_dict, analyser)
                    vulnerabilities.extend(vuln)
                elif ir_type == 'TypeConversion':
                    ir_dict = ir_util.type_conversion(security_variables, line_number, ir, ir_dict)
                elif ir_type == 'InternalCall':
                    ir_dict, vuln = ir_util.internal_call(function, node, security_variables, line_number, ir, ir_dict,
                                                          analyser, FunctionCallEnum.internal)
                    vulnerabilities.extend(vuln)
                elif ir_type == 'Binary':
                    ir_dict, vuln = ir_util.binary(node, security_variables, line_number, ir, ir_dict, analyser)
                    vulnerabilities.extend(vuln)


        lvalues = []
        rvalues = []
        for vuln in vulnerabilities:
            lvalues.extend(vuln.lvalues)
            rvalues.extend(vuln.rvalues)
        lvalues = list(set(lvalues))
        rvalues = list(set(rvalues))

        # control flow
        control_flows = analyser.control_flows[-1].security_variables if (
                analyser.control_flows and analyser.control_flows[-1].security_variables) else []
        rvalues.extend(control_flows)


        # condition
        if not vulnerabilities[0].rvalues:
            condition_return_num = 0
            for fun_node in function.nodes:
                for node_ir in fun_node.irs:
                    if node_ir.__class__.__name__ == 'Return':
                        condition_return_num += 1
            for fun_node in function.nodes:
                if fun_node.expression:
                    node_number = expression_util.get_line_number(fun_node)
                    if condition_return_num > 1 and node_number in returns_nums:
                        vulnerabilities = function_returns_tuple(function, fun_node, security_variables, node_number, analyser)

    return vulnerabilities


def function_returns_tuple(function, node, security_variables, line_number, analyser):
    vulnerabilities = []
    return_variables = []
    function_variable = None
    security_level = SecurityEnum.L
    vulnerable_type = VulnerabilityEnum.none

    function_line_number = expression_util.get_line_number(function)

    for variable in security_variables:
        if variable.line_number == function_line_number and variable.name == function.name:
            function_variable = variable

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Return':
            values = ir.values
            for value in values:
                reference_numbers = []
                references = value.references[:-1]
                if references:
                    reference_numbers.append(int(str(references[-1]).split('#')[1]))
                for reference in references:
                    reference_number = int(str(reference).split('#')[1])
                    for func_node in function.nodes:
                        if expression_util.get_line_number(func_node) == reference_number:
                            reference_numbers.append(reference_number)
                reference_numbers = list(set(reference_numbers))
                for reference_number in reference_numbers:
                    for security_variable in security_variables:
                        if security_variable.name == value.name and reference_number == security_variable.line_number:
                            return_variables.append(security_variable)

            for variable in return_variables:
                if variable.security_level == SecurityEnum.H:
                    security_level = SecurityEnum.H


    return vulnerabilities
