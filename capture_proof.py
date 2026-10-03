import asyncio
import json
import base64
import websockets

async def capture_proof():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Page.captureScreenshot',
            'params': {'format': 'png'}
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        img_b64 = res.get('result', {}).get('data')
        if img_b64:
            out_img = r"C:\Users\white\pocket-companion\assets\submission_confirmed_final.png"
            with open(out_img, 'wb') as f:
                f.write(base64.b64decode(img_b64))
            print(f"Captured screenshot to: {out_img}")

if __name__ == '__main__':
    asyncio.run(capture_proof())
