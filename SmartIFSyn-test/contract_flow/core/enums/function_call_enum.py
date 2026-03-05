# enum for function call type

from enum import Enum



class FunctionCallEnum(Enum):
    none = 'none'
    internal = 'internal'
    high_level = 'high_level'
