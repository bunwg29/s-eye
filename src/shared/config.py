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
    backend_preference: str = "dshow,msmf,any"


@dataclass(frozen=True)
class MlConfig:
    """Settings for modern ML inference mode."""

    enabled: bool = True
    model_path: str = "models/drowsiness.onnx"
    sequence_length: int = 16
    drowsy_probability_threshold: float = 0.50


@dataclass(frozen=True)
class CalibrationConfig:
    """Per-user threshold calibration settings."""

    enabled: bool = True
    duration_seconds: int = 20
    min_samples: int = 120
    threshold_factor: float = 0.75
    threshold_min: float = 0.15
    threshold_max: float = 0.30


@dataclass(frozen=True)
class LoggingConfig:
    """Runtime signal logging for dataset generation."""

    enabled: bool = True
    ear_log_path: str = "logs/ear_runtime.csv"


@dataclass(frozen=True)
class AppConfig:
    """Root config object."""

    drowsiness: DrowsinessConfig = DrowsinessConfig()
    camera: CameraConfig = CameraConfig()
    ml: MlConfig = MlConfig()
    calibration: CalibrationConfig = CalibrationConfig()
    logging: LoggingConfig = LoggingConfig()
