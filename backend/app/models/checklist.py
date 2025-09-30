from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String, nullable=False, index=True)  # 機種タグ
    title = Column(String, nullable=False)
    priority = Column(Integer, default=0)  # 重要度（0-10）
    is_required = Column(Boolean, default=False)  # 必須項目フラグ
    description = Column(Text)  # 補足コメント
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("checklist_templates.id"))
    title = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    is_required = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    completed_at = Column(DateTime)
    memo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="checklists")
    template = relationship("ChecklistTemplate")
    completed_user = relationship("User")