from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models import get_db, PlatformCookies, User, UserRole
from auth import get_current_user

router = APIRouter(prefix="/api/cookies", tags=["Cookies管理"])

VALID_PLATFORMS = ["youtube", "tiktok", "ins"]


class CookiesSave(BaseModel):
    platform: str
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "youtube",
                "content": "# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tTRUE\t...\n"
            }
        }


class CookiesResponse(BaseModel):
    id: int
    platform: str
    content_preview: str
    has_content: bool
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EffectiveCookiesResponse(BaseModel):
    platform: str
    source: str
    has_cookies: bool
    updated_at: Optional[datetime] = None


@router.get("", response_model=list[CookiesResponse])
def get_cookies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = []
    for platform in VALID_PLATFORMS:
        cookie = db.query(PlatformCookies).filter(
            PlatformCookies.user_id == current_user.id,
            PlatformCookies.platform == platform
        ).first()

        if cookie and cookie.content:
            preview = cookie.content[:20] + "..." if len(cookie.content) > 20 else cookie.content
            results.append(CookiesResponse(
                id=cookie.id,
                platform=platform,
                content_preview=preview,
                has_content=True,
                updated_at=cookie.updated_at
            ))
        else:
            results.append(CookiesResponse(
                id=0,
                platform=platform,
                content_preview="",
                has_content=False,
                updated_at=None
            ))
    return results


@router.get("/content/{platform}")
def get_cookies_content(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"无效的平台，可选值: {', '.join(VALID_PLATFORMS)}")

    cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id == current_user.id,
        PlatformCookies.platform == platform
    ).first()

    return {"platform": platform, "content": cookie.content if cookie else ""}


@router.post("")
def save_cookies(
    data: CookiesSave,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"无效的平台，可选值: {', '.join(VALID_PLATFORMS)}")

    cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id == current_user.id,
        PlatformCookies.platform == data.platform
    ).first()

    if cookie:
        cookie.content = data.content
        cookie.updated_at = datetime.now()
    else:
        cookie = PlatformCookies(
            user_id=current_user.id,
            platform=data.platform,
            content=data.content
        )
        db.add(cookie)

    db.commit()
    db.refresh(cookie)
    return {"message": "Cookies保存成功", "platform": data.platform}


@router.delete("/{platform}")
def delete_cookies(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"无效的平台，可选值: {', '.join(VALID_PLATFORMS)}")

    cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id == current_user.id,
        PlatformCookies.platform == platform
    ).first()

    if cookie:
        cookie.content = ""
        cookie.updated_at = datetime.now()
        db.commit()

    return {"message": "Cookies已清除", "platform": platform}


@router.get("/effective/{platform}", response_model=EffectiveCookiesResponse)
def get_effective_cookies(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"无效的平台，可选值: {', '.join(VALID_PLATFORMS)}")

    user_cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id == current_user.id,
        PlatformCookies.platform == platform
    ).first()

    if user_cookie and user_cookie.content and user_cookie.content.strip():
        return EffectiveCookiesResponse(
            platform=platform,
            source="user",
            has_cookies=True,
            updated_at=user_cookie.updated_at
        )

    admin_cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id != current_user.id,
        PlatformCookies.platform == platform
    ).join(User, PlatformCookies.user_id == User.id).filter(
        User.role == UserRole.ADMIN
    ).first()

    if admin_cookie and admin_cookie.content and admin_cookie.content.strip():
        return EffectiveCookiesResponse(
            platform=platform,
            source="admin",
            has_cookies=True,
            updated_at=admin_cookie.updated_at
        )

    return EffectiveCookiesResponse(
        platform=platform,
        source="none",
        has_cookies=False,
        updated_at=None
    )


def get_effective_cookies_content(user_id: int, platform: str, db: Session) -> str:
    user_cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id == user_id,
        PlatformCookies.platform == platform
    ).first()

    if user_cookie and user_cookie.content and user_cookie.content.strip():
        return user_cookie.content

    admin_cookie = db.query(PlatformCookies).filter(
        PlatformCookies.user_id != user_id,
        PlatformCookies.platform == platform
    ).join(User, PlatformCookies.user_id == User.id).filter(
        User.role == UserRole.ADMIN
    ).first()

    if admin_cookie and admin_cookie.content and admin_cookie.content.strip():
        return admin_cookie.content

    return ""
