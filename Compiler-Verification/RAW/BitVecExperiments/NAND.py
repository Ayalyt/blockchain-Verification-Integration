import time
from z3 import *

from BitVecExperiments.FrFunctionModels.NAND_parser import NANDCircuitConstraintParser
from FrFunctionModels.XOR_parser import *


def run_NAND_constraint(p):
    s = Solver()
    bw = p.bit_length() * 2

    m1 = 21888242871839275222246405745257275088548364400416034343698204186575808495616

    a = Int('a')
    b = Int('b')
    out = Int('out')


    circom_constraint = out % p == (1 - (a * b) % p) % p
    R1CS_constraint = ((a * 1) % p * (b * 1) % p) % p == (1 + (out * m1) % p) % p
    implies_1 = Implies(circom_constraint, R1CS_constraint)
    implies_2 = Implies(R1CS_constraint, circom_constraint)
    target = And(implies_1, implies_2)

    s.add(Not(target))

    start = time.time()
    if s.check() == sat:
        model = s.model()
        print("a =", model[a].as_long())
        print("b =", model[b].as_long())
        print("out =", model[b].as_long())
    else:
        print("编译正确")
    end = time.time()
    print(f'time cost = {end - start}s')

def signalEqFrElement(s, fr: FrElement, p):
    R = 6350874878119819312338956282401532410528162663560392320966563075034087161851
    is_l = Extract(31, 31, fr.type)
    is_m = Extract(30, 30, fr.type)

    ln = And(is_l == 1, is_m == 0)
    lm = And(is_l == 1, is_m == 1)
    sn = And(is_l == 0, is_m == 0)
    sm = And(is_l == 0, is_m == 1)

    ln_case = s == BV2Int(fr.longVal, is_signed=False)
    lm_case = (s * R) % p == BV2Int(fr.longVal, is_signed=False)
    sn_case = s == BV2Int(fr.shortVal, is_signed=False)
    sm_case = (s * R) % p == BV2Int(fr.shortVal, is_signed=False)

    return And(Implies(ln, ln_case),
               Implies(lm, lm_case),
               Implies(sn, sn_case),
               Implies(sm, sm_case))


def run_NAND_calculation(p):
    s = Solver()
    a = Int('s_a')
    b = Int('s_b')
    out = Int('s_out')
    circom_calculation = out == (1 - (a * b) % p ) % p

    cpp_parser = NANDCircuitConstraintParser()
    cpp_calculation_raw = cpp_parser.parse_cpp_circuit()
    cons_list = []

    for item in cpp_calculation_raw:
        cons_list.append(item[2])

    cpp_calculation = And(cons_list)

    a_eq = signalEqFrElement(a, cpp_parser.variables['a'], p)
    b_eq = signalEqFrElement(b, cpp_parser.variables['b'], p)
    out_eq = signalEqFrElement(out, cpp_parser.variables['out'], p)

    input_eq = And(a_eq, b_eq)
    out_not_eq = Not(out_eq)

    s.add(input_eq)
    s.add(circom_calculation)
    s.add(cpp_calculation)
    s.add(out_not_eq)

    print('开始求解')
    if s.check() == sat:
        model = s.model()
        # print("a =", model[a].as_long())
        # print("b =", model[b].as_long())
        # print("out =", model[b].as_long())
    else:
        print("编译正确")