"""Echo tool for testing and verification."""

from typing import Any

from pydantic import BaseModel, Field

from open_agent.tools.base import Tool


class EchoInput(BaseModel):
    """Input parameters for EchoTool."""

    message: str = Field(description="The message to echo back.")


class EchoTool(Tool):
    """Tool that echoes back the provided message."""

    def __init__(self) -> None:
        super().__init__(
            name="echo",
            description="Echo back the given message.",
            args_schema=EchoInput,
        )

    async def execute(self, message: str, **kwargs: Any) -> str:
        """Return the provided message."""
        return message
