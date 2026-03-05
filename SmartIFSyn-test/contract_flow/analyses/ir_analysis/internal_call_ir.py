# ir functions of ir_type 'SolidityCall'
from ...core.enums.expression_enum import ExpressionEnum
from ...core.enums.function_call_enum import FunctionCallEnum
from ...utils.analyse_util import traverse_ir_variable


def update_internal_call_vulnerabilities(vulnerabilities, argument_list, internal_call_function, constant_list, constant_dict, scope_start, scope_end, call_type):
    local_defined_variables = []

    def update_vuln(vuln, local_defined_variables):
        for argument, f_argument in zip(argument_list, internal_call_function.parameters):
            for i in range(len(vuln.lvalues)):
                lvalue = vuln.lvalues[i]
                if lvalue.name == f_argument.name and scope_start <= lvalue.line_number <= scope_end:
                    vuln.lvalues[i] = argument
            for i in range(len(vuln.rvalues)):
                rvalue = vuln.rvalues[i]
                if rvalue.name == f_argument.name and scope_start <= rvalue.line_number <= scope_end:
                    vuln.rvalues[i] = argument
        for constant in constant_list:
            for i in range(len(vuln.lvalues)):
                lvalue = vuln.lvalues[i]
                if lvalue.name == constant.name and constant.name in constant_dict and scope_start <= lvalue.line_number <= scope_end:
                    vuln.lvalues[i] = constant
            for i in range(len(vuln.rvalues)):
                rvalue = vuln.rvalues[i]
                if rvalue.name == constant.name and constant.name in constant_dict and scope_start <= rvalue.line_number <= scope_end:
                    vuln.rvalues[i] = constant

        if vuln.expression_type == ExpressionEnum.local_define and call_type == FunctionCallEnum.internal and vuln.lvalues:
            local_defined_variables.append(vuln.lvalues[0])

        if vuln.expression_type == ExpressionEnum.identifier_return and call_type == FunctionCallEnum.internal:
            if len(vuln.rvalues) == 1 and vuln.rvalues[0].defined:
                for local_variable in local_defined_variables:
                    if (vuln.rvalues[0].source and vuln.rvalues[0].source.line_number == local_variable.line_number
                            and vuln.rvalues[0].source.name == local_variable.name and local_variable.rvalues):
                        vuln.rvalues = local_variable.rvalues

        if vuln.sub_vulnerabilities:
            for sub_vuln in vuln.sub_vulnerabilities:
                update_vuln(sub_vuln, local_defined_variables)

    for vuln in vulnerabilities:
        update_vuln(vuln, local_defined_variables)

    return vulnerabilities, local_defined_variables


def update_sub_vulnerabilities(vuln_var, ir_dict):
    if vuln_var.sub_vulnerabilities is None:
        return vuln_var, ir_dict
    for sub_index in range(len(vuln_var.sub_vulnerabilities)):
        sub_vuln = vuln_var.sub_vulnerabilities[sub_index]
        lvalues = []
        rvalues = []

        for lvalue in sub_vuln.lvalues:
            if lvalue.name not in ir_dict:
                lvalues.append(lvalue)
            else:
                lvalues.extend(
                    [value.security_variable for value in traverse_ir_variable(ir_dict[lvalue.name]) if value.is_security_variable]
                )

        for rvalue in sub_vuln.rvalues:
            if rvalue.name not in ir_dict:
                rvalues.append(rvalue)
            else:
                rvalues.extend(
                    [value.security_variable for value in traverse_ir_variable(ir_dict[rvalue.name]) if value.is_security_variable]
                )

        vuln_var.sub_vulnerabilities[sub_index].lvalues = lvalues
        vuln_var.sub_vulnerabilities[sub_index].rvalues = rvalues

        update_sub_vulnerabilities(vuln_var.sub_vulnerabilities[sub_index], ir_dict)

    return vuln_var, ir_dict
