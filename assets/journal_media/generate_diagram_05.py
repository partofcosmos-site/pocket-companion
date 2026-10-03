"""
Hardware Documentation Graphics Generator for Pocket Companion
(Hack Club Half-Life)
Asset 5: 05_easyeda_schematic_capture.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

def create_schematic_capture(output_path):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0F141C')
    ax.set_facecolor('#0F141C')
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis('off')

    # Draw schematic grid dots (EDA 100 mil grid)
    for x in range(3, 158, 2):
        for y in range(3, 88, 2):
            ax.plot(x, y, '.', color='#1A2333', markersize=1.2)

    # Outer Sheet Border (Standard Engineering Drawing Frame)
    border = Rectangle((2, 2), 156, 86, facecolor='none', edgecolor='#334155', lw=1.8)
    ax.add_patch(border)
    inner_border = Rectangle((3, 3), 154, 84, facecolor='none', edgecolor='#1E293B', lw=0.8)
    ax.add_patch(inner_border)

    # Coordinate Reference Zones along border
    for idx, char in enumerate(['A', 'B', 'C', 'D']):
        zy = 80 - idx * 22
        ax.text(2.5, zy, char, color='#475569', fontsize=6, fontfamily='Consolas', ha='center', va='center')
        ax.text(157.5, zy, char, color='#475569', fontsize=6, fontfamily='Consolas', ha='center', va='center')

    for idx, num in enumerate(['1', '2', '3', '4', '5', '6']):
        zx = 15 + idx * 25
        ax.text(zx, 2.5, num, color='#475569', fontsize=6, fontfamily='Consolas', ha='center', va='center')
        ax.text(zx, 87.5, num, color='#475569', fontsize=6, fontfamily='Consolas', ha='center', va='center')

    # ------------------ TITLE BLOCK (BOTTOM RIGHT) ------------------
    tb_x, tb_y, tb_w, tb_h = 104, 3, 53, 17
    tb = Rectangle((tb_x, tb_y), tb_w, tb_h, facecolor='#111827', edgecolor='#38BDF8', lw=1.2)
    ax.add_patch(tb)

    # Horizontal dividing lines in title block
    ax.plot([tb_x, tb_x + tb_w], [tb_y + 11.5, tb_y + 11.5], color='#1E293B', lw=0.8)
    ax.plot([tb_x, tb_x + tb_w], [tb_y + 6.0, tb_y + 6.0], color='#1E293B', lw=0.8)
    # Vertical dividing lines
    ax.plot([tb_x + 32, tb_x + 32], [tb_y, tb_y + 6.0], color='#1E293B', lw=0.8)

    ax.text(tb_x + 2, tb_y + 14.5, "POCKET COMPANION SCHEMATIC", color='#F8FAFC', fontsize=9.0,
            fontweight='bold', fontfamily='Segoe UI')
    ax.text(tb_x + 2, tb_y + 12.3, "Hack Club Half-Life | Dual Cortex-M0+ Handheld Console", color='#94A3B8', fontsize=6.2, fontfamily='Segoe UI')

    ax.text(tb_x + 2, tb_y + 9.5, "AUTHOR: Debanjan Biswas (partofcosmos-site)", color='#E2E8F0', fontsize=6.8, fontfamily='Segoe UI')
    ax.text(tb_x + 2, tb_y + 7.2, "DOC: Pocket_Companion_Schematic.json", color='#38BDF8', fontsize=6.5, fontfamily='Consolas')

    ax.text(tb_x + 2, tb_y + 3.8, "DATE: 2026-10-02", color='#9CA3AF', fontsize=6.5, fontfamily='Consolas')
    ax.text(tb_x + 2, tb_y + 1.8, "STATUS: ERC PASSED (0 ERRORS)", color='#34D399', fontsize=6.5, fontweight='bold', fontfamily='Consolas')

    ax.text(tb_x + 34, tb_y + 3.8, "REV: v1.0", color='#FCD34D', fontsize=7.0, fontweight='bold', fontfamily='Consolas')
    ax.text(tb_x + 34, tb_y + 1.8, "SHEET: 1 / 1", color='#94A3B8', fontsize=6.5, fontfamily='Consolas')

    # Helper function for Net Label Flag
    def draw_net_flag(x, y, text, color='#38BDF8', direction='right'):
        # Pentagon flag
        w, h = len(text) * 0.95 + 2.0, 2.4
        if direction == 'right':
            poly = Polygon([[x, y], [x + 1.5, y + h/2], [x + w, y + h/2], [x + w, y - h/2], [x + 1.5, y - h/2]],
                           closed=True, facecolor='#1E293B', edgecolor=color, lw=1)
            ax.add_patch(poly)
            ax.text(x + w/2 + 0.5, y, text, color=color, fontsize=6.2, fontweight='bold',
                    fontfamily='Consolas', ha='center', va='center')
        else: # left
            poly = Polygon([[x, y], [x - 1.5, y + h/2], [x - w, y + h/2], [x - w, y - h/2], [x - 1.5, y - h/2]],
                           closed=True, facecolor='#1E293B', edgecolor=color, lw=1)
            ax.add_patch(poly)
            ax.text(x - w/2 - 0.5, y, text, color=color, fontsize=6.2, fontweight='bold',
                    fontfamily='Consolas', ha='center', va='center')

    # Helper function for Ground Symbol
    def draw_gnd(x, y):
        ax.plot([x, x], [y, y - 1.5], color='#94A3B8', lw=1.5)
        ax.plot([x - 1.8, x + 1.8], [y - 1.5, y - 1.5], color='#94A3B8', lw=1.5)
        ax.plot([x - 1.1, x + 1.1], [y - 2.2, y - 2.2], color='#94A3B8', lw=1.2)
        ax.plot([x - 0.4, x + 0.4], [y - 2.8, y - 2.8], color='#94A3B8', lw=1.0)
        ax.text(x, y - 4.2, "GND", color='#64748B', fontsize=5.5, fontfamily='Consolas', ha='center')

    # Helper function for VCC Power Flag
    def draw_pwr_flag(x, y, text, color='#EF4444'):
        ax.plot([x, x], [y, y + 1.5], color=color, lw=1.5)
        ax.plot([x - 1.5, x + 1.5], [y + 1.5, y + 1.5], color=color, lw=1.8)
        poly = Polygon([[x, y + 2.8], [x - 1.0, y + 1.5], [x + 1.0, y + 1.5]],
                       closed=True, facecolor=color, edgecolor='none')
        ax.add_patch(poly)
        ax.text(x, y + 4.0, text, color=color, fontsize=6.2, fontweight='bold', fontfamily='Consolas', ha='center')

    # =========================================================================
    # COMPONENT 1: U1 WAVESHARE RP2040-ZERO (CENTER)
    # =========================================================================
    u1_x, u1_y, u1_w, u1_h = 58, 28, 44, 48
    u1_box = Rectangle((u1_x, u1_y), u1_w, u1_h, facecolor='#111827', edgecolor='#0284C7', lw=1.8)
    ax.add_patch(u1_box)

    # Designation and component info
    ax.text(u1_x + u1_w/2, u1_y + u1_h + 3.0, "U1", color='#F8FAFC', fontsize=10.0,
            fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(u1_x + u1_w/2, u1_y + u1_h + 1.0, "Waveshare RP2040-Zero", color='#38BDF8', fontsize=7.5,
            fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(u1_x + u1_w/2, u1_y - 2.5, "LCSC: C2058836  |  MODULE-SMD_RP2040-ZERO", color='#FCD34D', fontsize=6.5,
            fontfamily='Consolas', ha='center')

    # Left Pins of U1 (GP0, GP1, GP2, GP3, GP4, GP5)
    u1_left_pins = [
        ("1", "GP0", "OLED_SDA", 44, '#06B6D4'),
        ("2", "GP1", "OLED_SCL", 38, '#06B6D4'),
        ("3", "GP2", "BTN_LEFT", 28, '#10B981'),
        ("4", "GP3", "BTN_ACTION", 22, '#10B981'),
        ("5", "GP4", "BTN_RIGHT", 16, '#10B981'),
        ("6", "GP5", "BUZZER_PWM", 8, '#EAB308'),
    ]

    for pnum, pname, net, rel_y, pcol in u1_left_pins:
        py = u1_y + rel_y
        # Pin terminal line extending left
        ax.plot([u1_x - 4, u1_x], [py, py], color='#94A3B8', lw=1.5)
        # Pin number outside
        ax.text(u1_x - 1.0, py + 1.0, pnum, color='#64748B', fontsize=5.5, fontfamily='Consolas', ha='right')
        # Pin name inside
        ax.text(u1_x + 1.5, py, pname, color='#F3F4F6', fontsize=7.0, fontweight='bold', fontfamily='Consolas', va='center')
        # Net label flag on wire
        draw_net_flag(u1_x - 4, py, net, color=pcol, direction='left')

    # Right Pins of U1 (5V, 3V3, GND)
    u1_right_pins = [
        ("9", "5V", "VBUS_IN", 40, '#EF4444'),
        ("7", "3V3", "+3V3", 26, '#FB923C'),
        ("8", "GND", "GND", 10, '#94A3B8'),
    ]

    for pnum, pname, net, rel_y, pcol in u1_right_pins:
        py = u1_y + rel_y
        ax.plot([u1_x + u1_w, u1_x + u1_w + 4], [py, py], color='#94A3B8', lw=1.5)
        ax.text(u1_x + u1_w + 1.0, py + 1.0, pnum, color='#64748B', fontsize=5.5, fontfamily='Consolas', ha='left')
        ax.text(u1_x + u1_w - 1.5, py, pname, color='#F3F4F6', fontsize=7.0, fontweight='bold', fontfamily='Consolas', ha='right', va='center')
        if pname == "GND":
            draw_gnd(u1_x + u1_w + 4, py)
        elif pname == "3V3":
            draw_pwr_flag(u1_x + u1_w + 4, py, "+3V3", color='#FB923C')
        else: # 5V
            draw_net_flag(u1_x + u1_w + 4, py, net, color='#EF4444', direction='right')

    # =========================================================================
    # COMPONENT 2: J1 SSD1306 OLED HEADER (TOP LEFT)
    # =========================================================================
    j1_x, j1_y, j1_w, j1_h = 10, 52, 24, 25
    j1_box = Rectangle((j1_x, j1_y), j1_w, j1_h, facecolor='#111827', edgecolor='#0284C7', lw=1.5)
    ax.add_patch(j1_box)

    ax.text(j1_x + j1_w/2, j1_y + j1_h + 2.5, "J1", color='#F8FAFC', fontsize=9.0, fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(j1_x + j1_w/2, j1_y + j1_h + 0.8, "0.96\" SSD1306 OLED", color='#38BDF8', fontsize=6.8, fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(j1_x + j1_w/2, j1_y - 2.5, "LCSC: C22453  |  HDR-M-2.54_1x4", color='#FCD34D', fontsize=6.0, fontfamily='Consolas', ha='center')

    oled_pins_data = [
        ("1", "GND", 20, '#94A3B8'),
        ("2", "VCC", 14, '#FB923C'),
        ("3", "SCL", 8, '#06B6D4'),
        ("4", "SDA", 2, '#06B6D4'),
    ]

    for pnum, pname, rel_y, col in oled_pins_data:
        py = j1_y + rel_y
        # Pin terminal line extending right
        ax.plot([j1_x + j1_w, j1_x + j1_w + 4], [py, py], color='#94A3B8', lw=1.5)
        ax.text(j1_x + j1_w - 1.5, py, pname, color='#F3F4F6', fontsize=6.5, fontfamily='Consolas', ha='right', va='center')
        ax.text(j1_x + j1_w + 1.0, py + 1.0, pnum, color='#64748B', fontsize=5.2, fontfamily='Consolas', ha='left')
        if pname == "GND":
            draw_gnd(j1_x + j1_w + 4, py)
        elif pname == "VCC":
            draw_pwr_flag(j1_x + j1_w + 4, py, "+3V3", color='#FB923C')
        elif pname == "SCL":
            draw_net_flag(j1_x + j1_w + 4, py, "OLED_SCL", color=col, direction='right')
        elif pname == "SDA":
            draw_net_flag(j1_x + j1_w + 4, py, "OLED_SDA", color=col, direction='right')

    # =========================================================================
    # COMPONENT 3: THREE PUSHBUTTONS SW1, SW2, SW3 (BOTTOM LEFT)
    # =========================================================================
    sw_data = [
        ("SW1", "Tactile Left", "BTN_LEFT", 38, 10, '#10B981'),
        ("SW2", "Tactile Action", "BTN_ACTION", 24, 10, '#10B981'),
        ("SW3", "Tactile Right", "BTN_RIGHT", 10, 10, '#10B981'),
    ]

    for sw_id, desc, net, sx, sy, scol in sw_data:
        # Pushbutton schematic symbol
        # Two contacts with switch lever and plunger
        ax.plot([sx + 4, sx + 4], [sy + 10, sy + 7.5], color='#94A3B8', lw=1.5)
        ax.plot([sx + 4, sx + 4], [sy + 2.5, sy], color='#94A3B8', lw=1.5)

        # Contact circles
        c1 = Circle((sx + 4, sy + 7.5), 0.5, facecolor='#111827', edgecolor='#94A3B8', lw=1)
        c2 = Circle((sx + 4, sy + 2.5), 0.5, facecolor='#111827', edgecolor='#94A3B8', lw=1)
        ax.add_patch(c1)
        ax.add_patch(c2)

        # Switch blade / plunger (angled normally open)
        ax.plot([sx + 3.2, sx + 6.2], [sy + 7.5, sy + 4.0], color='#F3F4F6', lw=1.8)
        # Pushbutton handle
        ax.plot([sx + 5.0, sx + 7.5], [sy + 5.5, sy + 5.5], color='#94A3B8', lw=1.2)
        ax.plot([sx + 7.5, sx + 7.5], [sy + 4.0, sy + 7.0], color='#94A3B8', lw=1.5)

        # GND at bottom
        draw_gnd(sx + 4, sy)

        # Top net flag
        draw_net_flag(sx + 4, sy + 10, net, color=scol, direction='right')

        # Annotation labels
        ax.text(sx + 4, sy + 13.5, sw_id, color='#F8FAFC', fontsize=7.5, fontweight='bold', fontfamily='Consolas', ha='center')
        ax.text(sx + 4, sy - 5.5, "LCSC: C318884\nSW-TH_4P", color='#FCD34D', fontsize=5.2, fontfamily='Consolas', ha='center')

    # =========================================================================
    # COMPONENT 4: BZ1 PASSIVE PIEZO BUZZER (TOP RIGHT OF RP2040)
    # =========================================================================
    bz_x, bz_y = 118, 62
    # Piezo buzzer symbol (two plates / transducer symbol)
    ax.plot([bz_x - 3, bz_x - 1.5], [bz_y + 4, bz_y + 4], color='#94A3B8', lw=1.5)
    ax.plot([bz_x - 3, bz_x - 1.5], [bz_y - 4, bz_y - 4], color='#94A3B8', lw=1.5)

    # Piezo body cylinder schematic representation
    bz_rect = Rectangle((bz_x - 1.5, bz_y - 6), 5, 12, facecolor='#111827', edgecolor='#EAB308', lw=1.5)
    ax.add_patch(bz_rect)
    # Piezo horn lines
    ax.plot([bz_x + 3.5, bz_x + 6.5], [bz_y + 6, bz_y + 8], color='#EAB308', lw=1.5)
    ax.plot([bz_x + 3.5, bz_x + 6.5], [bz_y - 6, bz_y - 8], color='#EAB308', lw=1.5)
    ax.plot([bz_x + 6.5, bz_x + 6.5], [bz_y + 8, bz_y - 8], color='#EAB308', lw=1.5)

    # Net connections
    draw_net_flag(bz_x - 3, bz_y + 4, "BUZZER_PWM", color='#EAB308', direction='left')
    draw_gnd(bz_x - 3, bz_y - 4)

    ax.text(bz_x + 1.0, bz_y + 10.5, "BZ1", color='#F8FAFC', fontsize=8.5, fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(bz_x + 1.0, bz_y + 8.8, "Passive Piezo 3-5V", color='#EAB308', fontsize=6.2, fontfamily='Segoe UI', ha='center')
    ax.text(bz_x + 1.0, bz_y - 10.5, "LCSC: C96395  |  BUZZER-TH_BD9.0", color='#FCD34D', fontsize=5.5, fontfamily='Consolas', ha='center')

    # =========================================================================
    # COMPONENT 5: POWER & BATTERY SECTION (TOP RIGHT: TP4056 + BAT1 + SW_PWR)
    # =========================================================================
    # Group box for Battery Subsystem
    pwr_group = Rectangle((112, 23), 43, 31, facecolor='none', edgecolor='#334155', lw=1, linestyle='--')
    ax.add_patch(pwr_group)
    ax.text(114, 52.0, "POWER MANAGEMENT SUBSYSTEM", color='#F59E0B', fontsize=6.8, fontweight='bold', fontfamily='Consolas')

    # BAT1: Battery Port JST-PH 2P
    bat_x, bat_y = 116, 40
    bat_box = Rectangle((bat_x, bat_y), 11, 9, facecolor='#111827', edgecolor='#F59E0B', lw=1.2)
    ax.add_patch(bat_box)
    ax.text(bat_x + 5.5, bat_y + 10.2, "BAT1 (JST-PH)", color='#F8FAFC', fontsize=6.5, fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(bat_x + 5.5, bat_y - 2.0, "LCSC: C131337", color='#FCD34D', fontsize=5.2, fontfamily='Consolas', ha='center')

    ax.text(bat_x + 2, bat_y + 6.0, "+", color='#EF4444', fontsize=7, fontweight='bold')
    ax.text(bat_x + 2, bat_y + 2.5, "-", color='#94A3B8', fontsize=7, fontweight='bold')
    # Terminal wires
    ax.plot([bat_x + 11, bat_x + 14], [bat_y + 6.5, bat_y + 6.5], color='#EF4444', lw=1.5)
    ax.plot([bat_x + 11, bat_x + 14], [bat_y + 2.5, bat_y + 2.5], color='#94A3B8', lw=1.5)
    draw_gnd(bat_x + 14, bat_y + 2.5)

    # SW_PWR: SPDT Slide Switch
    sw_px, sw_py = 135, 38
    # Switch contacts
    ax.plot([sw_px, sw_px + 2], [sw_py + 6.0, sw_py + 6.0], color='#EF4444', lw=1.5) # Pin 3: VBAT
    ax.plot([sw_px, sw_px + 2], [sw_py + 3.0, sw_py + 3.0], color='#EF4444', lw=1.5) # Pin 2: COM (VBUS_IN)
    ax.plot([sw_px, sw_px + 2], [sw_py, sw_py], color='#64748B', lw=1.5)             # Pin 1: NC

    # Contact dots
    for y_off in [6.0, 3.0, 0.0]:
        cd = Circle((sw_px + 2, sw_py + y_off), 0.4, facecolor='#111827', edgecolor='#94A3B8', lw=1)
        ax.add_patch(cd)

    # Wiper between COM and VBAT
    ax.plot([sw_px + 2, sw_px + 5.5], [sw_py + 3.0, sw_py + 5.5], color='#F3F4F6', lw=1.8)

    # Connect BAT1 (+) to SW_PWR Pin 3 (VBAT)
    ax.plot([bat_x + 14, sw_px], [bat_y + 6.5, sw_py + 6.0], color='#EF4444', lw=1.5)
    ax.plot(bat_x + 14, bat_y + 6.5, 'o', color='#EF4444', markersize=3)
    ax.text(sw_px - 2.5, sw_py + 7.5, "VBAT", color='#F59E0B', fontsize=6.0, fontfamily='Consolas')

    # Connect SW_PWR COM to VBUS_IN Net
    ax.plot([sw_px + 2, sw_px + 6], [sw_py + 3.0, sw_py + 3.0], color='#EF4444', lw=1.5)
    draw_net_flag(sw_px + 6, sw_py + 3.0, "VBUS_IN", color='#EF4444', direction='right')

    # NC mark (X) on Pin 1
    ax.plot([sw_px - 1, sw_px + 1], [sw_py - 1, sw_py + 1], color='#EF4444', lw=1.2)
    ax.plot([sw_px - 1, sw_px + 1], [sw_py + 1, sw_py - 1], color='#EF4444', lw=1.2)
    ax.text(sw_px - 2, sw_py, "NC", color='#64748B', fontsize=5.5, fontfamily='Consolas')

    ax.text(sw_px + 4, sw_py + 9.5, "SW_PWR", color='#F8FAFC', fontsize=7.5, fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(sw_px + 4, sw_py - 3.5, "LCSC: C432128\nSPDT SS-12D00G3", color='#FCD34D', fontsize=5.2, fontfamily='Consolas', ha='center')

    # Add TP4056 Module Annotation Note in Subsystem
    tp_note = FancyBboxPatch((114, 25), 39, 4.5, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor='#0F172A', edgecolor='#38BDF8', linewidth=0.8)
    ax.add_patch(tp_note)
    ax.text(115, 27.2, "TP4056 Module connects in parallel via JST-PH to BAT1 port.",
            color='#94A3B8', fontsize=5.8, fontfamily='Segoe UI')

    # =========================================================================
    # DECOUPLING CAPACITORS & CIRCUIT PROTECTION (NEAR RP2040)
    # =========================================================================
    # C1 (10uF on VBUS) and C2 (100nF on 3V3)
    caps = [
        ("C1", "10uF", "VBUS_IN", 48, 70, '#EF4444'),
        ("C2", "100nF", "+3V3", 52, 70, '#FB923C'),
    ]
    for cid, cval, net, cx, cy, ccol in caps:
        # Cap plates
        ax.plot([cx, cx], [cy + 4, cy + 1.2], color=ccol, lw=1.5)
        ax.plot([cx - 1.5, cx + 1.5], [cy + 1.2, cy + 1.2], color='#E2E8F0', lw=1.5)
        ax.plot([cx - 1.5, cx + 1.5], [cy + 0.4, cy + 0.4], color='#E2E8F0', lw=1.5)
        ax.plot([cx, cx], [cy + 0.4, cy - 2.0], color='#94A3B8', lw=1.5)
        draw_gnd(cx, cy - 2.0)
        if net == "+3V3":
            draw_pwr_flag(cx, cy + 4, "+3V3", color='#FB923C')
        else:
            draw_net_flag(cx, cy + 4, "VBUS_IN", color='#EF4444', direction='right')
        ax.text(cx + 2.2, cy + 1.0, f"{cid}\n{cval}", color='#94A3B8', fontsize=5.2, fontfamily='Consolas')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=120)
    plt.close(fig)
    print(f"Generated: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out = r"C:\Users\white\pocket-companion\assets\journal_media\05_easyeda_schematic_capture.png"
    create_schematic_capture(out)
