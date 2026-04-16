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
    LEADER = "leader"
    USER = "user"


# 角色层级：数值越大权限越高
ROLE_HIERARCHY = {
    UserRole.ADMIN: 3,
    UserRole.LEADER: 2,
    UserRole.USER: 1,
}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    projects = Column(String(200), default="Gamoji,Poseme,内容孵化")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    videos = relationship("Video", back_populates="creator")
    operation_logs = relationship("OperationLog", back_populates="user")
    parent = relationship("User", remote_side=[id], foreign_keys=[parent_id], backref="children")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_code = Column(String(20), unique=True, index=True)
    project = Column(String(50), nullable=False, default="Gamoji")
    platform = Column(String(20), nullable=False)
    region = Column(String(50))
    content_direction = Column(String(100))
    video_types = Column(String(200))
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
    stats_updated_at = Column(DateTime, nullable=True)
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


class PlatformCookies(Base):
    __tablename__ = "platform_cookies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(20), nullable=False)
    content = Column(Text, default="")
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User")


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    projects = Column(String(200))
    register_role = Column(String(20), default="leader")
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)

    creator = relationship("User", foreign_keys=[created_by])
    used_user = relationship("User", foreign_keys=[used_by])


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
        if 'video_types' not in existing_columns:
            conn.execute(text("ALTER TABLE videos ADD COLUMN video_types VARCHAR(200)"))
            conn.commit()
            print("✅ 已添加 video_types 列")
        if 'stats_updated_at' not in existing_columns:
            conn.execute(text("ALTER TABLE videos ADD COLUMN stats_updated_at DATETIME"))
            conn.commit()
            print("✅ 已添加 stats_updated_at 列")

        result = conn.execute(text("PRAGMA table_info(users)"))
        existing_columns = {row[1] for row in result}
        if 'projects' not in existing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN projects VARCHAR(200) DEFAULT 'Gamoji,Poseme,内容孵化'"))
            conn.commit()
            print("✅ 已添加 projects 列")
        if 'parent_id' not in existing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN parent_id INTEGER REFERENCES users(id)"))
            conn.commit()
            print("✅ 已添加 parent_id 列")

        # 迁移旧角色：super_admin -> admin，manager -> leader
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'super_admin'"))
        super_admin_count = result.fetchone()[0]
        if super_admin_count > 0:
            conn.execute(text("UPDATE users SET role = 'admin' WHERE role = 'super_admin'"))
            conn.commit()
            print("✅ 已迁移 super_admin 角色到 admin")
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'manager'"))
        manager_count = result.fetchone()[0]
        if manager_count > 0:
            conn.execute(text("UPDATE users SET role = 'leader' WHERE role = 'manager'"))
            conn.commit()
            print("✅ 已迁移 manager 角色到 leader")

        # 新角色体系迁移：确保角色体系正确
        # 普通用户(user)保持为普通用户，不再自动提升
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'user'"))
        user_count = result.fetchone()[0]
        if user_count > 0:
            print(f"ℹ️ 当前有 {user_count} 个普通用户")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='invite_codes'"))
        if not result.fetchone():
            conn.execute(text("""
                CREATE TABLE invite_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(20) NOT NULL UNIQUE,
                    created_by INTEGER NOT NULL REFERENCES users(id),
                    used_by INTEGER REFERENCES users(id),
                    used_at DATETIME,
                    is_used BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_invite_codes_code ON invite_codes (code)"))
            conn.commit()
            print("✅ 已创建 invite_codes 表")

    # 邀请码表新增字段
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(invite_codes)"))
        existing_columns = {row[1] for row in result}
        if 'projects' not in existing_columns:
            conn.execute(text("ALTER TABLE invite_codes ADD COLUMN projects VARCHAR(200)"))
            conn.commit()
            print("✅ 已添加 invite_codes.projects 列")
        if 'register_role' not in existing_columns:
            conn.execute(text("ALTER TABLE invite_codes ADD COLUMN register_role VARCHAR(20) DEFAULT 'user'"))
            conn.commit()
            print("✅ 已添加 invite_codes.register_role 列")

    print(f"✅ 数据库已初始化: {DATABASE_URL}")