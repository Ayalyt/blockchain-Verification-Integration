#!/bin/bash

# compiler-testing 环境配置脚本
# 版本: 1.0.0
# 最后更新: 2025年12月4日

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if command -v $1 &> /dev/null; then
        log_info "$1 已安装"
        return 0
    else
        log_warning "$1 未安装"
        return 1
    fi
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "正在以root用户运行，某些操作可能需要调整"
        return 0
    else
        log_info "以普通用户运行"
        return 1
    fi
}

# 显示标题
show_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  compiler-testing 环境配置脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 显示系统信息
show_system_info() {
    log_info "系统信息:"
    echo "操作系统: $(lsb_release -d 2>/dev/null | cut -f2 || uname -o)"
    echo "内核版本: $(uname -r)"
    echo "架构: $(uname -m)"
    echo "内存: $(free -h | awk '/^Mem:/ {print $2}')"
    echo "磁盘空间:"
    df -h . | tail -1
    echo ""
}

# 确认继续
confirm_continue() {
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "用户取消操作"
        exit 0
    fi
}

# 步骤1: 系统依赖安装
install_system_deps() {
    log_info "步骤1: 安装系统依赖"
    
    # 更新包管理器
    log_info "更新包管理器..."
    sudo apt-get update
    
    # 安装基础工具
    log_info "安装基础工具..."
    sudo apt-get install -y \
        curl \
        wget \
        git \
        ca-certificates \
        build-essential \
        pkg-config \
        cmake \
        ninja-build \
        nasm \
        libssl-dev \
        libgmp-dev \
        python3 \
        python3-pip \
        python3-venv
    
    # 清理缓存
    log_info "清理缓存..."
    sudo rm -rf /var/lib/apt/lists/*
    
    log_success "系统依赖安装完成"
}

# 步骤2: Node.js 和 pnpm 安装
install_nodejs_pnpm() {
    log_info "步骤2: 安装 Node.js 和 pnpm"
    
    # 检查是否已安装Node.js
    if check_command "node"; then
        log_info "Node.js 已安装，版本: $(node --version)"
    else
        log_info "安装 Node.js 20.x..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        log_success "Node.js 安装完成，版本: $(node --version)"
    fi
    
    # 检查是否已安装pnpm
    if check_command "pnpm"; then
        log_info "pnpm 已安装，版本: $(pnpm --version)"
    else
        log_info "安装 pnpm..."
        sudo npm install -g pnpm
        log_success "pnpm 安装完成，版本: $(pnpm --version)"
    fi
}

# 步骤3: Rust 工具链安装
install_rust_toolchain() {
    log_info "步骤3: 安装 Rust 工具链"
    
    # 检查是否已安装Rust
    if check_command "rustc"; then
        log_info "Rust 已安装，版本: $(rustc --version)"
        log_info "Cargo 版本: $(cargo --version)"
    else
        log_info "安装 Rust (nightly-2025-05-30)..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly-2025-05-30
        
        # 添加Rust到PATH
        if [ -f "$HOME/.cargo/env" ]; then
            source "$HOME/.cargo/env"
            log_success "Rust 已添加到PATH"
        fi
        
        log_success "Rust 安装完成，版本: $(rustc --version)"
    fi
    
    # 添加 llvm-tools-preview 组件
    log_info "添加 llvm-tools-preview 组件..."
    rustup component add llvm-tools-preview
    log_success "llvm-tools-preview 组件已添加"
}

# 步骤4: grcov 安装
install_grcov() {
    log_info "步骤4: 安装 grcov (覆盖率工具)"
    
    if check_command "grcov"; then
        log_info "grcov 已安装"
    else
        log_info "下载并安装 grcov..."
        sudo tar jxf - grcov-x86_64-unknown-linux-gnu.tar.bz2 -C /usr/local/bin
        log_success "grcov 安装完成"
    fi
}

# 步骤5: 项目设置
setup_project() {
    log_info "步骤5: 项目设置"
    
    # 检查当前目录
    CURRENT_DIR=$(pwd)
    log_info "当前目录: $CURRENT_DIR"
    
    # 检查是否为compiler-testing目录
    if [[ "$CURRENT_DIR" == *"compiler-testing"* ]] && [ -f "entrypoint.sh" ]; then
        log_info "已在 compiler-testing 目录中"
        PROJECT_DIR="$CURRENT_DIR"
    else
        # 检查是否存在compiler-testing目录
        if [ -d "compiler-testing" ]; then
            log_info "找到 compiler-testing 目录"
            PROJECT_DIR="$CURRENT_DIR/compiler-testing"
        else
            log_error "未找到 compiler-testing 目录"
            log_info "请确保在正确的位置运行此脚本"
            log_info "或者手动创建/克隆 compiler-testing 项目"
            exit 1
        fi
    fi
    
    cd "$PROJECT_DIR"
    log_info "项目目录: $(pwd)"
    
    # 设置环境变量
    log_info "设置环境变量..."
    export CARGO_HOME=/opt/cargo
    export CARGO_TARGET_DIR=/opt/cargo-target
    export PATH="/opt/cargo/bin:${PATH}"
    
    # 创建必要的目录
    log_info "创建必要的目录..."
    sudo mkdir -p /opt/node_cache/cmd /opt/node_cache/lib/snarkjs
    mkdir -p temp workspace profraw
    
    log_success "项目设置完成"
}

# 步骤6: Circom 编译器构建
build_circom_compilers() {
    log_info "步骤6: 构建 Circom 编译器"
    
    # 构建 circom-202（如果存在）
    if [ -d "assets/circom-202" ]; then
        log_info "构建 circom-202..."
        cd assets/circom-202
        cargo fetch
        cargo build --release
        sudo cp /opt/cargo-target/release/circom-202 /usr/local/bin/
        mkdir -p target/release
        cp /opt/cargo-target/release/circom-202 target/release/ 2>/dev/null || true
        cd ../..
        log_success "circom-202 构建完成"
    else
        log_warning "assets/circom-202 目录不存在，跳过构建"
    fi
    
    # 构建 circom-218（如果存在）
    if [ -d "assets/circom-218" ]; then
        log_info "构建 circom-218..."
        cd assets/circom-218
        cargo fetch
        cargo build --release
        sudo cp /opt/cargo-target/release/circom-218 /usr/local/bin/
        mkdir -p target/release
        cp /opt/cargo-target/release/circom-218 target/release/ 2>/dev/null || true
        cd ../..
        log_success "circom-218 构建完成"
    else
        log_warning "assets/circom-218 目录不存在，跳过构建"
    fi
}

# 步骤7: Node.js 依赖安装
install_node_deps() {
    log_info "步骤7: 安装 Node.js 依赖"
    
    # 安装 cmd 目录的依赖
    if [ -d "cmd" ]; then
        log_info "安装 cmd 目录的依赖..."
        cd cmd
        CI=true pnpm install
        sudo mv node_modules /opt/node_cache/cmd/ 2>/dev/null || true
        cd ..
        log_success "cmd 依赖安装完成"
    else
        log_warning "cmd 目录不存在，跳过依赖安装"
    fi
    
    # 安装 lib/snarkjs 目录的依赖
    if [ -d "lib/snarkjs" ]; then
        log_info "安装 lib/snarkjs 目录的依赖..."
        cd lib/snarkjs
        CI=true pnpm install
        sudo mv node_modules /opt/node_cache/lib/snarkjs/ 2>/dev/null || true
        cd ..
        log_success "lib/snarkjs 依赖安装完成"
    else
        log_warning "lib/snarkjs 目录不存在，跳过依赖安装"
    fi
}

# 步骤8: 权限设置
set_permissions() {
    log_info "步骤8: 设置权限"
    
    # 设置脚本执行权限
    log_info "设置脚本执行权限..."
    chmod +x entrypoint.sh 2>/dev/null || true
    chmod +x cases/*.sh 2>/dev/null || true
    chmod +x -R . 2>/dev/null || true
    
    # 为所有 .sh 文件添加执行权限
    log_info "为所有 .sh 文件添加执行权限..."
    find . -name "*.sh" -type f 2>/dev/null | while read -r file; do
        chmod +x "$file" 2>/dev/null || true
    done
    
    # 为所有 .js 文件添加读取和执行权限
    log_info "为所有 .js 文件添加读取和执行权限..."
    find . -name "*.js" -type f 2>/dev/null | while read -r file; do
        chmod +rx "$file" 2>/dev/null || true
    done
    
    # 为 bin 目录下的可执行文件设置权限
    if [ -d "bin" ]; then
        log_info "为 bin 目录下的可执行文件设置权限..."
        find bin -type f 2>/dev/null | while read -r file; do
            chmod +x "$file" 2>/dev/null || true
        done
    fi
    
    # 确保必要的目录有读写权限
    log_info "确保必要的目录有读写权限..."
    for dir in cmd config cases temp workspace profraw; do
        if [ -d "$dir" ]; then
            chmod -R 755 "$dir" 2>/dev/null || true
        fi
    done
    
    log_success "权限设置完成"
}

# 步骤9: 配置文件调整
adjust_config_files() {
    log_info "步骤9: 调整配置文件"
    
    # 替换配置文件中的路径（如果需要）
    if [ -f "config/config-default-1.json" ]; then
        log_info "调整 config/config-default-1.json..."
        sed -i 's|/home/cufoon/ppp|/app|g' config/config-default-1.json || log_warning "sed 替换失败"
    fi
    
    if [ -f "config/config-default-2.json" ]; then
        log_info "调整 config/config-default-2.json..."
        sed -i 's|/home/cufoon/ppp|/app|g' config/config-default-2.json || log_warning "sed 替换失败"
    fi
    
    log_success "配置文件调整完成"
}

# 步骤10: 符号链接创建
create_symlinks() {
    log_info "步骤10: 创建符号链接"
    
    # 创建 node_modules 符号链接
    if [ -d "cmd" ] && [ ! -d "cmd/node_modules" ] && [ -d "/opt/node_cache/cmd/node_modules" ]; then
        log_info "创建 cmd/node_modules 符号链接..."
        ln -sf /opt/node_cache/cmd/node_modules cmd/node_modules
    fi
    
    if [ -d "lib/snarkjs" ] && [ ! -d "lib/snarkjs/node_modules" ] && [ -d "/opt/node_cache/lib/snarkjs/node_modules" ]; then
        log_info "创建 lib/snarkjs/node_modules 符号链接..."
        ln -sf /opt/node_cache/lib/snarkjs/node_modules lib/snarkjs/node_modules
    fi
    
    log_success "符号链接创建完成"
}

# 步骤11: 验证安装
verify_installation() {
    log_info "步骤11: 验证安装"
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}          安装验证结果${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # 验证 circom 编译器
    echo -e "\n${BLUE}1. Circom 编译器:${NC}"
    if command -v circom-202 &> /dev/null; then
        echo -e "  ${GREEN}✓ circom-202: 已安装${NC}"
    else
        echo -e "  ${YELLOW}⚠ circom-202: 未找到${NC}"
    fi
    
    if command -v circom-218 &> /dev/null; then
        echo -e "  ${GREEN}✓ circom-218: 已安装${NC}"
    else
        echo -e "  ${YELLOW}⚠ circom-218: 未找到${NC}"
    fi
    
    # 验证 Node.js 和 pnpm
    echo -e "\n${BLUE}2. Node.js 和 pnpm:${NC}"
    if command -v node &> /dev/null; then
        echo -e "  ${GREEN}✓ Node.js: $(node --version)${NC}"
    else
        echo -e "  ${RED}✗ Node.js: 未安装${NC}"
    fi
    
    if command -v pnpm &> /dev/null; then
        echo -e "  ${GREEN}✓ pnpm: $(pnpm --version)${NC}"
    else
        echo -e "  ${RED}✗ pnpm: 未安装${NC}"
    fi
    
    # 验证 Rust
    echo -e "\n${BLUE}3. Rust 工具链:${NC}"
    if command -v rustc &> /dev/null; then
        echo -e "  ${GREEN}✓ Rust: $(rustc --version)${NC}"
    else
        echo -e "  ${RED}✗ Rust: 未安装${NC}"
    fi
    
    if command -v cargo &> /dev/null; then
        echo -e "  ${GREEN}✓ Cargo: $(cargo --version)${NC}"
    else
        echo -e "  ${RED}✗ Cargo: 未安装${NC}"
    fi
    
    # 验证 grcov
    echo -e "\n${BLUE}4. 覆盖率工具:${NC}"
    if command -v grcov &> /dev/null; then
        echo -e "  ${GREEN}✓ grcov: 已安装${NC}"
    else
        echo -e "  ${YELLOW}⚠ grcov: 未找到${NC}"
    fi
    
    # 验证项目结构
    echo -e "\n${BLUE}5. 项目结构:${NC}"
    if [ -f "entrypoint.sh" ]; then
        echo -e "  ${GREEN}✓ entrypoint.sh: 存在${NC}"
    else
        echo -e "  ${RED}✗ entrypoint.sh: 不存在${NC}"
    fi
    
    if [ -f "cmd/src/main.js" ]; then
        echo -e "  ${GREEN}✓ cmd/src/main.js: 存在${NC}"
    else
        echo -e "  ${RED}✗ cmd/src/main.js: 不存在${NC}"
    fi
    
    echo -e "\n${BLUE}========================================${NC}"
    log_success "安装验证完成"
}

# 步骤12: 测试运行
run_tests() {
    log_info "步骤12: 运行测试"
    
    echo ""
    read -p "是否运行测试? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "跳过测试运行"
        return
    fi
    
    # 测试单版本模式
    log_info "测试单版本模式..."
    if command -v node &> /dev/null && [ -f "cmd/src/main.js" ]; then
        node cmd/src/main.js single 2.1.8 --cflags --O1 || log_warning "单版本测试失败"
    else
        log_warning "无法运行单版本测试: Node.js 或 main.js 不存在"
    fi
    
    echo ""
    read -p "是否继续运行跨版本测试? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "测试跨版本模式..."
        if command -v node &> /dev/null && [ -f "cmd/src/main.js" ]; then
            node cmd/src/main.js cross 2.1.8 2.0.2 --cflags --O1 || log_warning "跨版本测试失败"
        else
            log_warning "无法运行跨版本测试: Node.js 或 main.js 不存在"
        fi
    fi
    
    echo ""
    read -p "是否继续运行重放测试? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "测试重放模式..."
        if command -v node &> /dev/null && [ -f "cmd/src/main.js" ]; then
            node cmd/src/main.js replay n1 || log_warning "重放测试失败"
        else
            log_warning "无法运行重放测试: Node.js 或 main.js 不存在"
        fi
    fi
    
    log_success "测试运行完成"
}

# 主函数
main() {
    # 显示标题
    show_header
    
    # 显示系统信息
    show_system_info
    
    # 检查是否为root用户
    check_root
    
    # 确认继续
    log_info "此脚本将安装和配置 compiler-testing 环境"
    log_info "包括:"
    log_info "  1. 系统依赖 (curl, git, build-essential等)"
    log_info "  2. Node.js 20.x 和 pnpm"
    log_info "  3. Rust 工具链 (nightly-2025-05-30)"
    log_info "  4. grcov 覆盖率工具"
    log_info "  5. Circom 编译器构建"
    log_info "  6. Node.js 依赖安装"
    log_info "  7. 权限设置"
    log_info "  8. 配置文件调整"
    log_info "  9. 符号链接创建"
    log_info "  10. 验证安装"
    log_info "  11. 测试运行"
    echo ""
    log_warning "注意: 某些步骤需要sudo权限"
    echo ""
    
    confirm_continue
    
    # 执行安装步骤
    install_system_deps
    install_nodejs_pnpm
    install_rust_toolchain
    install_grcov
    setup_project
    build_circom_compilers
    install_node_deps
    set_permissions
    adjust_config_files
    create_symlinks
    verify_installation
    run_tests
    
    # 完成信息
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  环境配置完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    log_info "下一步:"
    echo "  1. 你可以使用以下命令运行 compiler-testing:"
    echo "     cd compiler-testing"
    echo "     node cmd/src/main.js single 2.1.8 --cflags --O1"
    echo ""
    echo "  2. 或者使用 chainctl 工具:"
    echo "     ./chainctl -T single 2.1.8 --cflags --O1"
    echo ""
    echo "  3. 或者使用 orchestrator:"
    echo "     cd orchestrator && python3 main.py"
    echo ""
    log_info "故障排除请参考: compiler-testing环境配置步骤清单.md"
    echo ""
}

# 脚本入口点
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
