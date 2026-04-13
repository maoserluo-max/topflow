#!/bin/bash

echo "🚀 顶流 TopFlow - 快速重建脚本"
echo "============================"
echo ""

# 清理旧容器
echo "📦 清理旧容器..."
docker stop topflow-backend topflow-frontend 2>/dev/null || true
docker rm topflow-backend topflow-frontend 2>/dev/null || true

# 仅重建后端（前端通常没问题）
echo "🔨 重新构建后端镜像..."
docker compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 后端构建成功！启动服务..."
    docker compose up -d
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 15
    
    echo ""
    echo "📊 服务状态："
    docker compose ps
    
    echo ""
    echo "🌐 访问地址: http://43.160.238.9"
    echo "👤 账号: admin / admin123"
else
    echo ""
    echo "❌ 构建失败！请检查错误信息"
    exit 1
fi