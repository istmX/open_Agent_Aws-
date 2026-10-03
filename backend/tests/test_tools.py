"""Unit tests for tool definitions, registry, and built-in tools."""

from pathlib import Path
import pytest

from open_agent.core.exceptions import ToolError
from open_agent.tools.base import Tool
from open_agent.tools.builtin import (
    EchoTool,
    ReadFileTool,
    WriteFileTool,
)
from open_agent.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_echo_tool():
    tool = EchoTool()
    assert tool.name == "echo"
    result = await tool.execute(message="Hello Open Agent")
    assert result == "Hello Open Agent"



@pytest.mark.asyncio
async def test_file_tools_read_and_write(tmp_path: Path):
    write_tool = WriteFileTool(base_dir=tmp_path)
    read_tool = ReadFileTool(base_dir=tmp_path)

    write_result = await write_tool.execute(
        file_path="subfolder/test.txt",
        content="Hello file tools!",
    )
    assert "Successfully wrote" in write_result

    read_result = await read_tool.execute(file_path="subfolder/test.txt")
    assert read_result == "Hello file tools!"


@pytest.mark.asyncio
async def test_file_tools_security_confinement(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    read_tool = ReadFileTool(base_dir=workspace)
    write_tool = WriteFileTool(base_dir=workspace)

    # Path traversal attempts
    with pytest.raises(ToolError, match="outside allowed directory"):
        await read_tool.execute(file_path="../outside.txt")

    with pytest.raises(ToolError, match="outside allowed directory"):
        await write_tool.execute(file_path="../../outside.txt", content="payload")

    with pytest.raises(ToolError, match="File not found"):
        await read_tool.execute(file_path="nonexistent.txt")


def test_tool_registry():
    echo = EchoTool()
    reader = ReadFileTool()

    registry = ToolRegistry([echo])
    assert "echo" in registry
    assert "read_file" not in registry
    assert len(registry) == 1
    assert registry.get("echo") is echo
    assert registry.get_optional("read_file") is None

    # Register new tool
    registry.register(reader)
    assert len(registry) == 2
    assert "read_file" in registry


    # Duplicate registration raises ValueError
    with pytest.raises(ValueError, match="already registered"):
        registry.register(EchoTool())

    # Get non-existent raises KeyError
    with pytest.raises(KeyError, match="not registered"):
        registry.get("unknown_tool")

    # Remove tool
    removed = registry.remove("echo")
    assert removed is echo
    assert "echo" not in registry
    assert len(registry) == 1
