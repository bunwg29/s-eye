from core.application.use_cases.process_frame import ProcessFrameUseCase
from core.domain.entities.driver_state import DriverState
from core.domain.value_objects.eye_landmarks import EyeLandmarks


class StubDetector:
    def __init__(self, detected=True):
        self._detected = detected

    def detect(self, frame):
        _ = frame
        if not self._detected:
            return None

        eye = EyeLandmarks(
            p1=(0.0, 0.0),
            p2=(1.0, 0.1),
            p3=(2.0, 0.1),
            p4=(4.0, 0.0),
            p5=(2.0, -0.1),
            p6=(1.0, -0.1),
        )
        return eye, eye


class StubAlarm:
    def __init__(self):
        self.triggered = 0
        self.stopped = 0

    def trigger(self):
        self.triggered += 1

    def stop(self):
        self.stopped += 1


def test_use_case_marks_drowsy_after_threshold() -> None:
    detector = StubDetector(detected=True)
    alarm = StubAlarm()
    use_case = ProcessFrameUseCase(detector, alarm, ear_threshold=0.2, min_closed_frames=2)

    state = DriverState()
    use_case.execute(frame={}, state=state)
    result = use_case.execute(frame={}, state=state)

    assert result.is_drowsy is True
    assert alarm.triggered >= 1
