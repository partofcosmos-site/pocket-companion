# Pocket Companion - CircuitPython handheld firmware
# Runs on Waveshare RP2040-Zero + 0.96" SSD1306 OLED (128x64)
# Features:
# 1. Virtual Pet: Animated reactions, moods, feeding & petting
# 2. Reflex Mini-game: Random delay millisecond reaction tester
# 3. Focus Timer: 25-minute Pomodoro study countdown with buzzer alarms

import time
import random
import board
import busio
import digitalio
import pwmio
import adafruit_ssd1306

# Hardware I2C for SSD1306 OLED (GP0=SDA, GP1=SCL)
# Standard 400kHz works great on short perfboard runs
i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=400000)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# 3x tactile push buttons (active low with RP2040 internal pull-ups)
# Saves us from having to cram three 10k pull-up resistors on the perfboard!
btn_left = digitalio.DigitalInOut(board.GP2)
btn_left.direction = digitalio.Direction.INPUT
btn_left.pull = digitalio.Pull.UP

btn_action = digitalio.DigitalInOut(board.GP3)
btn_action.direction = digitalio.Direction.INPUT
btn_action.pull = digitalio.Pull.UP

btn_right = digitalio.DigitalInOut(board.GP4)
btn_right.direction = digitalio.Direction.INPUT
btn_right.pull = digitalio.Pull.UP

# Passive piezo buzzer on GP5 for retro 8-bit sound effects
try:
    buzzer = pwmio.PWMOut(board.GP5, duty_cycle=0, frequency=440, variable_frequency=True)
except Exception:
    buzzer = None

def sound_tone(freq, duration=0.06):
    """Play a clean square wave tone on the piezo."""
    if buzzer and freq > 0:
        buzzer.frequency = int(freq)
        buzzer.duty_cycle = 32768  # 50% duty cycle
        time.sleep(duration)
        buzzer.duty_cycle = 0
    else:
        time.sleep(duration)

def sound_happy():
    sound_tone(523, 0.04)
    sound_tone(659, 0.04)
    sound_tone(784, 0.07)

def sound_boop():
    sound_tone(440, 0.04)

def sound_buzz():
    sound_tone(180, 0.12)

def sound_alarm():
    for _ in range(3):
        sound_tone(880, 0.08)
        time.sleep(0.04)
        sound_tone(1174, 0.12)
        time.sleep(0.06)

# UI & App State
modes = ["Pet", "Reflex", "Timer"]
mode = 0

# Pet variables
pet_happiness = 85
last_blink_time = time.monotonic()
pet_blinking = False
pet_eating = False
pet_eat_until = 0.0
last_decay_time = time.monotonic()

# Reflex game variables
# States: 0=Idle, 1=Waiting random delay, 2=Ready ("PRESS NOW!"), 3=Result
reflex_state = 0
reflex_trigger_time = 0.0
reflex_wait_until = 0.0
reaction_ms = 0
best_reflex_ms = 999

# Study timer variables
# Default: 25 minutes (Pomodoro)
timer_seconds = 25 * 60
timer_running = False
last_timer_tick = time.monotonic()

def draw_header():
    oled.fill(0)
    oled.text(f"[{modes[mode]}]", 0, 0, 1)
    oled.text("< L  R >", 76, 0, 1)
    oled.hline(0, 10, 128, 1)

def draw_pet(now):
    global pet_blinking, last_blink_time, pet_eating
    
    # Check blink timing every 3 seconds
    if now - last_blink_time > 3.0:
        pet_blinking = True
        if now - last_blink_time > 3.25:
            pet_blinking = False
            last_blink_time = now
            
    # Check eating animation timer
    if pet_eating and now > pet_eat_until:
        pet_eating = False
        
    # Choose expression based on mood and animations
    if pet_eating:
        face = "( > w < ) *"
        status = "Yum! +15 Mood"
    elif pet_happiness > 70:
        face = "( - _ - )" if pet_blinking else "( ^ _ ^ )"
        status = "Super happy!"
    elif pet_happiness > 35:
        face = "( o _ o )"
        status = "Chillin'"
    else:
        face = "( ; _ ; )"
        status = "Hungry / bored"
        
    # Center face on OLED (128x64)
    oled.text(face, 34, 22, 1)
    oled.text(status, 20, 38, 1)
    
    # Happiness progress bar at bottom
    bar_width = int((pet_happiness / 100.0) * 100)
    oled.rect(13, 52, 102, 9, 1)
    if bar_width > 0:
        oled.fill_rect(14, 53, min(100, bar_width), 7, 1)

def draw_reflex():
    if reflex_state == 0:
        oled.text("Reflex Tester", 24, 18, 1)
        oled.text("Press [ACT] to start", 4, 34, 1)
        if best_reflex_ms < 999:
            oled.text(f"Best: {best_reflex_ms}ms", 34, 50, 1)
    elif reflex_state == 1:
        oled.text("Get ready...", 30, 24, 1)
        oled.text("Wait for flash!", 16, 40, 1)
    elif reflex_state == 2:
        # Screen flash inverted block!
        oled.fill_rect(10, 18, 108, 32, 1)
        oled.text("PRESS NOW!!", 24, 30, 0)
    elif reflex_state == 3:
        if reaction_ms == -1:
            oled.text("TOO EARLY! XD", 24, 22, 1)
            oled.text("Don't anticipate!", 10, 38, 1)
            oled.text("[ACT] to retry", 20, 52, 1)
        else:
            oled.text(f"Time: {reaction_ms} ms", 24, 18, 1)
            if reaction_ms < 220:
                oled.text("Lightning fast!", 16, 32, 1)
            elif reaction_ms < 320:
                oled.text("Solid reflexes!", 16, 32, 1)
            else:
                oled.text("A bit sleepy?", 20, 32, 1)
            oled.text(f"Best: {best_reflex_ms}ms", 32, 48, 1)

def draw_timer():
    mins = timer_seconds // 60
    secs = timer_seconds % 60
    time_str = f"{mins:02d}:{secs:02d}"
    
    oled.text(time_str, 44, 20, 1)
    state_str = "RUNNING..." if timer_running else "[PAUSED]"
    oled.text(state_str, 34, 36, 1)
    oled.text("ACT:Start  L:-  R:+", 2, 52, 1)

def render(now):
    draw_header()
    if mode == 0:
        draw_pet(now)
    elif mode == 1:
        draw_reflex()
    elif mode == 2:
        draw_timer()
    oled.show()

# Initial power-on chirp
sound_happy()
last_frame_time = time.monotonic()

while True:
    now = time.monotonic()
    
    # 1. Update Timer logic
    if timer_running and (now - last_timer_tick >= 1.0):
        last_timer_tick = now
        timer_seconds -= 1
        if timer_seconds <= 0:
            timer_running = False
            timer_seconds = 25 * 60
            sound_alarm()
            
    # 2. Update Pet happiness decay (every 45s of inattention)
    if now - last_decay_time > 45.0:
        last_decay_time = now
        pet_happiness = max(10, pet_happiness - 2)
        
    # 3. Update Reflex countdown trigger
    if reflex_state == 1 and (now >= reflex_wait_until):
        reflex_state = 2
        reflex_trigger_time = now
        sound_tone(988, 0.04)
        
    # 4. Handle Button Inputs (active-low with debounce)
    if not btn_left.value:
        if mode == 2 and not timer_running:
            # In timer pause mode, adjust minutes down
            timer_seconds = max(60, timer_seconds - 60)
            sound_boop()
        else:
            mode = (mode - 1) % len(modes)
            sound_boop()
        render(now)
        time.sleep(0.2)
        
    if not btn_right.value:
        if mode == 2 and not timer_running:
            # In timer pause mode, adjust minutes up
            timer_seconds = min(60 * 60, timer_seconds + 60)
            sound_boop()
        else:
            mode = (mode + 1) % len(modes)
            sound_boop()
        render(now)
        time.sleep(0.2)
        
    if not btn_action.value:
        if mode == 0:
            # Pet mode: feed and increase happiness
            pet_happiness = min(100, pet_happiness + 15)
            pet_eating = True
            pet_eat_until = now + 1.2
            sound_happy()
        elif mode == 1:
            # Reflex mode logic
            if reflex_state == 0 or reflex_state == 3:
                # Start new round
                reflex_state = 1
                reflex_wait_until = now + random.uniform(1.5, 3.5)
                sound_boop()
            elif reflex_state == 1:
                # Pressed too early!
                reflex_state = 3
                reaction_ms = -1
                sound_buzz()
            elif reflex_state == 2:
                # Clicked on time! Calculate elapsed ms
                reaction_ms = int((now - reflex_trigger_time) * 1000)
                if reaction_ms < best_reflex_ms:
                    best_reflex_ms = reaction_ms
                sound_happy()
                reflex_state = 3
        elif mode == 2:
            # Timer mode: toggle start/pause
            timer_running = not timer_running
            last_timer_tick = now
            sound_boop()
            
        render(now)
        time.sleep(0.2)
        
    # Re-render at ~15 FPS or when animations tick
    if now - last_frame_time > 0.06:
        last_frame_time = now
        render(now)
        
    time.sleep(0.01)
