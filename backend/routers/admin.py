from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timezone
import csv
import io

from models import get_db, User, OperationLog, UserRole, Video
from auth import get_current_admin
from schemas import OperationLogResponse

router = APIRouter(prefix="/api/admin", tags=["系统管理"])


@router.get("/logs", response_model=dict)
def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: Optional[str] = None,
    module: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(OperationLog)

    if action:
        query = query.filter(OperationLog.action.ilike(f"%{action}%"))
    if module:
        query = query.filter(OperationLog.module == module)
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)

    total = query.count()
    logs = query.order_by(desc(OperationLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    # 构建响应，附带用户名
    items = []
    for log in logs:
        item = OperationLogResponse.from_orm(log)
        item_dict = item.model_dump() if hasattr(item, 'model_dump') else item.dict()
        item_dict['username'] = log.user.username if log.user else None
        items.append(item_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get("/stats")
def get_system_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    total_videos = db.query(Video).count()

    today_logs = db.query(OperationLog).filter(
        OperationLog.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_videos": total_videos,
        "today_operations": today_logs
    }


@router.get("/export-logs")
def export_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(OperationLog)

    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)

    logs = query.order_by(desc(OperationLog.created_at)).all()

    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "用户", "操作", "模块", "详情", "IP地址", "时间"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for log in logs:
            writer.writerow([
                log.id,
                log.user.username if log.user else "",
                log.action,
                log.module or "",
                log.detail or "",
                log.ip_address or "",
                log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else ""
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    filename = f"operation_logs_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
