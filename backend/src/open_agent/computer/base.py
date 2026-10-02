"""Abstract contract for computer environments."""

from abc import ABC, abstractmethod


class Computer(ABC):
    """Define basic computer interaction operations."""

    @abstractmethod
    async def screenshot(self) -> bytes:
        """Capture the current screen as image bytes."""

    @abstractmethod
    async def click(self, x: int, y: int) -> None:
        """Click at screen coordinates ``(x, y)``."""

    @abstractmethod
    async def type(self, text: str) -> None:
        """Type the provided text into the active input target."""

    @abstractmethod
    async def press(self, key: str) -> None:
        """Press a key or named key chord."""

    @abstractmethod
    async def move(self, x: int, y: int) -> None:
        """Move the pointer to screen coordinates ``(x, y)``."""

    @abstractmethod
    async def scroll(self, delta_x: int, delta_y: int) -> None:
        """Scroll by the requested horizontal and vertical deltas."""
