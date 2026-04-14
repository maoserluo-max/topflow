#!/bin/bash

echo "🔧 顶流 TopFlow - 数据库持久化修复脚本"
echo "======================================"
echo ""
echo "本次修复："
echo "  ✅ 修复数据库路径配置（从环境变量读取）"
echo "  ✅ 确保数据存储到持久化目录 /app/data/"
echo "  ✅ 包含之前的所有功能优化"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 步骤1：验证关键文件
echo "📋 步骤1/6: 验证修复文件..."
errors=0

if [ ! -f "backend/models.py" ]; then
    print_error "缺少 backend/models.py"
    errors=$((errors + 1))
elif grep -q "get_database_url" backend/models.py && \
     grep -q "os.environ.get('DATABASE_URL')" backend/models.py; then
    print_success "models.py 已更新为动态读取DATABASE_URL ✓"
else
    print_error "models.py 版本不匹配！需要最新版本"
    errors=$((errors + 1))
fi

if [ ! -f "backend/routers/videos.py" ]; then
    print_error "缺少 backend/routers/videos.py"
    errors=$((errors + 1))
elif grep -q "sort_by.*Optional\[str\]" backend/routers/videos.py && \
     grep -q "VideoResponse.from_orm" backend/routers/videos.py; then
    print_success "videos.py 已支持排序和序列化 ✓"
else
    print_error "videos.py 版本不匹配！"
    errors=$((errors + 1))
fi

if [ ! -f "frontend/src/views/Videos.vue" ]; then
    print_error "缺少 frontend/src/views/Videos.vue"
    errors=$((errors + 1))
else
    print_success "Videos.vue 已准备就绪 ✓"
fi

if [ $errors -gt 0 ]; then
    print_error "发现 $errors 个文件问题！请确保所有文件已上传。"
    exit 1
fi

# 步骤2：备份数据库（如果存在）
echo ""
echo "💾 步骤2/6: 备份现有数据..."
if [ -d "./data" ] && [ -f "./data/topflow.db" ]; then
    BACKUP_NAME="topflow.db.backup.$(date +%Y%m%d_%H%M%S)"
    cp ./data/topflow.db "./data/$BACKUP_NAME"
    print_success "数据库已备份 ✓ ($BACKUP_NAME)"
else
    print_info "没有找到现有数据库，将创建新的"
fi

# 确保data目录存在
mkdir -p ./data
chmod 777 ./data

# 步骤3：停止并清理旧容器
echo ""
echo "🧹 步骤3/6: 清理旧容器..."
docker stop topflow-backend 2>/dev/null || true
docker rm topflow-backend 2>/dev/null || true
docker rmi topflow-backend 2>/dev/null || true
print_success "旧后端容器已清理 ✓"

# 步骤4：重建后端镜像
echo ""
echo "🔨 步骤4/6: 重建后端镜像..."
if docker compose build --no-cache backend; then
    print_success "后端镜像构建成功 ✓"
else
    print_error "后端镜像构建失败！"
    exit 1
fi

# 步骤5：启动服务
echo ""
echo "▶️  步骤5/6: 启动服务..."

# 先只启动后端，确保数据库初始化
docker compose up -d backend

if [ $? -eq 0 ]; then
    print_success "后端服务启动成功 ✓"
else
    print_error "后端服务启动失败！"
    exit 1
fi

# 等待数据库初始化
echo ""
echo "⏳ 等待数据库初始化（10秒）..."
sleep 10

# 检查数据库是否创建
if docker exec topflow-backend test -f "/app/data/topflow.db" 2>/dev/null; then
    DB_SIZE=$(docker exec topflow-backend ls -lh /app/data/topflow.db | awk '{print $5}')
    print_success "数据库文件已创建 ✓ (大小: $DB_SIZE)"
else
    print_error "数据库文件未创建！检查日志："
    docker logs topflow-backend --tail 20
    exit 1
fi

# 步骤6：验证数据持久化
echo ""
echo "✅ 步骤6/6: 验证配置..."

# 测试API
echo ""
echo "🧪 测试API接口..."

# 获取token
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))' 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$TOKEN" != "" ] && [ "$TOKEN" != "None" ]; then
    print_success "管理员登录成功 ✓ (admin/admin123)"
    
    # 测试视频列表
    VIDEO_RESP=$(curl -s "http://localhost:8000/api/videos/?page=1&page_size=10&sort_by=publish_date&sort_order=desc" \
      -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    
    if echo "$VIDEO_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('items' in d)" 2>/dev/null | grep -q "True"; then
        TOTAL=$(echo "$VIDEO_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total',0))")
        print_success "视频列表API正常 ✓ (总计: $TOTAL 条记录)"
    else
        print_warning "视频列表可能为空或API异常"
    fi
    
    # 测试用户列表
    USER_RESP=$(curl -s "http://localhost:8000/api/users/" \
      -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    
    if echo "$USER_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('items' in d)" 2>/dev/null | grep -q "True"; then
        USER_COUNT=$(echo "$USER_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('items',[])))")
        print_success "用户列表API正常 ✓ (用户数: $USER_COUNT)")
    else
        print_warning "无法获取用户列表"
    fi
else
    print_warning "admin账号不存在或密码错误"
    print_info "系统会自动创建初始管理员账号"
fi

# 检查volume挂载
VOLUME_CHECK=$(docker inspect topflow-backend --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' 2>/dev/null | grep "/app/data")
if [ -n "$VOLUME_CHECK" ]; then
    print_success "数据持久化Volume挂载正常 ✓"
    print_info "$VOLUME_CHECK"
else
    print_error "Volume挂载异常！数据可能不会持久化！"
fi

# 显示最终结果
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 数据库持久化修复完成！${NC}"
echo "=========================================="
echo ""
echo -e "🌐 访问地址: ${YELLOW}http://43.160.238.9${NC}"
echo -e "👤 默认账号: ${YELLOW}admin / admin123${NC}"
echo -e "📁 数据库位置: ${YELLOW}/opt/topflow/data/topflow.db${NC}"
echo ""
echo "📋 重要提示："
echo "----------------------------------------"
echo "1. 数据现在会持久化到主机 ./data/ 目录"
echo "2. 重建镜像不会丢失数据（只要不删除./data/目录）"
echo "3. 如果之前的数据丢失，需要重新添加"
echo ""
echo "如何验证数据是否正确保存："
echo "----------------------------------------"
echo "# 方法1: 使用诊断工具"
echo "chmod +x check-database.sh && ./check-database.sh"
echo ""
echo "# 方法2: 手动查看数据库文件"
echo "ls -lh ./data/topflow.db"
echo "sqlite3 ./data/topflow.db \"SELECT COUNT(*) FROM users;\""
echo "sqlite3 ./data/topflow.db \"SELECT COUNT(*) FROM videos;\""
echo ""
echo "# 方法3: 在浏览器中测试"
echo "- 登录 http://43.160.238.9"
echo "- 创建一个新用户"
echo "- 重启服务: docker compose restart"
echo "- 再次登录确认用户仍然存在"
echo ""
echo "常用命令："
echo "  查看日志: docker compose logs -f backend"
echo "  重启服务: docker compose restart"
echo "  备份数据: cp ./data/topflow.db ./data/topflow.db.backup"
echo "  诊断数据库: ./check-database.sh"
echo ""