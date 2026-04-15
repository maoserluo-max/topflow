from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from models import init_db
from routers import auth, videos, admin, cookies


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 正在初始化数据库...")
    init_db()
    verify_database_location()
    create_default_admin()
    print("✅ 系统启动完成！")
    yield


def verify_database_location():
    from models import DATABASE_URL
    import os
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "/")
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✅ 数据库文件: {db_path} (大小: {size} bytes)")
        else:
            print(f"⚠️  数据库文件不存在: {db_path} (将在首次写入时创建)")
        mount_check = os.stat(os.path.dirname(db_path) or "/app/data")
        print(f"📂 数据目录: {os.path.dirname(db_path) or '/app/data'}")


def create_default_admin():
    from models import SessionLocal, User, UserRole
    from auth import get_password_hash
    
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            admin_user = User(
                username="admin",
                email="admin@topflow.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ 默认管理员账号已创建: admin / admin123")
    finally:
        db.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(admin.router)
app.include_router(cookies.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    from datetime import datetime, timezone
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/crawler-diagnose")
def crawler_diagnose():
    import yt_dlp
    import platform
    result = {
        "yt_dlp_version": yt_dlp.version.__version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }

    test_url = 'https://www.youtube.com/shorts/U9QPM3C9n7g'
    clients_to_test = [
        ('android', {
            'quiet': True, 'no_warnings': True, 'skip_download': True,
            'nocheckcertificate': True, 'socket_timeout': 15, 'format': 'worst',
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }),
        ('ios', {
            'quiet': True, 'no_warnings': True, 'skip_download': True,
            'nocheckcertificate': True, 'socket_timeout': 15, 'format': 'worst',
            'extractor_args': {'youtube': {'player_client': ['ios']}},
        }),
        ('default', {
            'quiet': True, 'no_warnings': True, 'skip_download': True,
            'nocheckcertificate': True, 'socket_timeout': 15, 'format': 'worst',
        }),
    ]

    for client_name, opts in clients_to_test:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
            result[f"test_{client_name}"] = {
                "result": "success",
                "title": info.get('title', ''),
                "uploader": info.get('uploader', ''),
                "view_count": info.get('view_count', 0),
            }
            break
        except Exception as e:
            result[f"test_{client_name}"] = {
                "result": "failed",
                "error": str(e)[:300],
            }

    return result