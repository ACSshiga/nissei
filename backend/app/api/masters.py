"""
マスタ管理API

進捗マスタ、作業区分マスタ、問い合わせマスタ、機種シリーズマスタのCRUD操作
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.master import (
    MasterShinchoku,
    MasterSagyouKubun,
    MasterToiawase,
    MachineSeriesMaster
)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """進捗マスタ一覧取得"""
    query = db.query(MasterShinchoku)
    if not include_inactive:
        query = query.filter(MasterShinchoku.is_active == True)
    query = query.order_by(MasterShinchoku.sort_order)
    return query.offset(skip).limit(limit).all()


@router.post("/shinchoku", response_model=MasterShinchokuResponse, status_code=status.HTTP_201_CREATED)
def create_shinchoku(
    data: MasterShinchokuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """進捗マスタ作成"""
    # 重複チェック
    existing = db.query(MasterShinchoku).filter(
        MasterShinchoku.status_name == data.status_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このステータス名は既に登録されています"
        )

    new_item = MasterShinchoku(**data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/shinchoku/{item_id}", response_model=MasterShinchokuResponse)
def get_shinchoku(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """進捗マスタ詳細取得"""
    item = db.query(MasterShinchoku).filter(MasterShinchoku.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="進捗マスタが見つかりません"
        )
    return item


@router.put("/shinchoku/{item_id}", response_model=MasterShinchokuResponse)
def update_shinchoku(
    item_id: UUID,
    data: MasterShinchokuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """進捗マスタ更新"""
    item = db.query(MasterShinchoku).filter(MasterShinchoku.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="進捗マスタが見つかりません"
        )

    # 重複チェック（status_nameが更新される場合）
    if data.status_name and data.status_name != item.status_name:
        existing = db.query(MasterShinchoku).filter(
            MasterShinchoku.status_name == data.status_name,
            MasterShinchoku.id != item_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このステータス名は既に登録されています"
            )

    # 更新
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/shinchoku/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shinchoku(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """進捗マスタ論理削除"""
    item = db.query(MasterShinchoku).filter(MasterShinchoku.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="進捗マスタが見つかりません"
        )

    item.is_active = False
    db.commit()
    return None


# ==================== 作業区分マスタ ====================

@router.get("/sagyou-kubun", response_model=List[MasterSagyouKubunResponse])
def list_sagyou_kubun(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """作業区分マスタ一覧取得"""
    query = db.query(MasterSagyouKubun)
    if not include_inactive:
        query = query.filter(MasterSagyouKubun.is_active == True)
    query = query.order_by(MasterSagyouKubun.sort_order)
    return query.offset(skip).limit(limit).all()


@router.post("/sagyou-kubun", response_model=MasterSagyouKubunResponse, status_code=status.HTTP_201_CREATED)
def create_sagyou_kubun(
    data: MasterSagyouKubunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """作業区分マスタ作成"""
    # 重複チェック
    existing = db.query(MasterSagyouKubun).filter(
        MasterSagyouKubun.kubun_name == data.kubun_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この作業区分名は既に登録されています"
        )

    new_item = MasterSagyouKubun(**data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/sagyou-kubun/{item_id}", response_model=MasterSagyouKubunResponse)
def get_sagyou_kubun(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """作業区分マスタ詳細取得"""
    item = db.query(MasterSagyouKubun).filter(MasterSagyouKubun.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作業区分マスタが見つかりません"
        )
    return item


@router.put("/sagyou-kubun/{item_id}", response_model=MasterSagyouKubunResponse)
def update_sagyou_kubun(
    item_id: UUID,
    data: MasterSagyouKubunUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """作業区分マスタ更新"""
    item = db.query(MasterSagyouKubun).filter(MasterSagyouKubun.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作業区分マスタが見つかりません"
        )

    # 重複チェック
    if data.kubun_name and data.kubun_name != item.kubun_name:
        existing = db.query(MasterSagyouKubun).filter(
            MasterSagyouKubun.kubun_name == data.kubun_name,
            MasterSagyouKubun.id != item_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="この作業区分名は既に登録されています"
            )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/sagyou-kubun/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sagyou_kubun(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """作業区分マスタ論理削除"""
    item = db.query(MasterSagyouKubun).filter(MasterSagyouKubun.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作業区分マスタが見つかりません"
        )

    item.is_active = False
    db.commit()
    return None


# ==================== 問い合わせマスタ ====================

@router.get("/toiawase", response_model=List[MasterToiawaseResponse])
def list_toiawase(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """問い合わせマスタ一覧取得"""
    query = db.query(MasterToiawase)
    if not include_inactive:
        query = query.filter(MasterToiawase.is_active == True)
    query = query.order_by(MasterToiawase.sort_order)
    return query.offset(skip).limit(limit).all()


@router.post("/toiawase", response_model=MasterToiawaseResponse, status_code=status.HTTP_201_CREATED)
def create_toiawase(
    data: MasterToiawaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """問い合わせマスタ作成"""
    # 重複チェック
    existing = db.query(MasterToiawase).filter(
        MasterToiawase.status_name == data.status_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このステータス名は既に登録されています"
        )

    new_item = MasterToiawase(**data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/toiawase/{item_id}", response_model=MasterToiawaseResponse)
def get_toiawase(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """問い合わせマスタ詳細取得"""
    item = db.query(MasterToiawase).filter(MasterToiawase.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせマスタが見つかりません"
        )
    return item


@router.put("/toiawase/{item_id}", response_model=MasterToiawaseResponse)
def update_toiawase(
    item_id: UUID,
    data: MasterToiawaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """問い合わせマスタ更新"""
    item = db.query(MasterToiawase).filter(MasterToiawase.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせマスタが見つかりません"
        )

    # 重複チェック
    if data.status_name and data.status_name != item.status_name:
        existing = db.query(MasterToiawase).filter(
            MasterToiawase.status_name == data.status_name,
            MasterToiawase.id != item_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このステータス名は既に登録されています"
            )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/toiawase/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_toiawase(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """問い合わせマスタ論理削除"""
    item = db.query(MasterToiawase).filter(MasterToiawase.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせマスタが見つかりません"
        )

    item.is_active = False
    db.commit()
    return None


# ==================== 機種シリーズマスタ ====================

@router.get("/machine-series", response_model=List[MachineSeriesMasterResponse])
def list_machine_series(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """機種シリーズマスタ一覧取得"""
    query = db.query(MachineSeriesMaster)
    if not include_inactive:
        query = query.filter(MachineSeriesMaster.is_active == True)
    query = query.order_by(MachineSeriesMaster.sort_order)
    return query.offset(skip).limit(limit).all()


@router.post("/machine-series", response_model=MachineSeriesMasterResponse, status_code=status.HTTP_201_CREATED)
def create_machine_series(
    data: MachineSeriesMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """機種シリーズマスタ作成"""
    # 重複チェック
    existing = db.query(MachineSeriesMaster).filter(
        MachineSeriesMaster.series_name == data.series_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このシリーズ名は既に登録されています"
        )

    new_item = MachineSeriesMaster(**data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/machine-series/{item_id}", response_model=MachineSeriesMasterResponse)
def get_machine_series(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """機種シリーズマスタ詳細取得"""
    item = db.query(MachineSeriesMaster).filter(MachineSeriesMaster.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="機種シリーズマスタが見つかりません"
        )
    return item


@router.put("/machine-series/{item_id}", response_model=MachineSeriesMasterResponse)
def update_machine_series(
    item_id: UUID,
    data: MachineSeriesMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """機種シリーズマスタ更新"""
    item = db.query(MachineSeriesMaster).filter(MachineSeriesMaster.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="機種シリーズマスタが見つかりません"
        )

    # 重複チェック
    if data.series_name and data.series_name != item.series_name:
        existing = db.query(MachineSeriesMaster).filter(
            MachineSeriesMaster.series_name == data.series_name,
            MachineSeriesMaster.id != item_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このシリーズ名は既に登録されています"
            )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/machine-series/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine_series(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """機種シリーズマスタ論理削除"""
    item = db.query(MachineSeriesMaster).filter(MachineSeriesMaster.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="機種シリーズマスタが見つかりません"
        )

    item.is_active = False
    db.commit()
    return None