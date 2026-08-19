# 顶流 TopFlow

顶流 TopFlow 是一个面向达人营销、短视频投放线索和达人资源管理的后台系统。`newui` 分支为 2.0.0 版本，提供新版前端界面、视频数据管理、用户组织管理、邀请码注册、平台 Cookies 管理、操作日志和 Docker 部署能力。

## 功能特性

- 新版管理后台：基于 Vue 3、Element Plus 和 Tailwind CSS 构建，支持亮色/暗色主题。
- 视频数据管理：支持视频新增、编辑、删除、查询、导入、导出和视频编号生成。
- 达人营销字段：支持项目、平台、地区、内容方向、视频类型、达人名称、报价、标题、播放量、点赞量、评论量、分享量和联系方式。
- 视频元数据抓取：集成 `yt-dlp`，可用于抓取 YouTube、TikTok、Instagram 等平台的视频信息。
- 用户与权限：支持 `admin`、`leader`、`user` 三级角色，以及上下级组织关系。
- 项目权限：内置 `Gamoji`、`Poseme`、`内容孵化` 等项目字段，可按用户分配项目范围。
- 邀请码注册：用户注册需要邀请码，邀请码可指定注册角色和项目权限。
- 平台 Cookies 管理：支持为 YouTube、TikTok、Instagram 保存 Cookies，并提供个人 Cookies 与管理员 Cookies 兜底机制。
- 操作日志：记录用户登录、注册、用户管理、邀请码生成等后台操作，支持查询和导出。
- 数据看板：提供仪表盘页面，用于展示系统概览和业务数据。
- 容器化部署：提供后端、前端、Nginx、数据卷和健康检查配置。

## 技术栈

后端：

- FastAPI
- SQLAlchemy
- Pydantic / Pydantic Settings
- SQLite
- python-jose
- passlib / bcrypt
- yt-dlp
- Deno

前端：

- Vue 3
- Vite
- Vue Router
- Pinia
- Element Plus
- Tailwind CSS
- Axios
- ECharts / vue-echarts
- Day.js

部署：

- Docker
- Docker Compose
- Nginx

## 页面模块

前端主要页面包括：

- `/login`：登录页
- `/register`：邀请码注册页
- `/dashboard`：仪表盘
- `/videos`：视频管理
- `/users`：用户管理，仅 `admin` 和 `leader` 可访问
- `/logs`：操作日志，仅 `admin` 可访问

主要组件包括：

- `VideoFormDialog`：视频表单弹窗
- `UserFormDialog`：用户表单弹窗
- `UserTreeNode`：用户组织树节点
- `InviteCodesDialog`：邀请码管理弹窗
- `CookiesDialog`：平台 Cookies 管理弹窗
- `ProfileDialog`：个人资料弹窗
- `Pagination`：分页组件

## 项目结构

```text
topflow/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 系统配置
│   ├── models.py            # 数据库模型与初始化迁移
│   ├── schemas.py           # 接口数据结构与字段校验
│   ├── auth.py              # 登录认证、密码加密、权限依赖
│   └── routers/
│       ├── auth.py          # 登录、注册、用户管理、邀请码
│       ├── videos.py        # 视频管理、导入导出、元数据抓取
│       ├── admin.py         # 系统统计、操作日志
│       └── cookies.py       # 平台 Cookies 管理
├── frontend/
│   ├── src/
│   │   ├── components/      # 业务组件
│   │   ├── layouts/         # 后台主布局
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 前端路由
│   │   ├── stores/          # 用户与主题状态
│   │   └── utils/           # API 请求封装
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── docker/
│   └── nginx.conf
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── crawler.py
└── .env.example
```

## 快速开始

### 1. 准备环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

生产环境请务必修改 `SECRET_KEY`：

```env
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:5173"]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Docker 部署时，数据库默认使用：

```env
DATABASE_URL=sqlite:////app/data/topflow.db
```

### 2. 使用 Docker Compose 启动

```bash
docker compose up -d --build
```

启动后访问：

- 前端后台：`http://localhost`
- 后端服务：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

### 3. 默认管理员账号

系统首次启动会自动创建默认管理员：

```text
用户名：admin
密码：admin123
```

上线后请立即修改默认密码。

## 本地开发

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Windows PowerShell：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

本地开发时建议显式设置数据库地址，例如：

```env
DATABASE_URL=sqlite:///./data/topflow.db
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务通常运行在：

```text
http://localhost:5173
```

前端 API 基础路径为 `/api`，开发或部署时需要将 `/api` 代理到后端服务。

## 核心数据模型

### User

用户模型用于记录后台账号，包含用户名、邮箱、姓名、角色、上级用户、启用状态、可访问项目、创建时间和更新时间。

角色包括：

- `admin`：管理员
- `leader`：组长
- `user`：普通用户

### Video

视频模型用于记录达人营销视频数据，核心字段包括：

- `video_code`：视频编号
- `project`：所属项目
- `platform`：平台，支持 `youtube`、`tiktok`、`ins`
- `region`：地区
- `content_direction`：内容方向
- `video_types`：视频类型
- `influencer_name`：达人名称
- `price_usd`：美元报价
- `title`：视频标题
- `publish_date`：发布时间
- `play_count`、`like_count`、`comment_count`、`share_count`：互动数据
- `video_url`：视频链接
- `contact_person`、`contact_email`、`contact_whatsapp`：联系人信息
- `status`：业务状态
- `stats_updated_at`：数据更新时间

### InviteCode

邀请码模型用于控制注册入口。邀请码可设置可访问项目和注册后的角色，并记录创建人、使用人和使用时间。

### PlatformCookies

平台 Cookies 模型用于保存不同平台的访问凭据，支持 `youtube`、`tiktok`、`ins`。

### OperationLog

操作日志模型用于记录后台用户行为，包括用户、操作动作、模块、详情、IP 地址和创建时间。

## API 概览

启动后可通过 FastAPI 自动文档查看完整接口：

```text
http://localhost:8000/docs
```

主要接口模块：

- `GET /`：服务基础信息
- `GET /api/health`：服务健康检查
- `GET /api/crawler-diagnose`：采集能力诊断
- `/api/auth/*`：注册、登录、当前用户、个人资料、用户管理、邀请码管理
- `/api/videos/*`：视频编号、视频增删改查、导入、导出、元数据抓取
- `/api/cookies/*`：平台 Cookies 查看、保存、清除和有效 Cookies 查询
- `/api/admin/*`：系统统计、操作日志查询、日志导出

## 部署说明

`docker-compose.yml` 包含两个服务：

- `backend`：FastAPI 后端，默认暴露 `8000` 端口。
- `frontend`：Nginx 前端服务，默认暴露 `80` 和 `443` 端口。

数据持久化使用 Docker volume：

```text
topflow-data:/app/data
```

Nginx 会将 `/api/` 请求代理到后端服务，并支持较长请求超时，便于视频元数据抓取和导入导出等操作。

常用命令：

```bash
docker compose up -d --build
docker compose logs -f
docker compose down
```

## 安全建议

- 首次部署后立即修改默认管理员密码。
- 生产环境必须替换 `SECRET_KEY`。
- `CORS_ORIGINS` 只保留真实域名，不建议使用过宽配置。
- 不要提交 `.env`、数据库文件、SSL 证书和真实 Cookies。
- Cookies 具有敏感性，建议只在可信环境中保存和使用。
- 对公网开放前建议启用 HTTPS、访问控制和定期备份。

## 仓库维护说明

`newui` 分支当前包含 `frontend/dist` 和 `frontend/node_modules` 等构建产物/依赖目录，仓库体积会比较大。后续维护时建议以 `frontend/package.json` 为准安装依赖并重新构建，避免依赖仓库内已提交的 `node_modules`。

## 许可证

当前仓库未看到明确的开源许可证文件。使用、分发或商用前，请先与项目维护者确认授权范围。
