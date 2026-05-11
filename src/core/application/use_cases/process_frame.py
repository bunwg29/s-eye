import time
from dataclasses import dataclass
from collections import deque
from typing import Any, Callable

from core.application.ports.drowsiness_classifier import DrowsinessClassifierPort
from core.domain.entities.driver_state import DriverState
from core.domain.services.drowsiness_rules import compute_ear


@dataclass(frozen=True)
class FrameAnalysisResult:
    ear: float | None
    is_drowsy: bool
    has_face: bool
    drowsy_probability: float | None = None


class ProcessFrameUseCase:
    def __init__(
        self,
        eye_detector,
        alarm,
        ear_threshold: float,
        min_closed_frames: int,
        ml_classifier: DrowsinessClassifierPort | None = None,
        ml_sequence_length: int = 16,
        ml_probability_threshold: float = 0.65,
        no_face_tolerance_frames: int = 12,
        min_alert_hold_seconds: float = 2.0,
        reopen_eye_frames_required: int = 3,
        time_fn: Callable[[], float] | None = None,
    ) -> None:
        self._eye_detector = eye_detector
        self._alarm = alarm
        self._ear_threshold = ear_threshold
        self._min_closed_frames = min_closed_frames
        self._ml_classifier = ml_classifier
        self._ml_probability_threshold = ml_probability_threshold
        self._ear_window: deque[float] = deque(maxlen=max(2, ml_sequence_length))
        self._no_face_tolerance_frames = max(0, no_face_tolerance_frames)
        self._missing_face_frames = 0
        self._last_drowsy_probability: float | None = None
        self._min_alert_hold_seconds = max(0.0, min_alert_hold_seconds)
        self._drowsy_hold_until = 0.0
        self._reopen_eye_frames_required = max(1, reopen_eye_frames_required)
        self._open_eye_frames = 0
        self._time_fn = time_fn or time.monotonic

    def set_ear_threshold(self, threshold: float) -> None:
        self._ear_threshold = max(0.01, threshold)

    def get_ear_threshold(self) -> float:
        return self._ear_threshold

    def execute(
        self,
        frame: Any,
        state: DriverState,
        alarm_enabled: bool = True,
    ) -> FrameAnalysisResult:
        now = self._time_fn()
        if not alarm_enabled:
            self._alarm.stop()
        detected = self._eye_detector.detect(frame)
        if detected is None:
            self._missing_face_frames += 1

            if state.is_drowsy:
                state.is_drowsy = True
                if alarm_enabled:
                    self._alarm.trigger()
                return FrameAnalysisResult(
                    ear=None,
                    is_drowsy=True,
                    has_face=False,
                    drowsy_probability=self._last_drowsy_probability,
                )

            state.consecutive_closed_frames = 0
            state.is_drowsy = False
            self._last_drowsy_probability = None
            self._drowsy_hold_until = 0.0
            self._open_eye_frames = 0
            self._ear_window.clear()
            if alarm_enabled:
                self._alarm.stop()
            return FrameAnalysisResult(ear=None, is_drowsy=False, has_face=False)

        self._missing_face_frames = 0

        left_eye, right_eye = detected
        ear = (compute_ear(left_eye) + compute_ear(right_eye)) / 2.0
        self._ear_window.append(ear)

        drowsy_probability: float | None = None
        is_drowsy_now = False
        if (
            self._ml_classifier is not None
            and len(self._ear_window) == self._ear_window.maxlen
        ):
            drowsy_probability = self._ml_classifier.predict_proba(
                list(self._ear_window)
            )
            self._last_drowsy_probability = drowsy_probability
            is_drowsy_now = drowsy_probability >= self._ml_probability_threshold
            state.consecutive_closed_frames = 0
        else:
            if ear < self._ear_threshold:
                state.consecutive_closed_frames += 1
            else:
                state.consecutive_closed_frames = 0

            is_drowsy_now = state.consecutive_closed_frames >= self._min_closed_frames

        if is_drowsy_now:
            self._drowsy_hold_until = now + self._min_alert_hold_seconds
            self._open_eye_frames = 0
            state.is_drowsy = True
        elif state.is_drowsy:
            is_open_eye = ear >= self._ear_threshold
            self._open_eye_frames = self._open_eye_frames + 1 if is_open_eye else 0

            hold_active = now < self._drowsy_hold_until
            if (
                self._open_eye_frames >= self._reopen_eye_frames_required
                and not hold_active
            ):
                state.is_drowsy = False
                self._open_eye_frames = 0
                self._last_drowsy_probability = drowsy_probability
            else:
                state.is_drowsy = True
        else:
            state.is_drowsy = False

        if alarm_enabled:
            if state.is_drowsy:
                self._alarm.trigger()
            else:
                self._alarm.stop()

        return FrameAnalysisResult(
            ear=ear,
            is_drowsy=state.is_drowsy,
            has_face=True,
            drowsy_probability=drowsy_probability,
        )
