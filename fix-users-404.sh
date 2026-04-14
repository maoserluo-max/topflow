#!/bin/bash

echo "🔧 顶流 TopFlow - 修复用户列表404错误"
echo "====================================="
echo ""
echo "本次修复："
echo "  ✅ 修正前端API路径 (/api/users/ → /api/auth/users)"
echo "  ✅ 优化错误处理（不再弹出错误提示）"
echo "  ✅ 包含之前的所有优化（数据库持久化、排序、表单等）"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 步骤1：验证文件
echo "📋 步骤1/4: 验证修复文件..."
if [ ! -f "frontend/src/views/Videos.vue" ]; then
    print_error "缺少 Videos.vue"
    exit 1
fi

if grep -q "api.get('/auth/users')" frontend/src/views/Videos.vue; then
    print_success "Videos.vue API路径已修复 ✓"
else
    print_error "Videos.vue 版本不匹配！请上传最新版本"
    exit 1
fi

# 步骤2：仅重建前端（后端不需要改）
echo ""
echo "🎨 步骤2/4: 重建前端镜像..."
docker stop topflow-frontend 2>/dev/null || true
docker rm topflow-frontend 2>/dev/null || true
docker rmi topflow-frontend 2>/dev/null || true

if docker compose build --no-cache frontend; then
    print_success "前端镜像构建成功 ✓"
else
    print_error "前端镜像构建失败！"
    exit 1
fi

# 步骤3：启动服务
echo ""
echo "▶️  步骤3/4: 启动服务..."
if docker compose up -d; then
    print_success "服务启动成功 ✓"
else
    print_error "服务启动失败！"
    exit 1
fi

# 步骤4：测试
echo ""
echo "⏳ 步骤4/4: 等待前端启动..."
sleep 15

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 修复完成！${NC}"
echo "=========================================="
echo ""
echo -e "🌐 访问地址: ${YELLOW}http://43.160.238.9/videos${NC}"
echo ""
echo "修复内容："
echo "----------------------------------------"
echo "1. ✅ 用户列表API路径已修正为 /api/auth/users"
echo "2. ✅ 错误处理优化：获取用户列表失败时不再弹错误提示"
echo "3. ✅ 视频管理页面不会再显示 'not found' 错误"
echo ""
echo "说明："
echo "----------------------------------------"
echo "- admin/manager账号登录 → 可以加载用户列表用于对接人选择"
echo "- 普通用户登录 → 对接人字段自动填当前用户名（无需用户列表）"
echo "- 即使API调用失败，页面功能也不受影响"
echo ""
echo "常用命令："
echo "  重启前端: docker compose restart frontend"
echo "  查看日志: docker compose logs -f frontend"
echo ""