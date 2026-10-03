"""Built-in file reading and writing tools with workspace path confinement."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from open_agent.core.exceptions import ToolError
from open_agent.tools.base import Tool


class ReadFileInput(BaseModel):
    """Input parameters for ReadFileTool."""

    file_path: str = Field(description="Relative or absolute path of the file to read.")


class ReadFileTool(Tool):
    """Tool for reading text from a file within an allowed directory boundary."""

    def __init__(self, base_dir: Path | str | None = None) -> None:
        super().__init__(
            name="read_file",
            description="Read the contents of a text file from the filesystem.",
            args_schema=ReadFileInput,
        )
        self.base_dir = (Path(base_dir) if base_dir else Path.cwd()).resolve()

    def _resolve_safe_path(self, file_path: str) -> Path:
        raw_path = Path(file_path)
        target = (self.base_dir / raw_path).resolve() if not raw_path.is_absolute() else raw_path.resolve()
        try:
            target.relative_to(self.base_dir)
        except ValueError:
            raise ToolError(
                f"Access denied: path '{file_path}' resolves outside allowed directory '{self.base_dir}'."
            )
        return target

    async def execute(self, file_path: str, **kwargs: Any) -> str:
        """Read and return file text content."""
        safe_path = self._resolve_safe_path(file_path)
        if not safe_path.is_file():
            raise ToolError(f"File not found: '{file_path}'.")
        try:
            return safe_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ToolError(f"Failed to read file '{file_path}': {exc}") from exc


class WriteFileInput(BaseModel):
    """Input parameters for WriteFileTool."""

    file_path: str = Field(description="Relative or absolute path of the file to write.")
    content: str = Field(description="Text content to write into the file.")


class WriteFileTool(Tool):
    """Tool for writing text to a file within an allowed directory boundary."""

    def __init__(self, base_dir: Path | str | None = None) -> None:
        super().__init__(
            name="write_file",
            description="Write text content into a file on the filesystem.",
            args_schema=WriteFileInput,
        )
        self.base_dir = (Path(base_dir) if base_dir else Path.cwd()).resolve()

    def _resolve_safe_path(self, file_path: str) -> Path:
        raw_path = Path(file_path)
        target = (self.base_dir / raw_path).resolve() if not raw_path.is_absolute() else raw_path.resolve()
        try:
            target.relative_to(self.base_dir)
        except ValueError:
            raise ToolError(
                f"Access denied: path '{file_path}' resolves outside allowed directory '{self.base_dir}'."
            )
        return target

    async def execute(self, file_path: str, content: str, **kwargs: Any) -> str:
        """Write content into the specified file."""
        safe_path = self._resolve_safe_path(file_path)
        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} characters to '{file_path}'."
        except Exception as exc:
            raise ToolError(f"Failed to write file '{file_path}': {exc}") from exc
