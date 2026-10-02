"""Typed data carried through an agent's future execution."""

from dataclasses import dataclass, field
from typing import Literal

from langchain_core.messages import BaseMessage


AgentStatus = Literal["pending", "running", "completed", "failed"]


@dataclass
class AgentState:
    """Represent the current execution state of an agent."""

    agent_id: str
    task: str
    messages: list[BaseMessage] = field(default_factory=list)
    current_step: int = 0
    status: AgentStatus = "pending"
    error: str | None = None
