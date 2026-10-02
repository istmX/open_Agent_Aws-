"""GROQ LLM provider implementation."""

from langchain_core.messages import AIMessage, BaseMessage
from langchain_groq import ChatGroq

from open_agent.core.config import get_settings
from open_agent.llm.base import LLMProvider

class GroqProvider:
    def __init__(self)->None:
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
            messages:list[BaseMessage],

    )-> AIMessage:
        """Generate a response from a list of messages."""
        response = await self.llm.ainvoke(messages)
        return response

        @property
        def llm(self)-> ChatGroq:
            """Return the underlying LLM instance."""
            return self.llm







