from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class ProjectBase(BaseModel):
    management_no: str = Field(..., description="管理No")
    machine_series_id: Optional[UUID] = Field(None, description="機種シリーズID")
    generation: Optional[str] = Field(None, description="世代")
    tonnage: Optional[str] = Field(None, description="トン数")
    spec_tags: Optional[str] = Field(None, description="仕様タグ")
    machine_no: Optional[str] = Field(None, description="機番")
    commission_content: Optional[str] = Field(None, description="業務委託内容")
    toiawase_id: Optional[UUID] = Field(None, description="問い合わせID")
    sagyou_kubun_id: Optional[UUID] = Field(None, description="作業区分ID")
    estimated_hours: Optional[int] = Field(None, description="予定工数（分単位）")
    shinchoku_id: Optional[UUID] = Field(None, description="進捗ID")
    start_date: Optional[date] = Field(None, description="仕掛日")
    completion_date: Optional[date] = Field(None, description="完了日")
    drawing_deadline: Optional[date] = Field(None, description="作図期限")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    management_no: Optional[str] = None
    machine_series_id: Optional[UUID] = None
    generation: Optional[str] = None
    tonnage: Optional[str] = None
    spec_tags: Optional[str] = None
    machine_no: Optional[str] = None
    commission_content: Optional[str] = None
    toiawase_id: Optional[UUID] = None
    sagyou_kubun_id: Optional[UUID] = None
    estimated_hours: Optional[int] = None
    shinchoku_id: Optional[UUID] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    drawing_deadline: Optional[date] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: UUID
    actual_hours: int = Field(description="実績工数（分単位）")
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    # マスタ名称（JOIN結果）
    machine_series_name: Optional[str] = None
    toiawase_name: Optional[str] = None
    sagyou_kubun_name: Optional[str] = None
    shinchoku_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
    page: int
    per_page: int