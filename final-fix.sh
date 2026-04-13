#!/bin/bash

echo "🔧 最终修复：解决模块导入问题"
echo "=============================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 步骤1：清理
echo "📦 步骤1/4: 清理旧容器和镜像..."
docker stop topflow-backend topflow-frontend 2>/dev/null || true
docker rm topflow-backend topflow-frontend 2>/dev/null || true

echo ""
print_warning "是否删除旧的Docker镜像？（推荐：y）"
read -r rebuild_images
if [ "$rebuild_images" = "y" ] || [ "$rebuild_images" = "Y" ]; then
    docker rmi topflow-backend topflow-frontend 2>/dev/null || true
    print_success "旧镜像已删除，将完全重建"
else
    print_info "保留旧镜像（可能使用缓存）"
fi

# 步骤2：检查关键文件
echo ""
echo "📋 步骤2/4: 检查关键配置..."
echo "--------------------------------"

# 检查Dockerfile.backend中的WORKDIR
if grep -q "WORKDIR /app/backend" Dockerfile.backend; then
    print_success "Dockerfile.backend WORKDIR正确 ✓"
else
    print_error "Dockerfile.backend 配置错误！"
    exit 1
fi

# 检查启动命令
if grep -q "main:app" Dockerfile.backend; then
    print_success "启动命令已修正 ✓"
else
    print_error "启动命令错误！"
    exit 1
fi

# 步骤3：构建并启动
echo ""
echo "🔨 步骤3/4: 构建Docker镜像（这次需要重建后端）..."
echo "----------------------------------------------"

if docker compose build --no-cache backend frontend; then
    print_success "镜像构建成功 ✓"
else
    print_error "镜像构建失败！请检查上方错误信息"
    exit 1
fi

echo ""
echo "▶️  启动服务..."

if docker compose up -d; then
    print_success "服务启动成功！"
else
    print_error "服务启动失败！"
    exit 1
fi

# 步骤4：等待并验证
echo ""
echo "⏳ 步骤4/4: 等待服务初始化（约60秒）..."
echo ""

for i in {1..12}; do
    sleep 5
    
    # 检查容器状态
    if docker ps | grep -q "topflow-backend.*Up"; then
        # 测试API
        if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
            echo ""
            print_success "后端API已就绪！✨"
            break
        fi
        
        # 检查是否有错误日志
        error_count=$(docker compose logs backend 2>&1 | grep -c "Error\|Exception\|Traceback" || true)
        if [ "$error_count" -gt 0 ]; then
            echo ""
            print_warning "检测到错误日志，显示最近5行："
            docker compose logs --tail=5 backend
            echo ""
            print_error "后端启动失败！请查看完整日志："
            echo "   docker compose logs -f backend"
            exit 1
        fi
    else
        if [ $i -eq 12 ]; then
            echo ""
            print_error "后端容器未运行！查看状态："
            docker compose ps
            docker compose logs --tail=20 backend
            exit 1
        fi
    fi
    
    echo "    [$((i*5))秒] 等待中..."
done

# 显示最终结果
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 部署成功！${NC}"
echo "=========================================="

echo ""
echo "📊 服务状态："
docker compose ps

echo ""
echo "🧪 连接测试："

# 测试API
response=$(curl -s http://localhost:8000/api/health 2>/dev/null)
if [ -n "$response" ]; then
    print_success "后端API正常响应 ✓"
    echo "   响应: $response"
else
    print_warning "API暂未响应（稍后再试）"
fi

# 测试前端
if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面可访问 ✓"
else
    print_warning "前端暂未响应"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}访问信息${NC}"
echo "=========================================="
echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9${NC}"
echo -e "📚 API文档: ${YELLOW}http://43.160.238.9/docs${NC}"
echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
echo -e "⚠️  请立即修改默认密码！"
echo ""

echo "=========================================="
echo -e "${GREEN}常用命令${NC}"
echo "=========================================="
echo "查看所有日志:   docker compose logs -f"
echo "仅看后端日志:   docker compose logs -f backend"
echo "重启后端:       docker compose restart backend"
echo "进入后端容器:   docker compose exec backend bash"
echo "备份数据库:     cp data/topflow.db backups/\$(date +%Y%m%d).db"
echo ""