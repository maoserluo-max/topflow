from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

from models import get_db, User, UserRole, OperationLog, InviteCode, ROLE_HIERARCHY
from auth import verify_password, get_password_hash, create_access_token, get_current_user, get_current_admin, get_current_super_admin, get_current_leader_or_above, get_current_admin_or_leader
from schemas import UserCreate, UserUpdate, UserResponse, Token, LoginRequest, InviteCodeResponse, InviteCodeCreate, AdminUserCreate

router = APIRouter(prefix="/api/auth", tags=["认证"])


def _get_subordinate_ids(user: User, db: Session) -> list[int]:
    """递归获取用户所有下属ID（包含自身）"""
    ids = [user.id]
    children = db.query(User).filter(User.parent_id == user.id).all()
    for child in children:
        ids.extend(_get_subordinate_ids(child, db))
    return ids


def _get_ancestor_chain(user: User, db: Session) -> list[dict]:
    """获取用户的上级链（从直接上级到最顶级）"""
    chain = []
    current = user
    visited = set()
    while current.parent_id and current.parent_id not in visited:
        visited.add(current.parent_id)
        parent = db.query(User).filter(User.id == current.parent_id).first()
        if not parent:
            break
        chain.append({
            "id": parent.id,
            "username": parent.username,
            "full_name": parent.full_name,
            "role": parent.role.value if parent.role else "user"
        })
        current = parent
    return chain


def _user_to_response(user: User, db: Session = None) -> dict:
    """User对象转响应dict，附带parent_name和ancestor_chain"""
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value if user.role else "user",
        "parent_id": user.parent_id,
        "parent_name": user.parent.full_name or user.parent.username if user.parent else None,
        "is_active": user.is_active,
        "projects": user.projects,
        "created_at": user.created_at,
        "ancestor_chain": [],
        "children_count": 0,
    }
    if db:
        data["ancestor_chain"] = _get_ancestor_chain(user, db)
        data["children_count"] = db.query(User).filter(User.parent_id == user.id).count()
    return data


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

    # 邀请码的注册角色
    register_role = UserRole(invite.register_role) if invite.register_role else UserRole.USER

    # 邀请码的项目权限：继承创建者的项目（如果有指定则使用指定的）
    invite_creator = db.query(User).filter(User.id == invite.created_by).first()
    if invite.projects:
        new_projects = invite.projects
    elif invite_creator and invite_creator.projects:
        new_projects = invite_creator.projects
    else:
        new_projects = "Gamoji,Poseme,内容孵化"

    # 组长只能创建下属组长或普通用户邀请码，验证注册角色合法性
    if invite_creator and invite_creator.role == UserRole.LEADER:
        if register_role not in [UserRole.LEADER, UserRole.USER]:
            raise HTTPException(status_code=400, detail="组长只能邀请组长或普通用户")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=register_role,
        parent_id=invite.created_by,
        is_active=True,
        projects=new_projects
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


@router.get("/users")
def get_users(
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.SUPER_ADMIN:
        users = db.query(User).all()
    else:
        # 管理员和组长只能看到自己下属（包含自身）
        subordinate_ids = _get_subordinate_ids(current_user, db)
        users = db.query(User).filter(User.id.in_(subordinate_ids)).all()
    return [_user_to_response(u, db) for u in users]


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能修改比自己权限高的用户
    if ROLE_HIERARCHY.get(db_user.role, 0) >= ROLE_HIERARCHY.get(current_user.role, 0) and db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="不能修改同级或更高级别的用户")

    # 非super_admin不能修改super_admin
    if current_user.role != UserRole.SUPER_ADMIN and db_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")

    # 组长只能修改自己的下属（组长或普通用户）
    if current_user.role == UserRole.LEADER:
        subordinate_ids = _get_subordinate_ids(current_user, db)
        if db_user.id not in subordinate_ids:
            raise HTTPException(status_code=403, detail="只能修改自己的下属用户")

    update_data = user_update.dict(exclude_unset=True)
    if "role" in update_data and update_data["role"]:
        new_role = UserRole(update_data["role"])
        # 不能将用户角色提升到等于或高于自身
        if ROLE_HIERARCHY.get(new_role, 0) >= ROLE_HIERARCHY.get(current_user.role, 0):
            raise HTTPException(status_code=403, detail="不能将用户角色提升到等于或高于自身级别")
        # 组长只能在 leader 和 user 之间切换下属角色
        if current_user.role == UserRole.LEADER and new_role not in [UserRole.LEADER, UserRole.USER]:
            raise HTTPException(status_code=403, detail="组长只能将下属设为组长或普通用户")
        update_data["role"] = new_role

    # 组长修改项目权限时，不能超出自身拥有的项目
    if current_user.role == UserRole.LEADER and "projects" in update_data:
        leader_projects = set()
        if current_user.projects:
            leader_projects = {p.strip() for p in current_user.projects.split(',') if p.strip()}
        if update_data["projects"]:
            requested = {p.strip() for p in update_data["projects"].split(',') if p.strip()}
            invalid = requested - leader_projects
            if invalid:
                raise HTTPException(status_code=403, detail=f"您无权分配以下项目: {', '.join(invalid)}")

    # 验证 parent_id 有效性
    if "parent_id" in update_data and update_data["parent_id"] is not None:
        parent = db.query(User).filter(User.id == update_data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=400, detail="指定的上级用户不存在")
        if update_data["parent_id"] == user_id:
            raise HTTPException(status_code=400, detail="不能将自己设为自己的上级")

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

    return _user_to_response(db_user, db)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    # 不能删除同级或更高级别的用户
    if ROLE_HIERARCHY.get(db_user.role, 0) >= ROLE_HIERARCHY.get(current_user.role, 0):
        raise HTTPException(status_code=403, detail="不能删除同级或更高级别的用户")

    # 组长只能删除自己的下属（组长或普通用户）
    if current_user.role == UserRole.LEADER:
        subordinate_ids = _get_subordinate_ids(current_user, db)
        if db_user.id not in subordinate_ids:
            raise HTTPException(status_code=403, detail="只能删除自己的下属用户")

    # 将被删除用户的下属重新指向被删除用户的上级
    children = db.query(User).filter(User.parent_id == db_user.id).all()
    for child in children:
        child.parent_id = db_user.parent_id

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


@router.post("/users")
def admin_create_user(
    user: AdminUserCreate,
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    new_role = UserRole(user.role) if user.role else UserRole.USER
    # 不能创建等于或高于自身级别的用户
    if ROLE_HIERARCHY.get(new_role, 0) >= ROLE_HIERARCHY.get(current_user.role, 0):
        raise HTTPException(status_code=403, detail="不能创建等于或高于自身级别的用户")

    # 组长可创建下属组长或普通用户
    if current_user.role == UserRole.LEADER and new_role not in [UserRole.LEADER, UserRole.USER]:
        raise HTTPException(status_code=403, detail="组长只能创建下属组长或普通用户")

    # 验证 parent_id
    parent_id = user.parent_id
    if parent_id:
        parent = db.query(User).filter(User.id == parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="指定的上级用户不存在")
        # 上级的角色必须高于新建用户的角色
        if ROLE_HIERARCHY.get(parent.role, 0) <= ROLE_HIERARCHY.get(new_role, 0):
            raise HTTPException(status_code=400, detail="上级用户的角色级别必须高于新建用户")
    else:
        # 默认上级为当前用户
        parent_id = current_user.id

    # 项目权限：组长创建的用户只能拥有组长拥有的项目子集
    if current_user.role == UserRole.LEADER:
        leader_projects = set()
        if current_user.projects:
            leader_projects = {p.strip() for p in current_user.projects.split(',') if p.strip()}
        if user.projects:
            requested = {p.strip() for p in user.projects.split(',') if p.strip()}
            # 只允许组长拥有权限内的项目
            allowed = requested & leader_projects
            final_projects = ','.join(sorted(allowed)) if allowed else current_user.projects
        else:
            final_projects = current_user.projects
        # 组长创建下属组长时，下属组长项目不能超过自身
    else:
        final_projects = user.projects

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=new_role,
        parent_id=parent_id,
        is_active=True,
        projects=final_projects
    )
    db.add(new_user)

    log = OperationLog(
        user_id=current_user.id,
        action="管理员创建用户",
        module="系统管理",
        detail=f"管理员 {current_user.username} 创建用户: {user.username}，角色: {user.role}"
    )
    db.add(log)
    db.commit()
    db.refresh(new_user)

    return _user_to_response(new_user, db)


# ==================== 邀请码管理（管理员和组长） ====================

def _get_allowed_register_roles(current_user: User) -> list[str]:
    """获取当前用户允许生成的邀请码注册角色"""
    if current_user.role == UserRole.SUPER_ADMIN:
        return ['admin', 'leader', 'user']
    elif current_user.role == UserRole.ADMIN:
        return ['leader', 'user']
    elif current_user.role == UserRole.LEADER:
        return ['leader', 'user']
    return []


@router.post("/invite-codes", response_model=InviteCodeResponse)
def create_invite_code(
    code_data: InviteCodeCreate,
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    # 验证注册角色权限
    allowed_roles = _get_allowed_register_roles(current_user)
    if code_data.register_role and code_data.register_role not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"您只能生成注册角色为: {', '.join(allowed_roles)} 的邀请码")

    # 验证项目权限：组长生成的邀请码项目必须是自己拥有的
    if current_user.role == UserRole.LEADER:
        leader_projects = set()
        if current_user.projects:
            leader_projects = {p.strip() for p in current_user.projects.split(',') if p.strip()}
        if code_data.projects:
            requested = {p.strip() for p in code_data.projects.split(',') if p.strip()}
            invalid = requested - leader_projects
            if invalid:
                raise HTTPException(status_code=403, detail=f"您无权分配以下项目: {', '.join(invalid)}")

    # 管理员及以上默认所有项目
    if not code_data.projects:
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            code_data.projects = "Gamoji,Poseme,内容孵化"
        else:
            code_data.projects = current_user.projects

    code = secrets.token_urlsafe(8).upper()[:8]
    invite = InviteCode(
        code=code,
        created_by=current_user.id,
        projects=code_data.projects,
        register_role=code_data.register_role or "leader",
        is_used=False
    )
    db.add(invite)

    log = OperationLog(
        user_id=current_user.id,
        action="生成邀请码",
        module="系统管理",
        detail=f"生成邀请码: {code}，注册角色: {code_data.register_role or 'user'}，项目: {code_data.projects or '默认'}"
    )
    db.add(log)
    db.commit()
    db.refresh(invite)

    return invite


@router.post("/invite-codes/batch", response_model=list[InviteCodeResponse])
def batch_create_invite_codes(
    code_data: InviteCodeCreate,
    count: int = 5,
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    if count < 1 or count > 50:
        raise HTTPException(status_code=400, detail="批量生成数量需在1-50之间")

    # 验证注册角色权限
    allowed_roles = _get_allowed_register_roles(current_user)
    if code_data.register_role and code_data.register_role not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"您只能生成注册角色为: {', '.join(allowed_roles)} 的邀请码")

    # 验证项目权限
    if current_user.role == UserRole.LEADER:
        leader_projects = set()
        if current_user.projects:
            leader_projects = {p.strip() for p in current_user.projects.split(',') if p.strip()}
        if code_data.projects:
            requested = {p.strip() for p in code_data.projects.split(',') if p.strip()}
            invalid = requested - leader_projects
            if invalid:
                raise HTTPException(status_code=403, detail=f"您无权分配以下项目: {', '.join(invalid)}")

    if not code_data.projects:
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            code_data.projects = "Gamoji,Poseme,内容孵化"
        else:
            code_data.projects = current_user.projects

    codes = []
    for _ in range(count):
        code = secrets.token_urlsafe(8).upper()[:8]
        invite = InviteCode(
            code=code,
            created_by=current_user.id,
            projects=code_data.projects,
            register_role=code_data.register_role or "leader",
            is_used=False
        )
        db.add(invite)
        codes.append(invite)

    log = OperationLog(
        user_id=current_user.id,
        action="批量生成邀请码",
        module="系统管理",
        detail=f"批量生成 {count} 个邀请码，注册角色: {code_data.register_role or 'user'}，项目: {code_data.projects or '默认'}"
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
    current_user: User = Depends(get_current_admin_or_leader),
    db: Session = Depends(get_db)
):
    query = db.query(InviteCode).filter(InviteCode.created_by == current_user.id)
    if is_used is not None:
        query = query.filter(InviteCode.is_used == is_used)

    total = query.count()
    codes = query.order_by(InviteCode.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 附带已注册用户信息
    items = []
    for c in codes:
        item = InviteCodeResponse.model_validate(c).model_dump()
        if c.used_user:
            item["used_user_info"] = {
                "id": c.used_user.id,
                "username": c.used_user.username,
                "full_name": c.used_user.full_name,
                "role": c.used_user.role.value if c.used_user.role else "user",
                "email": c.used_user.email,
            }
        else:
            item["used_user_info"] = None
        if c.creator:
            item["creator_name"] = c.creator.full_name or c.creator.username
        items.append(item)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.delete("/invite-codes/{code_id}")
def delete_invite_code(
    code_id: int,
    current_user: User = Depends(get_current_admin_or_leader),
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
