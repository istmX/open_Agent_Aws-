"""Base interfaces for LLM providers."""

from typing import Protocol

from langchain_core.messages import AIMessage, BaseMessage


from open_agent.tools.base import Tool


class LLMProvider(Protocol):
    """Protocol that every LLM provider must implement."""

    async def generate(
        self,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
    ) -> AIMessage:
        """Generate a response from the configured LLM."""
        ...