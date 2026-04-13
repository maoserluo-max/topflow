# 顶流 TopFlow - 达人营销管理系统 Docker部署文档

## 📋 系统概述

**系统名称**: 顶流（TopFlow）达人营销管理系统  
**部署服务器**: 新加坡云服务器  
**公网IP**: 43.160.238.9  
**部署方式**: Docker容器化部署（推荐）  
**技术栈**: Python FastAPI + Vue3 + SQLite + Nginx

---

## 🐳 Docker架构说明

### 容器组成
```
┌─────────────────────────────────────────┐
│         Docker Compose 编排             │
├──────────────┬──────────────────────────┤
│   frontend   │       backend           │
│  (Nginx:80)  │ (FastAPI:8000)          │
│              │                          │
│  • 静态文件   │  • API服务               │
│  • 反向代理   │  • 数据爬取              │
│  • SSL终端    │  • JWT认证               │
└──────────────┴──────────────────────────┘
                    │
              ┌─────┴─────┐
              │  data/    │
              │ topflow.db│
              └───────────┘
```

### 核心优势
- ✅ **一键部署**: `docker-compose up -d` 即可启动全部服务
- ✅ **环境隔离**: 每个服务独立容器，互不影响
- ✅ **易于迁移**: 打包镜像即可在任何Docker环境运行
- ✅ **自动重启**: 容器崩溃自动恢复
- ✅ **版本管理**: 镜像标签化管理

---

## 📁 项目结构（Docker相关）

```
f:\trae\dome1\
├── Dockerfile.backend        # 后端容器构建文件
├── Dockerfile.frontend       # 前端容器构建文件（多阶段）
├── docker-compose.yml        # 服务编排配置
├── .dockerignore             # Docker构建忽略文件
├── .env.example              # 环境变量模板
├── deploy.sh                 # 一键部署脚本
├── docker/
│   └── nginx.conf            # Nginx反向代理配置
├── backend/                  # 后端代码
├── frontend/                 # 前端代码
├── data/                     # 数据目录（自动创建）
└── ssl/                      # SSL证书目录（可选）
```

---

## 🚀 快速部署指南（3步完成）

### 前置要求

确保服务器已安装：
- **Docker**: 20.10+
- **Docker Compose**: 2.0+ 或 docker-compose V1.29+

### 步骤一：安装Docker（如果未安装）

```bash
# Ubuntu/Debian 系统
# 1. 更新包索引
sudo apt update

# 2. 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 3. 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. 添加Docker仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. 启动Docker并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker

# 7. 将当前用户添加到docker组（避免每次使用sudo）
sudo usermod -aG docker $USER
# 重新登录或执行: newgrp docker

# 8. 验证安装
docker --version
docker compose version
```

**CentOS/RHEL系统**:
```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
```

### 步骤二：上传项目到服务器

#### 方法A：使用Git克隆（推荐）

```bash
# 在本地项目目录（假设你已推送到GitHub/GitLab）
cd f:\trae\dome1

# 初始化Git仓库（如果还没有）
git init
git add .
git commit -m "Initial commit: TopFlow with Docker support"

# 推送到远程仓库
git remote add origin <你的GitHub/GitLab仓库地址>
git push -u origin main

# SSH登录到服务器
ssh root@43.160.238.9

# 克隆项目到/opt/topflow
cd /opt
git clone <你的仓库地址> topflow
cd topflow
```

#### 方法B：使用SCP直接上传（适合小项目）

```bash
# 在本地Windows PowerShell中执行
scp -r f:\trae\dome1\* root@43.160.238.9:/opt/topflow/

# SSH登录服务器
ssh root@43.160.238.9
cd /opt/topflow
```

#### 方法C：打包上传

```bash
# 本地打包（排除不需要的文件）
cd f:\trae\dome1
tar --exclude='.venv' --exclude='node_modules' --exclude='__pycache__' --exclude='.git' -czvf topflow.tar.gz .

# 上传到服务器
scp topflow.tar.gz root@43.160.238.9:/opt/

# SSH登录并解压
ssh root@43.160.238.9
cd /opt
mkdir -p topflow
cd topflow
tar -xzvf ../topflow.tar.gz
rm ../topflow.tar.gz
```

### 步骤三：配置并启动服务

#### 方式A：使用一键脚本（最简单）

```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行部署脚本
./deploy.sh
```

脚本会自动完成：
- ✅ 检查Docker环境
- ✅ 创建必要目录
- ✅ 复制环境变量模板
- ✅ 构建Docker镜像
- ✅ 启动所有服务
- ✅ 显示访问信息

#### 方式B：手动部署（推荐理解原理）

```bash
# 1. 进入项目目录
cd /opt/topflow

# 2. 创建必要的数据和SSL目录
mkdir -p data ssl

# 3. 配置环境变量
cp .env.example .env
nano .env  # 编辑.env文件，修改SECRET_KEY！

# 4. 构建Docker镜像（首次需要下载基础镜像，约5-10分钟）
docker compose build --no-cache

# 5. 启动所有服务（后台运行）
docker compose up -d

# 6. 查看服务状态
docker compose ps

# 7. 查看启动日志（确认无错误）
docker compose logs -f
```

---

## ⚙️ 环境变量配置详解

编辑 `.env` 文件：

```bash
# 必须修改！JWT签名密钥（用于Token加密）
# 生成方法: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=你的随机32字节十六进制字符串

# 数据库路径（SQLite）
DATABASE_URL=sqlite:///./data/topflow.db

# CORS允许的前端来源（根据实际情况调整）
CORS_ORIGINS=["http://43.160.238.9","http://localhost:3000","http://127.0.0.1:5173"]

# Token过期时间（分钟），1440 = 24小时
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**重要提示**：
- 🔒 **必须修改 SECRET_KEY**，否则存在安全风险
- 📍 **CORS_ORIGINS** 要包含你的实际访问域名/IP
- ⏰ 生产环境建议将 ACCESS_TOKEN_EXPIRE_MINUTES 设为更短时间（如60）

---

## 🔧 常用运维命令

### 服务管理

```bash
# 查看所有容器状态
docker compose ps

# 查看实时日志（所有服务）
docker compose logs -f

# 仅查看后端日志
docker compose logs -f backend

# 仅查看前端日志
docker compose logs -f frontend

# 重启某个服务
docker compose restart backend

# 重启所有服务
docker compose restart

# 停止所有服务
docker compose down

# 停止并删除数据卷（⚠️ 会删除数据库！）
docker compose down -v

# 重新构建并启动（代码更新后使用）
docker compose up -d --build

# 强制重建（清除缓存）
docker compose build --no-cache && docker compose up -d
```

### 数据管理

```bash
# 进入后端容器（调试用）
docker compose exec backend bash

# 进入数据库目录查看
ls -lh data/

# 手动备份数据库
cp data/topflow.db data/topflow_backup_$(date +%Y%m%d).db

# 从备份恢复
cp data/topflow_backup_20240101.db data/topflow.db
docker compose restart backend
```

### 资源监控

```bash
# 查看容器资源占用
docker stats

# 查看磁盘占用
docker system df

# 清理未使用的镜像（释放空间）
docker image prune -a

# 清理所有未使用资源
docker system prune -a
```

---

## 🔄 版本更新流程

当有新代码需要更新时：

```bash
# 方法1：如果是Git管理的项目
cd /opt/topflow
git pull origin main
docker compose up -d --build

# 方法2：手动更新文件后重新构建
# 1. 上传新文件到服务器覆盖旧文件
# 2. 重新构建
docker compose up -d --build

# 方法3：完全重建（清理缓存）
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 🔒 SSL证书配置（HTTPS）

### 使用Let's Encrypt免费证书

```bash
# 1. 安装Certbot
sudo apt install -y certbot

# 2. 申请证书（确保80端口未被占用，先停掉Nginx容器）
docker compose stop frontend
sudo certbot certonly --standalone -d 43.160.238.9

# 3. 复制证书到ssl目录
sudo cp /etc/letsencrypt/live/43.160.238.9/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/43.160.238.9/privkey.pem ssl/key.pem
sudo chmod 644 ssl/*.pem

# 4. 取消注释docker/nginx.conf中的HTTPS配置
nano docker/nginx.conf
# 将第56-66行的注释取消

# 5. 修改docker-compose.yml，添加443端口映射
# （已经包含443端口映射）

# 6. 重新启动前端容器
docker compose up -d frontend
```

### 自动续期（推荐）

创建定时任务：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每月1号凌晨3点检查续期）
0 3 1 * * cd /opt/topflow && docker compose stop frontend && sudo certbot renew --quiet && sudo cp /etc/letsencrypt/live/43.160.238.9/fullchain.pem ssl/cert.pem && sudo cp /etc/letsencrypt/live/43.160.238.9/privkey.pem ssl/key.pem && docker compose up -d frontend >> /var/log/certbot-renew.log 2>&1
```

---

## 🛠️ 故障排查

### 问题1：容器无法启动

```bash
# 查看详细错误日志
docker compose logs backend
docker compose logs frontend

# 检查端口是否被占用
lsof -i :80
lsof -i :8000

# 检查Docker是否正常运行
systemctl status docker
docker info
```

### 问题2：数据库连接失败

```bash
# 检查data目录是否存在且可写
ls -la data/
chmod 755 data/

# 检查环境变量是否正确加载
docker compose config | grep DATABASE_URL

# 手动测试数据库创建
docker compose run --rm backend python -c "from backend.models import init_db; init_db(); print('DB OK')"
```

### 问题3：前端页面空白或API请求失败

```bash
# 检查Nginx配置
docker compose exec frontend cat /etc/nginx/conf.d/default.conf

# 测试API连通性
curl http://localhost:8000/api/health

# 检查CORS配置
docker compose exec backend env | grep CORS

# 查看浏览器控制台的网络请求（F12开发者工具）
```

### 问题4：内存不足（OOM Killed）

```bash
# 查看容器退出原因
docker inspect topflow-backend | grep -A 5 State

# 增加swap空间（临时方案）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 优化Docker资源限制（在docker-compose.yml中添加）
# services:
#   backend:
#     deploy:
#       resources:
#         limits:
#           memory: 512M
```

### 问题5：爬虫功能异常（网络问题）

```bash
# 检查网络连通性
docker compose exec backend curl -I https://www.tiktok.com

# 如果需要代理（修改docker-compose.yml添加环境变量）
# environment:
#   - HTTP_PROXY=http://your-proxy:port
#   - HTTPS_PROXY=http://your-proxy:port
```

---

## 📊 性能优化建议

### 1. 资源限制配置

在 `docker-compose.yml` 中为backend服务添加：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

### 2. 日志管理

防止日志文件过大：

```yaml
services:
  backend:
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "3"
  
  frontend:
    logging:
      driver: json-file
      options:
        max-size: "20m"
        max-file: "3"
```

### 3. 数据库备份自动化

创建备份脚本 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/topflow/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
docker compose exec backend cp /app/data/topflow.db /tmp/topflow_$DATE.db
docker cp topflow-backend:/tmp/topflow_$DATE.db $BACKUP_DIR/

# 保留最近30天的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "[$(date)] Backup completed: topflow_$DATE.db" >> $BACKUP_DIR/backup.log
```

设置定时任务：

```bash
chmod +x backup.sh
crontab -e
# 添加：每天凌晨3点备份
0 3 * * * /opt/topflow/backup.sh
```

---

## 🔐 安全加固清单

- [ ] ✅ 修改 `.env` 中的 `SECRET_KEY` 为强随机值
- [ ] ✅ 修改默认管理员密码（admin/admin123）
- [ ] ✅ 配置防火墙，仅开放80/443端口
  ```bash
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```
- [ ] ✅ 配置SSL证书（HTTPS）
- [ ] ✅ 定期更新系统和Docker镜像
  ```bash
  sudo apt update && sudo apt upgrade -y
  docker compose pull  # 如果使用预构建镜像
  docker compose up -d --build
  ```
- [ ] ✅ 设置定期数据库备份
- [ ] ✅ 禁用不必要的Docker API暴露（默认仅本地访问）
- [ ] ✅ 监控容器资源使用情况

---

## 📈 扩展方案

### 升级到PostgreSQL（高并发场景）

修改 `docker-compose.yml`，添加数据库服务：

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: topflow-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: topflow
      POSTGRES_USER: topflow_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - topflow-network
  
  backend:
    # ... 其他配置
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://topflow_user:${DB_PASSWORD:-changeme}@db:5432/topflow

volumes:
  postgres_data:
```

### 添加Redis缓存

```yaml
  redis:
    image: redis:7-alpine
    container_name: topflow-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - topflow-network
```

---

## ✅ 部署验证清单

完成部署后，请逐项检查：

- [ ] Docker服务正常运行
  ```bash
  docker compose ps
  # 应显示: Up (healthy) 或 Up
  ```

- [ ] 后端API可访问
  ```bash
  curl http://localhost:8000/
  # 应返回JSON: {"name":"顶流 TopFlow...","status":"running"}
  ```

- [ ] 前端页面可访问
  ```bash
  curl -I http://43.160.238.9
  # 应返回 HTTP/1.1 200 OK
  ```

- [ ] 可以通过浏览器访问系统
  - 打开浏览器访问: http://43.160.238.9
  - 看到登录页面

- [ ] 登录功能正常
  - 用户名: admin
  - 密码: admin123
  - 登录成功后跳转到仪表盘

- [ ] 各功能模块正常工作
  - [ ] 仪表盘数据显示正确
  - [ ] 视频管理CRUD操作正常
  - [ ] 视频元数据抓取功能可用
  - [ ] 用户管理功能正常（admin账号可见）
  - [ ] 操作日志记录正常

- [ ] 已修改默认密码和SECRET_KEY
- [ ] 数据库备份策略已设置
- [ ] SSL证书已配置（如需HTTPS）

---

## 📞 技术支持与参考

### 有用的命令速查

| 操作 | 命令 |
|------|------|
| 查看所有容器 | `docker ps -a` |
| 查看镜像列表 | `docker images` |
| 查看容器日志 | `docker logs -f <容器名>` |
| 进入容器内部 | `docker exec -it <容器名> bash` |
| 复制文件到容器 | `docker cp local_file <容器名>:/path/` |
| 从容器复制文件 | `docker cp <容器名>:/path/file local` |
| 查看容器详情 | `docker inspect <容器名>` |

### 官方文档

- **Docker**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Vue3**: https://vuejs.org/
- **Nginx**: https://nginx.org/en/docs/
- **Element Plus**: https://element-plus.org/

---

## 🎉 总结

恭喜！你已经完成了"顶流"TopFlow系统的Docker容器化部署。

**核心优势回顾**：
- ✅ 一键部署，简单高效
- ✅ 环境一致，避免"在我机器上能跑"的问题
- ✅ 易于扩展和维护
- ✅ 生产级可靠性

**下一步建议**：
1. 立即修改默认密码和SECRET_KEY
2. 配置SSL证书启用HTTPS
3. 设置定期数据库备份
4. 监控系统运行状态
5. 根据实际使用情况优化资源配置

祝使用愉快！如有问题，请查阅本文档的故障排查章节或参考官方文档。

---

**部署完成后访问信息**：
- 🌐 **前端界面**: http://43.160.238.9（或 https://43.160.238.9 如配置SSL）
- 📚 **API文档**: http://43.160.238.9/docs（开发阶段，生产环境建议关闭）
- 👤 **默认账号**: admin / admin123（⚠️ 请立即修改！）
- 📂 **数据位置**: ./data/topflow.db
- 📝 **日志位置**: `docker compose logs -f`