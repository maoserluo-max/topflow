from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from models import init_db
from routers import auth, videos, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 正在初始化数据库...")
    init_db()
    create_default_admin()
    print("✅ 系统启动完成！")
    yield


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
    return {"status": "healthy", "timestamp": "2026-04-13T12:00:00Z"}