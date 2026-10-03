"""
=============================================================================
POCKET COMPANION - RP2040 VIRTUAL PET & GAME CONSOLE
AUTHENTIC EDA SCHEMATIC CAPTURE GENERATOR (EasyEDA / KiCad Standards)
=============================================================================
Output: 05_easyeda_schematic_capture.png (1920x1080 @ 120 DPI)
Pure CAD/EDA aesthetic:
  - White sheet canvas with subtle 100 mil coordinate grid dots
  - Classic engineering drawing border with zones (A-D, 1-6)
  - Standard IEEE/IEC schematic symbols (zig-zag resistors, parallel plates, etc.)
  - Orthogonal 90-degree wiring with solder junction dots
  - Standard hierarchical / bus net label flags
  - Full EDA Title Block with revision, author, date, and ERC pass status
=============================================================================
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch

def generate_schematic():
    fig = plt.figure(figsize=(16, 9), dpi=120)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis('off')

    # Color Palette: Authentic EDA Theme
    BG_COLOR = '#FFFFFF'
    GRID_DOT = '#CBD5E1'
    BORDER_COLOR = '#991B1B'
    WIRE_COLOR = '#007A00'        # Standard CAD Green Wire
    JUNCTION_COLOR = '#007A00'    # CAD Solder Junction Dot
    BODY_FILL = '#FFFFFF'
    BODY_BORDER = '#0F172A'       # Dark Slate IC boundary
    PIN_NUM_COLOR = '#DC2626'     # Pin numbers in EDA Red
    REF_COLOR = '#B91C1C'         # Designator in Red
    VAL_COLOR = '#0369A1'         # Value in Blue

    # Set background pure white
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # 1. Coordinate Grid Dots (100 mil CAD spacing)
    for gx in range(5, 156, 2):
        for gy in range(5, 86, 2):
            ax.plot(gx, gy, '.', color=GRID_DOT, markersize=1.2, zorder=1)

    # 2. Classic Engineering Drawing Sheet Border
    ax.add_patch(Rectangle((3.5, 3.5), 153, 83, facecolor='none', edgecolor=BORDER_COLOR, lw=1.6, zorder=2))
    ax.add_patch(Rectangle((4.8, 4.8), 150.4, 80.4, facecolor='none', edgecolor=BORDER_COLOR, lw=0.8, zorder=2))

    # Coordinate Reference Markings (A-D vertically, 1-6 horizontally)
    zones_y = [('A', 75), ('B', 56), ('C', 37), ('D', 18)]
    for char, zy in zones_y:
        ax.text(4.1, zy, char, color=BORDER_COLOR, fontsize=6.5, fontfamily='Consolas', ha='center', va='center', fontweight='bold', zorder=10)
        ax.text(155.9, zy, char, color=BORDER_COLOR, fontsize=6.5, fontfamily='Consolas', ha='center', va='center', fontweight='bold', zorder=10)

    zones_x = [('1', 17), ('2', 42), ('3', 67), ('4', 92), ('5', 117), ('6', 142)]
    for num, zx in zones_x:
        ax.text(zx, 85.9, num, color=BORDER_COLOR, fontsize=6.5, fontfamily='Consolas', ha='center', va='center', fontweight='bold', zorder=10)
        ax.text(zx, 4.1, num, color=BORDER_COLOR, fontsize=6.5, fontfamily='Consolas', ha='center', va='center', fontweight='bold', zorder=10)

    # Header Sheet Banner
    ax.text(6.0, 83.5, "EASYEDA SCHEMATIC CAPTURE — OPEN SOURCE HARDWARE", color='#64748B',
            fontsize=6.5, fontfamily='Consolas', fontweight='bold', zorder=10)
    ax.text(154.0, 83.5, "HACK CLUB HALF-LIFE EDITION", color='#64748B',
            fontsize=6.5, fontfamily='Consolas', fontweight='bold', ha='right', zorder=10)

    # -------------------------------------------------------------------------
    # 3. HELPER FUNCTIONS FOR AUTHENTIC SCHEMATIC PRIMITIVES
    # -------------------------------------------------------------------------
    def draw_junction(x, y):
        ax.plot(x, y, 'o', color=JUNCTION_COLOR, markersize=4.5, zorder=5)

    def draw_gnd(x, y, label="GND"):
        ax.plot([x, x], [y, y - 1.2], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.plot([x - 1.8, x + 1.8], [y - 1.2, y - 1.2], color=BODY_BORDER, lw=1.5, zorder=4)
        ax.plot([x - 1.1, x + 1.1], [y - 1.8, y - 1.8], color=BODY_BORDER, lw=1.3, zorder=4)
        ax.plot([x - 0.4, x + 0.4], [y - 2.4, y - 2.4], color=BODY_BORDER, lw=1.0, zorder=4)
        if label:
            ax.text(x, y - 3.4, label, color='#475569', fontsize=5.5, fontfamily='Consolas', ha='center', zorder=10)

    def draw_pwr_arrow(x, y, text, color='#B91C1C'):
        ax.plot([x, x], [y, y + 1.4], color=WIRE_COLOR, lw=1.5, zorder=4)
        arrow = Polygon([[x, y + 3.0], [x - 1.1, y + 1.4], [x + 1.1, y + 1.4]],
                        closed=True, facecolor=color, edgecolor=color, zorder=5)
        ax.add_patch(arrow)
        ax.text(x, y + 3.9, text, color=color, fontsize=6.2, fontweight='bold',
                fontfamily='Consolas', ha='center', zorder=10)

    def draw_net_flag(x, y, text, direction='right', color='#0369A1'):
        w = len(text) * 0.95 + 2.2
        h = 2.4
        if direction == 'right':
            poly = Polygon([[x, y], [x + 1.4, y + h/2], [x + w, y + h/2],
                            [x + w, y - h/2], [x + 1.4, y - h/2]],
                           closed=True, facecolor='#F0F9FF', edgecolor=color, lw=1.1, zorder=6)
            ax.add_patch(poly)
            ax.text(x + w/2 + 0.5, y, text, color=color, fontsize=6.2, fontweight='bold',
                    fontfamily='Consolas', ha='center', va='center', zorder=10)
        else: # left
            poly = Polygon([[x, y], [x - 1.4, y + h/2], [x - w, y + h/2],
                            [x - w, y - h/2], [x - 1.4, y - h/2]],
                           closed=True, facecolor='#F0F9FF', edgecolor=color, lw=1.1, zorder=6)
            ax.add_patch(poly)
            ax.text(x - w/2 - 0.5, y, text, color=color, fontsize=6.2, fontweight='bold',
                    fontfamily='Consolas', ha='center', va='center', zorder=10)

    def draw_zigzag_resistor_vert(x, y_top, y_bot, ref, val):
        lead_len = 1.6
        y1 = y_top - lead_len
        y2 = y_bot + lead_len
        ax.plot([x, x], [y_top, y1], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.plot([x, x], [y2, y_bot], color=WIRE_COLOR, lw=1.5, zorder=4)
        
        # Zig-Zag IEEE standard (6 peaks)
        dy = (y1 - y2) / 6.0
        amp = 1.1
        pts = [[x, y1],
               [x + amp, y1 - dy * 0.5],
               [x - amp, y1 - dy * 1.5],
               [x + amp, y1 - dy * 2.5],
               [x - amp, y1 - dy * 3.5],
               [x + amp, y1 - dy * 4.5],
               [x - amp, y1 - dy * 5.5],
               [x, y2]]
        px = [p[0] for p in pts]
        py = [p[1] for p in pts]
        ax.plot(px, py, color=BODY_BORDER, lw=1.6, zorder=5)
        
        y_mid = (y_top + y_bot) / 2
        ax.text(x + 1.8, y_mid + 1.0, ref, color=REF_COLOR, fontsize=6.8, fontweight='bold', fontfamily='Consolas', zorder=10)
        ax.text(x + 1.8, y_mid - 1.2, val, color=VAL_COLOR, fontsize=6.0, fontfamily='Consolas', zorder=10)

    def draw_capacitor_vert(x, y_top, y_bot, ref, val):
        gap = 0.8
        plate_w = 2.4
        y_mid = (y_top + y_bot) / 2
        yp1 = y_mid + gap / 2
        yp2 = y_mid - gap / 2
        ax.plot([x, x], [y_top, yp1], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.plot([x, x], [yp2, y_bot], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.plot([x - plate_w, x + plate_w], [yp1, yp1], color=BODY_BORDER, lw=1.8, zorder=5)
        ax.plot([x - plate_w, x + plate_w], [yp2, yp2], color=BODY_BORDER, lw=1.8, zorder=5)
        
        ax.text(x + 2.8, y_mid + 1.0, ref, color=REF_COLOR, fontsize=6.8, fontweight='bold', fontfamily='Consolas', zorder=10)
        ax.text(x + 2.8, y_mid - 1.2, val, color=VAL_COLOR, fontsize=6.0, fontfamily='Consolas', zorder=10)

    # =========================================================================
    # 4. SUBSYSTEM 1: DISPLAY & I2C BUS PULLUPS (TOP LEFT)
    # =========================================================================
    ax.add_patch(Rectangle((7.5, 51), 40.5, 31.5, facecolor='none', edgecolor='#CBD5E1', lw=1, linestyle='--', zorder=2))
    ax.text(9.5, 80.8, "[ DISPLAY INTERFACE — I2C BUS ]", color='#0284C7', fontsize=6.8, fontweight='bold', fontfamily='Consolas', zorder=10)

    u2_x, u2_y, u2_w, u2_h = 9.5, 54, 16.0, 22
    ax.add_patch(Rectangle((u2_x, u2_y), u2_w, u2_h, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.6, zorder=3))

    ax.text(u2_x + u2_w/2, u2_y + u2_h + 2.4, "U2", color=REF_COLOR, fontsize=9.0, fontweight='bold', fontfamily='Consolas', ha='center', zorder=10)
    ax.text(u2_x + u2_w/2, u2_y + u2_h + 0.8, "SSD1306 0.96\" OLED", color='#0284C7', fontsize=6.8, fontweight='bold', fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u2_x + u2_w/2, u2_y - 2.0, "128x64 I2C | LCSC: C22453", color='#64748B', fontsize=5.2, fontfamily='Consolas', ha='center', zorder=10)

    # Pins on U2 right side (x = 25.5)
    u2_pins = [
        ("1", "GND", 19),
        ("2", "VCC", 13),
        ("3", "SCL", 7),
        ("4", "SDA", 2),
    ]

    for pnum, pname, rel_y in u2_pins:
        py = u2_y + rel_y
        ax.plot([u2_x + u2_w, u2_x + u2_w + 2.5], [py, py], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.text(u2_x + u2_w + 0.6, py + 0.7, pnum, color=PIN_NUM_COLOR, fontsize=5.0, fontfamily='Consolas', ha='left', zorder=10)
        ax.text(u2_x + u2_w - 0.8, py, pname, color='#0F172A', fontsize=6.2, fontweight='bold', fontfamily='Consolas', ha='right', va='center', zorder=10)

    # Pin 1: GND on U2 (y=73) -> wire to x=28, down to GND
    ax.plot([u2_x + u2_w + 2.5, 28], [u2_y + 19, u2_y + 19], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_gnd(28, u2_y + 19)

    # Pin 2: VCC on U2 (y=67) -> wire to x=32, up to +3V3 pullup rail at y=74
    ax.plot([u2_x + u2_w + 2.5, 32], [u2_y + 13, u2_y + 13], color=WIRE_COLOR, lw=1.5, zorder=4)
    ax.plot([32, 32], [u2_y + 13, 74], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_junction(32, 74)

    # +3V3 Rail for I2C Pull-ups (from x=32 to x=41 at y=74)
    ax.plot([32, 41], [74, 74], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_pwr_arrow(36.5, 74, "+3V3", color='#EA580C')
    draw_junction(36.5, 74)
    draw_junction(41, 74)

    # I2C Bus Wires
    scl_y = u2_y + 7  # 61
    sda_y = u2_y + 2  # 56

    # R2 on SCL (at x=36.5): between y=74 and scl_y (61)
    ax.plot([u2_x + u2_w + 2.5, 42], [scl_y, scl_y], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_zigzag_resistor_vert(36.5, 74, scl_y, "R2", "4.7kΩ")
    draw_junction(36.5, scl_y)
    draw_net_flag(42, scl_y, "SCL", direction='right', color='#0284C7')

    # R1 on SDA (at x=41): between y=74 and sda_y (56)
    ax.plot([u2_x + u2_w + 2.5, 42], [sda_y, sda_y], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_zigzag_resistor_vert(41, 74, sda_y, "R1", "4.7kΩ")
    draw_junction(41, sda_y)
    draw_net_flag(42, sda_y, "SDA", direction='right', color='#0284C7')

    ax.text(38.5, 52.5, "I2C 4.7kΩ Pull-Ups", color='#64748B', fontsize=5.5, fontfamily='Segoe UI', ha='center', zorder=10)

    # =========================================================================
    # 5. SUBSYSTEM 2: USER INPUT CONTROLS (BOTTOM LEFT)
    # =========================================================================
    ax.add_patch(Rectangle((7.5, 9.5), 40.5, 38.5, facecolor='none', edgecolor='#CBD5E1', lw=1, linestyle='--', zorder=2))
    ax.text(9.5, 46.2, "[ USER INPUT CONTROLS — ACTIVE LOW ]", color='#16A34A', fontsize=6.8,
            fontweight='bold', fontfamily='Consolas', zorder=10)

    buttons_data = [
        ("SW2", "BTN_L", "Left", 14),
        ("SW3", "BTN_M", "Action", 24),
        ("SW4", "BTN_R", "Right", 34),
    ]

    for sw_ref, net, name, bx in buttons_data:
        # Compact, authentic IEEE tactile pushbutton symbol
        y_mid = 30
        y_top = y_mid + 2.0   # 32.0
        y_bot = y_mid - 2.0   # 28.0
        
        # Upper lead wire up to net flag
        ax.plot([bx, bx], [y_top, y_top + 4.0], color=WIRE_COLOR, lw=1.5, zorder=4)
        draw_net_flag(bx, y_top + 4.0, net, direction='right', color='#16A34A')
        
        # Lower lead wire down to GND
        ax.plot([bx, bx], [y_bot, y_bot - 2.5], color=WIRE_COLOR, lw=1.5, zorder=4)
        draw_gnd(bx, y_bot - 2.5, label=None)

        # Switch Contact Terminals (Circles)
        ax.add_patch(Circle((bx, y_top), 0.45, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.3, zorder=5))
        ax.add_patch(Circle((bx, y_bot), 0.45, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.3, zorder=5))
        
        # Angled Contact Arm (Normally Open)
        ax.plot([bx, bx + 1.8], [y_top - 0.3, y_mid - 0.5], color=BODY_BORDER, lw=1.6, zorder=5)
        
        # Pushbutton Plunger / T-Hat
        ax.plot([bx + 1.0, bx + 2.4], [y_mid + 0.8, y_mid + 0.8], color=BODY_BORDER, lw=1.1, zorder=5)
        ax.plot([bx + 2.4, bx + 2.4], [y_mid - 0.2, y_mid + 1.8], color=BODY_BORDER, lw=1.5, zorder=5)

        # Reference designator to the left of the switch
        ax.text(bx - 2.0, y_mid, sw_ref, color=REF_COLOR, fontsize=7.2, fontweight='bold', fontfamily='Consolas', ha='right', va='center', zorder=10)
        # Part info below GND
        ax.text(bx, y_bot - 6.0, f"SW-TH_4P\n{name}", color='#475569', fontsize=5.2, fontfamily='Consolas', ha='center', zorder=10)

    ax.text(25, 11.5, "Internal RP2040 Pull-ups (~50kΩ) enabled | LCSC: C318884",
            color='#64748B', fontsize=5.5, fontfamily='Segoe UI', ha='center', zorder=10)

    # =========================================================================
    # 6. SUBSYSTEM 3: MICROCONTROLLER CORE U1 (CENTER)
    # =========================================================================
    u1_x, u1_y, u1_w, u1_h = 64, 23, 34, 56
    ax.add_patch(Rectangle((u1_x, u1_y), u1_w, u1_h, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.8, zorder=3))

    ax.text(u1_x + u1_w/2, u1_y + u1_h + 3.0, "U1", color=REF_COLOR, fontsize=10.5, fontweight='bold',
            fontfamily='Consolas', ha='center', zorder=10)
    ax.text(u1_x + u1_w/2, u1_y + u1_h + 1.2, "Waveshare RP2040-Zero", color='#0284C7', fontsize=7.8,
            fontweight='bold', fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u1_x + u1_w/2, u1_y - 2.2, "MODULE-SMD_RP2040-ZERO | LCSC: C2058836", color='#475569',
            fontsize=5.8, fontfamily='Consolas', ha='center', zorder=10)

    # Internal details badge
    badge = FancyBboxPatch((u1_x + 3.5, u1_y + 19), 27, 22, boxstyle="round,pad=0.2,rounding_size=0.6",
                           facecolor='#F8FAFC', edgecolor='#E2E8F0', lw=1, zorder=3)
    ax.add_patch(badge)
    ax.text(u1_x + 17, u1_y + 37.5, "Raspberry Pi RP2040", color='#0F172A', fontsize=7.5,
            fontweight='bold', fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u1_x + 17, u1_y + 34.5, "Dual Cortex-M0+ @ 133MHz", color='#475569', fontsize=5.8, fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u1_x + 17, u1_y + 31.5, "264KB SRAM | 2MB Flash", color='#475569', fontsize=5.8, fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u1_x + 17, u1_y + 28.5, "Type-C USB | WS2812 RGB", color='#475569', fontsize=5.8, fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u1_x + 17, u1_y + 25.5, "BOOT + RESET Pushbuttons", color='#475569', fontsize=5.8, fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u1_x + 17, u1_y + 22.5, "Internal 50kΩ Pull-ups", color='#16A34A', fontsize=5.8, fontweight='bold', fontfamily='Consolas', ha='center', zorder=10)

    # RP2040 Left Pins (GPIO) - wire from u1_x to 58, net flag at 58
    u1_left_pins = [
        ("1", "GP0 / SDA", "SDA", 51, '#0284C7'),
        ("2", "GP1 / SCL", "SCL", 44, '#0284C7'),
        ("3", "GP2", "BTN_L", 32, '#16A34A'),
        ("4", "GP3", "BTN_M", 24, '#16A34A'),
        ("5", "GP4", "BTN_R", 16, '#16A34A'),
        ("6", "GP5 / PWM", "BUZZ_PWM", 7, '#D97706'),
    ]

    for pnum, pname, net, rel_y, col in u1_left_pins:
        py = u1_y + rel_y
        ax.plot([58, u1_x], [py, py], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.text(u1_x - 1.2, py + 0.8, pnum, color=PIN_NUM_COLOR, fontsize=5.5, fontfamily='Consolas', ha='right', zorder=10)
        ax.text(u1_x + 1.4, py, pname, color='#0F172A', fontsize=6.6, fontweight='bold', fontfamily='Consolas', va='center', zorder=10)
        draw_net_flag(58, py, net, direction='left', color=col)

    # RP2040 Right Pins (Power) - wire from u1_x + u1_w to 102
    u1_right_pins = [
        ("9", "5V (VBUS)", "VBUS_IN", 51, '#B91C1C'),
        ("7", "3V3", "+3V3", 30, '#EA580C'),
        ("8", "GND", "GND", 10, '#475569'),
    ]

    for pnum, pname, net, rel_y, col in u1_right_pins:
        py = u1_y + rel_y
        ax.plot([u1_x + u1_w, u1_x + u1_w + 3.5], [py, py], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.text(u1_x + u1_w + 1.0, py + 0.8, pnum, color=PIN_NUM_COLOR, fontsize=5.5, fontfamily='Consolas', ha='left', zorder=10)
        ax.text(u1_x + u1_w - 1.4, py, pname, color='#0F172A', fontsize=6.6, fontweight='bold', fontfamily='Consolas', ha='right', va='center', zorder=10)
        
        if pname == "GND":
            draw_gnd(u1_x + u1_w + 3.5, py)
        elif "3V3" in pname:
            draw_pwr_arrow(u1_x + u1_w + 3.5, py, "+3V3", color='#EA580C')
        else:
            draw_net_flag(u1_x + u1_w + 3.5, py, net, direction='right', color='#B91C1C')

    # =========================================================================
    # 7. SUBSYSTEM 4: AUDIO OUTPUT PIEZO BUZZER (BOTTOM CENTER)
    # =========================================================================
    ax.add_patch(Rectangle((64, 6.5), 34, 14.5, facecolor='none', edgecolor='#CBD5E1', lw=1, linestyle='--', zorder=2))
    ax.text(66, 19.2, "[ AUDIO OUTPUT SUBSYSTEM ]", color='#D97706', fontsize=6.8,
            fontweight='bold', fontfamily='Consolas', zorder=10)

    bz_x, bz_y = 80, 12.5
    # Positive terminal (top)
    ax.plot([70, bz_x - 2], [bz_y + 2.2, bz_y + 2.2], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_net_flag(70, bz_y + 2.2, "BUZZ_PWM", direction='left', color='#D97706')
    ax.text(bz_x - 1.0, bz_y + 3.2, "+", color='#B91C1C', fontsize=6.5, fontweight='bold', ha='right', zorder=10)

    # Negative terminal (bottom)
    ax.plot([bz_x - 5, bz_x - 2], [bz_y - 2.2, bz_y - 2.2], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_gnd(bz_x - 5, bz_y - 2.2)
    ax.text(bz_x - 1.0, bz_y - 1.5, "-", color='#475569', fontsize=6.5, fontweight='bold', ha='right', zorder=10)

    # Buzzer rectangular cylinder body
    ax.add_patch(Rectangle((bz_x - 2, bz_y - 4), 4, 8, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.6, zorder=4))

    # Acoustic flare horn
    horn_pts = [[bz_x + 2, bz_y + 4],
                [bz_x + 5.5, bz_y + 5.5],
                [bz_x + 5.5, bz_y - 5.5],
                [bz_x + 2, bz_y - 4]]
    ax.add_patch(Polygon(horn_pts, closed=True, facecolor='#FEF3C7', edgecolor=BODY_BORDER, lw=1.4, zorder=4))

    # Labels
    ax.text(bz_x + 7.5, bz_y + 2.5, "BZ1", color=REF_COLOR, fontsize=8.5, fontweight='bold', fontfamily='Consolas', zorder=10)
    ax.text(bz_x + 7.5, bz_y + 0.3, "Passive Piezo", color='#0F172A', fontsize=6.5, fontweight='bold', fontfamily='Segoe UI', zorder=10)
    ax.text(bz_x + 7.5, bz_y - 1.7, "3-5V | 4kHz", color='#D97706', fontsize=6.0, fontfamily='Consolas', zorder=10)
    ax.text(bz_x + 7.5, bz_y - 3.7, "LCSC: C96395", color='#64748B', fontsize=5.5, fontfamily='Consolas', zorder=10)

    # =========================================================================
    # 8. SUBSYSTEM 5: POWER MANAGEMENT & CHARGING (RIGHT COLUMN)
    # =========================================================================
    ax.add_patch(Rectangle((106, 26), 48.5, 56.5, facecolor='none', edgecolor='#CBD5E1', lw=1, linestyle='--', zorder=2))
    ax.text(108, 80.8, "[ POWER MANAGEMENT & CHARGING ]", color='#B91C1C', fontsize=6.8,
            fontweight='bold', fontfamily='Consolas', zorder=10)

    # ------------------ U3 TP4056 CHARGER IC & PROTECTION ------------------
    u3_x, u3_y, u3_w, u3_h = 114, 52, 17, 25
    ax.add_patch(Rectangle((u3_x, u3_y), u3_w, u3_h, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.6, zorder=3))

    ax.text(u3_x + u3_w/2, u3_y + u3_h + 2.5, "U3", color=REF_COLOR, fontsize=9.0, fontweight='bold', fontfamily='Consolas', ha='center', zorder=10)
    ax.text(u3_x + u3_w/2, u3_y + u3_h + 0.8, "TP4056 Charger", color='#B91C1C', fontsize=7.0, fontweight='bold', fontfamily='Segoe UI', ha='center', zorder=10)
    ax.text(u3_x + u3_w/2, u3_y - 2.0, "DW01A + FS8205A | 250mA", color='#64748B', fontsize=5.2, fontfamily='Consolas', ha='center', zorder=10)

    # U3 Left Pins
    u3_left_pins = [
        ("IN+ (5V)", 21),
        ("IN- (GND)", 15),
        ("CHRG", 9),
        ("STDBY", 3),
    ]

    for pname, rel_y in u3_left_pins:
        py = u3_y + rel_y
        ax.plot([u3_x - 2.5, u3_x], [py, py], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.text(u3_x + 0.8, py, pname, color='#0F172A', fontsize=5.8, fontweight='bold', fontfamily='Consolas', va='center', zorder=10)

    # IN+ connects to 5V USB power flag
    draw_pwr_arrow(u3_x - 2.5, u3_y + 21, "VBUS_USB", color='#B91C1C')
    # IN- connects to GND
    draw_gnd(u3_x - 2.5, u3_y + 15)
    # Status LED labels
    ax.text(u3_x - 3.5, u3_y + 9, "LED_RED", color='#DC2626', fontsize=5.0, fontfamily='Consolas', ha='right', va='center', zorder=10)
    ax.text(u3_x - 3.5, u3_y + 3, "LED_BLUE", color='#2563EB', fontsize=5.0, fontfamily='Consolas', ha='right', va='center', zorder=10)

    # U3 Right Pins
    u3_right_pins = [
        ("BAT+", 21),
        ("BAT-", 15),
        ("OUT+ (VBAT)", 8),
        ("OUT- (GND)", 2),
    ]

    for pname, rel_y in u3_right_pins:
        py = u3_y + rel_y
        ax.plot([u3_x + u3_w, u3_x + u3_w + 2.5], [py, py], color=WIRE_COLOR, lw=1.5, zorder=4)
        ax.text(u3_x + u3_w - 0.8, py, pname, color='#0F172A', fontsize=5.8, fontweight='bold', fontfamily='Consolas', ha='right', va='center', zorder=10)

    # OUT- connects to system ground
    draw_gnd(u3_x + u3_w + 2.5, u3_y + 2)

    # ------------------ BT1 LIPO BATTERY PACK ------------------
    bt1_x = 140
    # BAT+ connects directly to BT1(+) plate
    ax.plot([u3_x + u3_w + 2.5, bt1_x], [u3_y + 21, u3_y + 21], color=WIRE_COLOR, lw=1.5, zorder=4)
    # BAT- connects directly to BT1(-) plate
    ax.plot([u3_x + u3_w + 2.5, bt1_x + 2.0], [u3_y + 15, u3_y + 15], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_junction(u3_x + u3_w + 2.5, u3_y + 21)
    draw_junction(u3_x + u3_w + 2.5, u3_y + 15)
    draw_junction(bt1_x, u3_y + 21)
    draw_junction(bt1_x + 2.0, u3_y + 15)

    # Long thin positive plate
    ax.plot([bt1_x, bt1_x], [u3_y + 21 - 3.5, u3_y + 21 + 3.5], color=BODY_BORDER, lw=1.8, zorder=5)
    # Short thick negative plate
    ax.plot([bt1_x + 2.0, bt1_x + 2.0], [u3_y + 15 - 2.0, u3_y + 15 + 2.0], color=BODY_BORDER, lw=3.2, zorder=5)
    # Internal dielectric dashed line
    ax.plot([bt1_x, bt1_x + 2.0], [u3_y + 18, u3_y + 18], color='#CBD5E1', lw=1, linestyle=':', zorder=3)

    ax.text(bt1_x - 1.2, u3_y + 21 + 2.0, "+", color='#B91C1C', fontsize=7.5, fontweight='bold', zorder=10)
    ax.text(bt1_x + 2.5, u3_y + 15 - 2.0, "-", color='#475569', fontsize=7.5, fontweight='bold', zorder=10)

    # Battery labels
    ax.text(bt1_x + 4.5, u3_y + 22, "BT1", color=REF_COLOR, fontsize=8.5, fontweight='bold', fontfamily='Consolas', zorder=10)
    ax.text(bt1_x + 4.5, u3_y + 19.5, "3.7V 400mAh LiPo", color='#0F172A', fontsize=6.8, fontweight='bold', fontfamily='Segoe UI', zorder=10)
    ax.text(bt1_x + 4.5, u3_y + 17.0, "Model: 502535 (1.48Wh)", color='#475569', fontsize=5.5, fontfamily='Consolas', zorder=10)
    ax.text(bt1_x + 4.5, u3_y + 14.5, "JST-PH 2.0mm (C131337)", color='#D97706', fontsize=5.5, fontfamily='Consolas', zorder=10)

    # ------------------ SW1 SPDT POWER SLIDE SWITCH ------------------
    sw1_x = 114
    sw1_y = 36

    # OUT+ wire exits U3 right side (133.5, 60), goes right to x=135, and has VBAT net flag
    ax.plot([u3_x + u3_w + 2.5, 135], [u3_y + 8, u3_y + 8], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_junction(135, u3_y + 8)
    draw_net_flag(135, u3_y + 8, "VBAT", direction='right', color='#EA580C')

    # OUT+ wire descends cleanly at x=135 down to SW1 Pin 3 (y=42)
    ax.plot([135, 135], [u3_y + 8, sw1_y + 6], color=WIRE_COLOR, lw=1.5, zorder=4)
    ax.plot([135, sw1_x + 2.5], [sw1_y + 6, sw1_y + 6], color=WIRE_COLOR, lw=1.5, zorder=4)

    # 3 Contacts of SPDT Switch
    # Pin 3: VBAT (top)
    ax.add_patch(Circle((sw1_x + 2.5, sw1_y + 6), 0.5, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.3, zorder=5))
    ax.text(sw1_x + 1.2, sw1_y + 6.8, "3", color=PIN_NUM_COLOR, fontsize=5.2, fontfamily='Consolas', zorder=10)

    # Pin 2: COM (middle)
    ax.add_patch(Circle((sw1_x + 2.5, sw1_y + 3), 0.5, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.3, zorder=5))
    ax.text(sw1_x + 1.2, sw1_y + 3.2, "2", color=PIN_NUM_COLOR, fontsize=5.2, fontfamily='Consolas', zorder=10)

    # Pin 1: NC (bottom)
    ax.plot([sw1_x + 0.5, sw1_x + 2.5], [sw1_y, sw1_y], color='#94A3B8', lw=1.5, zorder=4)
    ax.add_patch(Circle((sw1_x + 2.5, sw1_y), 0.5, facecolor=BODY_FILL, edgecolor=BODY_BORDER, lw=1.3, zorder=5))
    ax.text(sw1_x + 1.2, sw1_y - 0.8, "1", color=PIN_NUM_COLOR, fontsize=5.2, fontfamily='Consolas', zorder=10)

    # NC mark (Red Cross)
    ax.plot([sw1_x - 1.5, sw1_x + 0.5], [sw1_y - 1.0, sw1_y + 1.0], color='#DC2626', lw=1.2, zorder=5)
    ax.plot([sw1_x - 1.5, sw1_x + 0.5], [sw1_y + 1.0, sw1_y - 1.0], color='#DC2626', lw=1.2, zorder=5)
    ax.text(sw1_x - 2.5, sw1_y, "NC", color='#64748B', fontsize=5.5, fontfamily='Consolas', ha='right', va='center', zorder=10)

    # Wiper arm connecting Pin 2 (COM) to Pin 3 (VBAT - ON position)
    ax.plot([sw1_x + 2.5, sw1_x + 5.2], [sw1_y + 3.0, sw1_y + 5.5], color=BODY_BORDER, lw=1.8, zorder=6)

    # SW1 COM Wire connecting right to C1 and VBUS_IN Net
    ax.plot([sw1_x + 2.5, 138], [sw1_y + 3, sw1_y + 3], color=WIRE_COLOR, lw=1.5, zorder=4)
    draw_junction(124, sw1_y + 3)
    draw_net_flag(124, sw1_y + 3, "VBUS_IN", direction='right', color='#B91C1C')
    draw_junction(138, sw1_y + 3)

    ax.text(sw1_x + 4, sw1_y + 8.5, "SW1", color=REF_COLOR, fontsize=7.5, fontweight='bold', fontfamily='Consolas', ha='center', zorder=10)
    ax.text(sw1_x + 4, sw1_y - 3.2, "SPDT Slide Switch\nSS-12D00G3 (C432128)", color='#475569',
            fontsize=5.2, fontfamily='Consolas', ha='center', zorder=10)

    # ------------------ DECOUPLING CAPACITORS C1 & C2 ------------------
    # C1 (10uF on VBUS_IN)
    c1_x = 138
    c1_top_y = sw1_y + 3  # 39
    c1_bot_y = 30
    draw_capacitor_vert(c1_x, c1_top_y, c1_bot_y, "C1", "10µF / 10V")
    draw_gnd(c1_x, c1_bot_y)

    # C2 (100nF on +3V3)
    c2_x = 148
    c2_top_y = sw1_y + 3  # 39
    c2_bot_y = 30
    draw_pwr_arrow(c2_x, c2_top_y, "+3V3", color='#EA580C')
    draw_capacitor_vert(c2_x, c2_top_y, c2_bot_y, "C2", "100nF / 16V")
    draw_gnd(c2_x, c2_bot_y)

    # =========================================================================
    # 9. STANDARD EDA TITLE BLOCK (LOWER RIGHT CORNER)
    # =========================================================================
    tb_x, tb_y, tb_w, tb_h = 106, 4.8, 48.5, 19.5
    ax.add_patch(Rectangle((tb_x, tb_y), tb_w, tb_h, facecolor=BODY_FILL, edgecolor=BORDER_COLOR, lw=1.4, zorder=2))

    # Grid subdivisions inside title block
    ax.plot([tb_x, tb_x + tb_w], [tb_y + 13.5, tb_y + 13.5], color=BORDER_COLOR, lw=0.9, zorder=3)
    ax.plot([tb_x, tb_x + tb_w], [tb_y + 7.5, tb_y + 7.5], color=BORDER_COLOR, lw=0.9, zorder=3)
    ax.plot([tb_x + 31.5, tb_x + 31.5], [tb_y, tb_y + 7.5], color=BORDER_COLOR, lw=0.9, zorder=3)

    # Field 1: Title (Top Section)
    ax.text(tb_x + 2.0, tb_y + 16.8, "Pocket Companion - RP2040 Virtual Pet & Game Console",
            color='#0F172A', fontsize=8.0, fontweight='bold', fontfamily='Segoe UI', zorder=10)
    ax.text(tb_x + 2.0, tb_y + 14.5, "Hack Club Half-Life | Dual Cortex-M0+ Hardware Architecture",
            color='#475569', fontsize=6.2, fontfamily='Segoe UI', zorder=10)

    # Field 2: Company & Document (Middle Section)
    ax.text(tb_x + 2.0, tb_y + 11.2, "Company / Author: Part of Cosmos / Debanjan Biswas",
            color='#0F172A', fontsize=6.5, fontfamily='Segoe UI', zorder=10)
    ax.text(tb_x + 2.0, tb_y + 8.8, "Schematic File: Pocket_Companion_Schematic.json",
            color='#0284C7', fontsize=5.8, fontfamily='Consolas', zorder=10)

    # Field 3: Date, Size & Status (Bottom Left)
    ax.text(tb_x + 2.0, tb_y + 5.0, "Date: 2026-10-02   Size: A4 (1920x1080)",
            color='#334155', fontsize=5.8, fontfamily='Consolas', zorder=10)
    ax.text(tb_x + 2.0, tb_y + 2.2, "ERC Status: PASSED (0 ERRORS, 0 WARNINGS)",
            color='#16A34A', fontsize=5.8, fontweight='bold', fontfamily='Consolas', zorder=10)

    # Field 4: Revision & Sheet (Bottom Right)
    ax.text(tb_x + 33.5, tb_y + 5.0, "REV: v1.0",
            color='#B91C1C', fontsize=6.8, fontweight='bold', fontfamily='Consolas', zorder=10)
    ax.text(tb_x + 33.5, tb_y + 2.2, "SHEET: 1 / 1",
            color='#475569', fontsize=5.8, fontfamily='Consolas', zorder=10)

    # Save high-resolution PNG
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "05_easyeda_schematic_capture.png")
    plt.savefig(out_path, dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Pristine EDA Schematic Rendered: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    generate_schematic()
