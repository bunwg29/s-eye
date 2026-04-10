from typing import Any

from core.application.ports.eye_detector import EyeDetectorPort


class ManualEyeDetector(EyeDetectorPort):
    """Placeholder detector.

    TODO: Implement detector cổ điển tự xây dựng:
    1) Tiền xử lý ảnh xám + lọc nhiễu.
    2) Xác định ROI mặt/mắt (Haar/HOG thủ công hoặc heuristic).
    3) Trích xuất 6 điểm mốc cho mỗi mắt để tính EAR.
    """

    def detect(self, frame: Any):
        _ = frame
        return None
