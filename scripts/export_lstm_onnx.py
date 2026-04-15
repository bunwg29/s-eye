from __future__ import annotations

import argparse
from pathlib import Path

import torch

from train_lstm import LstmDrowsinessModel


def export_onnx(checkpoint_path: Path, output_path: Path) -> None:
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model = LstmDrowsinessModel(
        hidden_size=int(checkpoint["hidden_size"]),
        num_layers=int(checkpoint["num_layers"]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    seq_len = int(checkpoint["seq_len"])
    dummy = torch.zeros((1, seq_len, 1), dtype=torch.float32)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        dummy,
        str(output_path),
        input_names=["ear_sequence"],
        output_names=["drowsy_probability"],
        dynamic_axes={
            "ear_sequence": {1: "seq_len"},
        },
        opset_version=18,
        dynamo=False,
    )

    print(f"exported={output_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export trained LSTM checkpoint to ONNX")
    parser.add_argument("--checkpoint", default="models/lstm_drowsiness.pt")
    parser.add_argument("--output", default="models/drowsiness.onnx")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    export_onnx(Path(args.checkpoint), Path(args.output))
