"""
Hardware Documentation Graphics Generator for Pocket Companion
(Hack Club Half-Life)
Asset 1: 01_system_architecture_block_diagram.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_block_diagram(output_path):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis('off')

    # Draw subtle background grid dots
    for x in range(5, 156, 5):
        for y in range(5, 86, 5):
            ax.plot(x, y, '.', color='#162032', markersize=2)

    # ------------------ HEADER ------------------
    # Top banner bar
    banner = FancyBboxPatch((4, 80.5), 152, 6.5, boxstyle="round,pad=0.2,rounding_size=0.8",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.5)
    ax.add_patch(banner)

    # Decorative chip badge
    badge = FancyBboxPatch((6, 81.8), 12, 3.8, boxstyle="round,pad=0.2,rounding_size=0.5",
                           facecolor='#0284C7', edgecolor='#38BDF8', linewidth=1.2)
    ax.add_patch(badge)
    ax.text(12, 83.7, "RP2040", color='#FFFFFF', fontsize=10, fontweight='bold',
            fontfamily='Segoe UI', ha='center', va='center')

    ax.text(20, 84.8, "POCKET COMPANION — SYSTEM ARCHITECTURE BLOCK DIAGRAM",
            color='#F9FAFB', fontsize=13, fontweight='bold', fontfamily='Segoe UI', va='center')
    ax.text(20, 82.2, "Hack Club Half-Life Hardware Architecture | Embedded CircuitPython Virtual Pet & Console",
            color='#9CA3AF', fontsize=8.5, fontfamily='Segoe UI', va='center')

    # Metadata badges on right
    meta_box = FancyBboxPatch((116, 81.5), 38, 4.5, boxstyle="round,pad=0.2,rounding_size=0.5",
                              facecolor='#1E293B', edgecolor='#334155', linewidth=1)
    ax.add_patch(meta_box)
    ax.text(135, 83.75, "REV v1.0  |  DEBANJAN BISWAS  |  OCT 2026",
            color='#38BDF8', fontsize=8, fontweight='bold', fontfamily='Consolas', ha='center', va='center')

    # Helper function for card blocks
    def draw_card(x, y, w, h, title, subtitle, header_color, body_color='#111827', border_color='#374151'):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.0",
                              facecolor=body_color, edgecolor=border_color, linewidth=1.5)
        ax.add_patch(card)
        # Header banner inside card
        header = FancyBboxPatch((x, y + h - 3.8), w, 3.8, boxstyle="round,pad=0.2,rounding_size=1.0",
                                facecolor=header_color, edgecolor='none')
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 1.8, title, color='#FFFFFF', fontsize=9.5,
                fontweight='bold', fontfamily='Segoe UI', ha='center', va='center')
        if subtitle:
            ax.text(x + w/2, y + h - 3.0, subtitle, color='#E2E8F0', fontsize=7,
                    fontfamily='Segoe UI', ha='center', va='center')
        return card

    # =========================================================================
    # 1. POWER SUBSYSTEM (LEFT COLUMN)
    # =========================================================================
    # Section title
    ax.text(22, 77.5, "[ POWER & BATTERY SUBSYSTEM ]", color='#F59E0B', fontsize=9,
            fontweight='bold', fontfamily='Consolas', ha='center')

    # Card A: LiPo Battery Pack
    draw_card(6, 61, 32, 14, "3.7V 400mAh LiPo Battery", "Model: 502535 | 1.48Wh Single-Cell",
              header_color='#D97706', border_color='#B45309')
    # Details
    ax.text(8, 57.5, "• Nominal: 3.7V | Max: 4.2V", color='#D1D5DB', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 55.0, "• Cutoff: 3.0V (DW01A Prot.)", color='#D1D5DB', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 52.5, "• Connector: JST-PH 2.0mm 2P", color='#D1D5DB', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 50.0, "• Discharge: 1C continuous", color='#9CA3AF', fontsize=7, fontfamily='Consolas')

    # Card B: TP4056 Charger & Protection
    draw_card(6, 30, 32, 17, "TP4056 USB-C Charger", "Charge Mgmt & Battery Protection",
              header_color='#B45309', border_color='#78350F')
    ax.text(8, 43.0, "• Input: 5V DC via USB Type-C", color='#D1D5DB', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 40.5, "• Charging CC/CV: 250mA (Rprog)", color='#D1D5DB', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 38.0, "• Protection IC: DW01A + 8205A", color='#D1D5DB', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 35.5, "• Low-Voltage Cutoff: 2.5V", color='#F87171', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 33.0, "• Dual LED: Red (Chg) / Blue (Done)", color='#60A5FA', fontsize=7.5, fontfamily='Segoe UI')

    # Card C: SPDT Power Switch
    draw_card(6, 12, 32, 13, "SPDT Slide Switch", "Hardware System Power ON/OFF",
              header_color='#475569', border_color='#64748B')
    ax.text(8, 21.0, "• Pin 1: NC (OFF state isolated)", color='#9CA3AF', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 18.5, "• Pin 2 (COM): VBUS_IN to RP2040", color='#FCD34D', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 16.0, "• Pin 3: VBAT from TP4056 OUT+", color='#F59E0B', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(8, 13.5, "• Rating: 50V 0.5A Mini Slide", color='#9CA3AF', fontsize=7, fontfamily='Consolas')

    # Power interconnect lines
    # Battery to TP4056
    ax.annotate('', xy=(22, 47), xytext=(22, 61),
                arrowprops=dict(arrowstyle="<->", color='#F59E0B', lw=2))
    ax.text(23, 54, "VBAT / BATT+-\n(JST-PH 2P)", color='#FCD34D', fontsize=7, fontfamily='Consolas', va='center')

    # TP4056 OUT+ to Switch
    ax.annotate('', xy=(22, 25), xytext=(22, 30),
                arrowprops=dict(arrowstyle="->", color='#F59E0B', lw=2))
    ax.text(23, 27.5, "OUT+ (VBAT)", color='#FCD34D', fontsize=7, fontfamily='Consolas', va='center')

    # Switch to RP2040 VBUS_IN (horizontal long routing to center)
    ax.plot([38, 48, 48], [18.5, 18.5, 32], color='#EF4444', lw=2.5)
    ax.annotate('', xy=(50, 32), xytext=(48, 32),
                arrowprops=dict(arrowstyle="-|>", color='#EF4444', lw=2.5, mutation_scale=12))
    ax.text(40, 20, "VBUS_IN (+3.7V - 5V)", color='#FCA5A5', fontsize=7.5, fontweight='bold', fontfamily='Consolas')

    # =========================================================================
    # 2. MICROCONTROLLER CORE (CENTER COLUMN)
    # =========================================================================
    ax.text(80, 77.5, "[ CORE PROCESSING UNIT ]", color='#38BDF8', fontsize=9,
            fontweight='bold', fontfamily='Consolas', ha='center')

    # Master RP2040 Card
    draw_card(50, 10, 60, 65, "Waveshare RP2040-Zero",
              "Dual ARM Cortex-M0+ @ 133MHz | 2MB Flash | Ultra-Compact SMD/DIP",
              header_color='#0284C7', border_color='#0284C7', body_color='#0F172A')

    # Sub-block inside RP2040: Silicon Architecture
    mcu_sub = FancyBboxPatch((53, 53), 54, 18, boxstyle="round,pad=0.2,rounding_size=0.6",
                             facecolor='#1E293B', edgecolor='#38BDF8', linewidth=1)
    ax.add_patch(mcu_sub)
    ax.text(80, 68.5, "Raspberry Pi RP2040 Silicon", color='#38BDF8', fontsize=9,
            fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(56, 65.5, "• 2x ARM Cortex-M0+ Cores @ 133MHz", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 63.0, "• 264KB Multi-Bank SRAM (6 independent banks)", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 60.5, "• 2MB High-Speed QSPI NOR Flash (W25Q16JV)", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 58.0, "• 2x UART, 2x SPI, 2x I2C, 16x PWM Channels", color='#94A3B8', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 55.5, "• 8x Programmable I/O (PIO) State Machines", color='#94A3B8', fontsize=7.5, fontfamily='Segoe UI')

    # Sub-block: Firmware & Environment
    fw_sub = FancyBboxPatch((53, 38.5), 54, 12.5, boxstyle="round,pad=0.2,rounding_size=0.6",
                            facecolor='#1E293B', edgecolor='#10B981', linewidth=1)
    ax.add_patch(fw_sub)
    ax.text(80, 48.5, "CircuitPython 9.x Runtime Engine", color='#34D399', fontsize=8.5,
            fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(56, 45.5, "• code.py Main Loop: Mode State Machine (Pet / Reflex / Timer)", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 43.0, "• Frame Driver: adafruit_ssd1306 Framebuffer over I2C", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 40.5, "• Audio Engine: pwmio.PWMOut dynamic frequency synthesis", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')

    # Sub-block: On-board Power & Peripherals
    pwr_sub = FancyBboxPatch((53, 23.5), 54, 13, boxstyle="round,pad=0.2,rounding_size=0.6",
                             facecolor='#1E293B', edgecolor='#F59E0B', linewidth=1)
    ax.add_patch(pwr_sub)
    ax.text(80, 34.0, "On-Board Power Regulation & IO", color='#FBBF24', fontsize=8.5,
            fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(56, 31.0, "• ME6211 / RT9193 3.3V Low-Dropout LDO Regulator (500mA)", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 28.5, "• Type-C USB Port: Native USB 1.1 Bootloader / REPL", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')
    ax.text(56, 26.0, "• WS2812 RGB LED (GP16) & BOOT/RESET tactile buttons", color='#E2E8F0', fontsize=7.5, fontfamily='Segoe UI')

    # Pin badges on RP2040 right border
    pins = [
        (72, "GP0 / I2C0_SDA", '#06B6D4'),
        (68, "GP1 / I2C0_SCL", '#06B6D4'),
        (51, "GP5 / PWM2B", '#EAB308'),
        (25, "GP2 / BTN_LEFT", '#10B981'),
        (21, "GP3 / BTN_ACTION", '#10B981'),
        (17, "GP4 / BTN_RIGHT", '#10B981'),
        (13, "+3V3 Rail Out", '#FB923C'),
    ]
    for py, label, col in pins:
        p_badge = FancyBboxPatch((102, py - 1.2), 18, 2.4, boxstyle="round,pad=0.1,rounding_size=0.4",
                                 facecolor='#0F172A', edgecolor=col, linewidth=1.2)
        ax.add_patch(p_badge)
        ax.text(111, py, label, color=col, fontsize=6.8, fontweight='bold',
                fontfamily='Consolas', ha='center', va='center')

    # =========================================================================
    # 3. PERIPHERALS SUBSYSTEM (RIGHT COLUMN)
    # =========================================================================
    ax.text(141, 77.5, "[ HARDWARE PERIPHERALS ]", color='#A78BFA', fontsize=9,
            fontweight='bold', fontfamily='Consolas', ha='center')

    # Card 1: 0.96" SSD1306 OLED Display
    draw_card(122, 60, 34, 15, "0.96\" SSD1306 OLED Display", "128x64 Monochrome Graphic I2C",
              header_color='#0284C7', border_color='#0369A1')
    ax.text(124, 57.0, "• Resolution: 128 x 64 pixels (Blue phosphor)", color='#D1D5DB', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 54.5, "• Interface: I2C (Address: 0x3C @ 400kHz)", color='#38BDF8', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 52.0, "• Internal Charge Pump: 7.5V boost from 3.3V", color='#D1D5DB', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 49.5, "• Current: ~7mA (25% on) / ~20mA (100% on)", color='#9CA3AF', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 47.0, "• Pins: VCC (+3.3V), GND, SCL, SDA", color='#67E8F9', fontsize=7.2, fontfamily='Consolas')

    # Card 2: Passive Piezo Buzzer
    draw_card(122, 42, 34, 14, "Passive Piezo Buzzer", "Audio Tones & Haptic Sound Fx",
              header_color='#CA8A04', border_color='#A16207')
    ax.text(124, 38.5, "• Transducer: 3V-5V Passive Piezo Disc", color='#D1D5DB', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 36.0, "• Drive: PWM Square Wave via GP5", color='#FACC15', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 33.5, "• Freq: 440Hz - 2000Hz (Buzzer Chimes)", color='#D1D5DB', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 31.0, "• Peak Current: ~4mA during active chirps", color='#9CA3AF', fontsize=7.2, fontfamily='Segoe UI')
    ax.text(124, 28.5, "• Zero current consumption when silent", color='#34D399', fontsize=7.2, fontfamily='Segoe UI')

    # Card 3: 3x Tactile Push Buttons
    draw_card(122, 10, 34, 28, "3x Tactile Push Buttons", "User Input Navigation & Action",
              header_color='#059669', border_color='#047857')
    # SW1
    sw1_box = FancyBboxPatch((124, 26.5), 30, 4.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#1E293B', edgecolor='#10B981', linewidth=0.8)
    ax.add_patch(sw1_box)
    ax.text(125.5, 29.2, "SW1 [Left Button] → GP2", color='#6EE7B7', fontsize=7.2, fontweight='bold', fontfamily='Consolas')
    ax.text(125.5, 27.2, "Navigates left / previous mode | Active LOW", color='#9CA3AF', fontsize=6.5, fontfamily='Segoe UI')

    # SW2
    sw2_box = FancyBboxPatch((124, 21.0), 30, 4.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#1E293B', edgecolor='#10B981', linewidth=0.8)
    ax.add_patch(sw2_box)
    ax.text(125.5, 23.7, "SW2 [Action Button] → GP3", color='#6EE7B7', fontsize=7.2, fontweight='bold', fontfamily='Consolas')
    ax.text(125.5, 21.7, "Interact / Feed pet / Game trigger | Active LOW", color='#9CA3AF', fontsize=6.5, fontfamily='Segoe UI')

    # SW3
    sw3_box = FancyBboxPatch((124, 15.5), 30, 4.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#1E293B', edgecolor='#10B981', linewidth=0.8)
    ax.add_patch(sw3_box)
    ax.text(125.5, 18.2, "SW3 [Right Button] → GP4", color='#6EE7B7', fontsize=7.2, fontweight='bold', fontfamily='Consolas')
    ax.text(125.5, 16.2, "Navigates right / next mode | Active LOW", color='#9CA3AF', fontsize=6.5, fontfamily='Segoe UI')

    ax.text(125.5, 12.5, "• Internal Pull-Up Resistors (~50kΩ enabled in SW)", color='#D1D5DB', fontsize=6.8, fontfamily='Segoe UI')
    ax.text(125.5, 10.8, "• Active LOW topology (Switch shorts pin to GND)", color='#9CA3AF', fontsize=6.8, fontfamily='Segoe UI')

    # =========================================================================
    # ROUTING SIGNAL TRACES (BUSES & ARROWS)
    # =========================================================================
    # 1. I2C Bus to OLED
    ax.plot([110, 116, 116, 122], [72, 72, 69, 69], color='#06B6D4', lw=2)
    ax.plot([110, 118, 118, 122], [68, 68, 66, 66], color='#06B6D4', lw=2)
    ax.annotate('', xy=(122, 69), xytext=(120, 69),
                arrowprops=dict(arrowstyle="-|>", color='#06B6D4', lw=2, mutation_scale=10))
    ax.annotate('', xy=(122, 66), xytext=(120, 66),
                arrowprops=dict(arrowstyle="-|>", color='#06B6D4', lw=2, mutation_scale=10))
    ax.text(115, 73.5, "I2C SDA (GP0)", color='#67E8F9', fontsize=6.8, fontfamily='Consolas')
    ax.text(115, 64.5, "I2C SCL (GP1)", color='#67E8F9', fontsize=6.8, fontfamily='Consolas')

    # 2. PWM to Buzzer
    ax.plot([110, 122], [51, 51], color='#EAB308', lw=2)
    ax.annotate('', xy=(122, 51), xytext=(119, 51),
                arrowprops=dict(arrowstyle="-|>", color='#EAB308', lw=2, mutation_scale=10))
    ax.text(112, 52.2, "PWM Audio (GP5)", color='#FDE047', fontsize=6.8, fontfamily='Consolas')

    # 3. Button inputs to RP2040
    ax.plot([124, 116, 116, 110], [28.5, 28.5, 25, 25], color='#10B981', lw=2)
    ax.plot([124, 118, 118, 110], [23.0, 23.0, 21, 21], color='#10B981', lw=2)
    ax.plot([124, 120, 120, 110], [17.5, 17.5, 17, 17], color='#10B981', lw=2)
    ax.annotate('', xy=(110, 25), xytext=(112, 25),
                arrowprops=dict(arrowstyle="-|>", color='#10B981', lw=2, mutation_scale=10))
    ax.annotate('', xy=(110, 21), xytext=(112, 21),
                arrowprops=dict(arrowstyle="-|>", color='#10B981', lw=2, mutation_scale=10))
    ax.annotate('', xy=(110, 17), xytext=(112, 17),
                arrowprops=dict(arrowstyle="-|>", color='#10B981', lw=2, mutation_scale=10))

    # =========================================================================
    # FOOTER: SIGNAL LEGEND & OPERATING METRICS
    # =========================================================================
    footer = FancyBboxPatch((4, 2.5), 152, 5.5, boxstyle="round,pad=0.2,rounding_size=0.6",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.2)
    ax.add_patch(footer)

    # Legend items
    ax.text(7, 5.2, "SIGNAL LEGEND:", color='#9CA3AF', fontsize=7.5, fontweight='bold', fontfamily='Consolas', va='center')

    # Power rail
    ax.plot([25, 30], [5.2, 5.2], color='#EF4444', lw=2.5)
    ax.text(31, 5.2, "Power (VBUS/3V3)", color='#E2E8F0', fontsize=7.2, fontfamily='Segoe UI', va='center')

    # I2C
    ax.plot([50, 55], [5.2, 5.2], color='#06B6D4', lw=2.5)
    ax.text(56, 5.2, "I2C Bus (Fast 400kHz)", color='#E2E8F0', fontsize=7.2, fontfamily='Segoe UI', va='center')

    # GPIO
    ax.plot([76, 81], [5.2, 5.2], color='#10B981', lw=2.5)
    ax.text(82, 5.2, "Active-LOW Digital Inputs", color='#E2E8F0', fontsize=7.2, fontfamily='Segoe UI', va='center')

    # PWM
    ax.plot([105, 110], [5.2, 5.2], color='#EAB308', lw=2.5)
    ax.text(111, 5.2, "PWM Audio Output", color='#E2E8F0', fontsize=7.2, fontfamily='Segoe UI', va='center')

    # Battery Life Note
    ax.text(152, 5.2, "RUNTIME: 12.5h - 14.3h (400mAh LiPo)", color='#34D399', fontsize=7.5,
            fontweight='bold', fontfamily='Consolas', ha='right', va='center')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=120)
    plt.close(fig)
    print(f"Generated: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out = r"C:\Users\white\pocket-companion\assets\journal_media\01_system_architecture_block_diagram.png"
    create_block_diagram(out)
