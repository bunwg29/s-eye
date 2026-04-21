# S-Eye: Driver Drowsiness Detection System

Real-time drowsiness detection using computer vision and machine learning.

## Overview

**S-Eye** monitors driver eyes and triggers an alarm when drowsiness is detected.

- 📹 **OpenCV**: Real-time eye detection (Haar cascades)
- 🧠 **LSTM**: Neural network for drowsiness classification
- ⚡ **ONNX Runtime**: Efficient model inference
- 🔄 **Temporal Analysis**: Eye Aspect Ratio (EAR) over 16 frames

**Features**: Personal calibration (20s), Smart alerting, Fallback detection, ~100ms latency, 82% accuracy

## Installation

### Prerequisites

- Python 3.10+
- Windows 7+
- Webcam

### Setup

```bash
# Clone and enter project
cd d:\Projects\s-eye

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .

# For ML training/export scripts (optional)
pip install -e ".[ml]"
```

## Running

```bash
python -m src.main
```

- **First 20 seconds**: Calibration phase (no alarm)
- **After calibration**: Active drowsiness monitoring
- **Exit**: Press `Q` or close window

## Train Model

Use this pipeline when you want a model trained on your own data.

1. Collect labeled EAR data from webcam:

```bash
python scripts/collect_labeled_ear.py --output logs/manual_labeled_ear.csv
```

2. Build sequence dataset from logs:

```bash
python scripts/build_sequences_from_runtime_log.py \
	--input logs/manual_labeled_ear.csv \
	--output data/ear_sequences.csv \
	--window-size 16 \
	--stride 4 \
	--label-column is_drowsy
```

3. Split by session into train/val/test:

```bash
python scripts/split_sequences_by_session.py \
	--input data/ear_sequences.csv \
	--out-dir data/splits \
	--train-ratio 0.7 \
	--val-ratio 0.15 \
	--seed 42
```

4. Train LSTM checkpoint:

```bash
python scripts/train_lstm.py \
	--csv data/ear_sequences.csv \
	--train-csv data/splits/train.csv \
	--val-csv data/splits/val.csv \
	--output models/lstm_drowsiness.pt \
	--epochs 20 \
	--seq-len 16
```

5. Evaluate on test split:

```bash
python scripts/evaluate_lstm.py \
	--checkpoint models/lstm_drowsiness.pt \
	--csv data/splits/test.csv \
	--threshold 0.5
```

6. Export to ONNX for runtime inference:

```bash
python scripts/export_lstm_onnx.py \
	--checkpoint models/lstm_drowsiness.pt \
	--output models/drowsiness.onnx
```

7. Run app with the new ONNX model:

```bash
python -m src.main
```

## Project Structure

```
src/
├── main.py                    # Entry point
├── core/                      # Business logic
│   ├── application/           # Use cases
│   ├── domain/                # Entities & rules
│   └── infrastructure/        # Implementations
├── infrastructure/            # Camera, audio, ML, vision
├── presentation/              # CLI interface
└── shared/                    # Config

models/
├── drowsiness.onnx           # ONNX model

scripts/
├── train_lstm.py             # Training
├── export_lstm_onnx.py       # Export to ONNX
└── evaluate_lstm.py          # Evaluation

docs/
├── ARCHITECTURE.md           # System design
└── ML_WORKFLOW.md            # ML pipeline
```

## Configuration

Edit `src/shared/config.py`:

```python
ml.enabled = True
ml.drowsy_probability_threshold = 0.50    # Confidence threshold
ml.sequence_length = 16                   # LSTM input frames
calibration.duration_seconds = 20          # Calibration time
```

## Troubleshooting

**Cannot run scripts**

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

**Camera not found**: Close other camera apps (Zoom, Teams, etc.)

**False alarms**: Check lighting and camera angle quality.

## License

MIT
