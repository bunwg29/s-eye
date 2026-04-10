# Clean Architecture - S-Eye

## 1) Core Domain (`core/domain`)
Chứa quy tắc nghiệp vụ thuần:
- Entity trạng thái tài xế
- Value object landmarks mắt
- Service tính EAR và phát hiện buồn ngủ

Không import OpenCV, UI hay thiết bị.

## 2) Application (`core/application`)
Điều phối use case:
- Nhận frame từ cổng vào
- Gọi detector -> landmarks -> EAR -> decision
- Trả dữ liệu cho lớp trình bày

Dùng các interface trong `ports` để phụ thuộc ngược.

## 3) Infrastructure (`infrastructure`)
Implement chi tiết kỹ thuật:
- Camera adapter (OpenCV)
- Vision adapter (tiền xử lý, phát hiện mắt/khuôn mặt)
- Audio adapter (phát beep/alarm)

## 4) Presentation (`presentation`)
CLI/UI loop, render thông tin, xử lý lifecycle.

## 5) Dependency Rule
`presentation -> application -> domain`

`infrastructure` implement port do `application` định nghĩa.

## 6) Quy tắc “không dùng model”
- Không dùng deep learning model/weights.
- Ưu tiên thuật toán hình học + threshold + temporal smoothing.
- Nếu dùng detector cổ điển (Haar/HOG), coi là bước tiền xử lý và tách trong infrastructure.
