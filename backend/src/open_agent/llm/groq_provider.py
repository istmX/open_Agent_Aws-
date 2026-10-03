"""GROQ LLM provider implementation."""

from langchain_core.messages import AIMessage, BaseMessage
from langchain_groq import ChatGroq

from open_agent.core.config import get_settings
from open_agent.llm.base import LLMProvider
from open_agent.tools.base import Tool


class GroqProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatGroq(
            api_key=settings.groq_api_key.get_secret_value(),
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            timeout=settings.llm_timeout,
        )

    async def generate(
        self,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
    ) -> AIMessage:
        """Generate a response from a list of messages, optionally with bound tools."""
        runnable = self.llm
        if tools:
            lc_tools = [tool.to_langchain_tool() for tool in tools]
            runnable = self.llm.bind_tools(lc_tools)
        return await runnable.ainvoke(messages)









