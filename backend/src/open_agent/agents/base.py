"""Agent base class."""

from open_agent.llm.base import LLMProvider
from open_agent.tools.base import Tool


class Agent:
    """Represents an autonomous AI agent."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        llm: LLMProvider,
        tools: list[Tool]
    ) -> None:
        """Initialize an agent."""

        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.llm = llm
        self.tools = tools