from math import dist

from core.domain.value_objects.eye_landmarks import EyeLandmarks


def compute_ear(eye: EyeLandmarks) -> float:
    """Tính Eye Aspect Ratio (EAR).

    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    """

    vertical_1 = dist(eye.p2, eye.p6)
    vertical_2 = dist(eye.p3, eye.p5)
    horizontal = dist(eye.p1, eye.p4)

    if horizontal == 0:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)
