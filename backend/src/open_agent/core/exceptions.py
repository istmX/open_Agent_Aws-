"""Application-specific exception hierarchy."""


class OpenAgentError(Exception):
    """Base exception for all Open Agent errors."""


class ConfigurationError(OpenAgentError):
    """Raised when application configuration is invalid."""


class AgentError(OpenAgentError):
    """Base exception for agent-related failures."""


class ToolError(OpenAgentError):
    """Base exception for tool execution failures."""


class ComputerError(OpenAgentError):
    """Base exception for computer execution failures."""