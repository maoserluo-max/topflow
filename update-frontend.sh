#!/bin/bash

echo "🚀 顶流 TopFlow - 前端功能更新脚本"
echo "=================================="
echo ""
echo "本次更新内容："
echo "  ✅ 视频列表默认按发布日期从晚到早排序"
echo "  ✅ 抓取数据功能集成到新增视频对话框"
echo "  ✅ 地区改为下拉选择（ID/MY/TH/TW/KR/JP）"
echo "  ✅ 内容方向改为下拉选择（FF/MLBB）"
echo "  ✅ 发布日期默认当天"
echo "  ✅ 状态选项优化（待审核/待发布/已发布/已完成）"
echo "  ✅ 对接人权限控制（管理员可选择所有用户）"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "ℹ️  $1${NC}"; }

# 步骤1：验证文件
echo "📋 步骤1/4: 验证关键文件..."
if [ ! -f "frontend/src/views/Videos.vue" ]; then
    print_error "缺少 Videos.vue 文件！"
    exit 1
fi

# 检查关键特性是否在文件中
if grep -q "fetchMetadataInDialog" frontend/src/views/Videos.vue && \
   grep -q "regionOptions" frontend/src/views/Videos.vue && \
   grep -q "sort_by.*publish_date" frontend/src/views/Videos.vue; then
    print_success "Videos.vue 包含所有新功能 ✓"
else
    print_error "Videos.vue 文件可能未正确上传！"
    exit 1
fi

# 步骤2：仅重建前端镜像
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

# 步骤4：等待并测试
echo ""
echo "⏳ 步骤4/4: 等待前端启动..."
sleep 15

if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面可访问 ✓"
    
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🎉 更新完成！${NC}"
    echo "=========================================="
    echo ""
    echo -e "🌐 前端界面: ${YELLOW}http://43.160.238.9/videos${NC}"
    echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
    echo ""
    echo "新功能使用说明："
    echo "----------------------------------------"
    echo "1. 视频列表现在默认按发布日期从晚到早排序"
    echo ""
    echo "2. 点击「新增视频」按钮后："
    echo "   - 在顶部输入框粘贴视频链接"
    echo "   - 点击「抓取数据」按钮自动获取元数据"
    echo "   - 成功则自动填充表单，失败则提示手动填写"
    echo ""
    echo "3. 新增视频表单改进："
    echo "   - 地区：下拉选择 ID/MY/TH/TW/KR/JP"
    echo "   - 内容方向：下拉选择 FF(Free Fire) / MLBB(Mobile Legends)"
    echo "   - 发布日期：默认当天，可手动更改"
    echo "   - 状态：待审核 → 待发布 → 已发布 → 已完成"
    echo "   - 对接人：普通用户自动填当前账号，管理员可选所有用户"
    echo ""
    echo "常用命令："
    echo "  重启前端: docker compose restart frontend"
    echo "  查看日志: docker compose logs -f frontend"
else
    print_warning "前端可能还在启动中，请稍后访问 http://43.160.238.9/videos"
fi