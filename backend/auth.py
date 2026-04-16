from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from models import User, get_db, UserRole, ROLE_HIERARCHY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    secret_key = settings.SECRET_KEY[:72] if len(settings.SECRET_KEY) > 72 else settings.SECRET_KEY
    
    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        secret_key = settings.SECRET_KEY[:72] if len(settings.SECRET_KEY) > 72 else settings.SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """系统管理员或管理员权限"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user


async def get_current_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """仅系统管理员权限"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="权限不足，需要系统管理员权限")
    return current_user


async def get_current_leader_or_above(current_user: User = Depends(get_current_user)) -> User:
    """组长或以上权限"""
    if ROLE_HIERARCHY.get(current_user.role, 0) < ROLE_HIERARCHY.get(UserRole.LEADER, 0):
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user


async def get_current_admin_or_leader(current_user: User = Depends(get_current_user)) -> User:
    """管理员或组长权限（用于用户管理和邀请码管理）"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.LEADER]:
        raise HTTPException(status_code=403, detail="权限不足，需要管理员或组长权限")
    return current_user