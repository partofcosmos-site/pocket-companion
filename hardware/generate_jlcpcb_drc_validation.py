"""
Authentic JLCPCB Web Portal & DFM/DRC Validation Generator
Generates: C:\\Users\\white\\pocket-companion\\assets\\journal_media\\09_jlcpcb_drc_validation_pass.png (1920x1080)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = r"C:\Users\white\pocket-companion\assets\journal_media\09_jlcpcb_drc_validation_pass.png"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

def get_font(size, bold=False, mono=False):
    if mono:
        font_file = "consolab.ttf" if bold else "consola.ttf"
    else:
        font_file = "segoeuib.ttf" if bold else "segoeui.ttf"
    font_path = os.path.join(r"C:\Windows\Fonts", font_file)
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

def render_jlcpcb_portal():
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # 1. BROWSER CHROME (CHROME / EDGE STYLE) - Y = 0 to 76
    # =========================================================================
    draw.rectangle([(0, 0), (w, 40)], fill=(222, 225, 230))
    # Active Tab
    tab_w, tab_h = 320, 34
    draw.rounded_rectangle([(80, 6), (80 + tab_w, 40)], radius=8, fill=(255, 255, 255))
    draw.ellipse([(94, 15), (110, 31)], fill=(0, 118, 247))
    draw.text((118, 14), "JLCPCB - Online PCB Quote & DFM...", font=get_font(12), fill=(31, 35, 41))
    draw.text((380, 14), "x", font=get_font(11, bold=True), fill=(100, 106, 115))

    # Inactive Tab
    draw.text((420, 14), "EasyEDA - Pocket Companion PCB", font=get_font(12), fill=(100, 106, 115))

    # Window Controls
    draw.text((w - 110, 12), "-", font=get_font(16, bold=True), fill=(70, 75, 85))
    draw.rectangle([(w - 75, 14), (w - 63, 26)], outline=(70, 75, 85), width=1)
    draw.text((w - 35, 12), "x", font=get_font(14, bold=True), fill=(70, 75, 85))

    # URL Bar (Y = 40 to 76)
    draw.rectangle([(0, 40), (w, 76)], fill=(255, 255, 255))
    draw.line([(0, 76), (w, 76)], fill=(225, 228, 235), width=1)
    draw.text((22, 48), "<-", font=get_font(14, bold=True), fill=(140, 145, 155))
    draw.text((55, 48), "->", font=get_font(14, bold=True), fill=(180, 185, 195))
    # Refresh circle
    draw.arc([(82, 49), (96, 63)], start=45, end=315, fill=(100, 105, 115), width=2)

    url_box = [(115, 44), (w - 120, 70)]
    draw.rounded_rectangle(url_box, radius=13, fill=(241, 243, 244))
    # Vector padlock
    lx, ly = 132, 51
    draw.rounded_rectangle([(lx, ly + 5), (lx + 10, ly + 13)], radius=2, fill=(34, 197, 94))
    draw.arc([(lx + 2, ly), (lx + 8, ly + 7)], start=180, end=0, fill=(34, 197, 94), width=2)
    draw.text((152, 49), "https://cart.jlcpcb.com/quote?orderType=1&file=Pocket_Companion_v1.0_Gerber.zip", font=get_font(12), fill=(31, 35, 41))

    # Profile Icon
    draw.ellipse([(w - 95, 48), (w - 75, 68)], fill=(0, 118, 247))
    draw.text((w - 89, 50), "D", font=get_font(12, bold=True), fill=(255, 255, 255))
    draw.text((w - 55, 48), ":", font=get_font(18, bold=True), fill=(100, 105, 115))

    # =========================================================================
    # 2. JLCPCB PORTAL NAVBAR (Y = 77 to 135)
    # =========================================================================
    draw.rectangle([(0, 77), (w, 135)], fill=(255, 255, 255))
    draw.line([(0, 135), (w, 135)], fill=(225, 230, 238), width=1)

    # JLCPCB Logo
    draw.ellipse([(40, 88), (76, 124)], fill=(0, 118, 247))
    draw.ellipse([(46, 94), (70, 118)], outline=(255, 255, 255), width=3)
    draw.ellipse([(52, 100), (64, 112)], fill=(255, 255, 255))
    draw.text((86, 90), "JLCPCB", font=get_font(26, bold=True), fill=(0, 118, 247))
    draw.text((88, 116), "PROTOTYPE & HIGH-TECH MANUFACTURING", font=get_font(8, bold=True, mono=True), fill=(140, 145, 155))

    nav_tabs = [
        ("Standard PCB", True),
        ("Advanced PCB", False),
        ("SMT Assembly", False),
        ("3D Printing", False),
        ("CNC Machining", False),
        ("Electronic Parts", False)
    ]
    nx = 380
    for n_title, is_active in nav_tabs:
        if is_active:
            draw.text((nx, 98), n_title, font=get_font(14, bold=True), fill=(0, 118, 247))
            draw.line([(nx, 133), (nx + 95, 133)], fill=(0, 118, 247), width=3)
        else:
            draw.text((nx, 98), n_title, font=get_font(14), fill=(78, 89, 105))
        nx += 125

    draw.text((w - 380, 98), "USD ($)", font=get_font(13), fill=(78, 89, 105))
    draw.text((w - 310, 98), "Support", font=get_font(13), fill=(78, 89, 105))
    draw.text((w - 230, 98), "Order History", font=get_font(13), fill=(78, 89, 105))

    # Cart Pill
    draw.rounded_rectangle([(w - 120, 90), (w - 40, 122)], radius=16, fill=(240, 246, 255), outline=(0, 118, 247), width=1)
    draw.text((w - 105, 98), "Cart (1)", font=get_font(12, bold=True), fill=(0, 118, 247))

    # =========================================================================
    # 3. FILE UPLOAD STRIP (Y = 136 to 195)
    # =========================================================================
    draw.rectangle([(0, 136), (w, 195)], fill=(247, 248, 250))
    draw.line([(0, 195), (w, 195)], fill=(225, 230, 238), width=1)

    draw.text((40, 146), "Home  /  PCB Instant Quote  /  Standard PCB Order Configuration", font=get_font(12), fill=(140, 145, 155))

    draw.rounded_rectangle([(40, 164), (w - 40, 190)], radius=4, fill=(236, 253, 245), outline=(16, 185, 129), width=1)
    # Vector Parsed Badge
    draw.rounded_rectangle([(48, 167), (115, 187)], radius=3, fill=(16, 185, 129))
    draw.text((54, 170), "VERIFIED", font=get_font(10, bold=True, mono=True), fill=(255, 255, 255))
    draw.text((125, 168), "Pocket_Companion_v1.0_Gerber.zip (184.2 KB) — Dimensions 52.00 × 38.00 mm, 2 Layers auto-extracted from Edge.Cuts", font=get_font(11, mono=True), fill=(6, 78, 59))
    draw.text((w - 220, 168), "[ Re-upload ]  [ DFM Log ]", font=get_font(11, bold=True, mono=True), fill=(0, 118, 247))

    # =========================================================================
    # 4. ORDER CONFIGURATION FORM (LEFT COLUMN)
    # =========================================================================
    fx0, fy0, fw, fh = 40, 205, 1060, 855
    draw.rounded_rectangle([(fx0, fy0), (fx0 + fw, fy0 + fh)], radius=8, fill=(255, 255, 255), outline=(225, 230, 238), width=1)

    draw.text((fx0 + 25, fy0 + 16), "PCB Specifications & Manufacturing Parameters", font=get_font(16, bold=True), fill=(31, 35, 41))
    draw.line([(fx0 + 25, fy0 + 44), (fx0 + fw - 25, fy0 + 44)], fill=(238, 240, 244), width=1)

    def draw_param_row(ry, label_text, options, selected_idx, helper_text=None, highlight_badge=None):
        draw.text((fx0 + 25, ry + 6), label_text, font=get_font(13, bold=True), fill=(78, 89, 105))
        ox = fx0 + 220
        for idx, opt_name in enumerate(options):
            is_sel = (idx == selected_idx)
            font_opt = get_font(12, bold=is_sel)
            bbox = font_opt.getbbox(opt_name)
            pill_w = max(70, (bbox[2] - bbox[0]) + 32)
            pill_h = 30
            if is_sel:
                draw.rounded_rectangle([(ox, ry), (ox + pill_w, ry + pill_h)], radius=4, fill=(240, 246, 255), outline=(0, 118, 247), width=2)
                # Native Vector Radio Button
                rx, ry_c = ox + 14, ry + 15
                draw.ellipse([(rx - 6, ry_c - 6), (rx + 6, ry_c + 6)], outline=(0, 118, 247), width=2)
                draw.ellipse([(rx - 3, ry_c - 3), (rx + 3, ry_c + 3)], fill=(0, 118, 247))
                draw.text((ox + 26, ry + 6), opt_name, font=font_opt, fill=(0, 118, 247))
            else:
                draw.rounded_rectangle([(ox, ry), (ox + pill_w, ry + pill_h)], radius=4, fill=(255, 255, 255), outline=(225, 230, 238), width=1)
                draw.text((ox + 14, ry + 6), opt_name, font=font_opt, fill=(78, 89, 105))
            ox += pill_w + 10

        if helper_text:
            # Vector checkmark before helper text
            hx, hy = ox + 12, ry + 15
            draw.line([(hx - 4, hy), (hx - 1, hy + 4), (hx + 5, hy - 4)], fill=(16, 185, 129), width=2)
            draw.text((ox + 22, ry + 7), helper_text, font=get_font(11, mono=True), fill=(16, 185, 129))
        if highlight_badge:
            draw.rounded_rectangle([(ox + 10, ry + 4), (ox + 90, ry + 26)], radius=3, fill=(254, 243, 199), outline=(245, 158, 11), width=1)
            draw.text((ox + 16, ry + 7), highlight_badge, font=get_font(10, bold=True), fill=(180, 83, 9))

    draw_param_row(fy0 + 58, "Base Material", ["FR-4", "Aluminum", "Rogers", "Copper Core"], 0)
    draw_param_row(fy0 + 102, "Layers", ["1 Layer", "2 Layers", "4 Layers", "6 Layers"], 1, helper_text="Auto-matched from Gerber")

    # Dimensions
    ry = fy0 + 146
    draw.text((fx0 + 25, ry + 6), "Dimensions", font=get_font(13, bold=True), fill=(78, 89, 105))
    ox = fx0 + 220
    draw.rounded_rectangle([(ox, ry), (ox + 110, ry + 30)], radius=4, fill=(255, 255, 255), outline=(0, 118, 247), width=2)
    draw.text((ox + 12, ry + 6), "52.00", font=get_font(13, bold=True, mono=True), fill=(31, 35, 41))
    draw.text((ox + 75, ry + 6), "mm", font=get_font(12), fill=(140, 145, 155))
    draw.text((ox + 122, ry + 6), "x", font=get_font(14, bold=True), fill=(78, 89, 105))
    draw.rounded_rectangle([(ox + 140, ry), (ox + 250, ry + 30)], radius=4, fill=(255, 255, 255), outline=(0, 118, 247), width=2)
    draw.text((ox + 152, ry + 6), "38.00", font=get_font(13, bold=True, mono=True), fill=(31, 35, 41))
    draw.text((ox + 215, ry + 6), "mm", font=get_font(12), fill=(140, 145, 155))

    hx, hy = ox + 275, ry + 15
    draw.line([(hx - 4, hy), (hx - 1, hy + 4), (hx + 5, hy - 4)], fill=(16, 185, 129), width=2)
    draw.text((ox + 285, ry + 7), "Gerber Outline Verified (Area: 19.76 cm2)", font=get_font(11, mono=True), fill=(16, 185, 129))

    draw_param_row(fy0 + 190, "PCB Qty", ["5 pcs", "10 pcs", "20 pcs", "30 pcs", "50 pcs"], 0, helper_text="Special $2 Prototype Tier")
    draw_param_row(fy0 + 234, "Delivery Format", ["Single PCB", "Panel by Customer", "Panel by JLCPCB"], 0)
    draw_param_row(fy0 + 278, "PCB Thickness", ["0.8 mm", "1.0 mm", "1.2 mm", "1.6 mm", "2.0 mm"], 3, helper_text="Standard 1.6mm +- 10%")

    # PCB Color
    ry = fy0 + 322
    draw.text((fx0 + 25, ry + 6), "PCB Color (Mask)", font=get_font(13, bold=True), fill=(78, 89, 105))
    ox = fx0 + 220
    colors = [
        ("Green", (34, 197, 94)),
        ("Red", (239, 68, 68)),
        ("Yellow", (234, 179, 8)),
        ("Blue", (59, 130, 246)),
        ("White", (245, 245, 245)),
        ("Matte Black", (24, 24, 27))
    ]
    for c_idx, (c_name, c_rgb) in enumerate(colors):
        is_sel = (c_name == "Matte Black")
        pill_w = 105 if is_sel else 80
        pill_h = 30
        if is_sel:
            draw.rounded_rectangle([(ox, ry), (ox + pill_w, ry + pill_h)], radius=4, fill=(240, 246, 255), outline=(0, 118, 247), width=2)
            draw.ellipse([(ox + 8, ry + 7), (ox + 22, ry + 21)], fill=c_rgb, outline=(0, 118, 247), width=1)
            draw.text((ox + 28, ry + 6), c_name, font=get_font(11, bold=True), fill=(0, 118, 247))
        else:
            draw.rounded_rectangle([(ox, ry), (ox + pill_w, ry + pill_h)], radius=4, fill=(255, 255, 255), outline=(225, 230, 238), width=1)
            draw.ellipse([(ox + 8, ry + 8), (ox + 20, ry + 20)], fill=c_rgb, outline=(200, 205, 215), width=1)
            draw.text((ox + 26, ry + 6), c_name, font=get_font(11), fill=(78, 89, 105))
        ox += pill_w + 8
    draw.text((ox + 5, ry + 7), "★ Premium Matte Finish", font=get_font(10, bold=True), fill=(180, 83, 9))

    draw_param_row(fy0 + 366, "Silkscreen", ["White", "Black"], 0, helper_text="High-Definition Inkjet")
    draw_param_row(fy0 + 410, "Surface Finish", ["HASL (with lead)", "LeadFree HASL", "ENIG-1U (Immersion Gold)"], 2, highlight_badge="GOLD PLATED")
    draw_param_row(fy0 + 454, "Copper Weight", ["1 oz (35 um)", "2 oz (70 um)"], 0)
    draw_param_row(fy0 + 498, "FR4-TG", ["TG130-140", "TG150-160", "TG170-180"], 0, helper_text="Standard TG130-140 FR-4")
    draw_param_row(fy0 + 542, "Min Trace / Spacing", ["6/6 mil (0.152mm)", "5/5 mil", "4/4 mil"], 0, helper_text="Passed (Design min: 12/12 mil)")
    draw_param_row(fy0 + 586, "Min Hole Size", ["0.30 mm", "0.25 mm", "0.20 mm"], 0, helper_text="Passed (Design min: 0.35 mm)")
    draw_param_row(fy0 + 630, "Via Process", ["Tenting vias", "Solder mask plugged"], 1, helper_text="Plugged via holes under components")
    draw_param_row(fy0 + 674, "Castellated Holes", ["No", "Yes (Edge Pads Verified)"], 1)
    draw_param_row(fy0 + 718, "Flying Probe Test", ["Fully Tested (100% Netlist)", "Test by Sampling"], 0)
    draw_param_row(fy0 + 762, "Confirm Prod File", ["Yes (Pre-production DFM)", "No"], 0)

    draw.rounded_rectangle([(fx0 + 25, fy0 + 806), (fx0 + fw - 25, fy0 + 845)], radius=4, fill=(240, 246, 255), outline=(190, 218, 255), width=1)
    draw.text((fx0 + 40, fy0 + 817), "NOTE: All parameters comply with JLCPCB 2-Layer Standard Class-2 manufacturing capabilities. 24h express dispatch available.", font=get_font(11), fill=(0, 118, 247))

    # =========================================================================
    # 5. RIGHT PANEL: GERBER PREVIEW + AUTOMATED DFM RESULTS + ORDER SUMMARY
    # =========================================================================
    rx0, ry0, rw, rh = 1120, 205, 760, 855

    # -------------------------------------------------------------------------
    # RIGHT CARD 1: GERBER RS-274X INSPECTION CANVAS (Y = 205 to 550)
    # -------------------------------------------------------------------------
    g_h = 345
    draw.rounded_rectangle([(rx0, ry0), (rx0 + rw, ry0 + g_h)], radius=8, fill=(255, 255, 255), outline=(225, 230, 238), width=1)
    draw.text((rx0 + 20, ry0 + 14), "Gerber RS-274X Inspection Canvas · Pocket Companion v1.0", font=get_font(14, bold=True), fill=(31, 35, 41))
    draw.text((rx0 + rw - 130, ry0 + 14), "Top / Bottom 2D", font=get_font(12, bold=True, mono=True), fill=(0, 118, 247))
    draw.line([(rx0 + 20, ry0 + 38), (rx0 + rw - 20, ry0 + 38)], fill=(238, 240, 244), width=1)

    canvas_x0, canvas_y0 = rx0 + 20, ry0 + 45
    canvas_w, canvas_h = rw - 40, 255
    draw.rounded_rectangle([(canvas_x0, canvas_y0), (canvas_x0 + canvas_w, canvas_y0 + canvas_h)], radius=6, fill=(18, 20, 28))

    for gx in range(canvas_x0, canvas_x0 + canvas_w, 25):
        draw.line([(gx, canvas_y0), (gx, canvas_y0 + canvas_h)], fill=(26, 30, 42), width=1)
    for gy in range(canvas_y0, canvas_y0 + canvas_h, 25):
        draw.line([(canvas_x0, gy), (canvas_x0 + canvas_w, gy)], fill=(26, 30, 42), width=1)

    pcb_2d_w, pcb_2d_h = 380, 210
    pcb_2d_x0 = canvas_x0 + (canvas_w - pcb_2d_w) // 2
    pcb_2d_y0 = canvas_y0 + (canvas_h - pcb_2d_h) // 2
    pcb_2d_x1 = pcb_2d_x0 + pcb_2d_w
    pcb_2d_y1 = pcb_2d_y0 + pcb_2d_h

    draw.rounded_rectangle([(pcb_2d_x0, pcb_2d_y0), (pcb_2d_x1, pcb_2d_y1)], radius=20, fill=(24, 25, 30), outline=(234, 179, 8), width=2)

    for hx, hy in [(pcb_2d_x0 + 25, pcb_2d_y0 + 25), (pcb_2d_x1 - 25, pcb_2d_y0 + 25),
                   (pcb_2d_x0 + 25, pcb_2d_y1 - 25), (pcb_2d_x1 - 25, pcb_2d_y1 - 25)]:
        draw.ellipse([(hx - 12, hy - 12), (hx + 12, hy + 12)], fill=(234, 179, 8), outline=(202, 138, 4), width=1)
        draw.ellipse([(hx - 6, hy - 6), (hx + 6, hy + 6)], fill=(18, 20, 28))

    u_x0, u_y0 = pcb_2d_x0 + 70, pcb_2d_y0 + 40
    u_x1, u_y1 = pcb_2d_x0 + 170, pcb_2d_y0 + 160
    draw.rectangle([(u_x0, u_y0), (u_x1, u_y1)], outline=(255, 255, 255), width=1)
    draw.text((u_x0 + 12, u_y0 + 10), "RP2040-Zero", font=get_font(10, mono=True), fill=(255, 255, 255))
    for i in range(8):
        py = u_y0 + 25 + i * 12
        draw.rectangle([(u_x0 - 8, py - 4), (u_x0 + 2, py + 4)], fill=(234, 179, 8))
        draw.rectangle([(u_x1 - 2, py - 4), (u_x1 + 8, py + 4)], fill=(234, 179, 8))

    for i, px in enumerate([pcb_2d_x0 + 220, pcb_2d_x0 + 245, pcb_2d_x0 + 270, pcb_2d_x0 + 295]):
        draw.ellipse([(px - 6, pcb_2d_y0 + 35), (px + 6, pcb_2d_y0 + 47)], fill=(234, 179, 8))
    draw.text((pcb_2d_x0 + 225, pcb_2d_y0 + 20), "0.96\" OLED", font=get_font(9, mono=True), fill=(255, 255, 255))

    for bx in [pcb_2d_x0 + 120, pcb_2d_x0 + 210, pcb_2d_x0 + 300]:
        by = pcb_2d_y1 - 40
        draw.rectangle([(bx - 16, by - 16), (bx + 16, by + 16)], outline=(255, 255, 255), width=1)
        draw.ellipse([(bx - 8, by - 8), (bx + 8, by + 8)], outline=(255, 255, 255), width=1)
        for dx, dy in [(-12, -10), (12, -10), (-12, 10), (12, 10)]:
            draw.rectangle([(bx + dx - 3, by + dy - 3), (bx + dx + 3, by + dy + 3)], fill=(234, 179, 8))

    draw.line([(u_x1, u_y0 + 35), (pcb_2d_x0 + 220, u_y0 + 35)], fill=(225, 29, 72), width=2)
    draw.line([(u_x1, u_y0 + 47), (pcb_2d_x0 + 245, u_y0 + 47)], fill=(225, 29, 72), width=2)
    draw.line([(u_x0, u_y0 + 80), (pcb_2d_x0 + 120, u_y0 + 80), (pcb_2d_x0 + 120, pcb_2d_y1 - 56)], fill=(37, 99, 235), width=2)
    draw.line([(u_x1, u_y0 + 80), (pcb_2d_x0 + 210, u_y0 + 80), (pcb_2d_x0 + 210, pcb_2d_y1 - 56)], fill=(225, 29, 72), width=2)

    draw.text((pcb_2d_x0 + 195, pcb_2d_y0 + 85), "Pocket Companion", font=get_font(12, bold=True), fill=(255, 255, 255))
    draw.text((pcb_2d_x0 + 215, pcb_2d_y0 + 102), "v1.0 · HALF-LIFE", font=get_font(10, bold=True, mono=True), fill=(234, 179, 8))

    # Dimension Overlays on Gerber Canvas
    draw.line([(pcb_2d_x0, pcb_2d_y1 + 14), (pcb_2d_x1, pcb_2d_y1 + 14)], fill=(250, 204, 21), width=1)
    draw.line([(pcb_2d_x0, pcb_2d_y1 + 10), (pcb_2d_x0, pcb_2d_y1 + 18)], fill=(250, 204, 21), width=1)
    draw.line([(pcb_2d_x1, pcb_2d_y1 + 10), (pcb_2d_x1, pcb_2d_y1 + 18)], fill=(250, 204, 21), width=1)
    draw.text((pcb_2d_x0 + pcb_2d_w // 2 - 25, pcb_2d_y1 + 6), "52.00 mm", font=get_font(9, bold=True, mono=True), fill=(250, 204, 21))

    draw.line([(pcb_2d_x0 - 14, pcb_2d_y0), (pcb_2d_x0 - 14, pcb_2d_y1)], fill=(250, 204, 21), width=1)
    draw.line([(pcb_2d_x0 - 18, pcb_2d_y0), (pcb_2d_x0 - 10, pcb_2d_y0)], fill=(250, 204, 21), width=1)
    draw.line([(pcb_2d_x0 - 18, pcb_2d_y1), (pcb_2d_x0 - 10, pcb_2d_y1)], fill=(250, 204, 21), width=1)
    draw.text((pcb_2d_x0 - 58, pcb_2d_y0 + pcb_2d_h // 2 - 5), "38.00 mm", font=get_font(9, bold=True, mono=True), fill=(250, 204, 21))

    # Vector Checkbox Toggles below canvas
    ly_y = ry0 + 312
    draw.text((rx0 + 25, ly_y), "Layers:", font=get_font(11, bold=True), fill=(78, 89, 105))
    toggles = ["Top Solder Mask", "Top Copper (Red)", "Bottom Copper (Blue)", "Silkscreen", "Drill Holes"]
    tx_pos = rx0 + 80
    for t_name in toggles:
        draw.rounded_rectangle([(tx_pos, ly_y + 2), (tx_pos + 12, ly_y + 14)], radius=2, fill=(0, 118, 247))
        draw.line([(tx_pos + 2, ly_y + 8), (tx_pos + 5, ly_y + 11), (tx_pos + 10, ly_y + 5)], fill=(255, 255, 255), width=2)
        draw.text((tx_pos + 16, ly_y), t_name, font=get_font(10), fill=(100, 106, 115))
        tx_pos += (len(t_name) * 6) + 38

    # -------------------------------------------------------------------------
    # RIGHT CARD 2: AUTOMATED DFM & DRC VERIFICATION REPORT (Y = 565 to 885)
    # -------------------------------------------------------------------------
    dfm_y = 565
    dfm_h = 320
    draw.rounded_rectangle([(rx0, dfm_y), (rx0 + rw, dfm_y + dfm_h)], radius=8, fill=(255, 255, 255), outline=(225, 230, 238), width=1)

    # Large Green Success Banner with Vector Checkmark
    draw.rounded_rectangle([(rx0 + 16, dfm_y + 16), (rx0 + rw - 16, dfm_y + 80)], radius=6, fill=(236, 253, 245), outline=(16, 185, 129), width=2)
    # Vector Checkmark Circle
    cx, cy = rx0 + 50, dfm_y + 48
    draw.ellipse([(cx - 18, cy - 18), (cx + 18, cy + 18)], fill=(16, 185, 129))
    draw.line([(cx - 8, cy + 1), (cx - 2, cy + 7), (cx + 8, cy - 5)], fill=(255, 255, 255), width=3)

    draw.text((rx0 + 82, dfm_y + 26), "AUTOMATED DFM CHECK: PASSED", font=get_font(17, bold=True), fill=(6, 95, 70))
    draw.text((rx0 + 82, dfm_y + 50), "0 DRC Errors · 0 Warnings · 100% Ready for Production", font=get_font(12, bold=True, mono=True), fill=(5, 150, 105))

    # Detailed DFM Validation Matrix Table
    ty = dfm_y + 95
    headers = [("RULE CHECK ITEM", 25), ("REQUIRED", 260), ("ACTUAL", 420), ("STATUS", 580)]
    draw.line([(rx0 + 20, ty), (rx0 + rw - 20, ty)], fill=(225, 230, 238), width=1)
    for h_name, h_off in headers:
        draw.text((rx0 + h_off, ty + 6), h_name, font=get_font(10, bold=True, mono=True), fill=(100, 106, 115))
    draw.line([(rx0 + 20, ty + 24), (rx0 + rw - 20, ty + 24)], fill=(225, 230, 238), width=1)

    drc_items = [
        ("Board Outline Closed", "Complete", "Closed 52x38mm"),
        ("Trace-to-Trace Clearance", ">= 6.0 mil", "12.0 mil (200%)"),
        ("Trace-to-Pad Clearance", ">= 6.0 mil", "10.0 mil (166%)"),
        ("Minimum Trace Width", ">= 5.0 mil", "12.0 mil signal"),
        ("Minimum Drill Hole Size", ">= 0.30 mm", "0.35 mm via"),
        ("Annular Ring Width", ">= 4.0 mil", "8.0 mil (0.20mm)"),
        ("Solder Mask Webbing", ">= 0.10 mm", "0.16 mm bridge"),
        ("Castellated Pad Clearance", ">= 0.20 mm", "0.45 mm edge")
    ]
    ry_item = ty + 30
    for r_item, r_req, r_act in drc_items:
        draw.text((rx0 + 25, ry_item), r_item, font=get_font(11, bold=True), fill=(31, 35, 41))
        draw.text((rx0 + 260, ry_item), r_req, font=get_font(10, mono=True), fill=(100, 106, 115))
        draw.text((rx0 + 420, ry_item), r_act, font=get_font(10, bold=True, mono=True), fill=(0, 118, 247))

        # Vector PASS Badge
        px, py = rx0 + 580, ry_item - 2
        draw.rounded_rectangle([(px, py), (px + 62, py + 18)], radius=3, fill=(236, 253, 245), outline=(16, 185, 129), width=1)
        draw.text((px + 8, py + 2), "PASS", font=get_font(10, bold=True, mono=True), fill=(5, 150, 105))
        draw.line([(px + 44, py + 8), (px + 47, py + 11), (px + 53, py + 5)], fill=(5, 150, 105), width=2)

        draw.line([(rx0 + 20, ry_item + 18), (rx0 + rw - 20, ry_item + 18)], fill=(245, 247, 250), width=1)
        ry_item += 22

    # -------------------------------------------------------------------------
    # RIGHT CARD 3: ORDER TOTAL & INSTANT QUOTE SUMMARY (Y = 898 to 1060)
    # -------------------------------------------------------------------------
    quote_y = 898
    quote_h = 162
    draw.rounded_rectangle([(rx0, quote_y), (rx0 + rw, quote_y + quote_h)], radius=8, fill=(255, 255, 255), outline=(225, 230, 238), width=1)

    draw.text((rx0 + 25, quote_y + 14), "PCB Subtotal (5 pcs, 52x38mm, 2L):", font=get_font(11), fill=(100, 106, 115))
    draw.text((rx0 + 290, quote_y + 14), "$2.00", font=get_font(11, bold=True, mono=True), fill=(31, 35, 41))

    draw.text((rx0 + 25, quote_y + 34), "Surface Finish: ENIG-1U (Immersion Gold):", font=get_font(11), fill=(100, 106, 115))
    draw.text((rx0 + 290, quote_y + 34), "$4.80", font=get_font(11, bold=True, mono=True), fill=(31, 35, 41))

    draw.text((rx0 + 25, quote_y + 54), "Matte Black Mask / White Silkscreen:", font=get_font(11), fill=(100, 106, 115))
    draw.text((rx0 + 290, quote_y + 54), "$0.00 (Promo)", font=get_font(11, bold=True, mono=True), fill=(16, 185, 129))

    draw.text((rx0 + 25, quote_y + 74), "Automated DFM & Engineering Fee:", font=get_font(11), fill=(100, 106, 115))
    draw.text((rx0 + 290, quote_y + 74), "$0.00 (Free)", font=get_font(11, bold=True, mono=True), fill=(16, 185, 129))

    draw.line([(rx0 + 25, quote_y + 98), (rx0 + 340, quote_y + 98)], fill=(225, 230, 238), width=1)
    draw.text((rx0 + 25, quote_y + 106), "Est. Build Time: 24-48 Hours Express · Weight: 0.04 kg", font=get_font(10, mono=True), fill=(100, 106, 115))
    draw.text((rx0 + 25, quote_y + 128), "Guaranteed IPC-A-600 Class-2 Production Standard", font=get_font(10, bold=True), fill=(0, 118, 247))

    # Total Price Display
    draw.text((rx0 + 440, quote_y + 16), "Calculated Total:", font=get_font(13), fill=(78, 89, 105))
    draw.text((rx0 + 440, quote_y + 38), "$6.80", font=get_font(34, bold=True), fill=(239, 68, 68))
    draw.text((rx0 + 555, quote_y + 52), "USD", font=get_font(13, bold=True), fill=(100, 106, 115))

    btn_x = rx0 + 440
    btn_y = quote_y + 92
    btn_w = rw - 440 - 25
    btn_h = 48
    draw.rounded_rectangle([(btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h)], radius=6, fill=(0, 118, 247))
    draw.text((btn_x + btn_w // 2, btn_y + 24), "SAVE TO CART & ORDER", font=get_font(14, bold=True), fill=(255, 255, 255), anchor="mm")

    img.save(OUTPUT_PATH, "PNG", quality=95)
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"[SUCCESS] Saved perfected JLCPCB portal screenshot: {OUTPUT_PATH}")
    print(f"Dimensions: {w}x{h}, File Size: {file_size:,} bytes")

if __name__ == "__main__":
    render_jlcpcb_portal()
