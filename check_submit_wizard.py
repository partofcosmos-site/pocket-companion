import asyncio
import json
import websockets

async def check_submit_wizard():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Click "SUBMIT YOUR DESIGN"
        click_cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'SUBMIT YOUR DESIGN');
                    if (!btn) return 'Button not found';
                    btn.click();
                    return 'Clicked SUBMIT YOUR DESIGN';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(click_cmd))
        print("Click result:", await ws.recv())

        await asyncio.sleep(1.5)

        # Inspect open modal / wizard
        inspect_cmd = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const dialog = document.querySelector('[role="dialog"]') || document.querySelector('form') || document.body;
                    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                        text: b.innerText.trim(),
                        disabled: b.disabled
                    })).filter(b => b.text);
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5')).map(h => h.innerText.trim());
                    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
                        accept: i.accept,
                        multiple: i.multiple
                    }));
                    return {
                        headings: headings.slice(0, 10),
                        buttons: buttons.slice(-15),
                        fileInputs
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
    asyncio.run(check_submit_wizard())
