# variables


def get_state_variables_num(target_contract):
    state_variable_num = 0
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    for contract in contracts:
        state_variable_num += len(contract.variables)

    return state_variable_num


def get_parameters_num(target_contract):
    parameters_num = 0
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    for contract in contracts:
        for function in contract.functions:
            parameters_num += len(function.parameters)

    return parameters_num


def get_functions_num(target_contract):
    functions_num = 0
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    for contract in contracts:
        functions_num += len(contract.functions)

    return functions_num


def get_unused_state_variables_num(target_contract):
    unused_num = 0
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    for contract in contracts:
        # state variable
        for variable in contract.variables:
            if not variable.references:
                unused_num += 1

    return unused_num

def get_unused_parameters_num(target_contract):
    unused_num = 0
    contracts = [target_contract]
    contracts.extend(target_contract.inheritance)
    for contract in contracts:
        for function in contract.functions:
            for parameter in function.parameters:
                if not parameter.references:
                    unused_num += 1

    return unused_num