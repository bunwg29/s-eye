from dataclasses import dataclass
from typing import Tuple

Point = Tuple[float, float]


@dataclass(frozen=True)
class EyeLandmarks:
    """6 điểm mốc của 1 mắt theo thứ tự chuẩn EAR: p1..p6."""

    p1: Point
    p2: Point
    p3: Point
    p4: Point
    p5: Point
    p6: Point
