from z3 import *
import sys
import os

# 添加当前目录到路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入其他约束生成器
from fr_to_montgomery_constraint import FrToMontgomeryConstraint
from fr_to_long_normal_constraint import FrToLongNormalConstraint


class FrElement:
    """Fr_Element数据结构，表示有限域元素"""

    def __init__(self, name_prefix: str):
        # 创建位向量变量
        self.shortVal = BitVec(f'{name_prefix}_shortVal', 32)
        self.longVal = BitVec(f'{name_prefix}_longVal', 256)
        self.type = BitVec(f'{name_prefix}_type', 32)

    def get_dict(self):
        """返回字典格式，便于访问"""
        return {
            'shortVal': self.shortVal,
            'longVal': self.longVal,
            'type': self.type
        }


class FrMulConstraint:
    """Fr_mul约束生成器"""

    def __init__(self):
        # 模数p (256位)
        self.p = BitVecVal(0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001, 256)

        # Montgomery常数
        self.R = BitVecVal(0x0e0a77c19a07df2f666ea36f7879462e36fc76959f60cd29ac96341c4ffffffb, 256)
        self.R2 = BitVecVal(0x0216d0b17f4e44a58c49833d53bb808553fe3ab1e35c59e31bb8e645ae216da7, 256)

        # 类型常量
        self.Fr_SHORT = 0
        self.Fr_LONG = 1
        self.Fr_LONGMONTGOMERY = 2
        self.Fr_SHORTMONTGOMERY = 3

        # 创建转换约束生成器
        self.to_montgomery_gen = FrToMontgomeryConstraint()
        self.to_long_normal_gen = FrToLongNormalConstraint()

    def create_fr_element(self, name: str) -> FrElement:
        """创建Fr_Element实例"""
        return FrElement(name)

    def get_f_a(self, a_dict):
        """计算f_a (根据a的类型)"""
        return If(a_dict['type'] == self.Fr_SHORT,
                  SignExt(224, a_dict['shortVal']) % self.p,
                  a_dict['longVal'])

    def get_f_b(self, b_dict):
        """计算f_b (根据b的类型)"""
        return If(b_dict['type'] == self.Fr_SHORT,
                  SignExt(224, b_dict['shortVal']) % self.p,
                  b_dict['longVal'])

    def convert_to_montgomery(self, input_element: FrElement) -> tuple:
        """将元素转换为Montgomery形式"""
        temp_element = self.create_fr_element("temp_montgomery")
        constraint = self.to_montgomery_gen.generate_fr_constraint(temp_element, input_element)
        return temp_element, constraint

    def convert_to_long_normal(self, input_element: FrElement) -> tuple:
        """将元素转换为长整数普通形式"""
        temp_element = self.create_fr_element("temp_long_normal")
        constraint = self.to_long_normal_gen.generate_fr_constraint(temp_element, input_element)
        return temp_element, constraint

    def mul_l1ml2m(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数Montgomery，b是长整数Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # Montgomery乘法: (a.longVal * b.longVal * R^(-1)) % p
        # 由于都是Montgomery形式，结果也是Montgomery形式
        # 这里简化处理，实际Montgomery乘法需要更复杂的算法
        product = (a_dict['longVal'] * b_dict['longVal'] * self.R) % self.p

        return And(
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_l1ml2n(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数Montgomery，b是长整数非Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将b转换为Montgomery形式
        b_montgomery, b_montgomery_constraint = self.convert_to_montgomery(b)

        # 然后进行Montgomery乘法
        product = (a_dict['longVal'] * b_montgomery.longVal * self.R) % self.p

        return And(
            b_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_l1nl2m(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数非Montgomery，b是长整数Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将a转换为Montgomery形式
        a_montgomery, a_montgomery_constraint = self.convert_to_montgomery(a)

        # 然后进行Montgomery乘法
        product = (a_montgomery.longVal * b_dict['longVal'] * self.R) % self.p

        return And(
            a_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_l1nl2n(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数非Montgomery，b是长整数非Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 普通乘法: (a.longVal * b.longVal) % p
        product = (a_dict['longVal'] * b_dict['longVal']) % self.p

        return And(
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONG,
            r_dict['shortVal'] == 0
        )

    def mul_l1ms2m(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数Montgomery，b是短整数Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将b转换为Montgomery形式
        b_montgomery, b_montgomery_constraint = self.convert_to_montgomery(b)

        # 然后进行Montgomery乘法
        product = (a_dict['longVal'] * b_montgomery.longVal * self.R) % self.p

        return And(
            b_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_l1ms2n(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数Montgomery，b是短整数非Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将b转换为Montgomery形式
        b_montgomery, b_montgomery_constraint = self.convert_to_montgomery(b)

        # 然后进行Montgomery乘法
        product = (a_dict['longVal'] * b_montgomery.longVal * self.R) % self.p

        return And(
            b_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_l1ns2m(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数非Montgomery，b是短整数Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将a转换为Montgomery形式
        a_montgomery, a_montgomery_constraint = self.convert_to_montgomery(a)

        # 使用toMontgomery约束将b转换为Montgomery形式
        b_montgomery, b_montgomery_constraint = self.convert_to_montgomery(b)

        # 然后进行Montgomery乘法
        product = (a_montgomery.longVal * b_montgomery.longVal * self.R) % self.p

        return And(
            a_montgomery_constraint,  # 添加转换约束
            b_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_l1ns2n(self, r: FrElement, a: FrElement, b: FrElement):
        """a是长整数非Montgomery，b是短整数非Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toLongNormal约束将b转换为长整数形式
        b_long_normal, b_long_normal_constraint = self.convert_to_long_normal(b)

        # 然后进行普通乘法
        product = (a_dict['longVal'] * b_long_normal.longVal) % self.p

        return And(
            b_long_normal_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONG,
            r_dict['shortVal'] == 0
        )

    def mul_s1ml2m(self, r: FrElement, a: FrElement, b: FrElement):
        """a是短整数Montgomery，b是长整数Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将a转换为Montgomery形式
        a_montgomery, a_montgomery_constraint = self.convert_to_montgomery(a)

        # 然后进行Montgomery乘法
        product = (a_montgomery.longVal * b_dict['longVal'] * self.R) % self.p

        return And(
            a_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_s1ml2n(self, r: FrElement, a: FrElement, b: FrElement):
        """a是短整数Montgomery，b是长整数非Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将a转换为Montgomery形式
        a_montgomery, a_montgomery_constraint = self.convert_to_montgomery(a)

        # 使用toMontgomery约束将b转换为Montgomery形式
        b_montgomery, b_montgomery_constraint = self.convert_to_montgomery(b)

        # 然后进行Montgomery乘法
        product = (a_montgomery.longVal * b_montgomery.longVal * self.R) % self.p

        return And(
            a_montgomery_constraint,  # 添加转换约束
            b_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_s1nl2m(self, r: FrElement, a: FrElement, b: FrElement):
        """a是短整数非Montgomery，b是长整数Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toMontgomery约束将a转换为Montgomery形式
        a_montgomery, a_montgomery_constraint = self.convert_to_montgomery(a)

        # 然后进行Montgomery乘法
        product = (a_montgomery.longVal * b_dict['longVal'] * self.R) % self.p

        return And(
            a_montgomery_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONGMONTGOMERY,
            r_dict['shortVal'] == 0
        )

    def mul_s1nl2n(self, r: FrElement, a: FrElement, b: FrElement):
        """a是短整数非Montgomery，b是长整数非Montgomery"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 使用toLongNormal约束将a转换为长整数形式
        a_long_normal, a_long_normal_constraint = self.convert_to_long_normal(a)

        # 然后进行普通乘法
        product = (a_long_normal.longVal * b_dict['longVal']) % self.p

        return And(
            a_long_normal_constraint,  # 添加转换约束
            r_dict['longVal'] == product,
            r_dict['type'] == self.Fr_LONG,
            r_dict['shortVal'] == 0
        )

    def mul_s1s2(self, r: FrElement, a: FrElement, b: FrElement):
        """a是短整数，b是短整数"""
        r_dict = r.get_dict()
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 短整数乘法，检查是否溢出
        product_short = a_dict['shortVal'] * b_dict['shortVal']

        # 如果溢出，使用长整数表示
        # 使用Z3的比较函数而不是Python的布尔运算
        overflow = product_short >= BitVecVal(2 ** 31, 32)

        return If(overflow,
                  And(
                      r_dict['longVal'] == SignExt(224, product_short),
                      r_dict['type'] == self.Fr_LONG,
                      r_dict['shortVal'] == 0
                  ),
                  And(
                      r_dict['longVal'] == 0,
                      r_dict['type'] == self.Fr_SHORT,
                      r_dict['shortVal'] == product_short
                  ))

    def generate_fr_constraint(self, r: FrElement, a: FrElement, b: FrElement) -> ExprRef:
        """
        生成Fr_mul的Fr_Constraint

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element a
            b: 输入Fr_Element b

        Returns:
            Z3约束表达式
        """
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 定义各种类型组合条件
        a_l = (a_dict['type'] == self.Fr_LONG)
        a_s = (a_dict['type'] == self.Fr_SHORT)
        a_n = (a_dict['type'] == self.Fr_LONG)
        a_m = (a_dict['type'] == self.Fr_LONGMONTGOMERY)

        b_l = (b_dict['type'] == self.Fr_LONG)
        b_s = (b_dict['type'] == self.Fr_SHORT)
        b_n = (b_dict['type'] == self.Fr_LONG)
        b_m = (b_dict['type'] == self.Fr_LONGMONTGOMERY)

        # 组合条件
        mul_l1ml2m = And(a_l, a_m, b_l, b_m)
        mul_l1ml2n = And(a_l, a_m, b_l, b_n)
        mul_l1nl2m = And(a_l, a_n, b_l, b_m)
        mul_l1nl2n = And(a_l, a_n, b_l, b_n)
        mul_l1ms2m = And(a_l, a_m, b_s, b_m)
        mul_l1ms2n = And(a_l, a_m, b_s, b_n)
        mul_l1ns2m = And(a_l, a_n, b_s, b_m)
        mul_l1ns2n = And(a_l, a_n, b_s, b_n)
        mul_s1ml2m = And(a_s, a_m, b_l, b_m)
        mul_s1ml2n = And(a_s, a_m, b_l, b_n)
        mul_s1nl2m = And(a_s, a_n, b_l, b_m)
        mul_s1nl2n = And(a_s, a_n, b_l, b_n)
        mul_s1s2 = And(a_s, b_s)

        # 组合所有条件
        return And(
            Implies(mul_l1ml2m, self.mul_l1ml2m(r, a, b)),
            Implies(mul_l1ml2n, self.mul_l1ml2n(r, a, b)),
            Implies(mul_l1nl2m, self.mul_l1nl2m(r, a, b)),
            Implies(mul_l1nl2n, self.mul_l1nl2n(r, a, b)),
            Implies(mul_l1ms2m, self.mul_l1ms2m(r, a, b)),
            Implies(mul_l1ms2n, self.mul_l1ms2n(r, a, b)),
            Implies(mul_l1ns2m, self.mul_l1ns2m(r, a, b)),
            Implies(mul_l1ns2n, self.mul_l1ns2n(r, a, b)),
            Implies(mul_s1ml2m, self.mul_s1ml2m(r, a, b)),
            Implies(mul_s1ml2n, self.mul_s1ml2n(r, a, b)),
            Implies(mul_s1nl2m, self.mul_s1nl2m(r, a, b)),
            Implies(mul_s1nl2n, self.mul_s1nl2n(r, a, b)),
            Implies(mul_s1s2, self.mul_s1s2(r, a, b))
        )

    def generate_ff_constraint(self, r: FrElement, a: FrElement, b: FrElement) -> ExprRef:
        """
        生成Fr_mul的FF_Constraint

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element a
            b: 输入Fr_Element b

        Returns:
            Z3约束表达式
        """
        a_dict = a.get_dict()
        b_dict = b.get_dict()

        # 计算f_a和f_b
        f_a = self.get_f_a(a_dict)
        f_b = self.get_f_b(b_dict)

        # 创建r_2和r_2_type变量
        r_2 = BitVec('r_2', 256)
        r_2_type = BitVec('r_2type', 32)

        # 简单的有限域乘法: (f_a * f_b) % p
        product_val = (f_a * f_b) % self.p

        return And(
            r_2 == product_val,
            r_2_type == self.Fr_LONG  # 结果总是长整数形式
        )

    def verify_equivalence(self, r: FrElement, a: FrElement, b: FrElement) -> bool:
        """
        验证Fr_Constraint和FF_Constraint的等价性

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element a
            b: 输入Fr_Element b

        Returns:
            True如果等价，False否则
        """
        solver = Solver()

        # 添加类型约束
        solver.add(Or(a.type == self.Fr_SHORT,
                      a.type == self.Fr_LONG,
                      a.type == self.Fr_LONGMONTGOMERY,
                      a.type == self.Fr_SHORTMONTGOMERY))
        solver.add(Or(b.type == self.Fr_SHORT,
                      b.type == self.Fr_LONG,
                      b.type == self.Fr_LONGMONTGOMERY,
                      b.type == self.Fr_SHORTMONTGOMERY))

        # 生成约束
        fr_constraint = self.generate_fr_constraint(r, a, b)
        ff_constraint = self.generate_ff_constraint(r, a, b)

        # 添加约束
        solver.add(fr_constraint)
        solver.add(ff_constraint)

        # 检查等价性
        target = And(r.longVal == BitVec('r_2', 256),
                     r.type == BitVec('r_2type', 32))
        solver.add(Not(target))

        result = solver.check()
        return result == unsat


def test_fr_mul():
    """测试Fr_mul约束生成"""
    print("=== 测试Fr_mul约束生成 ===")

    # 创建约束生成器
    constraint_gen = FrMulConstraint()

    # 创建Fr_Element实例
    r = constraint_gen.create_fr_element("r")
    a = constraint_gen.create_fr_element("a")
    b = constraint_gen.create_fr_element("b")

    print("Fr_Element结构:")
    print(f"  shortVal: {r.shortVal}")
    print(f"  longVal: {r.longVal}")
    print(f"  type: {r.type}")

    print("\n常量值:")
    print(f"  模数p: {constraint_gen.p}")
    print(f"  Montgomery常数R: {constraint_gen.R}")
    print(f"  R2: {constraint_gen.R2}")

    print("\n类型常量:")
    print(f"  Fr_SHORT: {constraint_gen.Fr_SHORT}")
    print(f"  Fr_LONG: {constraint_gen.Fr_LONG}")
    print(f"  Fr_LONGMONTGOMERY: {constraint_gen.Fr_LONGMONTGOMERY}")
    print(f"  Fr_SHORTMONTGOMERY: {constraint_gen.Fr_SHORTMONTGOMERY}")

    # 生成约束
    fr_constraint = constraint_gen.generate_fr_constraint(r, a, b)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a, b)

    print("\n生成的约束:")
    print(f"Fr_Constraint: {fr_constraint}")
    print(f"FF_Constraint: {ff_constraint}")

    # 验证等价性
    print("\n验证等价性...")
    is_equivalent = constraint_gen.verify_equivalence(r, a, b)

    if is_equivalent:
        print("✓ Fr_Constraint和FF_Constraint等价")
    else:
        print("✗ Fr_Constraint和FF_Constraint不等价")


def test_specific_cases():
    """测试特定情况"""
    print("\n=== 测试特定情况 ===")

    constraint_gen = FrMulConstraint()

    # 测试情况1: 两个短整数相乘
    print("测试情况1: 两个短整数相乘")
    r = constraint_gen.create_fr_element("r1")
    a = constraint_gen.create_fr_element("a1")
    b = constraint_gen.create_fr_element("b1")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_SHORT)
    solver.add(b.type == constraint_gen.Fr_SHORT)
    solver.add(a.shortVal == 10)
    solver.add(b.shortVal == 20)

    fr_constraint = constraint_gen.generate_fr_constraint(r, a, b)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a, b)

    solver.add(fr_constraint)
    solver.add(ff_constraint)

    # 检查等价性
    r_2 = BitVec('r_2', 256)
    r_2_type = BitVec('r_2type', 32)
    target = And(r.longVal == r_2, r.type == r_2_type)
    solver.add(Not(target))

    result = solver.check()
    if result == unsat:
        print("✓ 等价")
    else:
        print("✗ 不等价")

    # 测试情况2: 长整数非Montgomery * 长整数非Montgomery
    print("\n测试情况2: 长整数非Montgomery * 长整数非Montgomery")
    r = constraint_gen.create_fr_element("r2")
    a = constraint_gen.create_fr_element("a2")
    b = constraint_gen.create_fr_element("b2")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_LONG)
    solver.add(b.type == constraint_gen.Fr_LONG)
    solver.add(a.shortVal == 0)
    solver.add(b.shortVal == 0)
    solver.add(a.longVal == 1000)
    solver.add(b.longVal == 2000)

    fr_constraint = constraint_gen.generate_fr_constraint(r, a, b)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a, b)

    solver.add(fr_constraint)
    solver.add(ff_constraint)

    target = And(r.longVal == r_2, r.type == r_2_type)
    solver.add(Not(target))

    result = solver.check()
    if result == unsat:
        print("✓ 等价")
    else:
        print("✗ 不等价")


if __name__ == "__main__":
    test_fr_mul()
    test_specific_cases() 