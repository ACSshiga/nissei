from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.auth import get_current_user, require_admin
from app.schemas.chuiten import (
    ChuitenCreate,
    ChuitenUpdate,
    Chuiten,
    ChuitenWithCategory,
    ChuitenCategoryCreate,
    ChuitenCategory,
)

router = APIRouter()


# ==================== カテゴリ管理 ====================

@router.get("/categories", response_model=List[ChuitenCategory])
def list_chuiten_categories(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """注意点カテゴリ一覧を取得"""
    result = db.table("master_chuiten_category").select("*").order("sort_order").execute()
    return result.data or []


@router.post("/categories", response_model=ChuitenCategory)
def create_chuiten_category(
    category: ChuitenCategoryCreate,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """注意点カテゴリを追加（管理者のみ）"""
    try:
        category_data = category.model_dump(mode="json")
        result = db.table("master_chuiten_category").insert(category_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="カテゴリの追加に失敗しました")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Category creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="カテゴリの追加に失敗しました"
        )


# ==================== 注意点管理 ====================

@router.get("", response_model=List[ChuitenWithCategory])
def list_chuiten(
    series: Optional[str] = Query(None, description="対象シリーズで絞り込み"),
    category_id: Optional[UUID] = Query(None, description="カテゴリIDで絞り込み"),
    keyword: Optional[str] = Query(None, description="キーワード検索（注意点内容）"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """注意点一覧を取得"""
    try:
        # JOINでカテゴリ名も取得
        query = db.table("master_chuiten").select("""
            *,
            master_chuiten_category(name)
        """)

        if series:
            query = query.eq("target_series", series)

        if category_id:
            query = query.eq("category_id", str(category_id))

        if keyword:
            query = query.ilike("note", f"%{keyword}%")

        result = query.order("seq_no").execute()

        # カテゴリ名を展開
        items = []
        for item in result.data or []:
            category_info = item.pop("master_chuiten_category", None)
            chuiten_data = {
                **item,
                "category_name": category_info["name"] if category_info else None
            }
            items.append(ChuitenWithCategory(**chuiten_data))

        return items

    except Exception as e:
        logger.error(f"Chuiten list failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="注意点一覧の取得に失敗しました"
        )


@router.post("", response_model=Chuiten)
def create_chuiten(
    chuiten: ChuitenCreate,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """注意点を追加（管理者のみ）"""
    try:
        chuiten_data = chuiten.model_dump(mode="json", exclude_none=True)

        # category_idをstr変換
        if "category_id" in chuiten_data and chuiten_data["category_id"]:
            chuiten_data["category_id"] = str(chuiten_data["category_id"])

        result = db.table("master_chuiten").insert(chuiten_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="注意点の追加に失敗しました")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chuiten creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="注意点の追加に失敗しました"
        )


@router.get("/{chuiten_id}", response_model=ChuitenWithCategory)
def get_chuiten(
    chuiten_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """注意点詳細を取得"""
    try:
        result = db.table("master_chuiten").select("""
            *,
            master_chuiten_category(name)
        """).eq("id", str(chuiten_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="注意点が見つかりません")

        item = result.data[0]
        category_info = item.pop("master_chuiten_category", None)
        chuiten_data = {
            **item,
            "category_name": category_info["name"] if category_info else None
        }

        return ChuitenWithCategory(**chuiten_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chuiten failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="注意点の取得に失敗しました"
        )


@router.patch("/{chuiten_id}", response_model=Chuiten)
def update_chuiten(
    chuiten_id: UUID,
    chuiten: ChuitenUpdate,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """注意点を更新（管理者のみ）"""
    try:
        # 既存チェック
        existing = db.table("master_chuiten").select("*").eq("id", str(chuiten_id)).execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="注意点が見つかりません")

        # 更新
        update_dict = chuiten.model_dump(exclude_unset=True, mode="json")

        # category_idをstr変換
        if "category_id" in update_dict and update_dict["category_id"]:
            update_dict["category_id"] = str(update_dict["category_id"])

        update_dict["updated_at"] = datetime.utcnow().isoformat()

        updated_response = db.table("master_chuiten").update(update_dict).eq(
            "id", str(chuiten_id)
        ).execute()

        if not updated_response.data:
            raise HTTPException(status_code=500, detail="注意点の更新に失敗しました")

        return updated_response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chuiten update failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="注意点の更新に失敗しました"
        )


@router.delete("/{chuiten_id}")
def delete_chuiten(
    chuiten_id: UUID,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """注意点を削除（管理者のみ）"""
    # 既存チェック
    existing = db.table("master_chuiten").select("*").eq("id", str(chuiten_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="注意点が見つかりません")

    # 削除
    db.table("master_chuiten").delete().eq("id", str(chuiten_id)).execute()

    return {"message": "注意点を削除しました"}


# ==================== 案件関連注意点取得 ====================

@router.get("/by-project/{project_id}", response_model=List[ChuitenWithCategory])
def get_chuiten_by_project(
    project_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件に関連する注意点を取得"""
    try:
        # プロジェクト情報を取得
        project = db.table("projects").select("machine_no, model").eq(
            "id", str(project_id)
        ).execute()

        if not project.data:
            raise HTTPException(status_code=404, detail="案件が見つかりません")

        # machine_noやmodelから対象シリーズを推定
        # 簡易実装: modelからシリーズ名を抽出（例: NEX140Ⅲ → NEX）
        model = project.data[0].get("model", "")
        series = None

        if model:
            # 先頭の英字部分をシリーズとする
            for i, char in enumerate(model):
                if not char.isalpha():
                    series = model[:i]
                    break
            if not series:
                series = model

        # 関連する注意点を取得
        query = db.table("master_chuiten").select("""
            *,
            master_chuiten_category(name)
        """)

        if series:
            query = query.eq("target_series", series)

        result = query.order("seq_no").execute()

        # カテゴリ名を展開
        items = []
        for item in result.data or []:
            category_info = item.pop("master_chuiten_category", None)
            chuiten_data = {
                **item,
                "category_name": category_info["name"] if category_info else None
            }
            items.append(ChuitenWithCategory(**chuiten_data))

        return items

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chuiten by project failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="案件関連注意点の取得に失敗しました"
        )
