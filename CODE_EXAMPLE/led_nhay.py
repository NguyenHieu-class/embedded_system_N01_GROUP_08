import RPi.GPIO as GPIO
import time

# GPIO pins for 8 LEDs and button
led_pins = [4, 17, 18, 27, 22, 23, 24, 25]  # GPIO pins connected to 8 LEDs
button_pin = 21  # GPIO pin connected to the button

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Configure LED pins as output
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Configure button pin as input with pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Running state
running = False

def toggle_running(channel):
    global running
    running = not running
    if running:
        print("LED effect started")
    else:
        print("LED effect stopped")

# Set up interrupt for the button
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=toggle_running, bouncetime=300)

def display_leds(pattern):
    for i in range(8):
        GPIO.output(led_pins[i], GPIO.HIGH if (pattern >> (7 - i)) & 1 else GPIO.LOW)

def led_effect():
    patterns = [
        0b00011000,
        0b00100100,
        0b01000010,
        0b10000001,
        0b00000000,
        0b10000001,
        0b01000010,
        0b00100100,
        0b00011000
    ]

    while True:
        if running:
            for pattern in patterns:
                display_leds(pattern)
                time.sleep(1)
        else:
            time.sleep(0.1)

try:
    led_effect()
except KeyboardInterrupt:
    print("\nProgram stopped")
finally:
    GPIO.cleanup()  # Clean up all GPIO pins before exiting the program
