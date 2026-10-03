"""
Render all individual layers and composite views using PyGerber
to verify 100% trace and pad connectivity of Pocket Companion v2.0.
"""

import os
import re
from PIL import Image, ImageDraw
from pygerber.gerberx3.api import ColorScheme, RGBA, Rasterized2DLayer, Rasterized2DLayerParams

RAW_GERBERS_DIR = r"C:\Users\white\pocket-companion\hardware\gerbers\raw_gerbers"
RENDERED_LAYERS_DIR = r"C:\Users\white\pocket-companion\hardware\gerbers\rendered_layers"

os.makedirs(RENDERED_LAYERS_DIR, exist_ok=True)

def parse_drill_to_gerber(drl_path):
    with open(drl_path, "r") as f:
        content = f.read()

    tools = {}
    for line in content.splitlines():
        line = line.strip()
        m = re.match(r"T(\d+)C([\d.]+)", line)
        if m:
            tools[int(m.group(1))] = float(m.group(2))

    g_lines = [
        "G04 Converted Excellon Drill to RS-274X*",
        "%FSLAX35Y35*%",
        "%MOMM*%",
        "%LPD*%"
    ]

    tool_ap = {}
    for idx, (t_id, dia) in enumerate(sorted(tools.items())):
        ap_id = 10 + idx
        tool_ap[t_id] = ap_id
        g_lines.append(f"%ADD{ap_id}C,{dia:.3f}*%")

    for line in content.splitlines():
        line = line.strip()
        m_tool = re.match(r"T(\d+)$", line)
        if m_tool:
            t_id = int(m_tool.group(1))
            g_lines.append(f"D{tool_ap[t_id]}*")
            continue
        m_xy = re.match(r"X([-\d]+)Y([-\d]+)", line)
        if m_xy:
            g_lines.append(f"X{m_xy.group(1)}Y{m_xy.group(2)}D03*")

    g_lines.append("M02*")
    return "\n".join(g_lines)

def render_layer(source, is_code, color_hex, out_path, dpi=600):
    scheme = ColorScheme(
        background_color=RGBA.from_hex("#0B0F19FF"),
        clear_color=RGBA.from_hex("#0B0F19FF"),
        solid_color=RGBA.from_hex(color_hex),
        clear_region_color=RGBA.from_hex("#0B0F19FF"),
        solid_region_color=RGBA.from_hex(color_hex),
    )
    if is_code:
        params = Rasterized2DLayerParams(source_code=source, colors=scheme, dpi=dpi)
    else:
        params = Rasterized2DLayerParams(source_path=source, colors=scheme, dpi=dpi)

    layer = Rasterized2DLayer(options=params)
    res = layer.render()
    img = res.get_image()
    img.save(out_path)
    print(f"[OK] Rendered layer: {out_path} ({os.path.getsize(out_path)} bytes)")
    return img

def render_transparent(source, is_code, color_hex, dpi=800):
    scheme = ColorScheme(
        background_color=RGBA.from_hex("#00000000"),
        clear_color=RGBA.from_hex("#00000000"),
        solid_color=RGBA.from_hex(color_hex),
        clear_region_color=RGBA.from_hex("#00000000"),
        solid_region_color=RGBA.from_hex(color_hex),
    )
    if is_code:
        params = Rasterized2DLayerParams(source_code=source, colors=scheme, dpi=dpi)
    else:
        params = Rasterized2DLayerParams(source_path=source, colors=scheme, dpi=dpi)

    layer = Rasterized2DLayer(options=params)
    res = layer.render()
    img = res.get_image()
    bbox = res.get_properties().gerber_bounding_box
    return img, bbox

def render_all():
    print("=== Rendering Individual Gerber Layers via PyGerber ===")
    dpi = 600

    # 1. GKO
    gko_path = os.path.join(RAW_GERBERS_DIR, "Gerber_BoardOutline.GKO")
    render_layer(gko_path, False, "#FACC15FF", os.path.join(RENDERED_LAYERS_DIR, "board_outline_gko.png"), dpi=dpi)

    # 2. GTL (Top Copper)
    gtl_path = os.path.join(RAW_GERBERS_DIR, "Gerber_TopLayer.GTL")
    render_layer(gtl_path, False, "#E11D48FF", os.path.join(RENDERED_LAYERS_DIR, "top_copper_gtl.png"), dpi=dpi)

    # 3. GBL (Bottom Copper)
    gbl_path = os.path.join(RAW_GERBERS_DIR, "Gerber_BottomLayer.GBL")
    render_layer(gbl_path, False, "#38BDF8FF", os.path.join(RENDERED_LAYERS_DIR, "bottom_copper_gbl.png"), dpi=dpi)

    # 4. GTS (Top Solder Mask)
    gts_path = os.path.join(RAW_GERBERS_DIR, "Gerber_TopSolderMask.GTS")
    render_layer(gts_path, False, "#10B981FF", os.path.join(RENDERED_LAYERS_DIR, "top_soldermask_gts.png"), dpi=dpi)

    # 5. GBS (Bottom Solder Mask)
    gbs_path = os.path.join(RAW_GERBERS_DIR, "Gerber_BottomSolderMask.GBS")
    render_layer(gbs_path, False, "#A855F7FF", os.path.join(RENDERED_LAYERS_DIR, "bottom_soldermask_gbs.png"), dpi=dpi)

    # 6. GTO (Top Silkscreen)
    gto_path = os.path.join(RAW_GERBERS_DIR, "Gerber_TopSilkScreen.GTO")
    render_layer(gto_path, False, "#FFFFFFFF", os.path.join(RENDERED_LAYERS_DIR, "top_silkscreen_gto.png"), dpi=dpi)

    # 7. GBO (Bottom Silkscreen)
    gbo_path = os.path.join(RAW_GERBERS_DIR, "Gerber_BottomSilkScreen.GBO")
    render_layer(gbo_path, False, "#FFFFFFFF", os.path.join(RENDERED_LAYERS_DIR, "bottom_silkscreen_gbo.png"), dpi=dpi)

    # 8. DRL (Drills)
    drl_path = os.path.join(RAW_GERBERS_DIR, "Drill_PTH_Through.DRL")
    drl_code = parse_drill_to_gerber(drl_path)
    render_layer(drl_code, True, "#F59E0BFF", os.path.join(RENDERED_LAYERS_DIR, "drill_holes_drl.png"), dpi=dpi)

    print("=== Generating Composite Multi-Layer Verification Image ===")
    cdpi = 800
    margin_mm = 2.0
    min_x, max_x = -margin_mm, 52.0 + margin_mm
    min_y, max_y = -margin_mm, 38.0 + margin_mm
    w_px = int((max_x - min_x) / 25.4 * cdpi)
    h_px = int((max_y - min_y) / 25.4 * cdpi)

    comp = Image.new("RGBA", (w_px, h_px), (15, 23, 42, 255))
    draw = ImageDraw.Draw(comp)

    # FR-4 Purple Substrate
    bx0 = int((0.0 - min_x) / 25.4 * cdpi)
    by0 = int((max_y - 38.0) / 25.4 * cdpi)
    bx1 = int((52.0 - min_x) / 25.4 * cdpi)
    by1 = int((max_y - 0.0) / 25.4 * cdpi)
    rad = int(3.0 / 25.4 * cdpi)
    draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=rad, fill=(46, 16, 101, 255))

    def paste(img, bbox):
        px = int((float(bbox.min_x.as_millimeters()) - min_x) / 25.4 * cdpi)
        py = int((max_y - float(bbox.max_y.as_millimeters())) / 25.4 * cdpi)
        comp.alpha_composite(img, (px, py))

    # Paste Bottom Copper (Blue semi-transparent)
    img_gbl, bbox_gbl = render_transparent(gbl_path, False, "#38BDF8BB", dpi=cdpi)
    paste(img_gbl, bbox_gbl)

    # Paste Top Copper (Red semi-transparent)
    img_gtl, bbox_gtl = render_transparent(gtl_path, False, "#F43F5EEE", dpi=cdpi)
    paste(img_gtl, bbox_gtl)

    # Paste Gold Pads
    img_pads, bbox_pads = render_transparent(gbl_path, False, "#FBBF24FF", dpi=cdpi)
    paste(img_pads, bbox_pads)

    # Paste Top Silk
    img_gto, bbox_gto = render_transparent(gto_path, False, "#FFFFFFFF", dpi=cdpi)
    paste(img_gto, bbox_gto)

    # Paste Bottom Silk (cyan dim)
    img_gbo, bbox_gbo = render_transparent(gbo_path, False, "#67E8F999", dpi=cdpi)
    paste(img_gbo, bbox_gbo)

    # Paste Drill cutouts
    img_drl, bbox_drl = render_transparent(drl_code, True, "#0F172AFF", dpi=cdpi)
    paste(img_drl, bbox_drl)

    # Paste Outline
    img_gko, bbox_gko = render_transparent(gko_path, False, "#FACC15FF", dpi=cdpi)
    paste(img_gko, bbox_gko)

    comp_out = os.path.join(RENDERED_LAYERS_DIR, "composite_v2_xray.png")
    comp.save(comp_out)
    print(f"[OK] Generated composite X-Ray: {comp_out} ({os.path.getsize(comp_out)} bytes)")

if __name__ == "__main__":
    render_all()
