import os
import subprocess
import sys
from pathlib import Path
import time

class CryptoLibraryValidator:
    def __init__(self):
        self.project_structure = {
            "mimc": {
                "description": "MiMC 哈希函数验证（所有文件中都已经将ref_model和tgt_model集成，并添加等价性判别语句）",
                "execution_command": "cvc5 --stats",  
                "files": {
                    "mimc7.smt2": "MiMC7 SMT2 验证文件", 
                    "mimc7_err.smt2": "MiMC7 错误案例 SMT 文件（更改了C10常数）"
                },
                 "benchmark_files": {
                    "mimc7_NIA_mix.smt2": "MiMC7 benchmark 文件",
                },
                "other_files": {
                    "mimc.circom": "MiMC CIRCOM实现文件",
                    "generate_mimc_FF.py": "MiMC ref_model 生成脚本",
                },
            },
            "poseidon": {
                "description": "Poseidon 哈希函数验证（所有文件中都已经将ref_model和tgt_model集成，并添加等价性判别语句）",
                "execution_command": "cvc5 --stats",  
                "files": {
                    "poseidon1.smt2": "Poseidon 输入变量数=1 SMT2 文件",
                    "poseidon2.smt2": "Poseidon 输入变量数=2 SMT2 文件",
                    "poseidon3.smt2": "Poseidon 输入变量数=3 SMT2 文件",
                    "poseidon4.smt2": "Poseidon 输入变量数=4 SMT2 文件",
                    "poseidon5.smt2": "Poseidon 输入变量数=5 SMT2 文件",
                    "poseidon6.smt2": "Poseidon 输入变量数=6 SMT2 文件",
                    "poseidon7.smt2": "Poseidon 输入变量数=7 SMT2 文件",
                    "poseidon8.smt2": "Poseidon 输入变量数=8 SMT2 文件",
                    "poseidon9.smt2": "Poseidon 输入变量数=9 SMT2 文件",
                    "poseidon10.smt2": "Poseidon 输入变量数=10 SMT2 文件",
                    "poseidon11.smt2": "Poseidon 输入变量数=11 SMT2 文件",
                    "poseidon12.smt2": "Poseidon 输入变量数=12 SMT2 文件",
                    "poseidon13.smt2": "Poseidon 输入变量数=13 SMT2 文件",
                    "poseidon14.smt2": "Poseidon 输入变量数=14 SMT2 文件",
                    "poseidon15.smt2": "Poseidon 输入变量数=15 SMT2 文件",
                    "poseidon16.smt2": "Poseidon 输入变量数=16 SMT2 文件",
                    "poseidon1_err.smt2": "Poseidon 输入变量数=1 错误案例(更改了C32常数)",
                    "poseidon6_err.smt2": "Poseidon 输入变量数=6 错误案例(3476行处mul改称add)",
                    "poseidon11_err.smt2": "Poseidon 输入变量数=11 错误案例(两个模型的输入数据不同)",
                    "poseidon16_err.smt2": "Poseidon 输入变量数=16 错误案例(17810initialState0->1)",
                },
                 "benchmark_files": {
                    "poseidon1_NIA_mix.smt2": "Poseidon 输入变量数=1 benchmark 文件",
                    "poseidon2_NIA_mix.smt2": "Poseidon 输入变量数=2 benchmark 文件",
                    "poseidon3_NIA_mix.smt2": "Poseidon 输入变量数=3 benchmark 文件",
                    "poseidon4_NIA_mix.smt2": "Poseidon 输入变量数=4 benchmark 文件",
                    "poseidon5_NIA_mix.smt2": "Poseidon 输入变量数=5 benchmark 文件",
                    "poseidon6_NIA_mix.smt2": "Poseidon 输入变量数=6 benchmark 文件",
                    "poseidon7_NIA_mix.smt2": "Poseidon 输入变量数=7 benchmark 文件",
                    "poseidon8_NIA_mix.smt2": "Poseidon 输入变量数=8 benchmark 文件",
                    "poseidon9_NIA_mix.smt2": "Poseidon 输入变量数= 9 benchmark 文件", 
                    "poseidon10_NIA_mix.smt2": "Poseidon 输入变量数=10 benchmark 文件",
                    "poseidon11_NIA_mix.smt2": "Poseidon 输入变量数=11 benchmark 文件",
                    "poseidon12_NIA_mix.smt2": "Poseidon 输入变量数=12 benchmark 文件",
                    "poseidon13_NIA_mix.smt2": "Poseidon 输入变量数=13 benchmark 文件",
                    "poseidon14_NIA_mix.smt2": "Poseidon 输入变量数=14 benchmark 文件",
                    "poseidon15_NIA_mix.smt2": "Poseidon 输入变量数=15 benchmark 文件",
                    "poseidon16_NIA_mix.smt2": "Poseidon 输入变量数=16 benchmark 文件",
                },
                "other_files": {
                    "poseidon.circom": "poseidon CIRCOM实现文件",
                    "generate_poseidon_all.py": "poseidon ref_model 生成脚本",
                },
            },
            "SHA-256": {
                "description": "SHA-256 哈希函数验证",
                "execution_command": "cv_cec -v -rename_local -ov a0,a1,a2,a3,a4,a5,a6,a7",  
                "execution_command2": "cv -v",  
                "files": {
                    "sha-256_ref.cl": "SHA-256 参考实现",
                    "sha-256_ref_err.cl": "SHA-256 参考实现错误案例",
                    "sha-256_tgt.cl": "SHA-256 目标实现",
                },
                 "benchmark_files": {
                    "combine_for_comparison_using_cv.cl": "SHA-256 benchmark 文件",
                },
                "other_files": {
                    "sha256compression_function.circom": "sha-256 CIRCOM实现文件",
                    "sha-256_ref.cl": "SHA-256 参考实现",
                },
            },
            # 新增BabyJub主模块（包含3个子模块）
            "babyjub": {
                "description": "BabyJub 椭圆曲线验证（包含点加法、点双倍、曲线点验证三大核心组件）",
                "execution_command": "cvc5 --stats",
                # 子模块配置（对应三个文件夹）
                "submodules": {
                    "babyadd": {
                        "description": "BabyJub 点加法验证（验证两个曲线点相加的等价性）",
                        "files": {
                            "babyadd_equivalence.smt2": "BabyAdd 等价性验证文件（QF_FF理论）",
                            "babyadd_err.smt2": "BabyAdd 错误案例（修改加法公式）",
                        },
                        "benchmark_files": {
                    "babyadd_equivalence_nia.smt2": "BabyAdd 等价性验证文件（QF_NIA理论）",
                },   
                        "other_files": {
                            "babyadd.circom": "BabyAdd CIRCOM实现文件",
                            "generate_babyadd_FF.py": "BabyAdd 参考模型生成脚本（QF_FF）",
                        }
                    },
                    "babydbl": {
                        "description": "BabyJub 点双倍验证（验证曲线点自加的等价性，即2P=P+P）",
                        "files": {
                            "babydbl_equivalence.smt2": "BabyDbl 等价性验证文件（QF_FF理论）",
                            "babydbl_err.smt2": "BabyDbl 错误案例（修改双倍公式）",

                        },
                        "benchmark_files": {
                    "babydbl_equivalence_nia.smt2": "BabyDbl 等价性验证文件",
                },   
                        "other_files": {
                            "babydbl.circom": "BabyDbl CIRCOM实现文件",
                            "generate_babydbl_FF.py": "BabyDbl 参考模型生成脚本（QF_FF）",
                        }
                    },
                    "babycheck": {
                        "description": "BabyJub 曲线点验证（验证点(x,y)是否满足BabyJub曲线方程）",
                        "files": {
                            "babycheck_equivalence.smt2": "BabyCheck 等价性验证文件（QF_FF理论）",
                            "babycheck_err.smt2": "BabyCheck 错误案例（修改曲线参数）",
                            
                        },
                        "benchmark_files": {
                    "babycheck_equivalence_nia.smt2": "BabyCheck 等价性验证文件（QF_NIA理论）",
                },   
                        "other_files": {
                            "babycheck.circom": "BabyCheck CIRCOM实现文件",
                            "generate_babycheck_FF.py": "BabyCheck 参考模型生成脚本（QF_FF）",
                        }
                    }
                }
            }
        }
    
    def display_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("       密码学算法库正确性验证系统")
        print("="*60)
        print("项目概述：")
        print("本部分旨在验证四种密码学核心组件的功能正确性：")
        print("1. MiMC 哈希函数")
        print("2. Poseidon 哈希函数") 
        print("3. SHA-256 哈希函数")
        print("4. BabyJub 椭圆曲线（含BabyAdd/BabyDbl/BabyCheck）")
        print("验证方法：")
        print("采用等价性验证，通过验证同一算法的两种不同实现之间的计算等价性来验证其算法实现正确性")
        print("模型来源：")
        print("target model为待验证模型，从circomlib中相应实现自动转化得来；reference model为参考模型，其中SHA-256的参考模型从其算法伪代码手动建模得到，Poseidon、MiMC、BabyJub系列的参考模型参考其Go实现或数学定义手动建模得到。")
        print("等价性验证工具：")
        print("对于MiMC、Poseidon、BabyJub系列，使用CVC5；对于SHA-256，使用Cryptoline.")
        print("\n请选择要查看的算法模块：")
        print("1. MiMC 验证模块")
        print("2. Poseidon 验证模块") 
        print("3. SHA-256 验证模块")
        print("4. BabyJub 验证模块")
        print("5. 性能测试模块")
        print("6. 显示项目完整结构")
        print("7. 退出程序")
        print("="*60)
    
    def display_module_details(self, module_name):
        """显示指定模块的详细信息（支持子模块）"""
        if module_name not in self.project_structure:
            print(f"错误：模块 {module_name} 不存在")
            return
        
        module = self.project_structure[module_name]
        print(f"\n{'='*60}")
        print(f"        {module_name} 验证模块")
        print(f"{'='*60}")
        print(f"描述：{module['description']}")
        
        if module_name == "babyjub" and "submodules" in module:
            print(f"\n子模块列表：")
            submodules = list(module['submodules'].items())
            for i, (submod_name, submod_info) in enumerate(submodules, 1):
                print(f"  {i}. {submod_name}")
                print(f"     └── 描述：{submod_info['description']}")
            
            print(f"\n操作选项：")
            print(f"  1. 进入子模块（执行验证/查看文件）")
            print(f"  2. 返回主菜单")
            
            choice = input(f"\n请选择操作 (1-2): ").strip()
            if choice == "1":
                self.select_babyjub_submodule(submodules)
            elif choice == "2":
                return
            else:
                print("无效选择，返回主菜单")
            return
        
        # 非BabyJub模块
        print(f"\n文件列表：")
        files_list = list(module['files'].items())
        for i, (filename, description) in enumerate(files_list, 1):
            print(f"  {i}. {filename}")
            print(f"     └── {description}")
        
        print(f"\n操作选项：")
        print(f"  1. 执行验证文件")
        print(f"  2. 返回主菜单")
        
        choice = input(f"\n请选择操作 (1-2): ").strip()
        if choice == "1":
            self.execute_verification_file(module_name, files_list, submod_name=None)
        elif choice == "2":
            return
        else:
            print("无效选择，返回主菜单")
    
    def select_babyjub_submodule(self, submodules):
        """选择BabyJub的子模块（babyadd/babydbl/babycheck）"""
        print(f"\n选择要操作的BabyJub子模块：")
        for i, (submod_name, submod_info) in enumerate(submodules, 1):
            print(f"  {i}. {submod_name} - {submod_info['description']}")
        
        try:
            choice = int(input(f"\n请输入子模块编号 (1-{len(submodules)}): ").strip())
            if choice < 1 or choice > len(submodules):
                print("无效选择")
                return
            
            submod_name, submod_info = submodules[choice-1]
            self.display_babyjub_submodule_details(submod_name, submod_info)
            
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"执行过程中发生错误: {e}")
    
    def display_babyjub_submodule_details(self, submod_name, submod_info):
        """显示BabyJub子模块的详细信息（文件列表+操作）"""
        print(f"\n{'='*60}")
        print(f"    BabyJub - {submod_name} 子模块")
        print(f"{'='*60}")
        print(f"描述：{submod_info['description']}")
        
        # 显示子模块的验证文件
        print(f"\n验证文件列表：")
        files_list = list(submod_info['files'].items())
        for i, (filename, description) in enumerate(files_list, 1):
            print(f"  {i}. {filename}")
            print(f"     └── {description}")
        
        print(f"\n操作选项：")
        print(f"  1. 执行验证文件")
        print(f"  2. 查看子模块其他文件")
        print(f"  3. 返回BabyJub主模块")
        
        choice = input(f"\n请选择操作 (1-3): ").strip()
        if choice == "1":
            self.execute_verification_file("babyjub", files_list, submod_name=submod_name)
        elif choice == "2":
            self.display_submodule_other_files(submod_name, submod_info)
        elif choice == "3":
            return
        else:
            print("无效选择，返回BabyJub主模块")
    
    def display_submodule_other_files(self, submod_name, submod_info):
        """显示子模块的其他文件（非验证文件）"""
        print(f"\n{'='*60}")
        print(f"    {submod_name} 子模块 - 其他文件")
        print(f"{'='*60}")
        
        # 显示benchmark文件
        if "benchmark_files" in submod_info and submod_info["benchmark_files"]:
            print(f"\n📊 Benchmark文件：")
            for filename, description in submod_info["benchmark_files"].items():
                print(f"  - {filename}：{description}")
        
        # 显示其他辅助文件
        if "other_files" in submod_info and submod_info["other_files"]:
            print(f"\n📁 辅助文件：")
            for filename, description in submod_info["other_files"].items():
                print(f"  - {filename}：{description}")
        
        input("\n按回车键返回子模块菜单...")
        self.display_babyjub_submodule_details(submod_name, submod_info)
    
    def execute_verification_file(self, module_name, files_list, submod_name=None):
        """执行验证文件（支持子模块路径）"""
        # 构建文件路径（子模块需拼接路径：babyjub/子模块名/文件名）
        base_path = Path(module_name)
        if submod_name:
            base_path = base_path / submod_name
        
        print(f"\n选择要执行的{('['+submod_name+']' if submod_name else module_name)}验证文件:")
        for i, (filename, description) in enumerate(files_list, 1):
            print(f"  {i}. {filename}")
        
        try:
            choice = int(input(f"\n请输入文件编号 (1-{len(files_list)}): ").strip())
            if choice < 1 or choice > len(files_list):
                print("无效选择")
                return
            
            selected_file = files_list[choice-1][0]
            self.run_verification_command(module_name, selected_file, submod_name=submod_name)
            
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"执行过程中发生错误: {e}")
    
    def run_verification_command(self, module_name, filename, submod_name=None):
        """运行验证命令（支持子模块路径）"""
        module = self.project_structure[module_name]
        # 构建完整文件路径
        if submod_name:
            file_path = Path(module_name) / submod_name / filename
            # 子模块的执行命令继承主模块
            execution_command = module['execution_command']
        else:
            file_path = Path(module_name) / filename
            execution_command = module['execution_command']
        
        if not file_path.exists():
            print(f"错误：文件 {file_path} 不存在")
            input("按回车键继续...")
            return
        
        if module_name in ["mimc", "poseidon", "babyjub"]:
            command = f"{execution_command} {file_path}"
        elif module_name == "SHA-256":
            # SHA-256原有逻辑（无需修改）
            print(f"\nSHA-256验证需要选择两个文件进行比较")
            print(f"已选择第一个文件: {filename}")
            sha_files = list(module['files'].keys())
            print(f"\n请选择第二个文件:")
            for i, file in enumerate(sha_files, 1):
                print(f"  {i}. {file}")
            
            try:
                choice = int(input(f"\n请输入第二个文件编号 (1-{len(sha_files)}): ").strip())
                if choice < 1 or choice > len(sha_files):
                    print("无效选择")
                    input("按回车键继续...")
                    return
                
                second_file = sha_files[choice-1]
                second_path = Path(module_name) / second_file
                if not second_path.exists():
                    print(f"错误：文件 {second_path} 不存在")
                    input("按回车键继续...")
                    return
                    
                command = f"{module['execution_command']} {file_path} {second_path}"
                print(f"将比较文件: {filename} 和 {second_file}")
                
            except ValueError:
                print("请输入有效的数字")
                input("按回车键继续...")
                return
        else:
            print(f"未知的模块: {module_name}")
            input("按回车键继续...")
            return
        
        print(f"\n准备执行验证命令:")
        print(f"  命令: {command}")
        confirm = input("确认执行? (y/n): ").strip().lower()
        
        if confirm == 'y':
            try:
                print(f"\n开始执行验证...")
                print("-" * 50)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                print("执行结果:")
                print("-" * 50)
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                
                print("-" * 50)
                if result.returncode == 0:
                    print("✓ 验证执行完成")
                else:
                    print(f"✗ 验证执行失败，返回码: {result.returncode}")
                
                input("\n按回车键继续...")
                    
            except Exception as e:
                print(f"执行过程中发生错误: {e}")
                input("按回车键继续...")
        else:
            print("取消执行")
            input("按回车键继续...")
    
    def display_performance_tests(self):
        """显示性能测试模块（支持BabyJub子模块）"""
        print("\n" + "="*60)
        print("           性能测试模块")
        print("="*60)
        print("性能测试包含两部分：")
        print("1. 代码行数统计 - 统计两个脚本的代码行，检查是否满足手动建模脚本<=12*CIRCOM代码行数")
        print("2. 基准测试 - 运行对应的benchmark文件，设置超时时间")
        print("\n请选择测试类型：")
        print("1. 代码行数统计")
        print("2. 基准测试")
        print("3. 返回主菜单")
        
        choice = input(f"\n请选择操作 (1-3): ").strip()
        if choice == "1":
            self.code_line_count_test()
        elif choice == "2":
            self.benchmark_test()
        elif choice == "3":
            return
        else:
            print("无效选择")
    
    def code_line_count_test(self):
        """代码行数统计测试（支持BabyJub子模块文件）"""
        print("\n" + "="*60)
        print("           代码行数统计测试")
        print("="*60)
        print("此测试将统计两个脚本的代码行数，并检查是否满足：脚本1代码行 <= 12 * 脚本2代码行")
        
        # 收集所有模块（含BabyJub子模块）的脚本文件
        all_scripts = []
        for module_name, module_info in self.project_structure.items():
            # 处理普通模块
            if "other_files" in module_info:
                for filename in module_info["other_files"]:
                    if filename.endswith(('.py', '.circom', '.cl')):
                        file_path = Path(module_name) / filename
                        all_scripts.append((f"{module_name}/{filename}", file_path, "验证代价对比文件"))
            # 处理BabyJub子模块
            if module_name == "babyjub" and "submodules" in module_info:
                for submod_name, submod_info in module_info["submodules"].items():
                    if "other_files" in submod_info:
                        for filename in submod_info["other_files"]:
                            if filename.endswith(('.py', '.circom', '.cl')):
                                file_path = Path(module_name) / submod_name / filename
                                all_scripts.append((f"{module_name}/{submod_name}/{filename}", file_path,"验证代价对比文件"))
                    
        if not all_scripts:
            print("未找到任何脚本文件")
            input("按回车键继续...")
            return
        
        # 显示所有可用脚本
        print("\n可用的脚本文件:")
        for i, (display_name, file_path, file_type) in enumerate(all_scripts, 1):
            print(f"  {i}. {display_name} ({file_type})")
        
        try:
            # 选择两个脚本进行比较
            choice1 = int(input(f"\n请选择第一个脚本 (1-{len(all_scripts)}): ").strip())
            choice2 = int(input(f"请选择第二个脚本 (1-{len(all_scripts)}): ").strip())
            if choice1 < 1 or choice1 > len(all_scripts) or choice2 < 1 or choice2 > len(all_scripts):
                print("无效选择")
                input("按回车键继续...")
                return
            
            display1, path1, type1 = all_scripts[choice1-1]
            display2, path2, type2 = all_scripts[choice2-1]
            
            if not path1.exists() or not path2.exists():
                print("错误：选择的文件不存在")
                input("按回车键继续...")
                return
            
            lines1 = self.count_code_lines(path1)
            lines2 = self.count_code_lines(path2)
            
            # 显示结果
            print(f"\n代码行数统计结果:")
            print(f"  脚本1: {display1} - {lines1} 行")
            print(f"  脚本2: {display2} - {lines2} 行")
            print(f"  条件检查: {lines1} <= 12 * {lines2} = {12 * lines2}")
            
            if lines1 <= 12 * lines2:
                print(f"  ✓ 满足条件: {lines1} <= {12 * lines2}")
            else:
                print(f"  ✗ 不满足条件: {lines1} > {12 * lines2}")
            
            input("\n按回车键继续...")
            
        except ValueError:
            print("请输入有效的数字")
            input("按回车键继续...")
        except Exception as e:
            print(f"执行过程中发生错误: {e}")
            input("按回车键继续...")
    
    def count_code_lines(self, file_path):
        """统计代码文件的行数（过滤空行和注释行）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                code_lines = 0
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('//') and not stripped.startswith('#') and not stripped.startswith('(*'):
                        code_lines += 1
                return code_lines
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            return 0
    
    def benchmark_test(self):
        """基准测试（支持BabyJub子模块）"""
        print("\n" + "="*60)
        print("           基准测试")
        print("="*60)
        print("此测试将运行各模块的benchmark文件，设置超时时间")
        
        # 收集所有支持benchmark的模块（含BabyJub子模块）
        benchmark_modules = []
        for module_name in self.project_structure.keys():
            if module_name == "babyjub":
                # BabyJub的benchmark在子模块中
                for submod_name, submod_info in self.project_structure[module_name]["submodules"].items():
                    if "benchmark_files" in submod_info and submod_info["benchmark_files"]:
                        benchmark_modules.append(("babyjub", submod_name, submod_info))
            else:
                # 普通模块
                module_info = self.project_structure[module_name]
                if "benchmark_files" in module_info and module_info["benchmark_files"]:
                    benchmark_modules.append((module_name, None, module_info))
        
        print("\n支持基准测试的模块:")
        for i, (mod_name, submod_name, _) in enumerate(benchmark_modules, 1):
            display_name = f"{mod_name}（{submod_name}）" if submod_name else mod_name
            print(f"  {i}. {display_name}")
        
        try:
            choice = int(input(f"\n请选择模块 (1-{len(benchmark_modules)}): ").strip())
            if choice < 1 or choice > len(benchmark_modules):
                print("无效选择")
                input("按回车键继续...")
                return
            
            mod_name, submod_name, mod_info = benchmark_modules[choice-1]
            self.run_benchmark(mod_name, submod_name, mod_info)
            
        except ValueError:
            print("请输入有效的数字")
            input("按回车键继续...")
        except Exception as e:
            print(f"执行过程中发生错误: {e}")
            input("按回车键继续...")
    
    def run_benchmark(self, module_name, submod_name, mod_info):
        """运行benchmark测试（支持BabyJub子模块）"""
        # 构建文件路径和命令
        if submod_name:
            # BabyJub子模块的benchmark
            benchmark_files = list(mod_info["benchmark_files"].items())
            display_name = f"BabyJub-{submod_name}"
            base_path = Path(module_name) / submod_name
            execution_command = self.project_structure[module_name]["execution_command"]
            timeout = 45 * 60  # BabyJub子模块计算复杂，45分钟超时
        else:
            # 普通模块的benchmark
            benchmark_files = list(mod_info["benchmark_files"].items())
            display_name = module_name
            base_path = Path(module_name)
            execution_command = mod_info["execution_command"] if module_name in ["mimc", "poseidon"] else mod_info["execution_command2"]
            timeout = 30 * 60 if module_name in ["mimc", "poseidon"] else 12 * 60 * 60
        
        print(f"\n{display_name} 模块的benchmark文件:")
        for i, (filename, description) in enumerate(benchmark_files, 1):
            print(f"  {i}. {filename} - {description}")
        
        try:
            file_choice = int(input(f"\n请选择benchmark文件 (1-{len(benchmark_files)}): ").strip())
            if file_choice < 1 or file_choice > len(benchmark_files):
                print("无效选择")
                input("按回车键继续...")
                return
            
            selected_file, _ = benchmark_files[file_choice-1]
            file_path = base_path / selected_file
            
            if not file_path.exists():
                print(f"错误：文件 {file_path} 不存在")
                input("按回车键继续...")
                return
            
            # 执行benchmark命令
            command = f"{execution_command} {file_path}"
            print(f"\n准备执行benchmark测试:")
            print(f"  命令: {command}")
            print(f"  超时时间: {timeout//60}分钟")
            confirm = input("确认执行? (y/n): ").strip().lower()
            
            if confirm == 'y':
                try:
                    print(f"\n开始执行{display_name} benchmark测试...")
                    print("-" * 50)
                    start_time = time.time()
                    
                    result = subprocess.run(
                        command, 
                        shell=True, 
                        capture_output=True, 
                        text=True,
                        timeout=timeout
                    )
                    
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    
                    print("执行结果:")
                    print("-" * 50)
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(result.stderr)
                    
                    print("-" * 50)
                    print(f"运行时间: {elapsed_time:.2f} 秒")
                    if result.returncode == 0:
                        print("✓ benchmark测试执行完成")
                    else:
                        print(f"✗ benchmark测试执行失败，返回码: {result.returncode}")
                    
                    input("\n按回车键继续...")
                        
                except subprocess.TimeoutExpired:
                    print(f"✗ benchmark测试超时（{timeout//60}分钟）")
                    input("\n按回车键继续...")
                except Exception as e:
                    print(f"执行过程中发生错误: {e}")
                    input("按回车键继续...")
            else:
                print("取消执行")
                input("按回车键继续...")
        
        except ValueError:
            print("请输入有效的数字")
            input("按回车键继续...")
    
    def display_full_structure(self):
        """显示完整的项目结构（含BabyJub子模块）"""
        print("\n" + "="*60)
        print("           项目完整结构")
        print("="*60)
        
        for module_name, module_info in self.project_structure.items():
            print(f"\n📁 {module_name}/")
            print(f"   └── 描述: {module_info['description']}")
            
            # 处理BabyJub子模块
            if module_name == "babyjub" and "submodules" in module_info:
                for submod_name, submod_info in module_info["submodules"].items():
                    print(f"\n   📂 {submod_name}/")
                    print(f"      └── 描述: {submod_info['description']}")
                    
                    # 子模块验证文件
                    print(f"      验证文件:")
                    sub_files = list(submod_info['files'].items())
                    for filename, _ in sub_files[:3]:
                        print(f"        ├── {filename}")
                    if len(sub_files) > 3:
                        print(f"        └── ... 共 {len(sub_files)} 个文件")
                    
                    # 子模块benchmark文件
                    if "benchmark_files" in submod_info and submod_info["benchmark_files"]:
                        print(f"      Benchmark文件:")
                        for filename in submod_info["benchmark_files"]:
                            print(f"        ├── {filename}")
                    
                    # 子模块其他文件
                    if "other_files" in submod_info and submod_info["other_files"]:
                        print(f"      辅助文件:")
                        for filename in submod_info["other_files"]:
                            print(f"        ├── {filename}")
            else:
                # 普通模块文件结构
                print(f"   验证文件:")
                files = list(module_info['files'].items())
                for filename, _ in files[:3]:
                    print(f"     ├── {filename}")
                if len(files) > 3:
                    print(f"     └── ... 共 {len(files)} 个文件")
                
                if "benchmark_files" in module_info and module_info["benchmark_files"]:
                    print(f"   Benchmark文件:")
                    for filename in module_info["benchmark_files"]:
                        print(f"     ├── {filename}")
                
                if "other_files" in module_info and module_info["other_files"]:
                    print(f"   辅助文件:")
                    for filename in module_info["other_files"]:
                        print(f"     ├── {filename}")
    
    def main(self):
        """主程序循环"""
        while True:
            self.display_main_menu()
            choice = input("\n请输入选择 (1-7): ").strip()
            
            if choice == "1":
                self.display_module_details("mimc")
            elif choice == "2":
                self.display_module_details("poseidon")
            elif choice == "3":
                self.display_module_details("SHA-256")
            elif choice == "4":
                self.display_module_details("babyjub")
            elif choice == "5":
                self.display_performance_tests()
            elif choice == "6":
                self.display_full_structure()
                input("\n按回车键继续...")
            elif choice == "7":
                print("感谢使用密码学算法验证系统！")
                break
            else:
                print("无效选择，请重新输入")

def main():
    """程序入口点"""
    validator = CryptoLibraryValidator()
    
    # 检查项目目录结构（含BabyJub子模块）
    missing_paths = []
    for module_name in validator.project_structure:
        module_path = Path(module_name)
        if not module_path.exists():
            missing_paths.append(str(module_path))
        # 检查BabyJub子模块目录
        if module_name == "babyjub" and "submodules" in validator.project_structure[module_name]:
            for submod_name in validator.project_structure[module_name]["submodules"]:
                submod_path = module_path / submod_name
                if not submod_path.exists():
                    missing_paths.append(str(submod_path))
    
    if missing_paths:
        print("警告: 以下目录不存在:")
        for path in missing_paths:
            print(f"  - {path}")
        print("请确保程序在正确的项目根目录下运行，且目录结构完整")
        response = input("是否继续? (y/n): ").strip().lower()
        if response != 'y':
            return
    
    validator.main()

if __name__ == "__main__":
    main()