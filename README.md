# S-Eye: Driver Drowsiness Detection System

Real-time driver drowsiness detection using OpenCV, EAR sequences, and a custom LSTM model.

## Overview

**S-Eye** monitors the driver's eyes through a webcam and triggers an alarm when drowsiness is detected.

- **OpenCV**: Detects face and eyes using Haar cascades.
- **EAR**: Extracts Eye Aspect Ratio values from detected eye regions.
- **LSTM**: Classifies drowsiness from a 16-frame EAR sequence.
- **ONNX Runtime**: Runs the trained model efficiently during realtime monitoring.
- **Fallback rules**: Uses classical EAR threshold logic if the ONNX model is unavailable.

Main runtime flow:

```text
Webcam frame -> face/eye detection -> EAR calculation -> LSTM/ONNX prediction -> alert decision -> alarm
```

## Installation

### Prerequisites

- Python 3.10+
- Windows
- Webcam

### Setup

```bash
cd d:\Projects\s-eye
```

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\Activate.ps1
```

```bash
pip install -e .
```

For training, evaluation, and ONNX export:

```bash
pip install -e ".[ml]"
```

For development tools as well:

```bash
pip install -e ".[dev,ml]"
```

## Running

Run the realtime monitor:

```bash
python -m src.main
```

After installing the package, you can also run:

```bash
s-eye
```

Runtime behavior:

- First 20 seconds: calibration phase, alarm is disabled.
- After calibration: active drowsiness monitoring.
- Exit: press `Q` or close the OpenCV window.

## Training Pipeline

Use this pipeline when you want to train the LSTM model on your own EAR data.

### 1. Collect Labeled EAR Data

```bash
python scripts/collect_labeled_ear.py --output logs/manual_labeled_ear.csv
```

Controls:

- `0`: label current state as alert.
- `1`: label current state as drowsy.
- `r`: toggle recording on/off.
- `q`: quit.

Output format:

```text
session_id,frame_index,timestamp,ear,is_drowsy,label_name,has_face
```

### 2. Build 16-Frame Sequences

```bash
python scripts/build_sequences_from_runtime_log.py --input logs/manual_labeled_ear.csv --output data/ear_sequences.csv --window-size 16 --stride 4 --label-column is_drowsy
```

This converts frame-level EAR rows into sequence-level training samples.

Output format:

```text
sequence_id,timestep,ear,label
```

### 3. Split Dataset By Session

```bash
python scripts/split_sequences_by_session.py --input data/ear_sequences.csv --out-dir data/splits --train-ratio 0.7 --val-ratio 0.15 --seed 42
```

This creates:

- `data/splits/train.csv`
- `data/splits/val.csv`
- `data/splits/test.csv`

The split is done by session to reduce data leakage between train and test sets.

### 4. Train LSTM Checkpoint

```bash
python scripts/train_lstm.py --csv data/ear_sequences.csv --train-csv data/splits/train.csv --val-csv data/splits/val.csv --output models/lstm_drowsiness.pt --epochs 20 --seq-len 16
```

The training script saves the best validation checkpoint to:

```text
models/lstm_drowsiness.pt
```

### 5. Evaluate On Test Split

```bash
python scripts/evaluate_lstm.py --checkpoint models/lstm_drowsiness.pt --csv data/splits/test.csv --threshold 0.5
```

The evaluation script reports:

- confusion matrix: `TP`, `FP`, `TN`, `FN`
- precision
- recall
- F1 score
- accuracy

### 6. Export To ONNX

```bash
python scripts/export_lstm_onnx.py --checkpoint models/lstm_drowsiness.pt --output models/drowsiness.onnx
```

The exported ONNX model is used by the realtime application:

```text
models/drowsiness.onnx
```

### 7. Run With The New Model

```bash
python -m src.main
```

## Project Structure

```text
src/
├── main.py                                  # Application entry point
├── core/
│   ├── application/
│   │   ├── ports/                           # Interfaces for alarm, camera, detector, classifier
│   │   └── use_cases/process_frame.py       # Main frame-processing use case
│   └── domain/
│       ├── entities/driver_state.py         # Driver state across frames
│       ├── services/drowsiness_rules.py     # EAR calculation
│       └── value_objects/eye_landmarks.py   # Eye landmark value object
├── infrastructure/
│   ├── audio/system_alarm.py                # Windows beep alarm
│   ├── camera/opencv_camera.py              # OpenCV camera adapter
│   ├── ml/onnx_drowsiness_classifier.py     # ONNX Runtime classifier
│   └── vision/manual_eye_detector.py        # Haar cascade eye detector
├── presentation/
│   └── cli/monitor_loop.py                  # Realtime OpenCV monitor loop
└── shared/config.py                         # Runtime configuration

scripts/
├── collect_labeled_ear.py                   # Collect manually labeled EAR data
├── build_sequences_from_runtime_log.py      # Convert frame logs to EAR sequences
├── split_sequences_by_session.py            # Create train/val/test splits
├── train_lstm.py                            # Train custom LSTM model
├── evaluate_lstm.py                         # Evaluate checkpoint
├── export_lstm_onnx.py                      # Export PyTorch checkpoint to ONNX
├── run_dev.cmd                              # Windows CMD dev runner
└── run_dev.ps1                              # PowerShell dev runner

models/
├── lstm_drowsiness.pt                       # PyTorch checkpoint
└── drowsiness.onnx                          # ONNX runtime model

data/
├── ear_sequences.csv                        # Full sequence dataset
└── splits/
    ├── train.csv
    ├── val.csv
    └── test.csv
```

## Configuration

Edit `src/shared/config.py`.

Important values:

```python
ml.enabled = True
ml.model_path = "models/drowsiness.onnx"
ml.sequence_length = 16
ml.drowsy_probability_threshold = 0.50
calibration.duration_seconds = 20
drowsiness.ear_threshold = 0.21
drowsiness.min_closed_frames = 12
```

Notes:

- `drowsiness.ear_threshold` is the default EAR threshold for rule-based fallback.
- During calibration, the app can replace the default EAR threshold with a personalized threshold.
- `ml.drowsy_probability_threshold` is the probability threshold used for ONNX/LSTM prediction.

## Development Runner

PowerShell:

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

CMD:

```bash
scripts\run_dev.cmd
```

These scripts create `.venv` if needed, install dependencies, and start the app.

## Troubleshooting

**Camera not found**: Close other apps using the webcam, such as Zoom, Teams, or browser camera tabs.

**ONNX model cannot be loaded**: Install ML dependencies with `pip install -e ".[ml]"` and check that `models/drowsiness.onnx` exists.

**False alarms**: Improve lighting, adjust camera angle, and let calibration finish before testing.

## License

MIT
