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


class FrCopyConstraint:
    """Fr_copy约束生成器"""

    def __init__(self):
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
        生成Fr_copy的Fr_Constraint

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element a

        Returns:
            Z3约束表达式
        """
        r_dict = r.get_dict()
        a_dict = a.get_dict()

        # 复制所有属性
        copy_short = (r_dict['shortVal'] == a_dict['shortVal'])
        copy_long = (r_dict['longVal'] == a_dict['longVal'])
        copy_type = (r_dict['type'] == a_dict['type'])

        return And(copy_short, copy_long, copy_type)

    def generate_ff_constraint(self, r: FrElement, a: FrElement) -> ExprRef:
        """
        生成Fr_copy的FF_Constraint

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element a

        Returns:
            Z3约束表达式
        """
        r_dict = r.get_dict()
        a_dict = a.get_dict()

        # 创建r_2和r_2_type变量
        r_2 = BitVec('r_2', 256)
        r_2_type = BitVec('r_2type', 32)

        # 简单的复制操作
        return And(
            r_2 == a_dict['longVal'],  # 复制longVal
            r_2_type == a_dict['type']  # 复制type
        )

    def verify_equivalence(self, r: FrElement, a: FrElement) -> bool:
        """
        验证Fr_Constraint和FF_Constraint的等价性

        Args:
            r: 输出Fr_Element
            a: 输入Fr_Element a

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


def test_fr_copy():
    """测试Fr_copy约束生成"""
    print("=== 测试Fr_copy约束生成 ===")

    # 创建约束生成器
    constraint_gen = FrCopyConstraint()

    # 创建Fr_Element实例
    r = constraint_gen.create_fr_element("r")
    a = constraint_gen.create_fr_element("a")

    print("Fr_Element结构:")
    print(f"  shortVal: {r.shortVal}")
    print(f"  longVal: {r.longVal}")
    print(f"  type: {r.type}")

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

    constraint_gen = FrCopyConstraint()

    # 测试情况1: 复制短整数
    print("测试情况1: 复制短整数")
    r = constraint_gen.create_fr_element("r1")
    a = constraint_gen.create_fr_element("a1")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_SHORT)
    solver.add(a.shortVal == 100)
    solver.add(a.longVal == 0)

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

    # 测试情况2: 复制长整数Montgomery
    print("\n测试情况2: 复制长整数Montgomery")
    r = constraint_gen.create_fr_element("r2")
    a = constraint_gen.create_fr_element("a2")

    solver = Solver()
    solver.add(a.type == constraint_gen.Fr_LONGMONTGOMERY)
    solver.add(a.shortVal == 0)
    solver.add(a.longVal == 1000)

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

    # 测试情况3: 复制长整数非Montgomery
    print("\n测试情况3: 复制长整数非Montgomery")
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


def test_copy_verification():
    """测试复制验证"""
    print("\n=== 测试复制验证 ===")

    constraint_gen = FrCopyConstraint()

    # 创建测试元素
    r = constraint_gen.create_fr_element("r")
    a = constraint_gen.create_fr_element("a")

    solver = Solver()

    # 设置输入值
    solver.add(a.type == constraint_gen.Fr_LONG)
    solver.add(a.shortVal == 0)
    solver.add(a.longVal == 12345)

    # 生成复制约束
    copy_constraint = constraint_gen.generate_fr_constraint(r, a)
    solver.add(copy_constraint)

    # 检查复制结果
    solver.add(r.shortVal == 0)
    solver.add(r.type == constraint_gen.Fr_LONG)
    solver.add(r.longVal == 12345)

    result = solver.check()
    if result == sat:
        print("✓ 复制约束正确")
        model = solver.model()
        print(f"  输入a: type={model[a.type]}, shortVal={model[a.shortVal]}, longVal={model[a.longVal]}")
        print(f"  输出r: type={model[r.type]}, shortVal={model[r.shortVal]}, longVal={model[r.longVal]}")
    else:
        print("✗ 复制约束错误")


if __name__ == "__main__":
    test_fr_copy()
    test_specific_cases()
    test_copy_verification()