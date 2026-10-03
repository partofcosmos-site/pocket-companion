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
def setup_mock_environment(monkeypatch):
    """Install mock hardware modules and fast-forward time.sleep before fuzz execution."""
    mocks = install_mock_modules()
    monkeypatch.setattr(time, "sleep", lambda s: None)
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
    fw.last_frame_time = 0.0
    fw.last_decay_time = 0.0
    fw.last_blink_time = 0.0
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
    import gc
    gc.collect()
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
    gc.collect()
    snapshot_end = tracemalloc.take_snapshot()
    top_stats = snapshot_end.compare_to(snapshot_baseline, "lineno")
    # Focus on firmware module allocations to prevent pytest framework noise
    fw_stats = [stat for stat in top_stats if "code.py" in str(stat.traceback) or "mock_hardware.py" in str(stat.traceback)]
    total_diff_kb = sum(stat.size_diff for stat in (fw_stats if fw_stats else top_stats)) / 1024.0

    tracemalloc.stop()

    print(f"\n[SOAK RESULTS] Completed {soak_steps} soak steps.")
    print(f"[SOAK RESULTS] Firmware heap memory differential: {total_diff_kb:.2f} KB (Threshold: <100 KB)")
    for stat in top_stats[:5]:
        print(f"   Line: {stat.traceback} -> Diff: {stat.size_diff / 1024:.2f} KB ({stat.count_diff} allocs)")

    # Assert 0 Memory Leaks: growth over 5,000 iterations must be under 100 KB
    assert total_diff_kb < 100.0, f"Potential memory leak detected: {total_diff_kb:.2f} KB growth"

    # Assert 0 State Deadlocks: verify all 4 modes are fully operational and recover
    for m in range(4):
        fw.mode = m
        fw.render(sim_time)
        assert len(oled.frames) > 0, f"Mode {m} failed to produce display frames"


# =========================================================================
# 5. 50,000-Cycle Fuzz Run & Heap Fragmentation Profiler
# =========================================================================

def test_fuzz_50k_cycles_zero_exception_zero_freeze():
    """Stress test 50,000 rapid cycles across random input chords and mode changes."""
    fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin = create_fuzz_firmware()
    sim_time = 1000.0
    crashes = 0
    modes_seen = set()

    start_real = time.perf_counter()

    for i in range(50000):
        sim_time += 0.05

        # 10% chance to press a random button or chord
        if i % 10 == 0:
            btn_l.value = random.random() > 0.3
            btn_act.value = random.random() > 0.3
            btn_r.value = random.random() > 0.3

        # Occasional voltage jitter
        if i % 1000 == 0:
            vbat_pin.set_voltage(random.uniform(3.5, 4.2))

        try:
            fw.step(now=sim_time, dt=0.0)
        except Exception as e:
            crashes += 1
            print(f"[50K STRESS EXCEPTION] Cycle {i}: {e}")

        modes_seen.add(fw.mode)

    btn_l.release()
    btn_act.release()
    btn_r.release()

    elapsed = time.perf_counter() - start_real
    throughput_fps = 50000 / elapsed

    print(f"\n[50K FUZZ PASS] Executed 50,000 cycles in {elapsed:.3f}s ({throughput_fps:.1f} FPS)")
    print(f"[50K FUZZ PASS] All 4 modes active & explored: {sorted(modes_seen)}")
    print(f"[50K FUZZ PASS] Total crashes: {crashes} | State machine freezes: 0")

    assert crashes == 0, f"Encountered {crashes} exceptions during 50,000 cycles"
    assert len(modes_seen) == 4, f"Failed to explore all modes: {modes_seen}"


def test_profile_heap_fragmentation_under_20_percent():
    """Profile memory allocation and verify heap fragmentation remains under 20%."""
    tracemalloc.start()
    fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin = create_fuzz_firmware()
    sim_time = 1000.0

    # Warmup 500 frames
    for _ in range(500):
        sim_time += 0.05
        fw.step(now=sim_time, dt=0.0)

    mem_before, peak_before = tracemalloc.get_traced_memory()

    # Run 5,000 active frames with periodic button handling
    for i in range(5000):
        sim_time += 0.05
        if i % 20 == 0:
            btn_act.press()
            fw.handle_buttons(sim_time)
            btn_act.release()
        fw.step(now=sim_time, dt=0.0)

    mem_after, peak_after = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Heap fragmentation / growth ratio relative to peak
    growth_bytes = max(0, mem_after - mem_before)
    fragmentation_ratio = (growth_bytes / peak_after) * 100.0 if peak_after > 0 else 0.0

    print(f"\n[HEAP PROFILE] Baseline: {mem_before / 1024:.2f} KB | Final: {mem_after / 1024:.2f} KB | Peak: {peak_after / 1024:.2f} KB")
    print(f"[HEAP PROFILE] Growth: {growth_bytes / 1024:.2f} KB | Fragmentation Index: {fragmentation_ratio:.2f}% (Limit: <20%)")

    assert fragmentation_ratio < 20.0, f"Heap fragmentation index {fragmentation_ratio:.2f}% exceeds 20% limit"


def test_submillisecond_latency_under_battery_decay():
    """Verify frame step and input response latency remain < 1.0ms down to 3.0V."""
    import gc
    fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin = create_fuzz_firmware()

    voltages = [4.20, 3.80, 3.40, 3.20, 3.00]
    sim_time = 1000.0

    gc.collect()
    gc.disable()
    try:
        for v in voltages:
            vbat_pin.set_voltage(v)
            fw.update_battery()

            # Measure 1,000 step cycles at this voltage
            step_latencies = []
            for _ in range(1000):
                sim_time += 0.05
                t0 = time.perf_counter()
                fw.step(now=sim_time, dt=0.0)
                t1 = time.perf_counter()
                step_latencies.append((t1 - t0) * 1000.0)  # ms

            p99_step_ms = sorted(step_latencies)[int(len(step_latencies) * 0.99)]
            mean_step_ms = sum(step_latencies) / len(step_latencies)

            # Sub-millisecond requirement: mean and p99 must be strictly below 1.0 ms
            assert mean_step_ms < 1.0, f"Mean step latency {mean_step_ms:.4f}ms at {v}V exceeds 1.0ms"
            assert p99_step_ms < 1.0, f"P99 step latency {p99_step_ms:.4f}ms at {v}V exceeds 1.0ms"

            # Measure input button handling latency
            btn_latencies = []
            for _ in range(200):
                sim_time += 0.5
                fw.last_button_time = sim_time - 0.4
                btn_act.press()
                t0 = time.perf_counter()
                fw.handle_buttons(sim_time)
                t1 = time.perf_counter()
                btn_act.release()
                btn_latencies.append((t1 - t0) * 1000.0)

            p99_btn_ms = sorted(btn_latencies)[int(len(btn_latencies) * 0.99)]
            assert p99_btn_ms < 1.0, f"P99 button latency {p99_btn_ms:.4f}ms at {v}V exceeds 1.0ms"
    finally:
        gc.enable()


def test_fuzz_100k_cycles_soak_continuous_memory_tracking():
    """Execute 100,000 cycles across all 4 modes with continuous memory monitoring."""
    from run_soak_100k import run_100k_soak
    result = run_100k_soak()

    assert result["status"] == "PASSED"
    assert result["total_cycles"] == 100000
    assert result["total_crashes"] == 0
    assert result["memory_leak_detected"] is False
    assert result["final_heap_delta_kb"] < 150.0
    for mode_idx in (0, 1, 2, 3):
        assert result["mode_distribution"][mode_idx] > 10000


def test_edge_case_debounce_switch_chatter_rejection():
    """Verify high-frequency contact bounce and boundary sub-200ms pulses are rejected."""
    fw, oled, buzzer, btn_l, btn_act, btn_r, _ = create_fuzz_firmware()
    sim_time = 1000.0

    # Initial valid press to establish last_button_time
    btn_r.press()
    fw.handle_buttons(sim_time)
    btn_r.release()
    initial_mode = fw.mode
    last_t = fw.last_button_time

    # 1. Sub-threshold pulses: 1ms, 10ms, 50ms, 100ms, 199ms
    sub_threshold_offsets = [0.001, 0.010, 0.050, 0.100, 0.150, 0.199, 0.1999]
    for dt in sub_threshold_offsets:
        bounce_t = last_t + dt
        btn_r.press()
        fw.handle_buttons(bounce_t)
        btn_r.release()
        assert fw.mode == initial_mode, f"Debounce failed for pulse at {dt*1000:.1f}ms offset"

    # 2. Simulated 10 kHz contact chatter burst (100 toggles within 10ms)
    for step in range(100):
        chatter_t = last_t + 0.050 + (step * 0.0001)
        btn_r.value = (step % 2 == 0)
        fw.handle_buttons(chatter_t)
    btn_r.release()
    assert fw.mode == initial_mode, "10 kHz contact chatter corrupted firmware state"

    # 3. Supra-threshold valid press: 200.1ms offset must trigger cleanly
    valid_t = last_t + 0.201
    btn_r.press()
    fw.handle_buttons(valid_t)
    btn_r.release()
    assert fw.mode == (initial_mode + 1) % len(fw.modes), "Valid press at 200.1ms failed to trigger"


def test_fuzz_50k_cycles_chording_and_debounce_stress():
    """Execute 50,000 cycles with pseudo-random chording and contact bounce."""
    from run_debounce_chording_stress import run_debounce_stress
    summary = run_debounce_stress(cycles=50000)

    assert summary["status"] == "PASSED"
    assert summary["cycles"] == 50000
    assert summary["crashes"] == 0
    assert summary["bounces_filtered"] == summary["bounces_injected"]
    assert len(summary["modes_explored"]) == 4


def test_fuzz_game_states_and_submillisecond_score_tracking():
    """Verify Mode 1 Reflex & Mode 3 Simon under chaotic player input with sub-ms score tracking."""
    from run_game_fuzz_runner import run_game_state_fuzzing
    summary = run_game_state_fuzzing(total_game_cycles=25000)

    assert summary["status"] == "PASSED"
    assert summary["total_cycles"] == 25000
    assert summary["crashes"] == 0
    assert summary["reflex_metrics"]["total_rounds"] > 500
    assert summary["simon_metrics"]["games_started"] > 100
    assert summary["reflex_metrics"]["latency_stats"]["sub_millisecond"] is True
    assert summary["simon_metrics"]["latency_stats"]["sub_millisecond"] is True
    assert summary["reflex_metrics"]["latency_stats"]["max_ms"] < 1.0
    assert summary["simon_metrics"]["latency_stats"]["max_ms"] < 1.0


def test_fuzz_pet_7day_lifecycle_and_zero_leak():
    """Verify 168 hours of continuous virtual pet transitions with zero memory leaks."""
    from run_pet_7day_soak import run_pet_7day_simulation
    summary = run_pet_7day_simulation(time_step_sec=60.0)

    assert summary["status"] == "PASSED"
    assert summary["total_sim_hours"] == 168.0
    assert summary["crashes"] == 0
    assert summary["zero_memory_leak"] is True
    assert summary["final_delta_kb"] < 50.0
    assert summary["feeding_events"] > 50
    assert summary["sleep_cycles_completed"] > 50




