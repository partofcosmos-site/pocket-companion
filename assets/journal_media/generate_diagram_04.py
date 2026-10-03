"""
Hardware Documentation Graphics Generator for Pocket Companion
(Hack Club Half-Life)
Asset 4: 04_breadboard_prototype_wiring.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, PathPatch
from matplotlib.path import Path

def create_breadboard_diagram(output_path):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis('off')

    # Draw ESD mat grid
    for x in range(4, 158, 4):
        ax.plot([x, x], [4, 88], color='#111827', lw=0.5)
    for y in range(4, 88, 4):
        ax.plot([4, 158], [y, y], color='#111827', lw=0.5)

    # ------------------ HEADER ------------------
    banner = FancyBboxPatch((4, 81), 152, 6.2, boxstyle="round,pad=0.2,rounding_size=0.8",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.5)
    ax.add_patch(banner)

    badge = FancyBboxPatch((6, 82.2), 12, 3.8, boxstyle="round,pad=0.2,rounding_size=0.5",
                           facecolor='#0284C7', edgecolor='#38BDF8', linewidth=1.2)
    ax.add_patch(badge)
    ax.text(12, 84.1, "PROTOTYPE", color='#FFFFFF', fontsize=9.0, fontweight='bold',
            fontfamily='Segoe UI', ha='center', va='center')

    ax.text(20, 85.0, "POCKET COMPANION — BREADBOARD PROTOTYPE WIRING DIAGRAM",
            color='#F9FAFB', fontsize=12.5, fontweight='bold', fontfamily='Segoe UI', va='center')
    ax.text(20, 82.5, "Complete Solderless Bench Wiring | Color-Coded Jumper Paths | RP2040-Zero, OLED, 3x Buttons, Buzzer & TP4056",
            color='#9CA3AF', fontsize=8.5, fontfamily='Segoe UI', va='center')

    meta_box = FancyBboxPatch((118, 81.8), 36, 4.4, boxstyle="round,pad=0.2,rounding_size=0.5",
                              facecolor='#1E293B', edgecolor='#334155', linewidth=1)
    ax.add_patch(meta_box)
    ax.text(136, 84.0, "BENCH VERIFIED  |  CIRCUITPYTHON 9.X",
            color='#38BDF8', fontsize=7.8, fontweight='bold', fontfamily='Consolas', ha='center', va='center')

    # =========================================================================
    # BREADBOARD CANVAS (SOLDERLESS 830-POINT / 400-POINT BREADBOARD)
    # =========================================================================
    bb_x, bb_y, bb_w, bb_h = 10, 22, 108, 55

    # Drop shadow
    shadow = FancyBboxPatch((bb_x + 1.2, bb_y - 1.2), bb_w, bb_h, boxstyle="round,pad=0.3,rounding_size=1.5",
                            facecolor='#030712', edgecolor='none', alpha=0.6)
    ax.add_patch(shadow)

    # Breadboard plastic body (authentic off-white cream)
    bb = FancyBboxPatch((bb_x, bb_y), bb_w, bb_h, boxstyle="round,pad=0.3,rounding_size=1.5",
                        facecolor='#F3F4F6', edgecolor='#D1D5DB', linewidth=2)
    ax.add_patch(bb)

    # Center DIP trough groove
    trough = Rectangle((bb_x + 3, bb_y + bb_h/2 - 1.2), bb_w - 6, 2.4, facecolor='#E5E7EB', edgecolor='#D1D5DB', lw=0.8)
    ax.add_patch(trough)

    # Top Power Rails (+ / -)
    # Red stripe (+)
    ax.plot([bb_x + 6, bb_x + bb_w - 6], [bb_y + bb_h - 4.2, bb_y + bb_h - 4.2], color='#DC2626', lw=1.8)
    ax.text(bb_x + 3.8, bb_y + bb_h - 4.2, "+", color='#DC2626', fontsize=8, fontweight='bold', va='center', ha='center')
    # Blue stripe (-)
    ax.plot([bb_x + 6, bb_x + bb_w - 6], [bb_y + bb_h - 7.5, bb_y + bb_h - 7.5], color='#2563EB', lw=1.8)
    ax.text(bb_x + 3.8, bb_y + bb_h - 7.5, "-", color='#2563EB', fontsize=9, fontweight='bold', va='center', ha='center')

    # Bottom Power Rails (+ / -)
    # Blue stripe (-)
    ax.plot([bb_x + 6, bb_x + bb_w - 6], [bb_y + 7.5, bb_y + 7.5], color='#2563EB', lw=1.8)
    ax.text(bb_x + 3.8, bb_y + 7.5, "-", color='#2563EB', fontsize=9, fontweight='bold', va='center', ha='center')
    # Red stripe (+)
    ax.plot([bb_x + 6, bb_x + bb_w - 6], [bb_y + 4.2, bb_y + 4.2], color='#DC2626', lw=1.8)
    ax.text(bb_x + 3.8, bb_y + 4.2, "+", color='#DC2626', fontsize=8, fontweight='bold', va='center', ha='center')

    # Column numbers (1 to 30) along top and bottom
    ncols = 30
    col_x_start = bb_x + 8
    col_pitch = (bb_w - 16) / (ncols - 1)

    for c in range(ncols):
        cx = col_x_start + c * col_pitch
        # Column number labels
        if (c + 1) % 5 == 0 or c == 0:
            ax.text(cx, bb_y + bb_h - 10.5, str(c + 1), color='#9CA3AF', fontsize=5.2, fontfamily='Consolas', ha='center')
            ax.text(cx, bb_y + 10.5, str(c + 1), color='#9CA3AF', fontsize=5.2, fontfamily='Consolas', ha='center')

        # Top Power rail holes
        ax.plot(cx, bb_y + bb_h - 4.2, 's', color='#374151', markersize=2)
        ax.plot(cx, bb_y + bb_h - 7.5, 's', color='#374151', markersize=2)

        # Bottom Power rail holes
        ax.plot(cx, bb_y + 7.5, 's', color='#374151', markersize=2)
        ax.plot(cx, bb_y + 4.2, 's', color='#374151', markersize=2)

        # Terminal holes rows: A,B,C,D,E (top half)
        for r_idx in range(5):
            ry = bb_y + bb_h/2 + 3.0 + r_idx * 3.0
            ax.plot(cx, ry, 's', color='#4B5563', markersize=2.2)

        # Terminal holes rows: F,G,H,I,J (bottom half)
        for r_idx in range(5):
            ry = bb_y + bb_h/2 - 3.0 - r_idx * 3.0
            ax.plot(cx, ry, 's', color='#4B5563', markersize=2.2)

    # Row letter labels on side
    row_labels_top = ['A', 'B', 'C', 'D', 'E']
    for idx, rlab in enumerate(row_labels_top):
        ry = bb_y + bb_h/2 + 3.0 + idx * 3.0
        ax.text(bb_x + 5.5, ry, rlab, color='#9CA3AF', fontsize=5.2, fontfamily='Consolas', va='center', ha='center')

    row_labels_bot = ['F', 'G', 'H', 'I', 'J']
    for idx, rlab in enumerate(row_labels_bot):
        ry = bb_y + bb_h/2 - 3.0 - idx * 3.0
        ax.text(bb_x + 5.5, ry, rlab, color='#9CA3AF', fontsize=5.2, fontfamily='Consolas', va='center', ha='center')

    # =========================================================================
    # HARDWARE COMPONENTS PLACED ON BREADBOARD
    # =========================================================================

    # 1. WAVESHARE RP2040-ZERO MODULE (Columns 4 to 11)
    rp_x = col_x_start + 3 * col_pitch - 1.5
    rp_y = bb_y + bb_h/2 - 13.5
    rp_w = 7 * col_pitch + 3.0
    rp_h = 27.0

    rp_patch = FancyBboxPatch((rp_x, rp_y), rp_w, rp_h, boxstyle="round,pad=0.2,rounding_size=1.0",
                             facecolor='#3B0764', edgecolor='#7E22CE', linewidth=1.8)
    ax.add_patch(rp_patch)

    # RP2040 Silkscreen
    ax.text(rp_x + rp_w/2, rp_y + rp_h - 3.5, "RP2040-Zero", color='#E9D5FF', fontsize=7.2,
            fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(rp_x + rp_w/2, rp_y + rp_h - 6.0, "Waveshare", color='#C084FC', fontsize=6.0,
            fontweight='bold', fontfamily='Segoe UI', ha='center')

    # USB Type-C plug on left
    usb_c = FancyBboxPatch((rp_x - 3.8, rp_y + rp_h/2 - 3.5), 4.2, 7.0, boxstyle="round,pad=0.1,rounding_size=0.6",
                           facecolor='#94A3B8', edgecolor='#CBD5E1', linewidth=1)
    ax.add_patch(usb_c)
    ax.text(rp_x - 1.7, rp_y + rp_h/2, "USB", color='#1E293B', fontsize=4.8, fontweight='bold', fontfamily='Segoe UI', rotation=90, ha='center', va='center')

    # Center Chip RP2040
    chip_sq = Rectangle((rp_x + rp_w/2 - 4.5, rp_y + rp_h/2 - 4.5), 9, 9, facecolor='#0F172A', edgecolor='#475569', lw=1)
    ax.add_patch(chip_sq)
    ax.text(rp_x + rp_w/2, rp_y + rp_h/2, "RP2040\nMCU", color='#F8FAFC', fontsize=5.5, fontweight='bold', fontfamily='Consolas', ha='center', va='center')

    # Pins & Pin Labels on top edge (GP0, GP1, GP2, GP3, GP4, GP5, GP6, GP7)
    # and bottom edge (5V, GND, 3V3, GP29, GP28, GP27, GP26, GP15)
    for i in range(8):
        px = rp_x + 2.0 + i * col_pitch
        # Top pin solder joint
        ax.plot(px, rp_y + rp_h - 1.0, 'o', color='#FACC15', markersize=3)
        # Bottom pin solder joint
        ax.plot(px, rp_y + 1.0, 'o', color='#FACC15', markersize=3)

    # 2. SSD1306 0.96" OLED DISPLAY (Columns 14 to 21, Top side)
    oled_x = col_x_start + 14 * col_pitch
    oled_y = bb_y + bb_h/2 + 2.5
    oled_w = 20.0
    oled_h = 22.0

    # Blue breakout PCB
    oled_pcb = FancyBboxPatch((oled_x, oled_y), oled_w, oled_h, boxstyle="round,pad=0.2,rounding_size=0.8",
                              facecolor='#1E3A8A', edgecolor='#3B82F6', linewidth=1.5)
    ax.add_patch(oled_pcb)

    # Black OLED glass screen
    oled_glass = Rectangle((oled_x + 2.0, oled_y + 6.0), oled_w - 4.0, oled_h - 8.0,
                           facecolor='#030712', edgecolor='#1F2937', lw=1.2)
    ax.add_patch(oled_glass)

    # Glowing OLED display graphics (Blue Phosphor)
    ax.text(oled_x + oled_w/2, oled_y + oled_h - 5.5, "( ^ _ ^ )", color='#38BDF8', fontsize=9.5,
            fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(oled_x + oled_w/2, oled_y + oled_h - 8.5, "Happiness: 100%", color='#38BDF8', fontsize=5.8,
            fontfamily='Consolas', ha='center')
    ax.text(oled_x + oled_w/2, oled_y + oled_h - 11.0, "Mode: Virtual Pet", color='#0284C7', fontsize=5.0,
            fontfamily='Segoe UI', ha='center')

    # OLED 4-pin header (GND, VCC, SCL, SDA)
    oled_pins = ["GND", "VCC", "SCL", "SDA"]
    for i, ptxt in enumerate(oled_pins):
        opx = oled_x + 3.0 + i * 4.4
        opy = oled_y + 2.5
        ax.plot(opx, opy, 'o', color='#FACC15', markersize=3.5)
        ax.text(opx, opy - 2.0, ptxt, color='#FFFFFF', fontsize=4.8, fontweight='bold', fontfamily='Consolas', ha='center')

    # 3. THREE TACTILE PUSHBUTTONS (Columns 15, 20, 25, Bottom side)
    buttons = [
        ("LEFT (GP2)", col_x_start + 14 * col_pitch, '#10B981', '#059669', "SW1"),
        ("ACTION (GP3)", col_x_start + 19 * col_pitch, '#0284C7', '#0369A1', "SW2"),
        ("RIGHT (GP4)", col_x_start + 24 * col_pitch, '#EF4444', '#DC2626', "SW3"),
    ]

    for label, bx_col, cap_col, rim_col, sw_id in buttons:
        by_pos = bb_y + 13.0
        # Metal body
        sw_body = Rectangle((bx_col - 3.0, by_pos - 3.0), 6.0, 6.0, facecolor='#374151', edgecolor='#9CA3AF', lw=1)
        ax.add_patch(sw_body)
        # Plunger cap
        cap = Circle((bx_col, by_pos), 2.2, facecolor=cap_col, edgecolor=rim_col, lw=1.2)
        ax.add_patch(cap)
        ax.text(bx_col, by_pos - 4.8, sw_id, color='#1F2937', fontsize=5.5, fontweight='bold', fontfamily='Consolas', ha='center')
        ax.text(bx_col, by_pos + 4.2, label, color='#111827', fontsize=5.2, fontweight='bold', fontfamily='Segoe UI', ha='center')

    # 4. PIEZO BUZZER (Columns 26-28, Top side)
    bz_x = col_x_start + 26 * col_pitch + 2.0
    bz_y = bb_y + bb_h - 18.0
    # Black cylinder body
    bz_outer = Circle((bz_x, bz_y), 5.5, facecolor='#111827', edgecolor='#4B5563', lw=1.5)
    ax.add_patch(bz_outer)
    # Sound hole
    bz_inner = Circle((bz_x, bz_y), 2.0, facecolor='#030712', edgecolor='#374151', lw=1)
    ax.add_patch(bz_inner)
    ax.text(bz_x, bz_y + 7.0, "PIEZO BUZZER (BZ1)", color='#1F2937', fontsize=5.5, fontweight='bold', fontfamily='Consolas', ha='center')
    ax.text(bz_x + 3.0, bz_y + 2.0, "+", color='#EF4444', fontsize=7.0, fontweight='bold')

    # =========================================================================
    # POWER MODULES (RIGHT / BOTTOM-RIGHT OFF-BREADBOARD)
    # =========================================================================

    # 5. TP4056 CHARGER MODULE (Right side: X=124, Y=45)
    tp_x, tp_y, tp_w, tp_h = 124, 46, 32, 22
    tp_card = FancyBboxPatch((tp_x, tp_y), tp_w, tp_h, boxstyle="round,pad=0.2,rounding_size=0.8",
                             facecolor='#1E3A8A', edgecolor='#3B82F6', linewidth=1.5)
    ax.add_patch(tp_card)
    ax.text(tp_x + tp_w/2, tp_y + tp_h - 3.2, "TP4056 Type-C Charger", color='#FFFFFF', fontsize=7.5,
            fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(tp_x + tp_w/2, tp_y + tp_h - 5.5, "Li-ion CC/CV 250mA + DW01A Prot.", color='#93C5FD', fontsize=5.8, fontfamily='Segoe UI', ha='center')

    # USB-C port on right edge of module
    tp_usb = Rectangle((tp_x + tp_w - 1.0, tp_y + tp_h/2 - 3.5), 3.5, 7.0, facecolor='#94A3B8', edgecolor='#E2E8F0', lw=1)
    ax.add_patch(tp_usb)

    # Solder pads on TP4056
    ax.text(tp_x + 3.0, tp_y + tp_h - 9.0, "B+ [To LiPo +]", color='#FCA5A5', fontsize=6.2, fontfamily='Consolas')
    ax.text(tp_x + 3.0, tp_y + tp_h - 12.0, "B- [To LiPo -]", color='#94A3B8', fontsize=6.2, fontfamily='Consolas')
    ax.text(tp_x + 3.0, tp_y + tp_h - 15.0, "OUT+ [To Switch]", color='#FCD34D', fontsize=6.2, fontfamily='Consolas')
    ax.text(tp_x + 3.0, tp_y + tp_h - 18.0, "OUT- [To GND Rail]", color='#67E8F9', fontsize=6.2, fontfamily='Consolas')

    # 6. 3.7V 400mAh LiPo BATTERY (Right bottom: X=124, Y=14)
    bat_x, bat_y, bat_w, bat_h = 124, 14, 32, 26
    bat_card = FancyBboxPatch((bat_x, bat_y), bat_w, bat_h, boxstyle="round,pad=0.2,rounding_size=0.8",
                              facecolor='#1E293B', edgecolor='#475569', linewidth=1.5)
    ax.add_patch(bat_card)
    # Silver pouch
    pouch = Rectangle((bat_x + 2.0, bat_y + 2.0), bat_w - 4.0, bat_h - 7.0, facecolor='#94A3B8', edgecolor='#CBD5E1', lw=1)
    ax.add_patch(pouch)
    # Kapton tape collar
    kapton = Rectangle((bat_x + 2.0, bat_y + bat_h - 8.0), bat_w - 4.0, 3.0, facecolor='#CA8A04', edgecolor='none')
    ax.add_patch(kapton)
    ax.text(bat_x + bat_w/2, bat_y + 11.0, "3.7V 400mAh LiPo", color='#0F172A', fontsize=8.0,
            fontweight='bold', fontfamily='Segoe UI', ha='center')
    ax.text(bat_x + bat_w/2, bat_y + 7.5, "1.48Wh  |  Model 502535", color='#1E293B', fontsize=6.5, fontfamily='Consolas', ha='center')

    # Battery leads to TP4056
    ax.plot([bat_x + 6, bat_x + 6, tp_x + 2], [bat_y + bat_h - 2, tp_y + 5, tp_y + tp_h - 8.5], color='#EF4444', lw=2)
    ax.plot([bat_x + 10, bat_x + 10, tp_x + 2], [bat_y + bat_h - 2, tp_y + 3, tp_y + tp_h - 11.5], color='#111827', lw=2)

    # 7. SPDT MINI SLIDE SWITCH
    sw_pwr_x, sw_pwr_y = 114, 37
    sw_pwr = Rectangle((sw_pwr_x - 3.0, sw_pwr_y - 4.5), 6.0, 9.0, facecolor='#475569', edgecolor='#94A3B8', lw=1.2)
    ax.add_patch(sw_pwr)
    # Knob
    sw_knob = Rectangle((sw_pwr_x - 1.5, sw_pwr_y), 3.0, 3.5, facecolor='#E2E8F0', edgecolor='#64748B', lw=1)
    ax.add_patch(sw_knob)
    ax.text(sw_pwr_x, sw_pwr_y + 6.0, "PWR SWITCH", color='#94A3B8', fontsize=5.8, fontweight='bold', fontfamily='Consolas', ha='center')

    # =========================================================================
    # JUMPER WIRES (BEZIER CURVES WITH SHADOWS & DISTINCT INSULATION COLORS)
    # =========================================================================
    def draw_jumper(p0, p1, color, lw=2.2, rad=0.3):
        # Draw curved jumper wire using bezier control points
        mx = (p0[0] + p1[0]) / 2
        my = (p0[1] + p1[1]) / 2 + rad * (abs(p1[0] - p0[0]) + 10)
        verts = [p0, (mx, my), p1]
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)
        # Shadow
        shadow_verts = [(v[0] + 0.5, v[1] - 0.5) for v in verts]
        shadow_path = Path(shadow_verts, codes)
        ax.add_patch(PathPatch(shadow_path, facecolor='none', edgecolor='#0F172A', lw=lw+0.8, alpha=0.4))
        # Wire
        ax.add_patch(PathPatch(path, facecolor='none', edgecolor=color, lw=lw))
        # Pin termination dots
        ax.plot(p0[0], p0[1], 'o', color=color, markersize=3.5, markeredgecolor='#FFFFFF', markeredgewidth=0.5)
        ax.plot(p1[0], p1[1], 'o', color=color, markersize=3.5, markeredgecolor='#FFFFFF', markeredgewidth=0.5)

    # WIRE 1: GP0 (RP2040 Pin 1) -> OLED SDA
    w1_start = (rp_x + 2.0, rp_y + rp_h - 1.0)
    w1_end = (oled_x + 3.0 + 3 * 4.4, oled_y + 2.5)
    draw_jumper(w1_start, w1_end, '#06B6D4', lw=2.4, rad=0.25)

    # WIRE 2: GP1 (RP2040 Pin 2) -> OLED SCL
    w2_start = (rp_x + 2.0 + col_pitch, rp_y + rp_h - 1.0)
    w2_end = (oled_x + 3.0 + 2 * 4.4, oled_y + 2.5)
    draw_jumper(w2_start, w2_end, '#3B82F6', lw=2.4, rad=0.35)

    # WIRE 3: OLED VCC -> +3.3V Rail (Top Power Rail or RP2040 3V3)
    w3_start = (rp_x + 2.0 + 2 * col_pitch, rp_y + 1.0) # 3V3 on RP2040 bottom
    w3_end = (oled_x + 3.0 + 1 * 4.4, oled_y + 2.5)
    draw_jumper(w3_start, w3_end, '#F97316', lw=2.4, rad=-0.25)

    # WIRE 4: OLED GND -> Breadboard Blue Rail (GND)
    w4_start = (oled_x + 3.0, oled_y + 2.5)
    w4_end = (oled_x + 3.0, bb_y + bb_h - 7.5)
    draw_jumper(w4_start, w4_end, '#1F2937', lw=2.2, rad=0.1)

    # WIRE 5: GP2 (RP2040) -> SW1 (Left Button)
    w5_start = (rp_x + 2.0 + 2 * col_pitch, rp_y + rp_h - 1.0)
    w5_end = (buttons[0][1], bb_y + 16.0)
    draw_jumper(w5_start, w5_end, '#10B981', lw=2.4, rad=-0.35)

    # WIRE 6: GP3 (RP2040) -> SW2 (Action Button)
    w6_start = (rp_x + 2.0 + 3 * col_pitch, rp_y + rp_h - 1.0)
    w6_end = (buttons[1][1], bb_y + 16.0)
    draw_jumper(w6_start, w6_end, '#0EA5E9', lw=2.4, rad=-0.4)

    # WIRE 7: GP4 (RP2040) -> SW3 (Right Button)
    w7_start = (rp_x + 2.0 + 4 * col_pitch, rp_y + rp_h - 1.0)
    w7_end = (buttons[2][1], bb_y + 16.0)
    draw_jumper(w7_start, w7_end, '#EF4444', lw=2.4, rad=-0.45)

    # WIRE 8: GP5 (RP2040) -> Piezo Buzzer (+)
    w8_start = (rp_x + 2.0 + 5 * col_pitch, rp_y + rp_h - 1.0)
    w8_end = (bz_x - 2.5, bz_y)
    draw_jumper(w8_start, w8_end, '#FACC15', lw=2.4, rad=0.3)

    # WIRE 9: Buzzer (-) -> GND Rail
    w9_start = (bz_x + 2.5, bz_y)
    w9_end = (bz_x + 2.5, bb_y + bb_h - 7.5)
    draw_jumper(w9_start, w9_end, '#1F2937', lw=2.2, rad=0.1)

    # Buttons to Bottom GND rail
    for _, bx_col, _, _, _ in buttons:
        ax.plot([bx_col, bx_col], [bb_y + 10.0, bb_y + 7.5], color='#1F2937', lw=2.0)
        ax.plot(bx_col, bb_y + 7.5, 'o', color='#1F2937', markersize=3)

    # Power routing from TP4056 -> Switch -> RP2040 5V Pin
    ax.plot([tp_x + 2, sw_pwr_x + 2], [tp_y + tp_h - 15.0, sw_pwr_y], color='#F59E0B', lw=2.2)
    ax.plot([sw_pwr_x - 2, rp_x + 2.0], [sw_pwr_y, rp_y + 1.0], color='#EF4444', lw=2.5)

    # TP4056 OUT- to Blue GND Rail
    ax.plot([tp_x + 2, bb_x + bb_w - 10], [tp_y + tp_h - 18.0, bb_y + 7.5], color='#1F2937', lw=2.2)

    # RP2040 GND to Blue GND rail
    ax.plot([rp_x + 2.0 + col_pitch, rp_x + 2.0 + col_pitch], [rp_y + 1.0, bb_y + 7.5], color='#1F2937', lw=2.2)

    # =========================================================================
    # FOOTER WIRING REFERENCE & COLOR CODE TABLE
    # =========================================================================
    footer = FancyBboxPatch((4, 2.5), 152, 6.0, boxstyle="round,pad=0.2,rounding_size=0.6",
                            facecolor='#111827', edgecolor='#1F2937', linewidth=1.2)
    ax.add_patch(footer)

    ax.text(7, 5.5, "WIRING GUIDE:", color='#9CA3AF', fontsize=7.5, fontweight='bold', fontfamily='Consolas', va='center')

    wire_keys = [
        ("Cyan: GP0 ↔ OLED SDA", '#06B6D4', 21),
        ("Blue: GP1 ↔ OLED SCL", '#3B82F6', 45),
        ("Orange: +3V3 ↔ OLED VCC", '#F97316', 70),
        ("Green: GP2 ↔ SW1 Left", '#10B981', 97),
        ("Yellow: GP5 ↔ Buzzer (+)", '#FACC15', 123),
    ]
    for lbl, col, kx in wire_keys:
        ax.plot([kx, kx + 3.0], [5.5, 5.5], color=col, lw=3)
        ax.text(kx + 4.0, 5.5, lbl, color='#E2E8F0', fontsize=7.0, fontfamily='Segoe UI', va='center')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=120)
    plt.close(fig)
    print(f"Generated: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out = r"C:\Users\white\pocket-companion\assets\journal_media\04_breadboard_prototype_wiring.png"
    create_breadboard_diagram(out)
