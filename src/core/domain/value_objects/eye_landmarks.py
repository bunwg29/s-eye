from dataclasses import dataclass
from typing import Tuple

Point = Tuple[float, float]


@dataclass(frozen=True)
class EyeLandmarks:
    """Six landmarks of one eye in standard EAR order: p1..p6."""

    p1: Point
    p2: Point
    p3: Point
    p4: Point
    p5: Point
    p6: Point
