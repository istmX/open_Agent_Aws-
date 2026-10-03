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
from open_agent.database.enums import RunStatus, enum_type


class AgentRun(UUIDPrimaryKey, Base):
    __tablename__ = "agent_runs"
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    status: Mapped[RunStatus] = mapped_column(
        enum_type(RunStatus, "run_status"), nullable=False, server_default="pending"
    )
    current_step: Mapped[int] = mapped_column(
        type_=Integer, nullable=False, default=0, server_default="0"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    error: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    task: Mapped[Task] = relationship(back_populates="runs")
    agent: Mapped[Agent] = relationship(back_populates="runs")
    messages: Mapped[list[Message]] = relationship(
        back_populates="run", passive_deletes=True
    )
    tool_calls: Mapped[list[ToolCall]] = relationship(
        back_populates="run", passive_deletes=True
    )
    artifacts: Mapped[list[Artifact]] = relationship(
        back_populates="run", passive_deletes=True
    )
