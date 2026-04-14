import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "顶流 TopFlow - 达人营销管理系统"
    APP_VERSION: str = "1.0.0"
    
    DATABASE_URL: str = "sqlite:///./data/topflow.db"
    SECRET_KEY: str = "topflow-secret-key-2024-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://43.160.238.9:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()

if len(settings.SECRET_KEY) > 72:
    print(f"⚠️  WARNING: SECRET_KEY过长({len(settings.SECRET_KEY)}字符)，已自动截断至72字符")
    settings.SECRET_KEY = settings.SECRET_KEY[:72]