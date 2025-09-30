from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class WorkLogBase(BaseModel):
    project_id: UUID = Field(..., description="案件ID")
    work_date: date = Field(..., description="作業日")
    start_time: Optional[str] = Field(None, description="開始時刻（HH:MM形式）")
    end_time: Optional[str] = Field(None, description="終了時刻（HH:MM形式）")
    duration_minutes: int = Field(..., gt=0, description="作業時間（分単位）")
    work_content: Optional[str] = Field(None, description="作業内容")


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    project_id: Optional[UUID] = None
    work_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    work_content: Optional[str] = None


class WorkLogResponse(WorkLogBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkLogListResponse(BaseModel):
    worklogs: list[WorkLogResponse]
    total: int
    page: int
    per_page: int