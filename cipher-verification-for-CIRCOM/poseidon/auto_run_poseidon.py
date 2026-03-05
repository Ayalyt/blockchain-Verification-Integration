import subprocess
import time
import os
import csv
from datetime import datetime

def run_cvc5_on_files(file_list, output_csv="NIA_results_mimc.csv"):
    """
    批量运行cvc5文件并统计结果和运行时间
    
    Args:
        file_list: 文件列表
        output_csv: 输出CSV文件名
    """
    
    results = []
    
    for file_name in file_list:
        print(f"正在处理: {file_name}")
        
        # 检查文件是否存在
        if not os.path.exists(file_name):
            print(f"  警告: 文件 {file_name} 不存在，跳过")
            continue
            
        start_time = time.time()
        
        try:
            # 运行cvc5命令，设置30分钟超时
            process = subprocess.run(
                ["cvc5", "--stats", file_name],
                capture_output=True,
                text=True,
                timeout=1800  # 5分钟超时
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 解析输出
            stdout = process.stdout
            stderr = process.stderr
            
            # 提取结果 (sat/unsat/unknown)
            result = "unknown"
            if "unsat" in stdout.lower():
                result = "unsat"
            elif "sat" in stdout.lower():
                result = "sat"
                
            # 提取统计信息中的时间
            stats_time = "N/A"
            for line in stderr.split('\n'):
                if "global::totalTime" in line:
                    try:
                        stats_time = line.split('=')[1].strip()
                    except:
                        pass
                    break
            
            # 记录结果
            file_result = {
                "filename": file_name,
                "result": result,
                "execution_time_seconds": round(execution_time, 3),
                "stats_time": stats_time,
                "return_code": process.returncode,
                "status": "completed"
            }
            
            print(f"  结果: {result}, 时间: {execution_time:.3f}s")
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            file_result = {
                "filename": file_name,
                "result": "timeout",
                "execution_time_seconds": round(execution_time, 3),
                "stats_time": "N/A",
                "return_code": -1,
                "status": "timeout"
            }
            print(f"  结果: 超时")
            
        except Exception as e:
            execution_time = time.time() - start_time
            file_result = {
                "filename": file_name,
                "result": "error",
                "execution_time_seconds": round(execution_time, 3),
                "stats_time": "N/A",
                "return_code": -1,
                "status": f"error: {str(e)}"
            }
            print(f"  结果: 错误 - {e}")
        
        results.append(file_result)
    
    # 保存结果到CSV文件
    save_results_to_csv(results, output_csv)
    
    # 打印汇总信息
    print_summary(results)
    
    return results

def save_results_to_csv(results, output_csv):
    """保存结果到CSV文件"""
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'result', 'execution_time_seconds', 'stats_time', 'return_code', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\n结果已保存到: {output_csv}")

def print_summary(results):
    """打印汇总统计信息"""
    print("\n" + "="*50)
    print("汇总统计")
    print("="*50)
    
    total_files = len(results)
    completed_files = len([r for r in results if r['status'] == 'completed'])
    timeout_files = len([r for r in results if r['status'] == 'timeout'])
    error_files = len([r for r in results if r['status'].startswith('error')])
    
    sat_count = len([r for r in results if r['result'] == 'sat'])
    unsat_count = len([r for r in results if r['result'] == 'unsat'])
    unknown_count = len([r for r in results if r['result'] == 'unknown'])
    
    # 计算时间统计（仅限完成的文件）
    completed_times = [r['execution_time_seconds'] for r in results if r['status'] == 'completed']
    if completed_times:
        avg_time = sum(completed_times) / len(completed_times)
        max_time = max(completed_times)
        min_time = min(completed_times)
    else:
        avg_time = max_time = min_time = 0
    
    print(f"总文件数: {total_files}")
    print(f"成功完成: {completed_files}")
    print(f"超时: {timeout_files}")
    print(f"错误: {error_files}")
    print(f"SAT: {sat_count}")
    print(f"UNSAT: {unsat_count}")
    print(f"UNKNOWN: {unknown_count}")
    print(f"平均时间: {avg_time:.3f}s")
    print(f"最短时间: {min_time:.3f}s")
    print(f"最长时间: {max_time:.3f}s")

def main():
    # 文件列表
    files = [
        #"./NIA理论/NIA_mix/poseidon1_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon2_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon3_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon4_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon5_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon6_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon7_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon8_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon9_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon10_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon11_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon12_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon13_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon14_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon15_NIA_mix.smt2",
        #"./NIA理论/NIA_mix/poseidon16_NIA_mix.smt2",
        "./NIA理论/NIA_mix/mimc7_NIA_mix.smt2"
    ]
    
    print("开始批量运行cvc5文件...")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行测试
    results = run_cvc5_on_files(files)
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()