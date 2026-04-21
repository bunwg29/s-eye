from dataclasses import dataclass


@dataclass
class DriverState:
    """Driver tracking state across multiple frames."""

    consecutive_closed_frames: int = 0
    is_drowsy: bool = False
