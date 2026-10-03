"""Base abstraction for agent tools."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class Tool(ABC):
    """Base class for every tool available to an agent."""

    def __init__(
        self,
        name: str,
        description: str,
        args_schema: type[BaseModel] | None = None,
    ) -> None:
        """Initialize the tool."""
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool."""
        raise NotImplementedError

    def to_langchain_tool(self) -> StructuredTool:
        """Convert this tool into a LangChain StructuredTool."""
        return StructuredTool.from_function(
            func=None,
            coroutine=self.execute,
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
        )