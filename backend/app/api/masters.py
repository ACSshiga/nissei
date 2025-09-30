"""
マスタ管理API

進捗マスタ、作業区分マスタ、問い合わせマスタ、機種シリーズマスタのCRUD操作
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List, Dict, Any
from uuid import UUID
import uuid

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.master import (
    MasterShinchokuCreate,
    MasterShinchokuUpdate,
    MasterShinchokuResponse,
    MasterSagyouKubunCreate,
    MasterSagyouKubunUpdate,
    MasterSagyouKubunResponse,
    MasterToiawaseCreate,
    MasterToiawaseUpdate,
    MasterToiawaseResponse,
    MachineSeriesMasterCreate,
    MachineSeriesMasterUpdate,
    MachineSeriesMasterResponse
)

router = APIRouter(prefix="/api/masters", tags=["masters"])


# ==================== 進捗マスタ ====================

@router.get("/shinchoku", response_model=List[MasterShinchokuResponse])
def list_shinchoku(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """進捗マスタ一覧取得"""
    query = db.table("master_shinchoku").select("*")
    if not include_inactive:
        query = query.eq("is_active", True)

    response = query.order("sort_order").range(skip, skip + limit - 1).execute()
    return response.data


@router.post("/shinchoku", response_model=MasterShinchokuResponse, status_code=status.HTTP_201_CREATED)
def create_shinchoku(
    data: MasterShinchokuCreate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """進捗マスタ作成"""
    # 重複チェック
    existing = db.table("master_shinchoku").select("id").eq("status_name", data.status_name).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このステータス名は既に登録されています"
        )

    new_item = {
        "id": str(uuid.uuid4()),
        **data.model_dump(mode="json")
    }
    response = db.table("master_shinchoku").insert(new_item).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="進捗マスタの作成に失敗しました"
        )

    return response.data[0]


@router.get("/shinchoku/{item_id}", response_model=MasterShinchokuResponse)
def get_shinchoku(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """進捗マスタ詳細取得"""
    response = db.table("master_shinchoku").select("*").eq("id", str(item_id)).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="進捗マスタが見つかりません"
        )
    return response.data[0]


@router.put("/shinchoku/{item_id}", response_model=MasterShinchokuResponse)
def update_shinchoku(
    item_id: UUID,
    data: MasterShinchokuUpdate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """進捗マスタ更新"""
    item_response = db.table("master_shinchoku").select("*").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="進捗マスタが見つかりません"
        )

    item = item_response.data[0]

    # 重複チェック（status_nameが更新される場合）
    if data.status_name and data.status_name != item["status_name"]:
        existing = db.table("master_shinchoku").select("id").eq("status_name", data.status_name).neq("id", str(item_id)).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このステータス名は既に登録されています"
            )

    # 更新
    update_data = data.model_dump(exclude_unset=True, mode="json")
    response = db.table("master_shinchoku").update(update_data).eq("id", str(item_id)).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="進捗マスタの更新に失敗しました"
        )

    return response.data[0]


@router.delete("/shinchoku/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shinchoku(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """進捗マスタ論理削除"""
    item_response = db.table("master_shinchoku").select("id").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="進捗マスタが見つかりません"
        )

    db.table("master_shinchoku").update({"is_active": False}).eq("id", str(item_id)).execute()
    return None


# ==================== 作業区分マスタ ====================

@router.get("/sagyou-kubun", response_model=List[MasterSagyouKubunResponse])
def list_sagyou_kubun(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """作業区分マスタ一覧取得"""
    query = db.table("master_sagyou_kubun").select("*")
    if not include_inactive:
        query = query.eq("is_active", True)

    response = query.order("sort_order").range(skip, skip + limit - 1).execute()
    return response.data


@router.post("/sagyou-kubun", response_model=MasterSagyouKubunResponse, status_code=status.HTTP_201_CREATED)
def create_sagyou_kubun(
    data: MasterSagyouKubunCreate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """作業区分マスタ作成"""
    # 重複チェック
    existing = db.table("master_sagyou_kubun").select("id").eq("kubun_name", data.kubun_name).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この作業区分名は既に登録されています"
        )

    new_item = {
        "id": str(uuid.uuid4()),
        **data.model_dump(mode="json")
    }
    response = db.table("master_sagyou_kubun").insert(new_item).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="作業区分マスタの作成に失敗しました"
        )

    return response.data[0]


@router.get("/sagyou-kubun/{item_id}", response_model=MasterSagyouKubunResponse)
def get_sagyou_kubun(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """作業区分マスタ詳細取得"""
    response = db.table("master_sagyou_kubun").select("*").eq("id", str(item_id)).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作業区分マスタが見つかりません"
        )
    return response.data[0]


@router.put("/sagyou-kubun/{item_id}", response_model=MasterSagyouKubunResponse)
def update_sagyou_kubun(
    item_id: UUID,
    data: MasterSagyouKubunUpdate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """作業区分マスタ更新"""
    item_response = db.table("master_sagyou_kubun").select("*").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作業区分マスタが見つかりません"
        )

    item = item_response.data[0]

    # 重複チェック
    if data.kubun_name and data.kubun_name != item["kubun_name"]:
        existing = db.table("master_sagyou_kubun").select("id").eq("kubun_name", data.kubun_name).neq("id", str(item_id)).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="この作業区分名は既に登録されています"
            )

    update_data = data.model_dump(exclude_unset=True, mode="json")
    response = db.table("master_sagyou_kubun").update(update_data).eq("id", str(item_id)).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="作業区分マスタの更新に失敗しました"
        )

    return response.data[0]


@router.delete("/sagyou-kubun/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sagyou_kubun(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """作業区分マスタ論理削除"""
    item_response = db.table("master_sagyou_kubun").select("id").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作業区分マスタが見つかりません"
        )

    db.table("master_sagyou_kubun").update({"is_active": False}).eq("id", str(item_id)).execute()
    return None


# ==================== 問い合わせマスタ ====================

@router.get("/toiawase", response_model=List[MasterToiawaseResponse])
def list_toiawase(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """問い合わせマスタ一覧取得"""
    query = db.table("master_toiawase").select("*")
    if not include_inactive:
        query = query.eq("is_active", True)

    response = query.order("sort_order").range(skip, skip + limit - 1).execute()
    return response.data


@router.post("/toiawase", response_model=MasterToiawaseResponse, status_code=status.HTTP_201_CREATED)
def create_toiawase(
    data: MasterToiawaseCreate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """問い合わせマスタ作成"""
    # 重複チェック
    existing = db.table("master_toiawase").select("id").eq("status_name", data.status_name).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このステータス名は既に登録されています"
        )

    new_item = {
        "id": str(uuid.uuid4()),
        **data.model_dump(mode="json")
    }
    response = db.table("master_toiawase").insert(new_item).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="問い合わせマスタの作成に失敗しました"
        )

    return response.data[0]


@router.get("/toiawase/{item_id}", response_model=MasterToiawaseResponse)
def get_toiawase(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """問い合わせマスタ詳細取得"""
    response = db.table("master_toiawase").select("*").eq("id", str(item_id)).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせマスタが見つかりません"
        )
    return response.data[0]


@router.put("/toiawase/{item_id}", response_model=MasterToiawaseResponse)
def update_toiawase(
    item_id: UUID,
    data: MasterToiawaseUpdate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """問い合わせマスタ更新"""
    item_response = db.table("master_toiawase").select("*").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせマスタが見つかりません"
        )

    item = item_response.data[0]

    # 重複チェック
    if data.status_name and data.status_name != item["status_name"]:
        existing = db.table("master_toiawase").select("id").eq("status_name", data.status_name).neq("id", str(item_id)).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このステータス名は既に登録されています"
            )

    update_data = data.model_dump(exclude_unset=True, mode="json")
    response = db.table("master_toiawase").update(update_data).eq("id", str(item_id)).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="問い合わせマスタの更新に失敗しました"
        )

    return response.data[0]


@router.delete("/toiawase/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_toiawase(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """問い合わせマスタ論理削除"""
    item_response = db.table("master_toiawase").select("id").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせマスタが見つかりません"
        )

    db.table("master_toiawase").update({"is_active": False}).eq("id", str(item_id)).execute()
    return None


# ==================== 機種シリーズマスタ ====================

@router.get("/machine-series", response_model=List[MachineSeriesMasterResponse])
def list_machine_series(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """機種シリーズマスタ一覧取得"""
    query = db.table("machine_series_master").select("*")
    if not include_inactive:
        query = query.eq("is_active", True)

    response = query.order("sort_order").range(skip, skip + limit - 1).execute()
    return response.data


@router.post("/machine-series", response_model=MachineSeriesMasterResponse, status_code=status.HTTP_201_CREATED)
def create_machine_series(
    data: MachineSeriesMasterCreate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """機種シリーズマスタ作成"""
    # 重複チェック
    existing = db.table("machine_series_master").select("id").eq("series_name", data.series_name).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このシリーズ名は既に登録されています"
        )

    new_item = {
        "id": str(uuid.uuid4()),
        **data.model_dump(mode="json")
    }
    response = db.table("machine_series_master").insert(new_item).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="機種シリーズマスタの作成に失敗しました"
        )

    return response.data[0]


@router.get("/machine-series/{item_id}", response_model=MachineSeriesMasterResponse)
def get_machine_series(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """機種シリーズマスタ詳細取得"""
    response = db.table("machine_series_master").select("*").eq("id", str(item_id)).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="機種シリーズマスタが見つかりません"
        )
    return response.data[0]


@router.put("/machine-series/{item_id}", response_model=MachineSeriesMasterResponse)
def update_machine_series(
    item_id: UUID,
    data: MachineSeriesMasterUpdate,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """機種シリーズマスタ更新"""
    item_response = db.table("machine_series_master").select("*").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="機種シリーズマスタが見つかりません"
        )

    item = item_response.data[0]

    # 重複チェック
    if data.series_name and data.series_name != item["series_name"]:
        existing = db.table("machine_series_master").select("id").eq("series_name", data.series_name).neq("id", str(item_id)).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このシリーズ名は既に登録されています"
            )

    update_data = data.model_dump(exclude_unset=True, mode="json")
    response = db.table("machine_series_master").update(update_data).eq("id", str(item_id)).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="機種シリーズマスタの更新に失敗しました"
        )

    return response.data[0]


@router.delete("/machine-series/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine_series(
    item_id: UUID,
    db: Client = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """機種シリーズマスタ論理削除"""
    item_response = db.table("machine_series_master").select("id").eq("id", str(item_id)).execute()
    if not item_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="機種シリーズマスタが見つかりません"
        )

    db.table("machine_series_master").update({"is_active": False}).eq("id", str(item_id)).execute()
    return None