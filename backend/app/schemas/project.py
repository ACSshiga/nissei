from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class ProjectBase(BaseModel):
    management_no: str = Field(..., description="管理No")
    series: Optional[str] = Field(None, description="シリーズ")
    generation: Optional[str] = Field(None, description="世代")
    tonnage: Optional[str] = Field(None, description="トン数")
    spec_tags: Optional[str] = Field(None, description="仕様タグ")
    machine_no: Optional[str] = Field(None, description="機番")
    commission_content: Optional[str] = Field(None, description="業務委託内容")
    inquiry_type: Optional[str] = Field(None, description="問い合わせ種別")
    work_category: Optional[str] = Field(None, description="作業区分")
    estimated_hours: Optional[int] = Field(None, description="予定工数（分単位）")
    status: str = Field(default="進行中", description="ステータス")
    start_date: Optional[date] = Field(None, description="開始日")
    completion_date: Optional[date] = Field(None, description="完了日")
    drawing_deadline: Optional[date] = Field(None, description="図面締め切り日")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    management_no: Optional[str] = None
    series: Optional[str] = None
    generation: Optional[str] = None
    tonnage: Optional[str] = None
    spec_tags: Optional[str] = None
    machine_no: Optional[str] = None
    commission_content: Optional[str] = None
    inquiry_type: Optional[str] = None
    work_category: Optional[str] = None
    estimated_hours: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    drawing_deadline: Optional[date] = None


class ProjectResponse(ProjectBase):
    id: UUID
    actual_hours: int = Field(description="実績工数（分単位）")
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
    page: int
    per_page: int