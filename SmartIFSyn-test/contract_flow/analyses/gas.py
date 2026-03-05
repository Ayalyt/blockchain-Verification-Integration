from ..core.enums.expression_enum import ExpressionEnum
from ..core.enums.security_enum import SecurityEnum
from ..core.vulnerability.vulnerability import Vulnerability

# unbounded_loop
def unbounded_loop(function, node, security_variables, line_number, analyser):
    rvalues = []
    vulnerabilities = []
    out_of_gas = False
    dynamic_structure = ''
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Length':
            if hasattr(ir.value.type, 'is_dynamic_array') and (function.visibility == 'external' or function.visibility == 'public'):
                out_of_gas = ir.value.type.is_dynamic_array
            dynamic_structure = str(ir.value)
        elif ir_type == 'Binary':
            if out_of_gas and (str(ir.variable_left) == 'msg.gas' or str(ir.variable_right) == 'msg.gas'):
                out_of_gas = False

    if out_of_gas:
        for variable in security_variables:
            if variable.name == dynamic_structure and variable.line_number == line_number and variable.security_level == SecurityEnum.H:
                rvalues.extend([variable])
        if rvalues:
            vulnerability_variable = Vulnerability([], rvalues, str(node.expression), line_number, analyser.vuln_mode,
                                               ExpressionEnum.out_of_gas)
            vulnerabilities.append(vulnerability_variable)


    return vulnerabilities