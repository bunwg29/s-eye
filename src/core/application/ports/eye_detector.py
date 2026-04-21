from abc import ABC, abstractmethod
from typing import Any

from core.domain.value_objects.eye_landmarks import EyeLandmarks


class EyeDetectorPort(ABC):
    """Port for detecting eye landmarks from a frame."""

    @abstractmethod
    def detect(self, frame: Any) -> tuple[EyeLandmarks, EyeLandmarks] | None:
        pass
