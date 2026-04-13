#!/bin/bash

echo "🔧 顶流 TopFlow - 完整重建脚本（后端+前端）"
echo "============================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 步骤1：清理
echo ""
echo "📦 步骤1/4: 清理旧容器..."
docker stop topflow-backend topflow-frontend 2>/dev/null || true
docker rm topflow-backend topflow-frontend 2>/dev/null || true
docker rmi topflow-backend topflow-frontend 2>/dev/null || true
print_success "清理完成"

# 步骤2：检查文件
echo ""
echo "📋 步骤2/4: 检查必要文件..."
required_files=(
    "requirements.txt"
    "Dockerfile.backend"
    "Dockerfile.frontend"
    "docker-compose.yml"
    "frontend/vite.config.js"
    "frontend/package.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file ✓"
    else
        print_error "$file ✗ 缺失！"
        exit 1
    fi
done

# 步骤3：构建镜像
echo ""
echo "🔨 步骤3/4: 构建Docker镜像..."
echo "----------------------------------"

echo "📦 [1/2] 构建后端镜像..."
if docker compose build --no-cache backend; then
    print_success "后端构建成功 ✓"
else
    print_error "后端构建失败！"
    exit 1
fi

echo ""
echo "🎨 [2/2] 构建前端镜像..."
if docker compose build --no-cache frontend; then
    print_success "前端构建成功 ✓"
else
    print_error "前端构建失败！"
    exit 1
fi

# 步骤4：启动服务
echo ""
echo "▶️  步骤4/4: 启动所有服务..."
if docker compose up -d; then
    print_success "服务启动成功！"
else
    print_error "服务启动失败！"
    exit 1
fi

# 等待并测试
echo ""
echo "⏳ 等待服务初始化..."
sleep 20

echo ""
echo "=========================================="
print_success "部署完成！"
echo "=========================================="

echo ""
echo "📊 服务状态："
docker compose ps

echo ""
echo "🧪 测试连接..."

# 测试后端API
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "后端API正常 ✓ (http://localhost:8000)"
else
    print_warning "后端API可能还在启动中，请稍后检查"
fi

# 测试前端
if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面正常 ✓ (http://localhost)"
else
    print_warning "前端可能还在启动中"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 访问信息${NC}"
echo "=========================================="
echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9${NC}"
echo -e "📚 API文档: ${YELLOW}http://43.160.238.9/docs${NC}"
echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
echo -e "📂 数据库:   ${YELLOW}./data/topflow.db${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}常用命令${NC}"
echo "=========================================="
echo "查看日志:     docker compose logs -f"
echo "重启服务:     docker compose restart"
echo "停止服务:     docker compose down"
echo "进入后端:     docker compose exec backend bash"
echo "备份数据库:   cp data/topflow.db backups/\$(date +%Y%m%d).db"
echo ""