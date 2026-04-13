#!/bin/bash

echo "🔧 顶流 TopFlow - 修复视频列表404问题"
echo "====================================="
echo ""
echo "本次修复："
echo "  ✅ 后端添加排序参数支持 (sort_by/sort_order)"
echo "  ✅ 修复API响应格式（使用Pydantic序列化）"
echo "  ✅ 前端功能优化（抓取数据集成、表单优化等）"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 步骤1：验证文件
echo "📋 步骤1/5: 验证关键文件..."
errors=0

if [ ! -f "backend/routers/videos.py" ]; then
    print_error "缺少 backend/routers/videos.py"
    errors=$((errors + 1))
elif grep -q "sort_by.*Optional\[str\]" backend/routers/videos.py && \
     grep -q "VideoResponse.from_orm" backend/routers/videos.py; then
    print_success "后端 videos.py 已更新 ✓"
else
    print_error "后端 videos.py 版本不匹配！"
    errors=$((errors + 1))
fi

if [ ! -f "frontend/src/views/Videos.vue" ]; then
    print_error "缺少 frontend/src/views/Videos.vue"
    errors=$((errors + 1))
elif grep -q "fetchMetadataInDialog" frontend/src/views/Videos.vue; then
    print_success "前端 Videos.vue 已更新 ✓"
else
    print_error "前端 Videos.vue 版本不匹配！"
    errors=$((errors + 1))
fi

if [ $errors -gt 0 ]; then
    print_error "发现 $errors 个文件问题！请确保所有文件已上传。"
    exit 1
fi

# 步骤2：重建后端镜像
echo ""
echo "🔨 步骤2/5: 重建后端镜像..."
docker stop topflow-backend 2>/dev/null || true
docker rm topflow-backend 2>/dev/null || true
docker rmi topflow-backend 2>/dev/null || true

if docker compose build --no-cache backend; then
    print_success "后端镜像构建成功 ✓"
else
    print_error "后端镜像构建失败！"
    exit 1
fi

# 步骤3：重建前端镜像
echo ""
echo "🎨 步骤3/5: 重建前端镜像..."
docker stop topflow-frontend 2>/dev/null || true
docker rm topflow-frontend 2>/dev/null || true
docker rmi topflow-frontend 2>/dev/null || true

if docker compose build --no-cache frontend; then
    print_success "前端镜像构建成功 ✓"
else
    print_error "前端镜像构建失败！"
    exit 1
fi

# 步骤4：启动服务
echo ""
echo "▶️  步骤4/5: 启动服务..."

if docker compose up -d; then
    print_success "服务启动成功 ✓"
else
    print_error "服务启动失败！"
    exit 1
fi

# 步骤5：等待并测试
echo ""
echo "⏳ 步骤5/5: 等待服务初始化..."
sleep 30

echo ""
echo "=========================================="
echo "🧪 测试API接口..."
echo "=========================================="

# 测试视频列表API
echo ""
echo "测试视频列表接口:"
video_response=$(curl -s http://localhost:8000/api/videos/ \
  -H "Authorization: Bearer $(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')" \
  2>/dev/null)

if echo "$video_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print('items' in d)" 2>/dev/null | grep -q "True"; then
    video_count=$(echo "$video_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('items',[])))")
    total_count=$(echo "$video_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total',0))")
    print_success "视频列表API正常 ✓ (当前页: $video_count 条, 总计: $total_count 条)"
else
    print_warning "视频列表API可能有问题，查看响应:"
    echo "$video_response" | head -c 200
fi

# 测试健康检查
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "后端健康检查正常 ✓"
fi

# 测试前端
if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面可访问 ✓"
fi

# 显示最终结果
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 修复完成！${NC}"
echo "=========================================="
echo ""
echo -e "🌐 访问地址: ${YELLOW}http://43.160.238.9/videos${NC}"
echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
echo ""

echo "如果视频管理页面仍然显示无数据，请检查："
echo "----------------------------------------"
echo "1. 是否以admin账号登录？（普通用户只能看到自己创建的视频）"
echo "2. 数据库中是否有视频数据？"
echo "   可以在仪表盘页面确认是否有数据显示"
echo "3. 查看浏览器控制台(F12)是否有错误信息"
echo ""
echo "常用命令："
echo "  查看日志: docker compose logs -f"
echo "  重启服务: docker compose restart"
echo ""