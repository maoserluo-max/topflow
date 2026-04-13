from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


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