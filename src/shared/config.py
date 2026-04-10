from dataclasses import dataclass


@dataclass(frozen=True)
class DrowsinessConfig:
    """Thresholds for EAR-based warning logic."""

    ear_threshold: float = 0.21
    min_closed_frames: int = 12


@dataclass(frozen=True)
class CameraConfig:
    """Camera runtime settings."""

    camera_index: int = 0
    width: int = 640
    height: int = 480


@dataclass(frozen=True)
class AppConfig:
    """Root config object."""

    drowsiness: DrowsinessConfig = DrowsinessConfig()
    camera: CameraConfig = CameraConfig()
