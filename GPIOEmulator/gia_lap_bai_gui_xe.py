import tkinter as tk
from tkinter import filedialog, Label, Button, Radiobutton, Checkbutton, IntVar, StringVar, Entry, Frame
import RPi.GPIO as GPIO
import time

# Cấu hình GPIO
BARIE_PIN = 1  # Chân GPIO điều khiển barie

GPIO.setmode(GPIO.BCM)  # Chế độ đánh số GPIO
GPIO.setup(BARIE_PIN, GPIO.OUT)  # Thiết lập chân là Output

class LicensePlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng nhận dạng biển số xe")

        # Frame nhập biển số
        frame_input = Frame(root, bd=2, relief="groove")
        frame_input.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        Label(frame_input, text="Nhập biển số:").grid(row=0, column=0, sticky="w")
        self.plate_input = StringVar()
        Entry(frame_input, textvariable=self.plate_input, width=20, font=("Arial", 14)).grid(row=0, column=1, padx=5, pady=5)

        # Frame chức năng
        frame_func = Frame(root, bd=2, relief="groove")
        frame_func.grid(row=1, column=0, padx=5, pady=5, sticky="nw")

        self.auto_recog = IntVar()
        Checkbutton(frame_func, text="Tự động nhận dạng", variable=self.auto_recog).grid(row=0, column=0, sticky="w")

        self.display_mode = IntVar(value=0)
        Radiobutton(frame_func, text="Hiện ảnh trong quá trình tìm biển", variable=self.display_mode, value=1).grid(row=1, column=0, sticky="w")
        Radiobutton(frame_func, text="Hiện ảnh trong quá trình tách kí tự", variable=self.display_mode, value=2).grid(row=2, column=0, sticky="w")
        Radiobutton(frame_func, text="Không hiện", variable=self.display_mode, value=0).grid(row=3, column=0, sticky="w")

        Button(frame_func, text="Mở ảnh", command=self.open_image).grid(row=4, column=0, pady=2)
        Button(frame_func, text="Nhận dạng", command=self.recognize).grid(row=4, column=1, pady=2)
        Button(frame_func, text="Đóng ảnh", command=self.close_image).grid(row=5, column=0, pady=2)
        Button(frame_func, text="Thoát", command=self.quit_app).grid(row=5, column=1, pady=2)

        # Kết quả biển số
        self.plate_number = StringVar()
        Label(root, textvariable=self.plate_number, font=("Arial", 20, "bold")).grid(row=2, column=0, pady=10)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.plate_number.set(f"Đã mở: {file_path.split('/')[-1]}")

    def recognize(self):
        entered_text = self.plate_input.get().strip()
        if entered_text:
            self.plate_number.set(entered_text)  # Hiển thị biển số nhập từ bàn phím
        else:
            self.plate_number.set("90T-9999")  # Giả lập kết quả nếu không nhập gì

        # Điều khiển barie
        GPIO.output(BARIE_PIN, GPIO.HIGH)  # Mở barie
        time.sleep(3)  # Giữ trạng thái mở trong 3 giây
        GPIO.output(BARIE_PIN, GPIO.LOW)  # Đóng barie lại

    def close_image(self):
        self.plate_number.set("")

    def quit_app(self):
        GPIO.cleanup()  # Reset trạng thái GPIO khi thoát chương trình
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateApp(root)
    root.mainloop()
