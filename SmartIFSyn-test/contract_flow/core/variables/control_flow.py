# class ControlFlow
from ..enums.expression_enum import ExpressionEnum
from ..enums.security_enum import SecurityEnum


class ControlFlow:
    def __init__(self, security_level=SecurityEnum.L, expression_type=ExpressionEnum.none, security_variables=None):
        self.security_level = security_level
        self.expression_type = expression_type
        self.security_variables = security_variables

    def set_security_level(self, security_level):
        self.security_level = security_level

    def set_expression_type(self, expression_type):
        self.expression_type = expression_type

    def set_security_variables(self, security_variable):
        self.security_variables = security_variable