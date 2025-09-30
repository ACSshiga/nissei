"""
案件管理API

案件の登録・一覧・詳細・更新・削除（論理削除）
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.master import (
    MasterShinchoku,
    MasterSagyouKubun,
    MasterToiawase,
    MachineSeriesMaster
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件を新規作成"""
    # 管理Noの重複チェック
    existing = db.query(Project).filter(
        Project.management_no == project_data.management_no,
        Project.is_active == True
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この管理Noは既に使用されています"
        )

    # 新規案件作成
    db_project = Project(
        **project_data.model_dump(),
        created_by=current_user.id,
        actual_hours=0,
        is_active=True,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # マスタ名称を取得
    return _enrich_project_response(db, db_project)


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    shinchoku_id: Optional[UUID] = Query(None, description="進捗IDでフィルタ"),
    sagyou_kubun_id: Optional[UUID] = Query(None, description="作業区分IDでフィルタ"),
    machine_no: Optional[str] = Query(None, description="機番で検索"),
    management_no: Optional[str] = Query(None, description="管理Noで検索"),
    include_inactive: bool = Query(False, description="無効な案件も含める"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件一覧を取得"""
    query = db.query(Project).options(
        joinedload(Project.machine_series),
        joinedload(Project.toiawase),
        joinedload(Project.sagyou_kubun),
        joinedload(Project.shinchoku)
    )

    # 論理削除フィルタ
    if not include_inactive:
        query = query.filter(Project.is_active == True)

    # フィルタリング
    if shinchoku_id:
        query = query.filter(Project.shinchoku_id == shinchoku_id)
    if sagyou_kubun_id:
        query = query.filter(Project.sagyou_kubun_id == sagyou_kubun_id)
    if machine_no:
        query = query.filter(Project.machine_no.contains(machine_no))
    if management_no:
        query = query.filter(Project.management_no.contains(management_no))

    # 総件数取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * per_page
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(per_page).all()

    # レスポンスにマスタ名称を追加
    enriched_projects = [_enrich_project_response(db, p) for p in projects]

    return ProjectListResponse(
        projects=enriched_projects,
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
    project = db.query(Project).options(
        joinedload(Project.machine_series),
        joinedload(Project.toiawase),
        joinedload(Project.sagyou_kubun),
        joinedload(Project.shinchoku)
    ).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件が見つかりません"
        )

    return _enrich_project_response(db, project)


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件が見つかりません"
        )

    # 管理Noの重複チェック（変更される場合）
    if project_data.management_no and project_data.management_no != project.management_no:
        existing = db.query(Project).filter(
            Project.management_no == project_data.management_no,
            Project.is_active == True,
            Project.id != project_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="この管理Noは既に使用されています"
            )

    # 更新
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return _enrich_project_response(db, project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """案件を論理削除"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件が見つかりません"
        )

    # 論理削除
    project.is_active = False
    db.commit()
    return None


def _enrich_project_response(db: Session, project: Project) -> ProjectResponse:
    """案件レスポンスにマスタ名称を追加"""
    response_data = {
        "id": project.id,
        "management_no": project.management_no,
        "machine_series_id": project.machine_series_id,
        "generation": project.generation,
        "tonnage": project.tonnage,
        "spec_tags": project.spec_tags,
        "machine_no": project.machine_no,
        "commission_content": project.commission_content,
        "toiawase_id": project.toiawase_id,
        "sagyou_kubun_id": project.sagyou_kubun_id,
        "estimated_hours": project.estimated_hours,
        "actual_hours": project.actual_hours,
        "shinchoku_id": project.shinchoku_id,
        "start_date": project.start_date,
        "completion_date": project.completion_date,
        "drawing_deadline": project.drawing_deadline,
        "is_active": project.is_active,
        "created_by": project.created_by,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "machine_series_name": project.machine_series.display_name if project.machine_series else None,
        "toiawase_name": project.toiawase.status_name if project.toiawase else None,
        "sagyou_kubun_name": project.sagyou_kubun.kubun_name if project.sagyou_kubun else None,
        "shinchoku_name": project.shinchoku.status_name if project.shinchoku else None,
    }

    return ProjectResponse(**response_data)