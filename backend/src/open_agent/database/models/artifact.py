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


class Artifact(UUIDPrimaryKey, Base):
    __tablename__ = "artifacts"
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    type: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(type_=Text, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(type_=String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(type_=BigInteger, nullable=True)
    metadata_: Mapped[dict[str, object] | None] = mapped_column(
        "metadata", JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    run: Mapped[AgentRun] = relationship(back_populates="artifacts")
    agent: Mapped[Agent] = relationship(
        back_populates="artifacts", foreign_keys=[agent_id]
    )
