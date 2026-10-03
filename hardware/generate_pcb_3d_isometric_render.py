"""
High-Precision 3D Isometric Board Visualizer for Pocket Companion
Generates: C:\\Users\\white\\pocket-companion\\assets\\journal_media\\08_pcb_3d_render_isometric.png (1920x1080)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_PATH = r"C:\Users\white\pocket-companion\assets\journal_media\08_pcb_3d_render_isometric.png"
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

# -----------------------------------------------------------------------------
# 3D CAMERA & PERSPECTIVE PROJECTION
# -----------------------------------------------------------------------------
T = np.array([0.0, 0.0, 2.0])          # Center target (mm)
psi = np.radians(-38.0)                # Yaw
theta = np.radians(31.0)              # Pitch
d = np.array([np.cos(theta)*np.sin(psi), -np.cos(theta)*np.cos(psi), np.sin(theta)])
D = 152.0                             # Distance
C = T + D * d                         # Camera center
f = -d                                # Forward
up = np.array([0.0, 0.0, 1.0])
r = np.cross(f, up)
r = r / np.linalg.norm(r)
u = np.cross(r, f)

F_SCALE = 2850.0                      # Focal scale
U0, V0 = 960.0, 530.0                 # Screen center

def proj(p):
    pc = np.array(p, dtype=float) - C
    xc = float(np.dot(pc, r))
    yc = float(np.dot(pc, u))
    zc = float(np.dot(pc, f))
    if zc <= 0.001:
        zc = 0.001
    return (U0 + F_SCALE * xc / zc, V0 - F_SCALE * yc / zc)

def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = np.matrix(matrix, dtype=float)
    B = np.array(pb).reshape(8)
    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

# -----------------------------------------------------------------------------
# 1. 2D HIGH-RESOLUTION PCB TOP SURFACE TEXTURE (2600 x 1900 px)
# Mapping: X in [-26, +26] mm -> [0, 2600] px, Y in [+19, -19] mm -> [0, 1900] px
# -----------------------------------------------------------------------------
def mm2px(x, y):
    px = int((x + 26.0) / 52.0 * 2600.0)
    py = int((19.0 - y) / 38.0 * 1900.0)
    return px, py

def create_top_texture():
    tw, th = 2600, 1900
    tex = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)

    cr = 150  # 3.0mm corner radius in px
    # Matte Black Solder Mask Substrate
    draw.rounded_rectangle([(0, 0), (tw - 1, th - 1)], radius=cr, fill=(22, 22, 26, 255))

    # Add realistic micro-texture grain
    np.random.seed(101)
    grain = np.random.randint(-4, 5, (th, tw, 3), dtype=np.int16)
    arr = np.array(tex, dtype=np.int16)
    arr[:, :, :3] = np.clip(arr[:, :, :3] + grain, 0, 255)
    tex = Image.fromarray(np.uint8(arr), "RGBA")
    draw = ImageDraw.Draw(tex)

    # Ground Plane Edge Isolation
    draw.rounded_rectangle([(35, 35), (tw - 36, th - 36)], radius=cr - 25, outline=(30, 30, 38, 255), width=3)

    # 4 Corner M2.5 Mounting Holes (Outer dia 5.0mm = 250px, Drill 2.7mm = 135px)
    mount_coords = [(-23.5, 16.5), (23.5, 16.5), (23.5, -16.5), (-23.5, -16.5)]
    for mx_mm, my_mm in mount_coords:
        mx, my = mm2px(mx_mm, my_mm)
        draw.ellipse([(mx - 140, my - 140), (mx + 140, my + 140)], fill=(16, 16, 20, 255))
        draw.ellipse([(mx - 125, my - 125), (mx + 125, my + 125)], fill=(234, 179, 8, 255), outline=(202, 138, 4, 255), width=4)
        draw.ellipse([(mx - 68, my - 68), (mx + 68, my + 68)], fill=(8, 8, 10, 255), outline=(161, 98, 7, 255), width=3)

    # Ground stitching vias
    via_coords = [
        (-21.0, 5.0), (-21.0, -10.0), (23.5, 5.0), (23.5, -5.0),
        (-10.0, 16.5), (0.0, 16.5), (10.0, 16.5),
        (-18.0, -16.5), (-7.0, -16.5), (7.0, -16.5), (18.0, -16.5),
        (2.0, -5.0), (14.0, -5.0)
    ]
    for vx_mm, vy_mm in via_coords:
        vx, vy = mm2px(vx_mm, vy_mm)
        draw.ellipse([(vx - 28, vy - 28), (vx + 28, vy + 28)], fill=(234, 179, 8, 255), outline=(202, 138, 4, 255), width=2)
        draw.ellipse([(vx - 12, vy - 12), (vx + 12, vy + 12)], fill=(8, 8, 10, 255))

    # Copper Traces Underneath Solder Mask
    trace_col = (36, 38, 48, 255)
    trace_hi = (48, 52, 66, 255)
    def trace(mm_pts, w=16):
        pts = [mm2px(x, y) for x, y in mm_pts]
        draw.line(pts, fill=trace_hi, width=w + 6)
        draw.line(pts, fill=trace_col, width=w)

    # Trace routing
    trace([(-8.0, 4.0), (-3.0, 4.0), (2.0, 9.0), (7.0, 9.0)], w=14)   # SDA to OLED
    trace([(-8.0, 2.0), (-2.0, 2.0), (3.0, 7.0), (9.0, 7.0)], w=14)   # SCL to OLED
    trace([(-8.0, -2.0), (-8.0, -8.0), (-13.0, -8.0), (-13.0, -11.0)], w=14) # GP2 to Left Button
    trace([(-6.0, -4.0), (-6.0, -8.0), (0.0, -8.0), (0.0, -11.0)], w=14)       # GP3 to Action Button
    trace([(-4.0, -4.0), (-4.0, -7.0), (13.0, -7.0), (13.0, -11.0)], w=14)     # GP4 to Right Button
    trace([(-1.0, 0.0), (5.0, 0.0), (14.0, -2.0), (18.0, -2.0)], w=14)         # GP5 to Buzzer
    trace([(-20.0, 11.0), (-23.0, 11.0), (-23.0, -2.0)], w=28)                 # VBAT from JST to Switch
    trace([(-22.0, -5.0), (-15.0, -5.0), (-15.0, 0.0), (-12.0, 0.0)], w=28)   # Switched power to RP2040

    # Gold ENIG Pads
    gold_fill = (245, 158, 11, 255)
    gold_edge = (180, 83, 9, 255)
    gold_hi = (253, 224, 71, 255)
    def pad_mm(x0, y0, x1, y1, r=8):
        px0, py1 = mm2px(x0, y0)
        px1, py0 = mm2px(x1, y1)
        if px0 > px1: px0, px1 = px1, px0
        if py0 > py1: py0, py1 = py1, py0
        draw.rounded_rectangle([(px0 - 8, py0 - 8), (px1 + 8, py1 + 8)], radius=r + 4, fill=(14, 14, 18, 255))
        draw.rounded_rectangle([(px0, py0), (px1, py1)], radius=r, fill=gold_fill, outline=gold_edge, width=2)
        draw.line([(px0 + 4, py0 + 3), (px1 - 4, py0 + 3)], fill=gold_hi, width=2)

    # RP2040-Zero Solder Pads on Main Board:
    # Module is from X = -17 to +1, Y = -5.75 to +17.75
    # Left edge pads (X = -17.5 to -16.5)
    for i in range(9):
        py = -4.0 + i * 2.3
        pad_mm(-17.8, py - 0.4, -16.2, py + 0.4, r=4)
    # Right edge pads (X = 0.5 to 1.8)
    for i in range(9):
        py = -4.0 + i * 2.3
        pad_mm(0.2, py - 0.4, 1.8, py + 0.4, r=4)
    # Bottom edge pads (Y = -6.5 to -5.0)
    for i in range(5):
        px = -14.0 + i * 3.0
        pad_mm(px - 0.4, -6.5, px + 0.4, -5.0, r=4)

    # OLED 4-Pin Female Header Pads (X = 4.0 to 14.5, Y = 12.0)
    for px in [5.5, 8.5, 11.5, 14.5]:
        pad_mm(px - 0.7, 11.3, px + 0.7, 12.7, r=8)
        cx, cy = mm2px(px, 12.0)
        draw.ellipse([(cx - 14, cy - 14), (cx + 14, cy + 14)], fill=(8, 8, 10, 255))

    # 3x Tactile Push Button Footprints (X = -13, 0, +13, Y = -12)
    for bx in [-13.0, 0.0, 13.0]:
        pad_mm(bx - 3.8, -13.5, bx - 2.6, -12.5, r=4)
        pad_mm(bx + 2.6, -13.5, bx + 3.8, -12.5, r=4)
        pad_mm(bx - 3.8, -11.5, bx - 2.6, -10.5, r=4)
        pad_mm(bx + 2.6, -11.5, bx + 3.8, -10.5, r=4)

    # Slide Switch Footprint (Left edge: X = -23.5, Y = -4.0)
    for sy in [-5.5, -4.0, -2.5]:
        pad_mm(-24.5, sy - 0.4, -22.5, sy + 0.4, r=4)
    pad_mm(-24.2, -6.8, -22.8, -6.0, r=4)
    pad_mm(-24.2, -2.0, -22.8, -1.2, r=4)

    # Buzzer Footprint (X = 19.0, Y = -3.0)
    pad_mm(17.5, -3.8, 18.5, -2.2, r=6)
    pad_mm(19.5, -3.8, 20.5, -2.2, r=6)
    for px in [18.0, 20.0]:
        cx, cy = mm2px(px, -3.0)
        draw.ellipse([(cx - 10, cy - 10), (cx + 10, cy + 10)], fill=(8, 8, 10, 255))

    # JST Battery Header Footprint (X = -21.0, Y = 12.0)
    pad_mm(-22.2, 11.2, -21.0, 12.8, r=6)
    pad_mm(-20.0, 11.2, -18.8, 12.8, r=6)
    for px in [-21.6, -19.4]:
        cx, cy = mm2px(px, 12.0)
        draw.ellipse([(cx - 12, cy - 12), (cx + 12, cy + 12)], fill=(8, 8, 10, 255))

    # ------------------ CRISP WHITE SILKSCREEN ------------------
    silk = (250, 250, 255, 255)
    silk_dim = (180, 185, 200, 255)

    # 1. Prominent Branding Silkscreen on Front Edge (Y in [-15, -18.5])
    # Perfectly placed between buttons and edge where it's 100% visible!
    px_b, py_b = mm2px(-18.0, -16.8)
    draw.text((px_b, py_b), "POCKET COMPANION v1.0", font=get_font(42, bold=True), fill=silk)
    draw.text((px_b + 550, py_b + 5), "· HACK CLUB HALF-LIFE", font=get_font(32, bold=True), fill=(245, 158, 11, 255))
    draw.text((px_b + 980, py_b + 10), "· OPEN HARDWARE RP2040", font=get_font(26, mono=True), fill=silk_dim)

    # 2. Hack Club Half-Life Emblem (Placed prominently in clear view at X=14 to 22, Y=5 to 14)
    # Between OLED and right mounting hole!
    hx, hy = mm2px(16.5, 9.5)
    draw.rounded_rectangle([(hx - 60, hy - 60), (hx + 60, hy + 60)], radius=24, outline=silk, width=5)
    # Lambda symbol
    draw.line([(hx - 22, hy - 32), (hx + 18, hy + 32)], fill=silk, width=8)
    draw.line([(hx + 18, hy - 32), (hx - 2, hy + 2)], fill=silk, width=8)
    draw.line([(hx - 32, hy + 32), (hx - 12, hy + 32)], fill=silk, width=6)
    draw.line([(hx + 8, hy + 32), (hx + 28, hy + 32)], fill=silk, width=6)
    draw.text((hx - 48, hy + 75), "HALF-LIFE", font=get_font(18, bold=True, mono=True), fill=(245, 158, 11, 255))
    draw.text((hx - 40, hy + 98), "YSWS 2026", font=get_font(14, mono=True), fill=silk_dim)

    # 3. Component Outlines & Reference Designators
    # U1 (RP2040-Zero)
    ux0, uy0 = mm2px(-17.0, 17.5)
    ux1, uy1 = mm2px(1.0, -5.75)
    draw.rectangle([(ux0, uy0), (ux1, uy1)], outline=silk_dim, width=2)
    draw.text((ux0 + 20, uy0 + 15), "U1 · RP2040-ZERO", font=get_font(22, bold=True, mono=True), fill=silk)

    # 3x Buttons Labels (SW1, SW2, SW3)
    btns = [(-13.0, "SW1", "◄ LEFT", "GP2"), (0.0, "SW2", "● ACTION", "GP3"), (13.0, "SW3", "RIGHT ►", "GP4")]
    for bx_mm, ref, fnc, pin in btns:
        bx, by = mm2px(bx_mm, -12.0)
        draw.rounded_rectangle([(bx - 100, by - 100), (bx + 100, by + 100)], radius=16, outline=silk_dim, width=2)
        draw.text((bx - 35, by - 95), ref, font=get_font(20, bold=True, mono=True), fill=silk)
        draw.text((bx - 50, by + 105), fnc, font=get_font(22, bold=True), fill=silk)
        draw.text((bx - 28, by + 135), pin, font=get_font(16, mono=True), fill=silk_dim)

    # SW_PWR (Slide Switch)
    sx, sy = mm2px(-23.5, -4.0)
    draw.text((sx - 35, sy - 85), "SW_PWR", font=get_font(18, bold=True, mono=True), fill=silk)
    draw.text((sx - 35, sy - 50), "OFF", font=get_font(16, mono=True), fill=silk_dim)
    draw.text((sx - 35, sy + 40), "ON", font=get_font(16, bold=True, mono=True), fill=(52, 211, 153, 255))

    # BZ1 (Buzzer)
    bx, by = mm2px(19.0, -3.0)
    draw.ellipse([(bx - 120, by - 120), (bx + 120, by + 120)], outline=silk_dim, width=2)
    draw.text((bx - 55, by - 145), "BZ1 · BUZZER", font=get_font(18, bold=True, mono=True), fill=silk)
    draw.text((bx - 50, by - 40), "+", font=get_font(24, bold=True), fill=(239, 68, 68, 255))
    draw.text((bx + 35, by - 40), "-", font=get_font(24, bold=True), fill=silk_dim)
    draw.text((bx - 40, by + 128), "GP5 PWM", font=get_font(16, mono=True), fill=silk_dim)

    # J1 (Battery Connector)
    jx, jy = mm2px(-21.0, 12.0)
    draw.rectangle([(jx - 80, jy - 80), (jx + 80, jy + 80)], outline=silk_dim, width=2)
    draw.text((jx - 70, jy - 110), "J1 · BATT 3.7V", font=get_font(18, bold=True, mono=True), fill=silk)
    draw.text((jx - 65, jy + 88), "+ RED", font=get_font(16, bold=True, mono=True), fill=(239, 68, 68, 255))
    draw.text((jx + 15, jy + 88), "- BLK", font=get_font(16, bold=True, mono=True), fill=silk_dim)

    # Altoids Tin Border Guide
    draw.rounded_rectangle([(60, 60), (tw - 61, th - 61)], radius=cr - 40, outline=(90, 95, 110, 140), width=2)

    return tex

# -----------------------------------------------------------------------------
# 2. 3D GEOMETRY UTILITIES
# -----------------------------------------------------------------------------
def render_3d_box(img_draw, x0, y0, z0, x1, y1, z1, col_top, col_front, col_left, col_border=None):
    p000 = proj((x0, y0, z0))
    p100 = proj((x1, y0, z0))
    p110 = proj((x1, y1, z0))
    p010 = proj((x0, y1, z0))

    p001 = proj((x0, y0, z1))
    p101 = proj((x1, y0, z1))
    p111 = proj((x1, y1, z1))
    p011 = proj((x0, y1, z1))

    # Visible faces: Left (X=x0), Front (Y=y0), Top (Z=z1)
    img_draw.polygon([p010, p000, p001, p011], fill=col_left, outline=col_border)
    img_draw.polygon([p000, p100, p101, p001], fill=col_front, outline=col_border)
    img_draw.polygon([p001, p101, p111, p011], fill=col_top, outline=col_border)

def render_3d_cylinder(img_draw, cx, cy, z0, z1, radius, col_top, col_side_dark, col_side_light, segments=36):
    angles = np.linspace(0, 2*np.pi, segments, endpoint=False)
    pts_bot = [proj((cx + radius * np.cos(a), cy + radius * np.sin(a), z0)) for a in angles]
    pts_top = [proj((cx + radius * np.cos(a), cy + radius * np.sin(a), z1)) for a in angles]

    # Calculate camera distance to sort quads back-to-front
    quad_info = []
    for i in range(segments):
        i_next = (i + 1) % segments
        mid_angle = (angles[i] + angles[i_next]) / 2.0
        mid_x = cx + radius * np.cos(mid_angle)
        mid_y = cy + radius * np.sin(mid_angle)
        mid_z = (z0 + z1) / 2.0
        pc = np.array([mid_x, mid_y, mid_z]) - C
        dist = np.dot(pc, f)
        quad_info.append((dist, i, i_next, mid_angle))

    # Sort furthest to closest
    quad_info.sort(key=lambda x: x[0], reverse=True)

    light_dir = np.array([-0.707, -0.707, 0.0])
    for dist, i, i_next, mid_angle in quad_info:
        norm = np.array([np.cos(mid_angle), np.sin(mid_angle), 0.0])
        shade = 0.45 + 0.55 * max(0.0, np.dot(norm, light_dir))
        r_c = int(col_side_dark[0] * (1 - shade) + col_side_light[0] * shade)
        g_c = int(col_side_dark[1] * (1 - shade) + col_side_light[1] * shade)
        b_c = int(col_side_dark[2] * (1 - shade) + col_side_light[2] * shade)
        quad = [pts_bot[i], pts_bot[i_next], pts_top[i_next], pts_top[i]]
        img_draw.polygon(quad, fill=(r_c, g_c, b_c, 255))

    img_draw.polygon(pts_top, fill=col_top)

# -----------------------------------------------------------------------------
# MAIN GENERATOR
# -----------------------------------------------------------------------------
def generate_isometric_render():
    w, h = 1920, 1080
    print("[1/5] Setting up CAD studio viewport...")

    base = Image.new("RGBA", (w, h), (11, 15, 25, 255))
    draw_base = ImageDraw.Draw(base)

    # Radial studio lighting
    cx_s, cy_s = w // 2, h // 2 + 30
    for rad in range(700, 0, -25):
        alpha = int((1.0 - rad / 700.0) * 22)
        draw_base.ellipse([(cx_s - rad * 1.5, cy_s - rad), (cx_s + rad * 1.5, cy_s + rad)], fill=(18 + alpha, 24 + alpha, 40 + alpha, 255))

    # Floor grid at Z = -4.0mm
    grid_col = (20, 28, 44, 255)
    for gx in range(-50, 51, 10):
        draw_base.line([proj((gx, -45, -4.0)), proj((gx, 45, -4.0))], fill=grid_col, width=1)
    for gy in range(-40, 41, 10):
        draw_base.line([proj((-55, gy, -4.0)), proj((55, gy, -4.0))], fill=grid_col, width=1)

    # Floor drop shadow
    print("[2/5] Rendering ambient occlusion & floor shadow...")
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_sh = ImageDraw.Draw(shadow_layer)
    sh_corners = [proj((-25, 20, -3.8)), proj((28, 20, -3.8)), proj((28, -18, -3.8)), proj((-25, -18, -3.8))]
    draw_sh.polygon(sh_corners, fill=(0, 0, 0, 160))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(26))
    base.alpha_composite(shadow_layer)

    # 3D PCB Substrate (1.6mm thickness: Z = -0.8 to +0.8 mm)
    print("[3/5] Rendering 3D PCB FR4 edges & substrate...")
    pcb_draw = ImageDraw.Draw(base)

    p_bl_bot = proj((-26, -19, -0.8))
    p_br_bot = proj((26, -19, -0.8))
    p_br_top = proj((26, -19, 0.8))
    p_bl_top = proj((-26, -19, 0.8))
    pcb_draw.polygon([p_bl_bot, p_br_bot, p_br_top, p_bl_top], fill=(22, 28, 26, 255), outline=(35, 45, 40, 255))
    pcb_draw.line([proj((-26, -19, 0.0)), proj((26, -19, 0.0))], fill=(180, 115, 30, 255), width=2)

    p_tl_bot = proj((-26, 19, -0.8))
    p_tl_top = proj((-26, 19, 0.8))
    pcb_draw.polygon([p_bl_bot, p_tl_bot, p_tl_top, p_bl_top], fill=(16, 22, 20, 255), outline=(28, 38, 32, 255))
    pcb_draw.line([proj((-26, -19, 0.0)), proj((-26, 19, 0.0))], fill=(160, 95, 20, 255), width=2)

    # Warp 2D High-Resolution Top Texture onto 3D Top Plane (Z = +0.8 mm)
    print("[4/5] Perspective warping high-res PCB texture...")
    top_tex = create_top_texture()
    src_pts = [(0, 0), (2600, 0), (2600, 1900), (0, 1900)]
    p_tr_top = proj((26, 19, 0.8))
    dst_pts = [p_tl_top, p_tr_top, p_br_top, p_bl_top]

    coeffs = find_coeffs(dst_pts, src_pts)
    warped_top = top_tex.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    base.alpha_composite(warped_top)

    # 3D Components
    print("[5/5] Modeling & rendering 3D components...")
    comp_draw = ImageDraw.Draw(base)

    # 1. WAVESHARE RP2040-ZERO MODULE
    # Position: X in [-17, 1], Y in [-5.75, 17.75], Z in [0.8, 2.0]
    render_3d_box(comp_draw, -17.0, -5.75, 0.8, 1.0, 17.75, 2.0,
                  col_top=(24, 30, 68, 255), col_front=(16, 20, 48, 255), col_left=(12, 15, 38, 255),
                  col_border=(45, 55, 110, 255))

    # Castellated Pads & Solder Fillets
    for i in range(9):
        py = -4.0 + i * 2.3
        # Left edge
        render_3d_box(comp_draw, -17.6, py - 0.4, 0.8, -16.8, py + 0.4, 1.6,
                      col_top=(215, 220, 235, 255), col_front=(160, 170, 185, 255), col_left=(130, 140, 155, 255))
        # Right edge
        render_3d_box(comp_draw, 0.8, py - 0.4, 0.8, 1.6, py + 0.4, 1.6,
                      col_top=(215, 220, 235, 255), col_front=(160, 170, 185, 255), col_left=(130, 140, 155, 255))
    for i in range(5):
        px = -14.0 + i * 3.0
        render_3d_box(comp_draw, px - 0.4, -6.4, 0.8, px + 0.4, -5.6, 1.6,
                      col_top=(215, 220, 235, 255), col_front=(160, 170, 185, 255), col_left=(130, 140, 155, 255))

    # RP2040 QFN-56 Chip (7x7mm, Z = 2.0 to 3.0mm)
    render_3d_box(comp_draw, -11.5, 2.0, 2.0, -4.5, 9.0, 2.95,
                  col_top=(26, 28, 32, 255), col_front=(16, 18, 20, 255), col_left=(12, 14, 16, 255),
                  col_border=(45, 48, 55, 255))
    p_chip_c = proj((-8.0, 5.5, 3.0))
    comp_draw.text((p_chip_c[0] - 22, p_chip_c[1] - 8), "RP2040", font=get_font(10, bold=True, mono=True), fill=(160, 170, 185, 255))
    comp_draw.text((p_chip_c[0] - 24, p_chip_c[1] + 2), "2408 B2", font=get_font(8, mono=True), fill=(120, 130, 145, 255))

    # Crystal Oscillator
    render_3d_box(comp_draw, -14.0, -1.0, 2.0, -11.5, 1.5, 2.7,
                  col_top=(215, 220, 230, 255), col_front=(165, 170, 180, 255), col_left=(130, 135, 145, 255),
                  col_border=(235, 240, 250, 255))

    # USB-C Connector (Stainless Steel shell: X in [-12.5, -3.5], Y in [13.0, 20.2], Z in [2.0, 5.2])
    render_3d_box(comp_draw, -12.5, 13.0, 2.0, -3.5, 20.0, 5.0,
                  col_top=(200, 205, 215, 255), col_front=(150, 155, 165, 255), col_left=(120, 125, 135, 255),
                  col_border=(230, 235, 245, 255))
    p_u_mouth = proj((-8.0, 20.1, 3.5))
    comp_draw.ellipse([(p_u_mouth[0] - 16, p_u_mouth[1] - 5), (p_u_mouth[0] + 16, p_u_mouth[1] + 5)], fill=(12, 14, 18, 255))

    # 2. 0.96" OLED DISPLAY (Mounted on Female Header)
    # 4-Pin Female Header Socket on Main PCB (X = 4.0 to 16.0, Y = 11.0 to 13.0, Z = 0.8 to 4.5mm)
    render_3d_box(comp_draw, 4.0, 11.0, 0.8, 16.0, 13.0, 4.5,
                  col_top=(28, 30, 36, 255), col_front=(18, 20, 24, 255), col_left=(12, 14, 16, 255),
                  col_border=(50, 54, 64, 255))
    for px in [5.5, 8.5, 11.5, 14.5]:
        comp_draw.line([proj((px, 12.0, 4.5)), proj((px, 12.0, 5.5))], fill=(234, 179, 8, 255), width=3)

    # OLED Carrier PCB (Elevated at Z = 4.8 to 5.8mm, X in [0.0, 20.0], Y in [-1.5, 14.5])
    render_3d_box(comp_draw, 0.0, -1.5, 4.8, 20.0, 14.5, 5.8,
                  col_top=(15, 23, 42, 255), col_front=(10, 15, 28, 255), col_left=(8, 12, 22, 255),
                  col_border=(30, 41, 59, 255))

    # OLED Glass Panel (X in [1.5, 18.5], Y in [-0.5, 13.0], Z in [5.8 to 6.8mm])
    gx0, gx1 = 1.5, 18.5
    gy0, gy1 = -0.5, 13.0
    render_3d_box(comp_draw, gx0, gy0, 5.8, gx1, gy1, 6.8,
                  col_top=(8, 12, 20, 255), col_front=(5, 8, 14, 255), col_left=(3, 5, 10, 255),
                  col_border=(56, 189, 248, 255))

    # Glowing Cyan Screen Graphics on Active Area (Z = 6.85mm)
    p_sc_tl = proj((gx0 + 1.2, gy1 - 1.2, 6.85))
    p_sc_tr = proj((gx1 - 1.2, gy1 - 1.2, 6.85))
    p_sc_br = proj((gx1 - 1.2, gy0 + 1.2, 6.85))
    p_sc_bl = proj((gx0 + 1.2, gy0 + 1.2, 6.85))

    disp_w, disp_h = 512, 256
    disp_img = Image.new("RGBA", (disp_w, disp_h), (2, 6, 15, 255))
    draw_disp = ImageDraw.Draw(disp_img)
    draw_disp.text((20, 15), "[♥ ♥ ♥]  BAT: 96%  3.7V", font=get_font(22, bold=True, mono=True), fill=(56, 189, 248, 255))
    draw_disp.text((360, 15), "LVL 04", font=get_font(22, bold=True, mono=True), fill=(52, 211, 153, 255))
    draw_disp.line([(15, 48), (disp_w - 15, 48)], fill=(56, 189, 248, 255), width=2)
    draw_disp.text((120, 85), "(  *  ^  *  )", font=get_font(46, bold=True, mono=True), fill=(186, 230, 253, 255))
    draw_disp.text((150, 160), "HAPPY  ·  EXP +25", font=get_font(24, bold=True, mono=True), fill=(52, 211, 153, 255))
    draw_disp.line([(15, 205), (disp_w - 15, 205)], fill=(30, 58, 95, 255), width=2)
    draw_disp.text((20, 218), "POCKET COMPANION · RP2040", font=get_font(20, mono=True), fill=(125, 211, 252, 255))

    disp_coeffs = find_coeffs([p_sc_tl, p_sc_tr, p_sc_br, p_sc_bl], [(0, 0), (disp_w, 0), (disp_w, disp_h), (0, disp_h)])
    warped_disp = disp_img.transform((w, h), Image.PERSPECTIVE, disp_coeffs, Image.BICUBIC)
    base.alpha_composite(warped_disp)

    # 3. 3x 6x6mm TACTILE SMD PUSH BUTTONS (SW1, SW2, SW3)
    for bx in [-13.0, 0.0, 13.0]:
        render_3d_box(comp_draw, bx - 3.0, -15.0, 0.8, bx + 3.0, -9.0, 2.8,
                      col_top=(190, 195, 205, 255), col_front=(140, 145, 155, 255), col_left=(110, 115, 125, 255),
                      col_border=(220, 225, 235, 255))
        for rx, ry in [(bx - 2.2, -14.2), (bx + 2.2, -14.2), (bx - 2.2, -9.8), (bx + 2.2, -9.8)]:
            pr = proj((rx, ry, 2.82))
            comp_draw.ellipse([(pr[0] - 2, pr[1] - 2), (pr[0] + 2, pr[1] + 2)], fill=(90, 95, 105, 255))

        render_3d_cylinder(comp_draw, bx, -12.0, 2.8, 4.4, 1.75,
                           col_top=(28, 30, 36, 255), col_side_dark=(12, 14, 16), col_side_light=(40, 44, 52), segments=24)
        p_btn_top = proj((bx, -12.0, 4.42))
        comp_draw.ellipse([(p_btn_top[0] - 4, p_btn_top[1] - 3), (p_btn_top[0] + 4, p_btn_top[1] + 3)], fill=(50, 55, 65, 255))

        for lx, ly in [(bx - 3.5, -13.5), (bx + 3.5, -13.5), (bx - 3.5, -10.5), (bx + 3.5, -10.5)]:
            p_leg = proj((lx, ly, 0.8))
            comp_draw.ellipse([(p_leg[0] - 3, p_leg[1] - 2), (p_leg[0] + 3, p_leg[1] + 2)], fill=(215, 220, 235, 255))

    # 4. MINIATURE SPDT SLIDE SWITCH (SW_PWR)
    render_3d_box(comp_draw, -25.0, -6.5, 0.8, -22.0, -1.5, 3.6,
                  col_top=(180, 185, 195, 255), col_front=(130, 135, 145, 255), col_left=(100, 105, 115, 255),
                  col_border=(210, 215, 225, 255))
    render_3d_box(comp_draw, -24.2, -3.0, 3.6, -22.8, -1.8, 5.4,
                  col_top=(25, 28, 32, 255), col_front=(15, 17, 20, 255), col_left=(10, 12, 14, 255),
                  col_border=(45, 48, 55, 255))

    # 5. PASSIVE PIEZO BUZZER (BZ1)
    render_3d_cylinder(comp_draw, 19.0, -3.0, 0.8, 5.2, 4.2,
                       col_top=(26, 28, 34, 255), col_side_dark=(12, 14, 18), col_side_light=(38, 42, 50), segments=36)
    p_bz_hole = proj((19.0, -3.0, 5.25))
    comp_draw.ellipse([(p_bz_hole[0] - 7, p_bz_hole[1] - 5), (p_bz_hole[0] + 7, p_bz_hole[1] + 5)], fill=(6, 8, 10, 255), outline=(40, 44, 52, 255), width=2)
    p_bz_plus = proj((17.0, -4.0, 5.25))
    comp_draw.text((p_bz_plus[0] - 4, p_bz_plus[1] - 8), "+", font=get_font(13, bold=True), fill=(239, 68, 68, 255))

    # 6. 2-PIN JST-PH 2.0mm BATTERY HEADER (J1)
    render_3d_box(comp_draw, -23.0, 9.5, 0.8, -17.0, 14.5, 6.8,
                  col_top=(245, 245, 240, 255), col_front=(210, 210, 200, 255), col_left=(175, 175, 165, 255),
                  col_border=(255, 255, 250, 255))
    render_3d_box(comp_draw, -22.2, 10.2, 2.5, -17.8, 13.8, 6.82,
                  col_top=(140, 140, 130, 255), col_front=(90, 90, 80, 255), col_left=(70, 70, 60, 255))
    for px in [-21.2, -18.8]:
        comp_draw.line([proj((px, 12.0, 2.5)), proj((px, 12.0, 5.2))], fill=(234, 179, 8, 255), width=3)

    # ------------------ CAD HUD & ANNOTATIONS ------------------
    hud_draw = ImageDraw.Draw(base)

    # Top Header Banner
    hud_draw.rectangle([(0, 0), (w, 105)], fill=(15, 23, 42, 235))
    hud_draw.line([(0, 105), (w, 105)], fill=(30, 41, 59, 255), width=2)

    hud_draw.rounded_rectangle([(35, 20), (145, 52)], radius=6, fill=(2, 132, 199, 255))
    hud_draw.text((90, 36), "3D CAD", font=get_font(13, bold=True, mono=True), fill=(255, 255, 255), anchor="mm")

    hud_draw.text((160, 34), "POCKET COMPANION v1.0 — 3D ISOMETRIC CAD VISUALIZATION", font=get_font(22, bold=True), fill=(241, 245, 249))
    hud_draw.text((160, 66), "Double-Sided SMT FR4 Architecture · 52.0 × 38.0 × 1.6 mm · Altoids Tin Enclosure Compliance", font=get_font(14), fill=(148, 163, 184))

    badges = [
        ("FINISH", "ENIG-1U GOLD", (245, 158, 11)),
        ("MASK", "MATTE BLACK", (148, 163, 184)),
        ("STATUS", "PROD READY", (52, 211, 153))
    ]
    bx_pos = w - 420
    for b_lbl, b_val, b_col in badges:
        hud_draw.rounded_rectangle([(bx_pos, 24), (bx_pos + 120, 78)], radius=8, fill=(24, 34, 53, 255), outline=(51, 65, 85, 255), width=1)
        hud_draw.text((bx_pos + 60, 40), b_lbl, font=get_font(10, mono=True), fill=(148, 163, 184), anchor="mm")
        hud_draw.text((bx_pos + 60, 60), b_val, font=get_font(11, bold=True, mono=True), fill=b_col, anchor="mm")
        bx_pos += 130

    # Dimensions
    dim_col = (56, 189, 248, 255)
    dim_line_col = (56, 189, 248, 180)

    # 52.00 mm dimension along front edge
    p_bl = proj((-26, -19, -0.8))
    p_br = proj((26, -19, -0.8))
    off_v = 45
    p_d_bl = (p_bl[0], p_bl[1] + off_v)
    p_d_br = (p_br[0], p_br[1] + off_v)

    hud_draw.line([p_bl, (p_bl[0], p_bl[1] + off_v + 8)], fill=dim_line_col, width=1)
    hud_draw.line([p_br, (p_br[0], p_br[1] + off_v + 8)], fill=dim_line_col, width=1)
    hud_draw.line([p_d_bl, p_d_br], fill=dim_col, width=2)
    hud_draw.line([(p_d_bl[0] - 6, p_d_bl[1] - 4), (p_d_bl[0] + 6, p_d_bl[1] + 4)], fill=dim_col, width=2)
    hud_draw.line([(p_d_br[0] - 6, p_d_br[1] - 4), (p_d_br[0] + 6, p_d_br[1] + 4)], fill=dim_col, width=2)
    mid_x = (p_d_bl[0] + p_d_br[0]) / 2.0
    mid_y = (p_d_bl[1] + p_d_br[1]) / 2.0 + 18
    hud_draw.text((mid_x, mid_y), "52.00 mm", font=get_font(14, bold=True, mono=True), fill=dim_col, anchor="mm")

    # 38.00 mm dimension along left edge
    p_tl = proj((-26, 19, -0.8))
    off_h = -55
    p_d_tl = (p_tl[0] + off_h, p_tl[1])
    p_d_bl2 = (p_bl[0] + off_h, p_bl[1])
    hud_draw.line([p_tl, (p_tl[0] + off_h - 8, p_tl[1])], fill=dim_line_col, width=1)
    hud_draw.line([p_bl, (p_bl[0] + off_h - 8, p_bl[1])], fill=dim_line_col, width=1)
    hud_draw.line([p_d_tl, p_d_bl2], fill=dim_col, width=2)
    hud_draw.line([(p_d_tl[0] - 4, p_d_tl[1] - 6), (p_d_tl[0] + 4, p_d_tl[1] + 6)], fill=dim_col, width=2)
    hud_draw.line([(p_d_bl2[0] - 4, p_d_bl2[1] - 6), (p_d_bl2[0] + 4, p_d_bl2[1] + 6)], fill=dim_col, width=2)
    mid_wx = (p_d_tl[0] + p_d_bl2[0]) / 2.0 - 20
    mid_wy = (p_d_tl[1] + p_d_bl2[1]) / 2.0
    hud_draw.text((mid_wx, mid_wy), "38.00 mm", font=get_font(14, bold=True, mono=True), fill=dim_col, anchor="rm")

    # Thickness callout
    p_thick_mid = ((p_bl_top[0] + p_bl_bot[0]) / 2.0, (p_bl_top[1] + p_bl_bot[1]) / 2.0)
    p_thick_txt = (p_thick_mid[0] - 90, p_thick_mid[1] + 25)
    hud_draw.line([p_thick_mid, p_thick_txt], fill=(245, 158, 11, 200), width=1)
    hud_draw.text(p_thick_txt, "t = 1.60 mm", font=get_font(12, bold=True, mono=True), fill=(245, 158, 11), anchor="rm")

    # Callouts
    def draw_callout(target_3d, label_title, label_sub, text_pos, anchor="lm"):
        pt_scr = proj(target_3d)
        hud_draw.ellipse([(pt_scr[0] - 4, pt_scr[1] - 4), (pt_scr[0] + 4, pt_scr[1] + 4)], fill=(56, 189, 248, 255), outline=(255, 255, 255), width=1)
        elbow = (text_pos[0] - 15 if anchor=="lm" else text_pos[0] + 15, pt_scr[1])
        hud_draw.line([pt_scr, elbow, (text_pos[0], text_pos[1])], fill=(56, 189, 248, 180), width=1)

        tw = 260
        tx0 = text_pos[0] if anchor=="lm" else text_pos[0] - tw
        hud_draw.rounded_rectangle([(tx0, text_pos[1] - 20), (tx0 + tw, text_pos[1] + 22)], radius=6, fill=(15, 23, 42, 220), outline=(51, 65, 85, 255), width=1)
        hud_draw.text((tx0 + 10, text_pos[1] - 8), label_title, font=get_font(12, bold=True), fill=(241, 245, 249))
        hud_draw.text((tx0 + 10, text_pos[1] + 8), label_sub, font=get_font(10, mono=True), fill=(56, 189, 248))

    draw_callout((-8.0, 16.5, 4.0), "U1 · RP2040-Zero (USB-C)", "Waveshare Cortex-M0+ 133MHz", (80, 220), anchor="lm")
    draw_callout((-20.0, 12.0, 5.0), "J1 · LiPo Battery Header", "JST-PH 2.0mm 3.7V Input", (80, 360), anchor="lm")
    draw_callout((-23.5, -4.0, 3.5), "SW_PWR · Slide Switch", "SPDT Power Disconnect", (80, 500), anchor="lm")

    draw_callout((10.0, 6.0, 7.0), "DISP1 · 0.96\" OLED", "SSD1306 128×64 Monochrome I2C", (1580, 240), anchor="rm")
    draw_callout((19.0, -3.0, 4.0), "BZ1 · Piezo Transducer", "9mm Passive Buzzer (GP5 PWM)", (1580, 380), anchor="rm")
    draw_callout((0.0, -12.0, 4.0), "SW1-SW3 · User Inputs", "3× 6×6mm Tactile Buttons", (1580, 520), anchor="rm")

    # Bottom Right Specs Card
    card_w, card_h = 420, 140
    card_x, card_y = w - 40 - card_w, h - 30 - card_h
    hud_draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=10, fill=(15, 23, 42, 235), outline=(51, 65, 85, 255), width=1)
    hud_draw.text((card_x + 16, card_y + 14), "MANUFACTURING SPECIFICATION FIT", font=get_font(13, bold=True), fill=(56, 189, 248))

    specs = [
        ("Layer Stackup", "2-Layer FR4 (1.6mm Finished, 1.0 oz Cu)"),
        ("Solder Mask / Legend", "Matte Black Mask / Crisp White Silk"),
        ("Surface Finish", "ENIG-1U (Electroless Nickel Immersion Gold)"),
        ("Form Factor", "52.0 × 38.0 mm (Altoids Mint Tin Compliant)"),
        ("Turnaround / Yield", "JLCPCB Standard Class-2 / 100% Pass")
    ]
    sy = card_y + 40
    for sk, sv in specs:
        hud_draw.text((card_x + 16, sy), sk, font=get_font(10), fill=(148, 163, 184))
        hud_draw.text((card_x + 155, sy), sv, font=get_font(10, bold=True, mono=True), fill=(241, 245, 249))
        sy += 18

    base.convert("RGB").save(OUTPUT_PATH, "PNG", quality=95)
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"[SUCCESS] Saved updated 3D render: {OUTPUT_PATH}")
    print(f"Dimensions: {w}x{h}, File Size: {file_size:,} bytes")

if __name__ == "__main__":
    generate_isometric_render()
