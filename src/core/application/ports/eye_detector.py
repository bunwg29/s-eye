from abc import ABC, abstractmethod
from typing import Any

from core.domain.value_objects.eye_landmarks import EyeLandmarks


class EyeDetectorPort(ABC):
    """Port phát hiện landmarks mắt từ frame."""

    @abstractmethod
    def detect(self, frame: Any) -> tuple[EyeLandmarks, EyeLandmarks] | None:
        pass
