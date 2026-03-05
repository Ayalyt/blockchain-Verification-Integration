import time
import subprocess
import uuid
import os
import sys

container_name = f"temp_container_{uuid.uuid4().hex[:8]}"
timeout_seconds = 7200

host_project_path = os.environ.get('HOST_PROJECT_PATH')
host_inout_path = os.path.join(host_project_path, "SmartIFSyn-test", "compare", "time_test_1", "inout")

subprocess.run('sudo pkill -f "docker exec.*python3.*STV_time_test_1"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

docker_command_test = (
    f'sudo docker run --name {container_name} --rm '
    f'-v {host_inout_path}:/inout 1994huxinwen/stc:latest '
    '/bin/bash -c "cd /code/solidity-type-checker && ./run.script 2>&1 | tee /inout/result.exp >/dev/null"'
)

start_time = time.time()
proc = subprocess.Popen(docker_command_test, shell=True)

exit_code = 0

try:
    return_code = proc.wait(timeout=timeout_seconds)
    if return_code != 0:
        exit_code = 1 
except KeyboardInterrupt:
    print("命令被用户中断，正在清理进程...")
    subprocess.run('sudo pkill -f "docker exec.*python3.*STV_time_test_1"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(f"sudo docker rm -f {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.kill()
    proc.wait()
    exit_code = 0
except subprocess.TimeoutExpired:
    print(f"Timeout {timeout_seconds}s, the Docker container is being forcibly stopped...")
    subprocess.run(f"sudo docker rm -f {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.kill()
    proc.wait()
    exit_code = 0 
end_time = time.time()
elapsed_time = end_time - start_time
print(f"STV average time: {elapsed_time}")

sys.exit(exit_code)
# STV average time: 18.00172816872597
