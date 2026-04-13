#!/bin/bash

echo "🔧 快速修复：解决后端健康检查失败问题"
echo "========================================"
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
echo "📦 步骤1/3: 清理旧容器..."
docker stop topflow-backend topflow-frontend 2>/dev/null || true
docker rm topflow-backend topflow-frontend 2>/dev/null || true
print_success "清理完成"

# 步骤2：重新构建并启动（不使用 --no-cache 以加快速度）
echo ""
echo "▶️  步骤2/3: 构建并启动服务..."
echo "--------------------------------"

# 直接启动（如果镜像已存在会很快）
if docker compose up -d --build; then
    print_success "服务已启动！"
else
    print_error "启动失败！尝试完全重建..."
    docker compose build --no-cache && docker compose up -d
fi

# 步骤3：等待并检查
echo ""
echo "⏳ 步骤3/3: 等待服务初始化..."
echo "    （首次启动可能需要30-60秒）"
echo ""

# 等待60秒让服务完全启动
for i in {1..12}; do
    sleep 5
    echo "    [$((i*5))秒] 检查状态..."
    
    # 检查后端是否运行
    if docker ps | grep -q "topflow-backend"; then
        backend_status="运行中"
        
        # 尝试测试API
        if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
            echo ""
            print_success "后端API已就绪！"
            break
        fi
    else
        backend_status="未运行"
    fi
    
    if [ $i -eq 12 ]; then
        echo ""
        print_warning "等待超时，但服务可能仍在启动中"
        print_info "请稍后手动检查:"
        echo "   docker compose ps"
        echo "   docker compose logs backend"
    fi
done

# 显示最终状态
echo ""
echo "=========================================="
echo "📊 当前服务状态："
echo "=========================================="
docker compose ps

echo ""
echo "🧪 测试连接..."

# 测试后端
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "后端API正常 ✓"
    echo "   URL: http://localhost:8000/api/health"
else
    print_warning "后端API暂未响应（可能还在启动）"
    echo "   建议: docker compose logs -f backend"
fi

# 测试前端
if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面正常 ✓"
    echo "   URL: http://localhost"
else
    print_warning "前端暂未响应"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}访问信息${NC}"
echo "=========================================="
echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9${NC}"
echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}调试命令${NC}"
echo "=========================================="
echo "查看日志:     docker compose logs -f"
echo "仅看后端:     docker compose logs -f backend"
echo "重启后端:     docker compose restart backend"
echo "进入后端:     docker compose exec backend bash"
echo ""