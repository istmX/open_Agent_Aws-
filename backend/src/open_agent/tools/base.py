"""Base abstraction for agent tools."""

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Base class for every tool available to an agent."""

    def __init__(
        self,
        name: str,
        description: str,
    ) -> None:
        """Initialize the tool."""

        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool."""

        raise NotImplementedError