from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict

# from Model.CPPWitnessCalculator.CPPModeler import CPPModeler
from ...Tools import ExpandedCVC5


class CircuitElement(ABC):

    solver = None

    @staticmethod
    def set_solver(exp_slv: ExpandedCVC5):
        CircuitElement.solver = exp_slv

    def __init__(self):
        pass

    @abstractmethod
    def get_value(self):
        pass


class CPPSignal(CircuitElement):
    def __init__(self, offset: int, is_input: bool, modeler_context):
        super().__init__()
        self.__offset = offset
        self.__name = f's_{offset}'
        self.__FF_exp = CircuitElement.solver.FF_const(self.__name)
        self.__value = None
        self.modeler_context = modeler_context
        if is_input:
            self.__is_assigned = True
            self.__is_constant = False
        else:
            self.__is_assigned = False
            self.__is_constant = False
        # print(f"CPPSignalinit: name-{self.__name}, offset-{self.__offset}, FF_exp-{self.__FF_exp}, value-{self.__value}")

    def get_value(self):
        # print(f"CPPSignalget_value: {self.__name}")
        if not self.__is_assigned:
            print(f"{self.__name} is not assigned, reprentation: {self.__FF_exp}, offset: {self.__offset}")
            print(f"is_constant: {self.__is_constant}")
            raise ValueError('cannot get value from an unsigned signal')
        if self.__is_constant:
            return self.__value
        else:
            return self.__FF_exp

    def assign_value(self, value):
        # print(f"CPPSignalassign_value: {self.__name}, {value}")
        if self.__is_assigned:
            raise PermissionError('may not assign assign twice!')
        self.__is_assigned = True
        if isinstance(value, int):
            self.__is_constant = True
            self.__value = value
            FF_num = self.modeler_context.solver.FF_number(value)
            self.modeler_context.mk_signal_assignment_trem(self, FF_num)
        else:
            self.__is_constant = False
            self.modeler_context.mk_signal_assignment_trem(self, value)

    def toSmt(self):
        return self.__FF_exp

    def is_assigned(self):
        return self.__is_assigned

    def __repr__(self):
        if not self.__is_assigned:
            return 'unassigned'
        if self.__is_constant:
            return str(self.__value)
        else:
            return str(self.__FF_exp)


class CPPConstant(CircuitElement):
    def __init__(self, value: int):
        super().__init__()
        self.__value = value

    def get_value(self):
        return self.__value

    def __repr__(self):
        return str(self.__value)
    

@dataclass
class IODef:
    offset: int
    len: int
    lengths: List[int] = field(default_factory=list)

@dataclass
class IODefPair:
    len: int 
    defs: List[IODef] = field(default_factory=list)