from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from models import get_db, User, UserRole, OperationLog
from auth import verify_password, get_password_hash, create_access_token, get_current_user, get_current_admin
from schemas import UserCreate, UserResponse, Token, LoginRequest

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=UserRole.USER,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log = OperationLog(
        user_id=new_user.id,
        action="用户注册",
        module="认证",
        detail=f"新用户注册: {user.username}"
    )
    db.add(log)
    db.commit()

    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")

    access_token = create_access_token(data={"sub": user.username})

    log = OperationLog(
        user_id=user.id,
        action="用户登录",
        module="认证",
        ip_address="unknown"
    )
    db.add(log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: dict,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    for key, value in user_update.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    log = OperationLog(
        user_id=current_user.id,
        action="更新用户",
        module="系统管理",
        detail=f"更新用户信息: {db_user.username}"
    )
    db.add(log)
    db.commit()

    return db_user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    username = db_user.username
    db.delete(db_user)
    db.commit()

    log = OperationLog(
        user_id=current_user.id,
        action="删除用户",
        module="系统管理",
        detail=f"删除用户: {username}"
    )
    db.add(log)
    db.commit()

    return {"message": "用户删除成功"}