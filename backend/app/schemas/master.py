"""
マスタデータのスキーマ定義

進捗マスタ、作業区分マスタ、問い合わせマスタ、機種シリーズマスタのAPI用スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# 進捗マスタ
class MasterShinchokuBase(BaseModel):
    """進捗マスタの基本情報"""
    status_name: str = Field(..., max_length=100, description="進捗ステータス名")
    background_color: Optional[str] = Field(None, max_length=20, description="背景色（HEXコード）")
    completion_trigger: bool = Field(False, description="完了日トリガー")
    start_date_trigger: bool = Field(False, description="仕掛日トリガー")
    sort_order: int = Field(0, description="並び順")
    is_active: bool = Field(True, description="有効フラグ")


class MasterShinchokuCreate(MasterShinchokuBase):
    """進捗マスタ作成用"""
    pass


class MasterShinchokuUpdate(BaseModel):
    """進捗マスタ更新用"""
    status_name: Optional[str] = Field(None, max_length=100)
    background_color: Optional[str] = Field(None, max_length=20)
    completion_trigger: Optional[bool] = None
    start_date_trigger: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MasterShinchokuResponse(MasterShinchokuBase):
    """進捗マスタ応答用"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 作業区分マスタ
class MasterSagyouKubunBase(BaseModel):
    """作業区分マスタの基本情報"""
    kubun_name: str = Field(..., max_length=100, description="作業区分名")
    background_color: Optional[str] = Field(None, max_length=20, description="背景色（HEXコード）")
    sort_order: int = Field(0, description="並び順")
    is_active: bool = Field(True, description="有効フラグ")


class MasterSagyouKubunCreate(MasterSagyouKubunBase):
    """作業区分マスタ作成用"""
    pass


class MasterSagyouKubunUpdate(BaseModel):
    """作業区分マスタ更新用"""
    kubun_name: Optional[str] = Field(None, max_length=100)
    background_color: Optional[str] = Field(None, max_length=20)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MasterSagyouKubunResponse(MasterSagyouKubunBase):
    """作業区分マスタ応答用"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 問い合わせマスタ
class MasterToiawaseBase(BaseModel):
    """問い合わせマスタの基本情報"""
    status_name: str = Field(..., max_length=100, description="問い合わせステータス名")
    background_color: Optional[str] = Field(None, max_length=20, description="背景色（HEXコード）")
    sort_order: int = Field(0, description="並び順")
    is_active: bool = Field(True, description="有効フラグ")


class MasterToiawaseCreate(MasterToiawaseBase):
    """問い合わせマスタ作成用"""
    pass


class MasterToiawaseUpdate(BaseModel):
    """問い合わせマスタ更新用"""
    status_name: Optional[str] = Field(None, max_length=100)
    background_color: Optional[str] = Field(None, max_length=20)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MasterToiawaseResponse(MasterToiawaseBase):
    """問い合わせマスタ応答用"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 機種シリーズマスタ
class MachineSeriesMasterBase(BaseModel):
    """機種シリーズマスタの基本情報"""
    series_name: str = Field(..., max_length=50, description="シリーズ名")
    display_name: str = Field(..., max_length=100, description="表示名")
    description: Optional[str] = Field(None, max_length=500, description="説明")
    category: Optional[str] = Field(None, max_length=50, description="カテゴリ（標準/特殊）")
    checklist_template_category: Optional[str] = Field(None, max_length=50, description="注意点テンプレート紐付け")
    sort_order: int = Field(0, description="並び順")
    is_active: bool = Field(True, description="有効フラグ")


class MachineSeriesMasterCreate(MachineSeriesMasterBase):
    """機種シリーズマスタ作成用"""
    pass


class MachineSeriesMasterUpdate(BaseModel):
    """機種シリーズマスタ更新用"""
    series_name: Optional[str] = Field(None, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    checklist_template_category: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MachineSeriesMasterResponse(MachineSeriesMasterBase):
    """機種シリーズマスタ応答用"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True