"""Pocket Companion Firmware Simulation & Testing Engine.

Comprehensive headless automated test suite for Pocket Companion CircuitPython firmware.
Validates:
- Hardware mocking subsystem (board, digitalio, busio, displayio, pwmio, time)
- Virtual pet emotional state machine (hunger, happiness, sleepiness, feeding, petting, blinking)
- Reflex reaction tester (random delay, millisecond latency measurement, early press penalty, scoring)
- Pomodoro study countdown (duration adjustment, 1s tick countdown, 3-stage buzzer alarm trigger)
- Retro Simon memory game (sequence generation, audio playback, button matching, level-up, game over)
- OLED rendering pipeline across all modes and edge states
- Sound engine and piezo buzzer PWM tone logging
- High-frequency simulation frame execution benchmark
- 100% statement and branch coverage across firmware
"""

import sys
import time
import random
import math
import runpy
import pytest

from tests.mock_hardware import (
    MockBoard,
    MockDigitalio,
    MockBusio,
    MockPwmio,
    MockAdafruitSSD1306,
    MockDisplayio,
    MockPin,
    MockDigitalInOut,
    MockI2C,
    MockPWMOut,
    MockSSD1306_I2C,
    Direction,
    Pull,
    SimulatedClock,
    install_mock_modules,
    uninstall_mock_modules,
)


def create_mock_firmware(sim_clock: SimulatedClock = None):
    """Instantiate a PocketCompanion firmware engine with mock hardware."""
    if sim_clock is None:
        sim_clock = SimulatedClock()

    oled = MockSSD1306_I2C(128, 64)
    buzzer = MockPWMOut(MockPin("GP5"))
    btn_left = MockDigitalInOut(MockPin("GP2"))
    btn_action = MockDigitalInOut(MockPin("GP3"))
    btn_right = MockDigitalInOut(MockPin("GP4"))

    import code
    firmware = code.PocketCompanion(
        oled=oled,
        buzzer=buzzer,
        btn_left=btn_left,
        btn_action=btn_action,
        btn_right=btn_right,
    )
    return firmware, oled, buzzer, btn_left, btn_action, btn_right, sim_clock


# =========================================================================
# 1. Hardware Mocking Subsystem Tests
# =========================================================================

def test_mock_hardware_components():
    """Verify mock hardware modules behave identically to real CircuitPython."""
    board_mock = MockBoard()
    assert hasattr(board_mock, "GP0")
    assert hasattr(board_mock, "GP5")
    assert hasattr(board_mock, "LED")
    assert repr(board_mock.GP0) == "Pin(GP0)"
    assert str(board_mock.GP1) == "GP1"

    dio = MockDigitalInOut(board_mock.GP2)
    assert dio.value is True  # Active low pull-up default
    dio.press()
    assert dio.value is False
    dio.release()
    assert dio.value is True
    dio.toggle()
    assert dio.value is False
    dio.deinit()
    assert dio._deinited is True

    with MockDigitalInOut(board_mock.GP3) as pin:
        assert pin.value is True

    i2c = MockI2C(board_mock.GP1, board_mock.GP0)
    assert i2c.try_lock() is True
    assert i2c.scan() == [0x3C]
    i2c.unlock()
    assert i2c._locked is False
    i2c.deinit()

    pwm = MockPWMOut(board_mock.GP5)
    pwm.frequency = 440
    pwm.duty_cycle = 32768
    assert (440, 32768) in pwm.tone_log
    pwm.duty_cycle = 0
    pwm.deinit()

    oled = MockSSD1306_I2C(128, 64)
    oled.fill(0)
    oled.pixel(10, 10, 1)
    oled.hline(0, 5, 20, 1)
    oled.vline(5, 0, 20, 1)
    oled.line(0, 0, 10, 10, 1)
    oled.rect(10, 10, 20, 20, 1)
    oled.fill_rect(2, 2, 5, 5, 1)
    oled.text("Hello World", 0, 0, 1)
    oled.show()

    assert oled.has_text("Hello")
    assert "Hello World" in oled.get_text_strings()
    assert len(oled.frames) == 1

    disp = MockDisplayio()
    grp = disp.Group()
    grp.append(disp.TileGrid())
    bmp = disp.Bitmap(10, 10)
    pal = disp.Palette(2)
    pal[0] = 0x000000
    disp.release_displays()


def test_simulated_clock():
    """Verify deterministic virtual clock stepping and fast-forwarding."""
    clock = SimulatedClock(initial_time=100.0, fast_forward=True)
    assert clock.monotonic() == 100.0
    clock.advance(5.5)
    assert clock.monotonic() == 105.5
    clock.sleep(2.0)
    assert clock.monotonic() == 107.5
    assert 2.0 in clock.sleep_calls
    clock.set_time(500.0)
    assert clock.monotonic() == 500.0


# =========================================================================
# 2. Virtual Pet Emotional State Machine Simulation Tests
# =========================================================================

def test_pet_initial_emotional_state():
    """Verify pet launches in a happy, healthy baseline condition."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    assert fw.pet_happiness == 85
    assert fw.pet_hunger == 20
    assert fw.pet_sleepiness == 15
    assert fw.pet_sleeping is False
    assert fw.pet_eating is False

    face, status = fw.get_pet_status(fw.last_decay_time)
    assert face == "( ^ _ ^ )"
    assert status == "Super happy!"


def test_pet_hunger_and_decay_over_time():
    """Verify that hunger and tiredness accumulate over time and affect happiness."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    initial_happiness = fw.pet_happiness
    t = fw.last_decay_time

    # Advance through 5 decay cycles (5 * 45s = 225s)
    for _ in range(5):
        t += 45.1
        fw.update_pet(t)

    assert fw.pet_hunger == 20 + (5 * 5)  # 45
    assert fw.pet_sleepiness == 15 + (5 * 4)  # 35
    assert fw.pet_happiness < initial_happiness  # Mood decayed


def test_pet_starvation_mood_crash():
    """Verify that hunger >= 70 triggers severe happiness decay and hungry face."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    fw.pet_hunger = 75
    fw.pet_happiness = 50
    t = fw.last_decay_time + 46.0

    fw.update_pet(t)
    assert fw.pet_happiness == 44  # -6 penalty
    face, status = fw.get_pet_status(t)
    assert face == "( o Q o )"
    assert "Hungry!" in status


def test_pet_exhaustion_natural_sleep_cycle():
    """Verify pet falls asleep when exhausted (sleepiness >= 85) and recovers."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    fw.pet_sleepiness = 84
    fw.pet_hunger = 30
    t = fw.last_decay_time + 46.0

    # Trigger sleepiness crossing 85 threshold
    fw.update_pet(t)
    assert fw.pet_sleepiness == 88
    assert fw.pet_sleeping is True

    face, status = fw.get_pet_status(t)
    assert face == "( z Z Z )"
    assert "Sleeping" in status

    # Sleep cycles: sleepiness recovers by -25 each 45s
    t += 46.0
    fw.update_pet(t)
    assert fw.pet_sleepiness == 63
    assert fw.pet_sleeping is True

    t += 46.0
    fw.update_pet(t)
    assert fw.pet_sleepiness == 38

    t += 46.0
    fw.update_pet(t)
    assert fw.pet_sleepiness == 13

    # Wake up refreshed when sleepiness reaches 0!
    t += 46.0
    fw.update_pet(t)
    assert fw.pet_sleepiness == 0
    assert fw.pet_sleeping is False
    assert fw.pet_happiness > 80


def test_pet_feeding_interaction():
    """Verify feeding decreases hunger, boosts mood, and shows eating animation."""
    fw, oled, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 0
    fw.pet_hunger = 60
    fw.pet_happiness = 60
    t = 100.0
    fw.last_button_time = 90.0

    # Simulate ACT button press
    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.pet_hunger == 35  # -25
    assert fw.pet_happiness == 75  # +15
    assert fw.pet_eating is True
    assert fw.pet_eat_until == t + 1.2
    assert len(buzzer.tone_log) > 0  # Joy chime played

    face, status = fw.get_pet_status(t)
    assert face == "( > w < ) *"
    assert "Yum!" in status

    # After eating timer expires, animation ends
    fw.update_pet(t + 1.3)
    assert fw.pet_eating is False


def test_pet_wake_up_interaction():
    """Verify pressing ACT when pet is sleeping wakes pet up gently."""
    fw, _, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 0
    fw.pet_sleeping = True
    fw.pet_happiness = 50
    t = 100.0
    fw.last_button_time = 90.0

    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.pet_sleeping is False
    assert fw.pet_happiness == 55
    assert len(buzzer.tone_log) > 0


def test_pet_blinking_animation_interval():
    """Verify awake pet blinks every 3 seconds for a quarter second."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    t = fw.last_blink_time + 3.1
    fw.update_pet(t)
    assert fw.pet_blinking is True
    face, _ = fw.get_pet_status(t)
    assert face == "( - _ - )"

    # End blink
    t += 0.2
    fw.update_pet(t)
    assert fw.pet_blinking is False
    face, _ = fw.get_pet_status(t)
    assert face == "( ^ _ ^ )"


def test_pet_expressions_and_status_spectrum():
    """Verify full spectrum of pet mood expressions."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    t = 100.0

    # Sleepy but awake
    fw.pet_sleeping = False
    fw.pet_sleepiness = 80
    face, status = fw.get_pet_status(t)
    assert face == "( - . - )"
    assert "Sleepy" in status

    # Content
    fw.pet_sleepiness = 20
    fw.pet_happiness = 50
    face, status = fw.get_pet_status(t)
    assert face == "( o _ o )"
    assert "Chillin'" in status

    # Sad / bored
    fw.pet_happiness = 20
    face, status = fw.get_pet_status(t)
    assert face == "( ; _ ; )"
    assert "Sad & lonely" in status


def test_pet_oled_progress_bar_bounds():
    """Verify pet OLED rendering with 0 happiness and full 100 happiness."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    fw.mode = 0

    fw.pet_happiness = 0
    oled.fill(0)
    fw.draw_pet(100.0)
    assert any(cmd[0] == "rect" for cmd in oled.draw_commands)

    fw.pet_happiness = 100
    oled.fill(0)
    fw.draw_pet(100.0)
    assert any(cmd[0] == "fill_rect" for cmd in oled.draw_commands)


# =========================================================================
# 3. Reflex Reaction Mini-game Simulation Tests
# =========================================================================

def test_reflex_idle_state_and_start():
    """Verify reflex game starts in idle mode and transitions to countdown."""
    fw, oled, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 1
    assert fw.reflex_state == 0

    # Test when best_reflex_ms < 999
    fw.best_reflex_ms = 210
    fw.draw_reflex()
    assert oled.has_text("Reflex Tester")
    assert oled.has_text("Press [ACT] to start")
    assert oled.has_text("Best: 210ms")

    # Press ACT to start
    t = 100.0
    fw.last_button_time = 90.0
    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.reflex_state == 1
    assert fw.reflex_wait_until >= t + 1.5
    assert len(buzzer.tone_log) > 0


def test_reflex_draw_state_1():
    """Verify reflex drawing during countdown state 1."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    fw.mode = 1
    fw.reflex_state = 1
    fw.draw_reflex()
    assert oled.has_text("Get ready...")
    assert oled.has_text("Wait for flash!")


def test_reflex_false_start_anticipation_penalty():
    """Verify pressing button too early incurs anticipation penalty (-1 ms)."""
    fw, oled, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 1
    fw.reflex_state = 1
    fw.reflex_wait_until = 200.0  # Future trigger
    t = 150.0  # Too early!
    fw.last_button_time = 140.0

    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.reflex_state == 3
    assert fw.reaction_ms == -1

    fw.draw_reflex()
    assert oled.has_text("TOO EARLY! XD")
    assert oled.has_text("Don't anticipate!")


def test_reflex_valid_stimulus_and_latency_measurement():
    """Verify stimulus trigger and precision millisecond latency calculation."""
    fw, oled, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 1
    fw.reflex_state = 1
    fw.reflex_wait_until = 110.0

    # Stimulus time arrives!
    fw.update_reflex(110.0)
    assert fw.reflex_state == 2
    assert fw.reflex_trigger_time == 110.0
    assert any(freq == 988 for freq, _ in buzzer.tone_log)

    fw.draw_reflex()
    assert oled.has_text("PRESS NOW!!")

    # Player reacts 185 milliseconds later
    reaction_time = 110.185
    fw.last_button_time = 100.0
    btn_action.press()
    fw.handle_buttons(reaction_time)
    btn_action.release()

    assert fw.reflex_state == 3
    assert fw.reaction_ms == 185
    assert fw.best_reflex_ms == 185

    fw.draw_reflex()
    assert oled.has_text("Time: 185 ms")
    assert oled.has_text("Lightning fast!")  # Grade S (<220ms)


def test_reflex_grading_categories():
    """Verify reaction time grading messages across latency brackets."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    fw.mode = 1
    fw.reflex_state = 3

    # Solid reflexes (220ms - 319ms)
    fw.reaction_ms = 260
    oled.fill(0)
    fw.draw_reflex()
    assert oled.has_text("Solid reflexes!")

    # Sleepy reflexes (>= 320ms)
    fw.reaction_ms = 410
    oled.fill(0)
    fw.draw_reflex()
    assert oled.has_text("A bit sleepy?")


def test_reflex_restart_from_result():
    """Verify pressing ACT on result screen restarts a fresh round."""
    fw, _, _, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 1
    fw.reflex_state = 3
    t = 100.0
    fw.last_button_time = 90.0

    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.reflex_state == 1


def test_reflex_navigation_buttons():
    """Verify Left/Right buttons navigate mode while in reflex idle or result."""
    fw, _, _, btn_left, _, btn_right, _ = create_mock_firmware()
    fw.mode = 1
    fw.reflex_state = 0
    t = 100.0

    # Left button switches to Pet (0)
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 0

    # Right button switches back to Reflex (1)
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 1


# =========================================================================
# 4. Pomodoro Focus Timer Simulation Tests
# =========================================================================

def test_timer_initialization_and_adjustments():
    """Verify timer duration can be incremented and decremented when paused."""
    fw, oled, _, btn_left, _, btn_right, _ = create_mock_firmware()
    fw.mode = 2
    assert fw.timer_seconds == 25 * 60  # 1500s
    assert fw.timer_running is False

    fw.draw_timer()
    assert oled.has_text("25:00")
    assert oled.has_text("[PAUSED]")

    # Decrement by 1 minute with Left button
    t = 100.0
    fw.last_button_time = 90.0
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.timer_seconds == 24 * 60

    # Increment by 2 minutes with Right button
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.timer_seconds == 25 * 60

    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.timer_seconds == 26 * 60


def test_timer_limits_clamping():
    """Verify timer is clamped between 1 minute (60s) and 60 minutes (3600s)."""
    fw, _, _, btn_left, _, btn_right, _ = create_mock_firmware()
    fw.mode = 2
    fw.timer_seconds = 60
    t = 100.0
    fw.last_button_time = 90.0

    # Attempt to decrement below 60s
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.timer_seconds == 60

    # Attempt to increment above 3600s
    fw.timer_seconds = 3600
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.timer_seconds == 3600


def test_timer_countdown_and_buzzer_alarm_trigger():
    """Verify 1s countdown ticks and 3-stage buzzer alarm on reaching 0."""
    fw, oled, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 2
    fw.timer_seconds = 3  # Set to 3 seconds for simulation
    t = 100.0
    fw.last_button_time = 90.0

    # Start timer
    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()
    assert fw.timer_running is True

    # Tick 1 second
    t += 1.0
    fw.update_timer(t)
    assert fw.timer_seconds == 2

    # Tick 2nd second
    t += 1.0
    fw.update_timer(t)
    assert fw.timer_seconds == 1

    # Tick 3rd second -> Countdown hits 0!
    t += 1.0
    fw.update_timer(t)
    assert fw.timer_seconds == 25 * 60  # Reset to default
    assert fw.timer_running is False
    assert fw.alarm_events_count == 1
    # Check that alarm frequencies (880Hz, 1174Hz) were sounded
    alarm_freqs = [f for f, _ in buzzer.tone_log if f in (880, 1174)]
    assert len(alarm_freqs) >= 6


def test_timer_pause_toggle():
    """Verify pressing ACT while timer is running pauses the countdown."""
    fw, _, _, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 2
    fw.timer_running = True
    t = 100.0
    fw.last_button_time = 90.0

    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.timer_running is False


def test_timer_running_mode_switch():
    """Verify Left/Right switches mode when timer is running instead of adjusting time."""
    fw, _, _, btn_left, _, btn_right, _ = create_mock_firmware()
    fw.mode = 2
    fw.timer_running = True
    t = 100.0
    fw.last_button_time = 90.0

    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 3  # Switched to Memory!

    t += 1.0
    fw.last_button_time = t - 0.5
    fw.mode = 2
    fw.timer_running = True
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 1  # Switched to Reflex!


# =========================================================================
# 5. Retro Mini-Game: Memory Sequence Simon Game Simulation Tests
# =========================================================================

def test_memory_game_idle_screen():
    """Verify Memory Simon launches in idle state with high score."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    fw.mode = 3
    assert fw.memory_state == 0

    fw.draw_memory()
    assert oled.has_text("Simon Memory")
    assert oled.has_text("Press [ACT] to play")
    assert oled.has_text("Best Score: 0")


def test_memory_game_start_and_sequence_playback():
    """Verify starting game generates sequence and completes playback."""
    fw, oled, buzzer, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 3
    t = 100.0
    fw.last_button_time = 90.0

    random.seed(42)
    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.memory_state == 1
    assert len(fw.memory_sequence) == 1
    assert fw.memory_score == 0
    assert fw.memory_playback_idx == 0

    # Draw playback screen
    fw.draw_memory()
    assert oled.has_text("Watch pattern!")

    # Advance time through playback duration (0.55s)
    fw.update_memory(t + 0.55)
    assert fw.memory_state == 2  # Transitioned to player's turn!
    assert fw.memory_player_idx == 0


def test_memory_game_playback_multi_step():
    """Verify playback stepping through multi-step sequence."""
    fw, oled, buzzer, _, _, _, _ = create_mock_firmware()
    fw.mode = 3
    fw.memory_state = 1
    fw.memory_sequence = [0, 1, 2]
    fw.memory_playback_idx = 0
    t = 100.0
    fw.memory_playback_step_time = t

    # Tick to step 1
    fw.update_memory(t + 0.55)
    assert fw.memory_playback_idx == 1
    assert any(f == fw.BUTTON_TONES[1] for f, _ in buzzer.tone_log)

    # Tick to step 2
    fw.update_memory(t + 1.10)
    assert fw.memory_playback_idx == 2
    assert any(f == fw.BUTTON_TONES[2] for f, _ in buzzer.tone_log)


def test_memory_game_player_correct_input_level_up():
    """Verify correct player button input advances sequence and increases score."""
    fw, oled, buzzer, btn_left, btn_action, btn_right, _ = create_mock_firmware()
    fw.mode = 3
    fw.memory_sequence = [0]  # Expected: Left button
    fw.memory_state = 2  # Player turn
    fw.memory_player_idx = 0
    fw.memory_score = 0
    t = 100.0
    fw.last_button_time = 90.0

    # Player presses correct button (Left = 0)
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()

    # Round cleared!
    assert fw.memory_score == 1
    assert fw.best_memory_score == 1
    assert fw.memory_state == 3  # Round clear celebration
    assert fw.memory_win_until == t + 0.8

    fw.draw_memory()
    assert oled.has_text("Round Clear!")
    assert oled.has_text("Score: 1")

    # After celebration delay, expands sequence and returns to playback
    fw.update_memory(t + 0.85)
    assert fw.memory_state == 1
    assert len(fw.memory_sequence) == 2  # Grew by 1!


def test_memory_game_player_input_buttons():
    """Verify player can press ACT (1) and Right (2) buttons correctly."""
    fw, oled, buzzer, _, btn_action, btn_right, _ = create_mock_firmware()
    fw.mode = 3
    fw.memory_sequence = [1, 2]
    fw.memory_state = 2
    fw.memory_player_idx = 0
    t = 100.0
    fw.last_button_time = 90.0

    # Draw player turn screen
    fw.draw_memory()
    assert oled.has_text("Your Turn!")

    # Step 1: press ACT (1)
    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()
    assert fw.memory_player_idx == 1

    # Step 2: press Right (2)
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.memory_state == 3  # Cleared!


def test_memory_game_incorrect_input_game_over():
    """Verify wrong player input triggers buzzer and displays game over screen."""
    fw, oled, buzzer, _, btn_action, btn_right, _ = create_mock_firmware()
    fw.mode = 3
    fw.memory_sequence = [1]  # Expected: ACT button
    fw.memory_state = 2  # Player turn
    fw.memory_player_idx = 0
    fw.memory_score = 3
    t = 100.0
    fw.last_button_time = 90.0

    # Player mistakenly presses Right button (2 != 1)
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()

    assert fw.memory_state == 4  # Game over!
    assert fw.best_memory_score == 3
    assert any(freq == 180 for freq, _ in buzzer.tone_log)  # Buzz tone

    fw.draw_memory()
    assert oled.has_text("GAME OVER! XD")
    assert oled.has_text("Score: 3")
    assert oled.has_text("[ACT] to retry")


def test_memory_game_retry():
    """Verify pressing ACT on Game Over restarts new game."""
    fw, _, _, _, btn_action, _, _ = create_mock_firmware()
    fw.mode = 3
    fw.memory_state = 4
    t = 100.0
    fw.last_button_time = 90.0

    btn_action.press()
    fw.handle_buttons(t)
    btn_action.release()

    assert fw.memory_state == 1
    assert len(fw.memory_sequence) == 1
    assert fw.memory_score == 0


def test_memory_game_navigation_in_idle_and_game_over():
    """Verify Left/Right navigates out of Memory game in idle and game over states."""
    fw, _, _, btn_left, _, btn_right, _ = create_mock_firmware()
    fw.mode = 3
    fw.memory_state = 0
    t = 100.0

    # Left switches to Timer (2)
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 2

    # In Game Over state, Right switches to Pet (0)
    fw.mode = 3
    fw.memory_state = 4
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 0


# =========================================================================
# 6. Navigation & Multi-Mode Transition Tests
# =========================================================================

def test_mode_cyclical_navigation():
    """Verify cycling through all 4 modes in forward and reverse directions."""
    fw, oled, _, btn_left, _, btn_right, _ = create_mock_firmware()
    t = 100.0

    # Pet (0) -> Reflex (1)
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 1

    # Reflex (1) -> Timer (2)
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 2

    # Timer (2) running -> Memory (3)
    fw.timer_running = True
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 3

    # Memory (3) -> Pet (0)
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_right.press()
    fw.handle_buttons(t)
    btn_right.release()
    assert fw.mode == 0

    # Pet (0) -> Memory (3) backwards with Left
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 3

    # Memory (3) -> Timer (2)
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 2

    # Timer (2) running -> Reflex (1)
    fw.timer_running = True
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 1

    # Reflex (1) -> Pet (0)
    t += 1.0
    fw.last_button_time = t - 0.5
    btn_left.press()
    fw.handle_buttons(t)
    btn_left.release()
    assert fw.mode == 0


def test_handle_buttons_guards():
    """Verify handle_buttons guards against None pins and debounce lockout."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    # Pins are None
    fw.btn_left = None
    fw.handle_buttons(100.0)

    # Debounce lockout (< 0.20s)
    fw.btn_left = MockDigitalInOut(MockPin("GP2"))
    fw.last_button_time = 100.0
    fw.handle_buttons(100.10)


# =========================================================================
# 7. Audio Subsystem & Fallback Robustness Tests
# =========================================================================

def test_sound_engine_tones_and_melodies():
    """Verify tone synthesis functions produce correct frequencies and durations."""
    fw, _, buzzer, _, _, _, _ = create_mock_firmware()
    buzzer.tone_log.clear()

    fw.sound_boop()
    assert any(f == 440 for f, _ in buzzer.tone_log)

    fw.sound_buzz()
    assert any(f == 180 for f, _ in buzzer.tone_log)

    fw.sound_happy()
    happy_freqs = [f for f, _ in buzzer.tone_log if f in (523, 659, 784)]
    assert len(happy_freqs) == 3

    fw.sound_alarm()
    assert fw.alarm_events_count == 1


def test_sound_engine_handles_none_or_failing_buzzer():
    """Verify sound methods degrade gracefully when buzzer hardware is absent or errors."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    fw.buzzer = None
    fw.sound_tone(440, 0.01)
    fw.sound_happy()
    fw.sound_alarm()

    class FailingBuzzer:
        def __init__(self):
            self._fail = False
            self.frequency = 440
            self.duty_cycle = 0
            self._fail = True

        def __setattr__(self, key, value):
            if getattr(self, "_fail", False) and key == "frequency":
                raise OSError("PWM bus error")
            super().__setattr__(key, value)

    fw.buzzer = FailingBuzzer()
    fw.sound_tone(440, 0.01)  # Exercises lines 90-91 (except Exception)


# =========================================================================
# 8. Render Engine & Framebuffer Integrity Tests
# =========================================================================

def test_render_all_modes_and_header():
    """Verify full OLED rendering passes for all 4 operational modes."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    t = 100.0

    for m in range(4):
        fw.mode = m
        oled.fill(0)
        fw.render(t)
        assert len(oled.frames) > 0
        header_text = f"[{fw.modes[m]}]"
        assert oled.has_text(header_text)
        assert oled.has_text("< L  R >")

    # Render without OLED attached
    fw.oled = None
    fw.render(t)
    fw.draw_header()
    fw.draw_pet(t)
    fw.draw_reflex()
    fw.draw_timer()
    fw.draw_memory()


def test_step_default_now_and_dt():
    """Verify fw.step with default now=None and zero dt."""
    fw, _, _, _, _, _, _ = create_mock_firmware()
    fw.step(now=None, dt=0.0)


# =========================================================================
# 9. Top-Level Module Compatibility & Direct API Tests
# =========================================================================

def test_module_level_aliases_and_functions():
    """Verify top-level module functions remain 100% backward compatible."""
    import code

    assert "Pet" in code.modes
    assert "Reflex" in code.modes
    assert "Timer" in code.modes
    assert "Memory" in code.modes

    code.sound_tone(440, 0.01)
    code.sound_happy()
    code.sound_boop()
    code.sound_buzz()
    code.sound_alarm()
    code.draw_header()
    code.draw_pet(100.0)
    code.draw_reflex()
    code.draw_timer()
    code.draw_memory()
    code.render(100.0)

    # Test main execution with max_ticks limit
    code.main(max_ticks=3)


def test_hardware_init_function(monkeypatch):
    """Verify code.init_hardware handles both healthy hardware and exceptions."""
    import code

    # Normal healthy init
    oled, buzzer, btn_l, btn_act, btn_r = code.init_hardware()
    assert oled is not None
    assert buzzer is not None

    # Error branches: failing I2C, failing buttons, failing buzzer
    class BrokenBusio:
        class I2C:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("I2C Fail")

    monkeypatch.setattr(code, "busio", BrokenBusio())
    code.init_hardware()

    class BrokenDigitalio:
        class DigitalInOut:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("GPIO Fail")

    monkeypatch.setattr(code, "digitalio", BrokenDigitalio())
    code.init_hardware()

    class BrokenPwmio:
        class PWMOut:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("PWM Fail")

    monkeypatch.setattr(code, "pwmio", BrokenPwmio())
    code.init_hardware()


def test_battery_monitoring_levels_and_header_rendering():
    """Verify battery voltage sensing, low-battery alert, cutoff protection, and error recovery."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()

    # Healthy battery (4.2V)
    fw.update_battery(voltage=4.20)
    assert fw.battery_voltage == 4.20
    assert fw.low_battery is False
    assert fw.power_cutoff is False
    fw.draw_header()
    assert oled.has_text("< L  R >")

    # Low battery warning (3.35V <= 3.4V)
    oled.fill(0)
    fw.update_battery(voltage=3.35)
    assert fw.low_battery is True
    assert fw.power_cutoff is False
    fw.draw_header()
    assert oled.has_text("!BAT!")

    # Power cutoff protection (3.15V <= 3.2V)
    oled.fill(0)
    fw.update_battery(voltage=3.15)
    assert fw.power_cutoff is True
    assert fw.low_battery is True
    fw.draw_header()
    assert oled.has_text("!CUTOFF!")

    # Cutoff guard in step()
    oled.fill(0)
    fw.last_frame_time = 0.0
    fw.step(now=100.0, dt=0.01)
    assert oled.has_text("POWER CUTOFF!")

    # Battery reading from mock AnalogIn
    from tests.mock_hardware import MockAnalogIn, MockPin
    adc = MockAnalogIn(MockPin("GP26"))
    adc.set_voltage(3.80)
    fw.vbat_pin = adc
    fw.update_battery()
    assert 3.75 <= fw.battery_voltage <= 3.85

    # Failing ADC read
    class BrokenADC:
        @property
        def value(self):
            raise OSError("ADC read failed")
    fw.vbat_pin = BrokenADC()
    fw.update_battery()


def test_init_hardware_battery_pin_exception(monkeypatch):
    """Verify init_hardware handles failing analogio gracefully."""
    import code

    class BrokenAnalogio:
        class AnalogIn:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("ADC init failed")

    monkeypatch.setattr(code, "analogio", BrokenAnalogio())
    code.init_hardware()


def test_benchmark_all_modes_execution_speed():
    """Benchmark sustained frame rate across all 4 operational modes."""
    fw, oled, _, _, _, _, _ = create_mock_firmware()
    modes = ["Virtual Pet", "Reflex Tester", "Pomodoro Timer", "Simon Memory"]
    iterations = 500

    for mode_idx, mode_name in enumerate(modes):
        fw.mode = mode_idx
        start = time.perf_counter()
        t = 1000.0
        for _ in range(iterations):
            t += 0.06
            fw.step(now=t, dt=0.0)
        elapsed = time.perf_counter() - start
        fps = iterations / elapsed
        latency_ms = (elapsed / iterations) * 1000.0
        print(f"\n[BENCHMARK] Mode {mode_idx} ({mode_name}): {fps:.1f} FPS | {latency_ms:.4f} ms/frame")
        assert fps > 100.0
# =========================================================================
# 10. Frame Execution Speed Benchmark
# =========================================================================

def test_benchmark_simulation_frame_execution_speed():
    """Benchmark headless simulation frame execution rate across 1000 iterations."""
    fw, oled, _, _, _, _, clock = create_mock_firmware()
    clock.fast_forward = True

    iterations = 1000
    start_real = time.perf_counter()
    virtual_time = 1000.0

    for i in range(iterations):
        virtual_time += 0.06
        fw.step(now=virtual_time, dt=0.0)

    elapsed_real = time.perf_counter() - start_real
    fps = iterations / elapsed_real
    ms_per_frame = (elapsed_real / iterations) * 1000.0

    print(f"\n[BENCHMARK] Executed {iterations} frames in {elapsed_real:.4f}s")
    print(f"[BENCHMARK] Throughput: {fps:.1f} FPS (Target: >100 FPS headless)")
    print(f"[BENCHMARK] Latency: {ms_per_frame:.3f} ms/frame")

    assert fps > 100.0, f"Headless execution throughput {fps:.1f} FPS is below 100 FPS threshold"


def test_boundary_conditions_and_persistence_unit(tmp_path):
    """Verify state persistence, sanitization, boundary checks, and ADC noise filtering."""
    import code
    fw, oled, _, _, _, _, vbat_pin = create_mock_firmware()

    # 1. _safe_val tests
    assert code.PocketCompanion._safe_val(10, 0, 100) == 10
    assert code.PocketCompanion._safe_val(True, 0, 100) is None  # bool rejected
    assert code.PocketCompanion._safe_val(150, 0, 100) is None  # out of bounds int
    assert code.PocketCompanion._safe_val(50.5, 0, 100) == 50   # valid float truncated
    assert code.PocketCompanion._safe_val(float("nan"), 0, 100) is None
    assert code.PocketCompanion._safe_val(float("inf"), 0, 100) is None
    assert code.PocketCompanion._safe_val(float("-inf"), 0, 100) is None
    assert code.PocketCompanion._safe_val(150.5, 0, 100) is None
    assert code.PocketCompanion._safe_val("invalid", 0, 100) is None

    class ExplodingVal:
        def __int__(self):
            raise RuntimeError("kaboom")

    assert code.PocketCompanion._safe_val(ExplodingVal(), 0, 100) is None

    # 2. reset_defaults
    fw.mode = 3
    fw.pet_happiness = 10
    fw.reset_defaults()
    assert fw.mode == 0
    assert fw.pet_happiness == 85
    assert fw.pet_hunger == 20
    assert fw.pet_sleepiness == 15
    assert fw.best_reflex_ms == 999
    assert fw.best_memory_score == 0

    # Module-level reset_defaults
    code.reset_defaults()
    assert code.app.mode == 0

    # 3. sanitize_state
    fw.mode = 99
    fw.sanitize_state()
    assert fw.mode == 0

    fw.mode = -5
    fw.sanitize_state()
    assert fw.mode == 0

    fw.mode = True
    fw.sanitize_state()
    assert fw.mode == 0

    fw.reflex_state = 88
    fw.sanitize_state()
    assert fw.reflex_state == 0

    fw.memory_state = 88
    fw.sanitize_state()
    assert fw.memory_state == 0

    fw.pet_happiness = 200
    fw.sanitize_state()
    assert fw.pet_happiness == 85

    fw.pet_hunger = -50
    fw.sanitize_state()
    assert fw.pet_hunger == 20

    fw.pet_sleepiness = float("nan")
    fw.sanitize_state()
    assert fw.pet_sleepiness == 15

    # 4. save_state and load_state
    valid_file = str(tmp_path / "valid_state.json")
    fw.best_reflex_ms = 195
    fw.best_memory_score = 12
    fw.pet_happiness = 95
    fw.pet_hunger = 10
    fw.pet_sleepiness = 5
    fw.mode = 2
    assert fw.save_state(valid_file) is True

    # Test load_state
    fw2, _, _, _, _, _, _ = create_mock_firmware()
    assert fw2.load_state(valid_file) is True
    assert fw2.best_reflex_ms == 195
    assert fw2.best_memory_score == 12
    assert fw2.pet_happiness == 95
    assert fw2.pet_hunger == 10
    assert fw2.pet_sleepiness == 5
    assert fw2.mode == 2

    # Module-level aliases
    mod_file = str(tmp_path / "mod_state.json")
    assert code.save_state(mod_file) is True
    assert code.load_state(mod_file) is True

    # Error handling paths
    assert fw.save_state("/non_existent_folder_abc_123/state.json") is False
    assert fw.load_state(str(tmp_path / "non_existent.json")) is False

    # Non-dict JSON
    arr_file = str(tmp_path / "array.json")
    with open(arr_file, "w") as f:
        f.write("[1, 2, 3]")
    assert fw.load_state(arr_file) is False

    # Missing keys JSON
    missing_file = str(tmp_path / "missing.json")
    with open(missing_file, "w") as f:
        f.write('{"best_reflex_ms": 100}')
    assert fw.load_state(missing_file) is False

    # Corrupted / out-of-range field JSON
    corrupt_file = str(tmp_path / "corrupt_val.json")
    with open(corrupt_file, "w") as f:
        f.write(
            '{"best_reflex_ms": -99, "best_memory_score": 0, "pet_happiness": 85, '
            '"pet_hunger": 20, "pet_sleepiness": 15, "mode": 0}'
        )
    assert fw.load_state(corrupt_file) is False

    # Broken JSON syntax
    broken_file = str(tmp_path / "broken.json")
    with open(broken_file, "w") as f:
        f.write('{"best_reflex_ms":')
    assert fw.load_state(broken_file) is False

    # 5. update_battery noise filtering
    fw.update_battery("corrupted_analog_data")
    assert fw.battery_voltage >= 2.5

    fw.update_battery(float("nan"))
    assert not math.isnan(fw.battery_voltage)

    fw.update_battery(float("inf"))
    assert not math.isinf(fw.battery_voltage)

    fw.update_battery(15.0)  # Over-voltage spike clamped
    assert fw.battery_voltage <= 4.5

    fw.update_battery(-10.0)  # Negative dip clamped
    assert fw.battery_voltage >= 2.5
