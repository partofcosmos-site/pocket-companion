import asyncio
import os
import subprocess
import time
from playwright.async_api import async_playwright

FRAMES_DIR = r'C:\Users\white\pocket-companion\assets\walkthrough_frames'
OUTPUT_VIDEO = r'C:\Users\white\pocket-companion\assets\portal_and_repo_ghost_walkthrough.mp4'
FFMPEG = r'C:\Users\white\.local\bin\ffmpeg.exe'

os.makedirs(FRAMES_DIR, exist_ok=True)

async def capture_walkthrough():
    print("=== CONNECTING TO BROWSEROS CDP FOR GHOST CAPTURE ===")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9100')
        context = browser.contexts[0]
        
        # 1. Capture Half-Life Portal Page
        hl_page = None
        for pg in context.pages:
            if 'cmuqw217z02uz01rlatu9wyrg' in pg.url or 'halflife' in pg.url:
                hl_page = pg
                break
                
        if not hl_page:
            raise RuntimeError("Half-Life portal page not found!")
            
        print(f"Located Half-Life Portal: {hl_page.url}")
        await hl_page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Scroll to top
        await hl_page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1.0)
        
        # Positions to capture on Half-Life portal
        scroll_targets_hl = [
            ("hl_01_header_status", 0),
            ("hl_02_review_badges", 350),
            ("hl_03_repo_checks_passed", 700),
            ("hl_04_hackatime_sync", 1100),
            ("hl_05_bom_materials", 1600),
            ("hl_06_entry1_proto", 2100),
            ("hl_07_entry1_breadboard_charts", 2700),
            ("hl_08_entry2_schematic_capture", 3400),
            ("hl_09_entry2_pcb_3d_render", 4100),
            ("hl_10_entry3_drc_validation", 4800),
            ("hl_11_entry3_firmware_fsm_scope", 5500),
            ("hl_12_video_reel_footer", 6200)
        ]
        
        captured_files = []
        for name, scroll_y in scroll_targets_hl:
            shot_path = os.path.join(FRAMES_DIR, f"{name}.png")
            if not os.path.exists(shot_path):
                await hl_page.evaluate(f"window.scrollTo({{ top: {scroll_y}, behavior: 'smooth' }})")
                await asyncio.sleep(1.0)
                await hl_page.screenshot(path=shot_path, full_page=False)
                print(f"Captured: {name} (Y={scroll_y})")
            else:
                print(f"Using cached: {name}")
            captured_files.append(shot_path)
            
        # 2. Capture GitHub Repo
        print("\n=== OPENING GITHUB REPO IN BACKGROUND GHOST TAB ===")
        repo_page = await context.new_page()
        try:
            await repo_page.set_viewport_size({"width": 1920, "height": 1080})
            await repo_page.goto("https://github.com/partofcosmos-site/pocket-companion", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1.5)
            
            scroll_targets_repo = [
                ("repo_01_overview_files", 0),
                ("repo_02_readme_header", 450),
                ("repo_03_hardware_architecture", 1000),
                ("repo_04_power_budget_schematic", 1600),
                ("repo_05_gerber_drc_specs", 2300),
                ("repo_06_cad_exploded_assembly", 3000),
                ("repo_07_firmware_benchmarks", 3700),
                ("repo_08_verification_table", 4400)
            ]
            
            for name, scroll_y in scroll_targets_repo:
                await repo_page.evaluate(f"window.scrollTo({{ top: {scroll_y}, behavior: 'smooth' }})")
                await asyncio.sleep(0.8)
                shot_path = os.path.join(FRAMES_DIR, f"{name}.png")
                await repo_page.screenshot(path=shot_path, full_page=False)
                captured_files.append(shot_path)
                print(f"Captured: {name} (Y={scroll_y})")
        finally:
            await repo_page.close()
            print("Closed temporary GitHub repo tab.")
        
        # 3. Create smooth video from captured slide frames using FFmpeg
        print(f"\nTotal key frames captured: {len(captured_files)}")
        print("Generating smooth presentation video with FFmpeg...")
        
        # Concat demuxer file (2.5 seconds per frame)
        concat_list_path = os.path.join(FRAMES_DIR, "slides.txt")
        with open(concat_list_path, 'w', encoding='utf-8') as f:
            for shot in captured_files:
                f.write(f"file '{shot.replace(os.sep, '/')}'\n")
                f.write("duration 2.5\n")
            f.write(f"file '{captured_files[-1].replace(os.sep, '/')}'\n")
            
        cmd = [
            FFMPEG,
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_path,
            '-vf', 'fps=30,format=yuv420p,scale=1920:1080',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            OUTPUT_VIDEO
        ]
        
        subprocess.check_call(cmd)
        video_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
        print(f"\n[SUCCESS] Ghost Mode walkthrough video generated at:")
        print(f"  {OUTPUT_VIDEO}")
        print(f"  Size: {video_size_mb:.2f} MB | Resolution: 1920x1080 | Duration: {len(captured_files)*2.5:.1f}s")

if __name__ == '__main__':
    asyncio.run(capture_walkthrough())
