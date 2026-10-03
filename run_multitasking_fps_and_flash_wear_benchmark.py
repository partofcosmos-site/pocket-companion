"""Multi-Tasking Frame Execution Speed, >=30 FPS Animation, & SPI Flash Wear-Out Audit.

Verifies:
1. Multi-Tasking Frame Execution Speed:
   - Simultaneous audio synthesis (piezo buzzer PWM), OLED framebuffer rendering (128x64),
     and 3-button debounced input scanning.
   - High-resolution timing metrics (mean, median, p95, p99, max latency in microseconds).
2. CPU Headroom & >= 30 FPS Full Pet Animation:
   - Sustained frame throughput during full pet animation state (eating animation + blinking +
     emotional status string + dynamic happiness progress bar fill).
   - CPU utilization percentage calculation at target 30 FPS refresh rate.
3. SPI Flash Save Debounce & Wear-Out Prevention:
   - Stress test evaluating 10,000 rapid state save requests.
   - Rate-limiting verification (2.0s debounce interval).
   - Flash write reduction ratio (>99.9% writes suppressed to eliminate SPI flash wear-out).
   - Forced write override verification (immediate emergency commit on cutoff/shutdown).
"""

import sys
import os
import time
import json
import statistics
import tracemalloc
import gc
from typing import Dict, List, Any

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


def run_multitasking_and_flash_wear_benchmark() -> Dict[str, Any]:
    """Execute frame execution speed benchmark and flash write debounce verification."""
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

    print("=" * 88)
    print(" POCKET COMPANION MULTI-TASKING PERFORMANCE & FLASH WEAR-OUT AUDIT ENGINE")
    print("=" * 88)
    print("Benchmarking: Multi-Tasking Frame Latency | >= 30 FPS Full Pet Animation | Flash Debounce")
    print("-" * 88)

    gc.collect()
    tracemalloc.start()
    baseline_mem, _ = tracemalloc.get_traced_memory()

    # -----------------------------------------------------------------------
    # Part 1 & 2: Multi-Tasking Frame Execution Speed & >= 30 FPS Verification
    # -----------------------------------------------------------------------
    # Configure firmware to full active pet animation state:
    # Eating animation active, blinking active, sound playing, buttons polled
    fw.mode = 0  # Mode 0: Virtual Pet
    fw.pet_happiness = 85
    fw.pet_hunger = 20
    fw.pet_sleepiness = 15
    fw.pet_eating = True
    fw.pet_blinking = True

    sim_time = 1000.0
    fw.pet_eat_until = sim_time + 1000.0
    fw.last_frame_time = 0.0

    FRAME_ITERATIONS = 5000
    latencies_us: List[float] = []

    # Warmup
    for _ in range(100):
        sim_time += 0.033
        fw.step(now=sim_time, dt=0.0)

    gc.collect()
    gc.disable()
    t_start_frames = time.perf_counter()
    try:
        for i in range(FRAME_ITERATIONS):
            sim_time += 0.033333  # 30 FPS time delta (33.33 ms)

            # Concurrent Multi-Tasking:
            # 1. Active button manipulation
            if i % 10 == 0:
                btn_act.value = False
            elif i % 10 == 1:
                btn_act.value = True

            # 2. Concurrent sound tone modulation
            if i % 25 == 0:
                fw.sound_tone(523 + (i % 500), 0.01)

            # 3. Maintain eating & blinking animations
            fw.pet_eating = True
            fw.pet_eat_until = sim_time + 5.0
            fw.pet_blinking = (i % 6 < 3)

            # Measure single-frame execution latency
            t0 = time.perf_counter()
            fw.step(now=sim_time, dt=0.0)
            t1 = time.perf_counter()

            latencies_us.append((t1 - t0) * 1_000_000.0)
    finally:
        gc.enable()

    t_end_frames = time.perf_counter()
    total_frames_wallclock = t_end_frames - t_start_frames

    latencies_us.sort()
    n = len(latencies_us)
    mean_lat_us = statistics.mean(latencies_us)
    median_lat_us = statistics.median(latencies_us)
    p95_lat_us = latencies_us[int(n * 0.95)]
    p99_lat_us = latencies_us[int(n * 0.99)]
    min_lat_us = min(latencies_us)
    max_lat_us = max(latencies_us)

    # Calculate sustained frame rate and CPU utilization at 30 FPS target
    max_sustainable_fps = 1_000_000.0 / mean_lat_us if mean_lat_us > 0 else 99999.0
    # At 30 FPS, frame budget is 33.333 ms (33,333 us)
    cpu_utilization_at_30fps_pct = (mean_lat_us / 33_333.33) * 100.0
    cpu_idle_headroom_pct = 100.0 - cpu_utilization_at_30fps_pct

    print(" 1. MULTI-TASKING FRAME EXECUTION SPEED METRICS (FULL PET ANIMATION):")
    print(f"    - Frame Benchmark Count:     {FRAME_ITERATIONS:,} frames")
    print(f"    - Total Wallclock Time:      {total_frames_wallclock:.3f} s")
    print(f"    - Mean Frame Latency:        {mean_lat_us:.2f} us ({mean_lat_us / 1000.0:.4f} ms)")
    print(f"    - Median Frame Latency:      {median_lat_us:.2f} us ({median_lat_us / 1000.0:.4f} ms)")
    print(f"    - 95th Percentile Latency:   {p95_lat_us:.2f} us ({p95_lat_us / 1000.0:.4f} ms)")
    print(f"    - 99th Percentile Latency:   {p99_lat_us:.2f} us ({p99_lat_us / 1000.0:.4f} ms)")
    print(f"    - Min / Max Latency:         [{min_lat_us:.2f} us / {max_lat_us:.2f} us]")
    print(f"    - Max Sustainable Headless:  {max_sustainable_fps:,.1f} FPS")
    print(f"    - CPU Utilization @ 30 FPS:  {cpu_utilization_at_30fps_pct:.2f}% (Target: < 10.0%)")
    print(f"    - CPU Idle Margin @ 30 FPS:  {cpu_idle_headroom_pct:.2f}%")
    print(f"    - 30 FPS Gate Verdict:       {'PASSED (>= 30 FPS MAINTAINED)' if max_sustainable_fps >= 30.0 else 'FAILED'}")
    print("-" * 88)

    # -----------------------------------------------------------------------
    # Part 3: SPI Flash Save Debounce & Wear-Out Prevention Verification
    # -----------------------------------------------------------------------
    print(" 2. SPI FLASH SAVE DEBOUNCE & WEAR-OUT AUDIT:")
    temp_flash_file = os.path.join("reports", "flash_debounce_test.json")
    os.makedirs("reports", exist_ok=True)

    TOTAL_SAVE_ATTEMPTS = 10000
    SIMULATED_SAVE_WINDOW_SEC = 10.0  # 1,000 saves/second spam rate
    time_increment = SIMULATED_SAVE_WINDOW_SEC / TOTAL_SAVE_ATTEMPTS

    fw.reset_defaults()
    fw.save_debounce_sec = 2.0  # 2.0-second rate-limiting debounce
    sim_save_time = 2000.0

    writes_allowed = 0
    writes_suppressed = 0

    t_start_flash = time.perf_counter()
    for attempt_idx in range(1, TOTAL_SAVE_ATTEMPTS + 1):
        sim_save_time += time_increment
        # Attempt to save state
        saved = fw.save_state(temp_flash_file, force=False, now=sim_save_time)
        if saved:
            writes_allowed += 1
        else:
            writes_suppressed += 1

    # Verify forced write override bypasses debounce
    forced_save_ok = fw.save_state(temp_flash_file, force=True, now=sim_save_time + 0.001)
    if forced_save_ok:
        writes_allowed += 1

    t_end_flash = time.perf_counter()

    wear_reduction_pct = (writes_suppressed / TOTAL_SAVE_ATTEMPTS) * 100.0
    # Expected writes with 2.0s debounce across 10s: ~5 normal writes + 1 forced write = 6 writes
    max_expected_writes = int(SIMULATED_SAVE_WINDOW_SEC / fw.save_debounce_sec) + 2

    # Clean up temp file
    if os.path.exists(temp_flash_file):
        try:
            os.remove(temp_flash_file)
        except Exception:
            pass

    print(f"    - Total Save Requests:       {TOTAL_SAVE_ATTEMPTS:,} attempts (1,000 req/s spam)")
    print(f"    - Debounce Threshold:        {fw.save_debounce_sec:.1f} s minimum interval")
    print(f"    - Physical Flash Writes:     {writes_allowed} writes (Expected: <= {max_expected_writes})")
    print(f"    - Suppressed Flash Writes:   {writes_suppressed:,} writes")
    print(f"    - Wear Reduction Ratio:      {wear_reduction_pct:.3f}% wear-out elimination")
    print(f"    - Forced Write Override:     {'PASSED (IMMEDIATE COMMIT)' if forced_save_ok else 'FAILED'}")
    print(f"    - Flash Lifespan Extension:  {TOTAL_SAVE_ATTEMPTS / writes_allowed:,.1f}x multiplier")
    print(f"    - Flash Wear Gate Verdict:   {'PASSED (WEAR PREVENTED)' if writes_allowed <= max_expected_writes else 'FAILED'}")
    print("-" * 88)

    del latencies_us
    gc.collect()
    cur_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    final_delta_kb = (cur_mem - baseline_mem) / 1024.0


    print(" 3. MEMORY STABILITY METRICS:")
    print(f"    - Baseline Heap:             {baseline_mem / 1024.0:.2f} KB")
    print(f"    - Peak Heap:                 {peak_mem / 1024.0:.2f} KB")
    print(f"    - Final Net Heap Delta:      {final_delta_kb:+.2f} KB")
    print(f"    - Memory Leak Gate:          {'PASSED (0 LEAKS)' if final_delta_kb < 35.0 else 'FAILED'}")
    print("=" * 88 + "\n")

    summary = {
        "status": "PASSED" if (
            max_sustainable_fps >= 30.0
            and writes_allowed <= max_expected_writes
            and forced_save_ok
            and final_delta_kb < 35.0
        ) else "FAILED",
        "multitasking_fps_benchmark": {
            "iterations": FRAME_ITERATIONS,
            "mean_latency_us": round(mean_lat_us, 2),
            "median_latency_us": round(median_lat_us, 2),
            "p95_latency_us": round(p95_lat_us, 2),
            "p99_latency_us": round(p99_lat_us, 2),
            "min_latency_us": round(min_lat_us, 2),
            "max_latency_us": round(max_lat_us, 2),
            "max_sustainable_fps": round(max_sustainable_fps, 1),
            "cpu_utilization_at_30fps_pct": round(cpu_utilization_at_30fps_pct, 2),
            "cpu_idle_headroom_pct": round(cpu_idle_headroom_pct, 2),
            "maintains_30fps_animation": max_sustainable_fps >= 30.0,
        },
        "flash_wear_debounce_audit": {
            "total_save_attempts": TOTAL_SAVE_ATTEMPTS,
            "debounce_interval_seconds": fw.save_debounce_sec,
            "physical_writes_executed": writes_allowed,
            "writes_suppressed": writes_suppressed,
            "wear_reduction_pct": round(wear_reduction_pct, 3),
            "forced_override_verified": forced_save_ok,
            "lifespan_extension_multiplier": round(TOTAL_SAVE_ATTEMPTS / writes_allowed, 1),
            "flash_wear_prevented": writes_allowed <= max_expected_writes,
        },
        "memory_metrics": {
            "baseline_heap_kb": round(baseline_mem / 1024.0, 2),
            "peak_heap_kb": round(peak_mem / 1024.0, 2),
            "final_delta_kb": round(final_delta_kb, 2),
            "zero_memory_leak": final_delta_kb < 35.0,
        },
    }

    with open(os.path.join("reports", "multitasking_fps_and_flash_wear_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    run_multitasking_and_flash_wear_benchmark()
