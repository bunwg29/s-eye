from core.application.use_cases.process_frame import ProcessFrameUseCase
from infrastructure.audio.system_alarm import SystemAlarm
from infrastructure.camera.opencv_camera import OpenCVCamera
from infrastructure.ml.onnx_drowsiness_classifier import OnnxDrowsinessClassifier
from infrastructure.vision.manual_eye_detector import ManualEyeDetector
from presentation.cli.monitor_loop import run_monitor_loop
from shared.config import AppConfig


def main() -> None:
    config = AppConfig()

    frame_source = OpenCVCamera(
        camera_index=config.camera.camera_index,
        width=config.camera.width,
        height=config.camera.height,
        backend_preference=config.camera.backend_preference,
    )
    eye_detector = ManualEyeDetector()
    alarm = SystemAlarm()
    ml_classifier = None

    if config.ml.enabled:
        try:
            ml_classifier = OnnxDrowsinessClassifier(model_path=config.ml.model_path)
            print(f"[S-Eye] ML mode enabled with model: {config.ml.model_path}")
        except Exception as exc:
            print(f"[S-Eye] ML mode unavailable ({exc}). Falling back to classical EAR rules.")

    process_frame = ProcessFrameUseCase(
        eye_detector=eye_detector,
        alarm=alarm,
        ear_threshold=config.drowsiness.ear_threshold,
        min_closed_frames=config.drowsiness.min_closed_frames,
        ml_classifier=ml_classifier,
        ml_sequence_length=config.ml.sequence_length,
        ml_probability_threshold=config.ml.drowsy_probability_threshold,
    )

    run_monitor_loop(
        frame_source=frame_source,
        process_frame_use_case=process_frame,
        calibration_config=config.calibration,
        logging_config=config.logging,
    )


if __name__ == "__main__":
    main()
