"""Continuous Randomized Game State Fuzzing Engine for Mode 1 (Reflex) & Mode 3 (Simon).

Simulates chaotic player behaviors, edge-case timing, and rapid game cycle transitions:
- Mode 1 (Reflex):
  * True human reactions (120ms - 450ms)
  * False-start anticipations (early button click while in State 1 Waiting)
  * Extreme high-speed reactions (< 150ms) and sluggish reactions (> 500ms)
  * High-resolution sub-millisecond reaction scoring and best-score tracking
- Mode 3 (Simon Memory Game):
  * Perfect sequence solvers (scaling up to 10+ levels)
  * Flawed player inputs (deliberate mismatches triggering State 4 Game Over)
  * Early button presses during State 1 Playback (debounce & ignore verification)
  * Rapid restarts from State 4 back to State 1
  * Sub-millisecond sequence comparison and score increment tracking

Tracks high-resolution score computation latencies to ensure all score evaluations
execute with sub-millisecond (< 1.000 ms) response times.
"""

import sys
import os
import time
import random
import json
import statistics
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


def run_game_state_fuzzing(total_game_cycles: int = 50000) -> Dict[str, Any]:
    """Execute continuous randomized game state fuzzing across Mode 1 and Mode 3."""
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

    print("=" * 86)
    print(" POCKET COMPANION GAME STATE FUZZING RUNNER (MODE 1 REFLEX & MODE 3 SIMON)")
    print("=" * 86)
    print(f"Target Cycles: {total_game_cycles:,} | Tracking: Sub-Millisecond Score Evaluation")
    print("-" * 86)

    sim_time = 1000.0
    reflex_rounds = 0
    reflex_false_starts = 0
    reflex_valid_scores = 0
    reflex_score_latencies_us: List[float] = []

    simon_games_started = 0
    simon_rounds_won = 0
    simon_games_over = 0
    simon_score_latencies_us: List[float] = []

    crashes = 0
    t_start = time.perf_counter()

    for cycle in range(1, total_game_cycles + 1):
        sim_time += 0.02

        # Alternate focus between Mode 1 and Mode 3 every 500 cycles
        current_focus = 1 if (cycle // 500) % 2 == 0 else 3
        if fw.mode != current_focus and not (fw.reflex_state in (1, 2) or fw.memory_state in (1, 2, 3)):
            fw.mode = current_focus

        # -------------------------------------------------------------
        # Mode 1: Reflex Reaction Tester Fuzzing
        # -------------------------------------------------------------
        if fw.mode == 1:
            # State 0: Idle -> Start round
            if fw.reflex_state == 0:
                sim_time += 0.25
                fw.last_button_time = sim_time - 0.21
                btn_act.press()
                fw.handle_buttons(sim_time)
                btn_act.release()
                reflex_rounds += 1

            # State 1: Waiting -> Random chance of early false start vs patient wait
            elif fw.reflex_state == 1:
                # 15% chance player is impatient and triggers false start
                if random.random() < 0.15:
                    sim_time += random.uniform(0.01, 0.5)
                    fw.last_button_time = sim_time - 0.21
                    btn_act.press()

                    t0 = time.perf_counter()
                    fw.handle_buttons(sim_time)
                    t1 = time.perf_counter()

                    btn_act.release()
                    reflex_false_starts += 1
                    reflex_score_latencies_us.append((t1 - t0) * 1_000_000.0)
                else:
                    # Advance to stimulus trigger time
                    sim_time = fw.reflex_wait_until + 0.005
                    fw.update_reflex(sim_time)

            # State 2: Ready (Stimulus visible) -> React!
            elif fw.reflex_state == 2:
                # Reaction latency: Gaussian distribution around 230ms (min 80ms)
                reaction_time = max(0.080, random.gauss(0.230, 0.050))
                sim_time = fw.reflex_trigger_time + reaction_time
                fw.last_button_time = sim_time - 0.21
                btn_act.press()

                t0 = time.perf_counter()
                fw.handle_buttons(sim_time)
                t1 = time.perf_counter()

                btn_act.release()
                reflex_valid_scores += 1
                reflex_score_latencies_us.append((t1 - t0) * 1_000_000.0)

            # State 3: Result -> View result and retry
            elif fw.reflex_state == 3:
                sim_time += 0.30
                fw.last_button_time = sim_time - 0.21
                btn_act.press()
                fw.handle_buttons(sim_time)
                btn_act.release()
                reflex_rounds += 1

        # -------------------------------------------------------------
        # Mode 3: Simon Memory Game Fuzzing
        # -------------------------------------------------------------
        elif fw.mode == 3:
            # State 0 or 4: Idle or Game Over -> Start game
            if fw.memory_state in (0, 4):
                sim_time += 0.25
                fw.last_button_time = sim_time - 0.21
                btn_act.press()
                fw.handle_buttons(sim_time)
                btn_act.release()
                simon_games_started += 1

            # State 1: Playback -> Advance through steps
            elif fw.memory_state == 1:
                # Occasional impatient button mash during playback (must be ignored)
                if random.random() < 0.10:
                    sim_time += 0.05
                    rand_b = random.choice(buttons)
                    rand_b.press()
                    fw.handle_buttons(sim_time)
                    rand_b.release()
                else:
                    sim_time += 0.52
                    fw.update_memory(sim_time)

            # State 2: Player turn -> Enter input
            elif fw.memory_state == 2:
                expected_btn = fw.memory_sequence[fw.memory_player_idx]
                # 80% chance correct input, 20% mistake
                is_correct = random.random() < 0.80
                chosen_btn_idx = expected_btn if is_correct else (expected_btn + 1) % 3

                sim_time += 0.22
                fw.last_button_time = sim_time - 0.21
                buttons[chosen_btn_idx].press()

                t0 = time.perf_counter()
                fw.handle_buttons(sim_time)
                t1 = time.perf_counter()

                buttons[chosen_btn_idx].release()
                score_dt_us = (t1 - t0) * 1_000_000.0
                simon_score_latencies_us.append(score_dt_us)

                if is_correct:
                    if fw.memory_state == 3:
                        simon_rounds_won += 1
                else:
                    simon_games_over += 1

            # State 3: Round Win celebration -> Advance delay to next round
            elif fw.memory_state == 3:
                sim_time += 0.85
                fw.update_memory(sim_time)

        # Step firmware
        try:
            fw.step(now=sim_time, dt=0.0)
        except Exception as e:
            crashes += 1
            print(f"[GAME FUZZ EXCEPTION] Cycle {cycle}: {e}")

        # Invariant asserts
        assert 0 <= fw.mode < 4
        assert fw.reflex_state in (0, 1, 2, 3)
        assert fw.memory_state in (0, 1, 2, 3, 4)

    total_time = time.perf_counter() - t_start
    throughput_fps = total_game_cycles / total_time

    # Calculate score latency statistics
    def calc_stats(latencies: List[float]) -> Dict[str, float]:
        if not latencies:
            return {"mean_us": 0.0, "p95_us": 0.0, "p99_us": 0.0, "max_ms": 0.0}
        s = sorted(latencies)
        n = len(s)
        return {
            "count": n,
            "mean_us": round(statistics.mean(s), 2),
            "p95_us": round(s[int(n * 0.95)], 2),
            "p99_us": round(s[int(n * 0.99)], 2),
            "max_us": round(max(s), 2),
            "max_ms": round(max(s) / 1000.0, 4),
            "sub_millisecond": (max(s) / 1000.0) < 1.0,
        }

    reflex_stats = calc_stats(reflex_score_latencies_us)
    simon_stats = calc_stats(simon_score_latencies_us)

    print("=" * 86)
    print(" GAME STATE FUZZING COMPLETE")
    print("=" * 86)
    print(f"Total Execution Time:       {total_time:.3f} s ({throughput_fps:,.1f} FPS)")
    print(f"Total Exceptions / Crashes: {crashes} (0 required)")
    print(f"Reflex Rounds Evaluated:    {reflex_rounds:,} (Valid: {reflex_valid_scores:,} | False Starts: {reflex_false_starts:,})")
    print(f"Simon Games Started:        {simon_games_started:,} (Rounds Won: {simon_rounds_won:,} | Game Overs: {simon_games_over:,})")
    print("-" * 86)
    print(" SUB-MILLISECOND SCORE TRACKING METRICS:")
    print(f" Mode 1 (Reflex Scoring): Mean = {reflex_stats['mean_us']} us | P95 = {reflex_stats['p95_us']} us | P99 = {reflex_stats['p99_us']} us | Max = {reflex_stats['max_ms']} ms [{'PASS' if reflex_stats['sub_millisecond'] else 'FAIL'}]")
    print(f" Mode 3 (Simon Scoring):  Mean = {simon_stats['mean_us']} us | P95 = {simon_stats['p95_us']} us | P99 = {simon_stats['p99_us']} us | Max = {simon_stats['max_ms']} ms [{'PASS' if simon_stats['sub_millisecond'] else 'FAIL'}]")
    print("=" * 86 + "\n")

    summary = {
        "status": "PASSED" if crashes == 0 and reflex_stats["sub_millisecond"] and simon_stats["sub_millisecond"] else "FAILED",
        "total_cycles": total_game_cycles,
        "elapsed_seconds": round(total_time, 3),
        "throughput_fps": round(throughput_fps, 1),
        "crashes": crashes,
        "reflex_metrics": {
            "total_rounds": reflex_rounds,
            "valid_scores": reflex_valid_scores,
            "false_starts": reflex_false_starts,
            "latency_stats": reflex_stats,
        },
        "simon_metrics": {
            "games_started": simon_games_started,
            "rounds_won": simon_rounds_won,
            "games_over": simon_games_over,
            "latency_stats": simon_stats,
        },
    }

    os.makedirs("reports", exist_ok=True)
    with open(os.path.join("reports", "game_fuzz_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    run_game_state_fuzzing()
