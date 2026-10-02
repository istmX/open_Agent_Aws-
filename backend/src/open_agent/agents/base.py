"""Agent base class."""

from open_agent.llm.base import LLMProvider


class Agent:
    """Represents an autonomous AI agent."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        llm: LLMProvider,
    ) -> None:
        """Initialize an agent."""

        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.llm = llm