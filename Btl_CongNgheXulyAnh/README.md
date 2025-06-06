# NHẬN DIỆN KHUÔN MẶT CẢNH BÁO NGƯỜI LẠ VÀO VÙNG KIỂM SOÁT CỦA CAMERA

## Giới thiệu chung

Ứng dụng giúp nhận diện khuôn mặt qua camera IP, phát hiện người lạ và cảnh báo qua Telegram, đồng thời ghi lại video sự kiện. Hệ thống phù hợp cho giám sát an ninh tại nhà, văn phòng, kho xưởng...

## Sơ đồ hệ thống & các chức năng

```
[Camera IP] ---> [Phần mềm nhận diện khuôn mặt] ---> [Báo động âm thanh]
                                              |---> [Gửi ảnh cảnh báo Telegram]
                                              |---> [Ghi & lưu video sự kiện]
                                              |---> [Giao diện xem trực tiếp & quản lý video]
```

**Chức năng chính:**
- Nhận diện khuôn mặt so với dữ liệu đã biết.
- Phát hiện người lạ, phát âm thanh cảnh báo.
- Gửi ảnh cảnh báo qua Telegram.
- Tự động ghi và lưu video khi phát hiện người lạ.
- Xem lại video sự kiện trên giao diện.

## Bảng công nghệ sử dụng

| Thành phần         | Công nghệ/Thư viện      | Vai trò chính                           |
|--------------------|------------------------|-----------------------------------------|
| Nhận diện khuôn mặt| face_recognition       | Phát hiện & mã hóa khuôn mặt            |
| Xử lý ảnh/video    | OpenCV                 | Đọc, ghi, xử lý khung hình & video      |
| Giao diện          | Tkinter, Pillow        | Hiển thị hình ảnh, giao diện người dùng |
| Cảnh báo âm thanh  | winsound               | Phát âm thanh báo động                  |
| Gửi cảnh báo       | requests, Telegram API | Gửi ảnh cảnh báo qua Telegram           |
| Đa luồng           | threading              | Xử lý song song các tác vụ              |

## Hướng dẫn sử dụng

1. **Cài đặt thư viện:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Thêm khuôn mặt đã biết:**
    - Thêm ảnh vào thư mục `known_faces/<Tên>/`.
    - Mỗi người một thư mục con, tên thư mục là tên người.

3. **Cấu hình camera:**
    - Đảm bảo camera IP hỗ trợ RTSP, chỉnh URL trong hàm `open_camera()` .

4. **Cấu hình Telegram:**
    - Thay đổi `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` trong `main.py`.

5. **Chạy chương trình:**
    ```sh
    python main.py
    ```

6. **Sử dụng giao diện:**
    - Nhấn "Bắt đầu nhận diện" để khởi động camera.
    - Bật/tắt chế độ cảnh báo người lạ.
    - Xem lại video đã lưu ở khung bên phải.

## Yêu cầu

- Python 3.12
- Camera IP hỗ trợ RTSP
- Kết nối Internet để gửi Telegram

## Thư mục

- `main.py`: Chương trình chính.
- `interface.py`: Giao diện người dùng (nếu dùng).
- `known_faces/`: Thư mục chứa ảnh khuôn mặt đã biết.
- `alarm_new.wav`: Âm thanh cảnh báo.
- Các file `.avi`: Video ghi lại sự kiện.

## Hướng mở rộng trong tương lai

| Định hướng mở rộng                                      | Mô tả ngắn                                      |
|--------------------------------------------------------|-------------------------------------------------|
| Nhận diện nhiều camera                                 | Hỗ trợ giám sát nhiều khu vực cùng lúc           |
| Lưu trữ đám mây                                        | Tự động upload video/ảnh lên cloud               |
| Quản lý người dùng                                     | Thêm/xóa/sửa người dùng qua giao diện            |
| Tăng tốc nhận diện                                     | Sử dụng GPU hoặc model deep learning nâng cao     |
| Nhận diện hành vi bất thường                           | Phát hiện các hành động lạ, xâm nhập bất hợp pháp |
| Đa nền tảng cảnh báo                                   | Gửi cảnh báo qua Zalo, Email, SMS...             |


---

**Tác giả:**  
- Nguyễn Thanh Hải