from z3 import *
import sys
import os

# 添加当前目录到路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入约束生成器
from fr_add_constraint import FrAddConstraint
from fr_sub_constraint import FrSubConstraint
from fr_mul_constraint import FrMulConstraint
from fr_copy_constraint import FrCopyConstraint
from elements import FrElement


class NORCircuitConstraintParser:
    """高级电路约束解析器 - 处理多步复杂运算"""

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
        self.constants = {}

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

    def get_or_create_constant(self, index: int, value: int) -> FrElement:
        """获取或创建常数"""
        if index not in self.constants:
            const_elem = self.create_fr_element("circuitConstants", index)
            self.constants[index] = (const_elem, value)
        return self.constants[index][0]

    def get_constant_constraints(self):
        """获取常数约束"""
        constraints = []

        # circuitConstants[0] = 1 (short且非蒙哥马利的常数)
        const1 = self.get_or_create_constant(0, 1)
        const1_constraints = And(
            const1.shortVal == 1,
            const1.longVal == 1,
            const1.type == 0  # 类型0表示short且非蒙哥马利
        )
        constraints.append(("Constant", "circuitConstants[0] = 1", const1_constraints))

        return constraints

    def parse_cpp_circuit(self):
        """
        解析C++电路代码：
        {
        PFrElement aux_dest = &signalValues[mySignalStart + 0];
        // load src
        Fr_mul(&expaux[3],&signalValues[mySignalStart + 1],&signalValues[mySignalStart + 2]); // line circom 255
        Fr_add(&expaux[2],&expaux[3],&circuitConstants[0]); // line circom 255
        Fr_sub(&expaux[1],&expaux[2],&signalValues[mySignalStart + 1]); // line circom 255
        Fr_sub(&expaux[0],&expaux[1],&signalValues[mySignalStart + 2]); // line circom 255
        // end load src
        Fr_copy(aux_dest,&expaux[0]);
        }

        其中：
        - &signalValues[mySignalStart + 1] 解析为 a
        - &signalValues[mySignalStart + 2] 解析为 b
        - aux_dest = &signalValues[mySignalStart + 0] 解析为 out
        - &circuitConstants[0] 是常数1
        """
        print("=== 解析高级C++电路代码生成约束 ===")

        # 创建信号变量
        a = self.get_or_create_signal("a")  # signalValues[mySignalStart + 1]
        b = self.get_or_create_signal("b")  # signalValues[mySignalStart + 2]
        out = self.get_or_create_signal("out")  # aux_dest = signalValues[mySignalStart + 0]

        # 获取常数
        const1 = self.get_or_create_constant(0, 1)  # circuitConstants[0] = 1

        # 添加常数约束
        const_constraints = self.get_constant_constraints()
        self.constraints.extend(const_constraints)

        # 第1步: Fr_mul(&expaux[3], a, b)
        expaux3 = self.get_or_create_expaux(3)
        constraint1 = self.mul_gen.generate_fr_constraint(expaux3, a, b)
        self.constraints.append(("Fr_mul", "expaux[3] = a * b", constraint1))

        # 第2步: Fr_add(&expaux[2], expaux[3], circuitConstants[0])
        expaux2 = self.get_or_create_expaux(2)
        constraint2 = self.add_gen.generate_fr_constraint(expaux2, expaux3, const1)
        self.constraints.append(("Fr_add", "expaux[2] = expaux[3] + 1", constraint2))

        # 第3步: Fr_sub(&expaux[1], expaux[2], a)
        expaux1 = self.get_or_create_expaux(1)
        constraint3 = self.sub_gen.generate_fr_constraint(expaux1, expaux2, a)
        self.constraints.append(("Fr_sub", "expaux[1] = expaux[2] - a", constraint3))

        # 第4步: Fr_sub(&expaux[0], expaux[1], b)
        expaux0 = self.get_or_create_expaux(0)
        constraint4 = self.sub_gen.generate_fr_constraint(expaux0, expaux1, b)
        self.constraints.append(("Fr_sub", "expaux[0] = expaux[1] - b", constraint4))

        # 第5步: Fr_copy(out, expaux[0])
        constraint5 = self.copy_gen.generate_fr_constraint(out, expaux0)
        self.constraints.append(("Fr_copy", "out = expaux[0]", constraint5))

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
            if op_type == "Constant":
                print(f"   约束: {constraint}")
            else:
                print(f"   约束: [复杂约束，已省略详细输出]")

        print(f"\n=== 组合约束 ===")
        all_constraints = self.get_all_constraints()
        print(f"总约束: [包含{len(self.constraints)}个子约束的复合约束]")

        print(f"\n=== 计算步骤详解 ===")
        print(f"0. circuitConstants[0] = 1           (常数定义)")
        print(f"1. expaux[3] = a * b                 (乘法运算)")
        print(f"2. expaux[2] = expaux[3] + 1 = ab + 1 (加法运算)")
        print(f"3. expaux[1] = expaux[2] - a = ab + 1 - a (第一次减法)")
        print(f"4. expaux[0] = expaux[1] - b = ab + 1 - a - b (第二次减法)")
        print(f"5. out = expaux[0]                   (复制运算)")


def main():
    """主函数：解析电路并输出约束"""
    parser = NORCircuitConstraintParser()

    # 解析C++电路代码并生成约束
    constraints = parser.parse_cpp_circuit()

    # 打印所有约束
    parser.print_constraints()


if __name__ == "__main__":
    main()