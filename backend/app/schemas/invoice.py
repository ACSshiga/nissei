from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class InvoiceItemBase(BaseModel):
    management_no: str = Field(..., description="管理No")
    machine_no: str = Field(..., description="機番")
    actual_hours: Decimal = Field(..., description="実工数")
    sort_order: int = Field(default=0, description="並び順")


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: UUID
    invoice_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    invoice_number: str = Field(..., description="請求書番号")
    issue_date: date = Field(..., description="発行日")
    status: str = Field(default='draft', description="ステータス")


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = Field(default=[], description="請求書明細")


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: UUID
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


# 請求プレビュー用のレスポンス
class InvoicePreviewItem(BaseModel):
    management_no: str
    machine_no: str
    actual_hours: Decimal


class InvoicePreviewResponse(BaseModel):
    month: str  # YYYY-MM形式
    total_hours: Decimal
    items: List[InvoicePreviewItem]
