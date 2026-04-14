import re
import enum
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class PlatformEnum(str, enum.Enum):
    tiktok = "tiktok"
    ins = "ins"
    youtube = "youtube"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('用户名至少3个字符')
        if len(v) > 50:
            raise ValueError('用户名不能超过50个字符')
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少6个字符')
        if len(v) > 72:
            raise ValueError('密码不能超过72个字符')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None:
            valid_roles = ['admin', 'manager', 'user']
            if v not in valid_roles:
                raise ValueError(f'无效的角色，可选值: {", ".join(valid_roles)}')
        return v


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


class VideoBase(BaseModel):
    platform: str
    region: Optional[str] = None
    content_direction: Optional[str] = None
    influencer_name: str
    price_usd: Optional[float] = None
    title: Optional[str] = None
    publish_date: Optional[datetime] = None
    play_count: Optional[int] = 0
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    share_count: Optional[int] = 0
    video_url: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_whatsapp: Optional[str] = None
    status: Optional[str] = "pending"

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v):
        valid_platforms = [e.value for e in PlatformEnum]
        if v not in valid_platforms:
            raise ValueError(f'无效的平台，可选值: {", ".join(valid_platforms)}')
        return v

    @field_validator('influencer_name')
    @classmethod
    def validate_influencer_name(cls, v):
        if not v or not v.strip():
            raise ValueError('达人名称不能为空')
        if len(v.strip()) > 100:
            raise ValueError('达人名称不能超过100个字符')
        return v.strip()

    @field_validator('price_usd')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['pending', 'approved', 'rejected', 'published']
            if v not in valid_statuses:
                raise ValueError(f'无效的状态，可选值: {", ".join(valid_statuses)}')
        return v


class VideoCreate(VideoBase):
    pass


class VideoUpdate(BaseModel):
    platform: Optional[str] = None
    region: Optional[str] = None
    content_direction: Optional[str] = None
    influencer_name: Optional[str] = None
    price_usd: Optional[float] = None
    title: Optional[str] = None
    publish_date: Optional[datetime] = None
    play_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    video_url: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_whatsapp: Optional[str] = None
    status: Optional[str] = None

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v):
        if v is not None:
            valid_platforms = [e.value for e in PlatformEnum]
            if v not in valid_platforms:
                raise ValueError(f'无效的平台，可选值: {", ".join(valid_platforms)}')
        return v

    @field_validator('influencer_name')
    @classmethod
    def validate_influencer_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('达人名称不能为空')
            if len(v.strip()) > 100:
                raise ValueError('达人名称不能超过100个字符')
            return v.strip()
        return v

    @field_validator('price_usd')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['pending', 'approved', 'rejected', 'published']
            if v not in valid_statuses:
                raise ValueError(f'无效的状态，可选值: {", ".join(valid_statuses)}')
        return v


class VideoResponse(VideoBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OperationLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    module: Optional[str]
    detail: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_videos: int
    total_plays: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_amount: float
    videos_by_platform: dict
    videos_by_region: dict
    recent_videos: list


class CrawlerRequest(BaseModel):
    url: str

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL不能为空')
        url_pattern = re.compile(
            r'^https?://'
        )
        if not url_pattern.match(v.strip()):
            raise ValueError('请输入有效的URL（以http://或https://开头）')
        return v.strip()
