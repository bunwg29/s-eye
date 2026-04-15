from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn

from train_lstm import LstmDrowsinessModel, SequenceSample, read_samples


@dataclass(frozen=True)
class Metrics:
    tp: int
    fp: int
    tn: int
    fn: int
    precision: float
    recall: float
    f1: float
    accuracy: float


def load_model(checkpoint_path: Path) -> tuple[nn.Module, int]:
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model = LstmDrowsinessModel(
        hidden_size=int(checkpoint["hidden_size"]),
        num_layers=int(checkpoint["num_layers"]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, int(checkpoint["seq_len"])


def sequence_to_tensor(values: list[float], seq_len: int) -> torch.Tensor:
    seq = values[:seq_len]
    if len(seq) < seq_len:
        fill = seq[-1] if seq else 0.0
        seq = seq + [fill] * (seq_len - len(seq))
    return torch.tensor(seq, dtype=torch.float32).reshape(1, seq_len, 1)


def evaluate(samples: list[SequenceSample], model: nn.Module, seq_len: int, threshold: float) -> Metrics:
    tp = fp = tn = fn = 0
    with torch.no_grad():
        for sample in samples:
            x = sequence_to_tensor(sample.values, seq_len)
            score = float(model(x).item())
            pred = 1 if score >= threshold else 0
            truth = 1 if sample.label >= 0.5 else 0

            if pred == 1 and truth == 1:
                tp += 1
            elif pred == 1 and truth == 0:
                fp += 1
            elif pred == 0 and truth == 0:
                tn += 1
            else:
                fn += 1

    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-9, precision + recall)
    accuracy = (tp + tn) / max(1, tp + fp + tn + fn)

    return Metrics(
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=f1,
        accuracy=accuracy,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate trained LSTM drowsiness checkpoint")
    parser.add_argument("--checkpoint", default="models/lstm_drowsiness.pt")
    parser.add_argument("--csv", default="data/ear_sequences.csv")
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    model, seq_len = load_model(Path(args.checkpoint))
    samples = read_samples(Path(args.csv))
    metrics = evaluate(samples, model, seq_len, threshold=float(args.threshold))

    print(f"samples={len(samples)} threshold={args.threshold}")
    print(f"confusion_matrix: TP={metrics.tp} FP={metrics.fp} TN={metrics.tn} FN={metrics.fn}")
    print(f"precision={metrics.precision:.4f}")
    print(f"recall={metrics.recall:.4f}")
    print(f"f1={metrics.f1:.4f}")
    print(f"accuracy={metrics.accuracy:.4f}")
