from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    management_no = Column(String, unique=True, index=True, nullable=False)  # 管理No

    # 機種情報
    machine_series_id = Column(UUID(as_uuid=True), ForeignKey("machine_series_master.id"), nullable=True)  # 機種シリーズマスタ参照
    generation = Column(String)  # 世代
    tonnage = Column(String)  # トン数
    spec_tags = Column(String)  # 仕様タグ
    machine_no = Column(String, index=True)  # 機番

    # 案件情報
    commission_content = Column(Text)  # 業務委託内容
    toiawase_id = Column(UUID(as_uuid=True), ForeignKey("master_toiawase.id"), nullable=True)  # 問い合わせマスタ参照
    sagyou_kubun_id = Column(UUID(as_uuid=True), ForeignKey("master_sagyou_kubun.id"), nullable=True)  # 作業区分マスタ参照

    # 工数情報
    estimated_hours = Column(Integer)  # 予定工数（分単位）
    actual_hours = Column(Integer, default=0)  # 実績工数（分単位、自動集計）

    # ステータス・日付
    shinchoku_id = Column(UUID(as_uuid=True), ForeignKey("master_shinchoku.id"), nullable=True)  # 進捗マスタ参照
    start_date = Column(Date)  # 仕掛日
    completion_date = Column(Date)  # 完了日
    drawing_deadline = Column(Date)  # 作図期限

    # システム項目
    is_active = Column(Boolean, default=True)  # 論理削除フラグ
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    machine_series = relationship("MachineSeriesMaster", foreign_keys=[machine_series_id])
    toiawase = relationship("MasterToiawase", foreign_keys=[toiawase_id])
    sagyou_kubun = relationship("MasterSagyouKubun", foreign_keys=[sagyou_kubun_id])
    shinchoku = relationship("MasterShinchoku", foreign_keys=[shinchoku_id])
    worklogs = relationship("WorkLog", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="project", cascade="all, delete-orphan")
    checklists = relationship("ChecklistItem", back_populates="project", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])