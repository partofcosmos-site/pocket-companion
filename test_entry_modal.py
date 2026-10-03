import asyncio
import json
import websockets

async def test_click_entry1():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Click "Entry 1" button
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Entry 1');
                    if (!btn) return 'Entry 1 button not found';
                    btn.click();
                    return 'Clicked Entry 1';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        print("Click result:", (await ws.recv()))

        await asyncio.sleep(1)

        # Inspect open modals, forms, inputs, file inputs, images, remove buttons
        inspect_cmd = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
                        id: i.id,
                        name: i.name,
                        multiple: i.multiple,
                        accept: i.accept
                    }));
                    const modal = Array.from(document.querySelectorAll('[role="dialog"], form, [class*="modal"]')).map(m => ({
                        tag: m.tagName,
                        role: m.getAttribute('role'),
                        text: m.innerText.slice(0, 300)
                    }));
                    const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
                    const images = Array.from(document.querySelectorAll('img')).map(i => ({
                        src: i.src,
                        alt: i.alt
                    }));
                    return { fileInputs, modal, buttons: buttons.slice(-20), imagesCount: images.length };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(inspect_cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(json.dumps(val, indent=2))

if __name__ == '__main__':
    asyncio.run(test_click_entry1())
