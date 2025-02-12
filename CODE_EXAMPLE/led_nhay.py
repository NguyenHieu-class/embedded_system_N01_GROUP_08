import RPi.GPIO as GPIO
import time
import threading
import keyboard  # Thư viện bắt phím

# Định nghĩa các chân GPIO kết nối với LED
LED_PINS = [2, 3, 4, 17, 27, 22, 10, 9]  # Điều chỉnh theo sơ đồ nối dây
BUTTON_PIN = 18  # Chân nút nhấn

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PINS, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

running = False  # Biến trạng thái chạy/dừng

def update_leds(state):
    """Cập nhật trạng thái LED theo giá trị state (8-bit)."""
    for i in range(8):
        GPIO.output(LED_PINS[i], (state >> i) & 1)

def led_effect():
    """Hiệu ứng LED theo yêu cầu."""
    global running
    sequence = [0b00011000, 0b00100100, 0b01000010, 0b10000001,
                0b00000000, 0b10000001, 0b01000010, 0b00100100,
                0b00011000]
    index = 0
    while running:
        update_leds(sequence[index])
        index = (index + 1) % len(sequence)
        time.sleep(1)

def toggle_running():
    """Hàm chuyển đổi trạng thái chạy/dừng."""
    global running
    if running:
        running = False
        update_leds(0)  # Tắt tất cả LED khi dừng
    else:
        running = True
        threading.Thread(target=led_effect, daemon=True).start()

def button_listener():
    """Lắng nghe nút nhấn vật lý."""
    while True:
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
        toggle_running()
        time.sleep(0.3)  # Chống dội nút

# Chạy lắng nghe nút nhấn trên luồng riêng
threading.Thread(target=button_listener, daemon=True).start()

# Lắng nghe phím Space trên bàn phím để chạy/dừng (dùng khi chạy mô phỏng trên máy tính)
print("Nhấn Space để Start/Stop hiệu ứng LED (hoặc dùng nút nhấn trên Raspberry Pi)")
while True:
    if keyboard.is_pressed("space"):
        toggle_running()
        time.sleep(0.3)  # Chống dội phím
