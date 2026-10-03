"""
Laboratory Digital Storage Oscilloscope (DSO) Screen Capture Generator
Asset 12: 12_reaction_game_timing_oscilloscope.png
Target: 1920x1080 publication-grade lab instrument screen capture
Authentic Siglent SDS1104X-E / Rigol MSO5000 Mixed-Signal Lab Oscilloscope Interface.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

def generate_oscilloscope_screen(output_path):
    width_px, height_px = 1920, 1080
    dpi = 100
    fig = plt.figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
    
    # Dark instrument chassis background
    fig.patch.set_facecolor('#080C11')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#080C11')
    ax.set_xlim(0, width_px)
    ax.set_ylim(0, height_px)
    ax.axis('off')

    # Channel Colors (Authentic Phosphor Palettes)
    CH1_COLOR = '#FFE600'      # Yellow (BTN_ACTION GP3)
    CH2_COLOR = '#00E5FF'      # Cyan (BUZZER_PWM GP5)
    CH3_COLOR = '#FF2A85'      # Hot Magenta (I2C_SCL GP1)
    CH4_COLOR = '#3B82F6'      # Electric Blue (I2C_SDA GP0)
    DEC_COLOR = '#10B981'      # Decode Green
    GRID_COLOR = '#162332'     # Graticule grid lines
    GRID_CENTER = '#1E3145'    # Center graticule axis
    GRID_TICKS = '#283E56'     # Minor 0.2 div ticks
    SCREEN_BG = '#04070D'      # Ultra-deep phosphor screen CRT black

    # -------------------------------------------------------------
    # 1. INSTRUMENT DISPLAY BEZEL & FRAME
    # -------------------------------------------------------------
    bezel = FancyBboxPatch((10, 10), width_px - 20, height_px - 20,
                           boxstyle="round,pad=0,rounding_size=10",
                           facecolor='#090E15', edgecolor='#1E293B', linewidth=2.5)
    ax.add_patch(bezel)

    # Main Phosphor Screen Viewport
    screen_x, screen_y = 28, 112
    screen_w, screen_h = 1530, 902
    screen_rect = FancyBboxPatch((screen_x, screen_y), screen_w, screen_h,
                                 boxstyle="round,pad=0,rounding_size=6",
                                 facecolor=SCREEN_BG, edgecolor='#1E2E40', linewidth=2)
    ax.add_patch(screen_rect)

    # -------------------------------------------------------------
    # 2. TOP HEADER STATUS BAR (Instrument System State)
    # -------------------------------------------------------------
    header_y = screen_y + screen_h + 10
    
    # Brand and Model banner
    ax.text(screen_x + 12, header_y + 28, "SIGLENT", color='#FFFFFF',
            fontsize=15, fontweight='black', fontfamily='DejaVu Sans', va='center')
    ax.text(screen_x + 98, header_y + 28, "SDS1104X-E", color='#38BDF8',
            fontsize=13, fontweight='bold', fontfamily='DejaVu Sans', va='center')
    ax.text(screen_x + 225, header_y + 28, "Super Phosphor Oscilloscope  100MHz  1GSa/s",
            color='#64748B', fontsize=9.5, fontfamily='DejaVu Sans', va='center')

    # Run / Stop Indicator Badge (Bright Red for STOPPED)
    stop_badge = FancyBboxPatch((screen_x + 550, header_y + 14), 95, 26,
                                boxstyle="round,pad=0,rounding_size=4",
                                facecolor='#DC2626', edgecolor='#EF4444', linewidth=1.5)
    ax.add_patch(stop_badge)
    ax.text(screen_x + 597, header_y + 27, "STOPPED", color='#FFFFFF',
            fontsize=10.5, fontweight='black', fontfamily='DejaVu Sans', ha='center', va='center')

    # Trigger Acquisition Mode (Trig'd in Neon Green)
    trig_badge = FancyBboxPatch((screen_x + 655, header_y + 14), 70, 26,
                                boxstyle="round,pad=0,rounding_size=4",
                                facecolor='#064E3B', edgecolor='#059669', linewidth=1.2)
    ax.add_patch(trig_badge)
    ax.text(screen_x + 690, header_y + 27, "Trig'd", color='#34D399',
            fontsize=10, fontweight='bold', fontfamily='DejaVu Sans', ha='center', va='center')

    # Sample Rate & Memory Depth
    ax.text(screen_x + 745, header_y + 27, "1.00 MSa/s", color='#F1F5F9',
            fontsize=10, fontweight='bold', fontfamily='monospace', va='center')
    ax.text(screen_x + 835, header_y + 27, "14.0 Mpts", color='#94A3B8',
            fontsize=9.2, fontfamily='monospace', va='center')

    # Timebase readout & Delay
    ax.text(screen_x + 920, header_y + 27, "H: 50.0ms/div", color='#F8FAFC',
            fontsize=10.5, fontweight='bold', fontfamily='monospace', va='center')
    ax.text(screen_x + 1045, header_y + 27, "Delay: 0.000s", color='#94A3B8',
            fontsize=9.2, fontfamily='monospace', va='center')

    # Connectivity & System Timestamp
    ax.text(screen_x + 1165, header_y + 27, "LAN: 192.168.1.104",
            color='#38BDF8', fontsize=8.8, fontfamily='monospace', va='center')
    ax.text(screen_x + screen_w - 12, header_y + 28, "2026-10-03  14:22:18",
            color='#94A3B8', fontsize=9.2, fontfamily='monospace', ha='right', va='center')

    # -------------------------------------------------------------
    # 3. OSCILLOSCOPE GRATICULE (14 Horizontal x 8 Vertical Divs)
    # -------------------------------------------------------------
    grat_x, grat_y = screen_x + 36, screen_y + 68
    grat_w, grat_h = screen_w - 68, screen_h - 110

    grat_border = Rectangle((grat_x, grat_y), grat_w, grat_h,
                            facecolor='none', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(grat_border)

    n_hdivs = 14
    n_vdivs = 8
    dx = grat_w / n_hdivs
    dy = grat_h / n_vdivs

    # Grid lines (dotted)
    for i in range(1, n_hdivs):
        gx = grat_x + i * dx
        ax.plot([gx, gx], [grat_y, grat_y + grat_h], color=GRID_COLOR,
                linestyle=':', linewidth=1.0, alpha=0.85)
    for j in range(1, n_vdivs):
        gy = grat_y + j * dy
        ax.plot([grat_x, grat_x + grat_w], [gy, gy], color=GRID_COLOR,
                linestyle=':', linewidth=1.0, alpha=0.85)

    # Center axes with tick marks
    mid_x = grat_x + 7 * dx
    mid_y = grat_y + 4 * dy
    ax.plot([mid_x, mid_x], [grat_y, grat_y + grat_h], color=GRID_CENTER, linewidth=1.2)
    ax.plot([grat_x, grat_x + grat_w], [mid_y, mid_y], color=GRID_CENTER, linewidth=1.2)

    # Subticks along center axes
    for sub in np.linspace(grat_x, grat_x + grat_w, n_hdivs * 5 + 1):
        ax.plot([sub, sub], [mid_y - 3, mid_y + 3], color=GRID_TICKS, linewidth=0.8)
    for sub in np.linspace(grat_y, grat_y + grat_h, n_vdivs * 5 + 1):
        ax.plot([mid_x - 3, mid_x + 3], [sub, sub], color=GRID_TICKS, linewidth=0.8)

    # Trigger point indicator (top inverted triangle at center)
    trig_marker = Polygon([[mid_x - 7, grat_y + grat_h + 8],
                           [mid_x + 7, grat_y + grat_h + 8],
                           [mid_x, grat_y + grat_h]],
                          closed=True, facecolor='#F59E0B', edgecolor='#D97706')
    ax.add_patch(trig_marker)
    ax.text(mid_x, grat_y + grat_h + 16, "T", color='#F59E0B',
            fontsize=8.5, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------
    # 4. WAVEFORM CHANNELS & PHYSICS
    # -------------------------------------------------------------
    time_pts = 14000
    t_ms = np.linspace(-350.0, 350.0, time_pts)
    x_coords = grat_x + ((t_ms - (-350.0)) / 700.0) * grat_w

    t_x1 = -92.1   # Buzzer Start Tone Stimulus
    t_x2 = +92.1   # User Button Press Falling Edge
    px_x1 = grat_x + ((t_x1 - (-350.0)) / 700.0) * grat_w
    px_x2 = grat_x + ((t_x2 - (-350.0)) / 700.0) * grat_w

    np.random.seed(42)

    # --- CHANNEL 1: BTN_ACTION (GP3 Active-Low Input) ---
    ch1_gnd = grat_y + 0.8 * dy
    ch1_vscale = dy * 0.44
    ch1_v = np.ones_like(t_ms) * 3.32
    for i, t in enumerate(t_ms):
        if t < t_x2:
            ch1_v[i] = 3.32 + np.random.normal(0, 0.012)
        elif t < t_x2 + 0.25:
            alpha = (t - t_x2) / 0.25
            ch1_v[i] = 3.32 * (1.0 - alpha) + np.random.normal(0, 0.02)
        elif t < t_x2 + 1.2:
            t_ring = (t - (t_x2 + 0.25))
            bounce = 0.32 * np.exp(-t_ring / 0.35) * np.sin(2 * np.pi * 3.5 * t_ring)
            ch1_v[i] = max(0.01, bounce + np.random.normal(0, 0.015))
        else:
            ch1_v[i] = 0.02 + np.random.normal(0, 0.008)
    ch1_y = ch1_gnd + ch1_v * ch1_vscale

    # --- CHANNEL 2: BUZZER_PWM (GP5 2.4kHz Audio Tone Stimulus) ---
    ch2_gnd = grat_y + 2.7 * dy
    ch2_vscale = dy * 0.42
    ch2_v = np.zeros_like(t_ms)
    burst_start = t_x1
    burst_end = t_x1 + 80.0
    freq_khz = 2.401
    for i, t in enumerate(t_ms):
        if burst_start <= t <= burst_end:
            phase = (t - burst_start) * freq_khz * 2 * np.pi
            sq = np.sign(np.sin(phase))
            val = 3.28 if sq > 0 else 0.03
            val += np.random.normal(0, 0.015)
            ch2_v[i] = val
        else:
            ch2_v[i] = 0.02 + np.random.normal(0, 0.008)
    ch2_y = ch2_gnd + ch2_v * ch2_vscale

    # --- CHANNEL 3: I2C_SCL (GP1 400kHz OLED Clock) ---
    ch3_gnd = grat_y + 4.5 * dy
    ch3_vscale = dy * 0.35
    ch3_v = np.ones_like(t_ms) * 3.30
    for i, t in enumerate(t_ms):
        in_packet_1 = (-160.0 <= t <= -100.0)
        in_packet_2 = (+105.0 <= t <= +155.0)
        if in_packet_1 or in_packet_2:
            phase = (t * 400.0) * 2 * np.pi
            sq = np.sign(np.sin(phase))
            byte_cycle = int((t * 400.0)) % 9
            if byte_cycle == 8:
                ch3_v[i] = 3.28 + np.random.normal(0, 0.02)
            else:
                ch3_v[i] = (3.28 if sq > 0 else 0.05) + np.random.normal(0, 0.02)
        else:
            ch3_v[i] = 3.30 + np.random.normal(0, 0.01)
    ch3_y = ch3_gnd + ch3_v * ch3_vscale

    # --- CHANNEL 4: I2C_SDA (GP0 OLED Framebuffer Data) ---
    ch4_gnd = grat_y + 6.0 * dy
    ch4_vscale = dy * 0.35
    ch4_v = np.ones_like(t_ms) * 3.30
    for i, t in enumerate(t_ms):
        in_packet_1 = (-160.0 <= t <= -100.0)
        in_packet_2 = (+105.0 <= t <= +155.0)
        if in_packet_1:
            pseudo_data = np.sin(t * 85.0) + np.cos(t * 190.0)
            ch4_v[i] = (3.26 if pseudo_data > 0 else 0.05) + np.random.normal(0, 0.02)
        elif in_packet_2:
            pseudo_data = np.sin(t * 95.0) - np.cos(t * 140.0)
            ch4_v[i] = (3.26 if pseudo_data > 0 else 0.05) + np.random.normal(0, 0.02)
        else:
            ch4_v[i] = 3.30 + np.random.normal(0, 0.01)
    ch4_y = ch4_gnd + ch4_v * ch4_vscale

    # -------------------------------------------------------------
    # 5. RENDER PHOSPHOR TRACES
    # -------------------------------------------------------------
    traces = [
        (x_coords, ch1_y, CH1_COLOR),
        (x_coords, ch2_y, CH2_COLOR),
        (x_coords, ch3_y, CH3_COLOR),
        (x_coords, ch4_y, CH4_COLOR),
    ]
    for xs, ys, col in traces:
        ax.plot(xs, ys, color=col, linewidth=4.5, alpha=0.18, solid_capstyle='round')
        ax.plot(xs, ys, color=col, linewidth=2.4, alpha=0.48, solid_capstyle='round')
        ax.plot(xs, ys, color=col, linewidth=1.1, alpha=0.98, solid_capstyle='round')

    # Ground Reference Arrow Markers on left edge
    gnd_markers = [
        (ch1_gnd, CH1_COLOR, "1"),
        (ch2_gnd, CH2_COLOR, "2"),
        (ch3_gnd, CH3_COLOR, "3"),
        (ch4_gnd, CH4_COLOR, "4")
    ]
    for gy, col, num in gnd_markers:
        tag = Polygon([[grat_x - 22, gy + 8],
                       [grat_x - 6, gy],
                       [grat_x - 22, gy - 8]],
                      closed=True, facecolor=col, edgecolor='#000000', linewidth=1)
        ax.add_patch(tag)
        ax.text(grat_x - 16, gy, num, color='#000000', fontsize=8, fontweight='black',
                ha='center', va='center')

    # Trigger level marker on right edge
    trig_y_px = ch2_gnd + 1.65 * ch2_vscale
    trig_tag = Polygon([[grat_x + grat_w + 22, trig_y_px + 8],
                        [grat_x + grat_w + 6, trig_y_px],
                        [grat_x + grat_w + 22, trig_y_px - 8]],
                       closed=True, facecolor=CH2_COLOR, edgecolor='#000000', linewidth=1)
    ax.add_patch(trig_tag)
    ax.text(grat_x + grat_w + 15, trig_y_px, "T", color='#000000',
            fontsize=8, fontweight='black', ha='center', va='center')

    # Channel Labels on Screen
    ax.text(grat_x + 15, ch4_gnd + 3.4 * ch4_vscale, "CH4: I2C_SDA (GP0 Framebuffer Data 3.3V)",
            color=CH4_COLOR, fontsize=8.5, fontweight='bold', fontfamily='monospace')
    ax.text(grat_x + 15, ch3_gnd + 3.4 * ch3_vscale, "CH3: I2C_SCL (GP1 400kHz OLED Clock 3.3V)",
            color=CH3_COLOR, fontsize=8.5, fontweight='bold', fontfamily='monospace')
    ax.text(grat_x + 15, ch2_gnd + 3.4 * ch2_vscale, "CH2: BUZZER_PWM (GP5 2.4kHz Start Tone Stimulus)",
            color=CH2_COLOR, fontsize=8.5, fontweight='bold', fontfamily='monospace')
    ax.text(grat_x + 15, ch1_gnd + 3.4 * ch1_vscale, "CH1: BTN_ACTION (GP3 Active-Low User Input)",
            color=CH1_COLOR, fontsize=8.5, fontweight='bold', fontfamily='monospace')

    # -------------------------------------------------------------
    # 6. PROTOCOL DECODE BUS: I2C BUS PACKET TRACK
    # -------------------------------------------------------------
    dec_y = grat_y + 7.42 * dy
    ax.plot([grat_x, grat_x + grat_w], [dec_y, dec_y], color='#1E293B', linewidth=1)
    
    ax.text(grat_x + 12, dec_y + 14, "DEC 1: I2C  [ SCL: CH3 · SDA: CH4 · 400 kbps · Address 7-bit · Hex ]",
            color=DEC_COLOR, fontsize=8.5, fontweight='bold', fontfamily='monospace')

    # Decode packets around stimulus frame (-160 ms to -100 ms)
    dec_start_x = grat_x + ((-165.0 - (-350.0)) / 700.0) * grat_w
    dec_end_x = grat_x + ((-95.0 - (-350.0)) / 700.0) * grat_w
    dec_w_total = dec_end_x - dec_start_x
    
    packets = [
        ("S", 0.08, '#10B981', '#064E3B'),
        ("0x3C [W]", 0.23, '#F59E0B', '#78350F'),
        ("~A", 0.07, '#10B981', '#064E3B'),
        ("0x40 [Co]", 0.22, '#38BDF8', '#075985'),
        ("~A", 0.07, '#10B981', '#064E3B'),
        ("0x7E", 0.16, '#EC4899', '#831843'),
        ("~A", 0.07, '#10B981', '#064E3B'),
        ("P", 0.10, '#EF4444', '#7F1D1D')
    ]
    cur_x = dec_start_x
    for lbl, frac, fcol, bcol in packets:
        pw = frac * dec_w_total
        pbox = FancyBboxPatch((cur_x, dec_y - 12), pw - 1.5, 20,
                              boxstyle="round,pad=0,rounding_size=3",
                              facecolor=bcol, edgecolor=fcol, linewidth=1, alpha=0.95)
        ax.add_patch(pbox)
        ax.text(cur_x + pw/2, dec_y - 2, lbl, color='#FFFFFF', fontsize=7.5,
                fontweight='bold', fontfamily='monospace', ha='center', va='center')
        cur_x += pw

    # Post-reaction update packets (+105 ms to +155 ms)
    dec_start_x2 = grat_x + ((+105.0 - (-350.0)) / 700.0) * grat_w
    dec_end_x2 = grat_x + ((+155.0 - (-350.0)) / 700.0) * grat_w
    dec_w_total2 = dec_end_x2 - dec_start_x2
    packets2 = [
        ("S", 0.09, '#10B981', '#064E3B'),
        ("0x3C [W]", 0.25, '#F59E0B', '#78350F'),
        ("~A", 0.08, '#10B981', '#064E3B'),
        ("0x40 [Co]", 0.24, '#38BDF8', '#075985'),
        ("~A", 0.08, '#10B981', '#064E3B'),
        ("0xFF", 0.16, '#A855F7', '#581C87'),
        ("P", 0.10, '#EF4444', '#7F1D1D')
    ]
    cur_x2 = dec_start_x2
    for lbl, frac, fcol, bcol in packets2:
        pw = frac * dec_w_total2
        pbox = FancyBboxPatch((cur_x2, dec_y - 12), pw - 1.5, 20,
                              boxstyle="round,pad=0,rounding_size=3",
                              facecolor=bcol, edgecolor=fcol, linewidth=1, alpha=0.95)
        ax.add_patch(pbox)
        ax.text(cur_x2 + pw/2, dec_y - 2, lbl, color='#FFFFFF', fontsize=7.2,
                fontweight='bold', fontfamily='monospace', ha='center', va='center')
        cur_x2 += pw

    # -------------------------------------------------------------
    # 7. TIME CURSORS (X1 = -92.1 ms, X2 = +92.1 ms)
    # -------------------------------------------------------------
    ax.plot([px_x1, px_x1], [grat_y, grat_y + grat_h], color='#F59E0B',
            linestyle='--', linewidth=1.5, alpha=0.95)
    ax.plot([px_x2, px_x2], [grat_y, grat_y + grat_h], color='#F59E0B',
            linestyle='--', linewidth=1.5, alpha=0.95)

    flag1 = FancyBboxPatch((px_x1 - 18, grat_y + grat_h - 2), 36, 18,
                           boxstyle="round,pad=0,rounding_size=3",
                           facecolor='#B45309', edgecolor='#F59E0B', linewidth=1.2)
    ax.add_patch(flag1)
    ax.text(px_x1, grat_y + grat_h + 7, "AX", color='#FFFFFF',
            fontsize=8.5, fontweight='bold', ha='center', va='center')

    flag2 = FancyBboxPatch((px_x2 - 18, grat_y + grat_h - 2), 36, 18,
                           boxstyle="round,pad=0,rounding_size=3",
                           facecolor='#B45309', edgecolor='#F59E0B', linewidth=1.2)
    ax.add_patch(flag2)
    ax.text(px_x2, grat_y + grat_h + 7, "BX", color='#FFFFFF',
            fontsize=8.5, fontweight='bold', ha='center', va='center')

    bracket_y = grat_y + grat_h - 38
    ax.annotate("", xy=(px_x1, bracket_y), xytext=(px_x2, bracket_y),
                arrowprops=dict(arrowstyle="<->", color="#F59E0B", lw=2.0))
    dt_pill_w = 300
    dt_pill = FancyBboxPatch(((px_x1 + px_x2)/2 - dt_pill_w/2, bracket_y - 13), dt_pill_w, 26,
                             boxstyle="round,pad=0,rounding_size=5",
                             facecolor='#111827', edgecolor='#F59E0B', linewidth=1.6)
    ax.add_patch(dt_pill)
    ax.text((px_x1 + px_x2)/2, bracket_y, "ΔX = 184.2 ms  (1/ΔX = 5.43 Hz)",
            color='#FDE047', fontsize=10, fontweight='black', fontfamily='monospace',
            ha='center', va='center')

    # Event callout pills
    callout1 = FancyBboxPatch((px_x1 - 195, ch2_gnd + 1.8 * ch2_vscale), 185, 34,
                              boxstyle="round,pad=0,rounding_size=4",
                              facecolor='#06202A', edgecolor=CH2_COLOR, linewidth=1)
    ax.add_patch(callout1)
    ax.text(px_x1 - 102, ch2_gnd + 1.8 * ch2_vscale + 17, "Start Stimulus Tone\n(Buzzer PWM 2.4kHz ON)",
            color='#E0F2FE', fontsize=8, fontweight='bold', ha='center', va='center')
    ax.annotate("", xy=(px_x1, ch2_gnd + 1.0 * ch2_vscale),
                xytext=(px_x1 - 10, ch2_gnd + 1.8 * ch2_vscale + 17),
                arrowprops=dict(arrowstyle="->", color=CH2_COLOR, lw=1.2))

    callout2 = FancyBboxPatch((px_x2 - 195, ch1_gnd + 1.8 * ch1_vscale), 185, 34,
                              boxstyle="round,pad=0,rounding_size=4",
                              facecolor='#26200A', edgecolor=CH1_COLOR, linewidth=1)
    ax.add_patch(callout2)
    ax.text(px_x2 - 102, ch1_gnd + 1.8 * ch1_vscale + 17, "User Button Reaction\n(BTN_ACTION GP3 Fall)",
            color='#FEF08A', fontsize=8, fontweight='bold', ha='center', va='center')
    ax.annotate("", xy=(px_x2, ch1_gnd + 0.8 * ch1_vscale),
                xytext=(px_x2 - 10, ch1_gnd + 1.8 * ch1_vscale + 17),
                arrowprops=dict(arrowstyle="->", color=CH1_COLOR, lw=1.2))

    # -------------------------------------------------------------
    # 8. PICTURE-IN-PICTURE HIGH-SPEED ZOOM INSET (Z1: 20 µs/div)
    # -------------------------------------------------------------
    # Positioned cleanly in the lower-right quadrant of the graticule
    zoom_w, zoom_h = 390, 175
    zoom_x = grat_x + grat_w - zoom_w - 20
    zoom_y = grat_y + 18
    
    zoom_box = FancyBboxPatch((zoom_x, zoom_y), zoom_w, zoom_h,
                              boxstyle="round,pad=0,rounding_size=6",
                              facecolor='#020617', edgecolor='#38BDF8', linewidth=1.6, alpha=0.98)
    ax.add_patch(zoom_box)
    
    # Zoom header
    ax.text(zoom_x + 12, zoom_y + zoom_h - 14, "ZOOM [Z1]  20.0 µs / div",
            color='#38BDF8', fontsize=9, fontweight='bold', fontfamily='monospace')
    ax.text(zoom_x + zoom_w - 12, zoom_y + zoom_h - 14, "100 MSa/s (Interp Sin(x)/x)",
            color='#94A3B8', fontsize=8, fontfamily='monospace', ha='right')

    # Zoom internal graticule
    for izx in np.linspace(zoom_x + 15, zoom_x + zoom_w - 15, 8):
        ax.plot([izx, izx], [zoom_y + 12, zoom_y + zoom_h - 26], color='#1E293B', linestyle=':', lw=0.6)
    for izy in np.linspace(zoom_y + 12, zoom_y + zoom_h - 26, 5):
        ax.plot([zoom_x + 15, zoom_x + zoom_w - 15], [izy, izy], color='#1E293B', linestyle=':', lw=0.6)

    # Inset waveforms
    z_t = np.linspace(0, 140, 500)
    z_px = np.linspace(zoom_x + 15, zoom_x + zoom_w - 15, 500)
    
    # 400kHz SCL clock wave (period = 2.5 µs, Tr = 182 ns)
    z_scl = []
    for t_us in z_t:
        t_cycle = t_us % 2.5
        if t_cycle < 1.25:
            val = 0.05 + 0.04 * np.exp(-t_cycle / 0.1)
        else:
            tr = t_cycle - 1.25
            val = 3.3 * (1.0 - np.exp(-tr / 0.28))
        z_scl.append(val)
    z_scl = np.array(z_scl)
    z_scl_py = zoom_y + 88 + z_scl * 10
    ax.plot(z_px, z_scl_py, color=CH3_COLOR, lw=1.3)
    ax.text(zoom_x + 16, zoom_y + 132, "CH3: SCL 400kHz (Tr=182ns)", color=CH3_COLOR, fontsize=7.5, fontfamily='monospace', fontweight='bold')

    # Buzzer PWM wave in zoom (period = 416.5 µs)
    z_pwm = []
    for t_us in z_t:
        val = 3.28 if (t_us % 416.5) < 208.25 else 0.03
        z_pwm.append(val)
    z_pwm = np.array(z_pwm)
    z_pwm_py = zoom_y + 24 + z_pwm * 9
    ax.plot(z_px, z_pwm_py, color=CH2_COLOR, lw=1.3)
    ax.text(zoom_x + 16, zoom_y + 64, "CH2: PWM 2.4kHz (Duty 50.1%)", color=CH2_COLOR, fontsize=7.5, fontfamily='monospace', fontweight='bold')

    # -------------------------------------------------------------
    # 9. RIGHT SIDEBAR DOCK (Rigol/Siglent Cursors & Measurements)
    # -------------------------------------------------------------
    dock_x = screen_x + screen_w + 12
    dock_y = screen_y
    dock_w = width_px - dock_x - 28
    dock_h = screen_h

    dock_bg = FancyBboxPatch((dock_x, dock_y), dock_w, dock_h,
                             boxstyle="round,pad=0,rounding_size=6",
                             facecolor='#0F1722', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(dock_bg)

    # Sidebar Header
    menu_head = FancyBboxPatch((dock_x + 8, dock_y + dock_h - 40), dock_w - 16, 32,
                               boxstyle="round,pad=0,rounding_size=4",
                               facecolor='#1E293B', edgecolor='#334155', linewidth=1)
    ax.add_patch(menu_head)
    ax.text(dock_x + dock_w/2, dock_y + dock_h - 24, "MEASURE / CURSOR",
            color='#38BDF8', fontsize=11, fontweight='black', fontfamily='DejaVu Sans', ha='center', va='center')

    # Softkeys list
    softkeys = [
        ("CURSOR MODE", "Manual (Time X)"),
        ("SOURCE A", "CH2 (BUZZER_PWM)"),
        ("SOURCE B", "CH1 (BTN_ACTION)"),
        ("Cur A (X1)", "-92.10 ms"),
        ("Cur B (X2)", "+92.10 ms"),
        ("ΔX (Reaction)", "184.20 ms"),
        ("1 / ΔX", "5.429 Hz"),
        ("ΔY (CH1)", "-3.300 V"),
        ("ΔY (CH2)", "+3.250 V"),
    ]

    sk_y = dock_y + dock_h - 56
    for title, val in softkeys:
        sk_y -= 43
        sk_box = FancyBboxPatch((dock_x + 10, sk_y), dock_w - 20, 37,
                                boxstyle="round,pad=0,rounding_size=3",
                                facecolor='#111827', edgecolor='#1F2937', linewidth=1)
        ax.add_patch(sk_box)
        ax.text(dock_x + 18, sk_y + 24, title, color='#64748B', fontsize=7.5,
                fontweight='bold', fontfamily='DejaVu Sans')
        val_color = '#FDE047' if '184.20' in val else '#F1F5F9'
        ax.text(dock_x + 18, sk_y + 9, val, color=val_color, fontsize=9.5,
                fontweight='bold', fontfamily='monospace')

    # Measurements Table Section at bottom of sidebar
    meas_y_start = sk_y - 18
    ax.plot([dock_x + 10, dock_x + dock_w - 10], [meas_y_start, meas_y_start],
            color='#334155', linewidth=1)
    ax.text(dock_x + dock_w/2, meas_y_start - 14, "HARDWARE PARAMETERS",
            color='#94A3B8', fontsize=8.5, fontweight='bold', ha='center')

    params = [
        ("CH1 Vpp", "3.32 V", CH1_COLOR),
        ("CH1 Vmin", "0.02 V", CH1_COLOR),
        ("CH1 Fall", "1.42 µs", CH1_COLOR),
        ("CH2 Freq", "2.401 kHz", CH2_COLOR),
        ("CH2 Vpp", "3.28 V", CH2_COLOR),
        ("CH2 Burst", "80.0 ms", CH2_COLOR),
        ("CH3 Freq", "398.4 kHz", CH3_COLOR),
        ("CH4 Duty", "49.1 %", CH4_COLOR),
    ]

    py_cur = meas_y_start - 36
    for pname, pval, pcol in params:
        pbox = FancyBboxPatch((dock_x + 10, py_cur), dock_w - 20, 26,
                              boxstyle="round,pad=0,rounding_size=2",
                              facecolor='#030712', edgecolor='#111827', linewidth=0.8)
        ax.add_patch(pbox)
        ax.text(dock_x + 18, py_cur + 13, pname, color='#94A3B8', fontsize=8,
                fontweight='bold', fontfamily='monospace', va='center')
        ax.text(dock_x + dock_w - 18, py_cur + 13, pval, color=pcol, fontsize=8.5,
                fontweight='bold', fontfamily='monospace', ha='right', va='center')
        py_cur -= 30

    # -------------------------------------------------------------
    # 10. BOTTOM CHANNEL STATUS DOCK (CH1 - CH4 Badges)
    # -------------------------------------------------------------
    bot_y = 30
    bot_h = 72
    ch_box_w = 265
    
    ch_configs = [
        (1, "CH1", "1.00V/div", "1X DC", "0.00V", CH1_COLOR, 'BTN_ACTION (GP3)'),
        (2, "CH2", "1.00V/div", "1X DC", "0.00V", CH2_COLOR, 'BUZZER_PWM (GP5)'),
        (3, "CH3", "1.00V/div", "1X DC", "0.00V", CH3_COLOR, 'I2C_SCL (GP1)'),
        (4, "CH4", "1.00V/div", "1X DC", "0.00V", CH4_COLOR, 'I2C_SDA (GP0)'),
    ]

    cur_bx = screen_x
    for ch_num, ch_tag, v_div, coup, offset, ccol, cdesc in ch_configs:
        cbox = FancyBboxPatch((cur_bx, bot_y), ch_box_w, bot_h,
                              boxstyle="round,pad=0,rounding_size=5",
                              facecolor='#111827', edgecolor=ccol, linewidth=1.5)
        ax.add_patch(cbox)
        
        cnum_box = FancyBboxPatch((cur_bx + 8, bot_y + bot_h - 26), 24, 18,
                                  boxstyle="round,pad=0,rounding_size=3",
                                  facecolor=ccol, edgecolor='none')
        ax.add_patch(cnum_box)
        ax.text(cur_bx + 20, bot_y + bot_h - 17, str(ch_num), color='#000000',
                fontsize=9.5, fontweight='black', ha='center', va='center')

        ax.text(cur_bx + 38, bot_y + bot_h - 17, ch_tag, color='#FFFFFF',
                fontsize=9, fontweight='bold', va='center')
        ax.text(cur_bx + 85, bot_y + bot_h - 17, f"{v_div}  {coup}",
                color=ccol, fontsize=8.5, fontweight='bold', fontfamily='monospace', va='center')

        ax.text(cur_bx + 10, bot_y + 24, cdesc, color='#E2E8F0',
                fontsize=8, fontweight='bold', va='center')
        ax.text(cur_bx + 10, bot_y + 10, f"Offset: {offset} · BW: 20MHz",
                color='#64748B', fontsize=7.2, fontfamily='monospace', va='center')

        cur_bx += ch_box_w + 10

    # Trigger & Timebase status badge at bottom right of screen
    trig_info_w = screen_x + screen_w - cur_bx
    tibox = FancyBboxPatch((cur_bx, bot_y), trig_info_w, bot_h,
                           boxstyle="round,pad=0,rounding_size=5",
                           facecolor='#0F172A', edgecolor='#334155', linewidth=1.2)
    ax.add_patch(tibox)
    ax.text(cur_bx + 15, bot_y + bot_h - 17, "TRIG: SLOW / FALLING EDGE", color='#F8FAFC',
            fontsize=9, fontweight='bold', va='center')
    ax.text(cur_bx + 15, bot_y + 30, "Source: CH1 (GP3)  1.00V/div  Run/Stop: STOPPED",
            color='#94A3B8', fontsize=8, fontfamily='monospace', va='center')
    ax.text(cur_bx + 15, bot_y + 12, "Coupling: DC · Noise Reject: ON · 50.0ms/div",
            color='#38BDF8', fontsize=7.5, fontfamily='monospace', va='center')

    # Save exactly 1920x1080
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(output_path, dpi=dpi, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Oscilloscope Screen Generated successfully: {output_path}")

if __name__ == "__main__":
    out_file = r"C:\Users\white\pocket-companion\assets\journal_media\12_reaction_game_timing_oscilloscope.png"
    generate_oscilloscope_screen(out_file)
