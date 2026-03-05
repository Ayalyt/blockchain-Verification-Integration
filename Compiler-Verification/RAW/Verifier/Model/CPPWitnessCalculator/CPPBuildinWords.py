from ..CircomSourceCode.CircomBuildinWords import *


class CPPBuildinWords:
    binary_op_map = {
        "Fr_add": EIO.Add,
        "Fr_sub": EIO.Sub,
        "Fr_mul": EIO.Mul,
        "Fr_div": EIO.Div,
        "Fr_band":EIO.BitAnd,
        "Fr_bor": EIO.BitOr,
        "Fr_bxor":EIO.BitXor,
        "Fr_shl": EIO.ShiftL,
        "Fr_shr": EIO.ShiftR,
        "Fr_pow": EIO.Pow,
        "Fr_idiv":EIO.IntDiv,
        "Fr_mod": EIO.Mod,

        "Fr_eq":  EIO.Eq,
        "Fr_neq": EIO.NotEq,
        "Fr_lt":  EIO.Lesser,
        "Fr_gt":  EIO.Greater,
        "Fr_leq": EIO.LesserEq,
        "Fr_geq": EIO.GreaterEq,
        "Fr_land": EIO.BoolAnd,
        "Fr_lor": EIO.BoolOr
    }

    unary_op_map = {
        "Fr_neg": EPO.Sub,  # e.g., Fr_neg(dest, src) -> dest = -src
        "Fr_not": EPO.BoolNot,  # e.g., Fr_not(dest, src) -> dest = !src
        "Fr_square": EPO.Square,
        "Fr_bnot": EPO.BitNot
    }