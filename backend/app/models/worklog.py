from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class WorkLog(Base):
    __tablename__ = "worklogs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False, index=True)
    start_time = Column(String, nullable=True)  # 開始時刻（HH:MM形式）
    end_time = Column(String, nullable=True)  # 終了時刻（HH:MM形式）
    duration_minutes = Column(Integer, nullable=False)  # 工数（分単位）
    work_content = Column(Text, nullable=True)  # 作業内容
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="worklogs")
    user = relationship("User")