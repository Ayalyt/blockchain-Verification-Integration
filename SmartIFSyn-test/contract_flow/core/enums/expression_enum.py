# enum for expression type

from enum import Enum

"""
- assignment: 
    a = b, a+=b, a=b+c
- push: .push
- event:
    event, selfdestruct
- access:
    a[b]
- identifier_return:
    return a
"""


class ExpressionEnum(Enum):
    none = 'none'
    assignment = 'assignment'
    push = 'push'
    event = 'event'
    transfer = 'transfer'
    access = 'access'
    identifier_return = 'return'
    local_define = 'local_define'
    internal_call = 'internal_call'
    high_level_call = 'high_level_call'
    low_level_call = 'low_level_call'
    assignment_define = 'assignment_define'
    binary_define = 'binary_define'
    unpack_define = 'unpack_define'
    public_call = 'public_call'
    sol_assert = 'assert'
    require = 'require'
    out_of_gas = 'out_of_gas'
    exp_if = 'if'
    loop = 'loop'
