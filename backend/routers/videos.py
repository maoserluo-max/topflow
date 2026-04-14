import sys
sys.path.append('..')
from crawler import TopFlowCrawler
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import Optional
from datetime import datetime
import asyncio

from models import get_db, Video, User, OperationLog, UserRole
from auth import get_current_user, get_current_manager_or_admin, get_current_admin
from schemas import VideoCreate, VideoUpdate, VideoResponse, CrawlerRequest, DashboardStats

router = APIRouter(prefix="/api/videos", tags=["视频管理"])
crawler = TopFlowCrawler()


@router.post("/", response_model=VideoResponse)
def create_video(
    video: VideoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_video = Video(**video.dict(), creator_id=current_user.id)
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    log = OperationLog(
        user_id=current_user.id,
        action="创建视频",
        module="视频管理",
        detail=f"创建视频记录: {video.influencer_name} - {video.title or '无标题'}"
    )
    db.add(log)
    db.commit()

    return new_video


@router.get("/", response_model=dict)
def get_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    region: Optional[str] = None,
    influencer_name: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向: asc/desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Video)

    if current_user.role == UserRole.USER:
        query = query.filter(Video.creator_id == current_user.id)

    if platform:
        query = query.filter(Video.platform.ilike(f"%{platform}%"))
    if region:
        query = query.filter(Video.region.ilike(f"%{region}%"))
    if influencer_name:
        query = query.filter(Video.influencer_name.ilike(f"%{influencer_name}%"))
    if status:
        query = query.filter(Video.status == status)
    if start_date:
        query = query.filter(Video.publish_date >= start_date)
    if end_date:
        query = query.filter(Video.publish_date <= end_date)

    total = query.count()

    sort_column = getattr(Video, sort_by, Video.created_at)
    if sort_order and sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    videos = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [VideoResponse.from_orm(v) for v in videos],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    if current_user.role == UserRole.USER and video.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此视频")

    return video


@router.put("/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: int,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    update_data = video_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)

    db.commit()
    db.refresh(video)

    log = OperationLog(
        user_id=current_user.id,
        action="更新视频",
        module="视频管理",
        detail=f"更新视频 ID: {video_id}"
    )
    db.add(log)
    db.commit()

    return video


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    db.delete(video)
    db.commit()

    log = OperationLog(
        user_id=current_user.id,
        action="删除视频",
        module="视频管理",
        detail=f"删除视频 ID: {video_id}"
    )
    db.add(log)
    db.commit()

    return {"message": "视频删除成功"}


@router.post("/fetch-metadata")
async def fetch_metadata(
    request: CrawlerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        data = await asyncio.to_thread(crawler.extract_video, request.url)
        if not data:
            raise HTTPException(status_code=400, detail="无法获取视频数据，请检查链接是否正确")

        log = OperationLog(
            user_id=current_user.id,
            action="抓取视频元数据",
            module="视频管理",
            detail=f"URL: {request.url}"
        )
        db.add(log)
        db.commit()

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    platform: Optional[str] = None,
    region: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Video)

    if current_user.role == UserRole.USER:
        query = query.filter(Video.creator_id == current_user.id)

    if start_date:
        query = query.filter(Video.publish_date >= start_date)
    if end_date:
        query = query.filter(Video.publish_date <= end_date)
    if platform:
        query = query.filter(Video.platform == platform)
    if region:
        query = query.filter(Video.region == region)

    agg_result = query.with_entities(
        func.count(Video.id).label('total_videos'),
        func.coalesce(func.sum(Video.play_count), 0).label('total_plays'),
        func.coalesce(func.sum(Video.like_count), 0).label('total_likes'),
        func.coalesce(func.sum(Video.comment_count), 0).label('total_comments'),
        func.coalesce(func.sum(Video.share_count), 0).label('total_shares'),
        func.coalesce(func.sum(Video.price_usd), 0).label('total_amount'),
    ).first()

    base_filter = query.whereclause
    platform_query = db.query(Video.platform, func.count(Video.id))
    if base_filter is not None:
        platform_query = platform_query.filter(base_filter)
    platform_stats = dict(platform_query.group_by(Video.platform).all())

    region_query = db.query(Video.region, func.count(Video.id)).filter(Video.region.isnot(None))
    if base_filter is not None:
        region_query = region_query.filter(base_filter)
    region_stats = dict(region_query.group_by(Video.region).all())

    recent_videos = query.order_by(desc(Video.created_at)).limit(10).all()

    return DashboardStats(
        total_videos=agg_result.total_videos,
        total_plays=agg_result.total_plays,
        total_likes=agg_result.total_likes,
        total_comments=agg_result.total_comments,
        total_shares=agg_result.total_shares,
        total_amount=agg_result.total_amount,
        videos_by_platform=platform_stats,
        videos_by_region=region_stats,
        recent_videos=[VideoResponse.from_orm(v) for v in recent_videos]
    )