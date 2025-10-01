from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user

router = APIRouter()


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """管理者権限チェック"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="管理者権限が必要です")
    return current_user


@router.get("/users")
def list_users(
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """全ユーザー一覧取得（管理者のみ）"""
    response = db.table("users").select("id, email, username, is_active, is_admin, created_at").execute()
    return {"users": response.data}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """ユーザー削除（管理者のみ）"""
    # 自分自身は削除できない
    if str(user_id) == current_user["id"]:
        raise HTTPException(status_code=400, detail="自分自身は削除できません")

    # ユーザーの存在確認
    user_response = db.table("users").select("id, username").eq("id", str(user_id)).execute()
    if not user_response.data:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # ユーザー削除
    db.table("users").delete().eq("id", str(user_id)).execute()

    return {"message": f"ユーザー {user_response.data[0]['username']} を削除しました"}


@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """ユーザーをアクティブ化（管理者のみ）"""
    response = db.table("users").update({"is_active": True}).eq("id", str(user_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return {"message": "ユーザーをアクティブ化しました"}


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """ユーザーを非アクティブ化（管理者のみ）"""
    # 自分自身は非アクティブ化できない
    if str(user_id) == current_user["id"]:
        raise HTTPException(status_code=400, detail="自分自身は非アクティブ化できません")

    response = db.table("users").update({"is_active": False}).eq("id", str(user_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return {"message": "ユーザーを非アクティブ化しました"}
