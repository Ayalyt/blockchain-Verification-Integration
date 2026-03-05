import sys
import time
import argparse
import os

from .Model.Main.CircuitManager import CircuitManager
from .Model.Setting import ModelingSettings
from .Tools.ExpandedCVC5 import ExpandedCVC5
from .Model.CircomSourceCode.Signal import Signal
from .Tools.ColorPrint import colorPrint, COLOR

def run_case(main_path, artifacts_path, prime_name='bn128', polish='O0'):
    print(main_path)
    print(artifacts_path)
    exp_slv = ExpandedCVC5(prime_name)

    modeling_time_data = list()
    circuitManager = CircuitManager(main_path, exp_slv, artifacts_path)
    circuitManager.set_polish_level(polish)

    # version = ModelingSettings.CIRCOM_VERSION
    # if not circuitManager.compile_case(version, polish, prime_name):
    #     colorPrint("Circuit compilation failed. Exiting.", COLOR.RED)
    #     sys.exit(1)

    circuitManager.pick_information(modeling_time_data)

    start_time = time.time()  # 记录开始时间

    colorPrint(f'-- CHECKING COMPILER CORRECTNESS --', COLOR.YELLOW)
    print(f'total signal num : {Signal.total_num}')

    signal_tag_equality = circuitManager.check_signal_tag_equality()
    colorPrint(f'Signal Classification Consistency : {signal_tag_equality}')

    end_time = time.time()  # 记录结束时间
    TE_time = end_time - start_time
    print(f'Signal Classification Consistency Checking Time: {TE_time:.4f} s')
    print()


    start_time = time.time()  # 记录开始时间
    if ModelingSettings.CHECK_CONSTRAINT:
        constraint_equality = circuitManager.check_constraint_equality()
    else:
        constraint_equality = 'SKIPPED'
    colorPrint(f'Constraint Equivalence : {constraint_equality}')

    end_time = time.time()  # 记录结束时间
    RE_time = end_time - start_time

    print(f'Constraint Equivalence Checking Time: {RE_time:.4f} s')
    print()

    # constraint_equality = True
    # RE_time = 'OOT'

    start_time = time.time()  # 记录开始时间

    if ModelingSettings.CHECK_CALCULATION:
        calculate_equality = circuitManager.check_calculate_equality()
    else:
        calculate_equality = 'SKIPPED'
    colorPrint(f'Calculation Equivalence : {calculate_equality}')
    end_time = time.time()  # 记录结束时间
    CE_time = end_time - start_time

    print(f'Calculation Equivalence Checking Time: {CE_time:.4f} s')

    data = circuitManager.get_main_info()

    print()
    print()

    circuitManager.print_table_output()


def readArgs():
    parser = argparse.ArgumentParser(description="Run verification for Circom programs.")
    parser.add_argument("circom_file_path", help="Path to the file containing the main component declaration")
    parser.add_argument("artifacts_path", help="Path to the folder of the compiled artifacts")
    parser.add_argument("-v", "--version", default="2.1.8", help="Specify Circom version (default: 2.1.8)")
    parser.add_argument("--NC", action="store_true", help="Disable calculation equivalence checking")
    parser.add_argument("--NR", action="store_true", help="Disable constraint equivalence checking")

    return parser.parse_args()


import os

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(base_dir, '../../benchmarks/tests/isZero.circom')
    artifacts_path = os.path.join(base_dir, 'temp_file/isZero')
    version = '2.1.8'
    ModelingSettings.CHECK_CONSTRAINT = True
    ModelingSettings.CHECK_CALCULATION = True

    if len(sys.argv) > 1:
        args = readArgs()
        main_path = args.circom_file_path
        artifacts_path = args.artifacts_path
        version = args.version
        ModelingSettings.CHECK_CONSTRAINT = not args.NR
        ModelingSettings.CHECK_CALCULATION = not args.NC

    ModelingSettings.CIRCOM_VERSION = version
    run_case(main_path=main_path, artifacts_path=artifacts_path)
