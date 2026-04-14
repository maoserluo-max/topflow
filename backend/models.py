import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    videos = relationship("Video", back_populates="creator")
    operation_logs = relationship("OperationLog", back_populates="user")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False)
    region = Column(String(50))
    content_direction = Column(String(100))
    influencer_name = Column(String(100), nullable=False)
    price_usd = Column(Float)
    title = Column(Text)
    publish_date = Column(DateTime)
    play_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    video_url = Column(String(500))
    contact_person = Column(String(50))
    contact_email = Column(String(100))
    contact_whatsapp = Column(String(30))
    creator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="pending_review")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    creator = relationship("User", back_populates="videos")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)
    module = Column(String(50))
    detail = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="operation_logs")


def get_database_url():
    from config import settings
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///./"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = url[len("sqlite:///./"):]
        abs_path = os.path.normpath(os.path.join(base_dir, '..', rel_path))
        data_dir = os.path.dirname(abs_path)
        os.makedirs(data_dir, exist_ok=True)
        return f"sqlite:///{abs_path}"
    return url


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库已初始化: {DATABASE_URL}")