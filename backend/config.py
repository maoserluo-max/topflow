import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "顶流 TopFlow - 达人营销管理系统"
    APP_VERSION: str = "1.0.0"
    
    DATABASE_URL: str = "sqlite:///./topflow.db"
    SECRET_KEY: str = "your-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://43.160.238.9:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()