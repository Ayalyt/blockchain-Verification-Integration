#!/bin/bash
set -e

# 获取当前目录名作为 Docker Compose 的项目名前缀
PROJECT_NAME=$(basename $(pwd) | tr '[:upper:]' '[:lower:]' | tr -cd '[a-z0-9-_]')
DIST_DIR="dist_package"
IMAGES_TAR="docker_images.tar"
SOURCE_TAR="source_code.tar.gz"

mkdir -p $DIST_DIR

echo ">>> 1. 正在构建最新镜像..."
docker-compose build

echo ">>> 2. 正在导出镜像到 $IMAGES_TAR (这可能需要几分钟)..."
# 获取 compose 定义的所有镜像名称
IMAGES=$(docker-compose config --format json | grep '"image":' | awk -F '"' '{print $4}' || true)
# 如果 compose 没指定 image name，则推断默认名称
if [ -z "$IMAGES" ]; then
    IMAGES="${PROJECT_NAME}-orchestrator ${PROJECT_NAME}-compiler-verification ${PROJECT_NAME}-cipher-verification ${PROJECT_NAME}-smartifsyn-test ${PROJECT_NAME}-compiler-testing"
fi

echo "    目标镜像: $IMAGES"
docker save -o $IMAGES_TAR $IMAGES

echo ">>> 3. 正在打包源代码..."
tar --exclude='./.git' \
    --exclude='./.env' \
    --exclude="./$IMAGES_TAR" \
    --exclude="./$DIST_DIR" \
    -czvf $SOURCE_TAR . > /dev/null

echo ">>> 4. 生成部署包..."
rm -rf $DIST_DIR
mkdir -p $DIST_DIR
mv $IMAGES_TAR $DIST_DIR/
mv $SOURCE_TAR $DIST_DIR/

# 创建一个安装脚本
cat > $DIST_DIR/install.sh << 'EOF'
#!/bin/bash
set -e

echo ">>> 解压源码..."
tar -xzvf source_code.tar.gz > /dev/null

echo ">>> 导入 Docker 镜像..."
docker load -i docker_images.tar

echo ">>> 生成环境配置..."
echo "HOST_PROJECT_PATH=$(pwd)" > .env

echo ">>> 部署完成！"
echo "请运行 ./chainctl 来启动工具。"
EOF

chmod +x $DIST_DIR/install.sh

echo "==========================================="
echo "打包完成！部署包位置: ./$DIST_DIR"
echo "==========================================="
