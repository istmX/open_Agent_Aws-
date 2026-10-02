"""Base interfaces for LLM providers."""

from typing import Protocol

from langchain_core.messages import AIMessage, BaseMessage


class LLMProvider(Protocol):
    """Protocol that every LLM provider must implement."""

    async def generate(
        self,
        messages: list[BaseMessage],
    ) -> AIMessage:
        """Generate a response from the configured LLM."""
        ...