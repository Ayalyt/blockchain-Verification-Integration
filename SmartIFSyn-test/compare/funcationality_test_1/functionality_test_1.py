import sys
import os
from tqdm import tqdm

from contract_flow.analyses import information_flow_analysis
from contract_flow.core.enums.mode_enum import ModeEnum
from contract_flow.core.enums.vulnerablity_enum import VulnerabilityEnum


# Custom class to handle file output only
class FileOutput:
    def __init__(self, file):
        self.file = file  # Save the file where we will write the output

    def write(self, message):
        # Only write to the file, not to the console
        self.file.write(message)

    def flush(self):
        # Flush the stream (required for proper buffering)
        self.file.flush()


# load file
with open('compare/sol_name', 'r') as file:
    sol_name_list = [line.rstrip() for line in file.readlines()]
with open('compare/contract_name', 'r') as file:
    contract_name_list = [line.rstrip() for line in file.readlines()]

sol_name_list = [path.replace('../../', '') for path in sol_name_list]

line_num = 0

confidentiality_list = [32, 33, 34, 113, 114]

# Ensure log directory exists
log_dir = './log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Wrap the range with tqdm to display progress
for i in tqdm(range(len(sol_name_list)), desc="Processing contracts (function1)", unit="contract"):
    sol_name = sol_name_list[i]
    contract_name = contract_name_list[i]
    vuln_mode = VulnerabilityEnum.integrity if i + 1 not in confidentiality_list else VulnerabilityEnum.confidentiality

    # Generate file name based on sol_name
    base_name = os.path.basename(sol_name).split('.')[0]  # "case1" from "case1.sol"
    log_file_name = os.path.join(log_dir, f"{base_name}.txt")

    # Open log file in append mode
    with open(log_file_name, 'a') as log_file:
        # Create FileOutput object to handle file outputs only
        file_output = FileOutput(log_file)

        # Redirect stdout to FileOutput
        sys.stdout = file_output

        # Run the analysis function
        analyser = information_flow_analysis.analyse_contract(sol_name, contract_name, vuln_mode, ModeEnum.normal, ModeEnum.function1)

        # Optionally, restore stdout after the function call if you want
        sys.stdout = sys.__stdout__

    line_num += 1
