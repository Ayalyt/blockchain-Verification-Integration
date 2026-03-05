# contract utils

# get target contract
def get_target_contract(slither, contract_name):
    target_contract = None
    for contract in slither.contracts:
        if contract.name == contract_name:
            target_contract = contract
            break
    return target_contract
