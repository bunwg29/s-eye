from dataclasses import dataclass


@dataclass
class DriverState:
    """Trạng thái theo dõi tài xế qua nhiều frame."""

    consecutive_closed_frames: int = 0
    is_drowsy: bool = False
