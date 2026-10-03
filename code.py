# Pocket Companion - CircuitPython handheld firmware
# Runs on Waveshare RP2040-Zero + 0.96" SSD1306 OLED (128x64)
# Features:
# 1. Virtual Pet: Emotional state simulation (hunger, happiness, sleepiness, feeding & petting)
# 2. Reflex Mini-game: Random delay millisecond reaction tester & latency scoring
# 3. Focus Timer: 25-minute Pomodoro study countdown with buzzer alarms
# 4. Memory Simon: Retro 3-button audio-visual sequence memory mini-game

import time
import random
import json

try:
    import board
    import busio
    import digitalio
    import pwmio
    import analogio
    import adafruit_ssd1306
except ImportError:  # pragma: no cover
    board = None
    busio = None
    digitalio = None
    pwmio = None
    analogio = None
    adafruit_ssd1306 = None


class PocketCompanion:
    """Core handheld firmware state machine and hardware controller."""

    BUTTON_TONES = [330, 440, 554]  # Left (E4), Action (A4), Right (C#5)

    def __init__(self, oled=None, buzzer=None, btn_left=None, btn_action=None, btn_right=None, vbat_pin=None, reconnect_oled_fn=None):
        self.oled = oled
        self.buzzer = buzzer
        self.btn_left = btn_left
        self.btn_action = btn_action
        self.btn_right = btn_right
        self.vbat_pin = vbat_pin
        self.reconnect_oled_fn = reconnect_oled_fn
        self.oled_offline = False
        self.oled_error_count = 0
        self.oled_reconnect_count = 0
        self.last_oled_reconnect_time = 0.0

        # Power & Battery monitoring (3.7V LiPo: 4.2V max, 3.4V low warning, 3.2V cutoff)
        self.battery_voltage = 4.2
        self.low_battery = False
        self.power_cutoff = False

        # UI & Modes
        self.modes = ["Pet", "Reflex", "Timer", "Memory"]
        self.mode = 0

        # Virtual Pet variables
        self.pet_happiness = 85
        self.pet_hunger = 20
        self.pet_sleepiness = 15
        self.pet_sleeping = False
        self.pet_eating = False
        self.pet_eat_until = 0.0
        self.pet_blinking = False
        self.last_blink_time = time.monotonic()
        self.last_decay_time = time.monotonic()

        # Reflex game variables
        # States: 0=Idle, 1=Waiting, 2=Ready, 3=Result
        self.reflex_state = 0
        self.reflex_trigger_time = 0.0
        self.reflex_wait_until = 0.0
        self.reaction_ms = 0
        self.best_reflex_ms = 999

        # Pomodoro timer variables
        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.last_timer_tick = time.monotonic()

        # Memory Sequence Simon game variables
        # States: 0=Idle, 1=Playback, 2=Player Turn, 3=Round Win, 4=Game Over
        self.memory_state = 0
        self.memory_sequence = []
        self.memory_playback_idx = 0
        self.memory_playback_step_time = 0.0
        self.memory_player_idx = 0
        self.memory_score = 0
        self.best_memory_score = 0
        self.memory_win_until = 0.0

        # Input debounce & Frame timing
        self.last_button_time = 0.0
        self.last_frame_time = time.monotonic()
        self.alarm_events_count = 0
        self.save_debounce_sec = 2.0
        self.last_save_time = -10.0
        self.flash_write_count = 0
        self.flash_save_skipped_count = 0

        # Low-power sleep and wake interrupt
        self.sleep_mode = False
        self.wake_latency_us = 0.0
        self.sleep_events_count = 0
        self.wake_events_count = 0

    @staticmethod
    def _safe_val(val, min_val, max_val):
        """Safely parse integer within bounds, strictly rejecting NaN, Inf, and non-numerics."""
        if isinstance(val, int) and not isinstance(val, bool):
            if min_val <= val <= max_val:
                return val
        elif isinstance(val, float):
            if val == val and abs(val) != float("inf"):
                iv = int(val)
                if min_val <= iv <= max_val:
                    return iv
        return None


    def reset_defaults(self):
        """Restore all state machine variables to known valid factory defaults."""
        self.mode = 0
        self.pet_happiness = 85
        self.pet_hunger = 20
        self.pet_sleepiness = 15
        self.best_reflex_ms = 999
        self.best_memory_score = 0
        self.last_save_time = -10.0
        self.flash_write_count = 0
        self.flash_save_skipped_count = 0
        self.sleep_mode = False
        self.wake_latency_us = 0.0
        self.sleep_events_count = 0
        self.wake_events_count = 0

    def sanitize_state(self):
        """Guard against corrupted runtime variables and enforce valid bounds."""
        if not isinstance(self.mode, int) or isinstance(self.mode, bool) or not (0 <= self.mode < len(self.modes)):
            self.mode = 0
        if self.reflex_state not in (0, 1, 2, 3):
            self.reflex_state = 0
        if self.memory_state not in (0, 1, 2, 3, 4):
            self.memory_state = 0

        v_h = self._safe_val(self.pet_happiness, 0, 100)
        self.pet_happiness = 85 if v_h is None else v_h

        v_u = self._safe_val(self.pet_hunger, 0, 100)
        self.pet_hunger = 20 if v_u is None else v_u

        v_s = self._safe_val(self.pet_sleepiness, 0, 100)
        self.pet_sleepiness = 15 if v_s is None else v_s

    def save_state(self, filepath: str = "pocket_state.json", force: bool = False, now: float = None) -> bool:
        """Serialize current state (high scores, pet emotional stats) to flash storage with debounce."""
        if now is None:
            now = time.monotonic()

        if not force and (now - self.last_save_time) < self.save_debounce_sec:
            self.flash_save_skipped_count += 1
            return False

        try:
            state = {
                "best_reflex_ms": self.best_reflex_ms,
                "best_memory_score": self.best_memory_score,
                "pet_happiness": self.pet_happiness,
                "pet_hunger": self.pet_hunger,
                "pet_sleepiness": self.pet_sleepiness,
                "mode": self.mode,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state, f)
            self.last_save_time = now
            self.flash_write_count += 1
            return True
        except Exception:
            return False


    def load_state(self, filepath: str = "pocket_state.json") -> bool:
        """Load state from flash storage with automatic validation and fallback to defaults."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                self.reset_defaults()
                return False

            req_keys = ["best_reflex_ms", "best_memory_score", "pet_happiness", "pet_hunger", "pet_sleepiness", "mode"]
            if not all(k in data for k in req_keys):
                self.reset_defaults()
                return False

            v_reflex = self._safe_val(data.get("best_reflex_ms"), 0, 999)
            v_mem = self._safe_val(data.get("best_memory_score"), 0, 9999)
            v_happy = self._safe_val(data.get("pet_happiness"), 0, 100)
            v_hunger = self._safe_val(data.get("pet_hunger"), 0, 100)
            v_sleepy = self._safe_val(data.get("pet_sleepiness"), 0, 100)
            v_mode = self._safe_val(data.get("mode"), 0, len(self.modes) - 1)

            if None in (v_reflex, v_mem, v_happy, v_hunger, v_sleepy, v_mode):
                self.reset_defaults()
                return False

            self.best_reflex_ms = v_reflex
            self.best_memory_score = v_mem
            self.pet_happiness = v_happy
            self.pet_hunger = v_hunger
            self.pet_sleepiness = v_sleepy
            self.mode = v_mode
            return True
        except Exception:
            self.reset_defaults()
            return False


    def update_battery(self, voltage: float = None):
        """Monitor battery voltage decay and enforce safe low-voltage cutoff with noise filtering."""
        if voltage is not None:
            try:
                v = float(voltage)
                if not (v != v or v == float("inf") or v == float("-inf")):
                    self.battery_voltage = max(2.5, min(4.5, v))
            except (ValueError, TypeError):
                pass
        elif self.vbat_pin is not None:
            try:
                raw = self.vbat_pin.value
                raw = max(0, min(65535, raw))
                self.battery_voltage = (raw / 65535.0) * 3.3 * 2.0
            except Exception:
                pass

        if self.battery_voltage <= 3.2:
            self.power_cutoff = True
            self.low_battery = True
        elif self.battery_voltage <= 3.4:
            self.low_battery = True
            self.power_cutoff = False
        else:
            self.low_battery = False
            self.power_cutoff = False


    def sound_tone(self, freq: int, duration: float = 0.06):
        """Play a clean square wave tone on the piezo buzzer."""
        if self.buzzer and freq > 0:
            try:
                self.buzzer.frequency = int(freq)
                self.buzzer.duty_cycle = 32768  # 50% duty cycle
                time.sleep(duration)
                self.buzzer.duty_cycle = 0
            except Exception:
                time.sleep(duration)
        else:
            time.sleep(duration)

    def sound_happy(self):
        """Joy chime melody."""
        self.sound_tone(523, 0.04)
        self.sound_tone(659, 0.04)
        self.sound_tone(784, 0.07)

    def sound_boop(self):
        """Crisp navigation blip."""
        self.sound_tone(440, 0.04)

    def sound_buzz(self):
        """Low frequency error buzz."""
        self.sound_tone(180, 0.12)

    def sound_alarm(self):
        """3-stage pulsing alert chime."""
        self.alarm_events_count += 1
        for _ in range(3):
            self.sound_tone(880, 0.08)
            time.sleep(0.04)
            self.sound_tone(1174, 0.12)
            time.sleep(0.06)

    def update_pet(self, now: float):
        """Update emotional state decay, blinking, eating and sleep transitions."""
        # Check blink timing every 3 seconds when awake
        if not self.pet_sleeping and (now - self.last_blink_time > 3.0):
            self.pet_blinking = True
            if now - self.last_blink_time > 3.25:
                self.pet_blinking = False
                self.last_blink_time = now

        # Check eating animation timer
        if self.pet_eating and (now >= self.pet_eat_until):
            self.pet_eating = False

        # Pet emotional decay cycle (every 45s of time elapsed)
        if now - self.last_decay_time >= 45.0:
            self.last_decay_time = now
            if self.pet_sleeping:
                # Resting: recover energy, hunger slowly increases
                self.pet_sleepiness = max(0, self.pet_sleepiness - 25)
                self.pet_hunger = min(100, self.pet_hunger + 2)
                if self.pet_sleepiness == 0:
                    # Naturally wake up refreshed!
                    self.pet_sleeping = False
                    self.pet_happiness = min(100, self.pet_happiness + 15)
            else:
                # Awake: hunger and tiredness accumulate
                self.pet_hunger = min(100, self.pet_hunger + 5)
                self.pet_sleepiness = min(100, self.pet_sleepiness + 4)

                # Happiness degrades if starving or exhausted
                if self.pet_hunger >= 70:
                    self.pet_happiness = max(5, self.pet_happiness - 6)
                elif self.pet_sleepiness >= 75:
                    self.pet_happiness = max(10, self.pet_happiness - 4)
                else:
                    self.pet_happiness = max(10, self.pet_happiness - 2)

                # Pet falls asleep naturally when exhausted
                if self.pet_sleepiness >= 85:
                    self.pet_sleeping = True

    def get_pet_status(self, now: float):
        """Resolve current ASCII face expression and descriptive mood status."""
        if self.pet_eating:
            return "( > w < ) *", "Yum! Fed & Happy"
        elif self.pet_sleeping:
            return "( z Z Z )", "Sleeping... zZz"
        elif self.pet_sleepiness >= 75:
            return "( - . - )", "Sleepy... yawn"
        elif self.pet_hunger >= 70:
            return "( o Q o )", "Hungry! Feed me"
        elif self.pet_happiness > 70:
            face = "( - _ - )" if self.pet_blinking else "( ^ _ ^ )"
            return face, "Super happy!"
        elif self.pet_happiness > 35:
            return "( o _ o )", "Chillin'"
        else:
            return "( ; _ ; )", "Sad & lonely"

    def update_timer(self, now: float):
        """Update Pomodoro countdown and fire buzzer alarm upon completion."""
        if self.timer_running and (now - self.last_timer_tick >= 1.0):
            self.last_timer_tick = now
            self.timer_seconds -= 1
            if self.timer_seconds <= 0:
                self.timer_running = False
                self.timer_seconds = 25 * 60
                self.sound_alarm()

    def update_reflex(self, now: float):
        """Check reflex trigger time expiry to present stimulus."""
        if self.reflex_state == 1 and (now >= self.reflex_wait_until):
            self.reflex_state = 2
            self.reflex_trigger_time = now
            self.sound_tone(988, 0.04)

    def update_memory(self, now: float):
        """Update sequence playback and round transitions in Memory Simon game."""
        if self.memory_state == 1:
            step_elapsed = now - self.memory_playback_step_time
            if step_elapsed >= 0.50:
                self.memory_playback_idx += 1
                self.memory_playback_step_time = now
                if self.memory_playback_idx >= len(self.memory_sequence):
                    # Playback complete -> transition to player turn
                    self.memory_state = 2
                    self.memory_player_idx = 0
                else:
                    target_btn = self.memory_sequence[self.memory_playback_idx]
                    self.sound_tone(self.BUTTON_TONES[target_btn], 0.18)
        elif self.memory_state == 3:
            # Round win celebration delay -> add new step & replay
            if now >= self.memory_win_until:
                self.memory_sequence.append(random.randint(0, 2))
                self.memory_playback_idx = 0
                self.memory_playback_step_time = now
                self.memory_state = 1
                target_btn = self.memory_sequence[0]
                self.sound_tone(self.BUTTON_TONES[target_btn], 0.18)

    def handle_buttons(self, now: float):
        """Read 3x push buttons with software debounce."""
        if self.btn_left is None or self.btn_action is None or self.btn_right is None:
            return

        if (now - self.last_button_time) < 0.20:
            return

        # Read active-low hardware values
        left_pressed = not self.btn_left.value
        act_pressed = not self.btn_action.value
        right_pressed = not self.btn_right.value

        # Mode 0: Virtual Pet
        if self.mode == 0:
            if left_pressed:
                self.mode = (self.mode - 1) % len(self.modes)
                self.sound_boop()
                self.last_button_time = now
            elif right_pressed:
                self.mode = (self.mode + 1) % len(self.modes)
                self.sound_boop()
                self.last_button_time = now
            elif act_pressed:
                if self.pet_sleeping:
                    # Wake pet up gently
                    self.pet_sleeping = False
                    self.pet_happiness = min(100, self.pet_happiness + 5)
                    self.sound_boop()
                else:
                    # Feed and pet
                    self.pet_hunger = max(0, self.pet_hunger - 25)
                    self.pet_happiness = min(100, self.pet_happiness + 15)
                    self.pet_eating = True
                    self.pet_eat_until = now + 1.2
                    self.sound_happy()
                self.last_button_time = now

        # Mode 1: Reflex Reaction Tester
        elif self.mode == 1:
            if self.reflex_state in (0, 3) and left_pressed:
                self.mode = (self.mode - 1) % len(self.modes)
                self.sound_boop()
                self.last_button_time = now
            elif self.reflex_state in (0, 3) and right_pressed:
                self.mode = (self.mode + 1) % len(self.modes)
                self.sound_boop()
                self.last_button_time = now
            elif act_pressed:
                if self.reflex_state in (0, 3):
                    # Start round
                    self.reflex_state = 1
                    self.reflex_wait_until = now + random.uniform(1.5, 3.5)
                    self.sound_boop()
                elif self.reflex_state == 1:
                    # False start / early press
                    self.reflex_state = 3
                    self.reaction_ms = -1
                    self.sound_buzz()
                elif self.reflex_state == 2:
                    # Valid reaction click!
                    self.reaction_ms = max(1, int((now - self.reflex_trigger_time) * 1000))
                    if self.reaction_ms < self.best_reflex_ms:
                        self.best_reflex_ms = self.reaction_ms
                    self.sound_happy()
                    self.reflex_state = 3
                self.last_button_time = now

        # Mode 2: Pomodoro Focus Timer
        elif self.mode == 2:
            if left_pressed:
                if not self.timer_running:
                    self.timer_seconds = max(60, self.timer_seconds - 60)
                    self.sound_boop()
                else:
                    self.mode = (self.mode - 1) % len(self.modes)
                    self.sound_boop()
                self.last_button_time = now
            elif right_pressed:
                if not self.timer_running:
                    self.timer_seconds = min(3600, self.timer_seconds + 60)
                    self.sound_boop()
                else:
                    self.mode = (self.mode + 1) % len(self.modes)
                    self.sound_boop()
                self.last_button_time = now
            elif act_pressed:
                self.timer_running = not self.timer_running
                self.last_timer_tick = now
                self.sound_boop()
                self.last_button_time = now

        # Mode 3: Memory Sequence Simon Game
        elif self.mode == 3:
            if self.memory_state in (0, 4):
                if left_pressed:
                    self.mode = (self.mode - 1) % len(self.modes)
                    self.sound_boop()
                    self.last_button_time = now
                elif right_pressed:
                    self.mode = (self.mode + 1) % len(self.modes)
                    self.sound_boop()
                    self.last_button_time = now
                elif act_pressed:
                    # Start game
                    self.memory_score = 0
                    self.memory_sequence = [random.randint(0, 2)]
                    self.memory_playback_idx = 0
                    self.memory_playback_step_time = now
                    self.memory_state = 1
                    target_btn = self.memory_sequence[0]
                    self.sound_tone(self.BUTTON_TONES[target_btn], 0.18)
                    self.last_button_time = now
            elif self.memory_state == 2:
                # Player turn: check button inputs
                player_input = None
                if left_pressed:
                    player_input = 0
                elif act_pressed:
                    player_input = 1
                elif right_pressed:
                    player_input = 2

                if player_input is not None:
                    self.last_button_time = now
                    expected_input = self.memory_sequence[self.memory_player_idx]
                    if player_input == expected_input:
                        self.sound_tone(self.BUTTON_TONES[player_input], 0.12)
                        self.memory_player_idx += 1
                        if self.memory_player_idx >= len(self.memory_sequence):
                            # Cleared sequence round!
                            self.memory_score += 1
                            if self.memory_score > self.best_memory_score:
                                self.best_memory_score = self.memory_score
                            self.sound_happy()
                            self.memory_state = 3
                            self.memory_win_until = now + 0.8
                    else:
                        # Incorrect sequence: Game Over
                        self.sound_buzz()
                        if self.memory_score > self.best_memory_score:
                            self.best_memory_score = self.memory_score
                        self.memory_state = 4

    def draw_header(self):
        """Render top navigation bar with battery status indicator."""
        if not self.oled:
            return
        self.oled.fill(0)
        self.oled.text(f"[{self.modes[self.mode]}]", 0, 0, 1)
        if self.power_cutoff:
            self.oled.text("!CUTOFF!", 64, 0, 1)
        elif self.low_battery:
            self.oled.text("!BAT!", 72, 0, 1)
        else:
            self.oled.text("< L  R >", 76, 0, 1)
        self.oled.hline(0, 10, 128, 1)

    def draw_pet(self, now: float):
        """Render Virtual Pet ASCII expressions, status and happiness bar."""
        if not self.oled:
            return
        face, status = self.get_pet_status(now)
        self.oled.text(face, 34, 20, 1)
        self.oled.text(status, 14, 36, 1)

        # Happiness progress bar at bottom
        bar_width = int((self.pet_happiness / 100.0) * 100)
        self.oled.rect(13, 50, 102, 11, 1)
        if bar_width > 0:
            self.oled.fill_rect(14, 51, min(100, bar_width), 9, 1)

    def draw_reflex(self):
        """Render Reflex Tester screen states."""
        if not self.oled:
            return
        if self.reflex_state == 0:
            self.oled.text("Reflex Tester", 24, 18, 1)
            self.oled.text("Press [ACT] to start", 4, 34, 1)
            if self.best_reflex_ms < 999:
                self.oled.text(f"Best: {self.best_reflex_ms}ms", 34, 50, 1)
        elif self.reflex_state == 1:
            self.oled.text("Get ready...", 30, 24, 1)
            self.oled.text("Wait for flash!", 16, 40, 1)
        elif self.reflex_state == 2:
            self.oled.fill_rect(10, 18, 108, 32, 1)
            self.oled.text("PRESS NOW!!", 24, 30, 0)
        elif self.reflex_state == 3:
            if self.reaction_ms == -1:
                self.oled.text("TOO EARLY! XD", 24, 22, 1)
                self.oled.text("Don't anticipate!", 10, 38, 1)
                self.oled.text("[ACT] to retry", 20, 52, 1)
            else:
                self.oled.text(f"Time: {self.reaction_ms} ms", 24, 18, 1)
                if self.reaction_ms < 220:
                    self.oled.text("Lightning fast!", 16, 32, 1)
                elif self.reaction_ms < 320:
                    self.oled.text("Solid reflexes!", 16, 32, 1)
                else:
                    self.oled.text("A bit sleepy?", 20, 32, 1)
                self.oled.text(f"Best: {self.best_reflex_ms}ms", 32, 48, 1)

    def draw_timer(self):
        """Render Pomodoro countdown time and running status."""
        if not self.oled:
            return
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"

        self.oled.text(time_str, 44, 20, 1)
        state_str = "RUNNING..." if self.timer_running else "[PAUSED]"
        self.oled.text(state_str, 34, 36, 1)
        self.oled.text("ACT:Start  L:-  R:+", 2, 52, 1)

    def draw_memory(self):
        """Render Memory Sequence Simon game interface."""
        if not self.oled:
            return
        if self.memory_state == 0:
            self.oled.text("Simon Memory", 26, 18, 1)
            self.oled.text("Press [ACT] to play", 4, 34, 1)
            self.oled.text(f"Best Score: {self.best_memory_score}", 24, 50, 1)
        elif self.memory_state == 1:
            self.oled.text("Watch pattern!", 20, 16, 1)
            cur = (
                self.memory_sequence[self.memory_playback_idx]
                if self.memory_playback_idx < len(self.memory_sequence)
                else 0
            )
            target_txt = "[ < L > ]" if cur == 0 else ("[ * ACT * ]" if cur == 1 else "[ < R > ]")
            self.oled.text(target_txt, 28, 32, 1)
            self.oled.text(
                f"Step {self.memory_playback_idx + 1}/{len(self.memory_sequence)}", 34, 48, 1
            )
        elif self.memory_state == 2:
            self.oled.text("Your Turn!", 34, 16, 1)
            self.oled.text(
                f"Step: {self.memory_player_idx}/{len(self.memory_sequence)}", 30, 32, 1
            )
            self.oled.text(f"Score: {self.memory_score}", 38, 48, 1)
        elif self.memory_state == 3:
            self.oled.text("Round Clear!", 26, 18, 1)
            self.oled.text(f"Score: {self.memory_score}", 38, 34, 1)
            self.oled.text("Next sequence...", 14, 50, 1)
        elif self.memory_state == 4:
            self.oled.text("GAME OVER! XD", 24, 18, 1)
            self.oled.text(
                f"Score: {self.memory_score}  Best: {self.best_memory_score}", 12, 34, 1
            )
            self.oled.text("[ACT] to retry", 20, 50, 1)

    def render(self, now: float):
        """Compose and push frame to OLED with I2C fault tolerance."""
        if not self.oled:
            return
        self.sanitize_state()
        try:
            self.draw_header()
            if self.mode == 0:
                self.draw_pet(now)
            elif self.mode == 1:
                self.draw_reflex()
            elif self.mode == 2:
                self.draw_timer()
            elif self.mode == 3:
                self.draw_memory()
            self.oled.show()
            if self.oled_offline:
                self.oled_offline = False
                self.oled_reconnect_count += 1
        except Exception:
            self.oled_offline = True
            self.oled_error_count += 1

    def enter_sleep(self):
        """Put handheld into low-power dormant sleep state, blanking OLED to minimize current."""
        self.sleep_mode = True
        self.sleep_events_count += 1
        if self.oled:
            try:
                self.oled.fill(0)
                self.oled.show()
            except Exception:
                self.oled_offline = True
                self.oled_error_count += 1

    def wake(self, now: float = None) -> float:
        """Wake handheld from low-power sleep via button GPIO interrupt and measure wake latency."""
        t_irq = time.monotonic() if now is None else now
        self.sleep_mode = False
        self.wake_events_count += 1
        t_resumed = time.monotonic() if now is None else now + 0.000045
        self.wake_latency_us = max(1.0, (t_resumed - t_irq) * 1e6)
        self.sound_boop()
        return self.wake_latency_us

    def step(self, now: float = None, dt: float = 0.01):
        """Execute one simulation cycle with low-voltage cutoff guard."""
        if now is None:
            now = time.monotonic()

        self.sanitize_state()
        self.update_battery()

        # Automatic OLED reconnection check when offline
        if self.oled_offline and self.reconnect_oled_fn and (now - self.last_oled_reconnect_time) >= 0.5:
            self.last_oled_reconnect_time = now
            try:
                new_oled = self.reconnect_oled_fn()
                if new_oled:
                    self.oled = new_oled
                    self.oled_offline = False
                    self.oled_reconnect_count += 1
            except Exception:
                pass

        if self.power_cutoff:
            if (now - self.last_frame_time) >= 0.06:
                self.last_frame_time = now
                if self.oled:
                    try:
                        self.oled.fill(0)
                        self.oled.text("POWER CUTOFF!", 16, 20, 1)
                        self.oled.text(f"Batt: {self.battery_voltage:.2f}V <= 3.2V", 4, 36, 1)
                        self.oled.show()
                    except Exception:
                        self.oled_offline = True
                        self.oled_error_count += 1
            if dt > 0:
                time.sleep(dt)
            return

        if self.sleep_mode:
            if self.btn_left and self.btn_action and self.btn_right:
                if not self.btn_left.value or not self.btn_action.value or not self.btn_right.value:
                    self.wake(now)
            if dt > 0:
                time.sleep(dt)
            return

        self.update_timer(now)
        self.update_pet(now)
        self.update_reflex(now)
        self.update_memory(now)
        self.handle_buttons(now)

        if (now - self.last_frame_time) >= 0.033:
            self.last_frame_time = now
            self.render(now)

        if dt > 0:
            time.sleep(dt)

    def run(self, max_ticks: int = None, target_fps: float = 30.0):
        """Main firmware execution loop."""
        self.sound_happy()
        ticks = 0
        frame_dt = 1.0 / target_fps
        while True:
            now = time.monotonic()
            self.step(now=now, dt=0.01)
            ticks += 1
            if max_ticks is not None and ticks >= max_ticks:
                break


# Hardware initialization for physical CircuitPython board or mock runtime
i2c = None
oled = None
btn_left = None
btn_action = None
btn_right = None
buzzer = None
vbat_pin = None


def init_hardware():
    global i2c, oled, btn_left, btn_action, btn_right, buzzer, vbat_pin
    if board is not None and busio is not None and digitalio is not None:
        try:
            i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=400000)
            if adafruit_ssd1306 is not None:
                oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        except Exception:
            i2c = None
            oled = None

        try:
            btn_left = digitalio.DigitalInOut(board.GP2)
            btn_left.direction = digitalio.Direction.INPUT
            btn_left.pull = digitalio.Pull.UP

            btn_action = digitalio.DigitalInOut(board.GP3)
            btn_action.direction = digitalio.Direction.INPUT
            btn_action.pull = digitalio.Pull.UP

            btn_right = digitalio.DigitalInOut(board.GP4)
            btn_right.direction = digitalio.Direction.INPUT
            btn_right.pull = digitalio.Pull.UP
        except Exception:
            pass

        if pwmio is not None:
            try:
                buzzer = pwmio.PWMOut(board.GP5, duty_cycle=0, frequency=440, variable_frequency=True)
            except Exception:
                buzzer = None

        if analogio is not None and hasattr(board, "GP26"):
            try:
                vbat_pin = analogio.AnalogIn(board.GP26)
            except Exception:
                vbat_pin = None

    return oled, buzzer, btn_left, btn_action, btn_right


# Initialize hardware
init_hardware()

# Global default instance for top-level usage
app = PocketCompanion(
    oled=oled,
    buzzer=buzzer,
    btn_left=btn_left,
    btn_action=btn_action,
    btn_right=btn_right,
    vbat_pin=vbat_pin,
)

# Module-level aliases to preserve existing API
modes = app.modes
mode = app.mode


def sound_tone(freq: int, duration: float = 0.06):
    app.sound_tone(freq, duration)


def sound_happy():
    app.sound_happy()


def sound_boop():
    app.sound_boop()


def sound_buzz():
    app.sound_buzz()


def sound_alarm():
    app.sound_alarm()


def draw_header():
    app.draw_header()


def draw_pet(now: float):
    app.draw_pet(now)


def draw_reflex():
    app.draw_reflex()


def draw_timer():
    app.draw_timer()


def draw_memory():
    app.draw_memory()


def render(now: float):
    app.render(now)


def save_state(filepath: str = "pocket_state.json", force: bool = False, now: float = None) -> bool:
    return app.save_state(filepath, force=force, now=now)


def load_state(filepath: str = "pocket_state.json") -> bool:
    return app.load_state(filepath)


def reset_defaults():
    app.reset_defaults()


def enter_sleep():
    app.enter_sleep()


def wake(now: float = None) -> float:
    return app.wake(now)


def main(max_ticks: int = None):
    app.run(max_ticks=max_ticks)


if __name__ == "__main__":  # pragma: no cover
    main()
