from abc import ABC, abstractmethod
from typing import Any


class FrameSourcePort(ABC):
    """Port lấy frame từ camera/video source."""

    @abstractmethod
    def read(self) -> Any | None:
        pass

    @abstractmethod
    def release(self) -> None:
        pass
