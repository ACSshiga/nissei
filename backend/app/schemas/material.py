from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class MaterialBase(BaseModel):
    title: str = Field(..., description="資料タイトル")
    machine_no: Optional[str] = Field(None, description="特定機番（scope=machineの場合）")
    model: Optional[str] = Field(None, description="特定機種（scope=modelの場合）")
    scope: str = Field(..., description="スコープレベル: machine, model, tonnage, series")
    series: str = Field(..., description="シリーズ名（NEX, HMX等）")
    tonnage: Optional[int] = Field(None, description="トン数（scope=tonnageの場合）")
    file_path: str = Field(..., description="ファイルパス")
    file_size: Optional[int] = Field(None, description="ファイルサイズ（バイト）")


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: UUID
    uploaded_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialSearchParams(BaseModel):
    """資料検索パラメータ"""
    machine_no: Optional[str] = Field(None, description="機番で検索")
    model: Optional[str] = Field(None, description="機種で検索")
    series: Optional[str] = Field(None, description="シリーズで検索")
    tonnage: Optional[int] = Field(None, description="トン数で検索")
    scope: Optional[str] = Field(None, description="スコープで絞り込み")
