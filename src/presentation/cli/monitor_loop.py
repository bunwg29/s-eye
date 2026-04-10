import cv2

from core.domain.entities.driver_state import DriverState


def run_monitor_loop(frame_source, process_frame_use_case) -> None:
    state = DriverState()

    while True:
        frame = frame_source.read()
        if frame is None:
            break

        result = process_frame_use_case.execute(frame, state)

        status_text = "NO FACE"
        if result.has_face:
            status_text = f"EAR: {result.ear:.3f}" if result.ear is not None else "EAR: N/A"

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

        cv2.putText(frame, status_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("S-Eye Monitor", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    frame_source.release()
    cv2.destroyAllWindows()
