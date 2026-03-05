# ir check utils


# check whether the function is a high-level call
def check_high_level_call(node):
    is_high_level_call = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'HighLevelCall':
            is_high_level_call = True
            break
    return is_high_level_call


# check whether the expression contains type conversion
def check_type_conversion(node):
    is_type_conversion = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'TypeConversion':
            is_type_conversion = True
            break
    return is_type_conversion


# check transfer
def check_transfer(node):
    is_transfer = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Transfer':
            is_transfer = True
            break
    return is_transfer


# check self_destruct
def check_self_destruct(node):
    if_self_destruct = False
    for ir in node.irs:
        if 'selfdestruct' in str(ir):
            if_self_destruct = True
            break
    return if_self_destruct


# check event
def check_event(node):
    is_event = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'EventCall':
            is_event = True
            break
    return is_event


# check return
def check_return(node):
    is_return = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Return':
            is_return = True
            break
    return is_return


# check send
def check_send(node):
    is_send = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'Send':
            is_send = True
            break
    return is_send


# check require
def check_require(node):
    is_require = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'SolidityCall' and str(ir.expression).startswith('require(bool)'):
            is_require = True
        elif ir_type == 'SolidityCall' and str(ir.expression).startswith('require(bool,string)'):
            is_require = True

    return is_require


# check internal call
def check_internal_call(node):
    is_internal_call = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'InternalCall':
            is_internal_call = True

    return is_internal_call


# check low level call
def check_low_level_call(node):
    is_low_level_call = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'LowLevelCall':
            is_low_level_call = True

    return is_low_level_call

# check revert
def check_revert(node):
    is_revert = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'SolidityCall' and str(ir.expression).startswith('revert()()'):
            is_revert = True
    return is_revert


# check assert
def check_assert(node):
    is_assert = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'SolidityCall' and str(ir.expression).startswith('assert(bool)'):
            is_assert = True
    return is_assert


# check loop
def check_loop(node, line_number, analyser):
    return node.contains_if and line_number in analyser.loop_numbers

# check if
def check_if(node):
    return 'IF ' in str(node)


# check_store
def check_store(node):
    is_store = False
    for ir in node.irs:
        ir_type = ir.__class__.__name__
        if ir_type == 'SolidityCall' and str(ir.expression).startswith('sstore'):
            is_store = True
    return is_store

