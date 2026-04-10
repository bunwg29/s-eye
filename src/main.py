from core.application.use_cases.process_frame import ProcessFrameUseCase
from infrastructure.audio.system_alarm import SystemAlarm
from infrastructure.camera.opencv_camera import OpenCVCamera
from infrastructure.vision.manual_eye_detector import ManualEyeDetector
from presentation.cli.monitor_loop import run_monitor_loop
from shared.config import AppConfig


def main() -> None:
    config = AppConfig()

    frame_source = OpenCVCamera(
        camera_index=config.camera.camera_index,
        width=config.camera.width,
        height=config.camera.height,
    )
    eye_detector = ManualEyeDetector()
    alarm = SystemAlarm()

    process_frame = ProcessFrameUseCase(
        eye_detector=eye_detector,
        alarm=alarm,
        ear_threshold=config.drowsiness.ear_threshold,
        min_closed_frames=config.drowsiness.min_closed_frames,
    )

    run_monitor_loop(frame_source=frame_source, process_frame_use_case=process_frame)


if __name__ == "__main__":
    main()
