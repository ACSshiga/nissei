from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件を新規作成"""
    # 管理Noの重複チェック
    existing = db.query(Project).filter(Project.management_no == project_data.management_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="この管理Noは既に使用されています")

    # 新規案件作成
    db_project = Project(
        **project_data.model_dump(),
        created_by=current_user.id,
        actual_hours=0,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: Optional[str] = Query(None, description="ステータスでフィルタ"),
    machine_no: Optional[str] = Query(None, description="機番で検索"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件一覧を取得"""
    query = db.query(Project)

    # フィルタリング
    if status:
        query = query.filter(Project.status == status)
    if machine_no:
        query = query.filter(Project.machine_no.contains(machine_no))

    # 総件数取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * per_page
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(per_page).all()

    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件詳細を取得"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件を更新"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")

    # 管理Noの重複チェック（変更される場合）
    if project_data.management_no and project_data.management_no != project.management_no:
        existing = db.query(Project).filter(Project.management_no == project_data.management_no).first()
        if existing:
            raise HTTPException(status_code=400, detail="この管理Noは既に使用されています")

    # 更新
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件を削除"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")

    db.delete(project)
    db.commit()
    return None