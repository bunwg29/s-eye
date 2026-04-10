from dataclasses import dataclass
from typing import Any

from core.domain.entities.driver_state import DriverState
from core.domain.services.drowsiness_rules import compute_ear


@dataclass(frozen=True)
class FrameAnalysisResult:
    ear: float | None
    is_drowsy: bool
    has_face: bool


class ProcessFrameUseCase:
    def __init__(self, eye_detector, alarm, ear_threshold: float, min_closed_frames: int) -> None:
        self._eye_detector = eye_detector
        self._alarm = alarm
        self._ear_threshold = ear_threshold
        self._min_closed_frames = min_closed_frames

    def execute(self, frame: Any, state: DriverState) -> FrameAnalysisResult:
        detected = self._eye_detector.detect(frame)
        if detected is None:
            state.consecutive_closed_frames = 0
            state.is_drowsy = False
            self._alarm.stop()
            return FrameAnalysisResult(ear=None, is_drowsy=False, has_face=False)

        left_eye, right_eye = detected
        ear = (compute_ear(left_eye) + compute_ear(right_eye)) / 2.0

        if ear < self._ear_threshold:
            state.consecutive_closed_frames += 1
        else:
            state.consecutive_closed_frames = 0

        state.is_drowsy = state.consecutive_closed_frames >= self._min_closed_frames
        if state.is_drowsy:
            self._alarm.trigger()
        else:
            self._alarm.stop()

        return FrameAnalysisResult(ear=ear, is_drowsy=state.is_drowsy, has_face=True)
