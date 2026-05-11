from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from core.application.ports.eye_detector import EyeDetectorPort
from core.domain.value_objects.eye_landmarks import EyeLandmarks


@dataclass(frozen=True)
class _Rect:
    x: int
    y: int
    w: int
    h: int


class ManualEyeDetector(EyeDetectorPort):
    """Classical detector using Haar cascades + geometric landmark estimation."""

    def __init__(self) -> None:
        cascade_root = cv2.data.haarcascades
        self._face_cascade = cv2.CascadeClassifier(
            f"{cascade_root}haarcascade_frontalface_default.xml"
        )
        self._eye_cascade = cv2.CascadeClassifier(f"{cascade_root}haarcascade_eye.xml")
        self._last_face: _Rect | None = None
        self._last_eyes: tuple[_Rect, _Rect] | None = None
        self._missing_face_frames = 0
        self._max_missing_face_frames = 8

    def detect(self, frame: Any) -> tuple[EyeLandmarks, EyeLandmarks] | None:
        if frame is None:
            return None

        frame_h, frame_w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        face = self._detect_primary_face(gray)
        if face is None:
            if (
                self._last_face is None
                or self._missing_face_frames >= self._max_missing_face_frames
            ):
                self._last_eyes = None
                return None
            self._missing_face_frames += 1
            face = self._last_face
        else:
            self._missing_face_frames = 0
            self._last_face = face

        eyes = self._detect_two_eyes(gray, face)
        if eyes is None:
            eyes = self._fallback_eyes(face)
        else:
            eyes = self._smooth_with_previous(eyes)

        if eyes is None:
            return None

        left_rect = self._clip_rect(eyes[0], frame_w, frame_h)
        right_rect = self._clip_rect(eyes[1], frame_w, frame_h)
        self._last_eyes = (left_rect, right_rect)

        left_opening = self._estimate_eye_opening(gray, left_rect)
        right_opening = self._estimate_eye_opening(gray, right_rect)

        left_landmarks = self._rect_to_landmarks(left_rect, left_opening)
        right_landmarks = self._rect_to_landmarks(right_rect, right_opening)
        return left_landmarks, right_landmarks

    def _fallback_eyes(self, face: _Rect) -> tuple[_Rect, _Rect] | None:
        if self._last_eyes is not None and self._last_face is not None:
            left_prev, right_prev = self._last_eyes
            left = self._map_rect_between_faces(left_prev, self._last_face, face)
            right = self._map_rect_between_faces(right_prev, self._last_face, face)
            return tuple(sorted((left, right), key=lambda r: r.x))

        return self._estimate_eyes_from_face(face)

    def _estimate_eyes_from_face(self, face: _Rect) -> tuple[_Rect, _Rect]:
        x, y, w, h = face.x, face.y, face.w, face.h
        eye_w = max(20, int(w * 0.28))
        eye_h = max(12, int(h * 0.14))
        eye_y = y + int(h * 0.28)
        left_x = x + int(w * 0.18)
        right_x = x + int(w * 0.54)
        left = _Rect(left_x, eye_y, eye_w, eye_h)
        right = _Rect(right_x, eye_y, eye_w, eye_h)
        return left, right

    def _map_rect_between_faces(
        self, eye: _Rect, src_face: _Rect, dst_face: _Rect
    ) -> _Rect:
        sx = dst_face.w / max(1.0, float(src_face.w))
        sy = dst_face.h / max(1.0, float(src_face.h))

        rel_x = eye.x - src_face.x
        rel_y = eye.y - src_face.y

        mapped_x = int(dst_face.x + rel_x * sx)
        mapped_y = int(dst_face.y + rel_y * sy)
        mapped_w = int(max(12, eye.w * sx))
        mapped_h = int(max(8, eye.h * sy))
        return _Rect(mapped_x, mapped_y, mapped_w, mapped_h)

    def _smooth_with_previous(self, eyes: tuple[_Rect, _Rect]) -> tuple[_Rect, _Rect]:
        if self._last_eyes is None:
            return eyes

        alpha = 0.65
        left = self._blend_rect(self._last_eyes[0], eyes[0], alpha)
        right = self._blend_rect(self._last_eyes[1], eyes[1], alpha)
        return left, right

    def _blend_rect(self, old: _Rect, new: _Rect, alpha: float) -> _Rect:
        inv = 1.0 - alpha
        return _Rect(
            x=int(old.x * inv + new.x * alpha),
            y=int(old.y * inv + new.y * alpha),
            w=int(max(12, old.w * inv + new.w * alpha)),
            h=int(max(8, old.h * inv + new.h * alpha)),
        )

    def _clip_rect(self, rect: _Rect, frame_w: int, frame_h: int) -> _Rect:
        x = max(0, min(rect.x, frame_w - 2))
        y = max(0, min(rect.y, frame_h - 2))
        w = max(2, min(rect.w, frame_w - x))
        h = max(2, min(rect.h, frame_h - y))
        return _Rect(x, y, w, h)

    def _detect_primary_face(self, gray: np.ndarray) -> _Rect | None:
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(120, 120),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(faces) == 0:
            return None

        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
        return _Rect(int(x), int(y), int(w), int(h))

    def _detect_two_eyes(
        self, gray: np.ndarray, face: _Rect
    ) -> tuple[_Rect, _Rect] | None:
        x0, y0, w, h = face.x, face.y, face.w, face.h
        upper_h = int(h * 0.6)
        face_roi = gray[y0 : y0 + upper_h, x0 : x0 + w]

        detected_eyes = self._eye_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(20, 20),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(detected_eyes) < 2:
            return None

        rects: list[_Rect] = []
        for ex, ey, ew, eh in detected_eyes:
            abs_rect = _Rect(int(x0 + ex), int(y0 + ey), int(ew), int(eh))
            if self._is_reasonable_eye(face, abs_rect):
                rects.append(abs_rect)

        if len(rects) < 2:
            return None

        rects.sort(key=lambda r: (r.y, -(r.w * r.h)))
        pair = sorted(rects[:2], key=lambda r: r.x)
        return pair[0], pair[1]

    def _is_reasonable_eye(self, face: _Rect, eye: _Rect) -> bool:
        fx, fy, fw, fh = face.x, face.y, face.w, face.h
        ex_center = eye.x + eye.w * 0.5
        ey_center = eye.y + eye.h * 0.5

        inside_horizontal = fx + fw * 0.08 <= ex_center <= fx + fw * 0.92
        inside_vertical = fy + fh * 0.10 <= ey_center <= fy + fh * 0.62
        good_size = fw * 0.12 <= eye.w <= fw * 0.5 and fh * 0.08 <= eye.h <= fh * 0.35
        return inside_horizontal and inside_vertical and good_size

    def _estimate_eye_opening(self, gray: np.ndarray, eye: _Rect) -> float:
        roi = gray[eye.y : eye.y + eye.h, eye.x : eye.x + eye.w]
        if roi.size == 0:
            return max(2.0, eye.h * 0.2)

        blur = cv2.GaussianBlur(roi, (5, 5), 0)
        grad_y = cv2.Sobel(blur, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = np.abs(grad_y)

        h, w = grad_mag.shape
        col_start = max(0, int(w * 0.35))
        col_end = min(w, int(w * 0.65))
        if col_start >= col_end:
            return max(2.0, eye.h * 0.2)

        profile = grad_mag[:, col_start:col_end].mean(axis=1)
        top_band_end = max(1, int(h * 0.5))
        bottom_band_start = min(h - 1, int(h * 0.5))

        upper_idx = int(np.argmax(profile[:top_band_end]))
        lower_relative = int(np.argmax(profile[bottom_band_start:]))
        lower_idx = lower_relative + bottom_band_start

        opening = float(max(1, lower_idx - upper_idx))
        min_open = max(2.0, h * 0.08)
        max_open = max(min_open, h * 0.9)
        return float(np.clip(opening, min_open, max_open))

    def _rect_to_landmarks(self, eye: _Rect, opening: float) -> EyeLandmarks:
        x = float(eye.x)
        y = float(eye.y)
        w = float(eye.w)
        h = float(eye.h)

        left_x = x + 0.05 * w
        right_x = x + 0.95 * w
        q1_x = x + 0.30 * w
        q3_x = x + 0.70 * w

        center_y = y + 0.5 * h
        half_open = max(1.0, opening * 0.5)
        upper_y = center_y - half_open
        lower_y = center_y + half_open

        return EyeLandmarks(
            p1=(left_x, center_y),
            p2=(q1_x, upper_y),
            p3=(q3_x, upper_y),
            p4=(right_x, center_y),
            p5=(q3_x, lower_y),
            p6=(q1_x, lower_y),
        )
