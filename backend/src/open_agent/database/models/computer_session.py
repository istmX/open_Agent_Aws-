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
from open_agent.database.enums import ComputerSessionStatus, enum_type


class ComputerSession(UUIDPrimaryKey, Base):
    __tablename__ = "computer_sessions"
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    status: Mapped[ComputerSessionStatus] = mapped_column(
        enum_type(ComputerSessionStatus, "computer_session_status"),
        nullable=False,
        server_default="starting",
    )
    external_session_id: Mapped[str | None] = mapped_column(
        type_=String(255), nullable=True
    )
    workspace: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    metadata_: Mapped[dict[str, object] | None] = mapped_column(
        "metadata", JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    agent: Mapped[Agent] = relationship(back_populates="computer_sessions")
