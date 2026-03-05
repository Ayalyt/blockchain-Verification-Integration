# class IRVariable

class IRVariable:
    def __init__(self, security_variable, is_security_variable, left_variable=None, right_variable=None):
        self.security_variable = security_variable
        self.is_security_variable = is_security_variable
        self.left_variable = left_variable
        self.right_variable = right_variable

    def set_security_variable(self, security_variable):
        self.is_security_variable = security_variable

    def set_is_security_variable(self, is_security_variable):
        self.is_security_variable = is_security_variable

    def set_left_variable(self, left_variable):
        self.left_variable = left_variable

    def set_right_variable(self, right_variable):
        self.right_variable = right_variable


    def __repr__(self):
        return "{" + f"{self.is_security_variable}, {self.security_variable}" + "}"