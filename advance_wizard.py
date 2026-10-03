import asyncio
import json
import websockets

async def advance_wizard():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Click NEXT
        click_cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                    if (!btn) return 'NEXT button not found';
                    btn.click();
                    return 'Clicked NEXT';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(click_cmd))
        print("Click result:", await ws.recv())

        await asyncio.sleep(1.5)

        # Inspect current screen
        inspect_cmd = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const modal = document.querySelector('[role="dialog"]') || document.body;
                    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                        text: b.innerText.trim(),
                        disabled: b.disabled
                    })).filter(b => b.text);
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, [class*="step"]')).map(h => h.innerText.trim());
                    const text = modal.innerText.slice(0, 500);
                    return {
                        headings: headings.slice(0, 10),
                        buttons: buttons.slice(-10),
                        textSnippet: text
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(inspect_cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(json.dumps(val, indent=2))

if __name__ == '__main__':
    asyncio.run(advance_wizard())
