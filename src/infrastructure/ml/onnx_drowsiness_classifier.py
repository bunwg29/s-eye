from __future__ import annotations

from pathlib import Path

import numpy as np

from core.application.ports.drowsiness_classifier import DrowsinessClassifierPort


class OnnxDrowsinessClassifier(DrowsinessClassifierPort):
    """ONNX Runtime adapter for sequence drowsiness classification."""

    def __init__(
        self,
        model_path: str,
        input_name: str | None = None,
        output_name: str | None = None,
    ) -> None:
        try:
            import onnxruntime as ort
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "onnxruntime is required for ML mode. Install with: pip install onnxruntime"
            ) from exc

        model_file = Path(model_path)
        if not model_file.exists():
            raise FileNotFoundError(f"ONNX model not found: {model_path}")

        self._ort = ort
        self._session = ort.InferenceSession(
            str(model_file), providers=["CPUExecutionProvider"]
        )

        inputs = self._session.get_inputs()
        outputs = self._session.get_outputs()
        if not inputs or not outputs:
            raise RuntimeError("Invalid ONNX model: missing input/output tensors")

        self._input_name = input_name or inputs[0].name
        self._output_name = output_name or outputs[0].name

    def predict_proba(self, ear_sequence: list[float]) -> float:
        if not ear_sequence:
            return 0.0

        sequence = np.asarray(ear_sequence, dtype=np.float32).reshape(1, -1, 1)
        output = self._session.run([self._output_name], {self._input_name: sequence})[0]

        proba = float(np.ravel(output)[0])
        return max(0.0, min(1.0, proba))
