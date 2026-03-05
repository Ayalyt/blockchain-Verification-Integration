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


class FrToMontgomeryConstraint:
    """Fr_toMontgomery约束生成器"""

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
        生成Fr_toMontgomery的Fr_Constraint

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

        # 条件1: 如果a的类型已经是蒙哥马利类型
        condition1 = Or(a_dict['type'] == self.Fr_LONGMONTGOMERY,
                        a_dict['type'] == self.Fr_SHORTMONTGOMERY)
        action1 = And(r_dict['shortVal'] == a_dict['shortVal'],
                      r_dict['longVal'] == a_dict['longVal'],
                      r_dict['type'] == a_dict['type'])

        # 条件2: 如果a的类型是长整数
        condition2 = a_dict['type'] == self.Fr_LONG
        action2 = And(r_dict['shortVal'] == a_dict['shortVal'],
                      r_dict['longVal'] == (a_dict['longVal'] * self.R) % self.p,
                      r_dict['type'] == self.Fr_LONGMONTGOMERY)

        # 条件3: 如果a的短整数值是负数
        condition3 = a_dict['shortVal'] < 0
        neg_a = -SignExt(480, a_dict['shortVal'])
        result = Extract(255, 0, (neg_a * ZeroExt(256, self.R)) % ZeroExt(256, self.p))
        neg_longVal = If(result == 0, 0, self.p - result)
        action3 = And(r_dict['longVal'] == neg_longVal,
                      r_dict['type'] == self.Fr_SHORTMONTGOMERY)

        # 条件4: 其他情况 (a的短整数值是正数)
        action4 = And(r_dict['longVal'] == Extract(255, 0,
                                                   (ZeroExt(480, a_dict['shortVal']) * ZeroExt(256, self.R)) % ZeroExt(
                                                       256, self.p)),
                      r_dict['type'] == self.Fr_SHORTMONTGOMERY)

        # 组合所有条件
        return If(condition1, action1,
                  If(condition2, action2,
                     If(condition3, action3, action4)))

    def generate_ff_constraint(self, r: FrElement, a: FrElement) -> ExprRef:
        """
        生成Fr_toMontgomery的FF_Constraint

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

        # 条件1: 如果a的类型已经是蒙哥马利类型
        condition1 = Or(a_dict['type'] == self.Fr_LONGMONTGOMERY,
                        a_dict['type'] == self.Fr_SHORTMONTGOMERY)
        action1_2 = And(r_2 == f_a, r_2_type == a_dict['type'])

        # 条件2: 如果a的类型是长整数
        condition2 = a_dict['type'] == self.Fr_LONG
        action2_2 = And(r_2 == f_a * self.R % self.p,
                        r_2_type == self.Fr_LONGMONTGOMERY)

        # 条件3: 如果a的短整数值是负数
        condition3 = a_dict['shortVal'] < 0
        action3_2 = And(r_2 == Extract(255, 0,
                                       ZeroExt(256, f_a) * ZeroExt(256, self.R) % ZeroExt(256, self.p)),
                        r_2_type == self.Fr_SHORTMONTGOMERY)

        # 条件4: 其他情况 (a的短整数值是正数)
        action4_2 = And(r_2 == Extract(255, 0,
                                       ZeroExt(256, f_a) * ZeroExt(256, self.R) % ZeroExt(256, self.p)),
                        r_2_type == self.Fr_SHORTMONTGOMERY)

        # 组合所有条件
        return If(condition1, action1_2,
                  If(condition2, action2_2,
                     If(condition3, action3_2, action4_2)))

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


def test_fr_to_montgomery():
    """测试Fr_toMontgomery约束生成"""
    print("=== 测试Fr_toMontgomery约束生成 ===")

    # 创建约束生成器
    constraint_gen = FrToMontgomeryConstraint()

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


if __name__ == "__main__":
    test_fr_to_montgomery()