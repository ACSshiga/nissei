from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.checklist import (
    ChecklistCreate,
    ChecklistUpdate,
    ChecklistResponse,
)

router = APIRouter()


@router.post("", response_model=ChecklistResponse)
def create_checklist(
    checklist: ChecklistCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """チェックリスト項目を作成"""
    try:
        # プロジェクトの存在確認
        project_response = db.table("projects").select("id").eq(
            "id", str(checklist.project_id)
        ).execute()

        if not project_response.data:
            raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

        # チェックリスト項目を作成
        checklist_data = checklist.model_dump(mode="json")
        checklist_data["project_id"] = str(checklist.project_id)

        result = db.table("checklists").insert(checklist_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="チェックリスト項目の作成に失敗しました")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checklist creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="チェックリスト項目の作成に失敗しました"
        )


@router.get("", response_model=List[ChecklistResponse])
def list_checklists(
    project_id: Optional[UUID] = Query(None, description="プロジェクトIDで絞り込み"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """チェックリスト一覧を取得"""
    try:
        query = db.table("checklists").select("*")

        if project_id:
            query = query.eq("project_id", str(project_id))

        query = query.order("sort_order").order("created_at")

        result = query.execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Checklist list failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="チェックリスト一覧の取得に失敗しました"
        )


@router.get("/{checklist_id}", response_model=ChecklistResponse)
def get_checklist(
    checklist_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """チェックリスト項目詳細を取得"""
    result = db.table("checklists").select("*").eq("id", str(checklist_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="チェックリスト項目が見つかりません")

    return result.data[0]


@router.patch("/{checklist_id}", response_model=ChecklistResponse)
def update_checklist(
    checklist_id: UUID,
    checklist_data: ChecklistUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """チェックリスト項目を更新"""
    # 既存のチェックリスト項目を確認
    existing = db.table("checklists").select("*").eq("id", str(checklist_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="チェックリスト項目が見つかりません")

    # 更新
    update_dict = checklist_data.model_dump(exclude_unset=True, mode="json")
    update_dict["updated_at"] = datetime.utcnow().isoformat()

    updated_response = db.table("checklists").update(update_dict).eq(
        "id", str(checklist_id)
    ).execute()

    if not updated_response.data:
        raise HTTPException(status_code=500, detail="チェックリスト項目の更新に失敗しました")

    return updated_response.data[0]


@router.delete("/{checklist_id}")
def delete_checklist(
    checklist_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """チェックリスト項目を削除"""
    # 既存のチェックリスト項目を確認
    existing = db.table("checklists").select("*").eq("id", str(checklist_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="チェックリスト項目が見つかりません")

    # 削除
    db.table("checklists").delete().eq("id", str(checklist_id)).execute()

    return {"message": "チェックリスト項目を削除しました"}


@router.post("/{checklist_id}/toggle", response_model=ChecklistResponse)
def toggle_checklist_completed(
    checklist_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """チェックリスト項目の完了状態をトグル"""
    # 既存のチェックリスト項目を確認
    existing = db.table("checklists").select("*").eq("id", str(checklist_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="チェックリスト項目が見つかりません")

    checklist = existing.data[0]
    new_status = not checklist["is_completed"]

    # 更新
    updated_response = db.table("checklists").update({
        "is_completed": new_status,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", str(checklist_id)).execute()

    if not updated_response.data:
        raise HTTPException(status_code=500, detail="チェックリスト項目の更新に失敗しました")

    return updated_response.data[0]
