# pre-analysis: declassify the variables when handling integrity
from ...core.enums.security_enum import SecurityEnum
from ...utils import expression_util, ir_check_util


# declassify variables
def declassify_variables(function, function_nodes, variables, contract_functions):
    security_variables = variables
    start, end = expression_util.get_scope(function)
    delegatecall_line_number = None
    require_line_number = None
    require_cond = []
    storage_var = None

    # check can declassify
    # for node in function.nodes:
    for node in function_nodes:
        # check declassify require
        expression_type = node.expression.__class__.__name__
        if expression_type == 'CallExpression' and ir_check_util.check_require(node) and '==' in str(node.expression):
            line_number = expression_util.get_line_number(node)
            for variable in security_variables:
                if variable.line_number == line_number and not variable.defined:
                    require_cond.append(variable)

            if len(require_cond) == 2 and '==' in str(node.expression):
                left, right = map(str.strip, str(node.expression).split('==', 1))
                if (require_cond[0].name in left and require_cond[1].name in left) or (require_cond[0].name in right and require_cond[1].name in right):
                    require_cond = []


            can_declassify = (
                    len(require_cond) == 2
                    and any(obj.security_level == SecurityEnum.L and obj.is_storage for obj in require_cond)
                    and any(obj.name == "msg.sender" for obj in require_cond)
            )
            if can_declassify:
                storage_var = next(
                    (obj for obj in require_cond if obj.security_level == SecurityEnum.L and obj.is_storage), None)
                require_line_number = line_number


    # check assignment and delegatecall
    if require_line_number:
        if not start <= require_line_number <= end:
            require_line_number = start
        stop_loop = False
        for fun in contract_functions:
            if stop_loop:
                break
            for node in fun.nodes:
                # check delegatecall
                if 'delegatecall' in str(node.expression):
                    line_number = expression_util.get_line_number(node)
                    delegatecall_line_number = line_number if (not delegatecall_line_number) else line_number
                    if not(require_line_number < line_number < end):
                        for variable in security_variables:
                            if variable.line_number == line_number and variable.security_level == SecurityEnum.H:
                                require_line_number = None
                                stop_loop = True
                                break

                # check assignment
                expression_type = node.expression.__class__.__name__
                if expression_type == 'AssignmentOperation':
                    line_number = expression_util.get_line_number(node)
                    if require_line_number and require_line_number < line_number < end:
                        continue
                    for ir in node.irs:
                        ir_type = ir.__class__.__name__
                        if ir_type == 'Assignment':
                            if ir.lvalue.name == storage_var.name:
                                for variable in security_variables:
                                    if (variable.line_number == line_number and variable.name == ir.rvalue.name
                                            and variable.security_level == SecurityEnum.H):
                                        require_line_number = None
                                        stop_loop = True

    # declassify
    if require_line_number:
        for variable in security_variables:
            if require_line_number <= variable.line_number < end and (not variable.is_storage) and (not "block" in variable.name)\
                    and (not 'now' in variable.name):
                variable.set_security_level(SecurityEnum.L)

    return security_variables