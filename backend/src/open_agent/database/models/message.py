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
from open_agent.database.enums import MessageRole, enum_type


class Message(UUIDPrimaryKey, Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_messages_run_sequence"),
        CheckConstraint("sequence >= 0", name="sequence_nonnegative"),
    )
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    role: Mapped[MessageRole] = mapped_column(
        enum_type(MessageRole, "message_role"), nullable=False
    )
    content: Mapped[str] = mapped_column(type_=Text, nullable=False)
    sequence: Mapped[int] = mapped_column(type_=Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    run: Mapped[AgentRun] = relationship(back_populates="messages")
