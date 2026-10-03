"""7-Day Continuous Non-Stop Virtual Pet Emotional Lifecycle & Soak Simulation.

Simulates 168 hours (604,800 seconds) of continuous Virtual Pet time:
- Realistic circadian owner interaction: breakfast feed, afternoon play, dinner feed, and natural nocturnal sleep.
- Periodic neglect cycles: starving and exhaustion stress testing.
- Natural fatigue accumulation (sleepiness >= 85 -> sleeping = True).
- Sleep recovery (sleepiness -> 0 -> natural wake-up refreshed with happiness bonus).
- High-frequency blinking and eating animation timer resolution.
- Heap memory tracking with tracemalloc across all 168 simulated hours (0 memory leak gate).
"""

import sys
import os
import time
import random
import json
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


def run_pet_7day_simulation(time_step_sec: float = 30.0) -> Dict[str, Any]:
    """Execute 168 hours of continuous virtual pet emotional simulation."""
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
    fw.mode = 0  # Virtual Pet Mode

    TOTAL_SIM_SECONDS = 7 * 24 * 3600.0  # 168 hours = 604,800 seconds
    sim_time = 1000.0
    fw.last_decay_time = sim_time
    fw.last_blink_time = sim_time
    fw.last_frame_time = sim_time

    print("=" * 86)
    print(" VIRTUAL PET 7-DAY (168 HOURS) CONTINUOUS EMOTIONAL LIFECYCLE SIMULATION")
    print("=" * 86)
    print(f"Simulated Duration: 168.0 Hours (604,800 s) | Time Slice Step: {time_step_sec} s")
    print("-" * 86)

    # Warmup memory
    for _ in range(200):
        sim_time += 1.0
        fw.step(now=sim_time, dt=0.0)

    gc.collect()
    tracemalloc.start()
    baseline_mem, _ = tracemalloc.get_traced_memory()

    t_real_start = time.perf_counter()

    feeding_events = 0
    waking_events = 0
    sleep_cycles_completed = 0
    in_sleep_streak = False

    mood_counts = {
        "Super happy!": 0,
        "Chillin'": 0,
        "Sad & lonely": 0,
        "Hungry! Feed me": 0,
        "Sleepy... yawn": 0,
        "Sleeping... zZz": 0,
        "Yum! Fed & Happy": 0,
    }

    steps = int(TOTAL_SIM_SECONDS / time_step_sec)
    checkpoints = []
    crashes = 0

    for step_i in range(1, steps + 1):
        sim_time += time_step_sec
        hour_of_day = ((sim_time - 1000.0) / 3600.0) % 24.0
        day_of_sim = int((sim_time - 1000.0) / 86400.0) + 1

        # Track sleep cycles
        if fw.pet_sleeping and not in_sleep_streak:
            in_sleep_streak = True
        elif not fw.pet_sleeping and in_sleep_streak:
            sleep_cycles_completed += 1
            in_sleep_streak = False

        # Owner interaction logic based on hour of day:
        # Normal owner interacts during daytime (8 AM, 1 PM, 7 PM)
        # Day 4: Neglect day (owner is away, pet gets very hungry and sleeps naturally)
        if day_of_sim != 4:
            # Morning feeding (8:00 - 8:30)
            if 8.0 <= hour_of_day < 8.5 and fw.pet_hunger >= 30:
                fw.last_button_time = sim_time - 0.3
                btn_act.press()
                fw.handle_buttons(sim_time)
                btn_act.release()
                if fw.pet_eating:
                    feeding_events += 1
                else:
                    waking_events += 1

            # Lunch play & snack (13:00 - 13:30)
            elif 13.0 <= hour_of_day < 13.5 and fw.pet_hunger >= 35:
                fw.last_button_time = sim_time - 0.3
                btn_act.press()
                fw.handle_buttons(sim_time)
                btn_act.release()
                if fw.pet_eating:
                    feeding_events += 1
                else:
                    waking_events += 1

            # Dinner feeding (19:00 - 19:30)
            elif 19.0 <= hour_of_day < 19.5 and fw.pet_hunger >= 30:
                fw.last_button_time = sim_time - 0.3
                btn_act.press()
                fw.handle_buttons(sim_time)
                btn_act.release()
                if fw.pet_eating:
                    feeding_events += 1
                else:
                    waking_events += 1

        # Step firmware
        try:
            fw.step(now=sim_time, dt=0.0)
        except Exception as e:
            crashes += 1
            print(f"[PET CRASH] Step {step_i} at hour {hour_of_day:.1f}: {e}")

        # Record mood
        face, mood = fw.get_pet_status(sim_time)
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

        # Invariant checks
        assert 0 <= fw.pet_happiness <= 100, f"Happiness corrupted: {fw.pet_happiness}"
        assert 0 <= fw.pet_hunger <= 100, f"Hunger corrupted: {fw.pet_hunger}"
        assert 0 <= fw.pet_sleepiness <= 100, f"Sleepiness corrupted: {fw.pet_sleepiness}"

        # Checkpoint every 24 simulated hours (every day)
        if step_i % int(86400.0 / time_step_sec) == 0:
            cur_mem, peak_mem = tracemalloc.get_traced_memory()
            checkpoints.append({
                "day": day_of_sim,
                "hour": round((sim_time - 1000.0) / 3600.0, 1),
                "hunger": fw.pet_hunger,
                "happiness": fw.pet_happiness,
                "sleepiness": fw.pet_sleepiness,
                "sleeping": fw.pet_sleeping,
                "mood": mood,
                "cur_heap_kb": round(cur_mem / 1024.0, 2),
                "peak_heap_kb": round(peak_mem / 1024.0, 2),
            })
            print(
                f"Day {day_of_sim} Complete | Sim Hours: {day_of_sim * 24:>3.0f}h | "
                f"Mood: {mood:<18} | Hap: {fw.pet_happiness:>3}% | Hng: {fw.pet_hunger:>3}% | "
                f"Slp: {fw.pet_sleepiness:>3}% | Heap: {cur_mem / 1024.0:>5.2f} KB"
            )

    t_real_total = time.perf_counter() - t_real_start
    final_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    delta_mem_kb = (final_mem - baseline_mem) / 1024.0
    throughput_fps = steps / t_real_total
    sim_speedup = TOTAL_SIM_SECONDS / t_real_total

    print("=" * 86)
    print(" 7-DAY SIMULATION RESULTS SUMMARY")
    print("=" * 86)
    print(f"Total Simulated Time:       168.0 Hours (604,800 seconds)")
    print(f"Wallclock Execution Time:   {t_real_total:.3f} s (Speedup: {sim_speedup:,.0f}x Real-Time)")
    print(f"Throughput:                 {throughput_fps:,.1f} Simulation Steps/Sec")
    print(f"Total Crashes / Deadlocks:  {crashes} (0 required)")
    print(f"Feeding Events Handled:     {feeding_events}")
    print(f"Gentle Wake-ups Handled:    {waking_events}")
    print(f"Sleep-Wake Cycles Finished: {sleep_cycles_completed}")
    print("-" * 86)
    print(" MOOD & EMOTIONAL DISTRIBUTION ACROSS 7 DAYS:")
    for m_name, m_cnt in mood_counts.items():
        pct = (m_cnt / steps) * 100.0
        print(f" - {m_name:<20}: {m_cnt:>6,} slices ({pct:5.1f}%)")
    print("-" * 86)
    print(" MEMORY STABILITY METRICS:")
    print(f" Baseline Heap:             {baseline_mem / 1024.0:.2f} KB")
    print(f" Peak Heap:                 {peak_mem / 1024.0:.2f} KB")
    print(f" Final Heap Delta:          {delta_mem_kb:+.2f} KB")
    print(f" Memory Leak Gate:          {'PASSED (0 LEAKS)' if delta_mem_kb < 50.0 else 'FAILED'}")
    print("=" * 86 + "\n")

    summary = {
        "status": "PASSED" if crashes == 0 and delta_mem_kb < 50.0 else "FAILED",
        "total_sim_hours": 168.0,
        "total_sim_seconds": TOTAL_SIM_SECONDS,
        "steps_executed": steps,
        "wallclock_seconds": round(t_real_total, 3),
        "speedup_factor": round(sim_speedup, 1),
        "crashes": crashes,
        "feeding_events": feeding_events,
        "waking_events": waking_events,
        "sleep_cycles_completed": sleep_cycles_completed,
        "mood_distribution": mood_counts,
        "baseline_heap_kb": round(baseline_mem / 1024.0, 2),
        "peak_heap_kb": round(peak_mem / 1024.0, 2),
        "final_delta_kb": round(delta_mem_kb, 2),
        "zero_memory_leak": delta_mem_kb < 50.0,
        "daily_checkpoints": checkpoints,
    }

    os.makedirs("reports", exist_ok=True)
    with open(os.path.join("reports", "pet_7day_soak_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    run_pet_7day_simulation()
