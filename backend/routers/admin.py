from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from models import get_db, User, OperationLog, UserRole
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

    return {
        "items": logs,
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
    
    from models import Video
    total_videos = db.query(Video).count()
    
    today_logs = db.query(OperationLog).filter(
        OperationLog.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_videos": total_videos,
        "today_operations": today_logs
    }


@router.get("/export-logs")
def export_logs(
    format: str = "csv",
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

    if format == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "用户ID", "操作", "模块", "详情", "IP地址", "时间"])

        for log in logs:
            writer.writerow([
                log.id,
                log.user_id,
                log.action,
                log.module or "",
                log.detail or "",
                log.ip_address or "",
                log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else ""
            ])

        output.seek(0)
        return {"data": output.getvalue(), "format": "csv"}

    return {"message": "仅支持CSV格式导出"}