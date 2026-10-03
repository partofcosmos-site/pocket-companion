"""
Hardware Documentation Graphics Generator for Pocket Companion
(Hack Club Half-Life)
Asset 1: 01_system_architecture_block_diagram.png
Publication-Grade System Architecture Block Diagram
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

def create_block_diagram(output_path):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis('off')

    # Background ESD dot grid (strictly low zorder)
    for x in range(4, 158, 4):
        for y in range(4, 88, 4):
            ax.plot(x, y, '.', color='#162032', markersize=1.8, zorder=1)

    # ------------------ HEADER ------------------
    banner = FancyBboxPatch((4, 81), 152, 6.4, boxstyle="round,pad=0.2,rounding_size=0.8",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.5, zorder=2)
    ax.add_patch(banner)

    badge = FancyBboxPatch((6, 82.2), 12, 3.8, boxstyle="round,pad=0.2,rounding_size=0.5",
                           facecolor='#0284C7', edgecolor='#38BDF8', linewidth=1.2, zorder=3)
    ax.add_patch(badge)
    ax.text(12, 84.1, "RP2040", color='#FFFFFF', fontsize=9.5, fontweight='bold',
            fontfamily='DejaVu Sans', ha='center', va='center', zorder=4)

    ax.text(20, 85.0, "POCKET COMPANION — SYSTEM ARCHITECTURE BLOCK DIAGRAM",
            color='#F9FAFB', fontsize=12.2, fontweight='bold', fontfamily='DejaVu Sans', va='center', zorder=4)
    ax.text(20, 82.5, "Hack Club Half-Life Hardware Architecture | Embedded CircuitPython Virtual Pet & Console",
            color='#9CA3AF', fontsize=8.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    meta_box = FancyBboxPatch((114, 81.8), 40, 4.4, boxstyle="round,pad=0.2,rounding_size=0.5",
                              facecolor='#1E293B', edgecolor='#334155', linewidth=1, zorder=3)
    ax.add_patch(meta_box)
    ax.text(134, 84.0, "REV v1.0 | DEBANJAN BISWAS | OCT 2026",
            color='#38BDF8', fontsize=7.8, fontweight='bold', fontfamily='monospace', ha='center', va='center', zorder=4)

    # Helper function for card blocks (fully opaque z-order)
    def draw_card(x, y, w, h, title, subtitle, header_color, body_color='#111827', border_color='#374151'):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.0",
                              facecolor=body_color, edgecolor=border_color, linewidth=1.5, zorder=2)
        ax.add_patch(card)
        header = FancyBboxPatch((x, y + h - 3.8), w, 3.8, boxstyle="round,pad=0.2,rounding_size=1.0",
                                facecolor=header_color, edgecolor='none', zorder=3)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 1.8, title, color='#FFFFFF', fontsize=9.2,
                fontweight='bold', fontfamily='DejaVu Sans', ha='center', va='center', zorder=4)
        if subtitle:
            ax.text(x + w/2, y + h - 3.0, subtitle, color='#E2E8F0', fontsize=6.8,
                    fontfamily='DejaVu Sans', ha='center', va='center', zorder=4)
        return card

    # =========================================================================
    # 1. POWER SUBSYSTEM (LEFT COLUMN)
    # =========================================================================
    ax.text(22, 77.5, "[ POWER & BATTERY SUBSYSTEM ]", color='#F59E0B', fontsize=8.8,
            fontweight='bold', fontfamily='monospace', ha='center', zorder=4)

    # Card A: LiPo Battery Pack (y: 62 to 75, height 13)
    draw_card(6, 62, 32, 13, "3.7V 400mAh LiPo Battery", "Model: 502535 | 1.48Wh Single-Cell",
              header_color='#D97706', border_color='#B45309')
    ax.text(8, 68.2, "• Nominal: 3.7V | Max: 4.2V", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 65.8, "• Cutoff: 3.0V (DW01A Prot.)", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 63.4, "• Connector: JST-PH 2.0mm 2P", color='#FCD34D', fontsize=7.2, fontfamily='monospace', zorder=4)

    # Arrow A -> B: Between y=62 and y=57
    ax.annotate('', xy=(22, 57.5), xytext=(22, 61.5),
                arrowprops=dict(arrowstyle="<->", color='#F59E0B', lw=2), zorder=3)
    ax.text(23.5, 59.5, "VBAT / BATT+-", color='#FCD34D', fontsize=6.8, fontfamily='monospace', va='center', zorder=4)

    # Card B: TP4056 Charger & Protection (y: 37 to 57, height 20)
    draw_card(6, 37, 32, 20, "TP4056 USB-C Charger", "Charge Mgmt & Battery Protection",
              header_color='#B45309', border_color='#78350F')
    ax.text(8, 51.0, "• Input: 5V DC via USB Type-C", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 48.4, "• Charging CC/CV: 250mA (Rprog)", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 45.8, "• Protection IC: DW01A + 8205A", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 43.2, "• Low-Voltage Cutoff: 2.5V", color='#F87171', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 40.6, "• Dual LED: Red (Chg) / Blue (Done)", color='#60A5FA', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 38.0, "• Solder Pads: B+, B-, OUT+, OUT-", color='#CBD5E1', fontsize=7.2, fontfamily='monospace', zorder=4)

    # Arrow B -> C: Between y=37 and y=32
    ax.annotate('', xy=(22, 32.5), xytext=(22, 36.5),
                arrowprops=dict(arrowstyle="->", color='#F59E0B', lw=2), zorder=3)
    ax.text(23.5, 34.5, "OUT+ (VBAT)", color='#FCD34D', fontsize=6.8, fontfamily='monospace', va='center', zorder=4)

    # Card C: SPDT Power Switch (y: 12 to 32, height 20)
    draw_card(6, 12, 32, 20, "SPDT Slide Switch", "Hardware System Power ON/OFF",
              header_color='#475569', border_color='#64748B')
    ax.text(8, 25.8, "• Pin 1: NC (OFF state isolated)", color='#9CA3AF', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 23.2, "• Pin 2 (COM): VBUS_IN to RP2040", color='#FCD34D', fontsize=7.2, fontfamily='monospace', zorder=4)
    ax.text(8, 20.6, "• Pin 3: VBAT from TP4056 OUT+", color='#F59E0B', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(8, 18.0, "• Rating: 50V 0.5A Mini Slide", color='#9CA3AF', fontsize=7.0, fontfamily='monospace', zorder=4)
    ax.text(8, 15.4, "• Model: SS-12D00G3 (LCSC: C432128)", color='#CBD5E1', fontsize=7.0, fontfamily='monospace', zorder=4)

    # Power interconnect from Switch to RP2040 Core
    ax.plot([38, 45, 45], [23.2, 23.2, 32], color='#EF4444', lw=2.2, zorder=3)
    ax.annotate('', xy=(48, 32), xytext=(45, 32),
                arrowprops=dict(arrowstyle="-|>", color='#EF4444', lw=2.2, mutation_scale=12), zorder=3)
    ax.text(39, 25.0, "VBUS_IN (+3.7V - 5V)", color='#FCA5A5', fontsize=7.0, fontweight='bold', fontfamily='monospace', zorder=4)

    # =========================================================================
    # 2. MICROCONTROLLER CORE (CENTER COLUMN)
    # =========================================================================
    ax.text(77, 77.5, "[ CORE PROCESSING UNIT ]", color='#38BDF8', fontsize=8.8,
            fontweight='bold', fontfamily='monospace', ha='center', zorder=4)

    # Master RP2040 Card (x: 48 to 106, width 58)
    draw_card(48, 10, 58, 65, "Waveshare RP2040-Zero",
              "Dual ARM Cortex-M0+ @ 133MHz | 2MB Flash | Ultra-Compact SMD/DIP",
              header_color='#0284C7', border_color='#0284C7', body_color='#0F172A')

    # Sub-block inside RP2040: Silicon Architecture
    mcu_sub = FancyBboxPatch((50.5, 52), 44, 18, boxstyle="round,pad=0.2,rounding_size=0.6",
                             facecolor='#1E293B', edgecolor='#38BDF8', linewidth=1, zorder=3)
    ax.add_patch(mcu_sub)
    ax.text(72.5, 67.5, "Raspberry Pi RP2040 Silicon", color='#38BDF8', fontsize=8.8,
            fontweight='bold', fontfamily='DejaVu Sans', ha='center', zorder=4)
    ax.text(53, 64.5, "• 2x ARM Cortex-M0+ Cores @ 133MHz", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 62.0, "• 264KB Multi-Bank SRAM (6 banks)", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 59.5, "• 2MB High-Speed QSPI NOR Flash", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 57.0, "• 2x UART, 2x SPI, 2x I2C, 16x PWM", color='#94A3B8', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 54.5, "• 8x Programmable I/O (PIO) Machines", color='#94A3B8', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)

    # Sub-block: Firmware & Environment
    fw_sub = FancyBboxPatch((50.5, 35.5), 44, 14.5, boxstyle="round,pad=0.2,rounding_size=0.6",
                            facecolor='#1E293B', edgecolor='#10B981', linewidth=1, zorder=3)
    ax.add_patch(fw_sub)
    ax.text(72.5, 47.5, "CircuitPython 9.x Runtime", color='#34D399', fontsize=8.5,
            fontweight='bold', fontfamily='DejaVu Sans', ha='center', zorder=4)
    ax.text(53, 44.5, "• code.py: Mode State Machine (Pet/Game)", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 42.0, "• Frame Driver: adafruit_ssd1306 (I2C Fast)", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 39.5, "• Audio Engine: pwmio.PWMOut dynamic sound", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 37.0, "• Non-blocking monotonic_ns() event loop", color='#38BDF8', fontsize=7.0, fontfamily='monospace', zorder=4)

    # Sub-block: Power & Onboard IO
    pwr_sub = FancyBboxPatch((50.5, 14.5), 44, 19, boxstyle="round,pad=0.2,rounding_size=0.6",
                             facecolor='#1E293B', edgecolor='#F59E0B', linewidth=1, zorder=3)
    ax.add_patch(pwr_sub)
    ax.text(72.5, 30.5, "On-Board Power & IO", color='#FCD34D', fontsize=8.5,
            fontweight='bold', fontfamily='DejaVu Sans', ha='center', zorder=4)
    ax.text(53, 27.5, "• ME6211 / RT9193 3.3V LDO (500mA)", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 25.0, "• Type-C USB Port: Native USB REPL", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 22.5, "• WS2812 RGB LED & BOOT/RESET buttons", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 20.0, "• Solid Copper Ground Plane Reference", color='#94A3B8', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(53, 17.5, "• ESD Protection Clamping Diodes", color='#94A3B8', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)

    # GPIO Pin Breakout Blocks on Right Edge of RP2040 (x: 95 to 110)
    pins = [
        ("GP0 / I2C0_SDA", 70.0, '#06B6D4'),
        ("GP1 / I2C0_SCL", 65.0, '#06B6D4'),
        ("GP5 / PWM2B", 51.0, '#EAB308'),
        ("GP2 / BTN_LEFT", 25.0, '#10B981'),
        ("GP3 / BTN_ACTION", 21.0, '#10B981'),
        ("GP4 / BTN_RIGHT", 17.0, '#10B981'),
        ("+3V3 Rail Out", 13.0, '#F97316'),
    ]

    for p_name, py, col in pins:
        p_box = FancyBboxPatch((95, py - 1.6), 16, 3.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                               facecolor='#0F172A', edgecolor=col, linewidth=1.2, zorder=3)
        ax.add_patch(p_box)
        ax.text(103, py, p_name, color=col, fontsize=6.2, fontweight='bold',
                fontfamily='monospace', ha='center', va='center', zorder=4)
        ax.plot([90, 95], [py, py], color=col, lw=1.5, zorder=3)

    # =========================================================================
    # 3. PERIPHERALS & INTERFACES (RIGHT COLUMN)
    # =========================================================================
    ax.text(139, 77.5, "[ HARDWARE PERIPHERALS ]", color='#10B981', fontsize=8.8,
            fontweight='bold', fontfamily='monospace', ha='center', zorder=4)

    # Card 1: 0.96" OLED Display (y: 59 to 75, height 16)
    draw_card(122, 59, 34, 16, "0.96\" SSD1306 OLED Display", "128x64 Monochrome Graphic I2C",
              header_color='#0284C7', border_color='#0369A1')
    ax.text(124, 69.8, "• Resolution: 128 x 64 pixels (Blue phosphor)", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 67.5, "• Interface: I2C (Address: 0x3C @ 400kHz)", color='#38BDF8', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 65.2, "• Internal Charge Pump: 7.5V boost from 3.3V", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 62.9, "• Current: ~7mA (25% on) / ~20mA (100% on)", color='#9CA3AF', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 60.6, "• Pins: VCC (+3.3V), GND, SCL, SDA", color='#67E8F9', fontsize=7.2, fontfamily='monospace', zorder=4)

    # Card 2: Passive Piezo Buzzer (y: 40.5 to 57, height 16.5)
    draw_card(122, 40.5, 34, 16.5, "Passive Piezo Buzzer", "Audio Tones & Haptic Sound Fx",
              header_color='#CA8A04', border_color='#A16207')
    ax.text(124, 51.3, "• Transducer: 3V-5V Passive Piezo Disc", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 49.0, "• Drive: PWM Square Wave via GP5", color='#FACC15', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 46.7, "• Freq: 440Hz - 2000Hz (Buzzer Chimes)", color='#D1D5DB', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 44.4, "• Peak Current: ~4mA during active chirps", color='#9CA3AF', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)
    ax.text(124, 42.1, "• Zero current consumption when silent", color='#34D399', fontsize=7.2, fontfamily='DejaVu Sans', zorder=4)

    # Card 3: 3x Tactile Push Buttons (y: 10 to 38.5, height 28.5)
    draw_card(122, 10, 34, 28.5, "3x Tactile Push Buttons", "User Input Navigation & Action",
              header_color='#059669', border_color='#047857')
    # SW1
    sw1_box = FancyBboxPatch((124, 27.2), 30, 4.3, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#1E293B', edgecolor='#10B981', linewidth=0.8, zorder=3)
    ax.add_patch(sw1_box)
    ax.text(125.5, 29.8, "SW1 [Left Button] → GP2", color='#6EE7B7', fontsize=7.2, fontweight='bold', fontfamily='monospace', zorder=4)
    ax.text(125.5, 28.0, "Navigates left / previous mode | Active LOW", color='#9CA3AF', fontsize=6.5, fontfamily='DejaVu Sans', zorder=4)

    # SW2
    sw2_box = FancyBboxPatch((124, 21.7), 30, 4.3, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#1E293B', edgecolor='#10B981', linewidth=0.8, zorder=3)
    ax.add_patch(sw2_box)
    ax.text(125.5, 24.3, "SW2 [Action Button] → GP3", color='#6EE7B7', fontsize=7.2, fontweight='bold', fontfamily='monospace', zorder=4)
    ax.text(125.5, 22.5, "Interact / Feed pet / Game trigger | Active LOW", color='#9CA3AF', fontsize=6.5, fontfamily='DejaVu Sans', zorder=4)

    # SW3
    sw3_box = FancyBboxPatch((124, 16.2), 30, 4.3, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#1E293B', edgecolor='#10B981', linewidth=0.8, zorder=3)
    ax.add_patch(sw3_box)
    ax.text(125.5, 18.8, "SW3 [Right Button] → GP4", color='#6EE7B7', fontsize=7.2, fontweight='bold', fontfamily='monospace', zorder=4)
    ax.text(125.5, 17.0, "Navigates right / next mode | Active LOW", color='#9CA3AF', fontsize=6.5, fontfamily='DejaVu Sans', zorder=4)

    ax.text(125.5, 13.5, "• Internal Pull-Up Resistors (50k enabled in SW)", color='#D1D5DB', fontsize=6.8, fontfamily='DejaVu Sans', zorder=4)
    ax.text(125.5, 11.5, "• Active LOW topology (Switch shorts pin to GND)", color='#9CA3AF', fontsize=6.8, fontfamily='DejaVu Sans', zorder=4)

    # =========================================================================
    # ROUTING SIGNAL TRACES (BUSES & ARROWS)
    # =========================================================================
    # 1. I2C Bus to OLED
    ax.plot([111, 116, 116, 122], [70, 70, 70, 70], color='#06B6D4', lw=2, zorder=3)
    ax.plot([111, 117, 117, 122], [65, 65, 65, 65], color='#06B6D4', lw=2, zorder=3)
    ax.annotate('', xy=(122, 70), xytext=(120, 70),
                arrowprops=dict(arrowstyle="-|>", color='#06B6D4', lw=2, mutation_scale=10), zorder=3)
    ax.annotate('', xy=(122, 65), xytext=(120, 65),
                arrowprops=dict(arrowstyle="-|>", color='#06B6D4', lw=2, mutation_scale=10), zorder=3)
    ax.text(116.5, 71.8, "I2C SDA (GP0)", color='#67E8F9', fontsize=6.5, fontfamily='monospace', ha='center', zorder=4)
    ax.text(116.5, 63.2, "I2C SCL (GP1)", color='#67E8F9', fontsize=6.5, fontfamily='monospace', ha='center', zorder=4)

    # 2. PWM to Buzzer
    ax.plot([111, 122], [51, 51], color='#EAB308', lw=2, zorder=3)
    ax.annotate('', xy=(122, 51), xytext=(119, 51),
                arrowprops=dict(arrowstyle="-|>", color='#EAB308', lw=2, mutation_scale=10), zorder=3)
    ax.text(116.5, 52.6, "PWM Audio (GP5)", color='#FDE047', fontsize=6.5, fontfamily='monospace', ha='center', zorder=4)

    # 3. Button inputs to RP2040
    ax.plot([124, 117, 117, 111], [29.3, 29.3, 25, 25], color='#10B981', lw=2, zorder=3)
    ax.plot([124, 118, 118, 111], [23.8, 23.8, 21, 21], color='#10B981', lw=2, zorder=3)
    ax.plot([124, 119, 119, 111], [18.3, 18.3, 17, 17], color='#10B981', lw=2, zorder=3)
    ax.annotate('', xy=(111, 25), xytext=(113, 25),
                arrowprops=dict(arrowstyle="-|>", color='#10B981', lw=2, mutation_scale=10), zorder=3)
    ax.annotate('', xy=(111, 21), xytext=(113, 21),
                arrowprops=dict(arrowstyle="-|>", color='#10B981', lw=2, mutation_scale=10), zorder=3)
    ax.annotate('', xy=(111, 17), xytext=(113, 17),
                arrowprops=dict(arrowstyle="-|>", color='#10B981', lw=2, mutation_scale=10), zorder=3)

    # =========================================================================
    # FOOTER: SIGNAL LEGEND & OPERATING METRICS
    # =========================================================================
    footer = FancyBboxPatch((4, 2.5), 152, 5.5, boxstyle="round,pad=0.2,rounding_size=0.6",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.2, zorder=2)
    ax.add_patch(footer)

    ax.text(7, 5.2, "SIGNAL LEGEND:", color='#9CA3AF', fontsize=7.5, fontweight='bold', fontfamily='monospace', va='center', zorder=4)

    ax.plot([25, 30], [5.2, 5.2], color='#EF4444', lw=2.5, zorder=3)
    ax.text(31, 5.2, "Power (VBUS/3V3)", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    ax.plot([50, 55], [5.2, 5.2], color='#06B6D4', lw=2.5, zorder=3)
    ax.text(56, 5.2, "I2C Bus (Fast 400kHz)", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    ax.plot([76, 81], [5.2, 5.2], color='#10B981', lw=2.5, zorder=3)
    ax.text(82, 5.2, "Active-LOW Digital Inputs", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    ax.plot([105, 110], [5.2, 5.2], color='#EAB308', lw=2.5, zorder=3)
    ax.text(111, 5.2, "PWM Audio Output", color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    ax.text(152, 5.2, "RUNTIME: 12.5h - 14.3h (400mAh LiPo)", color='#34D399', fontsize=7.5,
            fontweight='bold', fontfamily='monospace', ha='right', va='center', zorder=4)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=120)
    plt.close(fig)
    print(f"Generated: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out1 = r"C:\Users\white\pocket-companion\assets\journal_media\01_system_architecture_block_diagram.png"
    out2 = r"C:\Users\white\pocket-companion\assets\01_system_architecture_block_diagram.png"
    create_block_diagram(out1)
    create_block_diagram(out2)
