from z3 import *


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


class FrToLongNormalConstraint:
    """Fr_toLongNormal约束生成器"""

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

    def create_fr_element(self, name: str) -> FrElement:
        """创建Fr_Element实例"""
        return FrElement(name)

    def generate_fr_constraint(self, r: FrElement, a: FrElement) -> ExprRef:
        """
        生成Fr_toLongNormal的Fr_Constraint

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element

        Returns:
            Z3约束表达式
        """
        # 获取字典格式
        r_dict = r.get_dict()
        a_dict = a.get_dict()

        # 定义条件变量
        a_l = (a_dict['type'] == self.Fr_LONG)  # a是长整数
        a_s = (a_dict['type'] == self.Fr_SHORT)  # a是短整数
        a_m = (a_dict['type'] == self.Fr_LONGMONTGOMERY)  # a是长整数Montgomery
        a_sm = (a_dict['type'] == self.Fr_SHORTMONTGOMERY)  # a是短整数Montgomery

        # 组合条件
        l1m = And(a_l, a_m)  # 长整数且Montgomery (这个条件实际上不可能，因为类型是互斥的)
        l1n = And(a_l, Not(a_m))  # 长整数且非Montgomery

        # 条件1: 如果a是长整数Montgomery (Fr_LONGMONTGOMERY)
        # r.longVal * R = a.longVal (Montgomery到普通转换)
        result = (r_dict['longVal'] * self.R) % self.p == a_dict['longVal']
        fr_tolongnormal_l1m = And(
            result,
            r_dict['type'] == self.Fr_LONG,  # r.type = Fr_LONG
            r_dict['shortVal'] == 0  # r.shortVal = 0
        )

        # 条件2: 如果a是短整数 (Fr_SHORT)
        # r.longVal = a.shortVal, r.type = Fr_LONG
        fr_toLongNormal_s1 = And(
            r_dict['longVal'] == SignExt(224, a_dict['shortVal']),  # 扩展a.shortVal到256位
            r_dict['type'] == self.Fr_LONG,  # r.type = Fr_LONG
            r_dict['shortVal'] == 0  # r.shortVal = 0
        )

        # 条件3: 如果a是长整数且非Montgomery (Fr_LONG)
        # 直接复制a到r
        fr_copy = And(
            r_dict['longVal'] == a_dict['longVal'],
            r_dict['shortVal'] == a_dict['shortVal'],
            r_dict['type'] == a_dict['type']
        )

        # 条件4: 如果a是短整数Montgomery (Fr_SHORTMONTGOMERY)
        # 需要先转换Montgomery到普通，然后扩展
        fr_shortmontgomery = And(
            r_dict['longVal'] == (a_dict['longVal'] * self.R) % self.p,
            r_dict['type'] == self.Fr_LONG,  # r.type = Fr_LONG
            r_dict['shortVal'] == 0  # r.shortVal = 0
        )

        # 组合所有条件
        return And(
            Implies(a_dict['type'] == self.Fr_LONGMONTGOMERY, fr_tolongnormal_l1m),
            Implies(a_dict['type'] == self.Fr_LONG, fr_copy),
            Implies(a_dict['type'] == self.Fr_SHORT, fr_toLongNormal_s1),
            Implies(a_dict['type'] == self.Fr_SHORTMONTGOMERY, fr_shortmontgomery)
        )

    def generate_ff_constraint(self, r: FrElement, a: FrElement) -> ExprRef:
        """
        生成Fr_toLongNormal的FF_Constraint

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element

        Returns:
            Z3约束表达式
        """
        # 获取字典格式
        r_dict = r.get_dict()
        a_dict = a.get_dict()

        # 计算f_a (根据a的类型)
        f_a = If(a_dict['type'] == self.Fr_SHORT,
                 SignExt(224, a_dict['shortVal']) % self.p,
                 a_dict['longVal'])

        # 创建r_2和r_2_type变量
        r_2 = BitVec('r_2', 256)
        r_2_type = BitVec('r_2type', 32)

        # 条件1: 如果a是长整数Montgomery
        condition1 = a_dict['type'] == self.Fr_LONGMONTGOMERY
        action1 = And(
            r_2 == (f_a * self.R) % self.p,  # Montgomery到普通转换
            r_2_type == self.Fr_LONG
        )

        # 条件2: 如果a是短整数
        condition2 = a_dict['type'] == self.Fr_SHORT
        action2 = And(
            r_2 == f_a,  # f_a已经是扩展后的值
            r_2_type == self.Fr_LONG
        )

        # 条件3: 如果a是长整数且非Montgomery
        condition3 = a_dict['type'] == self.Fr_LONG
        action3 = And(
            r_2 == f_a,  # 直接使用f_a
            r_2_type == self.Fr_LONG
        )

        # 条件4: 如果a是短整数Montgomery
        condition4 = a_dict['type'] == self.Fr_SHORTMONTGOMERY
        action4 = And(
            r_2 == (f_a * self.R) % self.p,  # Montgomery到普通转换
            r_2_type == self.Fr_LONG
        )

        # 组合所有条件
        return If(condition1, action1,
                  If(condition2, action2,
                     If(condition3, action3, action4)))

    def verify_equivalence(self, r: FrElement, a: FrElement) -> bool:
        """
        验证Fr_Constraint和FF_Constraint的等价性

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element

        Returns:
            True如果等价，False否则
        """
        solver = Solver()

        # 添加类型约束
        solver.add(Or(a.type == self.Fr_SHORT,
                      a.type == self.Fr_LONG,
                      a.type == self.Fr_LONGMONTGOMERY,
                      a.type == self.Fr_SHORTMONTGOMERY))

        # 生成约束
        fr_constraint = self.generate_fr_constraint(r, a)
        ff_constraint = self.generate_ff_constraint(r, a)

        # 添加约束
        solver.add(fr_constraint)
        solver.add(ff_constraint)

        # 检查等价性
        target = And(r.longVal == BitVec('r_2', 256),
                     r.type == BitVec('r_2type', 32))
        solver.add(Not(target))

        result = solver.check()
        return result == unsat


def test_fr_to_long_normal():
    """测试Fr_toLongNormal约束生成"""
    print("=== 测试Fr_toLongNormal约束生成 ===")

    # 创建约束生成器
    constraint_gen = FrToLongNormalConstraint()

    # 创建Fr_Element实例
    r = constraint_gen.create_fr_element("r")
    a = constraint_gen.create_fr_element("a")

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
    fr_constraint = constraint_gen.generate_fr_constraint(r, a)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a)

    print("\n生成的约束:")
    print(f"Fr_Constraint: {fr_constraint}")
    print(f"FF_Constraint: {ff_constraint}")

    # 验证等价性
    print("\n验证等价性...")
    is_equivalent = constraint_gen.verify_equivalence(r, a)

    if is_equivalent:
        print("✓ Fr_Constraint和FF_Constraint等价")
    else:
        print("✗ Fr_Constraint和FF_Constraint不等价")


def test_specific_cases():
    """测试特定情况"""
    print("\n=== 测试特定情况 ===")

    constraint_gen = FrToLongNormalConstraint()

    # 测试情况1: 长整数Montgomery
    print("测试情况1: 长整数Montgomery")
    r = constraint_gen.create_fr_element("r1")
    a = constraint_gen.create_fr_element("a1")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_LONGMONTGOMERY)
    solver.add(a.shortVal == 0)
    solver.add(a.longVal == 1000)

    fr_constraint = constraint_gen.generate_fr_constraint(r, a)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a)

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

    # 测试情况2: 短整数
    print("\n测试情况2: 短整数")
    r = constraint_gen.create_fr_element("r2")
    a = constraint_gen.create_fr_element("a2")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_SHORT)
    solver.add(a.shortVal == 100)
    solver.add(a.longVal == 0)

    fr_constraint = constraint_gen.generate_fr_constraint(r, a)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a)

    solver.add(fr_constraint)
    solver.add(ff_constraint)

    target = And(r.longVal == r_2, r.type == r_2_type)
    solver.add(Not(target))

    result = solver.check()
    if result == unsat:
        print("✓ 等价")
    else:
        print("✗ 不等价")

    # 测试情况3: 长整数非Montgomery
    print("\n测试情况3: 长整数非Montgomery")
    r = constraint_gen.create_fr_element("r3")
    a = constraint_gen.create_fr_element("a3")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_LONG)
    solver.add(a.shortVal == 0)
    solver.add(a.longVal == 2000)

    fr_constraint = constraint_gen.generate_fr_constraint(r, a)
    ff_constraint = constraint_gen.generate_ff_constraint(r, a)

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
    test_fr_to_long_normal()
    test_specific_cases() 