"""
案件管理API

案件の登録・一覧・詳細・更新・削除（論理削除）
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid

from app.core.database import get_db
from app.api.auth import get_current_user
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
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件を新規作成"""
    # 管理Noの重複チェック
    existing = db.table("projects").select("id").eq("management_no", project_data.management_no).eq("is_active", True).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この管理Noは既に使用されています"
        )

    # 新規案件作成
    new_project = {
        "id": str(uuid.uuid4()),
        **project_data.model_dump(),
        "created_by": current_user["id"],
        "actual_hours": 0,
        "is_active": True,
    }

    response = db.table("projects").insert(new_project).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="案件の作成に失敗しました"
        )

    # マスタ名称を取得
    return _enrich_project_response(db, response.data[0])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    shinchoku_id: Optional[UUID] = Query(None, description="進捗IDでフィルタ"),
    sagyou_kubun_id: Optional[UUID] = Query(None, description="作業区分IDでフィルタ"),
    machine_no: Optional[str] = Query(None, description="機番で検索"),
    management_no: Optional[str] = Query(None, description="管理Noで検索"),
    include_inactive: bool = Query(False, description="無効な案件も含める"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件一覧を取得"""
    # Supabaseクエリ構築
    query = db.table("projects").select("*")

    # 論理削除フィルタ
    if not include_inactive:
        query = query.eq("is_active", True)

    # フィルタリング
    if shinchoku_id:
        query = query.eq("shinchoku_id", str(shinchoku_id))
    if sagyou_kubun_id:
        query = query.eq("sagyou_kubun_id", str(sagyou_kubun_id))
    if machine_no:
        query = query.ilike("machine_no", f"%{machine_no}%")
    if management_no:
        query = query.ilike("management_no", f"%{management_no}%")

    # 総件数取得（カウント用に別クエリ）
    count_query = db.table("projects").select("id", count="exact")
    if not include_inactive:
        count_query = count_query.eq("is_active", True)
    if shinchoku_id:
        count_query = count_query.eq("shinchoku_id", str(shinchoku_id))
    if sagyou_kubun_id:
        count_query = count_query.eq("sagyou_kubun_id", str(sagyou_kubun_id))
    if machine_no:
        count_query = count_query.ilike("machine_no", f"%{machine_no}%")
    if management_no:
        count_query = count_query.ilike("management_no", f"%{management_no}%")

    count_response = count_query.execute()
    total = count_response.count if count_response.count is not None else 0

    # ページネーション
    offset = (page - 1) * per_page
    projects_response = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()

    # レスポンスにマスタ名称を追加
    enriched_projects = [_enrich_project_response(db, p) for p in projects_response.data]

    return ProjectListResponse(
        projects=enriched_projects,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件詳細を取得"""
    response = db.table("projects").select("*").eq("id", str(project_id)).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件が見つかりません"
        )

    return _enrich_project_response(db, response.data[0])


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件を更新"""
    project_response = db.table("projects").select("*").eq("id", str(project_id)).execute()
    if not project_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件が見つかりません"
        )

    project = project_response.data[0]

    # 管理Noの重複チェック（変更される場合）
    if project_data.management_no and project_data.management_no != project["management_no"]:
        existing = db.table("projects").select("id").eq("management_no", project_data.management_no).eq("is_active", True).neq("id", str(project_id)).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="この管理Noは既に使用されています"
            )

    # 更新
    update_data = project_data.model_dump(exclude_unset=True)
    response = db.table("projects").update(update_data).eq("id", str(project_id)).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="案件の更新に失敗しました"
        )

    return _enrich_project_response(db, response.data[0])


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件を論理削除"""
    project_response = db.table("projects").select("id").eq("id", str(project_id)).execute()
    if not project_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件が見つかりません"
        )

    # 論理削除
    db.table("projects").update({"is_active": False}).eq("id", str(project_id)).execute()
    return None


def _enrich_project_response(db: Client, project: Dict[str, Any]) -> ProjectResponse:
    """案件レスポンスにマスタ名称を追加"""
    # マスタ名称を取得
    machine_series_name = None
    if project.get("machine_series_id"):
        ms_response = db.table("machine_series_master").select("display_name").eq("id", project["machine_series_id"]).execute()
        if ms_response.data:
            machine_series_name = ms_response.data[0]["display_name"]

    toiawase_name = None
    if project.get("toiawase_id"):
        ta_response = db.table("master_toiawase").select("status_name").eq("id", project["toiawase_id"]).execute()
        if ta_response.data:
            toiawase_name = ta_response.data[0]["status_name"]

    sagyou_kubun_name = None
    if project.get("sagyou_kubun_id"):
        sk_response = db.table("master_sagyou_kubun").select("kubun_name").eq("id", project["sagyou_kubun_id"]).execute()
        if sk_response.data:
            sagyou_kubun_name = sk_response.data[0]["kubun_name"]

    shinchoku_name = None
    if project.get("shinchoku_id"):
        sc_response = db.table("master_shinchoku").select("status_name").eq("id", project["shinchoku_id"]).execute()
        if sc_response.data:
            shinchoku_name = sc_response.data[0]["status_name"]

    response_data = {
        **project,
        "machine_series_name": machine_series_name,
        "toiawase_name": toiawase_name,
        "sagyou_kubun_name": sagyou_kubun_name,
        "shinchoku_name": shinchoku_name,
    }

    return ProjectResponse(**response_data)