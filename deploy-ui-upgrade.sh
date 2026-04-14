#!/bin/bash

echo "╔══════════════════════════════════════════════════════╗"
echo "║  🚀 顶流 TopFlow - UI 科技感升级部署脚本              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "本次更新内容："
echo "  ✨ 全新科技感暗色主题 UI（Tailwind CSS）"
echo "  🔮 玻璃拟态卡片 + 渐变色彩 + 霓虹光效"
echo "  🎨 Dashboard / Videos / Users 页面全面重构"
echo "  🖼️ 登录页面动态粒子背景效果"
echo "  🧭 现代化侧边栏 + 顶部导航栏"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# ========================================
# 步骤1：验证文件完整性
# ========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 步骤 1/6: 验证关键文件..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REQUIRED_FILES=(
    "frontend/tailwind.config.js"
    "frontend/postcss.config.js"
    "frontend/src/style.css"
    "frontend/src/views/Dashboard.vue"
    "frontend/src/views/Videos.vue"
    "frontend/src/views/Users.vue"
    "frontend/src/views/Login.vue"
    "frontend/src/layouts/MainLayout.vue"
    "Dockerfile.frontend"
)

MISSING=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "缺少: $file"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    print_error "共缺少 $MISSING 个关键文件！请确保代码已完整推送！"
    exit 1
fi

# 验证 Tailwind CSS 配置
if grep -q "tailwindcss" frontend/package.json && \
   grep -q "@tailwind base" frontend/src/style.css && \
   (grep -q "cyber:" frontend/tailwind.config.js || grep -q "'blue':" frontend/tailwind.config.js); then
    print_success "Tailwind CSS 配置验证通过 ✓"
else
    print_error "Tailwind CSS 配置不完整！"
    echo ""
    echo "  请检查以下文件："
    [ ! -f "frontend/package.json" ] && print_error "  ✗ 缺少 frontend/package.json"
    [ ! -f "frontend/src/style.css" ] && print_error "  ✗ 缺少 frontend/src/style.css"
    [ ! -f "frontend/tailwind.config.js" ] && print_error "  ✗ 缺少 frontend/tailwind.config.js"
    
    if [ -f "frontend/package.json" ]; then
        grep -q "tailwindcss" frontend/package.json || print_warning "  ⚠ package.json 中未找到 tailwindcss 依赖"
    fi
    if [ -f "frontend/tailwind.config.js" ]; then
        grep -q "cyber:" frontend/tailwind.config.js || print_warning "  ⚠ tailwind.config.js 中未找到 cyber 颜色配置"
    fi
    exit 1
fi

# 验证新 UI 特性
if grep -q "glass-card" frontend/src/views/Dashboard.vue && \
   grep -q "gradient-text" frontend/src/views/Videos.vue; then
    print_success "新 UI 组件已就位 ✓"
else
    print_error "UI 文件可能未正确上传！"
    exit 1
fi

# ========================================
# 步骤2：停止当前运行的服务
# ========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 步骤 2/6: 停止当前服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker compose down 2>/dev/null || true

# 强制清理可能残留的容器
for container in topflow-frontend topflow-backend; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
        print_info "清理容器: $container"
    fi
done

print_success "所有容器已停止 ✓"

# ========================================
# 步骤3：清理旧的前端镜像
# ========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  步骤 3/6: 清理旧镜像..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 删除旧的前端镜像以强制重建
if docker images | grep -q "topflow-frontend"; then
    docker rmi topflow-frontend 2>/dev/null || true
    print_info "旧前端镜像已删除"
fi

# 清理悬空镜像
docker image prune -f 2>/dev/null || true

print_success "镜像清理完成 ✓"

# ========================================
# 步骤4：构建新的前端镜像（含 Tailwind）
# ========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 步骤 4/6: 构建前端镜像 (Tailwind CSS)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "⏳ 这一步会安装 Tailwind CSS 并编译样式，请耐心等待..."

if docker compose build --no-cache frontend 2>&1; then
    print_success "前端镜像构建成功 ✓"
else
    print_error "前端镜像构建失败！"
    echo ""
    print_info "常见问题排查："
    echo "  1. 检查 Dockerfile.frontend 是否存在"
    echo "  2. 检查 package.json 中是否包含 tailwindcss 依赖"
    echo "  3. 运行 'docker compose build frontend' 查看详细错误"
    exit 1
fi

# ========================================
# 步骤5：启动所有服务
# ========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶️  步骤 5/6: 启动所有服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker compose up -d 2>&1; then
    print_success "服务启动命令执行成功 ✓"
else
    print_error "服务启动失败！"
    exit 1
fi

# ========================================
# 步骤6：等待并验证
# ========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏳ 步骤 6/6: 等待服务启动并验证..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
print_info "等待后端 API 启动 (约30秒)..."
sleep 15

# 检查后端健康状态
RETRIES=0
MAX_RETRIES=6
while [ $RETRIES -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "后端 API 健康检查通过 ✓"
        break
    fi
    RETRIES=$((RETRIES + 1))
    sleep 5
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    print_warning "后端可能还在启动中，稍后可访问 http://43.160.238.9/docs 查看"
fi

echo ""
print_info "等待前端 Nginx 启动 (约10秒)..."
sleep 10

# 检查前端是否可访问
if curl -sf http://localhost > /dev/null 2>&1; then
    print_success "前端页面可访问 ✓"
else
    print_warning "前端可能还在启动中..."
fi

# 最终输出
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo -e "${GREEN}║  🎉 UI 升级部署完成！                              ║${NC}"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "┌─────────────────────────────────────────────────────┐"
echo "│  🌐 访问地址                                        │"
echo "│     前端界面: ${YELLOW}http://43.160.238.9${NC}                    │"
echo "│     视频管理: ${YELLOW}http://43.160.238.9/videos${NC}                │"
echo "│     用户管理: ${YELLOW}http://43.160.238.9/users${NC}                 │"
echo "│     API文档:  ${YELLOW}http://43.160.238.9/docs${NC}                  │"
echo "├─────────────────────────────────────────────────────┤"
echo "│  👤 登录账号                                        │"
echo "│     用户名: ${YELLOW}admin${NC}                                    │"
echo "│     密码:   ${YELLOW}admin123${NC}                                  │"
echo "└─────────────────────────────────────────────────────┘"
echo ""
echo "🎨 新 UI 特性预览："
echo "----------------------------------------"
echo "  • 暗色科技主题 + 玻璃拟态效果"
echo "  • 渐变文字 + 霓虹发光按钮"
echo "  • 动态粒子登录背景"
echo "  • 现代化数据表格 + 悬停动画"
echo "  • 自定义侧边栏导航"
echo ""
echo "📋 常用运维命令："
echo "----------------------------------------"
echo "  查看日志:   docker compose logs -f"
echo "  重启前端:   docker compose restart frontend"
echo "  重启全部:   docker compose restart"
echo "  停止服务:   docker compose down"
echo "  查看状态:   docker compose ps"
echo ""