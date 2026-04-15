import csv
import time
from pathlib import Path

import cv2

from core.domain.entities.driver_state import DriverState


def run_monitor_loop(
    frame_source,
    process_frame_use_case,
    calibration_config=None,
    logging_config=None,
) -> None:
    state = DriverState()
    frame_index = 0

    calibration_enabled = bool(getattr(calibration_config, "enabled", False))
    calibration_duration = max(1, int(getattr(calibration_config, "duration_seconds", 20)))
    calibration_min_samples = max(30, int(getattr(calibration_config, "min_samples", 120)))
    calibration_factor = float(getattr(calibration_config, "threshold_factor", 0.75))
    calibration_min = float(getattr(calibration_config, "threshold_min", 0.15))
    calibration_max = float(getattr(calibration_config, "threshold_max", 0.30))
    calibration_start = time.time()
    calibration_samples: list[float] = []
    calibration_done = not calibration_enabled

    logging_enabled = bool(getattr(logging_config, "enabled", False))
    log_file = None
    log_writer = None
    session_id = time.strftime("%Y%m%d_%H%M%S")
    if logging_enabled:
        log_path = Path(str(getattr(logging_config, "ear_log_path", "logs/ear_runtime.csv")))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = log_path.open("a", newline="", encoding="utf-8")
        log_writer = csv.writer(log_file)
        if log_path.stat().st_size == 0:
            log_writer.writerow(
                [
                    "session_id",
                    "frame_index",
                    "timestamp",
                    "ear",
                    "is_drowsy",
                    "drowsy_probability",
                    "ear_threshold",
                    "is_calibrating",
                ]
            )

    while True:
        frame = frame_source.read()
        if frame is None:
            break

        result = process_frame_use_case.execute(
            frame,
            state,
            alarm_enabled=calibration_done,
        )
        frame_index += 1

        if not calibration_done:
            elapsed = time.time() - calibration_start
            if elapsed <= calibration_duration:
                if result.has_face and result.ear is not None:
                    calibration_samples.append(float(result.ear))
            else:
                calibration_done = True
                if len(calibration_samples) >= calibration_min_samples:
                    avg_open_ear = sum(calibration_samples) / len(calibration_samples)
                    personalized = avg_open_ear * calibration_factor
                    personalized = max(calibration_min, min(calibration_max, personalized))
                    if hasattr(process_frame_use_case, "set_ear_threshold"):
                        process_frame_use_case.set_ear_threshold(personalized)
                    print(
                        f"[S-Eye] Calibration complete. samples={len(calibration_samples)} "
                        f"threshold={personalized:.3f}"
                    )
                else:
                    print(
                        f"[S-Eye] Calibration skipped (insufficient samples: {len(calibration_samples)})."
                    )

        status_text = "NO FACE"
        if result.has_face:
            status_text = f"EAR: {result.ear:.3f}" if result.ear is not None else "EAR: N/A"
            if result.drowsy_probability is not None:
                status_text = f"{status_text} | P(drowsy): {result.drowsy_probability:.2f}"

        if result.is_drowsy:
            cv2.putText(
                frame,
                "DROWSINESS ALERT!",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
            )

        if not calibration_done:
            remaining = max(0, calibration_duration - int(time.time() - calibration_start))
            cv2.putText(
                frame,
                f"Calibrating... {remaining}s",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
            )

        if log_writer is not None and result.ear is not None:
            threshold = (
                process_frame_use_case.get_ear_threshold()
                if hasattr(process_frame_use_case, "get_ear_threshold")
                else ""
            )
            log_writer.writerow(
                [
                    session_id,
                    frame_index,
                    f"{time.time():.3f}",
                    f"{result.ear:.6f}",
                    int(result.is_drowsy),
                    ""
                    if result.drowsy_probability is None
                    else f"{result.drowsy_probability:.6f}",
                    threshold,
                    int(not calibration_done),
                ]
            )

        cv2.putText(frame, status_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("S-Eye Monitor", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    frame_source.release()
    if log_file is not None:
        log_file.close()
    cv2.destroyAllWindows()
