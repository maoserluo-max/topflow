#!/bin/bash

echo "🔧 最终完整修复：bcrypt + 密码问题"
echo "====================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "ℹ️  $1${NC}"; }

echo "⚠️  本次修复解决2个问题："
echo "   1. bcrypt版本不兼容 (AttributeError: __about__)"
echo "   2. 密码长度超过72字节限制 (ValueError)"
echo ""

# 步骤1：彻底清理
echo ""
echo "📦 步骤1/5: 彻底清理..."
echo "-----------------------------------"

docker stop topflow-backend topflow-frontend 2>/dev/null || true
docker rm topflow-backend topflow-frontend 2>/dev/null || true

echo "删除旧的Docker镜像..."
docker rmi topflow-backend 2>/dev/null || true
docker rmi topflow-frontend 2>/dev/null || true

# 清理构建缓存
docker builder prune -f 2>/dev/null || true

print_success "清理完成"

# 步骤2：验证关键文件
echo ""
echo "📋 步骤2/5: 验证关键文件..."
echo "-----------------------------------"

errors=0

# 检查requirements.txt中的bcrypt版本
if grep -q "bcrypt==4.0.1" requirements.txt && grep -q "passlib\[bcrypt\]==1.7.4" requirements.txt; then
    print_success "requirements.txt bcrypt版本正确 ✓"
else
    print_error "requirements.txt 配置错误！"
    errors=$((errors + 1))
fi

# 检查auth.py中是否有密码截断
if grep -q "\[:72\]" backend/auth.py; then
    print_success "auth.py 密码截断逻辑存在 ✓"
else
    print_error "auth.py 缺少密码截断！"
    errors=$((errors + 1))
fi

# 检查config.py中SECRET_KEY长度
if grep -q "topflow-secret-key-2024" backend/config.py; then
    print_success "config.py 默认密钥合理 ✓"
else
    print_warning "config.py 可能需要检查"
fi

if [ $errors -gt 0 ]; then
    print_error "发现 $errors 个配置错误！请确保所有文件已正确上传。"
    exit 1
fi

# 步骤3：重建后端镜像（必须 --no-cache）
echo ""
echo "🔨 步骤3/5: 重建后端镜像（完全重建，不使用缓存）..."
echo "--------------------------------------------------------"

if docker compose build --no-cache backend; then
    print_success "后端镜像构建成功 ✓"
else
    print_error "后端镜像构建失败！"
    print_info "请查看上方错误信息"
    exit 1
fi

# 步骤4：启动服务
echo ""
echo "▶️  步骤4/5: 启动服务..."
echo "-------------------------"

if docker compose up -d; then
    print_success "服务启动命令执行成功"
else
    print_error "服务启动失败！"
    exit 1
fi

# 步骤5：等待并验证
echo ""
echo "⏳ 步骤5/5: 等待并验证（最多等待90秒）..."
echo "--------------------------------------------"

success=false
for i in {1..18}; do
    sleep 5
    
    # 检查容器状态
    container_status=$(docker ps --filter "name=topflow-backend" --format "{{.Status}}" 2>/dev/null)
    
    if [[ "$container_status" == *"Up"* ]]; then
        # 测试API
        if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
            success=true
            break
        fi
        
        # 检查是否有错误日志（但不包括正常的启动信息）
        error_count=$(docker compose logs backend 2>&1 | grep -c "Error\|Exception\|Traceback\|ValueError\|AttributeError" || true)
        
        if [ "$error_count" -gt 3 ]; then
            echo ""
            print_warning "[$((i*5))秒] 检测到错误，显示最后10行日志："
            docker compose logs --tail=10 backend
            echo ""
            print_error "后端仍有错误！"
            echo ""
            echo "可能的原因："
            echo "1. 文件没有正确上传到服务器"
            echo "2. Docker使用了缓存（需要确认--no-cache生效）"
            echo ""
            echo "建议操作："
            echo "  docker system prune -a"
            echo "  ./final-complete-fix.sh"
            exit 1
        fi
    elif [[ "$container_status" == *"Restarting"* ]]; then
        if [ $((i % 6)) -eq 0 ]; then  # 每30秒提示一次
            echo "    [$((i*5))秒] 后端仍在重启中..."
        fi
    else
        echo "    [$((i*5))秒] 容器状态异常: $container_status"
    done
    
    if [ $i -eq 18 ]; then
        echo ""
        print_warning "等待超时"
    fi
done

# 显示最终结果
echo ""
echo "=========================================="
if [ "$success" = true ]; then
    echo -e "${GREEN}🎉 部署成功！${NC}"
else
    echo -e "${YELLOW}⚠️  部署可能未完全成功${NC}"
fi
echo "=========================================="

echo ""
echo "📊 服务状态："
docker compose ps

echo ""
echo "🧪 API测试："
response=$(curl -s http://localhost:8000/api/health 2>/dev/null)
if [ -n "$response" ]; then
    print_success "后端API响应正常 ✓"
    echo "   $response"
else
    print_warning "API暂未响应"
fi

# 前端测试
if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面可访问 ✓"
else
    print_warning "前端暂未响应"
fi

echo ""
if [ "$success" = true ]; then
    echo "=========================================="
    echo -e "${GREEN}访问信息${NC}"
    echo "=========================================="
    echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9${NC}"
    echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
    echo -e "📚 API文档: ${YELLOW}http://43.160.238.9/docs${NC}"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}常用命令${NC}"
    echo "=========================================="
    echo "查看日志:     docker compose logs -f"
    "重启服务:     docker compose restart"
    echo "进入后端:     docker compose exec backend bash"
    echo "备份数据库:   cp data/topflow.db backups/\$(date +%Y%m%d).db"
    echo ""
else
    echo "=========================================="
    echo -e "${RED}排查建议${NC}"
    echo "=========================================="
    echo "1. 查看完整日志:"
    echo "   docker compose logs -f backend"
    echo ""
    echo "2. 手动测试密码哈希:"
    echo '   docker exec topflow-backend python -c "from auth import get_password_hash; print(get_password_hash(\"test\"))"'
    echo ""
    echo "3. 如果仍有问题，请把完整错误日志发给我"
    echo ""
fi