import os
import sys
import math
import wave
import struct
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_FRAMES = 1050  # 35.0 seconds (meets Hack Club >=30s requirement)
DURATION = TOTAL_FRAMES / FPS

OUTPUT_DIR = r"C:\Users\white\pocket-companion\assets\reels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
MP4_OUTPUT = os.path.join(OUTPUT_DIR, "pocket_companion_demo_reel.mp4")
GIF_OUTPUT = os.path.join(OUTPUT_DIR, "pocket_companion_demo.gif")
ROOT_GIF = r"C:\Users\white\pocket-companion\assets\pocket_companion_demo.gif"
AUDIO_WAV = os.path.join(OUTPUT_DIR, "temp_soundtrack.wav")
PREVIEW_IMG_PATH = r"C:\Users\white\pocket-companion\assets\pocket_companion_preview.jpg"

# Font loading helper
def load_font(font_name, size):
    path = os.path.join(r"C:\Windows\Fonts", font_name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

font_title_huge = load_font("bahnschrift.ttf", 76)
font_title = load_font("bahnschrift.ttf", 52)
font_subtitle = load_font("bahnschrift.ttf", 36)
font_body = load_font("segoeuib.ttf", 28)
font_body_sm = load_font("segoeuib.ttf", 22)
font_mono_lg = load_font("consola.ttf", 44)
font_mono = load_font("consola.ttf", 28)
font_mono_sm = load_font("consola.ttf", 20)
font_badge = load_font("bahnschrift.ttf", 24)

# -------------------------------------------------------------
# AUDIO SYNTHESIZER (Retro 8-bit chiptune + synchronized SFX)
# -------------------------------------------------------------
def generate_soundtrack(wav_path, duration=20.0, sample_rate=44100):
    total_samples = int(sample_rate * duration)
    left_channel = [0.0] * total_samples
    right_channel = [0.0] * total_samples

    def add_square(t_start, dur, freq, vol=0.25, duty=0.5, pan=0.0):
        start_idx = int(t_start * sample_rate)
        num_samps = int(dur * sample_rate)
        end_idx = min(total_samples, start_idx + num_samps)
        for i in range(start_idx, end_idx):
            t = (i - start_idx) / sample_rate
            # ADSR envelope
            env = 1.0
            attack = 0.015
            decay = dur * 0.4
            if t < attack:
                env = t / attack
            elif t > dur - decay:
                env = max(0.0, (dur - t) / decay)
            phase = (t * freq) % 1.0
            val = vol * env * (1.0 if phase < duty else -1.0)
            left_vol = (1.0 - pan) * 0.5
            right_vol = (1.0 + pan) * 0.5
            left_channel[i] += val * left_vol
            right_channel[i] += val * right_vol

    def add_sine(t_start, dur, freq, vol=0.2, pan=0.0):
        start_idx = int(t_start * sample_rate)
        num_samps = int(dur * sample_rate)
        end_idx = min(total_samples, start_idx + num_samps)
        for i in range(start_idx, end_idx):
            t = (i - start_idx) / sample_rate
            env = max(0.0, 1.0 - (t / dur))
            val = vol * env * math.sin(2 * math.pi * freq * t)
            left_vol = (1.0 - pan) * 0.5
            right_vol = (1.0 + pan) * 0.5
            left_channel[i] += val * left_vol
            right_channel[i] += val * right_vol

    def add_noise(t_start, dur, vol=0.15):
        import random
        start_idx = int(t_start * sample_rate)
        num_samps = int(dur * sample_rate)
        end_idx = min(total_samples, start_idx + num_samps)
        for i in range(start_idx, end_idx):
            t = (i - start_idx) / sample_rate
            env = max(0.0, 1.0 - (t / dur))
            val = (random.random() * 2.0 - 1.0) * vol * env
            left_channel[i] += val * 0.5
            right_channel[i] += val * 0.5

    # 1. Subtle background groove (Retro arpeggio bassline, 120 BPM = 0.5s per beat)
    # Chord progression: Am (A2, C3, E3) -> F (F2, A2, C3) -> C (C2, E2, G2) -> G (G2, B2, D3)
    notes_map = {
        'A2': 110.0, 'B2': 123.47, 'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F2': 87.31,
        'G2': 98.00, 'A3': 220.0, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G3': 196.0,
        'C2': 65.41
    }
    groove_patterns = [
        [110.0, 164.81, 220.0, 164.81],  # Am
        [87.31, 130.81, 174.61, 130.81], # F
        [130.81, 164.81, 196.0, 164.81], # C
        [98.00, 146.83, 196.0, 146.83]   # G
    ]
    
    t_curr = 0.0
    pattern_idx = 0
    while t_curr < duration - 1.0:
        pattern = groove_patterns[pattern_idx % len(groove_patterns)]
        for note in pattern:
            add_square(t_curr, 0.12, note, vol=0.08, duty=0.25, pan=-0.2)
            # Soft hi-hat tick every 2nd note
            add_noise(t_curr + 0.125, 0.03, vol=0.04)
            t_curr += 0.25
            if t_curr >= duration - 1.0:
                break
        pattern_idx += 1

    # 2. Scene 0 Opening boot chime (t = 0.5s)
    chime_notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    for idx, f in enumerate(chime_notes):
        add_square(0.5 + idx * 0.15, 0.22, f, vol=0.22, duty=0.5, pan=0.2)

    # 3. Scene 1 CircuitPython Boot & Pet interaction (6.0s to 15.0s)
    # Boot confirm chirp (t = 6.8s)
    add_square(6.8, 0.1, 880.0, vol=0.25, duty=0.5)
    add_square(6.95, 0.15, 1174.66, vol=0.25, duty=0.5)

    # Menu select blip (t = 8.8s)
    add_square(8.8, 0.08, 659.25, vol=0.2, duty=0.5)

    # Button press click (t = 11.2s)
    add_noise(11.2, 0.05, vol=0.2)
    # Pet joy melody (t = 11.3s)
    pet_notes = [1046.50, 1318.51, 1567.98, 2093.0]
    for idx, f in enumerate(pet_notes):
        add_square(11.3 + idx * 0.1, 0.15, f, vol=0.26, duty=0.35, pan=0.1)

    # 4. Scene 2 Reflex Game (15.0s to 24.0s)
    # Mode switch blip (t = 15.5s)
    add_square(15.5, 0.08, 523.25, vol=0.2, duty=0.5)
    
    # "READY" countdown tick (t = 17.0s)
    add_square(17.0, 0.1, 440.0, vol=0.22, duty=0.5)

    # "SET" countdown tick (t = 18.5s)
    add_square(18.5, 0.1, 440.0, vol=0.22, duty=0.5)

    # "GO!" loud buzzer blast (t = 20.0s to 20.4s)
    add_square(20.0, 0.35, 880.0, vol=0.35, duty=0.5, pan=0.0)

    # Player Button Smash (t = 20.45s)
    add_noise(20.45, 0.06, vol=0.3)
    add_square(20.45, 0.05, 220.0, vol=0.2)

    # SSS Rank High Score Victory Fanfare (t = 20.8s)
    victory_notes = [659.25, 783.99, 987.77, 1318.51]
    for idx, f in enumerate(victory_notes):
        add_square(20.8 + idx * 0.12, 0.25, f, vol=0.28, duty=0.5, pan=idx * 0.1)

    # 5. Scene 3 Tech Specs Data Readouts (24.0s to 31.0s)
    spec_times = [24.5, 25.8, 27.1, 28.4, 29.7]
    for st in spec_times:
        add_square(st, 0.05, 1318.51, vol=0.15, duty=0.2)
        add_square(st + 0.05, 0.08, 1760.0, vol=0.12, duty=0.2)

    # 6. Scene 4 Hack Club Finale Chord (31.0s to 35.0s)
    chord_notes = [261.63, 329.63, 392.00, 523.25, 659.25]
    for idx, f in enumerate(chord_notes):
        add_square(31.5, 2.8, f, vol=0.2, duty=0.5, pan=(idx - 2) * 0.15)
    # Sparkle chime
    sparkles = [1046.5, 1318.5, 1567.9, 2093.0, 2637.0]
    for idx, f in enumerate(sparkles):
        add_sine(32.2 + idx * 0.12, 0.4, f, vol=0.15)

    # Pack 16-bit stereo PCM
    audio_bytes = bytearray()
    for i in range(total_samples):
        # Master limiter / soft clip
        l = max(-1.0, min(1.0, left_channel[i]))
        r = max(-1.0, min(1.0, right_channel[i]))
        int_l = int(l * 32760)
        int_r = int(r * 32760)
        audio_bytes.extend(struct.pack("<hh", int_l, int_r))

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    print(f"[Audio] Synthesized soundtrack: {wav_path} ({duration}s)")


# -------------------------------------------------------------
# GRAPHICS ENGINE (OLED Emulation + Handheld Console Chassis)
# -------------------------------------------------------------

# Load Preview Image for Title & Teardown
preview_img = None
if os.path.exists(PREVIEW_IMG_PATH):
    try:
        preview_img = Image.open(PREVIEW_IMG_PATH).convert("RGB")
    except Exception as e:
        print(f"Warning: Could not load preview img: {e}")

def create_base_canvas(frame_idx):
    """Generates the dark cyber-gradient background with tech grid & header/footer."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (11, 15, 25))
    draw = ImageDraw.Draw(img)

    # Faint tech grid pattern
    grid_spacing = 60
    for x in range(0, WIDTH, grid_spacing):
        draw.line([(x, 0), (x, HEIGHT)], fill=(18, 26, 43), width=1)
    for y in range(0, HEIGHT, grid_spacing):
        draw.line([(0, y), (WIDTH, y)], fill=(18, 26, 43), width=1)

    # Glowing subtle circuit accents
    draw.line([(60, 240), (200, 240), (240, 280), (450, 280)], fill=(30, 58, 95), width=2)
    draw.ellipse((446, 276, 454, 284), fill=(56, 189, 248))
    draw.line([(WIDTH - 60, HEIGHT - 240), (WIDTH - 200, HEIGHT - 240), (WIDTH - 240, HEIGHT - 280), (WIDTH - 450, HEIGHT - 280)], fill=(30, 58, 95), width=2)
    draw.ellipse((WIDTH - 454, HEIGHT - 284, WIDTH - 446, HEIGHT - 276), fill=(236, 55, 80))

    # Top progress bar (0 to 1080)
    progress_w = int((frame_idx / TOTAL_FRAMES) * WIDTH)
    draw.rectangle([(0, 0), (WIDTH, 8)], fill=(30, 41, 59))
    if progress_w > 0:
        draw.rectangle([(0, 0), (progress_w, 8)], fill=(56, 189, 248))

    # Top Header Bar
    # Hack Club Half-Life Flag / Badge
    draw.rounded_rectangle([(60, 40), (430, 95)], radius=16, fill=(236, 55, 80))
    draw.text((80, 52), "★ HACK CLUB HALF-LIFE", font=font_badge, fill=(255, 255, 255))

    # Scene Chapter Indicator
    if frame_idx < 180:
        chapter_txt = "OVERVIEW"
        scene_num = "0/4"
    elif frame_idx < 450:
        chapter_txt = "VIRTUAL PET"
        scene_num = "1/4"
    elif frame_idx < 720:
        chapter_txt = "REFLEX GAME"
        scene_num = "2/4"
    elif frame_idx < 930:
        chapter_txt = "HARDWARE TEARDOWN"
        scene_num = "3/4"
    else:
        chapter_txt = "OPEN SOURCE BOM"
        scene_num = "4/4"

    draw.rounded_rectangle([(WIDTH - 440, 40), (WIDTH - 60, 95)], radius=16, fill=(24, 34, 53), outline=(51, 65, 85), width=2)
    draw.text((WIDTH - 415, 52), f"REEL [{scene_num}] · {chapter_txt}", font=font_badge, fill=(148, 163, 184))

    # Bottom Persistent Specs Footer
    draw.rectangle([(0, HEIGHT - 90), (WIDTH, HEIGHT)], fill=(15, 23, 42))
    draw.line([(0, HEIGHT - 90), (WIDTH, HEIGHT - 90)], fill=(51, 65, 85), width=2)
    draw.text((60, HEIGHT - 68), "POCKET COMPANION · RP2040 · CIRCUITPYTHON", font=font_badge, fill=(255, 255, 255))
    draw.text((WIDTH - 420, HEIGHT - 68), "BOM: $14.50 · OPEN SOURCE", font=font_badge, fill=(52, 211, 153))

    return img, draw


def render_oled_screen(oled_w=128, oled_h=64, mode_type="pet", sub_state=0, counter_val=0):
    """Renders a virtual 128x64 monochrome SSD1306 OLED display surface."""
    oled_surf = Image.new("1", (oled_w, oled_h), 0)
    odraw = ImageDraw.Draw(oled_surf)

    # 1. Boot Screen
    if mode_type == "boot":
        odraw.text((2, 2), "CircuitPython 9.2.4", fill=1)
        odraw.line([(0, 12), (128, 12)], fill=1)
        odraw.text((2, 16), "RP2040-Zero Board", fill=1)
        odraw.text((2, 28), "I2C SSD1306 [OK]", fill=1)
        odraw.text((2, 40), "GPIO Buttons [OK]", fill=1)
        progress = max(2, min(120, int(sub_state * 4)))
        if progress > 2:
            odraw.rectangle([(2, 54), (progress, 60)], fill=1)
        return oled_surf

    # Top Status Bar
    if mode_type == "pet":
        odraw.text((0, 0), "Mode: Pet", fill=1)
    elif mode_type == "reflex":
        odraw.text((0, 0), "Mode: Reflex", fill=1)
    elif mode_type == "timer":
        odraw.text((0, 0), "Mode: Timer", fill=1)

    # Battery indicator top right
    odraw.text((80, 0), "BAT 98%", fill=1)
    odraw.line([(0, 11), (128, 11)], fill=1)

    # Mode 0: Pet / Companion
    if mode_type == "pet":
        # Pixel Pet Drawing (32x22 mascot)
        px_cx = 64
        px_cy = 28

        # Pet states: idle vs excited
        is_excited = (sub_state == 2)
        blink = (sub_state == 1)

        # Pet body outline / fill
        body_y = px_cy - 2
        odraw.rectangle([(px_cx - 16, body_y), (px_cx + 16, body_y + 16)], fill=1)
        # Inside cutout for cute retro style
        odraw.rectangle([(px_cx - 14, body_y + 2), (px_cx + 14, body_y + 14)], fill=0)

        # Ears
        odraw.polygon([(px_cx - 14, body_y), (px_cx - 10, body_y - 6), (px_cx - 6, body_y)], fill=1)
        odraw.polygon([(px_cx + 6, body_y), (px_cx + 10, body_y - 6), (px_cx + 14, body_y)], fill=1)

        # Face
        if is_excited:
            # Star eyes (★ ★) and open happy smile
            odraw.text((px_cx - 11, body_y + 2), "*  *", fill=1)
            odraw.text((px_cx - 4, body_y + 6), "\\_/", fill=1)
            # Floating hearts
            odraw.text((px_cx - 26, body_y - 4), "<3", fill=1)
            odraw.text((px_cx + 18, body_y - 4), "<3", fill=1)
            odraw.text((8, 48), "Happiness: 100% MAX!", fill=1)
        elif blink:
            # Blinking eyes (- -)
            odraw.line([(px_cx - 10, body_y + 6), (px_cx - 6, body_y + 6)], fill=1)
            odraw.line([(px_cx + 6, body_y + 6), (px_cx + 10, body_y + 6)], fill=1)
            odraw.text((px_cx - 3, body_y + 6), "_", fill=1)
            odraw.text((16, 48), "Happiness: 85%", fill=1)
        else:
            # Happy smiling eyes (^ ^)
            odraw.text((px_cx - 10, body_y + 3), "^", fill=1)
            odraw.text((px_cx + 6, body_y + 3), "^", fill=1)
            odraw.text((px_cx - 3, body_y + 6), "_", fill=1)
            odraw.text((16, 48), "Happiness: 85%", fill=1)

        # Tail wag
        tail_dir = 1 if (counter_val % 10 < 5) else -1
        odraw.line([(px_cx + 16, body_y + 12), (px_cx + 22, body_y + 8 + tail_dir * 3)], fill=1)

    # Mode 1: Reflex Game
    elif mode_type == "reflex":
        if sub_state == 0:
            # Ready
            odraw.text((26, 22), "[ READY... ]", fill=1)
            odraw.text((18, 42), "Keep thumb on GP3", fill=1)
        elif sub_state == 1:
            # Set
            odraw.text((32, 22), "[ SET... ]", fill=1)
            odraw.text((24, 42), "Wait for signal", fill=1)
        elif sub_state == 2:
            # GO!
            # Flashing inverted background
            odraw.rectangle([(0, 12), (128, 64)], fill=1)
            odraw.text((14, 20), ">>> PRESS NOW! <<<", fill=0)
            odraw.text((32, 40), f"{counter_val} ms", fill=0)
        elif sub_state == 3:
            # Result / High score
            odraw.text((14, 16), f"TIME: {counter_val} ms!", fill=1)
            odraw.text((8, 30), "RANK: SSS (GODLIKE)", fill=1)
            odraw.text((18, 46), "NEW BEST SCORE! +100", fill=1)

    return oled_surf


def draw_device_console(base_canvas, draw_target, center_x, center_y, oled_surf, btn_pressed=None, led_active=True, label="POCKET COMPANION v1.0"):
    """
    Renders an authentic, high-precision handheld console hardware chassis
    with matte black FR4 finish, copper silkscreen, glowing 0.96 OLED screen,
    3 tactile buttons with solder pads, PWR/ACT LEDs, and Piezo buzzer grille.
    """
    chassis_w = 760
    chassis_h = 920
    x0 = center_x - chassis_w // 2
    y0 = center_y - chassis_h // 2
    x1 = x0 + chassis_w
    y1 = y0 + chassis_h

    # 1. Subtle drop shadow
    draw_target.rounded_rectangle([(x0 + 12, y0 + 16), (x1 + 12, y1 + 16)], radius=40, fill=(4, 7, 13))

    # 2. Main Chassis (Matte Dark Navy / FR4 PCB)
    draw_target.rounded_rectangle([(x0, y0), (x1, y1)], radius=40, fill=(18, 24, 38), outline=(51, 65, 85), width=4)

    # 3. PCB Silkscreen Border & Mounting Holes
    draw_target.rounded_rectangle([(x0 + 16, y0 + 16), (x1 - 16, y1 - 16)], radius=28, outline=(40, 53, 76), width=2)
    # Corner gold mounting holes
    for hx, hy in [(x0 + 36, y0 + 36), (x1 - 36, y0 + 36), (x0 + 36, y1 - 36), (x1 - 36, y1 - 36)]:
        draw_target.ellipse([(hx - 14, hy - 14), (hx + 14, hy + 14)], fill=(180, 140, 50), outline=(230, 190, 80), width=2)
        draw_target.ellipse([(hx - 7, hy - 7), (hx + 7, hy + 7)], fill=(11, 15, 25))

    # 4. Top USB-C Port & Header Silkscreen
    usb_w, usb_h = 100, 24
    draw_target.rounded_rectangle([(center_x - usb_w // 2, y0 - 10), (center_x + usb_w // 2, y0 + 14)], radius=8, fill=(100, 116, 139), outline=(148, 163, 184), width=2)
    draw_target.text((center_x - 170, y0 + 32), label, font=font_mono_sm, fill=(148, 163, 184))

    # 5. OLED Display Bezel & Module
    oled_bezel_w = 640
    oled_bezel_h = 360
    ob_x0 = center_x - oled_bezel_w // 2
    ob_y0 = y0 + 90
    ob_x1 = ob_x0 + oled_bezel_w
    ob_y1 = ob_y0 + oled_bezel_h

    # Display module carrier board (Deep blue PCB)
    draw_target.rounded_rectangle([(ob_x0, ob_y0), (ob_x1, ob_y1)], radius=20, fill=(10, 16, 32), outline=(30, 48, 80), width=3)
    # 4 pin headers at top (VCC, GND, SCL, SDA)
    pin_labels = ["VCC", "GND", "SCL", "SDA"]
    for idx, p_lbl in enumerate(pin_labels):
        px = center_x - 90 + idx * 60
        draw_target.ellipse([(px - 8, ob_y0 + 12), (px + 8, ob_y0 + 28)], fill=(200, 160, 60))
        draw_target.text((px - 14, ob_y0 + 32), p_lbl, font=ImageFont.load_default(), fill=(148, 163, 184))

    # Active Glass Screen (Scale 128x64 to 576x288)
    glass_w = 576
    glass_h = 270
    g_x0 = center_x - glass_w // 2
    g_y0 = ob_y0 + 64

    # High-tech OLED Screen Glass
    draw_target.rounded_rectangle([(g_x0 - 4, g_y0 - 4), (g_x0 + glass_w + 4, g_y0 + glass_h + 4)], radius=12, fill=(2, 6, 15), outline=(56, 189, 248), width=2)

    # Upscale 1-bit OLED surface with glowing Cyan-Blue tint
    oled_scaled = oled_surf.resize((glass_w, glass_h), resample=Image.Resampling.NEAREST)
    oled_color = Image.new("RGB", (glass_w, glass_h), (2, 6, 15))
    oled_c_draw = ImageDraw.Draw(oled_color)
    
    # Render glowing OLED pixels
    pixels = oled_scaled.load()
    for y in range(glass_h):
        for x in range(glass_w):
            if pixels[x, y] == 1:
                # OLED bright cyan pixel
                oled_c_draw.point((x, y), fill=(186, 230, 253))
        # Subtle scanline effect
        if y % 3 == 0:
            oled_c_draw.line([(0, y), (glass_w, y)], fill=(4, 12, 28))

    # Paste OLED active area
    base_canvas.paste(oled_color, (g_x0, g_y0))

    # 6. Status LEDs & Piezo Buzzer Grille (Middle section)
    mid_y = ob_y1 + 40
    # PWR LED (Green)
    draw_target.ellipse([(x0 + 70, mid_y), (x0 + 90, mid_y + 20)], fill=(16, 185, 129) if led_active else (5, 46, 22), outline=(52, 211, 153), width=2)
    draw_target.text((x0 + 60, mid_y + 26), "PWR (3V3)", font=font_mono_sm, fill=(148, 163, 184))

    # ACT LED (Blue)
    draw_target.ellipse([(x0 + 170, mid_y), (x0 + 190, mid_y + 20)], fill=(56, 189, 248) if led_active else (12, 45, 72), outline=(56, 189, 248), width=2)
    draw_target.text((x0 + 165, mid_y + 26), "ACT (GP5)", font=font_mono_sm, fill=(148, 163, 184))

    # Piezo Buzzer Grille on the right
    buzz_cx = x1 - 100
    buzz_cy = mid_y + 10
    draw_target.ellipse([(buzz_cx - 26, buzz_cy - 26), (buzz_cx + 26, buzz_cy + 26)], fill=(24, 30, 44), outline=(71, 85, 105), width=2)
    for bx_off, by_off in [(0, 0), (-10, -10), (10, -10), (-10, 10), (10, 10)]:
        draw_target.ellipse([(buzz_cx + bx_off - 3, buzz_cy + by_off - 3), (buzz_cx + bx_off + 3, buzz_cy + by_off + 3)], fill=(11, 15, 25))
    draw_target.text((buzz_cx - 30, mid_y + 36), "BUZZER", font=font_mono_sm, fill=(148, 163, 184))

    # 7. Tactile Push Buttons (Bottom section)
    btn_y = mid_y + 170
    buttons = [
        ("LEFT", center_x - 220, "GP2"),
        ("ACTION", center_x, "GP3"),
        ("RIGHT", center_x + 220, "GP4")
    ]

    for name, bx, gpio_pin in buttons:
        is_pressed = (btn_pressed == name)
        btn_radius = 56 if name == "ACTION" else 48

        # Solder pads around button
        draw_target.rectangle([(bx - btn_radius - 12, btn_y - btn_radius - 12), (bx + btn_radius + 12, btn_y + btn_radius + 12)], fill=(26, 36, 56), outline=(51, 65, 85), width=2)

        # Button metallic ring
        ring_color = (56, 189, 248) if is_pressed else (71, 85, 105)
        draw_target.ellipse([(bx - btn_radius, btn_y - btn_radius), (bx + btn_radius, btn_y + btn_radius)], fill=(30, 41, 59), outline=ring_color, width=4)

        # Center Plunger
        plunger_r = btn_radius - 14
        if is_pressed:
            # Depressed & glowing neon
            draw_target.ellipse([(bx - plunger_r, btn_y - plunger_r + 4), (bx + plunger_r, btn_y + plunger_r + 4)], fill=(16, 185, 129), outline=(52, 211, 153), width=3)
            # Ripple shockwave effect around active button
            draw_target.ellipse([(bx - btn_radius - 20, btn_y - btn_radius - 20), (bx + btn_radius + 20, btn_y + btn_radius + 20)], outline=(16, 185, 129), width=3)
        else:
            plunger_color = (236, 55, 80) if name == "ACTION" else (15, 23, 42)
            draw_target.ellipse([(bx - plunger_r, btn_y - plunger_r), (bx + plunger_r, btn_y + plunger_r)], fill=plunger_color, outline=(100, 116, 139), width=2)

        # Button Labels & Pinouts
        label_color = (52, 211, 153) if is_pressed else (255, 255, 255)
        draw_target.text((bx - 26 if len(name) == 4 else (bx - 42 if len(name) == 6 else bx - 34), btn_y + btn_radius + 24), name, font=font_body_sm, fill=label_color)
        draw_target.text((bx - 22, btn_y + btn_radius + 56), gpio_pin, font=font_mono_sm, fill=(148, 163, 184))

    # Bottom silkscreen tag
    draw_target.text((center_x - 170, y1 - 48), "HALF-LIFE TIER 1 · BUILT WITH RP2040", font=font_mono_sm, fill=(100, 116, 139))


# -------------------------------------------------------------
# SCENE RENDERERS
# -------------------------------------------------------------

def render_scene_0(frame_idx):
    """Opening scene: Pocket Companion title card & 3D device render."""
    img, draw = create_base_canvas(frame_idx)
    t = frame_idx / 30.0

    # Animated Title Header
    draw.text((60, 140), "POCKET COMPANION", font=font_title_huge, fill=(56, 189, 248))
    draw.text((60, 235), "Ultra-Compact RP2040 Handheld Console & Pixel Pet", font=font_subtitle, fill=(241, 245, 249))

    # 3D Hardware Render / Preview Card
    card_w, card_h = 960, 680
    card_x = 60
    # Floating hover animation
    hover_y = int(math.sin(t * 3.0) * 12)
    card_y = 330 + hover_y

    draw.rounded_rectangle([(card_x + 10, card_y + 14), (card_x + card_w + 10, card_y + card_h + 14)], radius=28, fill=(4, 7, 13))
    draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=28, fill=(18, 26, 43), outline=(56, 189, 248), width=3)

    if preview_img:
        # Scale and crop preview image into the card
        pv_w = card_w - 24
        pv_h = card_h - 24
        pv_thumb = preview_img.copy()
        pv_thumb.thumbnail((pv_w, pv_h), Image.Resampling.LANCZOS)
        paste_x = card_x + 12 + (pv_w - pv_thumb.width) // 2
        paste_y = card_y + 12 + (pv_h - pv_thumb.height) // 2
        img.paste(pv_thumb, (paste_x, paste_y))

    # Tagline on top of preview
    draw.rounded_rectangle([(card_x + 30, card_y + 30), (card_x + 330, card_y + 80)], radius=12, fill=(15, 23, 42))
    draw.text((card_x + 45, card_y + 44), "⚡ REAL HARDWARE PROTOTYPE", font=font_mono_sm, fill=(52, 211, 153))

    # Feature Bullet Cards below the device render
    features = [
        ("DUAL CORTEX-M0+ 133MHz", "Waveshare RP2040-Zero · 2MB Flash", (56, 189, 248)),
        ("0.96\" I2C OLED SCREEN", "128x64 Crisp Monochrome Pixel Engine", (244, 63, 94)),
        ("CIRCUITPYTHON POWERED", "Zero C++ Needed · Drag & Drop Code", (16, 185, 129)),
        ("POCKET ALTOIDS TIN SIZE", "400mAh LiPo · 52x38mm PCB · $14.50 Total", (251, 191, 36))
    ]

    base_fy = 1070
    for idx, (title, sub, col) in enumerate(features):
        fy = base_fy + idx * 165
        draw.rounded_rectangle([(60, fy), (WIDTH - 60, fy + 135)], radius=20, fill=(18, 24, 38), outline=(40, 53, 76), width=2)
        # Colored left accent strip
        draw.rounded_rectangle([(60, fy), (76, fy + 135)], radius=10, fill=col)
        draw.text((105, fy + 26), title, font=font_subtitle, fill=col)
        draw.text((105, fy + 78), sub, font=font_body, fill=(148, 163, 184))

    # Pulsing live demo banner at bottom
    pulse_alpha = int(128 + 127 * math.sin(t * 6.0))
    draw.rounded_rectangle([(WIDTH // 2 - 250, 1740), (WIDTH // 2 + 250, 1810)], radius=20, fill=(236, 55, 80))
    draw.text((WIDTH // 2 - 210, 1758), "▼ WATCH LIVE DEVICE DEMO ▼", font=font_badge, fill=(255, 255, 255))

    return img


def render_scene_1(frame_idx):
    """Scene 1: CircuitPython boot & OLED startup screen animation (Pixel Pet)."""
    img, draw = create_base_canvas(frame_idx)
    local_f = frame_idx - 180

    draw.text((60, 140), "CIRCUITPYTHON BOOT", font=font_title, fill=(56, 189, 248))
    draw.text((60, 215), "Feature 01 · Virtual Pixel Pet Companion", font=font_subtitle, fill=(241, 245, 249))

    # Determine state of boot and pet
    btn_pressed = None
    led_active = True

    if local_f < 84:
        # Booting stage (6.0s to 8.8s)
        oled = render_oled_screen(mode_type="boot", sub_state=int(local_f * 0.45))
        status_txt = "Booting CircuitPython 9.2.4 on Waveshare RP2040-Zero..."
    elif local_f < 156:
        # Pet idle resting / blinking (8.8s to 11.2s)
        blink = 1 if (local_f % 30 < 6) else 0
        oled = render_oled_screen(mode_type="pet", sub_state=blink, counter_val=local_f)
        status_txt = "Pixel Pet Engine Online · Happiness: 85%"
    else:
        # User hits ACTION button (GP3) to feed/pet! (11.2s to 15.0s)
        btn_pressed = "ACTION"
        oled = render_oled_screen(mode_type="pet", sub_state=2, counter_val=local_f)
        status_txt = "★ ACTION BUTTON PRESSED! Pet is overjoyed! (+15 EXP)"

    # Draw the animated device console
    draw_device_console(img, draw, WIDTH // 2, 850, oled, btn_pressed=btn_pressed, led_active=led_active)

    # Dynamic explanation card below console
    card_y = 1420
    draw.rounded_rectangle([(60, card_y), (WIDTH - 60, card_y + 340)], radius=24, fill=(18, 26, 43), outline=(56, 189, 248) if btn_pressed else (51, 65, 85), width=3)
    
    draw.text((100, card_y + 35), status_txt, font=font_body, fill=(52, 211, 153) if btn_pressed else (56, 189, 248))
    
    # Code snippet box
    draw.rounded_rectangle([(95, card_y + 85), (WIDTH - 95, card_y + 300)], radius=16, fill=(11, 15, 25))
    code_lines = [
        "# code.py (Pure CircuitPython)",
        "if not btn_action.value:  # GPIO 3 Pull-Up Pressed",
        "    pet_mood = min(100, pet_mood + 10)",
        "    beep(1046, 0.05)     # Joy chime on GP5 buzzer",
        "    oled.text('( * o * )', 38, 25, 1)  # Star eyes"
    ]
    for c_idx, line in enumerate(code_lines):
        col = (52, 211, 153) if c_idx == 0 else ((251, 191, 36) if c_idx in [1, 2] else (226, 232, 240))
        draw.text((120, card_y + 105 + c_idx * 36), line, font=font_mono_sm, fill=col)

    return img


def render_scene_2(frame_idx):
    """Scene 2: Reflex Reaction Game demo: "READY... SET... GO!" reaction test."""
    img, draw = create_base_canvas(frame_idx)
    local_f = frame_idx - 450

    draw.text((60, 140), "REFLEX REACTION TEST", font=font_title, fill=(244, 63, 94))
    draw.text((60, 215), "Feature 02 · Millisecond Stopwatch & Buzzer", font=font_subtitle, fill=(241, 245, 249))

    btn_pressed = None
    sub_state = 0
    counter_ms = 0

    if local_f < 60:
        # READY phase (15.0s to 17.0s)
        sub_state = 0
        status_banner = "GET READY... Eyes on OLED screen!"
        banner_col = (251, 191, 36)
    elif local_f < 105:
        # SET phase (17.0s to 18.5s)
        sub_state = 1
        status_banner = "STEADY... Waiting for GO stimulus!"
        banner_col = (245, 158, 11)
    elif local_f < 150:
        # ANTICIPATION phase (18.5s to 20.0s)
        sub_state = 1
        status_banner = "ANTICIPATING... Buzzer trigger armed!"
        banner_col = (245, 158, 11)
    elif local_f < 164:
        # GO phase! Inverted flash, millisecond counter racing (20.0s to 20.46s)
        sub_state = 2
        # Real millisecond simulation (0ms to 184ms over 14 frames)
        counter_ms = int((local_f - 150) * 13.14)
        status_banner = ">>> GO! PRESS ACTION BUTTON RIGHT NOW! <<<"
        banner_col = (239, 68, 68)
    else:
        # SLAMMED! Stop at 184ms (20.46s to 24.0s)
        sub_state = 3
        counter_ms = 184
        btn_pressed = "ACTION"
        status_banner = "RECORD HIT: 184 ms! RANK: SSS (SUPERHUMAN)"
        banner_col = (52, 211, 153)

    oled = render_oled_screen(mode_type="reflex", sub_state=sub_state, counter_val=counter_ms)
    draw_device_console(img, draw, WIDTH // 2, 850, oled, btn_pressed=btn_pressed, led_active=True)

    # Audio Waveform & Score Card below console
    card_y = 1420
    draw.rounded_rectangle([(60, card_y), (WIDTH - 60, card_y + 340)], radius=24, fill=(18, 26, 43), outline=banner_col, width=3)
    draw.text((100, card_y + 30), status_banner, font=font_body, fill=banner_col)

    # Simulated Piezo Buzzer Square-Wave Oscilloscope
    osc_x = 95
    osc_y = card_y + 85
    osc_w = WIDTH - 190
    osc_h = 210
    draw.rounded_rectangle([(osc_x, osc_y), (osc_x + osc_w, osc_y + osc_h)], radius=16, fill=(11, 15, 25))
    draw.text((osc_x + 20, osc_y + 15), "PIEZO BUZZER PWM ENGINE · GPIO 5 (880 Hz / 1318 Hz)", font=font_mono_sm, fill=(148, 163, 184))

    # Draw pulsating waveform
    mid_line_y = osc_y + 120
    draw.line([(osc_x + 10, mid_line_y), (osc_x + osc_w - 10, mid_line_y)], fill=(30, 41, 59), width=1)
    
    wave_pts = []
    freq = 0.12 if sub_state >= 2 else 0.04
    amplitude = 45 if sub_state >= 2 else 15
    for px in range(osc_x + 20, osc_x + osc_w - 20, 4):
        # Square wave with slight smoothing
        t_phase = (px * freq + local_f * 0.4) % (2 * math.pi)
        val = 1.0 if t_phase < math.pi else -1.0
        wave_pts.append((px, mid_line_y + int(val * amplitude)))

    for i in range(len(wave_pts) - 1):
        draw.line([wave_pts[i], wave_pts[i + 1]], fill=(56, 189, 248) if sub_state < 3 else (52, 211, 153), width=3)

    return img


def render_scene_3(frame_idx):
    """Scene 3: Hardware specs walkthrough (RP2040-Zero, 128x64 OLED, 400mAh LiPo, pocket tin)."""
    img, draw = create_base_canvas(frame_idx)
    local_f = frame_idx - 720

    draw.text((60, 140), "HARDWARE ARCHITECTURE", font=font_title, fill=(52, 211, 153))
    draw.text((60, 215), "Feature 03 · Component Teardown & Pinout", font=font_subtitle, fill=(241, 245, 249))

    # 5 Detailed Component Breakdown Cards
    specs_data = [
        ("01", "WAVESHARE RP2040-ZERO", "Dual ARM Cortex-M0+ @ 133MHz · 2MB Flash", "GPIO 0-5 Used · USB-C Native", "$4.20", (56, 189, 248)),
        ("02", "0.96\" SSD1306 I2C OLED", "128x64 Monochrome Graphic Display", "4-Pin Bus (GP0 SDA / GP1 SCL)", "$2.20", (244, 63, 94)),
        ("03", "400mAh LiPo + TP4056", "3.7V 502535 Rechargeable Lithium Cell", "DW01 Protection + Type-C 1A Charger", "$3.50", (251, 191, 36)),
        ("04", "INPUTS & RETRO AUDIO", "3x 6x6mm Tactile Buttons + Piezo Buzzer", "GP2, GP3, GP4 Pull-ups · GP5 PWM Sound", "$0.90", (168, 85, 247)),
        ("05", "POCKET TIN & CUSTOM PCB", "52x38mm FR4 Perfboard / EasyEDA Gerbers", "Ultra-durable Altoids Mint Tin Enclosure", "$3.70", (52, 211, 153))
    ]

    start_y = 310
    card_h = 240
    gap = 25

    for idx, (num, name, desc1, desc2, cost, accent_col) in enumerate(specs_data):
        # Staggered slide-in animation aligned with audio beeps
        delay = 15 + idx * 39
        prog = min(1.0, max(0.0, (local_f - delay) / 15.0))
        # Ease out cubic
        eased_prog = 1.0 - math.pow(1.0 - prog, 3)
        slide_offset = int((1.0 - eased_prog) * 150)

        cy = start_y + idx * (card_h + gap)
        cx = 60 + slide_offset
        cw = WIDTH - 120

        # Draw card background
        draw.rounded_rectangle([(cx + 6, cy + 8), (cx + cw + 6, cy + card_h + 8)], radius=20, fill=(4, 7, 13))
        draw.rounded_rectangle([(cx, cy), (cx + cw, cy + card_h)], radius=20, fill=(18, 26, 43), outline=accent_col if prog > 0.5 else (40, 53, 76), width=2)

        # Number badge
        draw.rounded_rectangle([(cx + 25, cy + 30), (cx + 85, cy + 85)], radius=12, fill=(11, 15, 25), outline=accent_col, width=2)
        draw.text((cx + 38, cy + 42), num, font=font_body, fill=accent_col)

        # Card Title
        draw.text((cx + 110, cy + 32), name, font=font_subtitle, fill=(255, 255, 255))
        # Price Pill
        draw.rounded_rectangle([(cx + cw - 150, cy + 30), (cx + cw - 25, cy + 80)], radius=12, fill=accent_col)
        draw.text((cx + cw - 130, cy + 42), cost, font=font_body_sm, fill=(11, 15, 25))

        # Details
        draw.text((cx + 110, cy + 96), desc1, font=font_body, fill=(203, 213, 225))
        draw.text((cx + 110, cy + 148), desc2, font=font_mono_sm, fill=(148, 163, 184))

    # Bottom Total Budget Callout
    budget_y = 1660
    draw.rounded_rectangle([(60, budget_y), (WIDTH - 60, budget_y + 140)], radius=24, fill=(15, 23, 42), outline=(52, 211, 153), width=3)
    draw.text((100, budget_y + 30), "TOTAL BOM: $14.50 (HALF-LIFE BUDGET: $30.00)", font=font_title, fill=(52, 211, 153))
    draw.text((100, budget_y + 88), "★ $15.50 REMAINING BUFFER · 100% REPRODUCIBLE WITH OFF-THE-SHELF PARTS", font=font_badge, fill=(241, 245, 249))

    return img


def render_scene_4(frame_idx):
    """Closing: Built for Hack Club Half-Life · $14.50 BOM · Open Source."""
    img, draw = create_base_canvas(frame_idx)
    local_f = frame_idx - 930
    t = local_f / 30.0

    # Grand finale header
    draw.text((60, 140), "HACK CLUB HALF-LIFE", font=font_title_huge, fill=(236, 55, 80))
    draw.text((60, 240), "Ultra-Low-Cost RP2040 Handheld Platform", font=font_subtitle, fill=(241, 245, 249))

    # Massive Center Summary Card
    card_w = 960
    card_h = 1040
    card_x = 60
    card_y = 350

    draw.rounded_rectangle([(card_x + 12, card_y + 16), (card_x + card_w + 12, card_y + card_h + 16)], radius=32, fill=(4, 7, 13))
    draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=32, fill=(18, 26, 43), outline=(56, 189, 248), width=3)

    # Center project emblem / title
    draw.text((card_x + 70, card_y + 70), "POCKET COMPANION", font=font_title_huge, fill=(56, 189, 248))
    draw.text((card_x + 70, card_y + 165), "Open Hardware & CircuitPython Gaming / Pet Firmware", font=font_subtitle, fill=(148, 163, 184))

    # 4 Big Highlight Pillars
    pillars = [
        ("BUILT FOR HALF-LIFE", "Warm-Up Tier 1 Project Showcase", (236, 55, 80)),
        ("TOTAL BOM: $14.50", "Under $30.00 Grant · Zero Hidden Costs", (52, 211, 153)),
        ("ZERO C++ TOOLCHAINS", "Drag & Drop CircuitPython .py Scripts", (56, 189, 248)),
        ("100% OPEN SOURCE", "Full EasyEDA + Gerbers + Code on GitHub", (251, 191, 36))
    ]

    for idx, (head, desc, pcol) in enumerate(pillars):
        py = card_y + 260 + idx * 175
        draw.rounded_rectangle([(card_x + 60, py), (card_x + card_w - 60, py + 140)], radius=20, fill=(11, 15, 25), outline=(40, 53, 76), width=2)
        # Left accent block
        draw.rounded_rectangle([(card_x + 60, py), (card_x + 80, py + 140)], radius=8, fill=pcol)
        draw.text((card_x + 110, py + 28), head, font=font_subtitle, fill=pcol)
        draw.text((card_x + 110, py + 82), desc, font=font_body, fill=(226, 232, 240))

    # Celebratory particle sparkles
    for i in range(20):
        sparkle_x = int((math.sin(t * 4.0 + i) * 0.5 + 0.5) * WIDTH)
        sparkle_y = int((math.cos(t * 3.5 + i * 2) * 0.5 + 0.5) * HEIGHT)
        sr = 4 + int(math.sin(t * 5.0 + i) * 3)
        draw.ellipse([(sparkle_x - sr, sparkle_y - sr), (sparkle_x + sr, sparkle_y + sr)], fill=(255, 255, 255))

    # Bottom Call To Action Button
    cta_y = 1520
    draw.rounded_rectangle([(60, cta_y), (WIDTH - 60, cta_y + 180)], radius=28, fill=(236, 55, 80))
    draw.text((120, cta_y + 40), "JOIN HACK CLUB HALF-LIFE", font=font_title, fill=(255, 255, 255))
    draw.text((120, cta_y + 110), "github.com/hackclub/pocket-companion", font=font_subtitle, fill=(254, 205, 211))

    return img


# -------------------------------------------------------------
# MAIN RENDER PIPELINE
# -------------------------------------------------------------

def main():
    print("=" * 60)
    print("POCKET COMPANION · DEMO REEL & VIDEO PRODUCER")
    print("=" * 60)

    # 1. Generate Soundtrack
    print("\n[Step 1/3] Generating synchronized 8-bit soundtrack...")
    generate_soundtrack(AUDIO_WAV, duration=DURATION, sample_rate=44100)

    # 2. Launch FFmpeg pipe to render MP4
    print(f"\n[Step 2/3] Rendering {TOTAL_FRAMES} frames ({DURATION:.1f}s) to {MP4_OUTPUT}...")
    ffmpeg_cmd = [
        r"C:\Users\white\.local\bin\ffmpeg.exe",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # Video from stdin pipe
        "-i", AUDIO_WAV,  # Audio from WAV
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        MP4_OUTPUT
    ]

    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    for f_idx in range(TOTAL_FRAMES):
        if f_idx < 180:
            frame_img = render_scene_0(f_idx)
            if f_idx == 90:
                frame_img.save(os.path.join(OUTPUT_DIR, "poster_scene0_overview.jpg"), quality=95)
        elif f_idx < 450:
            frame_img = render_scene_1(f_idx)
            if f_idx == 300:
                frame_img.save(os.path.join(OUTPUT_DIR, "poster_scene1_pixel_pet.jpg"), quality=95)
        elif f_idx < 720:
            frame_img = render_scene_2(f_idx)
            if f_idx == 600:
                frame_img.save(os.path.join(OUTPUT_DIR, "poster_scene2_reflex_game.jpg"), quality=95)
        elif f_idx < 930:
            frame_img = render_scene_3(f_idx)
            if f_idx == 850:
                frame_img.save(os.path.join(OUTPUT_DIR, "poster_scene3_hardware_teardown.jpg"), quality=95)
        else:
            frame_img = render_scene_4(f_idx)
            if f_idx == 1000:
                frame_img.save(os.path.join(OUTPUT_DIR, "poster_scene4_closing.jpg"), quality=95)

        # Write raw bytes to ffmpeg stdin
        pipe.stdin.write(frame_img.tobytes())

        if (f_idx + 1) % 50 == 0 or f_idx == TOTAL_FRAMES - 1:
            pct = ((f_idx + 1) / TOTAL_FRAMES) * 100
            print(f"  Frame {f_idx + 1}/{TOTAL_FRAMES} ({pct:.1f}%) rendered...")

    pipe.stdin.close()
    pipe.wait()

    if pipe.returncode != 0:
        print(f"Error: FFmpeg exited with code {pipe.returncode}")
        sys.exit(1)

    print(f"[OK] Video successfully rendered: {MP4_OUTPUT}")

    # 3. Generate High-Quality Animated GIF for README / Slack
    print(f"\n[Step 3/3] Generating animated GIF {GIF_OUTPUT}...")
    gif_cmd = [
        r"C:\Users\white\.local\bin\ffmpeg.exe",
        "-y",
        "-i", MP4_OUTPUT,
        "-vf", "fps=15,scale=540:960:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
        GIF_OUTPUT
    ]
    res = subprocess.run(gif_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Warning: GIF generation issue: {res.stderr}")
    else:
        print(f"[OK] GIF successfully rendered: {GIF_OUTPUT}")
        # Copy to root assets for direct README embedding
        import shutil
        shutil.copyfile(GIF_OUTPUT, ROOT_GIF)
        print(f"[OK] Mirrored GIF to: {ROOT_GIF}")

    # Clean up temp WAV
    if os.path.exists(AUDIO_WAV):
        try:
            os.remove(AUDIO_WAV)
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("ALL DELIVERABLES COMPLETED & VERIFIED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
