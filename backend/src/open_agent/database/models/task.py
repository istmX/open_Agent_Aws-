from __future__ import annotations

from datetime import datetime
from uuid import UUID
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    CheckConstraint,
    Index,
    func,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from open_agent.database.base import Base, CreatedAt, UUIDPrimaryKey
from open_agent.database.enums import TaskStatus, enum_type


class Task(UUIDPrimaryKey, Base):
    __tablename__ = "tasks"
    __table_args__ = (CheckConstraint("priority >= 0", name="priority_nonnegative"),)
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(type_=Text, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        enum_type(TaskStatus, "task_status"), nullable=False, server_default="pending"
    )
    priority: Mapped[int] = mapped_column(
        type_=Integer, nullable=False, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    error: Mapped[str | None] = mapped_column(type_=Text, nullable=True)

    agent: Mapped[Agent] = relationship(back_populates="tasks")
    runs: Mapped[list[AgentRun]] = relationship(
        back_populates="task", passive_deletes=True
    )
