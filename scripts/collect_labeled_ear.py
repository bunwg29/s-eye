from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import cv2

from core.domain.services.drowsiness_rules import compute_ear
from infrastructure.camera.opencv_camera import OpenCVCamera
from infrastructure.vision.manual_eye_detector import ManualEyeDetector


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect EAR data with manual labels from webcam")
    parser.add_argument("--output", default="logs/manual_labeled_ear.csv")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--skip-no-face", action="store_true")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    session_id = args.session_id or time.strftime("manual_%Y%m%d_%H%M%S")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    camera = OpenCVCamera(
        camera_index=args.camera_index,
        width=args.width,
        height=args.height,
    )
    detector = ManualEyeDetector()

    file_exists = output_path.exists() and output_path.stat().st_size > 0
    label_value = 0
    label_name = "ALERT"
    recording = True
    frame_index = 0
    saved_rows = 0

    print("[collect] Controls:")
    print("  0: set label ALERT")
    print("  1: set label DROWSY")
    print("  r: toggle recording on/off")
    print("  q: quit")

    with output_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "session_id",
                    "frame_index",
                    "timestamp",
                    "ear",
                    "is_drowsy",
                    "label_name",
                    "has_face",
                ]
            )

        while True:
            frame = camera.read()
            if frame is None:
                break

            frame_index += 1
            now = time.time()

            detected = detector.detect(frame)
            ear = None
            has_face = 0
            if detected is not None:
                left_eye, right_eye = detected
                ear = (compute_ear(left_eye) + compute_ear(right_eye)) / 2.0
                has_face = 1

            if recording and (has_face == 1 or not args.skip_no_face):
                writer.writerow(
                    [
                        session_id,
                        frame_index,
                        f"{now:.3f}",
                        "" if ear is None else f"{ear:.6f}",
                        label_value,
                        label_name,
                        has_face,
                    ]
                )
                saved_rows += 1

            status = f"LABEL={label_name}({label_value}) REC={'ON' if recording else 'OFF'}"
            ear_text = "EAR: N/A" if ear is None else f"EAR: {ear:.3f}"
            cv2.putText(frame, status, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, ear_text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"saved={saved_rows}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, "Keys: 0 ALERT | 1 DROWSY | r REC | q QUIT", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            cv2.imshow("S-Eye Data Collection", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("0"):
                label_value = 0
                label_name = "ALERT"
            if key == ord("1"):
                label_value = 1
                label_name = "DROWSY"
            if key == ord("r"):
                recording = not recording

    camera.release()
    cv2.destroyAllWindows()
    print(f"[collect] session={session_id} rows_saved={saved_rows} output={output_path}")


if __name__ == "__main__":
    main()
