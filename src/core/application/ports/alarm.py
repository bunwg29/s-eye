from abc import ABC, abstractmethod


class AlarmPort(ABC):
    """Port cảnh báo âm thanh."""

    @abstractmethod
    def trigger(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
