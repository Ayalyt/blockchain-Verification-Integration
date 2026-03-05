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

our_approach_time = 0.0

# Redirect stdout to os.devnull to suppress console output
with open(os.devnull, 'w') as fnull:
    for i in tqdm(range(len(sol_name_list)), desc="Processing contracts (time1)", unit="contract"):
        sol_name = sol_name_list[i]
        contract_name = contract_name_list[i]

        # Suppress console output by redirecting stdout to null
        sys.stdout = fnull

        # Run the analysis function (no console output will be printed)
        analyser = information_flow_analysis.analyse_contract(sol_name, contract_name, VulnerabilityEnum.integrity,
                                                              ModeEnum.compare)

        # Accumulate the times
        our_approach_time += (analyser.verify_time + analyser.check_vuln_time)

        # Restore stdout after the function call if needed
        sys.stdout = sys.__stdout__

        line_num += 1

# Print the result after all iterations
print(f"SmartIFSyn average time: {our_approach_time / len(sol_name_list)}")
