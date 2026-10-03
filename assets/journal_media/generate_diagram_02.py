"""
Hardware Documentation Graphics Generator for Pocket Companion
(Hack Club Half-Life)
Asset 2: 02_rp2040_pinout_peripheral_matrix.png
High-Precision Waveshare RP2040-Zero Pinout & Peripheral Voltage Matrix
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

def create_pinout_matrix(output_path):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis('off')

    # Draw subtle background grid dots (low z-order so cards cover them completely)
    for x in range(4, 158, 4):
        for y in range(4, 88, 4):
            ax.plot(x, y, '.', color='#162032', markersize=1.8, zorder=1)

    # ------------------ HEADER ------------------
    banner = FancyBboxPatch((4, 81), 152, 6.4, boxstyle="round,pad=0.2,rounding_size=0.8",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.5, zorder=2)
    ax.add_patch(banner)

    badge = FancyBboxPatch((6, 82.2), 12, 3.8, boxstyle="round,pad=0.2,rounding_size=0.5",
                           facecolor='#7C3AED', edgecolor='#A78BFA', linewidth=1.2, zorder=3)
    ax.add_patch(badge)
    ax.text(12, 84.1, "PINOUT", color='#FFFFFF', fontsize=9.5, fontweight='bold',
            fontfamily='DejaVu Sans', ha='center', va='center', zorder=4)

    ax.text(20, 85.0, "WAVESHARE RP2040-ZERO — PINOUT & PERIPHERAL VOLTAGE MATRIX",
            color='#F9FAFB', fontsize=12.2, fontweight='bold', fontfamily='DejaVu Sans', va='center', zorder=4)
    ax.text(20, 82.5, "Pocket Companion Verified Pinout | Authentic Physical Alignment | 3.3V LVCMOS Logic Domain",
            color='#9CA3AF', fontsize=8.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    meta_box = FancyBboxPatch((114, 81.8), 40, 4.4, boxstyle="round,pad=0.2,rounding_size=0.5",
                              facecolor='#1E293B', edgecolor='#334155', linewidth=1, zorder=3)
    ax.add_patch(meta_box)
    ax.text(134, 84.0, "FORM FACTOR: 18.0 x 23.5 mm | 3.3V LOGIC",
            color='#A78BFA', fontsize=7.8, fontweight='bold', fontfamily='monospace', ha='center', va='center', zorder=4)

    # =========================================================================
    # LEFT: PHYSICAL RP2040-ZERO BOARD DRAWING (AUTHENTIC PINOUT)
    # =========================================================================
    ax.text(28, 77.5, "[ PHYSICAL BOARD LAYOUT & PIN MAPPING ]", color='#A78BFA', fontsize=8.8,
            fontweight='bold', fontfamily='monospace', ha='center', zorder=4)

    # Board dimensions in canvas coords
    bx, by, bw, bh = 18, 12, 20, 62

    # PCB Board Base (Waveshare signature deep purple)
    pcb = FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.4,rounding_size=2.0",
                         facecolor='#2E1065', edgecolor='#6D28D9', linewidth=2.5, zorder=2)
    ax.add_patch(pcb)

    # USB Type-C Receptacle (Top)
    usb = FancyBboxPatch((bx + 5, by + bh - 5), 10, 7.5, boxstyle="round,pad=0.2,rounding_size=1.2",
                         facecolor='#94A3B8', edgecolor='#CBD5E1', linewidth=1.5, zorder=3)
    ax.add_patch(usb)
    usb_in = FancyBboxPatch((bx + 6.2, by + bh - 4), 7.6, 5, boxstyle="round,pad=0.1,rounding_size=0.8",
                            facecolor='#1E293B', edgecolor='#64748B', linewidth=1, zorder=4)
    ax.add_patch(usb_in)
    ax.text(bx + bw/2, by + bh - 1.5, "USB-C", color='#E2E8F0', fontsize=6.5,
            fontweight='bold', fontfamily='DejaVu Sans', ha='center', zorder=5)

    # Board silkscreen branding
    ax.text(bx + bw/2, by + bh - 9.0, "Waveshare", color='#DDD6FE', fontsize=7.2,
            fontweight='bold', fontfamily='DejaVu Sans', ha='center', zorder=5)
    ax.text(bx + bw/2, by + bh - 11.5, "RP2040-Zero", color='#A78BFA', fontsize=7.8,
            fontweight='bold', fontfamily='monospace', ha='center', zorder=5)

    # Onboard Peripherals on PCB
    # Crystal 12MHz
    xtal = Rectangle((bx + 3.2, by + 43), 4.0, 2.4, facecolor='#D1D5DB', edgecolor='#9CA3AF', lw=1, zorder=3)
    ax.add_patch(xtal)
    ax.text(bx + 5.2, by + 44.2, "12M", color='#1F2937', fontsize=5.0, fontfamily='monospace', ha='center', va='center', zorder=5)

    # Flash W25Q16JV (2MB)
    flash = Rectangle((bx + 12.8, by + 42.5), 4.2, 3.2, facecolor='#1F2937', edgecolor='#4B5563', lw=1, zorder=3)
    ax.add_patch(flash)
    ax.text(bx + 14.9, by + 44.1, "2MB\nFLASH", color='#9CA3AF', fontsize=4.2, fontfamily='monospace', ha='center', va='center', zorder=5)

    # RP2040 Main Chip (Center black square)
    chip = FancyBboxPatch((bx + 4.5, by + 27), 11, 11, boxstyle="round,pad=0.1,rounding_size=0.8",
                          facecolor='#090D16', edgecolor='#475569', linewidth=1.2, zorder=3)
    ax.add_patch(chip)
    ax.plot(bx + 6.2, by + 35.8, 'o', color='#E11D48', markersize=3, zorder=5)
    ax.text(bx + bw/2, by + 33.2, "RP2040", color='#F8FAFC', fontsize=7.2,
            fontweight='bold', fontfamily='monospace', ha='center', zorder=5)
    ax.text(bx + bw/2, by + 30.2, "Dual Cortex-M0+", color='#94A3B8', fontsize=5.0,
            fontfamily='DejaVu Sans', ha='center', zorder=5)

    # LDO Regulator ME6211
    ldo = Rectangle((bx + 3.5, by + 21), 3.8, 2.8, facecolor='#1F2937', edgecolor='#4B5563', lw=1, zorder=3)
    ax.add_patch(ldo)
    ax.text(bx + 5.4, by + 22.4, "ME6211\n3V3 LDO", color='#F59E0B', fontsize=4.0, fontfamily='monospace', ha='center', va='center', zorder=5)

    # WS2812 RGB LED (GP16)
    rgb = Rectangle((bx + 12.5, by + 21), 3.5, 2.8, facecolor='#065F46', edgecolor='#10B981', lw=1, zorder=3)
    ax.add_patch(rgb)
    ax.plot(bx + 14.25, by + 22.4, '*', color='#34D399', markersize=4.5, zorder=5)
    ax.text(bx + 14.25, by + 19.5, "WS2812 (GP16)", color='#34D399', fontsize=4.6, fontfamily='monospace', ha='center', zorder=5)

    # BOOT and RESET buttons
    btn_b = Circle((bx + 5.5, by + 15), 1.4, facecolor='#CBD5E1', edgecolor='#475569', lw=1, zorder=3)
    btn_r = Circle((bx + 14.5, by + 15), 1.4, facecolor='#CBD5E1', edgecolor='#475569', lw=1, zorder=3)
    ax.add_patch(btn_b)
    ax.add_patch(btn_r)
    ax.text(bx + 5.5, by + 12.2, "BOOT", color='#94A3B8', fontsize=4.8, fontfamily='monospace', ha='center', zorder=5)
    ax.text(bx + 14.5, by + 12.2, "RESET", color='#94A3B8', fontsize=4.8, fontfamily='monospace', ha='center', zorder=5)

    # AUTHENTIC PHYSICAL PINOUT:
    # LEFT EDGE (Top to Bottom): 5V, GND, 3V3, GP29, GP28, GP27, GP26, GP15, GP14
    left_pins = [
        ("5V", "VBUS_IN", '#EF4444', True),
        ("GND", "GND", '#64748B', True),
        ("3V3", "+3V3_OUT", '#FB923C', True),
        ("GP29", "ADC3", '#475569', False),
        ("GP28", "ADC2", '#475569', False),
        ("GP27", "ADC1", '#475569', False),
        ("GP26", "ADC0", '#475569', False),
        ("GP15", "Unused", '#475569', False),
        ("GP14", "Unused", '#475569', False),
    ]

    # RIGHT EDGE (Top to Bottom): GP0, GP1, GP2, GP3, GP4, GP5, GP6, GP7, GP8
    right_pins = [
        ("GP0", "OLED_SDA", '#06B6D4', True),
        ("GP1", "OLED_SCL", '#06B6D4', True),
        ("GP2", "BTN_LEFT", '#10B981', True),
        ("GP3", "BTN_ACTION", '#10B981', True),
        ("GP4", "BTN_RIGHT", '#10B981', True),
        ("GP5", "BUZZER_PWM", '#EAB308', True),
        ("GP6", "Unused", '#475569', False),
        ("GP7", "Unused", '#475569', False),
        ("GP8", "Unused", '#475569', False),
    ]

    pin_ys = [by + bh - 16 - i * 5.2 for i in range(9)]

    # Draw Left Pins (5V, GND, 3V3...) & Left Callouts
    for i, (pname, net, col, is_active) in enumerate(left_pins):
        py = pin_ys[i]
        pad = Rectangle((bx - 0.8, py - 1.2), 2.2, 2.4, facecolor='#FACC15', edgecolor='#CA8A04', lw=0.8, zorder=3)
        ax.add_patch(pad)
        hole = Circle((bx + 0.3, py), 0.7, facecolor='#0B0F19', edgecolor='#94A3B8', lw=0.6, zorder=4)
        ax.add_patch(hole)
        ax.text(bx + 2.2, py, pname, color='#FFFFFF' if is_active else '#64748B',
                fontsize=5.6, fontweight='bold' if is_active else 'normal',
                fontfamily='monospace', va='center', zorder=5)

        if is_active:
            ax.plot([bx - 0.8, bx - 3.5], [py, py], color=col, lw=1.5, zorder=3)
            badge = FancyBboxPatch((bx - 16.5, py - 1.6), 13.0, 3.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                                   facecolor='#1E293B', edgecolor=col, linewidth=1.2, zorder=4)
            ax.add_patch(badge)
            ax.text(bx - 10.0, py, f"{pname} → {net}", color=col, fontsize=6.2,
                    fontweight='bold', fontfamily='monospace', ha='center', va='center', zorder=5)
        else:
            ax.plot([bx - 0.8, bx - 2.5], [py, py], color='#334155', lw=0.8, zorder=3)
            ax.text(bx - 3.2, py, pname, color='#64748B', fontsize=5.2, fontfamily='monospace', ha='right', va='center', zorder=5)

    # Draw Right Pins (GP0, GP1, GP2...) & Right Callouts
    for i, (pname, net, col, is_active) in enumerate(right_pins):
        py = pin_ys[i]
        pad = Rectangle((bx + bw - 1.4, py - 1.2), 2.2, 2.4, facecolor='#FACC15', edgecolor='#CA8A04', lw=0.8, zorder=3)
        ax.add_patch(pad)
        hole = Circle((bx + bw - 0.3, py), 0.7, facecolor='#0B0F19', edgecolor='#94A3B8', lw=0.6, zorder=4)
        ax.add_patch(hole)
        ax.text(bx + bw - 2.2, py, pname, color='#FFFFFF' if is_active else '#64748B',
                fontsize=5.6, fontweight='bold' if is_active else 'normal',
                fontfamily='monospace', ha='right', va='center', zorder=5)

        if is_active:
            ax.plot([bx + bw + 0.8, bx + bw + 3.2], [py, py], color=col, lw=1.5, zorder=3)
            badge = FancyBboxPatch((bx + bw + 3.2, py - 1.6), 16.5, 3.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                                   facecolor='#1E293B', edgecolor=col, linewidth=1.2, zorder=4)
            ax.add_patch(badge)
            ax.text(bx + bw + 11.45, py, f"{pname} → {net}", color=col, fontsize=6.2,
                    fontweight='bold', fontfamily='monospace', ha='center', va='center', zorder=5)
        else:
            ax.plot([bx + bw + 0.8, bx + bw + 2.5], [py, py], color='#334155', lw=0.8, zorder=3)
            ax.text(bx + bw + 3.2, py, pname, color='#64748B', fontsize=5.2, fontfamily='monospace', ha='left', va='center', zorder=5)

    # =========================================================================
    # RIGHT SIDE: PERIPHERAL MAPPING & VOLTAGE MATRIX (ENGINEERING TABLE)
    # =========================================================================
    table_x = 61
    table_y = 10
    table_w = 95
    table_h = 65

    ax.text(table_x + table_w/2, 77.5, "[ HARDWARE PERIPHERAL & ELECTRICAL SPECIFICATION MATRIX ]",
            color='#38BDF8', fontsize=8.8, fontweight='bold', fontfamily='monospace', ha='center', zorder=4)

    tcard = FancyBboxPatch((table_x, table_y), table_w, table_h, boxstyle="round,pad=0.2,rounding_size=1.0",
                           facecolor='#111827', edgecolor='#1F2937', linewidth=1.5, zorder=2)
    ax.add_patch(tcard)

    th_bg = FancyBboxPatch((table_x, table_y + table_h - 4.2), table_w, 4.2, boxstyle="round,pad=0.2,rounding_size=0.8",
                           facecolor='#1E293B', edgecolor='#334155', linewidth=1, zorder=3)
    ax.add_patch(th_bg)

    headers = [
        (table_x + 3.5, "PIN"),
        (table_x + 13.5, "NET NAME"),
        (table_x + 28.5, "PERIPHERAL TARGET"),
        (table_x + 48.0, "FUNCTION / BUS"),
        (table_x + 67.0, "VOLTAGE / LOGIC"),
        (table_x + 82.5, "PULL CONFIG"),
    ]
    for hx, htext in headers:
        ax.text(hx, table_y + table_h - 2.1, htext, color='#94A3B8', fontsize=7.2,
                fontweight='bold', fontfamily='monospace', va='center', zorder=5)

    rows = [
        ("GP0", "OLED_SDA", "SSD1306 OLED (Pin 4)", "I2C0 Data (Fast-mode 400kHz)", "3.3V Logic (LVCMOS)", "Internal PU (50k)", '#06B6D4'),
        ("GP1", "OLED_SCL", "SSD1306 OLED (Pin 3)", "I2C0 Clock (400kHz SCL)", "3.3V Logic (LVCMOS)", "Internal PU (50k)", '#06B6D4'),
        ("GP2", "BTN_LEFT", "SW1 Tactile Pushbutton", "Nav Left / Prev Mode In", "3.3V Active-LOW", "Pull.UP Enabled", '#10B981'),
        ("GP3", "BTN_ACTION", "SW2 Tactile Pushbutton", "Action / Feed Pet / Game", "3.3V Active-LOW", "Pull.UP Enabled", '#10B981'),
        ("GP4", "BTN_RIGHT", "SW3 Tactile Pushbutton", "Nav Right / Next Mode In", "3.3V Active-LOW", "Pull.UP Enabled", '#10B981'),
        ("GP5", "BUZZER_PWM", "BZ1 Passive Piezo Buzzer", "PWM Tone Synthesis (Slice 2B)", "3.3V Peak Sq. Wave", "Push-Pull Driver", '#EAB308'),
        ("5V", "VBUS_IN", "TP4056 Switched Output", "Main System Power Input", "+3.7V to +5.0V DC", "Schottky Protected", '#EF4444'),
        ("3V3", "+3V3", "SSD1306 OLED VCC", "Regulated 3.3V Rail Out", "+3.30V DC (+-2%)", "Max 500mA LDO", '#FB923C'),
        ("GND", "GND", "Common Ground (All)", "System Zero-Volt Reference", "0.00V Ref Plane", "Solid Ground Bus", '#94A3B8'),
        ("GP16", "NEOPIXEL", "Onboard WS2812 RGB LED", "Status Indication / Heartbeat", "3.3V NRZ Single-Wire", "Internal Push-Pull", '#34D399'),
        ("GP6-15", "EXPANSION", "Unpopulated Header / Pads", "Future Expansion / Debug", "3.3V High-Z", "Disabled / Floating", '#64748B'),
    ]

    row_y_start = table_y + table_h - 8.5
    for idx, (pin, net, target, func, volt, pull, color) in enumerate(rows):
        ry = row_y_start - idx * 4.4
        if idx % 2 == 0:
            row_bg = Rectangle((table_x + 0.5, ry - 1.8), table_w - 1.0, 4.0,
                               facecolor='#162032', edgecolor='none', zorder=2)
            ax.add_patch(row_bg)

        pbox = FancyBboxPatch((table_x + 1.5, ry - 1.3), 7.2, 2.6, boxstyle="round,pad=0.1,rounding_size=0.4",
                              facecolor='#0F172A', edgecolor=color, linewidth=1, zorder=3)
        ax.add_patch(pbox)
        ax.text(table_x + 5.1, ry, pin, color=color, fontsize=6.2, fontweight='bold',
                fontfamily='monospace', ha='center', va='center', zorder=4)

        ax.text(table_x + 13.5, ry, net, color='#F3F4F6', fontsize=6.8, fontweight='bold', fontfamily='monospace', va='center', zorder=4)
        ax.text(table_x + 28.5, ry, target, color='#E5E7EB', fontsize=6.5, fontfamily='DejaVu Sans', va='center', zorder=4)
        ax.text(table_x + 48.0, ry, func, color='#D1D5DB', fontsize=6.4, fontfamily='DejaVu Sans', va='center', zorder=4)
        ax.text(table_x + 67.0, ry, volt, color=color, fontsize=6.5, fontweight='bold', fontfamily='monospace', va='center', zorder=4)
        ax.text(table_x + 82.5, ry, pull, color='#9CA3AF', fontsize=6.4, fontfamily='DejaVu Sans', va='center', zorder=4)

    nbox = FancyBboxPatch((table_x + 1.5, table_y + 1.2), table_w - 3.0, 8.5, boxstyle="round,pad=0.2,rounding_size=0.6",
                          facecolor='#0F172A', edgecolor='#334155', linewidth=0.8, zorder=3)
    ax.add_patch(nbox)
    ax.text(table_x + 3.0, table_y + 7.5, "ELECTRICAL CONSTRAINTS & DESIGN NOTES:",
            color='#FBBF24', fontsize=7.0, fontweight='bold', fontfamily='monospace', zorder=4)
    ax.text(table_x + 3.0, table_y + 5.5, "• I/O Domain: All GPIOs operate strictly in 3.3V logic domain (3.63V absolute maximum; NOT 5V tolerant).",
            color='#CBD5E1', fontsize=6.6, fontfamily='DejaVu Sans', zorder=4)
    ax.text(table_x + 3.0, table_y + 3.8, "• Pull-Up Topography: Tactile buttons rely on software pull-ups (`digitalio.Pull.UP`), eliminating external resistors.",
            color='#CBD5E1', fontsize=6.6, fontfamily='DejaVu Sans', zorder=4)
    ax.text(table_x + 3.0, table_y + 2.1, "• Power Gating: Power rail VBUS_IN accepts direct switched LiPo battery (3.5V-4.2V) or 5V USB Type-C supply.",
            color='#CBD5E1', fontsize=6.6, fontfamily='DejaVu Sans', zorder=4)

    # =========================================================================
    # FOOTER: VOLTAGE LEGEND & SUMMARY
    # =========================================================================
    footer = FancyBboxPatch((4, 2.5), 152, 5.5, boxstyle="round,pad=0.2,rounding_size=0.6",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.2, zorder=2)
    ax.add_patch(footer)

    ax.text(7, 5.2, "COLOR KEY:", color='#9CA3AF', fontsize=7.5, fontweight='bold', fontfamily='monospace', va='center', zorder=4)

    keys = [
        ("I2C Bus (3.3V)", '#06B6D4', 21),
        ("Digital Input (Active-LOW)", '#10B981', 44),
        ("PWM Audio Out", '#EAB308', 76),
        ("Power Rail (+5V / +3V3)", '#EF4444', 99),
        ("Ground (0V Ref)", '#64748B', 126),
    ]
    for lbl, col, kx in keys:
        ax.plot([kx, kx + 3.5], [5.2, 5.2], color=col, lw=3, zorder=3)
        ax.text(kx + 4.5, 5.2, lbl, color='#E2E8F0', fontsize=7.2, fontfamily='DejaVu Sans', va='center', zorder=4)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=120)
    plt.close(fig)
    print(f"Generated: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out1 = r"C:\Users\white\pocket-companion\assets\journal_media\02_rp2040_pinout_peripheral_matrix.png"
    out2 = r"C:\Users\white\pocket-companion\assets\02_rp2040_pinout_peripheral_matrix.png"
    create_pinout_matrix(out1)
    create_pinout_matrix(out2)
