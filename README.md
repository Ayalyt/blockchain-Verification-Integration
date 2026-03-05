`chainctl` 是本项目的核心命令行工具，用于统一管理所有验证服务。

### 基本语法

```bash
./chainctl [选项] [参数]
```

### 主要功能

#### 1. 密码算法验证

执行密码学算法的验证测试。

```bash
./chainctl -C
# 或
./chainctl --cipher
```

#### 2. Circom编译器验证

验证Circom零知识证明电路的正确性。

**基本用法：**
```bash
./chainctl -V
```

**指定电路文件和编译产物：**
```bash
./chainctl -V circuit.circom artifacts/
```

**高级选项：**
```bash
./chainctl -V circuit.circom artifacts/ -v 2.2.0 --NC --NR
```

**选项说明：**
- `-v, --version`: 指定Circom版本
- `--NC`: 禁用计算等价性检查
- `--NR`: 禁用约束等价性检查

**运行测试套件：**
```bash
./chainctl -V --test_suite
./chainctl -V --test_suite --test_case "功能测试1"
```

#### 3. 智能合约信息流分析

分析Solidity智能合约的安全漏洞。

**基本用法：**
```bash
./chainctl -S file.sol ContractName
```

**高级选项：**
```bash
./chainctl -S file.sol ContractName -m c -d n
```

**选项说明：**
- `-m, --vuln_mode`: 漏洞模式
  - `c`: 机密性检查
  - `i`: 完整性检查
- `-d, --dev_mode`: 开发模式
  - `n`: 正常模式
  - `c`: 比较模式

**运行测试用例：**
```bash
./chainctl -S --test_case "功能测试1"
./chainctl -S --test_case "性能测试1"
```

可用测试用例：
- 功能测试1, 功能测试2
- 性能测试1, 性能测试2, 性能测试3, 性能测试4

#### 4. 通用服务

直接指定服务名称执行任意命令。

```bash
./chainctl --service compiler-verification --command "python3 -m RAW.Verifier.main circuit.circom artifacts/"
./chainctl --service smartifsyn-test --command "python3 script.py file.sol ContractName"
```

**执行模式选项：**
- `--mode run`: 一次性运行
- `--mode exec`: 交互执行（用于-C）

### 使用示例

1. **快速验证密码算法：**
   ```bash
   ./chainctl -C
   ```

2. **验证Circom电路：**
   ```bash
   ./chainctl -V my_circuit.circom ./artifacts/
   ```

3. **分析智能合约安全：**
   ```bash
   ./chainctl -S MyContract.sol MyContract -m c
   ```

4. **运行性能测试：**
   ```bash
   ./chainctl -S --test_case "性能测试1"
   ```

5. **使用通用模式执行自定义命令：**
   ```bash
   ./chainctl --service compiler-verification --command "python3 -m RAW.Verifier.main" --mode exec
   ```

### 服务架构

项目使用Docker Compose管理以下服务：

- **orchestrator**: 编排器服务，协调其他服务
- **compiler-verification**: Circom编译器验证服务
- **cipher-verification**: 密码算法验证服务  
- **smartifsyn-test**: 智能合约信息流分析服务

### 注意事项

1. 所有服务都运行在Docker容器中，确保系统已安装Docker和Docker Compose
2. 首次运行时会自动构建相关容器镜像
3. 项目配置了代理设置以支持网络访问
4. 智能合约分析需要相应的Solidity编译器环境

### 帮助信息

查看完整的帮助信息：
```bash
./chainctl --help
```

## 项目结构

```
.
├── chainctl                    # 主命令行工具
├── docker-compose.yml          # Docker编排配置
├── start.sh                    # 启动脚本
├── stop.sh                     # 停止脚本
├── tools-config.yml            # 工具配置
├── cipher-verification-for-CIRCOM/    # 密码算法验证
├── Compiler-Verification/             # 编译器验证
├── orchestrator/                      # 编排器
└── SmartIFSyn-test/                   # 智能合约分析
```