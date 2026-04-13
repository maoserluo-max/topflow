import sys
sys.path.append('..')
from crawler import TopFlowCrawler
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime

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
    videos = query.order_by(desc(Video.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": videos,
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
def fetch_metadata(
    request: CrawlerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        data = crawler.extract_video(request.url)
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

    videos = query.all()

    total_videos = len(videos)
    total_plays = sum(v.play_count or 0 for v in videos)
    total_likes = sum(v.like_count or 0 for v in videos)
    total_comments = sum(v.comment_count or 0 for v in videos)
    total_shares = sum(v.share_count or 0 for v in videos)
    total_amount = sum(v.price_usd or 0 for v in videos)

    platform_stats = {}
    for v in videos:
        platform_stats[v.platform] = platform_stats.get(v.platform, 0) + 1

    region_stats = {}
    for v in videos:
        if v.region:
            region_stats[v.region] = region_stats.get(v.region, 0) + 1

    recent_videos = sorted(videos, key=lambda x: x.created_at, reverse=True)[:10]

    return DashboardStats(
        total_videos=total_videos,
        total_plays=total_plays,
        total_likes=total_likes,
        total_comments=total_comments,
        total_shares=total_shares,
        total_amount=total_amount,
        videos_by_platform=platform_stats,
        videos_by_region=region_stats,
        recent_videos=[VideoResponse.from_orm(v) for v in recent_videos]
    )