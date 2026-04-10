# S-Eye

Hệ thống cảnh báo buồn ngủ cho tài xế bằng xử lý ảnh cổ điển (không dùng AI model suy luận).

## Mục tiêu kỹ thuật
- Theo dõi mắt theo thời gian thực từ camera.
- Tính EAR (Eye Aspect Ratio) từ landmarks mắt.
- Cảnh báo âm thanh + thông báo khi tài xế nhắm mắt quá ngưỡng.
- Kiến trúc Clean Architecture để dễ mở rộng/testing.

## Cấu trúc thư mục
- `src/core`: Domain + Use case (không phụ thuộc framework)
- `src/infrastructure`: Camera, vision, audio (phụ thuộc OpenCV/hệ thống)
- `src/presentation`: Điểm vào CLI/UI
- `src/shared`: Config, logging, tiện ích chung
- `tests`: Unit + integration tests

## Chạy nhanh
1. Tạo môi trường ảo và cài dependencies.
2. Chạy:
   - `python -m main`
   - hoặc sau khi cài package editable: `s-eye`

## Ghi chú quan trọng
Dự án này thiết kế theo hướng **không dùng model học sâu**. Các bước phát hiện và cảnh báo nên dùng thuật toán cổ điển: tiền xử lý ảnh, ROI, hình học, ngưỡng logic theo thời gian.
