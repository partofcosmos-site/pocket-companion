import asyncio
import json
import websockets

async def check_next_btn():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        for sec in range(1, 10):
            await asyncio.sleep(1)
            cmd = {
                'id': sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                        const images = Array.from(document.querySelectorAll('img')).map(i => i.src);
                        return {
                            nextFound: !!nextBtn,
                            nextDisabled: nextBtn ? nextBtn.disabled : null,
                            imgCount: images.length
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd))
            res = json.loads(await ws.recv())
            val = res.get('result', {}).get('result', {}).get('value', {})
            print(f"[{sec}s] Next button state:", val)
            if val.get('nextFound') and not val.get('nextDisabled'):
                print("NEXT button is enabled!")
                break

if __name__ == '__main__':
    asyncio.run(check_next_btn())
