#!/bin/bash

echo "🔧 快速修复：bcrypt密码长度问题"
echo "==============================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 步骤1：清理旧容器
echo "📦 步骤1/3: 清理容器..."
docker stop topflow-backend topflow-frontend 2>/dev/null || true
docker rm topflow-backend topflow-frontend 2>/dev/null || true
print_success "清理完成"

# 步骤2：检查.env文件
echo ""
echo "📋 步骤2/3: 检查环境变量..."
if [ -f ".env" ]; then
    secret_key=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2-)
    if [ -n "$secret_key" ]; then
        key_length=${#secret_key}
        if [ "$key_length" -gt 72 ]; then
            print_warning "SECRET_KEY过长 ($key_length 字符)！"
            echo "   建议修改为72字符以内的密钥"
            echo ""
            print_info "当前SECRET_KEY前20个字符: ${secret_key:0:20}..."
        else
            print_success "SECRET_KEY长度正常 ($key_length 字符) ✓"
        fi
    else
        print_warning ".env文件中未设置SECRET_KEY，将使用默认值"
    fi
else
    print_warning "未找到.env文件，将使用默认配置"
fi

# 步骤3：重建后端镜像（必须！）
echo ""
echo "🔨 步骤3/3: 重建后端镜像..."
echo "    （这次只需要重建后端，前端可以复用）"

# 删除旧的backend镜像
docker rmi topflow-backend 2>/dev/null || true

# 重新构建
if docker compose build --no-cache backend; then
    print_success "后端镜像构建成功 ✓"
else
    print_error "后端镜像构建失败！"
    exit 1
fi

# 启动服务
echo ""
echo "▶️  启动服务..."

if docker compose up -d; then
    print_success "服务启动成功！"
else
    print_error "服务启动失败！"
    exit 1
fi

# 等待初始化
echo ""
echo "⏳ 等待数据库初始化（约30秒）..."
sleep 30

# 检查状态
echo ""
echo "=========================================="
echo "📊 服务状态："
echo "=========================================="
docker compose ps

# 检查日志中的错误
echo ""
error_logs=$(docker compose logs backend 2>&1 | grep -i "error\|exception\|traceback" | tail -5)
if [ -n "$error_logs" ]; then
    print_warning "检测到错误日志："
    echo "$error_logs"
    echo ""
    print_error "后端可能仍有问题，请查看完整日志："
    echo "   docker compose logs -f backend"
    exit 1
else
    # 测试API
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "✅ 后端API运行正常！"
        
        echo ""
        echo "=========================================="
        echo -e "${GREEN}🎉 部署成功！${NC}"
        echo "=========================================="
        echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9${NC}"
        echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
        echo ""
        echo "常用命令:"
        echo "  查看日志: docker compose logs -f"
        echo "  重启服务: docker compose restart"
    else
        print_warning "后端API暂未响应，请稍后检查："
        echo "  docker compose logs -f backend"
    fi
fi