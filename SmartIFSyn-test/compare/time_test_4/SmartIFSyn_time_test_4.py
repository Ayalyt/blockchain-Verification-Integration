from contract_flow.analyses import information_flow_analysis
from contract_flow.core.enums.mode_enum import ModeEnum
from contract_flow.core.enums.vulnerablity_enum import VulnerabilityEnum


our_approach_time = 0.0
contract_name = 'ERC223Token'
sol_name = 'contract/check/case134.sol'

analyser = information_flow_analysis.analyse_contract(sol_name, contract_name, VulnerabilityEnum.integrity,
                                                      ModeEnum.compare)
our_approach_time += (analyser.verify_time + analyser.check_vuln_time)
