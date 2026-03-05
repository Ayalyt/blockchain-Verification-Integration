from z3 import *

class FrElement:
    """Fr_Element数据结构，表示有限域元素"""

    def __init__(self, name_prefix: str, index: int = None):
        if index is not None:
            name = f'{name_prefix}_{index}'
        else:
            name = name_prefix
        # 创建位向量变量
        self.shortVal = BitVec(f'{name}_shortVal', 32)
        self.longVal = BitVec(f'{name}_longVal', 256)
        self.type = BitVec(f'{name}_type', 32)
        self.name = name

    def get_dict(self):
        """返回字典格式，便于访问"""
        return {
            'shortVal': self.shortVal,
            'longVal': self.longVal,
            'type': self.type
        }