#!/usr/bin/env python3
from EmulatorGUI import GPIO  # Sử dụng module GPIO giả lập (xem :contentReference[oaicite:0]{index=0}, :contentReference[oaicite:1]{index=1}, :contentReference[oaicite:2]{index=2})
#import Adafruit_DHT  # Comment: không dùng cảm biến thật, dữ liệu sẽ được tạo ngẫu nhiên
import time
import threading
import random
import tkinter as tk

# --- CẤU HÌNH CHÂN GPIO ---
SENSOR_90_PIN    = 22   # Cảm biến sản phẩm đạt 90cm
SENSOR_45_PIN    = 26   # Cảm biến sản phẩm đạt 45cm
START_BUTTON_PIN = 23   # Nút Start (trả về 0 khi nhấn)
STOP_BUTTON_PIN  = 24   # Nút Stop (trả về 0 khi nhấn)
DHT22_PIN        = 4    # Cảm biến nhiệt độ – độ ẩm (không dùng thật)

RELAY_90_PIN = 17  # Rơ le cho sản phẩm 90cm
RELAY_45_PIN = 27  # Rơ le cho sản phẩm 45cm
LED_PIN      = 25  # LED báo hiệu

# --- KHỞI TẠO "CẢM BIẾN" DHT22 ---  
# Comment: không dùng Adafruit_DHT, sử dụng giá trị ngẫu nhiên

# --- BIẾN TOÀN CỤC ---
running = False  # Trạng thái hệ thống (đang đếm hay không)
count_90 = 0     # Số sản phẩm đạt 90cm
count_45 = 0     # Số sản phẩm đạt 45cm

# Biến lưu trữ dữ liệu cảm biến giả lập
sim_temperature = 0.0
sim_humidity = 0.0
led_status = False

# --- KHỞI TẠO GPIO GIẢ LẬP ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SENSOR_90_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SENSOR_45_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(START_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STOP_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(RELAY_90_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(RELAY_45_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

# --- LỚP GIẢ LẬP "LCD LED" ---
class SimulatedDisplay(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()  # Khởi chạy luồng riêng cho giao diện

    def run(self):
        self.root = tk.Tk()
        self.root.title("Simulated LED LCD Display")
        # Tạo 3 label: dòng 1 LCD, dòng 2 LCD, và trạng thái LED
        self.label_line1 = tk.Label(self.root, text="", font=("Consolas", 16), width=20, anchor="w")
        self.label_line2 = tk.Label(self.root, text="", font=("Consolas", 16), width=20, anchor="w")
        self.label_led   = tk.Label(self.root, text="", font=("Consolas", 16), width=20, anchor="w")
        self.label_line1.pack(pady=5)
        self.label_line2.pack(pady=5)
        self.label_led.pack(pady=5)
        self.update_display()
        self.root.mainloop()

    def update_display(self):
        global running, sim_temperature, sim_humidity, count_90, count_45, led_status
        # Khi hệ thống đang chạy hay chưa chạy sẽ có cách hiển thị khác nhau:
        if running:
            line1 = "Temp:{:.1f}C Hum:{:.0f}%".format(sim_temperature, sim_humidity)
            line2 = "90c={:<3} 45c={:<3}".format(count_90, count_45)
        else:
            line1 = "DEM SAN PHAM C"
            line2 = "Temp:{:.1f}C Hum:{:.0f}%".format(sim_temperature, sim_humidity)
        led_line = "LED: " + ("ON" if led_status else "OFF")
        self.label_line1.config(text=line1)
        self.label_line2.config(text=line2)
        self.label_led.config(text=led_line)
        # Cập nhật giao diện mỗi 500ms
        self.root.after(500, self.update_display)

# --- HÀM CẬP NHẬT NHIỆT ĐỘ – ĐỘ ẨM ---
def update_temp_humidity():
    global running, sim_temperature, sim_humidity
    while True:
        # Sinh dữ liệu ngẫu nhiên cho cảm biến DHT22:
        temperature = random.uniform(20.0, 30.0)  # nhiệt độ từ 20 đến 30°C
        humidity = random.uniform(40, 60)          # độ ẩm từ 40% đến 60%
        sim_temperature = temperature
        sim_humidity = humidity
        time.sleep(1)

# --- HÀM NHÍP NHÁY LED ---
def led_blink():
    global running, led_status
    while True:
        if running:
            led_status = not led_status
            GPIO.output(LED_PIN, GPIO.HIGH if led_status else GPIO.LOW)
            time.sleep(2)
        else:
            led_status = False
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.5)

# --- HÀM PHÁT HIỆN SẢN PHẨM VÀ ĐIỀU KHIỂN RƠ LE ---
def product_detection():
    global running, count_90, count_45
    while True:
        if running:
            sensor_90 = GPIO.input(SENSOR_90_PIN)
            sensor_45 = GPIO.input(SENSOR_45_PIN)
            # Giả lập: nếu cảm biến trả về False (0) thì coi như sản phẩm đạt chiều cao tương ứng
            if sensor_90 == False:
                count_90 += 1
                GPIO.output(RELAY_90_PIN, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(RELAY_90_PIN, GPIO.LOW)
                # Chờ cho sản phẩm rời khỏi vùng cảm biến
                while GPIO.input(SENSOR_90_PIN) == False:
                    time.sleep(0.1)
            elif sensor_45 == False:
                count_45 += 1
                GPIO.output(RELAY_45_PIN, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(RELAY_45_PIN, GPIO.LOW)
                while GPIO.input(SENSOR_45_PIN) == False:
                    time.sleep(0.1)
        time.sleep(0.1)

# --- HÀM GIÁM SÁT NÚT START/STOP ---
def start_stop_monitor():
    global running, count_90, count_45
    while True:
        # Nếu hệ thống chưa chạy và nút Start được nhấn (trả về False)
        if not running and GPIO.input(START_BUTTON_PIN) == False:
            running = True
            count_90 = 0
            count_45 = 0
            time.sleep(0.5)  # chống nhiễu
        # Nếu hệ thống đang chạy và nút Stop được nhấn
        if running and GPIO.input(STOP_BUTTON_PIN) == False:
            running = False
            time.sleep(0.5)
        time.sleep(0.1)

# --- CHƯƠNG TRÌNH CHÍNH ---
try:
    # Khởi tạo cửa sổ giả lập LCD LED
    display_thread = SimulatedDisplay()

    # Khởi tạo các luồng xử lý đồng thời
    temp_thread    = threading.Thread(target=update_temp_humidity, daemon=True)
    led_thread     = threading.Thread(target=led_blink, daemon=True)
    product_thread = threading.Thread(target=product_detection, daemon=True)
    button_thread  = threading.Thread(target=start_stop_monitor, daemon=True)
    
    temp_thread.start()
    led_thread.start()
    product_thread.start()
    button_thread.start()

    # Giữ chương trình chính chạy (vòng lặp này sẽ không chặn cửa sổ LCD vì display_thread có mainloop riêng)
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Dừng chương trình...")
finally:
    GPIO.cleanup()
