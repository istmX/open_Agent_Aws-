from __future__ import annotations

from datetime import datetime
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
from open_agent.database.enums import AgentStatus, enum_type

from sqlalchemy import Enum as SAEnum
from open_agent.database.enums import enum_type


class Agent(UUIDPrimaryKey, Base):
    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_agents_user_name"),)
    user_id: Mapped[str] = mapped_column(type_=String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    role: Mapped[str] = mapped_column(type_=Text, nullable=False)
    description: Mapped[str | None] = mapped_column(type_=Text, nullable=True)
    status: Mapped[AgentStatus] = mapped_column(
        enum_type(AgentStatus, "agent_status"), nullable=False, server_default="active"
    )
    configuration: Mapped[dict[str, object] | None] = mapped_column(
        type_=JSON().with_variant(JSONB, "postgresql"), nullable=True
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

    tasks: Mapped[list[Task]] = relationship(
        back_populates="agent", passive_deletes=True
    )
    runs: Mapped[list[AgentRun]] = relationship(
        back_populates="agent", passive_deletes=True
    )
    computer_sessions: Mapped[list[ComputerSession]] = relationship(
        back_populates="agent", passive_deletes=True
    )
    artifacts: Mapped[list[Artifact]] = relationship(
        back_populates="agent",
        foreign_keys="Artifact.agent_id",
        passive_deletes=True,
    )
