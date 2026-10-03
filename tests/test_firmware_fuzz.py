"""Pocket Companion Firmware Fuzz Testing & Resilience Suite.

Simulates extreme environmental and operational stress:
1. Rapid concurrent button mashing across BTN_LEFT, BTN_ACTION, BTN_RIGHT.
2. Sudden battery voltage decay and noisy ADC drops from 4.2V down to 3.2V cutoff.
3. Race conditions during asynchronous state machine mode transitions.
4. Continuous multi-thousand cycle soak test verifying:
   - 0 crashes (exceptions caught and prevented)
   - 0 state deadlocks (recoverability across all operational modes)
   - 0 memory leaks (strict heap growth bounds via tracemalloc)
"""

import sys
import time
import random
import tracemalloc
import pytest

from tests.mock_hardware import (
    MockBoard,
    MockDigitalio,
    MockBusio,
    MockPwmio,
    MockAnalogio,
    MockAdafruitSSD1306,
    MockPin,
    MockDigitalInOut,
    MockAnalogIn,
    MockPWMOut,
    MockSSD1306_I2C,
    SimulatedClock,
    install_mock_modules,
    uninstall_mock_modules,
)


@pytest.fixture(autouse=True)
def setup_mock_environment():
    """Install mock hardware modules before fuzz execution."""
    mocks = install_mock_modules()
    yield mocks
    uninstall_mock_modules()


def create_fuzz_firmware():
    """Create firmware instance configured for fuzzing."""
    oled = MockSSD1306_I2C(128, 64)
    buzzer = MockPWMOut(MockPin("GP5"))
    btn_left = MockDigitalInOut(MockPin("GP2"))
    btn_action = MockDigitalInOut(MockPin("GP3"))
    btn_right = MockDigitalInOut(MockPin("GP4"))
    vbat_pin = MockAnalogIn(MockPin("GP26"))

    import code
    fw = code.PocketCompanion(
        oled=oled,
        buzzer=buzzer,
        btn_left=btn_left,
        btn_action=btn_action,
        btn_right=btn_right,
        vbat_pin=vbat_pin,
    )
    return fw, oled, buzzer, btn_left, btn_action, btn_right, vbat_pin


# =========================================================================
# 1. Rapid Concurrent Button Mashing Fuzz Test
# =========================================================================

def test_fuzz_concurrent_button_mashing():
    """Fuzz 3,000 rapid concurrent button chords and verify state validity."""
    fw, oled, buzzer, btn_l, btn_act, btn_r, _ = create_fuzz_firmware()
    buttons = [btn_l, btn_act, btn_r]

    # Pre-generate 8 button state combinations (all combinations of 3 buttons)
    chords = [
        (True, True, True),     # None pressed
        (False, True, True),    # Left only
        (True, False, True),    # Action only
        (True, True, False),    # Right only
        (False, False, True),   # Left + Action
        (True, False, False),   # Action + Right
        (False, True, False),   # Left + Right
        (False, False, False),  # ALL 3 BUTTONS PRESSED
    ]

    sim_time = 1000.0
    crashes = 0
    iterations = 3000

    for i in range(iterations):
        # Pick random chord and random time delta (1ms to 250ms)
        chord = random.choice(chords)
        btn_l.value = chord[0]
        btn_act.value = chord[1]
        btn_r.value = chord[2]

        dt = random.uniform(0.001, 0.25)
        sim_time += dt

        try:
            fw.step(now=sim_time, dt=0.0)
        except Exception as e:
            crashes += 1
            print(f"[CRASH DETECTED] Step {i}: {e}")

        # Invariant Assertions:
        assert 0 <= fw.mode < len(fw.modes), f"Invalid mode index: {fw.mode}"
        assert fw.timer_seconds >= 0, f"Timer underflowed: {fw.timer_seconds}"
        assert 0 <= fw.pet_happiness <= 100, f"Pet happiness out of bounds: {fw.pet_happiness}"
        assert 0 <= fw.pet_hunger <= 100, f"Pet hunger out of bounds: {fw.pet_hunger}"
        assert 0 <= fw.pet_sleepiness <= 100, f"Pet sleepiness out of bounds: {fw.pet_sleepiness}"
        assert fw.reflex_state in (0, 1, 2, 3), f"Corrupted reflex state: {fw.reflex_state}"
        assert fw.memory_state in (0, 1, 2, 3, 4), f"Corrupted memory state: {fw.memory_state}"

    # Release all buttons at conclusion
    btn_l.release()
    btn_act.release()
    btn_r.release()

    assert crashes == 0, f"Encountered {crashes} crashes during button mashing fuzz test"


# =========================================================================
# 2. Battery Voltage Decay & Spurious ADC Drops Fuzz Test
# =========================================================================

def test_fuzz_battery_voltage_decay_and_cutoff():
    """Simulate battery discharge from 4.2V down to 3.2V cutoff with ADC noise."""
    fw, oled, _, _, _, _, vbat_pin = create_fuzz_firmware()

    # Discharge profile with noisy fluctuations
    voltages = [
        4.20, 4.15, 4.10, 4.00, 3.85, 3.70, 3.65, 3.55, 3.45,
        3.40,  # Enters low-battery warning
        3.35, 3.30, 3.25,
        3.20,  # Enters power cutoff protection
        3.15, 3.00, 2.80,
    ]

    sim_time = 1000.0

    for v in voltages:
        sim_time += 1.0
        # Set voltage on mock ADC
        vbat_pin.set_voltage(v)
        fw.step(now=sim_time, dt=0.0)

        if v <= 3.20:
            assert fw.power_cutoff is True, f"Cutoff protection failed to trigger at {v}V"
            assert fw.low_battery is True
            assert oled.has_text("POWER CUTOFF!")
        elif v <= 3.40:
            assert fw.low_battery is True, f"Low battery warning failed to trigger at {v}V"
            assert fw.power_cutoff is False
            assert oled.has_text("!BAT!")
        else:
            assert fw.low_battery is False
            assert fw.power_cutoff is False

    # Simulate charger plug-in event (instant rise from 2.8V back to 4.2V)
    sim_time += 1.0
    vbat_pin.set_voltage(4.20)
    fw.step(now=sim_time, dt=0.0)

    assert fw.power_cutoff is False, "Firmware failed to recover after battery recharge"
    assert fw.low_battery is False


def test_fuzz_noisy_adc_spikes():
    """Fuzz raw 16-bit ADC values including extreme boundary spikes."""
    fw, _, _, _, _, _, vbat_pin = create_fuzz_firmware()

    test_adc_values = [0, 1, 100, 30000, 41704, 60000, 65535, -50, 70000]

    for raw in test_adc_values:
        vbat_pin.value = raw
        fw.update_battery()
        # Battery voltage must always be a valid non-negative float
        assert isinstance(fw.battery_voltage, float)
        assert fw.battery_voltage >= 0.0


# =========================================================================
# 3. Race Conditions During Asynchronous Mode Transitions
# =========================================================================

def test_fuzz_state_machine_transition_race_conditions():
    """Test transitions during active timers, animations, and sound events."""
    fw, oled, buzzer, btn_l, btn_act, btn_r, _ = create_fuzz_firmware()
    sim_time = 1000.0
    crashes = 0

    scenarios = [
        # Scenario A: Mode switch while pet is actively eating
        {"mode": 0, "setup": lambda: setattr(fw, "pet_eating", True)},
        # Scenario B: Mode switch while reflex is waiting random delay
        {"mode": 1, "setup": lambda: (setattr(fw, "reflex_state", 1), setattr(fw, "reflex_wait_until", sim_time + 2.0))},
        # Scenario C: Mode switch at exact moment reflex stimulus fires
        {"mode": 1, "setup": lambda: (setattr(fw, "reflex_state", 2), setattr(fw, "reflex_trigger_time", sim_time))},
        # Scenario D: Mode switch while Pomodoro timer is mid-countdown
        {"mode": 2, "setup": lambda: (setattr(fw, "timer_running", True), setattr(fw, "timer_seconds", 5))},
        # Scenario E: Mode switch while Simon Memory is in playback
        {"mode": 3, "setup": lambda: (setattr(fw, "memory_state", 1), setattr(fw, "memory_sequence", [0, 1, 2]))},
        # Scenario F: Mode switch while Simon Memory is in celebration
        {"mode": 3, "setup": lambda: (setattr(fw, "memory_state", 3), setattr(fw, "memory_win_until", sim_time + 1.0))},
    ]

    for round_idx in range(50):
        for scen in scenarios:
            fw.mode = scen["mode"]
            scen["setup"]()

            # Rapidly cycle modes through Left and Right inputs
            for _ in range(5):
                sim_time += 0.25
                fw.last_button_time = sim_time - 0.5
                btn_r.press()
                fw.handle_buttons(sim_time)
                btn_r.release()

                btn_l.press()
                fw.handle_buttons(sim_time + 0.1)
                btn_l.release()

                fw.step(now=sim_time, dt=0.0)

    assert crashes == 0


# =========================================================================
# 4. Continuous Soak Test: 0 Crashes, 0 Deadlocks, 0 Memory Leaks
# =========================================================================

def test_fuzz_soak_and_zero_memory_leak():
    """Execute 5,000 soak iterations monitoring heap growth and liveness."""
    tracemalloc.start()
    fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin = create_fuzz_firmware()

    warmup_steps = 500
    soak_steps = 5000
    sim_time = 1000.0

    # Warmup phase: initialize all internal state collections
    for _ in range(warmup_steps):
        sim_time += 0.05
        fw.step(now=sim_time, dt=0.0)

    # Snapshot baseline memory after warmup
    snapshot_baseline = tracemalloc.take_snapshot()

    # Soak execution phase
    for step_i in range(soak_steps):
        sim_time += 0.04

        # Randomly toggle buttons occasionally
        if random.random() < 0.2:
            btn = random.choice([btn_l, btn_act, btn_r])
            btn.press()
            fw.handle_buttons(sim_time)
            btn.release()

        # Step simulation engine
        fw.step(now=sim_time, dt=0.0)

    # Snapshot end memory
    snapshot_end = tracemalloc.take_snapshot()
    top_stats = snapshot_end.compare_to(snapshot_baseline, "lineno")
    total_diff_kb = sum(stat.size_diff for stat in top_stats) / 1024.0

    tracemalloc.stop()

    print(f"\n[SOAK RESULTS] Completed {soak_steps} soak steps.")
    print(f"[SOAK RESULTS] Heap memory differential: {total_diff_kb:.2f} KB (Threshold: <100 KB)")

    # Assert 0 Memory Leaks: growth over 5,000 iterations must be under 100 KB
    assert total_diff_kb < 100.0, f"Potential memory leak detected: {total_diff_kb:.2f} KB growth"

    # Assert 0 State Deadlocks: verify all 4 modes are fully operational and recover
    for m in range(4):
        fw.mode = m
        fw.render(sim_time)
        assert len(oled.frames) > 0, f"Mode {m} failed to produce display frames"
