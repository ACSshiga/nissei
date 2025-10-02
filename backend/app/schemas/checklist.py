from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ChecklistBase(BaseModel):
    title: str = Field(..., description="チェックリスト項目タイトル")
    is_completed: bool = Field(default=False, description="完了フラグ")
    sort_order: int = Field(default=0, description="並び順")


class ChecklistCreate(ChecklistBase):
    project_id: UUID = Field(..., description="プロジェクトID")


class ChecklistUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    sort_order: Optional[int] = None


class ChecklistResponse(ChecklistBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
