# verify utils
from z3 import *
from ..core.enums.expression_enum import ExpressionEnum
from ..core.enums.security_enum import SecurityEnum
from ..utils import lattice_util


# traverse add constraints
def traverse_add_constraints(vulnerabilities, solver, z3_vars):
    for vuln in vulnerabilities:
        if (vuln.expression_type == ExpressionEnum.assignment or vuln.expression_type == ExpressionEnum.push or
                vuln.expression_type == ExpressionEnum.access):
            right_side_or = Or([z3_vars[r_val] for r_val in vuln.rvalues])
            left_side_and = And([z3_vars[l_val] for l_val in vuln.lvalues])
            solver.add(Not(And(Not(left_side_and), right_side_or)))
            if lattice_util.lowest_upper_bound(vuln.rvalues) == SecurityEnum.H:
                solver.add_soft(right_side_or, 2)
        elif (vuln.expression_type == ExpressionEnum.event or vuln.expression_type == ExpressionEnum.sol_assert or
              vuln.expression_type == ExpressionEnum.out_of_gas):
            right_side_or = Or([z3_vars[r_val] for r_val in vuln.rvalues])
            solver.add(Not(right_side_or))
        elif vuln.expression_type == ExpressionEnum.transfer:
            right_side_or = Or([z3_vars[r_val] for r_val in vuln.rvalues])
            solver.add(Not(right_side_or))
        elif vuln.expression_type == ExpressionEnum.identifier_return:
            right_side_or = Or([z3_vars[r_val] for r_val in vuln.rvalues])
            left_side_and = And([z3_vars[l_val] for l_val in vuln.lvalues])
            solver.add(Not(And(Not(left_side_and), right_side_or)))
        elif vuln.expression_type == ExpressionEnum.local_define:
            right_side_or = Or(*[z3_vars[r_val] for r_val in vuln.rvalues])
            for l_val in vuln.lvalues:
                solver.add(z3_vars[l_val] == right_side_or)
        elif vuln.expression_type == ExpressionEnum.internal_call:
            solver, z3_vars = traverse_add_constraints(vuln.sub_vulnerabilities, solver, z3_vars)
        elif vuln.expression_type == ExpressionEnum.high_level_call:
            solver, z3_vars = traverse_add_constraints(vuln.sub_vulnerabilities, solver, z3_vars)
        elif vuln.expression_type == ExpressionEnum.low_level_call:
            right_side_or = Or([z3_vars[r_val] for r_val in vuln.rvalues])
            left_side_or = Or([z3_vars[l_val] for l_val in vuln.lvalues])
            solver.add(Not(Or(left_side_or, right_side_or)))
        elif vuln.expression_type == ExpressionEnum.public_call:
            right_side_or = Or([z3_vars[r_val] for r_val in vuln.rvalues])
            solver.add(Not(right_side_or))

    return solver, z3_vars


# traverse_get_assignments
def traverse_get_assignments(vulnerabilities):
    assignments = []

    def recurse(vuln_s):
        for vuln in vuln_s:
            assignments.append((vuln.lvalues, vuln.rvalues))
            if hasattr(vuln, 'sub_vulnerabilities') and vuln.sub_vulnerabilities:
                recurse(vuln.sub_vulnerabilities)

    recurse(vulnerabilities)
    return assignments
