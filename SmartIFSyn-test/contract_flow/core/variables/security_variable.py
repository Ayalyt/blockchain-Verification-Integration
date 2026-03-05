# class SecurityVariable

class SecurityVariable:
    def __init__(self, name=None, security_level=None, line_number=None, source=None, reserved=None, annotated=False, defined=False,
                 function=None, rvalues=None, location=None, in_if=False, if_source=None, if_set=False, is_storage=False):
        self.name = name
        self.security_level = security_level
        self.line_number = line_number
        self.source = source
        self.reserved = reserved
        self.annotated = annotated
        self.defined = defined
        self.function = function
        self.rvalues = rvalues
        self.location = location
        self.in_if = in_if
        self.if_source = if_source
        self.if_set = if_set
        self.is_storage = is_storage

    def __eq__(self, other):
        if other is None:
            return False
        return self.line_number == other.line_number and self.name == other.name and self.defined == other.defined

    def __hash__(self):
        return hash((self.line_number, self.name))

    def copy(self):
        return SecurityVariable(self.name, self.security_level, self.line_number, self.source, self.reserved,
                                self.defined)

    def set_name(self, name):
        self.name = name

    def set_security_level(self, security_level):
        self.security_level = security_level

    def set_line_number(self, line_number):
        self.line_number = line_number

    def set_source(self, source):
        self.source = source

    def set_reserved(self, reserved):
        self.reserved = reserved

    def set_annotated(self, annotated):
        self.annotated = annotated

    def set_defined(self, defined):
        self.defined = defined

    def set_function(self, function):
        self.function = function

    def set_rvalues(self, rvalues):
        self.rvalues = rvalues

    def set_location(self, location):
        self.location = location

    def set_in_if(self, in_if):
        self.in_if = in_if

    def set_if_source(self, if_source):
        self.if_source = if_source

    def set_if_set(self, if_set):
        self.if_set = if_set

    def append_if_source(self, if_source):
        if not self.if_source:
            self.if_source = []
        self.if_source.append(if_source)

    def set_is_storage(self, is_storage):
        self.is_storage = is_storage


    def __repr__(self):
        return "{" + f"{self.name}, {self.line_number}, {self.security_level}" + "}"