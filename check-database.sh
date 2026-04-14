#!/bin/bash

echo "🔍 顶流 TopFlow - 数据库诊断与验证工具"
echo "======================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# 步骤1：检查数据库文件
echo "📂 步骤1/6: 检查数据库文件..."
echo "----------------------------------------"

DB_FILE="./data/topflow.db"
CONTAINER_DB_PATH="/app/data/topflow.db"

if [ -f "$DB_FILE" ]; then
    FILE_SIZE=$(ls -lh "$DB_FILE" | awk '{print $5}')
    FILE_MOD=$(ls -l "$DB_FILE" | awk '{print $6, $7, $8}')
    print_success "本地数据库文件存在 ✓"
    print_info "文件路径: $(pwd)/data/topflow.db"
    print_info "文件大小: $FILE_SIZE"
    print_info "修改时间: $FILE_MOD"
else
    print_warning "本地数据库文件不存在！"
    print_info "这可能是正常的（如果数据在容器内）"
fi

# 步骤2：检查容器内数据库
echo ""
echo "🐳 步骤2/6: 检查容器内数据库..."
echo "----------------------------------------"

if docker ps | grep -q "topflow-backend"; then
    print_success "后端容器运行中 ✓"
    
    if docker exec topflow-backend test -f "$CONTAINER_DB_PATH" 2>/dev/null; then
        CONTAINER_SIZE=$(docker exec topflow-backend ls -lh "$CONTAINER_DB_PATH" | awk '{print $5}')
        print_success "容器内数据库存在 ✓ (大小: $CONTAINER_SIZE)"
        
        # 检查表是否存在
        TABLES=$(docker exec topflow-backend python3 -c "
import sqlite3
conn = sqlite3.connect('$CONTAINER_DB_PATH')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
tables = cursor.fetchall()
for t in tables:
    print(t[0])
conn.close()
" 2>/dev/null)
        
        if [ -n "$TABLES" ]; then
            print_success "数据库表结构正常 ✓"
            print_info "发现的表:"
            echo "$TABLES" | while read table; do
                echo "   📋 $table"
            done
        else
            print_error "数据库中没有找到任何表！"
        fi
    else
        print_error "容器内数据库文件不存在！"
        print_info "路径: $CONTAINER_DB_PATH"
    fi
else
    print_error "后端容器未运行！"
fi

# 步骤3：检查数据统计
echo ""
echo "📊 步骤3/6: 数据统计..."
echo "----------------------------------------"

if docker ps | grep -q "topflow-backend"; then
    STATS=$(docker exec topflow-backend python3 -c "
import sqlite3
conn = sqlite3.connect('$CONTAINER_DB_PATH')
cursor = conn.cursor()

# 用户统计
try:
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
except:
    user_count = 0

# 视频统计
try:
    cursor.execute('SELECT COUNT(*) FROM videos')
    video_count = cursor.fetchone()[0]
except:
    video_count = 0

# 日志统计
try:
    cursor.execute('SELECT COUNT(*) FROM operation_logs')
    log_count = cursor.fetchone()[0]
except:
    log_count = 0

print(f'{user_count},{video_count},{log_count}')
conn.close()
" 2>/dev/null)

    if [ -n "$STATS" ]; then
        IFS=',' read -r USER_COUNT VIDEO_COUNT LOG_COUNT <<< "$STATS"
        
        echo "👤 用户数量: $USER_COUNT"
        echo "🎬 视频数量: $VIDEO_COUNT"
        echo "📝 操作日志: $LOG_COUNT"
        
        if [ "$USER_COUNT" -gt 0 ] || [ "$VIDEO_COUNT" -gt 0 ]; then
            print_success "数据库中有数据 ✓"
        else
            print_warning "数据库为空（可能需要初始化或重新添加数据）"
        fi
    else
        print_error "无法读取数据统计"
    fi
fi

# 步骤4：查看用户列表
echo ""
echo "👥 步骤4/6: 用户列表详情..."
echo "----------------------------------------"

if docker ps | grep -q "topflow-backend"; then
    USERS=$(docker exec topflow-backend python3 -c "
import sqlite3
from datetime import datetime
conn = sqlite3.connect('$CONTAINER_DB_PATH')
cursor = conn.cursor()
cursor.execute('''SELECT id, username, email, role, is_active, created_at 
                 FROM users ORDER BY id''')
users = cursor.fetchall()
if users:
    for u in users:
        uid, uname, email, role, active, created = u
        status = '✅' if active == 1 else '❌'
        print(f'{uid}|{uname}|{email}|{role}|{status}|{created}')
else:
    print('NO_USERS')
conn.close()
" 2>/dev/null)

    if [ "$USERS" != "NO_USERS" ] && [ -n "$USERS" ]; then
        printf "%-5s %-15s %-25s %-10s %s %-20s\n" "ID" "用户名" "邮箱" "角色" "状态" "创建时间"
        echo "---------------------------------------------------------------------------------------------"
        echo "$USERS" | while IFS='|' read -r uid uname email role status created; do
            printf "%-5s %-15s %-25s %-10s %s %-20s\n" "$uid" "$uname" "$email" "$role" "$status" "${created:0:19}"
        done
    else
        print_warning "没有找到任何用户记录"
        print_info "需要先创建管理员账号"
    fi
fi

# 步骤5：查看视频列表
echo ""
echo "🎬 步骤5/6: 视频列表详情..."
echo "----------------------------------------"

if docker ps | grep -q "topflow-backend"; then
    VIDEOS=$(docker exec topflow-backend python3 -c "
import sqlite3
conn = sqlite3.connect('$CONTAINER_DB_PATH')
cursor = conn.cursor()
cursor.execute('''SELECT id, platform, influencer_name, region, status, play_count, created_at 
                 FROM videos ORDER BY id DESC LIMIT 10''')
videos = cursor.fetchall()
if videos:
    for v in videos:
        vid, platform, influencer, region, status, plays, created = v
        print(f'{vid}|{platform}|{influencer}|{region or \"N/A\"}|{status}|{plays or 0}|{created}')
else:
    print('NO_VIDEOS')
conn.close()
" 2>/dev/null)

    if [ "$VIDEOS" != "NO_VIDEOS" ] && [ -n "$VIDEOS" ]; then
        printf "%-5s %-10s %-20s %-8s %-12s %-10s %-20s\n" "ID" "平台" "达人名称" "地区" "状态" "播放量" "创建时间"
        echo "----------------------------------------------------------------------------------------------------"
        echo "$VIDEOS" | while IFS='|' read -r vid platform influencer region status plays created; do
            printf "%-5s %-10s %-20s %-8s %-12s %-10s %-20s\n" "$vid" "$platform" "$influencer" "$region" "$status" "$plays" "${created:0:19}"
        done
    else
        print_warning "没有找到任何视频记录"
        print_info "可以通过前端页面新增视频数据"
    fi
fi

# 步骤6：验证持久化配置
echo ""
echo "💾 步骤6/6: 数据持久化验证..."
echo "----------------------------------------"

# 检查volume挂载
VOLUME_INFO=$(docker inspect topflow-backend --format='{{range .Mounts}}{{.Source}} -> {{.Destination}} ({{.Type}}){{"\n"}}{{end}}' 2>/dev/null)

if [ -n "$VOLUME_INFO" ]; then
    print_success "Docker Volume挂载配置:"
    echo "$VOLUME_INFO" | while read line; do
        echo "   📁 $line"
    done
    
    # 检查data目录是否挂载
    if echo "$VOLUME_INFO" | grep -q "/app/data"; then
        print_success "数据库目录已正确挂载 ✓"
        print_info "数据将持久化到主机 ./data/ 目录"
    else
        print_error "数据库目录未挂载！数据可能丢失！"
    fi
else
    print_error "无法获取Volume信息"
fi

# 最终总结
echo ""
echo "=========================================="
echo -e "${YELLOW}📋 诊断总结${NC}"
echo "=========================================="
echo ""
echo "如果看到以下情况，说明数据库正常工作："
echo "  ✅ 容器内数据库文件存在"
echo "  ✅ 有用户和视频数据（如果之前创建过）"
echo "  ✅ /app/data 目录已挂载到主机"
echo ""
echo "常见问题及解决方案："
echo "----------------------------------------"
echo "1. 如果数据库为空 → 需要重新创建管理员账号和视频数据"
echo "2. 如果容器内无数据库 → 检查 models.py 是否使用正确的DATABASE_URL"
echo "3. 如果volume未挂载 → 修改 docker-compose.yml 并重建容器"
echo ""
echo "如何手动操作数据库："
echo "----------------------------------------"
echo "# 进入容器操作SQLite"
echo "docker exec -it topflow-backend sh"
echo "python3 -c \"import sqlite3; conn=sqlite3.connect('/app/data/topflow.db'); cursor=conn.cursor(); cursor.execute('SELECT * FROM users'); print(cursor.fetchall())\""
echo ""
echo "# 或者直接在主机上查看（如果有映射）"
echo "sqlite3 ./data/topflow.db 'SELECT * FROM users;'"
echo ""