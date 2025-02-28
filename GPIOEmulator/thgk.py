#!/usr/bin/env python3
from EmulatorGUI import GPIO  # Sử dụng module GPIO từ EmulatorGUI (xem :contentReference[oaicite:0]{index=0}, :contentReference[oaicite:1]{index=1}, :contentReference[oaicite:2]{index=2})
import Adafruit_DHT
import time
import threading
from RPLCD.i2c import CharLCD

# --- CẤU HÌNH CHÂN GPIO ---
# Các chân dựa trên giả lập: số chân ở đây phải trùng với các định nghĩa trong EmulatorGUI.py
SENSOR_90_PIN    = 22   # Cảm biến 90cm
SENSOR_45_PIN    = 26   # Cảm biến 45cm
START_BUTTON_PIN = 23   # Nút Start (trả về 0 khi nhấn)
STOP_BUTTON_PIN  = 24   # Nút Stop  (trả về 0 khi nhấn)
DHT22_PIN        = 4    # Cảm biến nhiệt độ – độ ẩm

RELAY_90_PIN = 17  # Rơ le cho sản phẩm 90cm
RELAY_45_PIN = 27  # Rơ le cho sản phẩm 45cm
LED_PIN      = 25  # LED báo hiệu

# LCD 16x2 qua I2C (địa chỉ và cổng có thể thay đổi tùy module của bạn)
I2C_LCD_ADDRESS = 0x27  
I2C_LCD_PORT    = 1

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

# --- KHỞI TẠO LCD ---
lcd = CharLCD('PCF8574', I2C_LCD_ADDRESS, port=I2C_LCD_PORT, cols=16, rows=2)

# --- KHỞI TẠO CẢM BIẾN DHT22 ---
DHT_SENSOR = Adafruit_DHT.DHT22

# --- BIẾN TOÀN CỤC ---
running = False  # Trạng thái hệ thống (đang đếm hay không)
count_90 = 0     # Số sản phẩm đạt 90cm
count_45 = 0     # Số sản phẩm đạt 45cm

# --- HÀM CẬP NHẬT NHIỆT ĐỘ – ĐỘ ẨM ---
def update_temp_humidity():
    global running
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT22_PIN)
        if humidity is not None and temperature is not None:
            temp_hum_str = "Temp:{:.1f}C Hum:{:.0f}%".format(temperature, humidity)
        else:
            temp_hum_str = "Sensor Error"
        
        if running:
            # Khi đang đếm, dòng 1 LCD cập nhật nhiệt độ – độ ẩm
            lcd.cursor_pos = (0, 0)
            lcd.write_string(temp_hum_str.ljust(16))
        else:
            # Trạng thái ban đầu: dòng 1 hiển thị tiêu đề, dòng 2 hiển thị nhiệt độ – độ ẩm
            lcd.cursor_pos = (0, 0)
            lcd.write_string("DEM SAN PHAM C".ljust(16))
            lcd.cursor_pos = (1, 0)
            lcd.write_string(temp_hum_str.ljust(16))
        time.sleep(1)

# --- HÀM NHÍP NHÁY LED ---
def led_blink():
    global running
    led_state = False
    while True:
        if running:
            led_state = not led_state
            GPIO.output(LED_PIN, GPIO.HIGH if led_state else GPIO.LOW)
            time.sleep(2)
        else:
            # Khi không chạy, đảm bảo LED tắt
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.5)

# --- HÀM PHÁT HIỆN SẢN PHẨM VÀ ĐIỀU KHIỂN RƠ LE ---
def product_detection():
    global running, count_90, count_45
    while True:
        if running:
            sensor_90 = GPIO.input(SENSOR_90_PIN)
            sensor_45 = GPIO.input(SENSOR_45_PIN)
            # Nếu sản phẩm đạt 90cm (sensor trả về 0)
            if sensor_90 == False:  # Vì PUD_UP nên giá trị logic: 0 -> False
                count_90 += 1
                # Kích hoạt rơ le 90cm (bật trong 0.5 giây)
                GPIO.output(RELAY_90_PIN, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(RELAY_90_PIN, GPIO.LOW)
                # Chờ cho sản phẩm rời khỏi vùng cảm biến
                while GPIO.input(SENSOR_90_PIN) == False:
                    time.sleep(0.1)
            # Nếu không đạt 90cm mà cảm biến 45cm trả về 0
            elif sensor_45 == False:
                count_45 += 1
                GPIO.output(RELAY_45_PIN, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(RELAY_45_PIN, GPIO.LOW)
                while GPIO.input(SENSOR_45_PIN) == False:
                    time.sleep(0.1)
            
            # Cập nhật số đếm lên LCD dòng 2
            lcd.cursor_pos = (1, 0)
            lcd.write_string("90c={:<3} 45c={:<3}".format(count_90, count_45))
        time.sleep(0.1)

# --- HÀM GIÁM SÁT NÚT START/STOP ---
def start_stop_monitor():
    global running, count_90, count_45
    while True:
        # Nếu chưa chạy và nút Start được nhấn (trả về 0)
        if not running and GPIO.input(START_BUTTON_PIN) == False:
            running = True
            count_90 = 0
            count_45 = 0
            time.sleep(0.5)  # chống nhiễu
        # Nếu đang chạy và nút Stop được nhấn
        if running and GPIO.input(STOP_BUTTON_PIN) == False:
            running = False
            time.sleep(0.5)
        time.sleep(0.1)

# --- CHƯƠNG TRÌNH CHÍNH ---
try:
    # Khởi tạo các luồng xử lý đồng thời
    temp_thread    = threading.Thread(target=update_temp_humidity, daemon=True)
    led_thread     = threading.Thread(target=led_blink, daemon=True)
    product_thread = threading.Thread(target=product_detection, daemon=True)
    button_thread  = threading.Thread(target=start_stop_monitor, daemon=True)
    
    temp_thread.start()
    led_thread.start()
    product_thread.start()
    button_thread.start()

    # Giữ chương trình chính chạy liên tục
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Dừng chương trình...")
finally:
    GPIO.cleanup()
