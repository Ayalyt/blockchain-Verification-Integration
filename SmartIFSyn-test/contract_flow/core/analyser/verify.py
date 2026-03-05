# verify the security
from z3 import *
from ...utils import verify_util
from ..enums.security_enum import SecurityEnum


def verify_vulnerability(analyser):
    solutions = []
    solver = Optimize()
    variables = analyser.core_variables
    security_variables = analyser.security_variables
    vulnerabilities = analyser.vulnerabilities
    assignments = verify_util.traverse_get_assignments(analyser.vulnerabilities)

    # get vars from variables and assignments
    z3_vars = {var: Bool(f"obj_{var.name}_{var.line_number}") for var in variables}
    for l_vals, r_vals in assignments:
        for l_val in l_vals:
            z3_vars[l_val] = Bool(f"obj_{l_val.name}_{l_val.line_number}")
        for r_val in r_vals:
            z3_vars[r_val] = Bool(f"obj_{r_val.name}_{r_val.line_number}")
    for security_variable in security_variables:
        if security_variable not in z3_vars:
            # z3_vars[security_variable] = Bool(f"obj_{id(security_variable)}")
            z3_vars[security_variable] = Bool(f"obj_{security_variable.name}_{security_variable.line_number}")

    # set constraints
    solver, z3_vars = verify_util.traverse_add_constraints(vulnerabilities, solver, z3_vars)

    # add constraints of defined variables in the function
    for l_vals, r_vals in assignments:
        for l_val in l_vals:
            if l_val.source:
                solver.add(z3_vars[l_val] == z3_vars[l_val.source])
            if l_val.if_source:
                for source in l_val.if_source:
                    solver.add(z3_vars[l_val] == z3_vars[source])
        for r_val in r_vals:
            if r_val.source:
                solver.add(z3_vars[r_val] == z3_vars[r_val.source])
            if r_val.if_source:
                for source in r_val.if_source:
                    solver.add(z3_vars[r_val] == z3_vars[source])

    # soft constraints of reserved variables
    for key in z3_vars:
        if key.reserved:
            solver.add(z3_vars[key]) if key.security_level == SecurityEnum.H else solver.add(Not(z3_vars[key]))
        elif key.annotated:
            if key.security_level == SecurityEnum.L:
                solver.add_soft(Not(z3_vars[key]), 1)
            else:
                solver.add_soft(z3_vars[key], 1)
        else:
            if key.security_level == SecurityEnum.L:
                solver.add_soft(Not(z3_vars[key]), 0.5)
            else:
                solver.add_soft(z3_vars[key], 0.5)

    # get all solutions
    solver.check()
    model = solver.model()
    solution = {var: is_true(model[z3_vars[var]]) for var in variables}
    solutions.append(solution)

    analyser.set_solver(solver)

    return solutions, z3_vars
