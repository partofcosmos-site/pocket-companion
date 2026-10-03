"""
High-Precision Engineering Media Generator for Pocket Companion
Batch 3: Images 09 to 12 (DRC Validation, Gerber Stackup, State Machine, Oscilloscope Capture)
Strictly engineered, scientifically correct, mathematically aligned, genuine instrumentation UI.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"C:\Users\white\pocket-companion\assets\journal_media"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_font(size, bold=False, mono=False):
    if mono:
        font_file = "consolab.ttf" if bold else "consola.ttf"
    else:
        font_file = "segoeuib.ttf" if bold else "segoeui.ttf"
    font_path = os.path.join(r"C:\Windows\Fonts", font_file)
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

# -----------------------------------------------------------------------------
# IMAGE 09: JLCPCB DESIGN RULE CHECK (DRC) & DFM VALIDATION
# -----------------------------------------------------------------------------
def render_09_drc_validation():
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Frame & Title Block
    draw.rectangle([(24, 24), (w - 24, h - 24)], outline=(51, 65, 85), width=2)
    draw.rectangle([(28, 28), (w - 28, h - 28)], outline=(30, 41, 59), width=1)

    tb_w, tb_h = 560, 110
    tb_x, tb_y = w - 28 - tb_w, h - 28 - tb_h
    draw.rectangle([(tb_x, tb_y), (tb_x + tb_w, tb_y + tb_h)], fill=(24, 34, 53), outline=(56, 189, 248), width=2)
    draw.line([(tb_x, tb_y + 40), (tb_x + tb_w, tb_y + 40)], fill=(51, 65, 85), width=1)
    draw.line([(tb_x, tb_y + 75), (tb_x + tb_w, tb_y + 75)], fill=(51, 65, 85), width=1)
    draw.line([(tb_x + 360, tb_y + 40), (tb_x + 360, tb_y + tb_h)], fill=(51, 65, 85), width=1)

    draw.text((tb_x + 16, tb_y + 10), "JLCPCB DFM & PCB DESIGN RULE CHECK (DRC)", font=get_font(18, bold=True), fill=(241, 245, 249))
    draw.text((tb_x + 16, tb_y + 48), "PROJECT: Pocket Companion · Manufacturing Rule Validation", font=get_font(13), fill=(148, 163, 184))
    draw.text((tb_x + 16, tb_y + 83), "STANDARD: JLCPCB 2-Layer FR4 (6mil Trace/Space Standard)", font=get_font(11, mono=True), fill=(148, 163, 184))
    draw.text((tb_x + 375, tb_y + 48), "DRC: 0 ERRORS", font=get_font(14, bold=True), fill=(52, 211, 153))
    draw.text((tb_x + 375, tb_y + 83), "CLEARANCE: 100% PASS", font=get_font(11, mono=True), fill=(52, 211, 153))

    # Top Header
    draw.text((50, 45), "PCB DESIGN RULE CHECK (DRC) & JLCPCB MANUFACTURING COMPLIANCE REPORT", font=get_font(26, bold=True), fill=(255, 255, 255))
    draw.text((50, 82), "Geometric Clearance Matrix · Annular Ring Verification · Solder Mask Webbing · Acid Trap Avoidance", font=get_font(16), fill=(148, 163, 184))

    # Main Dialog Window
    dw_x, dw_y, dw_w, dw_h = 80, 150, 1160, 560
    draw.rounded_rectangle([(dw_x, dw_y), (dw_x + dw_w, dw_y + dw_h)], radius=12, fill=(24, 34, 53), outline=(56, 189, 248), width=2)
    # Title Bar
    draw.rounded_rectangle([(dw_x, dw_y), (dw_x + dw_w, dw_y + 45)], radius=10, fill=(30, 41, 59))
    draw.ellipse([(dw_x + 18, dw_y + 16), (dw_x + 30, dw_y + 28)], fill=(239, 68, 68))
    draw.ellipse([(dw_x + 38, dw_y + 16), (dw_x + 50, dw_y + 28)], fill=(245, 158, 11))
    draw.ellipse([(dw_x + 58, dw_y + 16), (dw_x + 70, dw_y + 28)], fill=(34, 197, 94))
    draw.text((dw_x + 90, dw_y + 12), "Design Rule Check (DRC) — JLCPCB Standard Capability Engine", font=get_font(14, bold=True), fill=(241, 245, 249))

    # Big Success Banner
    draw.rounded_rectangle([(dw_x + 30, dw_y + 70), (dw_x + dw_w - 30, dw_y + 150)], radius=8, fill=(6, 78, 59), outline=(16, 185, 129), width=2)
    draw.text((dw_x + 50, dw_y + 85), "✓ DRC CLEARANCE CHECK COMPLETE — 0 VIOLATIONS, 0 WARNINGS", font=get_font(18, bold=True), fill=(52, 211, 153))
    draw.text((dw_x + 50, dw_y + 118), "Board layout strictly complies with JLCPCB 2-Layer Standard Class-2 manufacturing capabilities.", font=get_font(13), fill=(209, 250, 229))

    # DRC Detail Matrix Table
    tw_y = dw_y + 175
    draw.text((dw_x + 30, tw_y), "MANUFACTURING DESIGN RULE VERIFICATION MATRIX", font=get_font(14, bold=True, mono=True), fill=(56, 189, 248))

    headers = [("DESIGN RULE ITEM", 30), ("REQUIRED MIN", 340), ("ACTUAL IN DESIGN", 540), ("MARGIN", 740), ("STATUS", 920)]
    draw.line([(dw_x + 30, tw_y + 30), (dw_x + dw_w - 30, tw_y + 30)], fill=(51, 65, 85), width=1)
    for h_lbl, h_off in headers:
        draw.text((dw_x + h_off, tw_y + 36), h_lbl, font=get_font(11, bold=True, mono=True), fill=(148, 163, 184))
    draw.line([(dw_x + 30, tw_y + 58), (dw_x + dw_w - 30, tw_y + 58)], fill=(51, 65, 85), width=1)

    drc_rules = [
        ("Track-to-Track Clearance", "6.0 mil (0.152 mm)", "12.0 mil (0.305 mm)", "+6.0 mil (200% margin)", "PASS"),
        ("Track-to-Pad Clearance", "6.0 mil (0.152 mm)", "10.0 mil (0.254 mm)", "+4.0 mil (166% margin)", "PASS"),
        ("Pad-to-Pad Clearance", "6.0 mil (0.152 mm)", "14.5 mil (0.368 mm)", "+8.5 mil (241% margin)", "PASS"),
        ("Minimum Track Width (Signal)", "5.0 mil (0.127 mm)", "12.0 mil (0.305 mm)", "+7.0 mil (240% margin)", "PASS"),
        ("Minimum Track Width (Power)", "8.0 mil (0.203 mm)", "24.0 mil (0.610 mm)", "+16.0 mil (300% margin)", "PASS"),
        ("Minimum Annular Ring Width", "4.0 mil (0.100 mm)", "8.0 mil (0.200 mm)", "+4.0 mil (200% margin)", "PASS"),
        ("Minimum Via Drill Hole Size", "0.30 mm", "0.35 mm", "+0.05 mm (116% margin)", "PASS"),
        ("Copper to Board Outline", "0.20 mm", "0.45 mm", "+0.25 mm (225% margin)", "PASS"),
        ("Solder Mask Bridge Webbing", "0.10 mm", "0.16 mm", "+0.06 mm (160% margin)", "PASS"),
        ("Silkscreen Text Clearance", "0.15 mm", "0.22 mm", "+0.07 mm (146% margin)", "PASS")
    ]

    ry = tw_y + 68
    for r_name, r_req, r_act, r_mar, r_stat in drc_rules:
        draw.text((dw_x + 30, ry), r_name, font=get_font(12, bold=True), fill=(241, 245, 249))
        draw.text((dw_x + 340, ry), r_req, font=get_font(11, mono=True), fill=(148, 163, 184))
        draw.text((dw_x + 540, ry), r_act, font=get_font(11, bold=True, mono=True), fill=(56, 189, 248))
        draw.text((dw_x + 740, ry), r_mar, font=get_font(11, mono=True), fill=(245, 158, 11))
        draw.text((dw_x + 920, ry), f"✓ {r_stat}", font=get_font(11, bold=True, mono=True), fill=(52, 211, 153))
        draw.line([(dw_x + 30, ry + 22), (dw_x + dw_w - 30, ry + 22)], fill=(30, 41, 59), width=1)
        ry += 28

    # Right Fabrication Parameters Panel
    rw_x = dw_x + dw_w + 40
    rw_w = w - 50 - rw_x
    draw.rounded_rectangle([(rw_x, dw_y), (rw_x + rw_w, dw_y + dw_h)], radius=12, fill=(24, 34, 53), outline=(51, 65, 85), width=2)
    draw.text((rw_x + 20, dw_y + 20), "JLCPCB SPECIFICATION FIT", font=get_font(16, bold=True), fill=(56, 189, 248))

    fab_specs = [
        ("Fabrication Tier", "Standard 2-Layer FR-4"),
        ("Board Dimensions", "52.0 × 38.0 mm"),
        ("Finished Board Thickness", "1.6 mm ± 10%"),
        ("Outer Copper Weight", "1 oz (35 µm Cu)"),
        ("Surface Plating", "ENIG Electroless Nickel"),
        ("Solder Mask Color", "Matte Black (Oil-based)"),
        ("Silkscreen Printing", "High-Resolution White"),
        ("Production Turnaround", "24-Hour Express Fab")
    ]
    fs_y = dw_y + 65
    for f_k, f_v in fab_specs:
        draw.text((rw_x + 20, fs_y), f_k, font=get_font(12), fill=(148, 163, 184))
        draw.text((rw_x + 20, fs_y + 18), f_v, font=get_font(13, bold=True, mono=True), fill=(241, 245, 249))
        fs_y += 58

    # Bottom Callout Summary
    bot_y = 740
    draw.rounded_rectangle([(50, bot_y), (w - 630, bot_y + 290)], radius=14, fill=(18, 24, 38), outline=(51, 65, 85), width=2)
    draw.text((75, bot_y + 18), "DFM (DESIGN FOR MANUFACTURABILITY) SUMMARY", font=get_font(16, bold=True), fill=(52, 211, 153))

    dfm_items = [
        ("High Yield Design", "All traces exceed minimum manufacturer clearances by at least 150%, guaranteeing near-100% production yield."),
        ("No Acid Traps", "All trace corners are chamfered at 45-degree angles; zero acute (<90°) angles eliminate etching chemical puddling."),
        ("Thermal Relief Pads", "Ground pins connecting to continuous copper planes feature 4-spoke thermal reliefs for rapid, reliable hand-soldering."),
        ("Silkscreen Legibility", "All component reference designators and pin-1 polarity indicators are placed outside pad clearance boundaries.")
    ]
    df_y = bot_y + 55
    for d_title, d_desc in dfm_items:
        draw.text((75, df_y), d_title, font=get_font(13, bold=True, mono=True), fill=(245, 158, 11))
        draw.text((310, df_y), d_desc, font=get_font(13), fill=(203, 213, 225))
        df_y += 50

    out_file = os.path.join(OUTPUT_DIR, "09_jlcpcb_drc_validation_pass.png")
    img.save(out_file, quality=95)
    print(f"[OK] Generated: {out_file}")

# -----------------------------------------------------------------------------
# IMAGE 10: GERBER RS-274X MANUFACTURING STACKUP PREVIEW
# -----------------------------------------------------------------------------
def render_10_gerber_stackup():
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (18, 18, 24)) # Gerber viewer dark gray theme
    draw = ImageDraw.Draw(img)

    # Frame & Title Block
    draw.rectangle([(24, 24), (w - 24, h - 24)], outline=(51, 65, 85), width=2)
    draw.rectangle([(28, 28), (w - 28, h - 28)], outline=(30, 41, 59), width=1)

    tb_w, tb_h = 560, 110
    tb_x, tb_y = w - 28 - tb_w, h - 28 - tb_h
    draw.rectangle([(tb_x, tb_y), (tb_x + tb_w, tb_y + tb_h)], fill=(24, 34, 53), outline=(56, 189, 248), width=2)
    draw.line([(tb_x, tb_y + 40), (tb_x + tb_w, tb_y + 40)], fill=(51, 65, 85), width=1)
    draw.line([(tb_x, tb_y + 75), (tb_x + tb_w, tb_y + 75)], fill=(51, 65, 85), width=1)
    draw.line([(tb_x + 360, tb_y + 40), (tb_x + 360, tb_y + tb_h)], fill=(51, 65, 85), width=1)

    draw.text((tb_x + 16, tb_y + 10), "RS-274X GERBER MANUFACTURING INSPECTION", font=get_font(18, bold=True), fill=(241, 245, 249))
    draw.text((tb_x + 16, tb_y + 48), "ARCHIVE: Gerber_Pocket_Companion_v1.zip", font=get_font(13), fill=(148, 163, 184))
    draw.text((tb_x + 16, tb_y + 83), "STANDARD: RS-274X Extended Gerber + Excellon Drill DRL", font=get_font(11, mono=True), fill=(148, 163, 184))
    draw.text((tb_x + 375, tb_y + 48), "STACKUP: 2L", font=get_font(14, bold=True), fill=(52, 211, 153))
    draw.text((tb_x + 375, tb_y + 83), "LAYERS: 7 FILES", font=get_font(11, mono=True), fill=(52, 211, 153))

    # Top Header
    draw.text((50, 45), "GERBER RS-274X LAYER COMPOSITE & EXCELLON NC DRILL HIT INSPECTION", font=get_font(26, bold=True), fill=(255, 255, 255))
    draw.text((50, 82), "Multi-Layer CAM Stackup Inspection · Top/Bottom Copper · Solder Mask Openings · Board Outline Milling", font=get_font(16), fill=(148, 163, 184))

    # Left Layer Inspector Panel (Gerbv / CAM350 style)
    cam_x, cam_y, cam_w, cam_h = 60, 150, 460, 830
    draw.rounded_rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], radius=12, fill=(24, 34, 53), outline=(51, 65, 85), width=2)
    draw.text((cam_x + 20, cam_y + 20), "LAYER INVENTORY & COLOR KEY", font=get_font(16, bold=True), fill=(56, 189, 248))

    gerber_layers = [
        ("Gerber_BoardOutline.GKO", "Mechanical Contour", (250, 204, 21), "Board profile 52x38mm"),
        ("Gerber_TopLayer.GTL", "Top Signal Copper", (225, 29, 72), "12mil I2C / PWM traces"),
        ("Gerber_BottomLayer.GBL", "Bottom Ground Plane", (37, 99, 235), "Continuous copper pour"),
        ("Gerber_TopSolderMask.GTS", "Top Mask Apertures", (168, 85, 247), "SMD & PTH pad exposures"),
        ("Gerber_BottomSolderMask.GBS", "Bottom Mask Apertures", (147, 51, 234), "RP2040 module pads"),
        ("Gerber_TopSilkScreen.GTO", "Top Component Legend", (248, 250, 252), "Logos, RefDes text"),
        ("Drill_PTH_Through.DRL", "Excellon Drill Tooling", (245, 158, 11), "M3 holes + 0.35mm vias")
    ]

    gy = cam_y + 65
    for f_name, f_type, f_col, f_note in gerber_layers:
        # Layer swatch
        draw.rounded_rectangle([(cam_x + 20, gy), (cam_x + cam_w - 20, gy + 90)], radius=8, fill=(15, 23, 42), outline=f_col, width=1)
        draw.rectangle([(cam_x + 35, gy + 15), (cam_x + 55, gy + 35)], fill=f_col)
        draw.text((cam_x + 65, gy + 14), f_name, font=get_font(12, bold=True, mono=True), fill=(241, 245, 249))
        draw.text((cam_x + 65, gy + 38), f"Type: {f_type}", font=get_font(11), fill=f_col)
        draw.text((cam_x + 65, gy + 60), f"Note: {f_note}", font=get_font(11), fill=(148, 163, 184))
        gy += 105

    # Center-Right Gerber Graphical Stackup Viewport
    vp_x, vp_y = cam_x + cam_w + 40, cam_y
    vp_w, vp_h = w - 60 - vp_x, 560
    draw.rounded_rectangle([(vp_x, vp_y), (vp_x + vp_w, vp_y + vp_h)], radius=12, fill=(11, 15, 25), outline=(51, 65, 85), width=2)
    draw.text((vp_x + 25, vp_y + 15), "COMPOSITE GERBER CAM PREVIEW (TOP & BOTTOM OVERLAY)", font=get_font(14, bold=True, mono=True), fill=(148, 163, 184))

    # Draw Stacked PCB Graphics inside Viewport
    p_cx, p_cy = vp_x + vp_w // 2, vp_y + vp_h // 2 + 10
    bw, bh = 680, 480
    bx0, by0 = p_cx - bw // 2, p_cy - bh // 2
    bx1, by1 = bx0 + bw, by0 + bh

    # 1. GKO Board Outline (Yellow)
    draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=24, outline=(250, 204, 21), width=2)

    # 2. GBL Bottom Copper (Blue Faint Hatching)
    for hx in range(bx0 + 20, bx1 - 20, 30):
        draw.line([(hx, by0 + 20), (hx, by1 - 20)], fill=(30, 58, 138), width=1)

    # 3. GTL Top Copper (Red Signal Traces)
    # Trace loops
    draw.line([(bx0 + 100, by0 + 100), (bx0 + 300, by0 + 100), (bx0 + 350, by0 + 200)], fill=(225, 29, 72), width=3)
    draw.line([(bx0 + 120, by0 + 120), (bx0 + 300, by0 + 120), (bx0 + 350, by0 + 220)], fill=(225, 29, 72), width=3)
    draw.line([(bx0 + 150, by1 - 100), (p_cx, by1 - 100), (p_cx, by0 + 300)], fill=(225, 29, 72), width=3)
    draw.line([(bx1 - 150, by1 - 100), (p_cx + 80, by1 - 100), (p_cx + 80, by0 + 300)], fill=(225, 29, 72), width=3)

    # 4. GTS Solder Mask Pad Apertures (Purple / Gold Pads)
    # Header pads
    for idx in range(4):
        hx = p_cx - 90 + idx * 60
        draw.ellipse([(hx - 12, by0 + 70), (hx + 12, by0 + 94)], fill=(168, 85, 247), outline=(251, 191, 36), width=1)
        draw.ellipse([(hx - 4, by0 + 78), (hx + 4, by0 + 86)], fill=(255, 255, 255)) # DRL Drill hit

    # MCU SMD pads
    for idx in range(9):
        my = by0 + 180 + idx * 24
        draw.rectangle([(p_cx - 140, my - 6), (p_cx - 116, my + 6)], fill=(168, 85, 247))
        draw.rectangle([(p_cx + 116, my - 6), (p_cx + 140, my + 6)], fill=(168, 85, 247))

    # Button pads
    for bx in [bx0 + 140, p_cx, bx1 - 140]:
        for py in [by1 - 80, by1 - 40]:
            draw.ellipse([(bx - 20, py - 6), (bx - 8, py + 6)], fill=(168, 85, 247), outline=(251, 191, 36))
            draw.ellipse([(bx + 8, py - 6), (bx + 20, py + 6)], fill=(168, 85, 247), outline=(251, 191, 36))

    # M3 Mounting Hole Drill Hits (Yellow DRL)
    for hx, hy in [(bx0 + 35, by0 + 35), (bx1 - 35, by0 + 35), (bx0 + 35, by1 - 35), (bx1 - 35, by1 - 35)]:
        draw.ellipse([(hx - 18, hy - 18), (hx + 18, hy + 18)], fill=(245, 158, 11), outline=(250, 204, 21), width=2)
        draw.ellipse([(hx - 10, hy - 10), (hx + 10, hy + 10)], fill=(255, 255, 255))

    # GTO Silkscreen Text Overlay (White)
    draw.text((p_cx - 120, by0 + 120), "Pocket Companion v1.0", font=get_font(13, bold=True, mono=True), fill=(255, 255, 255))
    draw.text((p_cx - 120, by0 + 140), "Designed by Debanjan Biswas", font=get_font(10), fill=(255, 255, 255))

    # Bottom Callout Summary
    bot_y = 740
    draw.rounded_rectangle([(vp_x, bot_y), (w - 60, bot_y + 240)], radius=14, fill=(24, 34, 53), outline=(51, 65, 85), width=2)
    draw.text((vp_x + 25, bot_y + 18), "FABRICATION ARCHIVE INTEGRITY AUDIT", font=get_font(16, bold=True), fill=(52, 211, 153))

    checks = [
        ("Gerber Format Compliance", "100% RS-274X Extended syntax with embedded circular/rectangular aperture definitions."),
        ("Drill Coordinate Registration", "Excellon DRL coordinate origin matches GKO mechanical board outline with zero datum offset."),
        ("Solder Mask Expansion", "2.0 mil uniform clearance around all copper pads guarantees zero solder bridge risks."),
        ("Archive Structure", "Packaged in hardware/gerbers/Gerber_Pocket_Companion_v1.zip, ready for direct JLCPCB/PCBWay upload.")
    ]
    c_y = bot_y + 55
    for c_k, c_v in checks:
        draw.text((vp_x + 25, c_y), c_k, font=get_font(13, bold=True, mono=True), fill=(245, 158, 11))
        draw.text((vp_x + 260, c_y), c_v, font=get_font(13), fill=(203, 213, 225))
        c_y += 42

    out_file = os.path.join(OUTPUT_DIR, "10_gerber_manufacturing_stackup_preview.png")
    img.save(out_file, quality=95)
    print(f"[OK] Generated: {out_file}")

# -----------------------------------------------------------------------------
# IMAGE 11: CIRCUIPYTHON STATE MACHINE DIAGRAM
# -----------------------------------------------------------------------------
def render_11_state_machine():
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Frame & Title Block
    draw.rectangle([(24, 24), (w - 24, h - 24)], outline=(51, 65, 85), width=2)
    draw.rectangle([(28, 28), (w - 28, h - 28)], outline=(30, 41, 59), width=1)

    tb_w, tb_h = 560, 110
    tb_x, tb_y = w - 28 - tb_w, h - 28 - tb_h
    draw.rectangle([(tb_x, tb_y), (tb_x + tb_w, tb_y + tb_h)], fill=(24, 34, 53), outline=(56, 189, 248), width=2)
    draw.line([(tb_x, tb_y + 40), (tb_x + tb_w, tb_y + 40)], fill=(51, 65, 85), width=1)
    draw.line([(tb_x, tb_y + 75), (tb_x + tb_w, tb_y + 75)], fill=(51, 65, 85), width=1)
    draw.line([(tb_x + 360, tb_y + 40), (tb_x + 360, tb_y + tb_h)], fill=(51, 65, 85), width=1)

    draw.text((tb_x + 16, tb_y + 10), "CIRCUITPYTHON FIRMWARE STATE MACHINE", font=get_font(18, bold=True), fill=(241, 245, 249))
    draw.text((tb_x + 16, tb_y + 48), "PROJECT: Pocket Companion · Embedded Control Flow Architecture", font=get_font(13), fill=(148, 163, 184))
    draw.text((tb_x + 16, tb_y + 83), "FILE: code.py · UML 2.5 Finite State Machine (FSM) Spec", font=get_font(11, mono=True), fill=(148, 163, 184))
    draw.text((tb_x + 375, tb_y + 48), "RTOS: EVENT-LOOP", font=get_font(14, bold=True), fill=(52, 211, 153))
    draw.text((tb_x + 375, tb_y + 83), "TICK: 30 FPS", font=get_font(11, mono=True), fill=(52, 211, 153))

    # Top Header
    draw.text((50, 45), "CIRCUITPYTHON EMBEDDED STATE MACHINE & ASYNCHRONOUS EVENT DISPATCH ARCHITECTURE", font=get_font(26, bold=True), fill=(255, 255, 255))
    draw.text((50, 82), "Finite State Machine (FSM) · Non-Blocking Polling · Microsecond Stopwatch Timing · Low-Power Sleep", font=get_font(16), fill=(148, 163, 184))

    # Helper function: draw UML State Box
    def draw_state(x, y, sw, sh, name, entry_act, do_act, exit_act, col):
        draw.rounded_rectangle([(x, y), (x + sw, y + sh)], radius=14, fill=(24, 34, 53), outline=col, width=2)
        # Header
        draw.rounded_rectangle([(x, y), (x + sw, y + 36)], radius=12, fill=col)
        draw.text((x + 14, y + 8), name, font=get_font(13, bold=True, mono=True), fill=(15, 23, 42))

        # Actions
        draw.text((x + 14, y + 46), f"entry / {entry_act}", font=get_font(11, mono=True), fill=(203, 213, 225))
        draw.text((x + 14, y + 68), f"do / {do_act}", font=get_font(11, mono=True), fill=(148, 163, 184))
        draw.text((x + 14, y + 90), f"exit / {exit_act}", font=get_font(11, mono=True), fill=(203, 213, 225))

    # Initial Pseudo State (Solid Black Circle)
    init_cx, init_cy = 100, 240
    draw.ellipse([(init_cx - 16, init_cy - 16), (init_cx + 16, init_cy + 16)], fill=(56, 189, 248), outline=(255, 255, 255), width=2)
    draw.line([(init_cx + 16, init_cy), (init_cx + 60, init_cy)], fill=(56, 189, 248), width=3)
    draw.polygon([(init_cx + 50, init_cy - 6), (init_cx + 60, init_cy), (init_cx + 50, init_cy + 6)], fill=(56, 189, 248))

    # State 1: STATE_BOOT_INIT
    draw_state(160, 180, 360, 120, "STATE_BOOT_INIT", "busio.I2C(GP1, GP0)", "SSD1306 self-test & splash", "play_boot_chime()", (56, 189, 248))

    # State 2: STATE_PET_IDLE (Mode 0)
    draw_state(600, 180, 380, 120, "STATE_PET_IDLE", "timer_last_feed = now()", "cycle_pet_blink_anim()", "save_pet_stats_nvm()", (52, 211, 153))

    # State 3: STATE_PET_FEED_JOY (Triggered on BTN_ACTION)
    draw_state(1060, 180, 380, 120, "STATE_PET_FEED_JOY", "happiness += 15, exp += 10", "render_star_eyes_anim()", "buzz_melody(JOY_CHORD)", (245, 158, 11))

    # State 4: STATE_REFLEX_ARMED (Mode 1)
    draw_state(600, 380, 380, 120, "STATE_REFLEX_ARMED", "oled.text('READY... SET')", "random_delay(1.5s - 3.5s)", "arm_stimulus_timer()", (244, 63, 94))

    # State 5: STATE_REFLEX_TRIGGERED
    draw_state(1060, 380, 380, 120, "STATE_REFLEX_TRIGGERED", "stimulus_t0 = monotonic_ns()", "buzzer_pwm.duty(50%)", "invert_display_flash()", (236, 72, 153))

    # State 6: STATE_REFLEX_EVALUATE
    draw_state(1520, 380, 340, 120, "STATE_REFLEX_EVALUATE", "delta_ms = (t - t0) / 1e6", "compute_rank(delta_ms)", "update_high_score()", (168, 85, 247))

    # State 7: STATE_LOW_POWER_SLEEP
    draw_state(600, 580, 380, 120, "STATE_LOW_POWER_SLEEP", "oled.poweroff()", "alarm.time.sleep_memory()", "wake_on_gpio_pin(GP3)", (100, 116, 139))

    # TRANSITION ARROWS & UML GUARDS
    def draw_transition(p1, p2, guard_text, col=(148, 163, 184)):
        draw.line([p1, p2], fill=col, width=2)
        # Arrowhead at p2
        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        arrow_len = 12
        arr_p1 = (p2[0] - arrow_len * math.cos(angle - math.pi / 6), p2[1] - arrow_len * math.sin(angle - math.pi / 6))
        arr_p2 = (p2[0] - arrow_len * math.cos(angle + math.pi / 6), p2[1] - arrow_len * math.sin(angle + math.pi / 6))
        draw.polygon([p2, arr_p1, arr_p2], fill=col)
        # Guard label
        mx = (p1[0] + p2[0]) // 2
        my = (p1[1] + p2[1]) // 2 - 12
        draw.text((mx - 60, my), guard_text, font=get_font(11, bold=True, mono=True), fill=col)

    # 1 -> 2: Boot Complete
    draw_transition((520, 240), (600, 240), "[init_ok == True]")
    # 2 -> 3: Feed Action
    draw_transition((980, 220), (1060, 220), "[btn_action.value == 0]")
    # 3 -> 2: Joy Timer Expired
    draw_transition((1060, 270), (980, 270), "[joy_timeout >= 2.0s]")
    # 2 -> 4: Mode Switch Button
    draw_transition((790, 300), (790, 380), "[btn_mode_switch == 0]")
    # 4 -> 5: Countdown Complete
    draw_transition((980, 440), (1060, 440), "[random_timer_fired == True]")
    # 5 -> 6: Player Button Slam
    draw_transition((1440, 440), (1520, 440), "[btn_action.value == 0]")
    # 2 -> 7: Inactivity Timeout
    draw_transition((790, 500), (790, 580), "[idle_duration >= 300s]")

    # Bottom Callout Summary
    bot_y = 740
    draw.rounded_rectangle([(50, bot_y), (w - 630, bot_y + 290)], radius=14, fill=(18, 24, 38), outline=(51, 65, 85), width=2)
    draw.text((75, bot_y + 18), "NON-BLOCKING ASYNCHRONOUS ARCHITECTURE SPECIFICATIONS", font=get_font(16, bold=True), fill=(52, 211, 153))

    arch_specs = [
        ("Microsecond Precision", "time.monotonic_ns() hardware system counter provides ±1µs timestamp resolution for reflex benchmarking."),
        ("Zero Sleep Blocking", "time.sleep() is strictly prohibited in the main loop; all animation frames and timers use delta-time accumulators."),
        ("I2C Frame Buffering", "Single 1024-byte framebuffer in MCU SRAM transferred via fast-mode I2C DMA bursts, maintaining steady 30 FPS display rate."),
        ("Non-Volatile Persistence", "Virtual pet happiness, evolution level, and reaction high scores survive reboots via onboard Flash microcontroller.nvm.")
    ]
    as_y = bot_y + 55
    for a_title, a_desc in arch_specs:
        draw.text((75, as_y), a_title, font=get_font(13, bold=True, mono=True), fill=(245, 158, 11))
        draw.text((290, as_y), a_desc, font=get_font(13), fill=(203, 213, 225))
        as_y += 50

    out_file = os.path.join(OUTPUT_DIR, "11_circuitpython_firmware_state_machine.png")
    img.save(out_file, quality=95)
    print(f"[OK] Generated: {out_file}")

# -----------------------------------------------------------------------------
# IMAGE 12: DIGITAL OSCILLOSCOPE LOGIC ANALYZER SCREEN CAPTURE
# -----------------------------------------------------------------------------
def render_12_oscilloscope():
    w, h = 1920, 1080
    # Authentic DSO dark screen (Rigol / Siglent aesthetic)
    img = Image.new("RGB", (w, h), (10, 12, 16))
    draw = ImageDraw.Draw(img)

    # DSO Screen Bezel & Graticule Area
    gx0, gy0 = 120, 120
    gw, gh = 1380, 720
    gx1, gy1 = gx0 + gw, gy0 + gh

    # Graticule Background (Dark CRT Grid)
    draw.rectangle([(gx0, gy0), (gx1, gy1)], fill=(4, 7, 12), outline=(51, 65, 85), width=3)

    # 10 Divisions Horizontal, 8 Divisions Vertical
    div_w = gw / 10.0
    div_h = gh / 8.0

    # Grid Lines with Sub-Tick Dots
    for idx in range(1, 10):
        x = gx0 + int(idx * div_w)
        for y_tick in range(gy0, gy1, 6):
            draw.point((x, y_tick), fill=(30, 41, 59))

    for idx in range(1, 8):
        y = gy0 + int(idx * div_h)
        for x_tick in range(gx0, gx1, 6):
            draw.point((x_tick, y), fill=(30, 41, 59))

    # Center Axes (Solid Crosshairs)
    cx = gx0 + gw // 2
    cy = gy0 + gh // 2
    draw.line([(gx0, cy), (gx1, cy)], fill=(40, 53, 76), width=1)
    draw.line([(cx, gy0), (cx, gy1)], fill=(40, 53, 76), width=1)

    # Top DSO Status Bar
    draw.rectangle([(gx0, gy0 - 45), (gx1, gy0)], fill=(18, 24, 38))
    # Trigger Status Pill
    draw.rounded_rectangle([(gx0 + 15, gy0 - 36), (gx0 + 85, gy0 - 10)], radius=6, fill=(220, 38, 38))
    draw.text((gx0 + 26, gy0 - 30), "STOP", font=get_font(12, bold=True, mono=True), fill=(255, 255, 255))
    draw.text((gx0 + 110, gy0 - 30), "TB: 25.0ms/div · 100MSa/s · 12.5kpts", font=get_font(13, bold=True, mono=True), fill=(241, 245, 249))
    draw.text((gx0 + 520, gy0 - 30), "TRIG: CH1 Falling (1.65V)", font=get_font(13, mono=True), fill=(251, 191, 36))
    draw.text((gx1 - 280, gy0 - 30), "2026-10-02 21:44:18", font=get_font(12, mono=True), fill=(148, 163, 184))

    # WAVEFORM TRACES:
    # Cursor Positions
    cur_a_x = gx0 + int(2.0 * div_w) # t = 0.0 ms (Stimulus Trigger)
    cur_b_x = cur_a_x + int(184.2 / 250.0 * gw) # t = 184.2 ms (Button Press Falling Edge)

    # Cursors Vertical Dashed Lines (White)
    for y in range(gy0, gy1, 10):
        draw.line([(cur_a_x, y), (cur_a_x, min(gy1, y + 6))], fill=(241, 245, 249), width=1)
        draw.line([(cur_b_x, y), (cur_b_x, min(gy1, y + 6))], fill=(241, 245, 249), width=1)
    draw.text((cur_a_x - 30, gy0 + 15), "CURSOR A", font=get_font(11, bold=True, mono=True), fill=(241, 245, 249))
    draw.text((cur_b_x - 30, gy0 + 15), "CURSOR B", font=get_font(11, bold=True, mono=True), fill=(241, 245, 249))

    # Delta X Cursor Bracket & Measurement Callout
    draw.line([(cur_a_x, gy0 + 50), (cur_b_x, gy0 + 50)], fill=(52, 211, 153), width=2)
    draw.line([(cur_a_x, gy0 + 40), (cur_a_x, gy0 + 60)], fill=(52, 211, 153), width=2)
    draw.line([(cur_b_x, gy0 + 40), (cur_b_x, gy0 + 60)], fill=(52, 211, 153), width=2)
    draw.text((cur_a_x + 80, gy0 + 26), "Δt = 184.2 ms (REACTION TIME)", font=get_font(14, bold=True, mono=True), fill=(52, 211, 153))

    # TRACE 1: CH1 (Yellow #FACC15) - GPIO 3 Button Line (3.3V Logic Level, Active-Low)
    ch1_base_y = gy0 + int(3.0 * div_h)
    ch1_high_y = ch1_base_y - 120 # 3.3V High
    ch1_low_y = ch1_base_y       # 0V Low (Pressed)

    ch1_pts = []
    for x in range(gx0, gx1 + 1):
        if x < cur_b_x:
            ch1_pts.append((x, ch1_high_y))
        elif x == cur_b_x:
            ch1_pts.append((x, ch1_high_y))
            ch1_pts.append((x, ch1_low_y))
        else:
            ch1_pts.append((x, ch1_low_y))
    for i in range(len(ch1_pts) - 1):
        draw.line([ch1_pts[i], ch1_pts[i + 1]], fill=(250, 204, 21), width=3)

    # TRACE 2: CH2 (Cyan #38BDF8) - GPIO 5 Piezo Buzzer PWM Output (880 Hz Square Wave)
    ch2_base_y = gy0 + int(5.5 * div_h)
    ch2_high_y = ch2_base_y - 110 # 3.3V High
    ch2_low_y = ch2_base_y       # 0V Low

    ch2_pts = []
    pwm_period = 16 # pixels
    for x in range(gx0, gx1 + 1):
        if x < cur_a_x:
            # Idle Low
            ch2_pts.append((x, ch2_low_y))
        elif x <= cur_b_x + 60:
            # Square wave burst
            phase = (x - cur_a_x) % pwm_period
            y = ch2_high_y if phase < pwm_period // 2 else ch2_low_y
            ch2_pts.append((x, y))
        else:
            ch2_pts.append((x, ch2_low_y))
    for i in range(len(ch2_pts) - 1):
        draw.line([ch2_pts[i], ch2_pts[i + 1]], fill=(56, 189, 248), width=3)

    # TRACE 3: CH3 (Magenta #EC4899) - I2C SCL Clock Burst (400 kHz display buffer flush)
    ch3_base_y = gy0 + int(7.5 * div_h)
    ch3_high_y = ch3_base_y - 80
    ch3_low_y = ch3_base_y

    ch3_pts = []
    i2c_period = 6
    for x in range(gx0, gx1 + 1):
        if cur_a_x - 120 <= x <= cur_a_x:
            # I2C burst triggering stimulus on OLED
            phase = (x - cur_a_x) % i2c_period
            y = ch3_high_y if phase < i2c_period // 2 else ch3_low_y
            ch3_pts.append((x, y))
        else:
            ch3_pts.append((x, ch3_high_y)) # I2C Idle High
    for i in range(len(ch3_pts) - 1):
        draw.line([ch3_pts[i], ch3_pts[i + 1]], fill=(236, 72, 153), width=2)

    # Channel Labels on Left
    draw.rounded_rectangle([(gx0 + 15, ch1_high_y - 20), (gx0 + 75, ch1_high_y + 6)], radius=4, fill=(250, 204, 21))
    draw.text((gx0 + 22, ch1_high_y - 16), "1·CH1", font=get_font(12, bold=True, mono=True), fill=(15, 23, 42))

    draw.rounded_rectangle([(gx0 + 15, ch2_high_y - 20), (gx0 + 75, ch2_high_y + 6)], radius=4, fill=(56, 189, 248))
    draw.text((gx0 + 22, ch2_high_y - 16), "2·CH2", font=get_font(12, bold=True, mono=True), fill=(15, 23, 42))

    draw.rounded_rectangle([(gx0 + 15, ch3_high_y - 20), (gx0 + 75, ch3_high_y + 6)], radius=4, fill=(236, 72, 153))
    draw.text((gx0 + 22, ch3_high_y - 16), "3·CH3", font=get_font(12, bold=True, mono=True), fill=(15, 23, 42))

    # Right DSO Measurement Sidebar
    side_x = gx1 + 25
    side_w = w - 40 - side_x
    draw.rounded_rectangle([(side_x, gy0), (side_x + side_w, gy1)], radius=12, fill=(24, 34, 53), outline=(51, 65, 85), width=2)
    draw.text((side_x + 18, gy0 + 18), "MEASUREMENT SUITE", font=get_font(15, bold=True, mono=True), fill=(56, 189, 248))

    dso_measures = [
        ("ΔX (Cursor A -> B)", "184.2 ms", (52, 211, 153)),
        ("1 / ΔX (Eq. Freq)", "5.428 Hz", (203, 213, 225)),
        ("CH1 Vmax (Logic 1)", "3.31 V", (250, 204, 21)),
        ("CH1 Vmin (Logic 0)", "0.04 V", (250, 204, 21)),
        ("CH1 Fall Time (tf)", "42.8 ns", (250, 204, 21)),
        ("CH2 Freq (PWM Tone)", "880.4 Hz", (56, 189, 248)),
        ("CH2 Duty Cycle", "50.0 %", (56, 189, 248)),
        ("CH2 Vpp Amplitude", "3.28 V", (56, 189, 248)),
        ("CH3 I2C Bus Rate", "392.1 kHz", (236, 72, 153))
    ]
    my_pos = gy0 + 55
    for m_lbl, m_val, m_col in dso_measures:
        draw.text((side_x + 18, my_pos), m_lbl, font=get_font(11), fill=(148, 163, 184))
        draw.text((side_x + 18, my_pos + 18), m_val, font=get_font(14, bold=True, mono=True), fill=m_col)
        my_pos += 44

    # Bottom Channel Status Bar
    bbar_y = gy1 + 15
    draw.rounded_rectangle([(gx0, bbar_y), (gx1, bbar_y + 55)], radius=8, fill=(18, 24, 38), outline=(51, 65, 85), width=1)
    draw.text((gx0 + 25, bbar_y + 16), "CH1: 1.00V/div 1X DC (BTN_ACTION · GP3)", font=get_font(12, bold=True, mono=True), fill=(250, 204, 21))
    draw.text((gx0 + 440, bbar_y + 16), "CH2: 1.00V/div 1X DC (BUZZER_PWM · GP5)", font=get_font(12, bold=True, mono=True), fill=(56, 189, 248))
    draw.text((gx0 + 860, bbar_y + 16), "CH3: 1.00V/div 1X DC (OLED_SCL · GP1)", font=get_font(12, bold=True, mono=True), fill=(236, 72, 153))

    out_file = os.path.join(OUTPUT_DIR, "12_reaction_game_timing_oscilloscope.png")
    img.save(out_file, quality=95)
    print(f"[OK] Generated: {out_file}")

if __name__ == "__main__":
    print("Rendering Batch 3: Images 09 - 12...")
    render_09_drc_validation()
    render_10_gerber_stackup()
    render_11_state_machine()
    render_12_oscilloscope()
    print("Batch 3 completed!")
