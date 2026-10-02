"""Execution boundary for a single agent."""

from open_agent.agents.base import Agent

class AgentRuntime:
    """Provide a small foundation for future execution of one agent."""

    def __init__(self, agent: Agent) -> None:
        """Initialize the runtime for ``agent``."""

        self.agent = agent
