import yaml
import inquirer
import subprocess
import os
import sys
import time
from contextlib import contextmanager

@contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = fnull, fnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'tools-config.yml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("错误: tools-config.yml 未找到。")
        sys.exit(1)

def get_user_params(tool_config):
    answers = {}
    all_params = tool_config.get('parameters', [])
    
    for param in all_params:
        condition = param.get('condition')
        if condition:
            should_include = True
            for key, values in condition.items():
                if key in answers:
                    answer_value = answers[key]
                    if ' - ' in answer_value:
                        answer_value = answer_value.split(' - ')[0]
                    
                    if answer_value not in values:
                        should_include = False
                        break
                else:
                    should_include = False
                    break
            if not should_include:
                continue
        
        q_type = param.get('type', 'text')
        if q_type == 'text':
            question = inquirer.Text(param['id'], message=param['prompt'])
        elif q_type == 'choice':
            question = inquirer.List(param['id'], message=param['prompt'], choices=param.get('options', []))
        elif q_type == 'boolean':
            question = inquirer.Confirm(param['id'], message=param['prompt'])
        else:
            continue
        
        param_answer = inquirer.prompt([question])
        if param_answer:
            answers.update(param_answer)
    
    return answers if answers else None

def execute_tool_in_container(tool_config, user_params):
    command = ["./chainctl"]
    
    if tool_config['id'] == 'compiler_verification':
        command.append("-V")
        command.append("--test_suite")
        
        test_case = user_params.get('test_case')
        if test_case:
            test_case_mapping = {
                "功能测试": "功能测试",
                "性能测试1": "性能测试1",
                "性能测试2": "性能测试2", 
                "性能测试3": "性能测试3",
                "性能测试4": "性能测试4",
                "性能测试5": "性能测试5"
            }
            if test_case in test_case_mapping:
                command.extend(["--test_case", test_case])
    
    elif tool_config['id'] == 'cipher_verification':
        command.append("-C")
    
    elif tool_config['id'] == 'smartifsyn_test':
        command.append("-S")
        
        test_case = user_params.get('test_case')
        if test_case:
            test_case_mapping = {
                "功能测试1（输出结果日志在SmartIFSyn-test/log）": "功能测试1",
                "功能测试2（输出结果在SmartIFSyn-test/output）": "功能测试2",
                "性能测试1（输出结果在SmartIFSyn-test/compare/time_test_i/inout）": "性能测试1",
                "性能测试2": "性能测试2",
                "性能测试3": "性能测试3",
                "性能测试4": "性能测试4"
            }
            if test_case in test_case_mapping:
                command.extend(["--test_case", test_case_mapping[test_case]])

    elif tool_config['id'] == 'compiler_testing':
        command.append("-T")
        
        mode = user_params.get('mode')
        if mode:
            mode_name = mode.split(' - ')[0]
            command.append(mode_name)
            
            if mode_name == 'single':
                version = user_params.get('version')
                if version:
                    command.append(version)
                cflags = user_params.get('cflags')
                if cflags:
                    command.extend(['--cflags', cflags])
                
            elif mode_name == 'cross':
                version1 = user_params.get('version')
                version2 = user_params.get('version2')
                if version1 and version2:
                    command.append(version1)
                    command.append(version2)
                cflags = user_params.get('cflags')
                if cflags:
                    command.extend(['--cflags', cflags])
                    
            elif mode_name == 'replay':
                case_name = user_params.get('case_name')
                if case_name:
                    command.append(case_name)

    print("\n" + "="*20)
    print("  即将执行的命令  ")
    print("="*20)
    print(' '.join(command))
    print("="*50 + "\n")
    
    try:
        process = subprocess.Popen(command)
        process.wait()
        rc = process.poll()

        if rc == 0:
            print(f"\n[成功] {tool_config['name']} 执行完毕。")
        else:
            print(f"\n[失败] {tool_config['name']} 执行出错，退出码: {rc}")

    except FileNotFoundError:
        print("\n[失败] 'chainctl' 命令未找到。")
    except KeyboardInterrupt:
        print(f"\n[中断] {tool_config['name']} 执行被用户中断")
    except Exception as e:
        print(f"\n[失败] 执行命令时发生未知错误: {e}")

def check_container_status(service_name):
    try:
        result = subprocess.run(
            ["docker-compose", "ps", service_name],
            capture_output=True, text=True
        )
        return result.returncode == 0 and "Up" in result.stdout
    except:
        return False

def main():
    config = load_config()
    tools = config.get('tools', [])

    while True:
        main_menu_choices = [tool['name'] for tool in tools] + ["退出"]
        
        questions = [
            inquirer.List('choice',
                          message="请选择测试对象",
                          choices=main_menu_choices,
                          ),
        ]
        answer = inquirer.prompt(questions)
        if not answer or answer['choice'] == "退出":
            print("感谢使用，再见！")
            break

        selected_tool_name = answer['choice']
        selected_tool_config = next((tool for tool in tools if tool['name'] == selected_tool_name), None)

        if selected_tool_config:
            print(f"\n--- 配置: {selected_tool_config['name']} ---")

            if selected_tool_config['id'] == 'cipher_verification':
                execute_tool_in_container(selected_tool_config, {})
            else:
                user_params = get_user_params(selected_tool_config)
                if user_params:
                    execute_tool_in_container(selected_tool_config, user_params)
        
        # 移除强制等待输入，让程序自动返回主菜单
if __name__ == "__main__":
    project_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(project_dir)
    main()
