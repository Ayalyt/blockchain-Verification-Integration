import cvc5

from ..CircomSourceCode.CircomBuildinWords import EIO, EPO
from ...Tools.ColorPrint import colorPrint, COLOR
from ...Tools.Errors import UnSupportedOperators
from ...Tools.ExpandedCVC5 import ExpandedCVC5


def calculate_deterministic_infixOp(left, op, right, prime):
    if op == EIO.Add.value:
        return (left + right) % prime
    elif op == EIO.Sub.value:
        return (left - right) % prime
    elif op == EIO.Mul.value:
        return (left * right) % prime
    elif op == EIO.Div.value:
        rev = pow(right, -1, prime)
        return (left * rev) % prime
        # return (left // right) % prime
    elif op == EIO.IntDiv.value:
        return left // right
    elif op == EIO.Mod.value:
        return (left % right) % prime
    elif op == EIO.Pow.value:
        # return (left ** right) % prime
        return pow(left, right, prime)
    elif op == EIO.Lesser.value:
        return val(left, prime) < val(right, prime)
    elif op == EIO.LesserEq.value:
        return val(left, prime) <= val(right, prime)
    elif op == EIO.Greater.value:
        return val(left, prime) > val(right, prime)
    elif op == EIO.GreaterEq.value:
        return val(left, prime) >= val(right, prime)
    elif op == EIO.Eq.value:
        return val(left, prime) == val(right, prime)
    elif op == EIO.NotEq.value:
        return val(left, prime) != val(right, prime)
    elif op == EIO.ShiftR.value:
        return shift_right(left, right, prime)
    elif op == EIO.ShiftL.value:
        return shift_left(left, right, prime)
    elif op == EIO.BitAnd.value:
        return (left & right) % prime
    elif op == EIO.BitOr.value:
        return (left | right) % prime
    elif op == EIO.BitXor.value:
        return (left ^ right) % prime
    elif op == EIO.BoolAnd.value:
        return left and right
    elif op == EIO.BoolOr.value:
        return left or right
    else:
        colorPrint(f'WARNING: meet currently unsupported infix operator: {op}', COLOR.PURPLE)
        UnSupportedOperators()


def calculate_deterministic_prefixOp(op, right, prime):
    if op == EPO.Sub.value:
        return (-right) % prime
    elif op == EPO.BoolNot.value:
        return not right
    elif op == EPO.Complement.value or op == EPO.BitNot.value:
        m = prime.bit_length()
        all_ones = (1 << m) - 1
        complement = all_ones - right
        return complement % prime
        # MASK = prime.bit_length()
        # right &= MASK  
        # return ((~right) & MASK)% prime  
    else:
        colorPrint(f'WARNING: meet currently unsupported prefix operator: {op}', COLOR.PURPLE)
        UnSupportedOperators()


def shift_right(x, k, p):
    b = (p - 1).bit_length() 
    mask = (1 << b) - 1

    if 0 <= k <= p // 2:
        return x // (1 << k)  # x >> k
    elif p // 2 + 1 <= k < p:
        return (x * (1 << (p - k)) & mask) % p  # x << (p - k)


def shift_left(x, k, p):
    b = (p - 1).bit_length()
    mask = (1 << b) - 1

    if 0 <= k <= p // 2:
        return (x * (1 << k) & mask) % p  # x << k
    elif p // 2 + 1 <= k < p:
        return x // (1 << (p - k))  # x >> (p - k)


def val(raw, prime):
    if prime + 2 <= raw * 2 <= prime * 2:
        return raw - prime
    else:
        return raw


def arrangeNumber(array, prime):
    outcome = 0
    i = 0
    for item in reversed(array):
        outcome = outcome + item
        i = i + 1
        if i < len(array):
            outcome = outcome << 32
    return outcome % prime


'''
additional term will be added when dealing inv
'''
def generate_infix_term(left, op, right, solver: ExpandedCVC5)->(cvc5.Term, cvc5.Term):
    if op == EIO.Add.value:
        return solver.mkFFTerm_Add(left, right), None
    elif op == EIO.Sub.value:
        return solver.mkFFTerm_Sub(left, right), None
    elif op == EIO.Mul.value:
        return solver.mkFFTerm_Mul(left, right), None
    elif op == EIO.Div.value:
        return solver.mkFFTerm_Inv(left, right)
    elif op == EIO.IntDiv.value:
        return solver.mkFFTerm_IntDiv(left, right), None
    elif op == EIO.Mod.value:
        return solver.mkFFTerm_Mod(left, right), None
    elif op == EIO.Pow.value:
        return solver.mkFFTerm_Pow(left, right), None
    elif op == EIO.Lesser.value:
        return solver.mkFFTerm_Lt(left, right), None
    elif op == EIO.LesserEq.value:
        return solver.mkFFTerm_Le(left, right), None
    elif op == EIO.Greater.value:
        return solver.mkFFTerm_Gt(left, right), None
    elif op == EIO.GreaterEq.value:
        return solver.mkFFTerm_Ge(left, right), None
    elif op == EIO.Eq.value:
        return solver.mkFFTerm_Eq(left, right), None
    elif op == EIO.NotEq.value:
        return solver.mkFFTerm_Neq(left, right), None
    elif op == EIO.ShiftR.value:
        return solver.mkFFTerm_Right_Shift(left, right), None
    elif op == EIO.ShiftL.value:
        return solver.mkFFTerm_Left_Shift(left, right), None
    elif op == EIO.BitAnd.value:
        return solver.mkFFTerm_Bit_And(left, right), None
    elif op == EIO.BitOr.value:
        return solver.mkFFTerm_Bit_Or(left, right), None
    elif op == EIO.BitXor.value:
        return solver.mkFFTerm_Bit_Xor(left, right), None
    elif op == EIO.BoolAnd.value:
        return solver.mkBool_And(left, right), None
    elif op == EIO.BoolOr.value:
        return solver.mkBool_Or(left, right), None
    else:
        colorPrint(f'WARNING: meet currently unsupported infix operator: {op}', COLOR.PURPLE)
        UnSupportedOperators()


def generate_prefix_term(op, right, solver: ExpandedCVC5)->cvc5.Term:
    if op == EPO.Sub.value:
        return solver.mkFFTerm_Neg(right)
    elif op == EPO.BoolNot.value:
        return solver.mkBool_Not(right)
    elif op == EPO.Complement.value or op == EPO.BitNot.value:
        return solver.mkFFTerm_bit_Complement(right)
    elif op == EPO.Square.value:
        return solver.mkFFTerm_Mul(right, right)
    else:
        colorPrint(f'WARNING: meet currently unsupported prefix operator: {op}', COLOR.PURPLE)
        UnSupportedOperators()

def generate_prefix_term(op, right, solver: ExpandedCVC5) -> cvc5.Term:
    if op == EPO.Sub.value:
        return solver.mkFFTerm_Neg(right)
    
    elif op == EPO.BoolNot.value:
        return solver.mkBool_Not(right)
        
    elif op == EPO.Complement.value:
        return solver.mkFFTerm_bit_Complement(right)
    elif op == EPO.Add.value:
        return right
        
    else:
        colorPrint(f'WARNING: meet currently unsupported prefix operator: {op}', COLOR.PURPLE)
        UnSupportedOperators()