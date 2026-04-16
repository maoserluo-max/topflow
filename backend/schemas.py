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
    invite_code: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少6个字符')
        if len(v) > 72:
            raise ValueError('密码不能超过72个字符')
        return v

    @field_validator('invite_code')
    @classmethod
    def validate_invite_code(cls, v):
        if not v or not v.strip():
            raise ValueError('邀请码不能为空')
        return v.strip()


class AdminUserCreate(UserBase):
    password: str
    role: Optional[str] = "user"
    projects: Optional[str] = "Gamoji,Poseme,内容孵化"

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少6个字符')
        if len(v) > 72:
            raise ValueError('密码不能超过72个字符')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None:
            valid_roles = ['admin', 'manager', 'user']
            if v not in valid_roles:
                raise ValueError(f'无效的角色，可选值: {", ".join(valid_roles)}')
        return v


class InviteCodeResponse(BaseModel):
    id: int
    code: str
    created_by: int
    used_by: Optional[int] = None
    used_at: Optional[datetime] = None
    is_used: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    projects: Optional[str] = None

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None:
            valid_roles = ['admin', 'manager', 'user']
            if v not in valid_roles:
                raise ValueError(f'无效的角色，可选值: {", ".join(valid_roles)}')
        return v

    @field_validator('projects')
    @classmethod
    def validate_projects(cls, v):
        if v is not None:
            valid_projects = ['Gamoji', 'Poseme', '内容孵化']
            for p in v.split(','):
                if p.strip() and p.strip() not in valid_projects:
                    raise ValueError(f'无效的项目，可选值: {", ".join(valid_projects)}')
        return v


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    projects: Optional[str] = "Gamoji,Poseme,内容孵化"
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
    video_code: Optional[str] = None
    project: str = "Gamoji"
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
    status: Optional[str] = "pending_review"

    @field_validator('project')
    @classmethod
    def validate_project(cls, v):
        valid_projects = ['Gamoji', 'Poseme', '内容孵化']
        if v not in valid_projects:
            raise ValueError(f'无效的项目，可选值: {", ".join(valid_projects)}')
        return v

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
            valid_statuses = ['pending_review', 'pending_publish', 'published', 'completed']
            if v not in valid_statuses:
                raise ValueError(f'无效的状态，可选值: {", ".join(valid_statuses)}')
        return v


class VideoCreate(VideoBase):
    pass


class VideoUpdate(BaseModel):
    video_code: Optional[str] = None
    project: Optional[str] = None
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
    def validate_status_update(cls, v):
        if v is not None:
            valid_statuses = ['pending_review', 'pending_publish', 'published', 'completed']
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
