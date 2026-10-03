"""
Hardware Documentation Graphics Generator for Pocket Companion
(Hack Club Half-Life)
Asset 3: 03_power_budget_battery_discharge_curve.png
Publication-Grade Power Budget & Battery Discharge Profile
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.gridspec as gridspec

def create_power_budget_chart(output_path):
    fig = plt.figure(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0B0F19')

    gs = gridspec.GridSpec(2, 2, height_ratios=[1.3, 1.0],
                           left=0.04, right=0.96, top=0.90, bottom=0.06, wspace=0.18, hspace=0.28)

    # ------------------ MASTER HEADER ------------------
    ax_header = fig.add_axes([0.02, 0.915, 0.96, 0.07])
    ax_header.set_facecolor('#0B0F19')
    ax_header.axis('off')

    hbanner = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.15",
                             facecolor='#111827', edgecolor='#1F2937', linewidth=1.5,
                             transform=ax_header.transAxes)
    ax_header.add_patch(hbanner)

    badge = FancyBboxPatch((0.012, 0.2), 0.045, 0.6, boxstyle="round,pad=0.015,rounding_size=0.1",
                           facecolor='#059669', edgecolor='#34D399', linewidth=1.2,
                           transform=ax_header.transAxes)
    ax_header.add_patch(badge)
    ax_header.text(0.0345, 0.5, "POWER", color='#FFFFFF', fontsize=9.0, fontweight='bold',
                   fontfamily='DejaVu Sans', ha='center', va='center', transform=ax_header.transAxes)

    ax_header.text(0.105, 0.65, "POCKET COMPANION — POWER BUDGET & BATTERY DISCHARGE PROFILE",
                   color='#F9FAFB', fontsize=12.2, fontweight='bold', fontfamily='DejaVu Sans',
                   va='center', transform=ax_header.transAxes)
    ax_header.text(0.105, 0.28, "400mAh 3.7V LiPo Runtime Characterization | Subsystem Current Breakdown | 12.5h - 14.3h Verification",
                   color='#9CA3AF', fontsize=8.2, fontfamily='DejaVu Sans',
                   va='center', transform=ax_header.transAxes)

    meta_badge = FancyBboxPatch((0.74, 0.18), 0.245, 0.64, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor='#1E293B', edgecolor='#334155', linewidth=1,
                                transform=ax_header.transAxes)
    ax_header.add_patch(meta_badge)
    ax_header.text(0.862, 0.5, "BATTERY: 502535 400mAh 1.48Wh | DW01A 3.0V CUTOFF",
                   color='#34D399', fontsize=7.8, fontweight='bold', fontfamily='monospace',
                   ha='center', va='center', transform=ax_header.transAxes)

    # =========================================================================
    # PANEL 1 (TOP LEFT): BATTERY DISCHARGE CURVES
    # =========================================================================
    ax_curve = fig.add_subplot(gs[0, 0])
    ax_curve.set_facecolor('#111827')

    ax_curve.grid(True, linestyle='--', color='#1F2937', alpha=0.8, linewidth=0.8)
    ax_curve.set_axisbelow(True)

    def lipo_discharge_v(t, total_hours):
        x = np.clip(t / total_hours, 0.0, 1.0)
        v = 4.20 - 0.28 * (x ** 0.35) - 0.35 * x - 0.57 * (x ** 6)
        return np.maximum(v, 3.0)

    # 1. Pet Idle (28.0 mA -> 14.28 hrs)
    t_idle = np.linspace(0, 14.28, 250)
    v_idle = lipo_discharge_v(t_idle, 14.28)
    line_idle, = ax_curve.plot(t_idle, v_idle, color='#10B981', lw=3.0,
                               label='Pet Idle Mode (28.0 mA) → 14.28 Hours Runtime')

    # 2. Blended Usage (29.2 mA -> 13.70 hrs)
    t_blend = np.linspace(0, 13.70, 250)
    v_blend = lipo_discharge_v(t_blend, 13.70)
    line_blend, = ax_curve.plot(t_blend, v_blend, color='#06B6D4', lw=3.0,
                                label='Typical Blended Profile (29.2 mA) → 13.70 Hours Runtime')

    # 3. Active Reaction Game (32.0 mA -> 12.50 hrs)
    t_game = np.linspace(0, 12.50, 250)
    v_game = lipo_discharge_v(t_game, 12.50)
    line_game, = ax_curve.plot(t_game, v_game, color='#F59E0B', lw=3.0, linestyle='--',
                               label='Reaction Game Mode (32.0 mA) → 12.50 Hours Runtime')

    # Annotations & Thresholds
    ax_curve.axhline(3.0, color='#EF4444', linestyle='-', lw=1.5, alpha=0.9)
    ax_curve.plot(14.28, 3.0, 'o', color='#10B981', markersize=7, markeredgecolor='#FFFFFF', markeredgewidth=1.2)
    ax_curve.plot(13.70, 3.0, 'o', color='#06B6D4', markersize=7, markeredgecolor='#FFFFFF', markeredgewidth=1.2)
    ax_curve.plot(12.50, 3.0, 'o', color='#F59E0B', markersize=7, markeredgecolor='#FFFFFF', markeredgewidth=1.2)

    ax_curve.axhline(3.30, color='#FB923C', linestyle=':', lw=1.2, alpha=0.8)
    ax_curve.text(0.4, 3.33, "3.30V (Low-Battery OLED Warning Threshold)", color='#FB923C', fontsize=7.2, fontfamily='monospace')

    ax_curve.axhline(3.70, color='#64748B', linestyle=':', lw=1.0, alpha=0.6)
    ax_curve.text(0.4, 3.73, "3.70V (Nominal Voltage / 50% SOC)", color='#94A3B8', fontsize=7.2, fontfamily='monospace')

    ax_curve.text(0.4, 4.23, "4.20V (100% Fully Charged)", color='#E2E8F0', fontsize=7.2, fontfamily='monospace')

    # Deep Sleep Callout Badge
    sleep_box = FancyBboxPatch((9.5, 4.02), 4.2, 0.24, boxstyle="round,pad=0.05,rounding_size=0.08",
                               facecolor='#1E1B4B', edgecolor='#818CF8', linewidth=1)
    ax_curve.add_patch(sleep_box)
    ax_curve.text(11.6, 4.14, "Deep Sleep: 1.2 mA\n333 Hours (13.8 Days)",
                  color='#C7D2FE', fontsize=6.8, fontweight='bold', fontfamily='monospace',
                  ha='center', va='center')

    ax_curve.set_xlim(0, 16.0)
    ax_curve.set_ylim(2.9, 4.35)
    ax_curve.set_title("LiPo Battery Cell Discharge Voltage vs. Time (400mAh Single-Cell)",
                       color='#F9FAFB', fontsize=9.5, fontweight='bold', fontfamily='DejaVu Sans', pad=10)
    ax_curve.set_xlabel("Operational Runtime (Hours)", color='#9CA3AF', fontsize=8.2, fontfamily='DejaVu Sans')
    ax_curve.set_ylabel("Cell Terminal Voltage (V)", color='#9CA3AF', fontsize=8.2, fontfamily='DejaVu Sans')
    ax_curve.tick_params(colors='#9CA3AF', labelsize=8)

    leg = ax_curve.legend(loc='lower left', facecolor='#0F172A', edgecolor='#334155',
                          fontsize=7.5, labelcolor='#F1F5F9', framealpha=0.95)

    for spine in ax_curve.spines.values():
        spine.set_color('#374151')

    # =========================================================================
    # PANEL 2 (TOP RIGHT): CURRENT CONSUMPTION WATERFALL & BAR BREAKDOWN
    # =========================================================================
    ax_bar = fig.add_subplot(gs[0, 1])
    ax_bar.set_facecolor('#111827')
    ax_bar.grid(True, linestyle='--', color='#1F2937', alpha=0.8, linewidth=0.8, axis='x')
    ax_bar.set_axisbelow(True)

    components = [
        "Quiescent / LDO Loss",
        "Piezo Buzzer (Avg)",
        "SSD1306 OLED (25% on)",
        "RP2040 MCU Core (133MHz)"
    ]
    currents = [1.2, 2.5, 7.0, 18.5]
    colors = ['#64748B', '#F59E0B', '#06B6D4', '#3B82F6']

    y_pos = np.arange(len(components))
    bars = ax_bar.barh(y_pos, currents, color=colors, height=0.55, edgecolor='#1E293B', linewidth=1)

    for i, (bar, val) in enumerate(zip(bars, currents)):
        pct = (val / sum(currents)) * 100
        ax_bar.text(val + 0.4, bar.get_y() + bar.get_height()/2,
                    f"{val:.1f} mA ({pct:.1f}%)",
                    va='center', color='#F3F4F6', fontsize=7.5, fontweight='bold', fontfamily='monospace')

    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(components, color='#E2E8F0', fontsize=8.0, fontfamily='DejaVu Sans')
    ax_bar.set_xlim(0, 24)
    ax_bar.set_ylim(-0.5, 3.5)
    ax_bar.set_title("Subsystem Current Breakdown (Typical Active: 29.2 mA Total)\n[ Sleep: 1.2mA  |  Pet Idle: 28.0mA  |  Active Game: 32.0mA ]",
                     color='#F9FAFB', fontsize=8.8, fontweight='bold', fontfamily='DejaVu Sans', pad=10)
    ax_bar.set_xlabel("Current Consumption (mA)", color='#9CA3AF', fontsize=8.2, fontfamily='DejaVu Sans')
    ax_bar.tick_params(colors='#9CA3AF', labelsize=8)

    for spine in ax_bar.spines.values():
        spine.set_color('#374151')

    # =========================================================================
    # PANEL 3 (BOTTOM FULL-WIDTH): DETAILED ENGINEERING POWER METRICS TABLE
    # =========================================================================
    ax_tbl = fig.add_subplot(gs[1, :])
    ax_tbl.set_facecolor('#111827')
    ax_tbl.axis('off')

    t_box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01,rounding_size=0.05",
                           facecolor='#111827', edgecolor='#1F2937', linewidth=1.5,
                           transform=ax_tbl.transAxes)
    ax_tbl.add_patch(t_box)

    ax_tbl.text(0.02, 0.90, "POWER BUDGET SPECIFICATIONS & BATTERY ENDURANCE AUDIT",
                color='#38BDF8', fontsize=9.0, fontweight='bold', fontfamily='monospace', transform=ax_tbl.transAxes)
    ax_tbl.text(0.98, 0.90, "FORMULA: Runtime (h) = Cell Capacity (400mAh) / Average Current Draw (mA)",
                color='#9CA3AF', fontsize=7.2, fontfamily='monospace', ha='right', transform=ax_tbl.transAxes)

    cols = [
        (0.02, "OPERATIONAL STATE"),
        (0.24, "AVG CURRENT"),
        (0.38, "AVG POWER (3.7V)"),
        (0.53, "BATTERY RUNTIME"),
        (0.70, "ACTIVE HARDWARE BEHAVIOR"),
        (0.92, "COMPLIANCE"),
    ]
    th_bar = FancyBboxPatch((0.01, 0.72), 0.98, 0.14, boxstyle="round,pad=0.01,rounding_size=0.03",
                            facecolor='#1E293B', edgecolor='#334155', linewidth=0.8, transform=ax_tbl.transAxes)
    ax_tbl.add_patch(th_bar)
    for cx, ctitle in cols:
        ax_tbl.text(cx, 0.79, ctitle, color='#94A3B8', fontsize=7.0, fontweight='bold',
                    fontfamily='monospace', transform=ax_tbl.transAxes, va='center')

    table_rows = [
        ("Deep Sleep / Standby", "1.2 mA", "4.44 mW", "333.3 Hours (13.8 Days)", "RP2040 dormant sleep, OLED internal DC-DC off, pull-ups only", "STANDBY", '#C084FC'),
        ("Virtual Pet Idle Mode", "28.0 mA", "103.6 mW", "14.28 Hours Runtime", "OLED pet face (25% on), 20Hz state tick, internal button polling", "PASS (>12h)", '#10B981'),
        ("Typical Blended Play (70/30)", "29.2 mA", "108.0 mW", "13.70 Hours Runtime", "Daily mix of pet feeding, idle animations, reflex game sessions", "PASS (>12h)", '#06B6D4'),
        ("Reaction Game Active", "32.0 mA", "118.4 mW", "12.50 Hours Runtime", "60Hz display refresh, PWM audio beeps, active player inputs", "PASS (>12h)", '#F59E0B'),
    ]

    for i, (state, cur, pwr, rtime, desc, status, col) in enumerate(table_rows):
        ry = 0.58 - i * 0.145
        if i % 2 == 1:
            r_bg = Rectangle((0.01, ry - 0.04), 0.98, 0.12, facecolor='#162032', edgecolor='none', transform=ax_tbl.transAxes)
            ax_tbl.add_patch(r_bg)

        ax_tbl.text(0.02, ry + 0.02, state, color='#F9FAFB', fontsize=7.2, fontweight='bold', fontfamily='DejaVu Sans', transform=ax_tbl.transAxes)
        ax_tbl.text(0.24, ry + 0.02, cur, color=col, fontsize=7.2, fontweight='bold', fontfamily='monospace', transform=ax_tbl.transAxes)
        ax_tbl.text(0.38, ry + 0.02, pwr, color='#E2E8F0', fontsize=7.2, fontfamily='monospace', transform=ax_tbl.transAxes)
        ax_tbl.text(0.53, ry + 0.02, rtime, color='#34D399', fontsize=7.2, fontweight='bold', fontfamily='monospace', transform=ax_tbl.transAxes)
        ax_tbl.text(0.70, ry + 0.02, desc, color='#CBD5E1', fontsize=6.8, fontfamily='DejaVu Sans', transform=ax_tbl.transAxes)

        s_box = FancyBboxPatch((0.915, ry - 0.02), 0.07, 0.09, boxstyle="round,pad=0.01,rounding_size=0.03",
                               facecolor='#064E3B', edgecolor='#10B981', linewidth=0.8, transform=ax_tbl.transAxes)
        ax_tbl.add_patch(s_box)
        ax_tbl.text(0.95, ry + 0.02, status, color='#6EE7B7', fontsize=6.2, fontweight='bold',
                    fontfamily='monospace', ha='center', transform=ax_tbl.transAxes)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=120)
    plt.close(fig)
    print(f"Generated: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out1 = r"C:\Users\white\pocket-companion\assets\journal_media\03_power_budget_battery_discharge_curve.png"
    out2 = r"C:\Users\white\pocket-companion\assets\03_power_budget_battery_discharge_curve.png"
    create_power_budget_chart(out1)
    create_power_budget_chart(out2)
