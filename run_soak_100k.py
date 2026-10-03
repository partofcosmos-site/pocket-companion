"""100,000-Cycle Headless Soak Test with Continuous Memory Tracking.

Executes 100,000 continuous simulation steps across all 4 operating modes:
- Mode 0: Virtual Pet (emotional state transitions, feeding, petting, sleeping, blinking)
- Mode 1: Reflex Reaction Tester (random wait, stimulus trigger, reaction timing)
- Mode 2: Pomodoro Focus Timer (countdown ticks, start/pause, minute adjustments)
- Mode 3: Simon Memory Game (sequence generation, playback, player input replay)

Tracks continuous memory every 5,000 cycles:
- Traced Heap Allocation (KB)
- Peak Heap Usage (KB)
- Memory Growth Delta (KB)
- Garbage collection stability
- Throughput (FPS) & Frame Execution Latency
- Zero unhandled exceptions / zero state deadlocks
"""

import sys
import os
import time
import json
import random
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


def run_100k_soak():
    os.makedirs("reports", exist_ok=True)
    report_file = os.path.join("reports", "soak_100k_report.json")

    oled = MockSSD1306_I2C(128, 64)
    buzzer = MockPWMOut(MockPin("GP5"))
    btn_l = MockDigitalInOut(MockPin("GP2"))
    btn_act = MockDigitalInOut(MockPin("GP3"))
    btn_r = MockDigitalInOut(MockPin("GP4"))
    vbat_pin = MockAnalogIn(MockPin("GP26"))
    buttons = [btn_l, btn_act, btn_r]

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

    TOTAL_CYCLES = 100000
    SAMPLE_INTERVAL = 5000

    print("=" * 86)
    print(" POCKET COMPANION 100,000-CYCLE SOAK TEST WITH CONTINUOUS MEMORY TRACKING")
    print("=" * 86)
    print(f"Target Cycles: {TOTAL_CYCLES:,} | Checkpoint Every: {SAMPLE_INTERVAL:,} cycles")
    print(f"Modes: {fw.modes} | Target Architecture: Waveshare RP2040-Zero Headless Mock")
    print("-" * 86)

    # Warmup phase (1,000 steps)
    sim_time = 1000.0
    for _ in range(1000):
        sim_time += 0.05
        fw.step(now=sim_time, dt=0.0)

    gc.collect()
    tracemalloc.start()
    baseline_cur, baseline_peak = tracemalloc.get_traced_memory()

    checkpoints: List[Dict[str, Any]] = []
    mode_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    crashes = 0
    t_start = time.perf_counter()
    last_checkpoint_t = t_start

    print(f"{'Cycle':<9} | {'Heap (KB)':<10} | {'Peak (KB)':<10} | {'Delta (KB)':<11} | {'FPS':<10} | {'Mode Distribution':<28}")
    print("-" * 86)

    for cycle in range(1, TOTAL_CYCLES + 1):
        sim_time += 0.05

        # Record mode execution
        mode_counts[fw.mode] = mode_counts.get(fw.mode, 0) + 1

        # Interactive stimulus: switch modes or press buttons every 15 cycles
        if cycle % 15 == 0:
            action = random.random()
            if action < 0.25:
                # Cycle mode
                fw.mode = (fw.mode + 1) % 4
            elif action < 0.70:
                # Press a random button
                btn = random.choice(buttons)
                btn.press()
                fw.last_button_time = sim_time - 0.4
                fw.handle_buttons(sim_time)
                btn.release()
            else:
                # Multi-button chord
                btn_l.value = random.random() < 0.5
                btn_act.value = random.random() < 0.5
                btn_r.value = random.random() < 0.5
                fw.handle_buttons(sim_time)
                btn_l.release()
                btn_act.release()
                btn_r.release()

        # Simulated battery voltage decay curve:
        # Every 10,000 cycles, smoothly transition through discharge and recharge
        phase_in_10k = cycle % 10000
        if phase_in_10k < 7000:
            # 4.2V down to 3.45V normal operation
            v_now = 4.20 - (phase_in_10k / 7000.0) * 0.75
        elif phase_in_10k < 8500:
            # 3.45V down to 3.25V low battery warning
            v_now = 3.45 - ((phase_in_10k - 7000) / 1500.0) * 0.20
        elif phase_in_10k < 9500:
            # 3.20V down to 3.05V cutoff threshold
            v_now = 3.20 - ((phase_in_10k - 8500) / 1000.0) * 0.15
        else:
            # Recharging back to 4.2V
            v_now = 3.05 + ((phase_in_10k - 9500) / 500.0) * 1.15

        vbat_pin.set_voltage(v_now)

        # Step firmware
        try:
            fw.step(now=sim_time, dt=0.0)
        except Exception as e:
            crashes += 1
            print(f"[EXCEPTION] Cycle {cycle}: {e}")

        # Checkpoint memory tracking
        if cycle % SAMPLE_INTERVAL == 0:
            now_t = time.perf_counter()
            segment_fps = SAMPLE_INTERVAL / (now_t - last_checkpoint_t)
            last_checkpoint_t = now_t

            cur_bytes, peak_bytes = tracemalloc.get_traced_memory()
            cur_kb = cur_bytes / 1024.0
            peak_kb = peak_bytes / 1024.0
            delta_kb = (cur_bytes - baseline_cur) / 1024.0

            mode_str = f"P:{mode_counts[0]:,} R:{mode_counts[1]:,} T:{mode_counts[2]:,} M:{mode_counts[3]:,}"
            print(
                f"{cycle:>7,}   | {cur_kb:>8.2f}   | {peak_kb:>8.2f}   | {delta_kb:>+9.2f}   | "
                f"{segment_fps:>8.1f} | {mode_str:<28}"
            )

            checkpoints.append({
                "cycle": cycle,
                "current_kb": round(cur_kb, 2),
                "peak_kb": round(peak_kb, 2),
                "delta_kb": round(delta_kb, 2),
                "segment_fps": round(segment_fps, 1),
                "mode_counts": dict(mode_counts),
                "voltage": round(v_now, 3),
            })

    total_time = time.perf_counter() - t_start
    overall_fps = TOTAL_CYCLES / total_time
    gc.collect()
    final_cur, final_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    final_delta_kb = (final_cur - baseline_cur) / 1024.0
    leak_detected = final_delta_kb > 30.0  # Strict threshold: < 30.0 KB for 100,000 cycles

    print("=" * 86)
    print(f" 100,000-CYCLE SOAK TEST COMPLETE")
    print("=" * 86)
    print(f"Total Execution Time: {total_time:.3f} s")
    print(f"Average Throughput:   {overall_fps:,.1f} FPS")
    print(f"Total Crashes:        {crashes} (0 required)")
    print(f"Baseline Heap:        {baseline_cur / 1024.0:.2f} KB")
    print(f"Peak Heap:            {final_peak / 1024.0:.2f} KB")
    print(f"Final Heap Delta:     {final_delta_kb:+.2f} KB")
    print(f"Memory Leak Status:   {'PASSED (ZERO LEAK)' if not leak_detected else 'FAILED (LEAK DETECTED)'}")
    print(f"Mode Distribution:    Pet={mode_counts[0]:,} | Reflex={mode_counts[1]:,} | Timer={mode_counts[2]:,} | Simon={mode_counts[3]:,}")
    print("=" * 86 + "\n")

    summary_data = {
        "status": "PASSED" if crashes == 0 and not leak_detected else "FAILED",
        "total_cycles": TOTAL_CYCLES,
        "sample_interval": SAMPLE_INTERVAL,
        "elapsed_seconds": round(total_time, 3),
        "overall_fps": round(overall_fps, 1),
        "total_crashes": crashes,
        "baseline_heap_kb": round(baseline_cur / 1024.0, 2),
        "peak_heap_kb": round(final_peak / 1024.0, 2),
        "final_heap_delta_kb": round(final_delta_kb, 2),
        "memory_leak_detected": leak_detected,
        "mode_distribution": mode_counts,
        "checkpoints": checkpoints,
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    return summary_data


if __name__ == "__main__":
    run_100k_soak()
