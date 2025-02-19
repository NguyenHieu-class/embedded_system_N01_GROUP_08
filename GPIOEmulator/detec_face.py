import cv2
import face_recognition

# Khởi động camera USB (thường là 0 hoặc 1)
video_capture = cv2.VideoCapture(0)

while True:
    # Đọc từng frame từ camera
    ret, frame = video_capture.read()
    if not ret:
        break

    # Chuyển ảnh sang định dạng RGB để sử dụng với face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Phát hiện vị trí khuôn mặt trong frame
    face_locations = face_recognition.face_locations(rgb_frame)

    for top, right, bottom, left in face_locations:
        # Vẽ hình chữ nhật quanh khuôn mặt
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Hiển thị hình ảnh
    cv2.imshow('Face Recognition', frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng camera và đóng cửa sổ
video_capture.release()
cv2.destroyAllWindows()
