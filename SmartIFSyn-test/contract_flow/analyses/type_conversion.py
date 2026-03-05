# type conversion
"""
    unary convert
    1. self_destruct(convert(a))
"""


def unary_convert(node):
    arguments = []

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'TypeConversion':
            if not str(ir.variable).startswith('TMP_'):
                arguments.append(ir.variable)
            arguments.append(ir.lvalue)

    return arguments


"""
    binary convert
    1. convert(a).transfer(convert(b))
"""


def binary_convert(node):
    # left True right False
    convert_type = False
    lvalues = []
    rvalues = []

    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'TypeConversion':
            if not str(ir.variable).startswith('TMP_'):
                convert_type = not convert_type
                lvalues.append(str(ir.variable)) if convert_type else rvalues.append((str(ir.variable)))
            lvalues.append(str(ir.lvalue)) if convert_type else rvalues.append(str(ir.lvalue))
        elif ir_type == 'SolidityCall' and ' balance(address)' in str(ir):
            lvalues.append(str(ir.lvalue)) if convert_type else rvalues.append(str(ir.lvalue))
            if convert_type:
                lvalues[0] = 'balance'
            else:
                rvalues[0] = 'balance'

    return lvalues, rvalues
