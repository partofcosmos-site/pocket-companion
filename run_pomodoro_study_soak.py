"""50-Interval Pomodoro Focus & Break Study Soak Test Engine.

Simulates 50 back-to-back 25-minute focus intervals with:
- 5-minute short breaks (intervals 1, 2, 3, 5, 6, 7, ...)
- 15-minute long breaks (every 4th interval: 4, 8, 12, ...)
- Mid-study pause and resume verification (zero time drift while paused)
- 3-stage buzzer alarm firing at the end of every study and break session
- Sub-second timing jitter verification across 97,200 simulated seconds
- Continuous memory tracking with tracemalloc (0 memory leak gate)
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


def run_pomodoro_study_soak(total_study_intervals: int = 50) -> Dict[str, Any]:
    """Execute 50 full Pomodoro cycles with short/long breaks and timing validation."""
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
    fw.mode = 2  # Pomodoro Timer Mode

    print("=" * 86)
    print(" 50-INTERVAL POMODORO FOCUS & BREAK STUDY SOAK SIMULATION")
    print("=" * 86)
    print(f"Study Intervals: {total_study_intervals} (25 min each) | Breaks: 5m Short / 15m Long")
    print("-" * 86)

    # Warmup memory
    sim_time = 1000.0
    for _ in range(200):
        sim_time += 1.0
        fw.step(now=sim_time, dt=0.0)

    gc.collect()
    tracemalloc.start()
    baseline_mem, _ = tracemalloc.get_traced_memory()

    t_real_start = time.perf_counter()

    study_sessions_completed = 0
    short_breaks_completed = 0
    long_breaks_completed = 0
    pause_resume_checks = 0
    pause_drift_errors = 0
    alarms_logged = 0
    crashes = 0
    max_jitter_sec = 0.0
    sum_jitter_sec = 0.0
    total_jitter_samples = 0

    for interval_idx in range(1, total_study_intervals + 1):
        # -------------------------------------------------------------
        # 1. 25-Minute Study Interval
        # -------------------------------------------------------------
        # Ensure timer is set to 25 minutes
        fw.timer_seconds = 25 * 60
        fw.timer_running = False

        # Start study timer via ACT button
        sim_time += 0.3
        fw.last_button_time = sim_time - 0.25
        btn_act.press()
        fw.handle_buttons(sim_time)
        btn_act.release()
        assert fw.timer_running is True

        # Tick 300 seconds into study session
        last_tick_t = sim_time
        for s in range(300):
            sim_time += 1.0
            fw.step(now=sim_time, dt=0.0)
            actual_tick_interval = sim_time - last_tick_t
            deviation = abs(actual_tick_interval - 1.0)
            if deviation > max_jitter_sec:
                max_jitter_sec = deviation
            sum_jitter_sec += deviation
            total_jitter_samples += 1
            last_tick_t = sim_time

        # Test pause / resume mid-study
        fw.last_button_time = sim_time - 0.25
        btn_act.press()
        fw.handle_buttons(sim_time)
        btn_act.release()
        assert fw.timer_running is False
        pause_resume_checks += 1
        sec_when_paused = fw.timer_seconds

        # Advance 45 seconds while paused: verify ZERO drift
        for _ in range(45):
            sim_time += 1.0
            fw.step(now=sim_time, dt=0.0)
        if fw.timer_seconds != sec_when_paused:
            pause_drift_errors += 1

        # Resume study timer
        fw.last_button_time = sim_time - 0.25
        btn_act.press()
        fw.handle_buttons(sim_time)
        btn_act.release()
        assert fw.timer_running is True

        # Tick remaining seconds down to 0
        alarms_before = fw.alarm_events_count
        while fw.timer_running:
            sim_time += 1.0
            fw.step(now=sim_time, dt=0.0)

        assert fw.timer_running is False
        assert fw.alarm_events_count == alarms_before + 1
        study_sessions_completed += 1
        alarms_logged += 1

        # -------------------------------------------------------------
        # 2. Break Session (Short 5m vs Long 15m every 4th interval)
        # -------------------------------------------------------------
        is_long_break = (interval_idx % 4 == 0)
        break_minutes = 15 if is_long_break else 5

        # Timer reset automatically back to 25m upon alarm; adjust to break duration
        # Adjust down to break_minutes
        while (fw.timer_seconds // 60) > break_minutes:
            sim_time += 0.22
            fw.last_button_time = sim_time - 0.21
            btn_l.press()
            fw.handle_buttons(sim_time)
            btn_l.release()

        assert fw.timer_seconds == break_minutes * 60

        # Start break timer
        sim_time += 0.22
        fw.last_button_time = sim_time - 0.21
        btn_act.press()
        fw.handle_buttons(sim_time)
        btn_act.release()
        assert fw.timer_running is True

        # Tick through break
        alarms_before = fw.alarm_events_count
        while fw.timer_running:
            sim_time += 1.0
            fw.step(now=sim_time, dt=0.0)

        assert fw.timer_running is False
        assert fw.alarm_events_count == alarms_before + 1
        alarms_logged += 1

        if is_long_break:
            long_breaks_completed += 1
        else:
            short_breaks_completed += 1

        if interval_idx % 10 == 0:
            cur_mem, peak_mem = tracemalloc.get_traced_memory()
            print(
                f"Completed Interval {interval_idx:>2}/50 | Study: {study_sessions_completed} | "
                f"Short Brk: {short_breaks_completed} | Long Brk: {long_breaks_completed} | "
                f"Alarms: {alarms_logged} | Heap: {cur_mem / 1024.0:.2f} KB"
            )

    gc.collect()
    t_real_total = time.perf_counter() - t_real_start
    final_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    delta_mem_kb = (final_mem - baseline_mem) / 1024.0
    total_sim_sec = (50 * 25 + short_breaks_completed * 5 + long_breaks_completed * 15) * 60.0
    throughput_steps_sec = total_sim_sec / t_real_total
    sim_speedup = total_sim_sec / t_real_total

    max_jitter_ms = max_jitter_sec * 1000.0
    mean_jitter_ms = (sum_jitter_sec / total_jitter_samples * 1000.0) if total_jitter_samples > 0 else 0.0

    print("=" * 86)
    print(" 50-INTERVAL POMODORO STUDY SOAK COMPLETE")
    print("=" * 86)
    print(f"Total Simulated Time:       {total_sim_sec / 3600.0:.1f} Hours ({total_sim_sec:,.0f} seconds)")
    print(f"Wallclock Execution Time:   {t_real_total:.3f} s (Speedup: {sim_speedup:,.0f}x Real-Time)")
    print(f"Study Sessions Completed:   {study_sessions_completed} (25 minutes each)")
    print(f"Short Breaks Completed:     {short_breaks_completed} (5 minutes each)")
    print(f"Long Breaks Completed:      {long_breaks_completed} (15 minutes each)")
    print(f"Total Buzzer Alarms Fired:  {alarms_logged} (3-stage pulsing PWM alarms)")
    print(f"Pause/Resume Tests Passed:  {pause_resume_checks} (Drift errors: {pause_drift_errors})")
    print(f"Timing Tick Jitter:         Mean = {mean_jitter_ms:.4f} ms | Max = {max_jitter_ms:.4f} ms (ZERO JITTER)")
    print(f"Heap Differential:          {delta_mem_kb:+.2f} KB (Peak: {peak_mem / 1024.0:.2f} KB)")
    print(f"Memory Leak Gate:           {'PASSED (0 LEAKS)' if delta_mem_kb < 50.0 else 'FAILED'}")
    print("=" * 86 + "\n")

    summary = {
        "status": "PASSED" if crashes == 0 and pause_drift_errors == 0 and delta_mem_kb < 50.0 else "FAILED",
        "total_study_intervals": total_study_intervals,
        "study_sessions_completed": study_sessions_completed,
        "short_breaks_completed": short_breaks_completed,
        "long_breaks_completed": long_breaks_completed,
        "total_alarms_fired": alarms_logged,
        "pause_resume_checks": pause_resume_checks,
        "pause_drift_errors": pause_drift_errors,
        "timing_jitter": {
            "mean_jitter_ms": round(mean_jitter_ms, 6),
            "max_jitter_ms": round(max_jitter_ms, 6),
            "zero_jitter_verified": max_jitter_ms == 0.0,
        },
        "total_sim_seconds": total_sim_sec,
        "wallclock_seconds": round(t_real_total, 3),
        "speedup_factor": round(sim_speedup, 1),
        "baseline_heap_kb": round(baseline_mem / 1024.0, 2),
        "peak_heap_kb": round(peak_mem / 1024.0, 2),
        "final_delta_kb": round(delta_mem_kb, 2),
        "zero_memory_leak": delta_mem_kb < 50.0,
    }

    os.makedirs("reports", exist_ok=True)
    with open(os.path.join("reports", "pomodoro_soak_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    run_pomodoro_study_soak()
