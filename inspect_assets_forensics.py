import os
import sys
import numpy as np
from PIL import Image

ASSETS_DIR = r"C:\Users\white\pocket-companion\assets"
JOURNAL_MEDIA_DIR = r"C:\Users\white\pocket-companion\assets\journal_media"

FILES = [
    "01_system_architecture_block_diagram.png",
    "02_rp2040_pinout_peripheral_matrix.png",
    "03_power_budget_battery_discharge_curve.png",
    "04_breadboard_prototype_wiring.png",
    "05_easyeda_schematic_capture.png",
    "06_easyeda_erc_report.png",
    "07_easyeda_pcb_2d_layout.png",
    "08_pcb_3d_render_isometric.png",
    "09_jlcpcb_drc_validation_pass.png",
    "10_gerber_manufacturing_stackup_preview.png",
    "11_circuitpython_firmware_state_machine.png",
    "12_reaction_game_timing_oscilloscope.png"
]

def analyze_image(path):
    issues = []
    if not os.path.exists(path):
        return {"status": "MISSING", "issues": ["File does not exist"]}

    img = Image.open(path)
    w, h = img.size
    mode = img.mode
    dpi = img.info.get("dpi", (72, 72))
    filesize = os.path.getsize(path)

    # Convert to RGB numpy array
    rgb_img = img.convert("RGB")
    arr = np.array(rgb_img)

    # Resolution check (min 1200x800 for high quality EDA/diagrams)
    if w < 1000 or h < 600:
        issues.append(f"Low resolution: {w}x{h}")

    # Check for empty / monochromatic images
    std_per_channel = np.std(arr, axis=(0, 1))
    if np.all(std_per_channel < 5.0):
        issues.append(f"Near uniform / blank image: std={std_per_channel}")

    # Check for unnatural color clipping or saturation extremes
    mean_val = np.mean(arr)
    if mean_val < 5:
        issues.append("Image is almost entirely black")
    elif mean_val > 250:
        issues.append("Image is almost entirely white")

    # Check aspect ratio
    aspect = w / h

    # Check color histogram / gradient smoothness (detect posterization or extreme banding)
    # Check edges sharpness: laplacian-like variance
    gray = np.mean(arr, axis=2)
    # Simple laplacian kernel
    kernel_h = gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:] - 4 * gray[1:-1, 1:-1]
    sharpness = np.var(kernel_h)

    return {
        "status": "PASS" if len(issues) == 0 else "FAIL",
        "size": (w, h),
        "aspect_ratio": round(aspect, 3),
        "mode": mode,
        "dpi": dpi,
        "filesize_bytes": filesize,
        "sharpness": round(float(sharpness), 2),
        "mean_intensity": round(float(mean_val), 2),
        "std_intensity": [round(float(s), 2) for s in std_per_channel],
        "issues": issues
    }

def run_inspection():
    print("=" * 80)
    print("VISION FORENSIC QUALITY INSPECTOR - ASSET SCAN")
    print("=" * 80)
    
    total_defects = 0
    results = {}

    for fname in FILES:
        p_asset = os.path.join(ASSETS_DIR, fname)
        res = analyze_image(p_asset)
        results[fname] = res
        status = res["status"]
        if status != "PASS":
            total_defects += 1
        print(f"[{status}] {fname}: size={res.get('size')} dpi={res.get('dpi')} sharp={res.get('sharpness')} issues={res.get('issues')}")

    print("-" * 80)
    print(f"Total defects found: {total_defects}")
    return total_defects, results

if __name__ == "__main__":
    defects, _ = run_inspection()
    sys.exit(defects)
