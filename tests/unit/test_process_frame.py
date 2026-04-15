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


class SequenceDetector:
    def __init__(self, outputs):
        self._outputs = list(outputs)
        self._index = 0

    def detect(self, frame):
        _ = frame
        if self._index >= len(self._outputs):
            return self._outputs[-1]
        item = self._outputs[self._index]
        self._index += 1
        return item


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def now(self) -> float:
        return self.value


class StubAlarm:
    def __init__(self):
        self.triggered = 0
        self.stopped = 0

    def trigger(self):
        self.triggered += 1

    def stop(self):
        self.stopped += 1


class StubClassifier:
    def __init__(self, proba: float):
        self._proba = proba

    def predict_proba(self, ear_sequence):
        _ = ear_sequence
        return self._proba


def test_use_case_marks_drowsy_after_threshold() -> None:
    detector = StubDetector(detected=True)
    alarm = StubAlarm()
    use_case = ProcessFrameUseCase(detector, alarm, ear_threshold=0.2, min_closed_frames=2)

    state = DriverState()
    use_case.execute(frame={}, state=state)
    result = use_case.execute(frame={}, state=state)

    assert result.is_drowsy is True
    assert alarm.triggered >= 1


def test_use_case_uses_ml_probability_when_sequence_ready() -> None:
    detector = StubDetector(detected=True)
    alarm = StubAlarm()
    classifier = StubClassifier(proba=0.9)
    use_case = ProcessFrameUseCase(
        detector,
        alarm,
        ear_threshold=0.1,
        min_closed_frames=99,
        ml_classifier=classifier,
        ml_sequence_length=2,
        ml_probability_threshold=0.7,
    )

    state = DriverState()
    use_case.execute(frame={}, state=state)
    result = use_case.execute(frame={}, state=state)

    assert result.drowsy_probability == 0.9
    assert result.is_drowsy is True
    assert alarm.triggered >= 1


def test_use_case_keeps_alert_during_short_no_face_window() -> None:
    eye = EyeLandmarks(
        p1=(0.0, 0.0),
        p2=(1.0, 0.1),
        p3=(2.0, 0.1),
        p4=(4.0, 0.0),
        p5=(2.0, -0.1),
        p6=(1.0, -0.1),
    )
    detector = SequenceDetector(outputs=[(eye, eye), (eye, eye), None])
    alarm = StubAlarm()
    use_case = ProcessFrameUseCase(
        detector,
        alarm,
        ear_threshold=0.2,
        min_closed_frames=2,
        no_face_tolerance_frames=2,
    )

    state = DriverState()
    use_case.execute(frame={}, state=state)
    use_case.execute(frame={}, state=state)
    result = use_case.execute(frame={}, state=state)

    assert result.has_face is False
    assert result.is_drowsy is True
    assert alarm.triggered >= 2


def test_use_case_holds_alert_for_minimum_duration() -> None:
    closed_eye = EyeLandmarks(
        p1=(0.0, 0.0),
        p2=(1.0, 0.1),
        p3=(2.0, 0.1),
        p4=(4.0, 0.0),
        p5=(2.0, -0.1),
        p6=(1.0, -0.1),
    )
    open_eye = EyeLandmarks(
        p1=(0.0, 0.0),
        p2=(1.0, 1.0),
        p3=(2.0, 1.0),
        p4=(4.0, 0.0),
        p5=(2.0, -1.0),
        p6=(1.0, -1.0),
    )
    detector = SequenceDetector(
        outputs=[
            (closed_eye, closed_eye),
            (closed_eye, closed_eye),
            (open_eye, open_eye),
            (open_eye, open_eye),
            (open_eye, open_eye),
        ]
    )
    alarm = StubAlarm()
    clock = FakeClock()
    use_case = ProcessFrameUseCase(
        detector,
        alarm,
        ear_threshold=0.2,
        min_closed_frames=2,
        min_alert_hold_seconds=5.0,
        time_fn=clock.now,
    )

    state = DriverState()
    use_case.execute(frame={}, state=state)
    use_case.execute(frame={}, state=state)

    clock.value = 2.0
    result_hold = use_case.execute(frame={}, state=state)

    clock.value = 6.1
    result_still = use_case.execute(frame={}, state=state)

    clock.value = 6.2
    result_expired = use_case.execute(frame={}, state=state)

    assert result_hold.is_drowsy is True
    assert result_still.is_drowsy is True
    assert result_expired.is_drowsy is False


def test_use_case_can_mute_alarm_during_calibration() -> None:
    closed_eye = EyeLandmarks(
        p1=(0.0, 0.0),
        p2=(1.0, 0.1),
        p3=(2.0, 0.1),
        p4=(4.0, 0.0),
        p5=(2.0, -0.1),
        p6=(1.0, -0.1),
    )
    detector = SequenceDetector(outputs=[(closed_eye, closed_eye), (closed_eye, closed_eye)])
    alarm = StubAlarm()
    use_case = ProcessFrameUseCase(
        detector,
        alarm,
        ear_threshold=0.2,
        min_closed_frames=2,
        min_alert_hold_seconds=2.0,
    )

    state = DriverState()
    use_case.execute(frame={}, state=state, alarm_enabled=False)
    result = use_case.execute(frame={}, state=state, alarm_enabled=False)

    assert result.is_drowsy is True
    assert alarm.triggered == 0
    assert alarm.stopped >= 1


