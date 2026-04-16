from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

from models import get_db, User, UserRole, OperationLog, InviteCode
from auth import verify_password, get_password_hash, create_access_token, get_current_user, get_current_admin
from schemas import UserCreate, UserUpdate, UserResponse, Token, LoginRequest, InviteCodeResponse, AdminUserCreate

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 验证邀请码
    invite = db.query(InviteCode).filter(InviteCode.code == user.invite_code, InviteCode.is_used == False).first()
    if not invite:
        raise HTTPException(status_code=400, detail="邀请码无效或已被使用")

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
    db.flush()

    # 标记邀请码为已使用
    invite.is_used = True
    invite.used_by = new_user.id
    invite.used_at = datetime.utcnow()

    log = OperationLog(
        user_id=new_user.id,
        action="用户注册",
        module="认证",
        detail=f"新用户注册: {user.username}，邀请码: {user.invite_code}"
    )
    db.add(log)
    db.commit()
    db.refresh(new_user)

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
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = user_update.dict(exclude_unset=True)
    if "role" in update_data and update_data["role"]:
        update_data["role"] = UserRole(update_data["role"])

    for field, value in update_data.items():
        setattr(db_user, field, value)

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


@router.post("/users", response_model=UserResponse)
def admin_create_user(
    user: AdminUserCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
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
        role=UserRole(user.role) if user.role else UserRole.USER,
        is_active=True,
        projects=user.projects
    )
    db.add(new_user)

    log = OperationLog(
        user_id=current_user.id,
        action="管理员创建用户",
        module="系统管理",
        detail=f"管理员 {current_user.username} 创建用户: {user.username}"
    )
    db.add(log)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==================== 邀请码管理（仅管理员） ====================

@router.post("/invite-codes", response_model=InviteCodeResponse)
def create_invite_code(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    code = secrets.token_urlsafe(8).upper()[:8]
    invite = InviteCode(
        code=code,
        created_by=current_user.id,
        is_used=False
    )
    db.add(invite)

    log = OperationLog(
        user_id=current_user.id,
        action="生成邀请码",
        module="系统管理",
        detail=f"生成邀请码: {code}"
    )
    db.add(log)
    db.commit()
    db.refresh(invite)

    return invite


@router.post("/invite-codes/batch", response_model=list[InviteCodeResponse])
def batch_create_invite_codes(
    count: int = 5,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if count < 1 or count > 50:
        raise HTTPException(status_code=400, detail="批量生成数量需在1-50之间")

    codes = []
    for _ in range(count):
        code = secrets.token_urlsafe(8).upper()[:8]
        invite = InviteCode(
            code=code,
            created_by=current_user.id,
            is_used=False
        )
        db.add(invite)
        codes.append(invite)

    log = OperationLog(
        user_id=current_user.id,
        action="批量生成邀请码",
        module="系统管理",
        detail=f"批量生成 {count} 个邀请码"
    )
    db.add(log)
    db.commit()

    for c in codes:
        db.refresh(c)

    return codes


@router.get("/invite-codes", response_model=dict)
def get_invite_codes(
    page: int = 1,
    page_size: int = 20,
    is_used: bool = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(InviteCode)
    if is_used is not None:
        query = query.filter(InviteCode.is_used == is_used)

    total = query.count()
    codes = query.order_by(InviteCode.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [InviteCodeResponse.model_validate(c) for c in codes],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.delete("/invite-codes/{code_id}")
def delete_invite_code(
    code_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    invite = db.query(InviteCode).filter(InviteCode.id == code_id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="邀请码不存在")
    if invite.is_used:
        raise HTTPException(status_code=400, detail="已使用的邀请码不能删除")

    db.delete(invite)
    db.commit()

    return {"message": "邀请码删除成功"}