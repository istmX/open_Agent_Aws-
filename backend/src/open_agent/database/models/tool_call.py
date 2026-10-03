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
from open_agent.database.enums import ToolCallStatus, enum_type


class ToolCall(UUIDPrimaryKey, Base):
    __tablename__ = "tool_calls"
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(
        type_=String(255), nullable=False, index=True
    )
    arguments: Mapped[dict[str, object]] = mapped_column(
        type_=JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    result: Mapped[dict[str, object] | None] = mapped_column(
        type_=JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    status: Mapped[ToolCallStatus] = mapped_column(
        enum_type(ToolCallStatus, "tool_call_status"),
        nullable=False,
        server_default="pending",
    )
    error: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    run: Mapped[AgentRun] = relationship(back_populates="tool_calls")
