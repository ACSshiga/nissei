from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    management_no = Column(String, unique=True, index=True, nullable=False)  # 管理No
    series = Column(String)  # シリーズ
    generation = Column(String)  # 世代
    tonnage = Column(String)  # トン数
    spec_tags = Column(String)  # 仕様タグ
    machine_no = Column(String, index=True)  # 機番
    commission_content = Column(Text)  # 業務委託内容
    inquiry_type = Column(String)  # 問い合わせ種別
    work_category = Column(String)  # 作業区分
    estimated_hours = Column(Integer)  # 予定工数（分単位）
    actual_hours = Column(Integer, default=0)  # 実績工数（分単位、自動集計）
    status = Column(String, default="進行中")  # ステータス
    start_date = Column(Date)  # 仕掛日
    completion_date = Column(Date)  # 完了日
    drawing_deadline = Column(Date)  # 作図期限
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    worklogs = relationship("WorkLog", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="project", cascade="all, delete-orphan")
    checklists = relationship("ChecklistItem", back_populates="project", cascade="all, delete-orphan")
    creator = relationship("User")