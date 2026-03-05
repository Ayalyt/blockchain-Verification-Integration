#!/bin/bash
set -e

if [ "$(id -u)" != "0" ]; then
    find /app -user root -type d 2>/dev/null | while read -r dir; do
        echo ">>> [权限] 更改目录所有权: $dir"
        chown -R "$(id -u):$(id -g)" "$dir" 2>/dev/null || true
    done
    find /app -user root -type f 2>/dev/null | while read -r file; do
        echo ">>> [权限] 更改文件所有权: $file"
        chown "$(id -u):$(id -g)" "$file" 2>/dev/null || true
    done
fi

shopt -s nullglob
config_files=(config/*.json)
if [ ${#config_files[@]} -gt 0 ]; then
    echo ">>> [Config] 正在替换 config/*.json..."
    sed -i 's|/home/cufoon/ppp|/app|g' config/*.json || echo ">>> [Warning] sed 替换部分文件失败"
else
    echo ">>> [Config] 未找到配置文件，跳过。"
fi

shopt -u nullglob

if [ -d "cmd" ]; then
    if [ ! -d "cmd/node_modules" ] && [ -d "/opt/node_cache/cmd/node_modules" ]; then
        echo ">>> [Node] Linking cmd/node_modules..."
        ln -sf /opt/node_cache/cmd/node_modules cmd/node_modules
    fi
fi

if [ -d "lib/snarkjs" ]; then
    if [ ! -d "lib/snarkjs/node_modules" ] && [ -d "/opt/node_cache/lib/snarkjs/node_modules" ]; then
        echo ">>> [Node] Linking lib/snarkjs/node_modules..."
        ln -sf /opt/node_cache/lib/snarkjs/node_modules lib/snarkjs/node_modules
    fi
fi

if [ -d "cases" ]; then
    sed -i 's/\r$//' cases/*.sh 2>/dev/null || true
    chmod +x cases/*.sh 2>/dev/null || true
fi

find /app -name "*.sh" -type f 2>/dev/null | while read -r file; do
    chmod +x "$file" 2>/dev/null || true
done

# 为所有.js文件添加读取和执行权限（Node.js需要）
find /app -name "*.js" -type f 2>/dev/null | while read -r file; do
    chmod +rx "$file" 2>/dev/null || true
done

# 为bin目录下的可执行文件设置权限
if [ -d "/app/bin" ]; then
    find /app/bin -type f 2>/dev/null | while read -r file; do
        chmod +x "$file" 2>/dev/null || true
    done
fi

# 确保必要的目录有读写权限
for dir in /app/cmd /app/config /app/cases /app/temp /app/workspace /app/profraw; do
    if [ -d "$dir" ]; then
        chmod -R 755 "$dir" 2>/dev/null || true
    fi
done

for file in /app/cmd/src/main.js /app/cmd/src/runner.js /app/cmd/src/shell/run.sh; do
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            true
        else
            chmod +x "$file" 2>/dev/null || true
        fi
    fi
done

echo ">>> 初始化完成，服务就绪。"

exec "$@"
