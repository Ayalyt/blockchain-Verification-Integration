#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

check_directory() {
    if [ ! -f "docker-compose.yml" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

stop_containers() {
    log_info "正在停止服务..."
    
    if docker-compose down; then
        log_success "服务已停止"
    else
        log_error "停止服务时发生错误"
        exit 1
    fi
}

cleanup_resources() {
    log_info "清理未使用的Docker资源..."
    
    if docker container prune -f &> /dev/null; then
        log_success "未使用的容器已清理"
    fi
    
    if docker image prune -f &> /dev/null; then
        log_success "未使用的镜像已清理"
    fi
    
    if docker network prune -f &> /dev/null; then
        log_success "未使用的网络已清理"
    fi
    
    read -p "是否清理Docker构建缓存？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if docker builder prune -f &> /dev/null; then
            log_success "构建缓存已清理"
        fi
    fi
}

show_stopped_status() {
    log_info "检查平台状态..."
    
    if docker-compose ps | grep -q "Up"; then
        log_warning "仍有容器在运行:"
        docker-compose ps
    else
        log_success "所有容器已停止"
    fi
    
    echo ""
    echo "平台已完全停止。"
    echo "如需重新启动，请运行: ./start_platform.sh"
    echo ""
}

main() {
    echo -e "${BLUE}"
    echo "================================================"
    echo "    验证工具停止脚本"
    echo "================================================"
    echo -e "${NC}"
    
    check_directory
    
    log_info "当前运行状态:"
    docker-compose ps
    
    echo ""
    read -p "确认停止？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 0
    fi
    
    stop_containers
    cleanup_resources
    show_stopped_status
    
    log_success "停止完成"
}

main "$@"
