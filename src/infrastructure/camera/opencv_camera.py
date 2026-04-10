import cv2

from core.application.ports.frame_source import FrameSourcePort


class OpenCVCamera(FrameSourcePort):
    def __init__(self, camera_index: int, width: int, height: int) -> None:
        self._cap = cv2.VideoCapture(camera_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self):
        ok, frame = self._cap.read()
        if not ok:
            return None
        return frame

    def release(self) -> None:
        self._cap.release()
