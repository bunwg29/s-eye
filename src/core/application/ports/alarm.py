from abc import ABC, abstractmethod


class AlarmPort(ABC):
    """Audio alert port."""

    @abstractmethod
    def trigger(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
