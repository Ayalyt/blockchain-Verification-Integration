from ...Tools.Check import TypeCheck
from ...Tools.Errors import MyNumError


def reverse_pairs(s):
    TypeCheck(str, s)
    s = s.replace(' ', '')
    if len(s) % 2 != 0:
        MyNumError("The length of the input string must be even")

    reversed_str = ''
    for i in range(len(s), 0, -2):
        reversed_str += s[i-2] + s[i-1]

    return int(reversed_str, 16)
