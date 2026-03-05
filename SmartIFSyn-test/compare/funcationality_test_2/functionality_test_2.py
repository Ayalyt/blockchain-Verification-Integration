import sys
import os
from tqdm import tqdm

from contract_flow.analyses import information_flow_analysis
from contract_flow.core.enums.mode_enum import ModeEnum
from contract_flow.core.enums.vulnerablity_enum import VulnerabilityEnum


# load file
with open('compare/sol_name', 'r') as file:
    sol_name_list = [line.rstrip() for line in file.readlines()]
with open('compare/contract_name', 'r') as file:
    contract_name_list = [line.rstrip() for line in file.readlines()]

# Fix paths for Docker environment
sol_name_list = [path.replace('../../', '') for path in sol_name_list]

line_num = 0

confidentiality_list = [32, 33, 34, 113, 114]

# Redirect stdout to os.devnull to suppress console output
with open(os.devnull, 'w') as fnull:
    for i in tqdm(range(len(sol_name_list)), desc="Processing contracts (function2)", unit="contract"):
        sol_name = sol_name_list[i]
        contract_name = contract_name_list[i]
        vuln_mode = VulnerabilityEnum.integrity if i + 1 not in confidentiality_list else VulnerabilityEnum.confidentiality

        # Redirect stdout to null (suppress console output)
        sys.stdout = fnull

        # Run the analysis function (no console output will be printed)
        analyser = information_flow_analysis.analyse_contract(sol_name, contract_name, vuln_mode, ModeEnum.normal)

        # Optionally, restore stdout if you need to output something later
        sys.stdout = sys.__stdout__

        line_num += 1
