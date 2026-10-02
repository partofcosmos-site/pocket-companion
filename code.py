import time
import board
import busio
import digitalio
import pwmio
import adafruit_ssd1306

# Initialize I2C for SSD1306 OLED (128x64)
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize Buttons (with internal pull-ups)
btn_left = digitalio.DigitalInOut(board.GP2)
btn_left.direction = digitalio.Direction.INPUT
btn_left.pull = digitalio.Pull.UP

btn_action = digitalio.DigitalInOut(board.GP3)
btn_action.direction = digitalio.Direction.INPUT
btn_action.pull = digitalio.Pull.UP

btn_right = digitalio.DigitalInOut(board.GP4)
btn_right.direction = digitalio.Direction.INPUT
btn_right.pull = digitalio.Pull.UP

# Buzzer setup
try:
    buzzer = pwmio.PWMOut(board.GP5, duty_cycle=0, frequency=440, variable_frequency=True)
except Exception:
    buzzer = None

def beep(freq, duration=0.08):
    if buzzer:
        buzzer.frequency = freq
        buzzer.duty_cycle = 32768
        time.sleep(duration)
        buzzer.duty_cycle = 0

# Game State
mode = 0  # 0: Pet / Companion, 1: Reflex Mini-game, 2: Study Timer
modes = ["Pet", "Reflex", "Timer"]
pet_mood = 100
score = 0

def draw_screen():
    oled.fill(0)
    oled.text(f"Mode: {modes[mode]}", 0, 0, 1)
    oled.hline(0, 10, 128, 1)
    
    if mode == 0:
        oled.text("( ^ _ ^ )", 38, 25, 1)
        oled.text(f"Happiness: {pet_mood}%", 15, 48, 1)
    elif mode == 1:
        oled.text("Press Action!", 20, 25, 1)
        oled.text(f"Score: {score}", 38, 45, 1)
    elif mode == 2:
        oled.text("Study Timer", 30, 22, 1)
        oled.text("Focus Mode ON", 24, 42, 1)
        
    oled.show()

beep(880, 0.1)
draw_screen()

while True:
    # Button checks (active low)
    if not btn_left.value:
        mode = (mode - 1) % len(modes)
        beep(523, 0.05)
        draw_screen()
        time.sleep(0.2)
        
    if not btn_right.value:
        mode = (mode + 1) % len(modes)
        beep(659, 0.05)
        draw_screen()
        time.sleep(0.2)
        
    if not btn_action.value:
        if mode == 0:
            pet_mood = min(100, pet_mood + 10)
        elif mode == 1:
            score += 1
        beep(1046, 0.05)
        draw_screen()
        time.sleep(0.2)
        
    time.sleep(0.05)
