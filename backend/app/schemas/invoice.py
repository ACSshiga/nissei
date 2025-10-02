from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# 請求書明細
class InvoiceItemBase(BaseModel):
    project_id: UUID = Field(..., description="案件ID")
    management_no: str = Field(..., description="管理No")
    work_content: str = Field(..., description="委託業務内容（機番）")
    total_hours: Decimal = Field(..., description="実工数（時間）")


class InvoiceItem(InvoiceItemBase):
    id: UUID
    invoice_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 請求書ヘッダ
class InvoiceBase(BaseModel):
    year: int = Field(..., description="年")
    month: int = Field(..., ge=1, le=12, description="月")


class Invoice(InvoiceBase):
    id: UUID
    status: str = Field(..., description="ステータス: draft | closed")
    closed_at: Optional[datetime] = None
    closed_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# プレビュー用（明細付き）
class InvoicePreview(Invoice):
    items: List[InvoiceItem] = []
