# some functions of class Analyser
import re
from ...analyses import access, gas
from ...analyses import identifier
from ...analyses import assignment
from ...analyses import function_call
from ...analyses.pre_analysis import declassify
from ..enums.expression_enum import ExpressionEnum
from ..enums.security_enum import SecurityEnum
from ..enums.vulnerablity_enum import VulnerabilityEnum
from ..variables.control_flow import ControlFlow
from ..vulnerability.vulnerability import Vulnerability
from ...utils import ir_check_util, lattice_util
from ...utils import expression_util
from ...analyses import tuple_expression


# check vulnerability
def check_vulnerability(analyser):
    target_contract = analyser.target_contract
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    vulnerabilities = []

    changed = True
    while changed:
        changed = False
        old_types = {var.name: var.security_level for var in analyser.security_variables}

        for contract in contracts:
            library_functions = [call[1] for call in contract.all_library_calls]
            contract_functions = contract.functions + library_functions
            for function in contract_functions:
                function_nodes = function.nodes
                # modifier
                for modifier in reversed(function.modifiers):
                    new_nodes = []
                    for node in modifier.nodes:
                        if str(node.type) == 'NodeType.PLACEHOLDER':
                            new_nodes.extend(function_nodes)
                        else:
                            new_nodes.append(node)
                    function_nodes = new_nodes

                # pre-analysis: declassify
                if analyser.vuln_mode == VulnerabilityEnum.integrity:
                    analyser.security_variables = declassify.declassify_variables(function, function_nodes, analyser.security_variables, contract_functions)

        new_types = {var.name: var.security_level for var in analyser.security_variables}
        if new_types != old_types:
            changed = True

    for contract in contracts:
        library_functions = [call[1] for call in contract.all_library_calls]
        contract_functions = contract.functions + library_functions
        for function in contract_functions:
            analyser.control_flows = []
            function_nodes = function.nodes
            for modifier in reversed(function.modifiers):
                new_nodes = []
                for node in modifier.nodes:
                    if str(node.type) == 'NodeType.PLACEHOLDER':
                        new_nodes.extend(function_nodes)
                    else:
                        new_nodes.append(node)
                function_nodes = new_nodes

            for node in function_nodes:
                vulnerabilities.extend(analyse_node(function, node, analyser.security_variables, analyser))
            vulnerabilities.extend(analyse_function(function, analyser.security_variables, analyser))

    return sorted(list(set(vulnerabilities)), key=lambda obj: getattr(obj, 'line_number'))


# analyse function
def analyse_function(function, security_variables, analyser):
    vulnerabilities = []
    input_variables = []
    lvalues = []
    rvalues = []

    line_number = expression_util.get_line_number(function)
    for parameter in function.parameters:
        for variable in analyser.core_variables:
            if line_number == variable.line_number and parameter.name == variable.name:
                input_variables.append(variable)

    # check public call
    if (not function.view and not function.pure and analyser.vuln_mode == VulnerabilityEnum.confidentiality
            and (str(function.visibility) == 'public' or str(function.visibility) == 'external') and
            lattice_util.lowest_upper_bound(input_variables) == SecurityEnum.H):
        for variable in security_variables:
            if variable.source in input_variables:
                rvalues.append(variable)
        vulnerable_type = analyser.vuln_mode
        expression_type = ExpressionEnum.public_call
        vulnerability_variable = Vulnerability(lvalues, rvalues, str(function.full_name), line_number,
                                               vulnerable_type, expression_type)
        vulnerabilities.append(vulnerability_variable)

    return vulnerabilities


# analyse node
def analyse_node(function, node, security_variables, analyser):
    vulnerabilities = []
    # patterns
    index_pattern = r'\w+\[[^\]]+\]'

    expression_type = node.expression.__class__.__name__

    if expression_type == 'AssignmentOperation':
        vulnerabilities.extend(analyse_assignment(function, node, security_variables, analyser))
        # index
        if re.search(index_pattern, str(node.expression.expression_left)) is not None:
            vulnerabilities.extend(access.index_equal(function, node, security_variables,
                                                      expression_util.get_line_number(node.expression), analyser))
    elif expression_type == 'CallExpression':
        vulnerabilities.extend(analyse_call_expression(function, node, security_variables, analyser))
    elif expression_type == 'Identifier':
        vulnerabilities.extend(analyse_identifier(function, node, security_variables, analyser))
    elif expression_type == 'UnaryOperation':
        vulnerabilities.extend(analyse_unary(function, node, security_variables, analyser))
    elif expression_type == 'BinaryOperation':
        vulnerabilities.extend(analyse_binary(function, node, security_variables, analyser))
    elif expression_type == 'TupleExpression':
        vulnerabilities.extend(analyse_tuple_expression(function, node, security_variables, analyser))
    elif expression_type == 'MemberAccess':
        vulnerabilities.extend(analyse_member_access(function, node, security_variables, analyser))
    elif expression_type == 'IndexAccess':
        vulnerabilities.extend(analyse_index_access(function, node, security_variables, analyser))
    elif expression_type == 'TypeConversion':
        vulnerabilities.extend(analyse_type_conversion(function, node, security_variables, analyser))
    elif str(node) == 'END_IF':
        while analyser.control_flows:
            top = analyser.control_flows[-1]
            if top.expression_type == ExpressionEnum.exp_if:
                analyser.control_flows.pop()
                break
            else:
                analyser.control_flows.pop()
    elif str(node) == 'END_LOOP':
        while analyser.control_flows:
            top = analyser.control_flows[-1]
            if top.expression_type == ExpressionEnum.loop:
                analyser.control_flows.pop()
                break
            else:
                analyser.control_flows.pop()

    return vulnerabilities




# analyse assignment
def analyse_assignment(function, node, security_variables, analyser):

    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    # simple assignments
    vulnerabilities.extend(assignment.handle_assignment(function, node, security_variables, line_number, analyser))

    return vulnerabilities


# analyse callExpression
def analyse_call_expression(function, node, security_variables, analyser):

    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    # check push
    if '.push' in str(node.expression):
        vulnerabilities.extend(function_call.push(function, node, security_variables, line_number, analyser))
    # check event
    elif ir_check_util.check_event(node):
        vulnerabilities.extend(function_call.event(node, security_variables, line_number, analyser))
    # check transfer
    elif ir_check_util.check_transfer(node):
        vulnerabilities.extend(function_call.transfer(function, node, security_variables, line_number, analyser))
    # check self-destruct
    elif ir_check_util.check_self_destruct(node):
        vulnerabilities.extend(function_call.self_destruct(node, security_variables, line_number, analyser))
    # check high-level call
    elif ir_check_util.check_high_level_call(node):
        vulnerabilities.extend(function_call.high_level_call(function, analyser, node, security_variables, line_number))
    # check require
    elif ir_check_util.check_require(node):
        vulnerabilities.extend(function_call.require(function, node, security_variables, line_number, analyser))
    # check internal call
    elif ir_check_util.check_internal_call(node):
        vulnerabilities.extend(function_call.internal_call(function, node, security_variables, line_number, analyser))
    # check send
    elif ir_check_util.check_send(node):
        vulnerabilities.extend(function_call.send(function, node, security_variables, line_number, analyser))
    # check low-level call
    elif ir_check_util.check_low_level_call(node):
        vulnerabilities.extend(function_call.low_level_call(function, node, security_variables, line_number, analyser))
    # check revert
    elif ir_check_util.check_revert(node):
        vulnerabilities.extend(function_call.revert(function, node, security_variables, line_number, analyser))
    # check assert
    elif ir_check_util.check_assert(node):
        vulnerabilities.extend(function_call.sol_assert(function, node, security_variables, line_number, analyser))
    # check store
    elif ir_check_util.check_store(node):
        vulnerabilities.extend(function_call.store(function, node, security_variables, line_number, analyser))
    return vulnerabilities


# analyse identifier
def analyse_identifier(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    # check return
    if ir_check_util.check_return(node):
        vulnerabilities.extend(identifier.identifier_return(function, node, security_variables, line_number, analyser))
    elif ir_check_util.check_if(node):
        analyser.control_flows.append(analyse_control_flow(security_variables, line_number, analyser))

    return vulnerabilities


# analyse unary
def analyse_unary(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    # check send
    if ir_check_util.check_send(node):
        vulnerabilities.extend(function_call.send(function, node, security_variables, line_number, analyser))
    # check internal call
    elif ir_check_util.check_internal_call(node):
        vulnerabilities.extend(function_call.internal_call(function, node, security_variables, line_number, analyser))
    # check solidity call
    elif ir_check_util.check_low_level_call(node):
        vulnerabilities.extend(function_call.low_level_call(function, node, security_variables, line_number, analyser))
    elif ir_check_util.check_if(node):
        analyser.control_flows.append(analyse_control_flow(security_variables, line_number, analyser))


    return vulnerabilities


# analyse binary
def analyse_binary(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    if ir_check_util.check_return(node):
        vulnerabilities.extend(identifier.identifier_return(function, node, security_variables, line_number, analyser))
    elif ir_check_util.check_if(node):
        analyser.control_flows.append(analyse_control_flow(security_variables, line_number, analyser))
    elif ir_check_util.check_loop(node, line_number, analyser):
        analyser.control_flows.append(analyse_control_flow(security_variables, line_number, analyser))
        vulnerabilities.extend(gas.unbounded_loop(function, node, security_variables, line_number, analyser))

    return vulnerabilities


# analyse tuple expression
def analyse_tuple_expression(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    # check return
    if ir_check_util.check_return(node):
        vulnerabilities.extend(tuple_expression.tuple_return(function, node, security_variables, line_number, analyser))

    return vulnerabilities


# analyse member access
def analyse_member_access(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    vulnerabilities.extend(access.member(function, node, security_variables, line_number, analyser))

    return vulnerabilities


# analyse index access
def analyse_index_access(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)
    if ir_check_util.check_if(node):
        analyser.control_flows.append(analyse_control_flow(security_variables, line_number, analyser))
    vulnerabilities.extend(access.index(function, node, security_variables, line_number, analyser))
    return vulnerabilities


# analyse type conversion
def analyse_type_conversion(function, node, security_variables, analyser):
    vulnerabilities = []
    line_number = expression_util.get_line_number(node.expression)

    # check return
    if ir_check_util.check_return(node):
        vulnerabilities.extend(identifier.identifier_return(function, node, security_variables, line_number, analyser))

    return vulnerabilities


# analyse control_flow
def analyse_control_flow(security_variables, line_number, analyser):
    variables = analyser.control_flows[-1].security_variables if (
                analyser.control_flows and analyser.control_flows[-1].security_variables) else []
    for var in security_variables:
        if var.line_number == line_number and (not var.defined):
            variables.append(var)
        elif var.line_number == line_number and var.defined and var.rvalues:
            for v in var.rvalues:
                if not v.defined:
                    variables.append(v)
    return ControlFlow(lattice_util.lowest_upper_bound(variables), ExpressionEnum.exp_if, variables)

