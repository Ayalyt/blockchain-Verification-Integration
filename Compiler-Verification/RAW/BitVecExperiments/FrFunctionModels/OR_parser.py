from z3 import *
import sys
import os

# 添加当前目录到路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入各种约束生成器
from fr_add_constraint import FrAddConstraint
from fr_sub_constraint import FrSubConstraint
from fr_mul_constraint import FrMulConstraint
from fr_copy_constraint import FrCopyConstraint
from elements import FrElement

class ORCircuitConstraintParser:
    """复杂电路约束解析器"""

    def __init__(self):
        # 创建各种约束生成器
        self.add_gen = FrAddConstraint()
        self.sub_gen = FrSubConstraint()
        self.mul_gen = FrMulConstraint()
        self.copy_gen = FrCopyConstraint()

        # 存储所有约束
        self.constraints = []

        # 存储变量映射
        self.variables = {}
        self.expaux = {}

    def create_fr_element(self, name: str, index: int = None) -> FrElement:
        """创建Fr_Element实例"""
        return FrElement(name, index)

    def get_or_create_signal(self, signal_name: str) -> FrElement:
        """获取或创建信号变量"""
        if signal_name not in self.variables:
            self.variables[signal_name] = self.create_fr_element(signal_name)
        return self.variables[signal_name]

    def get_or_create_expaux(self, index: int) -> FrElement:
        """获取或创建expaux中间变量"""
        if index not in self.expaux:
            self.expaux[index] = self.create_fr_element("expaux", index)
        return self.expaux[index]

    def parse_cpp_circuit(self):
        """
        解析C++电路代码：
        Fr_add(&expaux[1],&signalValues[mySignalStart + 1],&signalValues[mySignalStart + 2])
        Fr_mul(&expaux[2],&signalValues[mySignalStart + 1],&signalValues[mySignalStart + 2])
        Fr_sub(&expaux[0],&expaux[1],&expaux[2])
        Fr_copy(aux_dest,&expaux[0]);

        其中：
        - &signalValues[mySignalStart + 1] 解析为 a
        - &signalValues[mySignalStart + 2] 解析为 b
        - aux_dest 解析为 out
        """
        print("=== 解析复杂C++电路代码生成约束 ===")

        # 创建信号变量
        a = self.get_or_create_signal("a")  # signalValues[mySignalStart + 1]
        b = self.get_or_create_signal("b")  # signalValues[mySignalStart + 2]
        out = self.get_or_create_signal("out")  # aux_dest

        # 第1步: Fr_add(&expaux[1], a, b)
        expaux1 = self.get_or_create_expaux(1)
        constraint1 = self.add_gen.generate_fr_constraint(expaux1, a, b)
        self.constraints.append(("Fr_add", "expaux[1] = a + b", constraint1))

        # 第2步: Fr_mul(&expaux[2], a, b)
        expaux2 = self.get_or_create_expaux(2)
        constraint2 = self.mul_gen.generate_fr_constraint(expaux2, a, b)
        self.constraints.append(("Fr_mul", "expaux[2] = a * b", constraint2))

        # 第3步: Fr_sub(&expaux[0], expaux[1], expaux[2])
        expaux0 = self.get_or_create_expaux(0)
        constraint3 = self.sub_gen.generate_fr_constraint(expaux0, expaux1, expaux2)
        self.constraints.append(("Fr_sub", "expaux[0] = expaux[1] - expaux[2]", constraint3))

        # 第4步: Fr_copy(out, expaux[0])
        constraint4 = self.copy_gen.generate_fr_constraint(out, expaux0)
        self.constraints.append(("Fr_copy", "out = expaux[0]", constraint4))

        return self.constraints

    def get_all_constraints(self):
        """获取所有约束的组合"""
        if not self.constraints:
            self.parse_cpp_circuit()

        all_constraints = []

        # 添加电路约束
        for op_type, description, constraint in self.constraints:
            all_constraints.append(constraint)

        return And(all_constraints)

    def print_constraints(self):
        """打印所有约束"""
        if not self.constraints:
            self.parse_cpp_circuit()

        print("\n=== 生成的Fr_Constraints ===")
        for i, (op_type, description, constraint) in enumerate(self.constraints, 1):
            print(f"\n{i}. {op_type}: {description}")
            print(f"   约束: {constraint}")

        print(f"\n=== 组合约束 ===")
        all_constraints = self.get_all_constraints()
        print(f"总约束: {all_constraints}")

        print(f"\n=== 电路逻辑 ===")
        print(f"实现逻辑: out = (a + b) - (a * b)")
        print(f"即: out = a + b - ab")
        print(f"数学表达式: out = a + b - ab = a(1-b) + b")

        print(f"\n=== 变量映射 ===")
        print(f"输入变量: a, b")
        print(f"输出变量: out")
        print(f"中间变量: expaux[0], expaux[1], expaux[2]")

        print(f"\n=== 计算步骤 ===")
        print(f"1. expaux[1] = a + b     (加法)")
        print(f"2. expaux[2] = a * b     (乘法)")
        print(f"3. expaux[0] = expaux[1] - expaux[2] = (a+b) - (a*b)")
        print(f"4. out = expaux[0]       (复制)")


def main():
    """主函数：解析电路并输出约束"""
    parser = ORCircuitConstraintParser()

    # 解析C++电路代码并生成约束
    constraints = parser.parse_cpp_circuit()

    # 打印所有约束
    parser.print_constraints()

    print(f"\n=== 总结 ===")
    print(f"共生成 {len(constraints)} 个Fr_Constraint")
    print(f"电路功能: 实现 (a + b) - (a * b) 运算")
    print(f"应用场景: 可能用于布尔逻辑或条件运算的有限域实现")


if __name__ == "__main__":
    main()