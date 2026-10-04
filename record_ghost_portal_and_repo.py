import asyncio
import base64
import json
import os
import subprocess
import time
import urllib.request
import websockets

CDP_JSON_URL = 'http://127.0.0.1:9100/json'
FRAME_DIR = r'C:\Users\white\pocket-companion\assets\ghost_frames'
OUTPUT_VIDEO = r'C:\Users\white\pocket-companion\assets\ghost_recording_portal_and_repo.mp4'
FFMPEG = r'C:\Users\white\.local\bin\ffmpeg.exe'

os.makedirs(FRAME_DIR, exist_ok=True)

# Clean up existing frames
for f in os.listdir(FRAME_DIR):
    if f.endswith('.png'):
        try:
            os.remove(os.path.join(FRAME_DIR, f))
        except Exception:
            pass

def get_tab(url_keyword):
    with urllib.request.urlopen(CDP_JSON_URL, timeout=5) as resp:
        tabs = json.loads(resp.read().decode())
    for t in tabs:
        if url_keyword in t.get('url', ''):
            return t
    return None

async def capture_frame(ws, frame_idx):
    msg = {'id': 1000 + frame_idx, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}
    await ws.send(json.dumps(msg))
    res = json.loads(await ws.recv())
    data = res.get('result', {}).get('data')
    if data:
        path = os.path.join(FRAME_DIR, f"frame_{frame_idx:05d}.png")
        with open(path, 'wb') as f:
            f.write(base64.b64decode(data))
        return True
    return False

async def record_portal_and_repo():
    print("=== GHOST MODE RECORDING INITIATED ===")
    frame_counter = 0

    # 1. Locate Half-Life Tab
    tab = get_tab('cmuqw217z02uz01rlatu9wyrg')
    if not tab:
        tab = get_tab('halflife')
    if not tab:
        raise RuntimeError("Half-Life tab not found in BrowserOS!")

    ws_url = tab['webSocketDebuggerUrl']
    print(f"Connecting to Half-Life tab: {tab['url']}")

    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        # Set viewport to 1920x1080 without changing OS window focus
        await ws.send(json.dumps({
            'id': 1,
            'method': 'Emulation.setDeviceMetricsOverride',
            'params': {'width': 1920, 'height': 1080, 'deviceScaleFactor': 1, 'mobile': False}
        }))
        await ws.recv()

        # Scroll to top first
        await ws.send(json.dumps({
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {'expression': 'window.scrollTo(0, 0);'}
        }))
        await ws.recv()
        await asyncio.sleep(0.5)

        # Get total scroll height
        await ws.send(json.dumps({
            'id': 3,
            'method': 'Runtime.evaluate',
            'params': {'expression': 'document.body.scrollHeight', 'returnByValue': True}
        }))
        res = json.loads(await ws.recv())
        total_height = res.get('result', {}).get('result', {}).get('value', 4000)
        print(f"Half-Life Page Total Height: {total_height}px")

        # Smooth scroll downwards over ~80 steps to show header, repo checks, entries 1, 2, 3
        step_px = 65
        current_y = 0
        while current_y < total_height:
            await ws.send(json.dumps({
                'id': 10,
                'method': 'Runtime.evaluate',
                'params': {'expression': f'window.scrollTo({{ top: {current_y}, behavior: "instant" }});'}
            }))
            await ws.recv()
            await asyncio.sleep(0.08)
            await capture_frame(ws, frame_counter)
            frame_counter += 1
            current_y += step_px

        # Hold at bottom for 15 frames
        for _ in range(15):
            await capture_frame(ws, frame_counter)
            frame_counter += 1
            await asyncio.sleep(0.05)

        # Smooth scroll back up to the entries section
        while current_y > 800:
            current_y -= 120
            await ws.send(json.dumps({
                'id': 11,
                'method': 'Runtime.evaluate',
                'params': {'expression': f'window.scrollTo({{ top: {current_y}, behavior: "instant" }});'}
            }))
            await ws.recv()
            await asyncio.sleep(0.06)
            await capture_frame(ws, frame_counter)
            frame_counter += 1

        # Pause on entries for 20 frames
        for _ in range(20):
            await capture_frame(ws, frame_counter)
            frame_counter += 1
            await asyncio.sleep(0.05)

    print(f"Captured {frame_counter} frames on Half-Life portal.")

    # 2. Open / Navigate to GitHub repo in a background tab
    print("Navigating to GitHub repository page in background...")
    create_tab_req = urllib.request.urlopen('http://127.0.0.1:9100/json/new?https://github.com/partofcosmos-site/pocket-companion')
    repo_tab = json.loads(create_tab_req.read().decode())
    repo_ws_url = repo_tab['webSocketDebuggerUrl']
    repo_id = repo_tab['id']

    try:
        async with websockets.connect(repo_ws_url, max_size=50*1024*1024) as ws_repo:
            # Set viewport
            await ws_repo.send(json.dumps({
                'id': 1,
                'method': 'Emulation.setDeviceMetricsOverride',
                'params': {'width': 1920, 'height': 1080, 'deviceScaleFactor': 1, 'mobile': False}
            }))
            await ws_repo.recv()
            # Wait for page to load
            await asyncio.sleep(3.0)

            # Get height of GitHub repo page
            await ws_repo.send(json.dumps({
                'id': 2,
                'method': 'Runtime.evaluate',
                'params': {'expression': 'document.body.scrollHeight', 'returnByValue': True}
            }))
            res = json.loads(await ws_repo.recv())
            repo_height = res.get('result', {}).get('result', {}).get('value', 3500)
            print(f"GitHub Repo Page Total Height: {repo_height}px")

            # Hold at top for 20 frames
            for _ in range(20):
                await capture_frame(ws_repo, frame_counter)
                frame_counter += 1
                await asyncio.sleep(0.05)

            # Scroll down through README
            curr_y = 0
            while curr_y < repo_height:
                await ws_repo.send(json.dumps({
                    'id': 10,
                    'method': 'Runtime.evaluate',
                    'params': {'expression': f'window.scrollTo({{ top: {curr_y}, behavior: "instant" }});'}
                }))
                await ws_repo.recv()
                await asyncio.sleep(0.08)
                await capture_frame(ws_repo, frame_counter)
                frame_counter += 1
                curr_y += 75

            # Hold at bottom of repo
            for _ in range(20):
                await capture_frame(ws_repo, frame_counter)
                frame_counter += 1
                await asyncio.sleep(0.05)

    finally:
        # Close the temporary background tab via CDP
        try:
            close_url = f"http://127.0.0.1:9100/json/close/{repo_id}"
            urllib.request.urlopen(close_url)
            print("Closed background GitHub tab cleanly.")
        except Exception as e:
            print("Note closing tab:", e)

    print(f"Total frames recorded: {frame_counter}")

    # Compile with FFMPEG
    print(f"Encoding video with ffmpeg to {OUTPUT_VIDEO}...")
    cmd = [
        FFMPEG,
        '-y',
        '-framerate', '24',
        '-i', os.path.join(FRAME_DIR, 'frame_%05d.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '20',
        '-preset', 'fast',
        OUTPUT_VIDEO
    ]
    subprocess.check_call(cmd)
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"Video encoded successfully! File size: {file_size_mb:.2f} MB")

if __name__ == '__main__':
    asyncio.run(record_portal_and_repo())
