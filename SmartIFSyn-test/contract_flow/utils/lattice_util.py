# lattice utils
from ..core.enums.security_enum import SecurityEnum


def lowest_upper_bound(security_variable_list):
    lub = SecurityEnum.L
    for security_variable in security_variable_list:
        if security_variable.security_level == SecurityEnum.H:
            lub = SecurityEnum.H
            break
    return lub


def upper(security_level1, security_level2):
    if security_level1 == SecurityEnum.H and security_level2 == SecurityEnum.L:
        return True
    else:
        return False


def lower(security_level1, security_level2):
    if security_level1 == SecurityEnum.L and security_level2 == SecurityEnum.H:
        return True
    else:
        return False


def equal(security_level1, security_level2):
    if security_level1 == security_level2:
        return True
    else:
        return False
