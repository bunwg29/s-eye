from core.domain.services.drowsiness_rules import compute_ear
from core.domain.value_objects.eye_landmarks import EyeLandmarks


def test_compute_ear_returns_expected_value() -> None:
    eye = EyeLandmarks(
        p1=(0.0, 0.0),
        p2=(1.0, 2.0),
        p3=(2.0, 2.0),
        p4=(4.0, 0.0),
        p5=(2.0, -2.0),
        p6=(1.0, -2.0),
    )

    ear = compute_ear(eye)
    assert 0.9 < ear < 1.1
