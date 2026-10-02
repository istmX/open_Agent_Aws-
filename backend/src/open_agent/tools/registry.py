"""Registry for tool definitions available to agents."""

from open_agent.tools.base import Tool


class ToolRegistry:
    """Manage tools by their unique names without executing them."""

    def __init__(self, tools: list[Tool] | None = None) -> None:
        """Initialize an empty registry and optionally register tools."""

        self._tools: dict[str, Tool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        """Register a tool, raising ``ValueError`` if its name is taken."""

        if tool.name in self._tools:
            raise ValueError(f"Tool with name {tool.name!r} is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Return the tool named ``name`` or raise ``KeyError``."""

        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool with name {name!r} is not registered.") from exc

    def list_tools(self) -> list[Tool]:
        """Return registered tools in registration order."""

        return list(self._tools.values())

    def remove(self, name: str) -> Tool:
        """Remove and return the named tool or raise ``KeyError``."""

        try:
            return self._tools.pop(name)
        except KeyError as exc:
            raise KeyError(f"Tool with name {name!r} is not registered.") from exc
