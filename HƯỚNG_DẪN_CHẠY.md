# S-Eye: Hướng Dẫn Chạy Dự Án

Dự án **S-Eye** là một hệ thống phát hiện buồn ngủ của tài xế sử dụng computer vision và machine learning. Hệ thống sử dụng LSTM để phân loại trạng thái tỉnh táo/buồn ngủ dựa trên Eye Aspect Ratio (EAR) từ camera.

## 📋 Yêu Cầu Hệ Thống

- **OS**: Windows 7+
- **Python**: 3.11+ (khuyến nghị 3.11, tránh 3.14 vì vấn đề NumPy DLL trên Windows)
- **Camera**: Webcam hoặc camera USB
- **RAM**: Tối thiểu 4GB

## 🚀 Cài Đặt Ban Đầu

### 1. Clone hoặc tải dự án
```bash
cd d:\Projects\s-eye
```

### 2. Tạo Virtual Environment
```bash
python -m venv .venv
```

### 3. Kích hoạt Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.\.venv\Scripts\activate.bat
```

### 4. Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### 5. Cài đặt dự án ở chế độ phát triển
```bash
pip install -e .
```

## ▶️ Chạy Ứng Dụng

### Phương pháp 1: Sử dụng Script PowerShell (Khuyến nghị)
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

### Phương pháp 2: Chạy trực tiếp bằng Python
```bash
python -m src.main
```

## 📊 Quy Trình Chạy Ứng Dụng

1. **Khởi tạo hệ thống** (~2 giây)
   - Tải mô hình ML (ONNX)
   - Kết nối camera
   - Chọn backend mặc định: `dshow` → `msmf` → tự động

2. **Giai đoạn Calibration** (20 giây)
   - ❌ **KHÔNG CÓ ÂM THANH CẢNH BÁO** trong lúc này
   - Hệ thống thu thập dữ liệu EAR để tính ngưỡng cá nhân
   - Giữ mắt mở bình thường trong giai đoạn này
   - Hiển thị: `[S-Eye] Calibration complete. samples=XXX threshold=Y.YY`

3. **Phát hiện buồn ngủ** (liên tục sau calibration)
   - Hệ thống theo dõi EAR từ camera
   - Sử dụng mô hình LSTM để dự đoán trạng thái buồn ngủ
   - Phát cảnh báo nếu xác suất buồn ngủ > 50%

4. **Thoát ứng dụng**
   - Nhấn `Q` hoặc đóng cửa sổ camera

## 🎯 Hành Động Cảnh Báo

### Khi Phát Hiện Buồn Ngủ:
- 🔊 Phát âm thanh cảnh báo liên tục (~0.75 giây mỗi lần)
- ⏱️ Cảnh báo sẽ kéo dài tối thiểu **2 giây** ngay cả khi mở mắt tạm thời
- 👁️ Chỉ **DỪNG** cảnh báo khi mắt mở trong **3 khung hình liên tiếp**

### Khi Mắt Đóng Hoàn Toàn:
- Cảnh báo tiếp tục phát mà không bị gián đoạn
- Sẽ dừng khi phát hiện mắt mở lại

## 🔧 Cấu Hình

Tệp cấu hình chính: `src/shared/config.py`

### Các thông số quan trọng:

```python
# ML Configuration
ml.enabled = True                                  # Bật/tắt ML mode
ml.model_path = "models/drowsiness.onnx"         # Đường dẫn mô hình
ml.drowsy_probability_threshold = 0.50            # Ngưỡng xác suất (0.5 = 50%)
ml.sequence_length = 16                           # Số frame dùng cho LSTM

# Calibration
calibration.duration_seconds = 20                 # Thời gian calibration (giây)

# Alert Behavior
min_alert_hold_seconds = 2.0                      # Cảnh báo tối thiểu (giây)
reopen_eye_frames_required = 3                    # Frame cần để thoát khỏi cảnh báo

# Camera
camera.backend_preference = "dshow,msmf,any"     # Ưu tiên backend camera
camera.camera_index = 0                           # Chỉ số camera (0 = mặc định)
```

## 🧪 Chạy Unit Tests

```bash
# Chạy tất cả tests
pytest -v

# Chạy tests cụ thể
pytest tests/unit/test_process_frame.py -v

# Chạy nhanh (quiet mode)
pytest -q
```

## 📁 Cấu Trúc Dự Án

```
s-eye/
├── src/                              # Mã nguồn chính
│   ├── main.py                       # Điểm vào chính
│   ├── core/                         # Lôgic nghiệp vụ (Clean Architecture)
│   │   ├── application/              # Use cases
│   │   │   ├── use_cases/
│   │   │   │   └── process_frame.py # State machine xử lý khung hình
│   │   │   └── ports/               # Interfaces
│   │   ├── domain/                   # Entities & Services
│   │   │   ├── entities/
│   │   │   │   └── driver_state.py  # Trạng thái tài xế
│   │   │   ├── services/
│   │   │   │   └── drowsiness_rules.py # EAR computation
│   │   │   └── value_objects/
│   │   │       └── eye_landmarks.py
│   ├── infrastructure/               # Implementasi chi tiết (Camera, AL, ML)
│   │   ├── camera/
│   │   │   └── opencv_camera.py     # Backend lựa chọn (dshow/msmf)
│   │   ├── vision/
│   │   │   ├── manual_eye_detector.py # Haar cascade + temporal smoothing
│   │   │   └── preprocess.py         # Xử lý ảnh
│   │   ├── audio/
│   │   │   └── system_alarm.py       # Windows winsound alarm
│   │   └── ml/
│   │       └── onnx_drowsiness_classifier.py # ONNX Runtime inference
│   ├── presentation/
│   │   └── cli/
│   │       └── monitor_loop.py       # Vòng lặp chính thực thi
│   └── shared/
│       └── config.py                  # Cấu hình toàn cục
├── tests/                             # Unit tests
│   ├── conftest.py
│   └── unit/
│       ├── test_drowsiness_rules.py
│       └── test_process_frame.py
├── models/
│   └── drowsiness.onnx               # Mô hình LSTM đã export
├── scripts/
│   ├── run_dev.ps1                   # Script chạy PowerShell
│   └── run_dev.cmd                   # Script chạy CMD
├── docs/
│   └── ARCHITECTURE.md               # Kiến trúc chi tiết
├── pyproject.toml                    # Cấu hình dự án
├── requirements.txt                  # Dependencies
└── README.md
```

## 🐛 Gỡ Lỗi Thường Gặp

### 1. Lỗi: `ImportError: DLL load failed while importing _umath_linalg`
**Nguyên nhân**: Python 3.14+ có vấn đề với NumPy trên Windows (App Control policy)
**Giải pháp**: 
- Nâng cấp Python lên 3.11
- Hoặc whitelistaed NumPy DLL trong Windows App Control

### 2. Lỗi: `Cannot be loaded because running scripts is disabled`
**Nguyên nhân**: ExecutionPolicy bị giới hạn
**Giải pháp**:
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

### 3. Lỗi: `Camera not found` hoặc `Cannot open video capture`
**Nguyên nhân**: Camera bị chiếm dụng hoặc driver lỗi
**Giải pháp**:
- Kiểm tra camera trong Device Manager
- Đóng ứng dụng khác dùng camera (Zoom, Teams, OBS...)
- Thử thay đổi `camera.backend_preference` trong config.py

### 4. Cảnh báo phát liên tục mặc dù mắt không nhắm
**Nguyên nhân**: Ngưỡng calibration quá thấp
**Giải pháp**:
- Đóng ứng dụng
- Chạy lại để recalibrate
- Hoặc điều chỉnh `ml.drowsy_probability_threshold` lên 0.55-0.60

### 5. Không có âm thanh cánh báo
**Nguyên nhân**: Có thể đang trong giai đoạn calibration (20 giây đầu)
**Giải pháp**:
- Chờ tới khi thấy `[S-Eye] Calibration complete`
- Kiểm tra âm lượng Windows
- Kiểm tra `alarm_enabled` parameter

## 📈 Hiệu Suất

- **FPS**: 25-30 FPS (tùy camera)
- **Latency**: ~100ms từ khung hình đến cảnh báo
- **Độ chính xác ML**: 81.75% (validation set từ 3 session)
- **RAM sử dụng**: ~200-300MB

## 🔐 Thông Tin Bảo Mật

- Dự án chỉ xử lý dữ liệu video cục bộ
- Không có kết nối internet
- Dữ liệu calibration chỉ lưu trong bộ nhớ (không lưu trữ)

## 📚 Tài Nguyên Bổ Sung

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Chi tiết kiến trúc dự án
- [Idea.md](Idea.md) - Ý tưởng ban đầu
- [README.md](README.md) - Tổng quan dự án

## ❓ Câu Hỏi Thường Gặp

**Q: Làm sao để cải thiện độ chính xác?**
A: 
- Giữ camera ở vị trí tốt, sáng đủ
- Cho phép ít nhất 20 giây calibration
- Nếu vẫn chưa tốt, có thể retrain mô hình với dữ liệu mới

**Q: Có thể tắt âm thanh cảnh báo không?**
A: Chỉnh `alarm_enabled = False` hoặc comment dòng trigger trong `system_alarm.py`

**Q: Tại sao cảnh báo bị lệch so với khi tôi nhắm mắt?**
A: Do độ trễ xử lý (~100ms) và cần 16 frame tích lũy cho LSTM

**Q: Có thể kết nối với ứng dụng khác không?**
A: Có. Sửa đổi `monitor_loop.py` để gỡ khỏi dependency vào `SystemAlarm` và tích hợp hệ thống thông báo của bạn.

---

**Phiên bản**: 0.1.0  
**Cập nhật lần cuối**: April 2026  
**Tác giả**: S-Eye Development Team
