# analyse util
# functions used in other utils
import random

from ..utils import lattice_util
from ..core.enums.security_enum import SecurityEnum
from ..core.enums.expression_enum import ExpressionEnum


# traverse ir variable
def traverse_ir_variable(ir_variable):
    if not ir_variable:
        return []

    result = [ir_variable]
    if isinstance(ir_variable.left_variable, list):
        for left_var in ir_variable.left_variable:
            result.extend(traverse_ir_variable(left_var))
    else:
        result.extend(traverse_ir_variable(ir_variable.left_variable))

    if isinstance(ir_variable.right_variable, list):
        for right_var in ir_variable.right_variable:
            result.extend(traverse_ir_variable(right_var))
    else:
        result.extend(traverse_ir_variable(ir_variable.right_variable))

    return result


# Branch merging
def vulnerability_branch_merge(vulnerabilities):
    line_dict = {}

    for vuln in vulnerabilities:
        if vuln.line_number in line_dict:
            line_dict[vuln.line_number].append(vuln)
        else:
            line_dict[vuln.line_number] = [vuln]

    updated_vulnerabilities = []

    for line_number, vuln_list in line_dict.items():
        assignments_vuln = [vuln for vuln in vuln_list if vuln.expression_type == ExpressionEnum.local_define]
        if len(assignments_vuln) > 1:
            high_vuln = [vuln for vuln in assignments_vuln if lattice_util.lowest_upper_bound(vuln.rvalues)==SecurityEnum.H]
            if high_vuln:
                updated_vulnerabilities.extend(high_vuln)
            else:
                updated_vulnerabilities.append(random.choice(assignments_vuln))
        else:
            updated_vulnerabilities.extend(vuln_list)

    return updated_vulnerabilities
