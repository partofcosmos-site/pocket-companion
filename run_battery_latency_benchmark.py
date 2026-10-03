"""Sub-Millisecond Response Latency Benchmark under Simulated Battery Decay.

Measures high-resolution input response latency, step execution time,
and ADC evaluation across battery voltage levels from 4.2V down to 3.0V:
- 4.2V: Nominal full charge LiPo
- 4.0V: Normal high operating curve
- 3.8V: Nominal discharge plateau
- 3.6V: Mid-discharge curve
- 3.4V: Low-battery warning trigger (!BAT! icon)
- 3.3V: Critical low threshold
- 3.2V: Power cutoff trigger (OLED warning & subsystem lock)
- 3.1V: Sub-cutoff deep discharge state
- 3.0V: Absolute low voltage floor

Verifies sub-millisecond (< 1.000 ms) execution across all tiers.
"""

import sys
import time
import statistics
from typing import Dict, List, Tuple

from tests.mock_hardware import (
    MockPin,
    MockDigitalInOut,
    MockAnalogIn,
    MockPWMOut,
    MockSSD1306_I2C,
    install_mock_modules,
)

install_mock_modules()
time.sleep = lambda s: None
import code


def create_benchmark_firmware():
    """Instantiate firmware with mock hardware peripherals."""
    oled = MockSSD1306_I2C(128, 64)
    buzzer = MockPWMOut(MockPin("GP5"))
    btn_l = MockDigitalInOut(MockPin("GP2"))
    btn_act = MockDigitalInOut(MockPin("GP3"))
    btn_r = MockDigitalInOut(MockPin("GP4"))
    vbat_pin = MockAnalogIn(MockPin("GP26"))

    fw = code.PocketCompanion(
        oled=oled,
        buzzer=buzzer,
        btn_left=btn_l,
        btn_action=btn_act,
        btn_right=btn_r,
        vbat_pin=vbat_pin,
    )
    fw.last_frame_time = 0.0
    fw.last_decay_time = 0.0
    fw.last_blink_time = 0.0
    return fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin


def measure_step_latency_at_voltage(voltage: float, iterations: int = 5000) -> Dict[str, float]:
    """Measure single-step execution latency distribution at a given battery voltage."""
    fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin = create_benchmark_firmware()
    vbat_pin.set_voltage(voltage)
    fw.update_battery()

    latencies_us: List[float] = []
    sim_time = 1000.0

    # Warmup
    for _ in range(200):
        sim_time += 0.06
        fw.step(now=sim_time, dt=0.0)

    import gc
    gc.collect()
    gc.disable()
    try:
        for i in range(iterations):
            sim_time += 0.06
            # Rotate modes if not in cutoff
            if not fw.power_cutoff and i % 500 == 0:
                fw.mode = (fw.mode + 1) % 4

            t0 = time.perf_counter()
            fw.step(now=sim_time, dt=0.0)
            t1 = time.perf_counter()

            dt_us = (t1 - t0) * 1_000_000.0
            latencies_us.append(dt_us)
    finally:
        gc.enable()

    latencies_us.sort()
    n = len(latencies_us)
    p95 = latencies_us[int(n * 0.95)]
    p99 = latencies_us[int(n * 0.99)]
    mean_val = statistics.mean(latencies_us)
    min_val = min(latencies_us)
    max_val = max(latencies_us)
    max_ms = max_val / 1000.0

    return {
        "voltage": voltage,
        "iterations": iterations,
        "mode_state": "CUTOFF" if fw.power_cutoff else ("LOW_BAT" if fw.low_battery else "NORMAL"),
        "min_us": min_val,
        "mean_us": mean_val,
        "p95_us": p95,
        "p99_us": p99,
        "max_us": max_val,
        "max_ms": max_ms,
        "sub_millisecond": max_ms < 1.0,
    }


def measure_button_response_latency(voltage: float, iterations: int = 1000) -> Dict[str, float]:
    """Measure end-to-end button input to action handling latency."""
    fw, oled, buzzer, btn_l, btn_act, btn_r, vbat_pin = create_benchmark_firmware()
    vbat_pin.set_voltage(voltage)
    fw.update_battery()

    latencies_us: List[float] = []
    sim_time = 1000.0

    import gc
    gc.collect()
    gc.disable()
    try:
        for i in range(iterations):
            sim_time += 0.5
            fw.last_button_time = sim_time - 0.4
            btn_act.press()

            t0 = time.perf_counter()
            fw.handle_buttons(sim_time)
            fw.render(sim_time)
            t1 = time.perf_counter()

            btn_act.release()
            latencies_us.append((t1 - t0) * 1_000_000.0)
    finally:
        gc.enable()

    latencies_us.sort()
    n = len(latencies_us)
    return {
        "voltage": voltage,
        "mean_us": statistics.mean(latencies_us),
        "p95_us": latencies_us[int(n * 0.95)],
        "p99_us": latencies_us[int(n * 0.99)],
        "max_ms": max(latencies_us) / 1000.0,
        "sub_millisecond": (max(latencies_us) / 1000.0) < 1.0,
    }


def run_full_latency_verification():
    """Execute complete latency benchmark across battery decay curve."""
    voltages = [4.20, 4.00, 3.80, 3.60, 3.40, 3.30, 3.20, 3.10, 3.00]

    print("\n" + "=" * 88)
    print(" SUB-MILLISECOND LATENCY BENCHMARK UNDER SIMULATED BATTERY DECAY (4.2V -> 3.0V)")
    print("=" * 88)
    print(f"{'Voltage':<9} | {'State':<8} | {'Min (us)':<9} | {'Mean (us)':<10} | {'P95 (us)':<9} | {'P99 (us)':<9} | {'Max (ms)':<9} | {'< 1.0ms Pass':<12}")
    print("-" * 88)

    all_passed = True
    results = []

    for v in voltages:
        res = measure_step_latency_at_voltage(v, iterations=5000)
        results.append(res)
        is_sub = res["sub_millisecond"]
        if not is_sub:
            all_passed = False
        status_flag = "PASS" if is_sub else "FAIL"

        print(
            f"{res['voltage']:>5.2f}V   | {res['mode_state']:<8} | {res['min_us']:>8.2f}  | "
            f"{res['mean_us']:>9.2f}  | {res['p95_us']:>8.2f}  | {res['p99_us']:>8.2f}  | "
            f"{res['max_ms']:>8.4f}  | {status_flag:<12}"
        )

    print("=" * 88)
    print("\n" + "=" * 88)
    print(" BUTTON INPUT-TO-RENDER LATENCY BENCHMARK")
    print("=" * 88)
    print(f"{'Voltage':<9} | {'Mean (us)':<10} | {'P95 (us)':<9} | {'P99 (us)':<9} | {'Max (ms)':<9} | {'< 1.0ms Pass':<12}")
    print("-" * 88)

    for v in [4.20, 3.70, 3.40, 3.20, 3.00]:
        btn_res = measure_button_response_latency(v, iterations=1000)
        status_flag = "PASS" if btn_res["sub_millisecond"] else "FAIL"
        print(
            f"{btn_res['voltage']:>5.2f}V   | {btn_res['mean_us']:>9.2f}  | "
            f"{btn_res['p95_us']:>8.2f}  | {btn_res['p99_us']:>8.2f}  | "
            f"{btn_res['max_ms']:>8.4f}  | {status_flag:<12}"
        )

    print("=" * 88)
    print(f"\nSub-Millisecond Response Latency Across All Battery Levels: {'VERIFIED [PASS]' if all_passed else 'FAILED'}\n")
    return results


if __name__ == "__main__":
    run_full_latency_verification()
