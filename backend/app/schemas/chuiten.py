from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# 注意点カテゴリ
class ChuitenCategoryBase(BaseModel):
    name: str = Field(..., description="カテゴリ名")
    sort_order: int = Field(default=0, description="並び順")


class ChuitenCategoryCreate(ChuitenCategoryBase):
    pass


class ChuitenCategory(ChuitenCategoryBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 注意点
class ChuitenBase(BaseModel):
    seq_no: int = Field(..., description="連番")
    target_series: Optional[str] = Field(None, description="対象シリーズ")
    target_model_pattern: Optional[str] = Field(None, description="対象機種パターン")
    category_id: Optional[UUID] = Field(None, description="カテゴリID")
    note: str = Field(..., description="注意点・留意点")
    author: Optional[str] = Field(None, description="記入者")
    remarks: Optional[str] = Field(None, description="備考")


class ChuitenCreate(ChuitenBase):
    pass


class ChuitenUpdate(BaseModel):
    seq_no: Optional[int] = Field(None, description="連番（変更時は重複注意）")
    target_series: Optional[str] = None
    target_model_pattern: Optional[str] = None
    category_id: Optional[UUID] = None
    note: Optional[str] = None
    author: Optional[str] = None
    remarks: Optional[str] = None


class Chuiten(ChuitenBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# カテゴリ付き注意点（結合結果）
class ChuitenWithCategory(Chuiten):
    category_name: Optional[str] = None
