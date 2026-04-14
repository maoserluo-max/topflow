import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Enum as SQLEnum, text
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
    projects = Column(String(200), default="Gamoji,Poseme,内容孵化")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    videos = relationship("Video", back_populates="creator")
    operation_logs = relationship("OperationLog", back_populates="user")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_code = Column(String(20), unique=True, index=True)
    project = Column(String(50), nullable=False, default="Gamoji")
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
    if url.startswith("sqlite:////"):
        data_dir = os.path.dirname(url.replace("sqlite:////", "/"))
        os.makedirs(data_dir, exist_ok=True)
        return url
    if url.startswith("sqlite:///./"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = url[len("sqlite:///./"):]
        abs_path = os.path.normpath(os.path.join(base_dir, '..', rel_path))
        data_dir = os.path.dirname(abs_path)
        os.makedirs(data_dir, exist_ok=True)
        return f"sqlite:///{abs_path}"
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        abs_path = url.replace("sqlite:///", "/")
        data_dir = os.path.dirname(abs_path)
        os.makedirs(data_dir, exist_ok=True)
        return url
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


def generate_video_code(db, region, content_direction, publish_date=None):
    region_part = (region or "XX").upper()[:2]
    direction_part = (content_direction or "XX").upper()[:2]

    if publish_date:
        if isinstance(publish_date, str):
            from datetime import datetime as _dt
            try:
                pd = _dt.strptime(publish_date[:10], "%Y-%m-%d")
            except ValueError:
                pd = _dt.now()
        else:
            pd = publish_date
        date_part = pd.strftime("%m%d")
    else:
        from datetime import datetime as _dt
        date_part = _dt.now().strftime("%m%d")

    prefix = f"{region_part}{direction_part}{date_part}"

    last_video = db.query(Video).filter(
        Video.video_code.like(f"{prefix}%")
    ).order_by(Video.id.desc()).first()

    if last_video and last_video.video_code:
        try:
            seq = int(last_video.video_code[-2:]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1

    return f"{prefix}{seq:02d}"


def init_db():
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(videos)"))
        existing_columns = {row[1] for row in result}
        if 'video_code' not in existing_columns:
            conn.execute(text("ALTER TABLE videos ADD COLUMN video_code VARCHAR(20)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_videos_video_code ON videos (video_code)"))
            conn.commit()
            print("✅ 已添加 video_code 列")
        if 'project' not in existing_columns:
            conn.execute(text("ALTER TABLE videos ADD COLUMN project VARCHAR(50) DEFAULT 'Gamoji'"))
            conn.commit()
            print("✅ 已添加 project 列")

        result = conn.execute(text("PRAGMA table_info(users)"))
        existing_columns = {row[1] for row in result}
        if 'projects' not in existing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN projects VARCHAR(200) DEFAULT 'Gamoji,Poseme,内容孵化'"))
            conn.commit()
            print("✅ 已添加 projects 列")

    print(f"✅ 数据库已初始化: {DATABASE_URL}")