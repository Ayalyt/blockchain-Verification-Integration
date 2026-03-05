# SmartIFSyn 测试说明

##  1. 依赖环境说明

（1）本项目主要的环境依赖可见 [requirements.txt](https://github.com/BlockchainVP/SmartIFSyn-test/blob/main/requirements.txt) ，具体如下：

python=3.9 (实际版本有差别应该也可以), z3-solver==4.13.0.0, tqdm==4.66.4, slither-analyzer==0.10.2, solc-select==1.1.0

你可以使用如下代码进行安装：

```ba
pip install -r requirements.txt
```



（2）测试时由于需要调用其他工具的 docker（例如如下代码）,  所以打包时需要注意安装对比工具的 docker。

```python
docker_command_test = (
    f'sudo docker run --name {container_name} --rm -it '
    '-v /${PWD}/inout:/inout 1994huxinwen/stc:latest '
    '/bin/bash -c "cd solidity-type-checker && ./run.script | tee /inout/result.exp"'
)
```

可以使用如下的指令 pull 镜像：

```bash
docker pull 1994huxinwen/stc:latest
```

如果 pull 失败了，也可以手动使用 stc.tar 进行安装：

```bash
docker load -i ./stc.tar
```

**这个 stc.tar 可以直接找我要，由于其比较大（大约 3 个 G）所以我没有上传到 github 上。到时候这个 stc.tar 可以不用被打包整合进去，但是一定要确保这个 image 安装成功**

(3) 由于本项目会对智能合约进行编译，所以你需要安装 solc-select，并且需要进行如下的指令安装并选择编译器版本：

```bash
solc-select install 0.4.26
solc-select use 0.4.26
```

如果出现：Installing solc '0.4.26'...，Version '0.4.26' installed. 以及 Switched global version to 0.4.26 即为成功。

需要注意的是，solc-select install 大部分情况下需要翻墙才能安装成功，否则可能会卡住或者显示网络问题，可以试试使用 clash 的局域网连接功能确保当前会话能够成功翻墙。

(4) **注意：**

**由于对比工具在性能测试时需要的时间非常久，所以我们设置了超时的处理，此时最好为当前用户配置 sudo 免密操作。**

例如我们使用了如下的指令来运行对比工具：

```python
docker_command_test = (
    f'sudo docker run --name {container_name} --rm -it '
    '-v /${PWD}/inout:/inout 1994huxinwen/stc:latest '
    '/bin/bash -c "cd solidity-type-checker && ./run.script | tee /inout/result.exp"'
)
```

此时如果不进行额外处理，运行 docker 指令时需要提示输入密码，但是在运行超时后，可能会遇到 Python 的进程和 docker 的 TTY 管理冲突 （即虽然超时了，但是目标的 docker 还在运行，这是由于本应该输入密码终止，但是实际存在冲突），所以需要按照如下的操作首先进行配置：

a. 运行：

```bash
sudo visudo
```

b. 在文件末尾添加一行（假设当前用户名为 username）:

```ba
username ALL=(ALL) NOPASSWD: /usr/bin/docker
```

> 注意：有的系统 docker 在 `/usr/bin/docker` 或 `/usr/local/bin/docker`， 你可以运行 `which docker` 来确认。

c. 保存退出

这里的保存一般是 nano 编辑器的退出，具体可以上网搜索一下如何退出。

大致的流程是：用方向键 ↓ 滚动到末尾并且添加了配置之后，按下 ctrl + o （字母o）保存，屏幕显示 File Name to Write: /etc/sudoers ，直接按下 Enter，然后再按 ctrl + x 应该就可以退出。



##   2. 脚本运行代码

测试共包含：功能目标一 （1 个用例），功能目标二（1 个用例）以及性能目标一（4 个用例）

如果你想要快速测试项目安装是否成功的话，可以先试试执行  *功能目标一* 和 *性能目标1-2* 。

1. 功能目标一：（1个用例）

   - 在项目目录下运行以下代码：

   ```bash
   cd compare/funcationality_test_1/
   python functionality_test_1.py
   ```

   - 如果没有报错并且有新的文件夹 ./log 生成在当前路径中（即compare/funcationality_test_1/log/）即为运行成功。

2. 功能目标二：（1个用例）

   - 在项目目录下运行以下代码：

     ```bash	
     cd compare/funcationality_test_2/
     python functionality_test_2.py
     ```

   - 如果没有报错并且有新的文件夹 ./output 生成在当前路径中（即compare/funcationality_test_2/output/）即为运行成功。

3. 性能目标一（4个用例）

   （1）用例 1：

   - 在项目目录下运行以下代码：

     ```bash	
     cd compare/time_test_1/
     # 工具一指令
     python SmartIFSyn_time_test_1.py
     # 工具二指令
     python STV_time_test_1.py 
     ```

   - 如果没有报错并且有对应的输出信息到控制台即为运行成功。

   - **注：工具一指令是我们自己的工具，工具二是对比工具，工具二指令的运行可能耗时很长（超时时间设为 2 小时）。有额外的文件夹生成或者输出属于正常情况。** 

   （2）用例 2：

   - 在项目目录下运行以下代码：

     ```bash	
     cd compare/time_test_2/
     # 工具一指令
     python SmartIFSyn_time_test_2.py
     # 工具二指令
     python STV_time_test_2.py 
     ```

   - 如果没有报错并且有对应的输出信息到控制台即为运行成功。

   - **注：工具一指令是我们自己的工具，工具二是对比工具，工具二指令的运行可能耗时很长（超时时间设为 600秒）。有额外的文件夹生成属于正常情况。**

   （3）用例 3：

   - 在项目目录下运行以下代码：

     ```bash	
     cd compare/time_test_3/
     # 工具一指令
     python SmartIFSyn_time_test_3.py
     # 工具二指令
     python STV_time_test_3.py 
     ```

   - 如果没有报错并且有对应的输出信息到控制台即为运行成功。

   - **注：工具一指令是我们自己的工具，工具二是对比工具，工具二指令的运行可能耗时很长 （超时时间设为 600秒）。有额外的文件夹生成属于正常情况。**

   （4）用例 4：

   - 在项目目录下运行以下代码：

     ```bash	
     cd compare/time_test_4/
     # 工具一指令
     python SmartIFSyn_time_test_4.py
     # 工具二指令
     python STV_time_test_4.py 
     ```

   - 如果没有报错并且有对应的输出信息到控制台即为运行成功。

   - **注：工具一指令是我们自己的工具，工具二是对比工具，工具二指令的运行可能耗时很长 （超时时间设为 600秒）。有额外的文件夹生成属于正常情况。**
