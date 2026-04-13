#!/bin/bash

echo "🔧 顶流 TopFlow - Docker故障修复与重新部署脚本"
echo "=============================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# 步骤1：停止并删除所有相关容器
echo ""
print_info "步骤1/5: 清理旧容器和镜像..."
echo "-----------------------------------"

# 停止所有topflow相关的容器
docker stop topflow-backend topflow-frontend 2>/dev/null || true

# 删除容器
docker rm topflow-backend topflow-frontend 2>/dev/null || true

# 删除旧的镜像（可选，如果需要完全重建）
print_warning "是否要删除旧的Docker镜像以节省空间？(y/n)"
read -r cleanup_images
if [ "$cleanup_images" = "y" ] || [ "$cleanup_images" = "Y" ]; then
    docker rmi topflow-backend topflow-frontend 2>/dev/null || true
    print_success "旧镜像已删除"
else
    print_info "保留旧镜像（将使用缓存加速构建）"
fi

# 清理未使用的Docker资源
docker system prune -f --volumes 2>/dev/null || true

print_success "容器清理完成"

# 步骤2：检查环境文件
echo ""
print_info "步骤2/5: 检查环境配置..."
echo "---------------------------"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning ".env 文件不存在，已从模板创建"
        print_warning "请务必编辑 .env 文件修改 SECRET_KEY！"
        read -p "按回车键继续..." 
    else
        print_error ".env 和 .env.example 都不存在！"
        exit 1
    fi
else
    print_success ".env 配置文件存在"
fi

# 步骤3：创建必要目录
echo ""
print_info "步骤3/5: 创建数据目录..."
echo "-------------------------"

mkdir -p data ssl backups
print_success "目录创建完成"

# 步骤4：构建Docker镜像
echo ""
print_info "步骤4/5: 构建Docker镜像（首次约需5-10分钟）..."
echo "----------------------------------------------"

if docker compose build --no-cache backend; then
    print_success "后端镜像构建成功"
else
    print_error "后端镜像构建失败！请检查错误信息"
    print_info "常见问题排查："
    echo "   1. 检查网络连接（需要下载Python包）"
    echo "   2. 检查requirements.txt是否有语法错误"
    echo "   3. 尝试: docker compose build --no-cache backend"
    exit 1
fi

if docker compose build --no-cache frontend; then
    print_success "前端镜像构建成功"
else
    print_error "前端镜像构建失败！"
    exit 1
fi

# 步骤5：启动服务
echo ""
print_info "步骤5/5: 启动所有服务..."
echo "--------------------------"

if docker compose up -d; then
    print_success "服务启动成功！"
else
    print_error "服务启动失败！"
    print_info "尝试手动查看日志:"
    echo "   docker compose logs backend"
    echo "   docker compose logs frontend"
    exit 1
fi

# 等待服务启动
echo ""
print_info "等待服务初始化（约30秒）..."
sleep 10

# 显示状态
echo ""
echo "=========================================="
print_success "部署完成！检查服务状态："
echo "=========================================="
docker compose ps

# 测试API
echo ""
print_info "测试后端API连接..."

for i in {1..6}; do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "后端API运行正常！"
        break
    else
        if [ $i -eq 6 ]; then
            print_warning "后端API可能还在启动中，请稍后检查日志"
            print_info "命令: docker compose logs -f backend"
        else
            sleep 5
        fi
    fi
done

# 显示访问信息
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 访问信息${NC}"
echo "=========================================="
echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9${NC}"
echo -e "📚 API文档: ${YELLOW}http://43.160.238.9/docs${NC} (开发阶段)"
echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC} (⚠️ 请立即修改)"
echo -e "📂 数据位置: ${YELLOW}./data/topflow.db${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}常用运维命令${NC}"
echo "=========================================="
echo "查看日志:     docker compose logs -f"
echo "重启服务:     docker compose restart"
echo "停止服务:     docker compose down"
echo "重新构建:     docker compose up -d --build"
echo "进入后端:     docker compose exec backend bash"
echo "备份数据库:   cp data/topflow.db backups/\$(date +%Y%m%d).db"
echo ""

print_success "所有操作完成！如有问题请查看日志排查"
echo ""