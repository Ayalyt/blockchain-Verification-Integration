import argparse
from contract_flow.analyses import information_flow_analysis
from contract_flow.core.enums.mode_enum import ModeEnum
from contract_flow.core.enums.vulnerablity_enum import VulnerabilityEnum


# python script.py solidity_path contract_name
def main():
    parser = argparse.ArgumentParser(description='Process command line arguments')
    parser.add_argument('file', type=str, help='Solidity file to process')
    parser.add_argument('contract', type=str, help='Contract name')
    parser.add_argument('-m', '--vuln_mode', type=str, help='Vulnerable mode')
    parser.add_argument('-d', '--dev_mode', type=str, help='Development mode')

    args = parser.parse_args()
    sol_name = args.file
    contract_name = args.contract
    vuln_mode = args.vuln_mode
    dev_mode = args.dev_mode

    if vuln_mode is None or vuln_mode == 'c':
        vuln_mode = VulnerabilityEnum.confidentiality
    elif vuln_mode == 'i':
        vuln_mode = VulnerabilityEnum.integrity
    else:
        raise TypeError("Error vulnerable mode")

    if dev_mode is None or dev_mode == 'n':
        dev_mode = ModeEnum.normal
    elif dev_mode == 'c':
        dev_mode = ModeEnum.compare
    else:
        raise TypeError("Error development mode")

    information_flow_analysis.analyse_contract(sol_name, contract_name, vuln_mode, dev_mode)


if __name__ == '__main__':
    main()
