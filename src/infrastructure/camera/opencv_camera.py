import cv2

from core.application.ports.frame_source import FrameSourcePort


class OpenCVCamera(FrameSourcePort):
    def __init__(
        self,
        camera_index: int,
        width: int,
        height: int,
        backend_preference: str = "dshow,msmf,any",
    ) -> None:
        self._camera_index = camera_index
        self._width = width
        self._height = height
        self._prefetched_frame = None

        self._backend_candidates = self._parse_backend_preference(backend_preference)
        self._backend_index = -1
        self._cap = None
        self._open_first_working_backend()

    def read(self):
        if self._prefetched_frame is not None:
            frame = self._prefetched_frame
            self._prefetched_frame = None
            return frame

        if self._cap is None:
            return None

        ok, frame = self._cap.read()
        if not ok:
            if self._open_next_backend():
                ok, frame = self._cap.read()
                if ok:
                    return frame
            return None
        return frame

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()

    def _parse_backend_preference(
        self, backend_preference: str
    ) -> list[tuple[str, int]]:
        mapping: dict[str, int] = {
            "any": cv2.CAP_ANY,
            "msmf": cv2.CAP_MSMF,
            "dshow": cv2.CAP_DSHOW,
            "vfw": cv2.CAP_VFW,
        }

        result: list[tuple[str, int]] = []
        seen: set[int] = set()
        for raw in backend_preference.split(","):
            name = raw.strip().lower()
            if name not in mapping:
                continue
            code = mapping[name]
            if code in seen:
                continue
            seen.add(code)
            result.append((name, code))

        if not result:
            result = [("any", cv2.CAP_ANY)]
        return result

    def _open_first_working_backend(self) -> None:
        for index, (name, code) in enumerate(self._backend_candidates):
            cap = cv2.VideoCapture(self._camera_index, code)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

            if not cap.isOpened():
                cap.release()
                continue

            ok, frame = cap.read()
            if not ok:
                cap.release()
                continue

            self._cap = cap
            self._backend_index = index
            self._prefetched_frame = frame
            print(f"[S-Eye] Camera backend selected: {name}")
            return

        self._cap = None
        self._backend_index = -1
        print("[S-Eye] Camera open failed for all preferred backends.")

    def _open_next_backend(self) -> bool:
        if self._cap is not None:
            self._cap.release()

        start = self._backend_index + 1
        if start >= len(self._backend_candidates):
            return False

        for index in range(start, len(self._backend_candidates)):
            name, code = self._backend_candidates[index]
            cap = cv2.VideoCapture(self._camera_index, code)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

            if not cap.isOpened():
                cap.release()
                continue

            self._cap = cap
            self._backend_index = index
            self._prefetched_frame = None
            print(f"[S-Eye] Camera backend fallback to: {name}")
            return True

        self._cap = None
        return False
