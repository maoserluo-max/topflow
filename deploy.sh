#!/bin/bash

echo "🚀 顶流 TopFlow - Docker一键部署脚本"
echo "======================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：Docker未安装，请先安装Docker"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误：Docker Compose未安装"
    echo "安装指南: https://docs.docker.com/compose/install/"
    exit 1
fi

# 创建必要目录
echo "📁 创建数据目录..."
mkdir -p data ssl

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，从模板创建..."
    cp .env.example .env
    echo ""
    echo "⚠️  重要：请编辑 .env 文件，修改 SECRET_KEY 为随机密钥！"
    echo "   生成命令: python3 -c \"import secrets; print(secrets.token_hex(32))\""
    echo ""
    read -p "按回车键继续..." 
fi

# 构建并启动服务
echo ""
echo "🏗️  构建Docker镜像..."
docker-compose build --no-cache

echo ""
echo "▶️  启动服务..."
docker-compose up -d

echo ""
echo "✅ 部署完成！"
echo ""
echo "=========================================="
echo "📊 服务状态:"
docker-compose ps
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://43.160.238.9"
echo "   API文档: http://43.160.238.9/docs (开发阶段)"
echo ""
echo "👤 默认账号:"
echo "   用户名: admin"
echo "   密码: admin123"
echo "=========================================="
echo ""
echo "📝 常用命令:"
echo "   查看日志:     docker-compose logs -f"
echo "   停止服务:     docker-compose down"
echo "   重启服务:     docker-compose restart"
echo "   重新构建:     docker-compose up -d --build"
echo ""