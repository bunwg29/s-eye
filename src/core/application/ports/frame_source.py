from abc import ABC, abstractmethod
from typing import Any


class FrameSourcePort(ABC):
    """Port for reading frames from a camera/video source."""

    @abstractmethod
    def read(self) -> Any | None:
        pass

    @abstractmethod
    def release(self) -> None:
        pass
