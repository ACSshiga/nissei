from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.worklog import WorkLog
from app.models.project import Project
from app.schemas.worklog import (
    WorkLogCreate,
    WorkLogUpdate,
    WorkLogResponse,
    WorkLogListResponse,
)

router = APIRouter()


@router.post("", response_model=WorkLogResponse, status_code=201)
def create_worklog(
    worklog_data: WorkLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """工数入力を新規作成"""
    # 案件の存在確認
    project = db.query(Project).filter(Project.id == worklog_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")

    # 新規工数入力作成
    db_worklog = WorkLog(
        **worklog_data.model_dump(),
        user_id=current_user.id,
    )
    db.add(db_worklog)

    # 案件の実績工数を更新
    project.actual_hours += worklog_data.duration_minutes

    db.commit()
    db.refresh(db_worklog)
    return db_worklog


@router.get("", response_model=WorkLogListResponse)
def list_worklogs(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    project_id: Optional[UUID] = Query(None, description="案件IDでフィルタ"),
    work_date: Optional[date] = Query(None, description="作業日でフィルタ"),
    user_id: Optional[UUID] = Query(None, description="ユーザーIDでフィルタ"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """工数入力一覧を取得"""
    query = db.query(WorkLog)

    # フィルタリング
    if project_id:
        query = query.filter(WorkLog.project_id == project_id)
    if work_date:
        query = query.filter(WorkLog.work_date == work_date)
    if user_id:
        query = query.filter(WorkLog.user_id == user_id)

    # 総件数取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * per_page
    worklogs = query.order_by(WorkLog.work_date.desc(), WorkLog.created_at.desc()).offset(offset).limit(per_page).all()

    return WorkLogListResponse(
        worklogs=worklogs,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{worklog_id}", response_model=WorkLogResponse)
def get_worklog(
    worklog_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """工数入力詳細を取得"""
    worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if not worklog:
        raise HTTPException(status_code=404, detail="工数入力が見つかりません")
    return worklog


@router.put("/{worklog_id}", response_model=WorkLogResponse)
def update_worklog(
    worklog_id: UUID,
    worklog_data: WorkLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """工数入力を更新"""
    worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if not worklog:
        raise HTTPException(status_code=404, detail="工数入力が見つかりません")

    # 作業時間が変更される場合、案件の実績工数を調整
    old_duration = worklog.duration_minutes
    update_data = worklog_data.model_dump(exclude_unset=True)
    new_duration = update_data.get("duration_minutes", old_duration)

    if new_duration != old_duration:
        project = db.query(Project).filter(Project.id == worklog.project_id).first()
        if project:
            project.actual_hours = project.actual_hours - old_duration + new_duration

    # 更新
    for key, value in update_data.items():
        setattr(worklog, key, value)

    db.commit()
    db.refresh(worklog)
    return worklog


@router.delete("/{worklog_id}", status_code=204)
def delete_worklog(
    worklog_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """工数入力を削除"""
    worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if not worklog:
        raise HTTPException(status_code=404, detail="工数入力が見つかりません")

    # 案件の実績工数を減算
    project = db.query(Project).filter(Project.id == worklog.project_id).first()
    if project:
        project.actual_hours -= worklog.duration_minutes

    db.delete(worklog)
    db.commit()
    return None


@router.get("/summary/{project_id}")
def get_worklog_summary(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件の工数集計を取得"""
    # 案件の存在確認
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")

    # ユーザー別工数集計
    user_summary = (
        db.query(
            User.username,
            func.sum(WorkLog.duration_minutes).label("total_minutes"),
            func.count(WorkLog.id).label("entry_count"),
        )
        .join(WorkLog, WorkLog.user_id == User.id)
        .filter(WorkLog.project_id == project_id)
        .group_by(User.id, User.username)
        .all()
    )

    # 日別工数集計
    daily_summary = (
        db.query(
            WorkLog.work_date,
            func.sum(WorkLog.duration_minutes).label("total_minutes"),
            func.count(WorkLog.id).label("entry_count"),
        )
        .filter(WorkLog.project_id == project_id)
        .group_by(WorkLog.work_date)
        .order_by(WorkLog.work_date.desc())
        .all()
    )

    return {
        "project_id": project_id,
        "management_no": project.management_no,
        "estimated_hours": project.estimated_hours or 0,
        "actual_hours": project.actual_hours,
        "by_user": [
            {
                "username": row.username,
                "total_minutes": row.total_minutes,
                "entry_count": row.entry_count,
            }
            for row in user_summary
        ],
        "by_date": [
            {
                "work_date": row.work_date.isoformat(),
                "total_minutes": row.total_minutes,
                "entry_count": row.entry_count,
            }
            for row in daily_summary
        ],
    }