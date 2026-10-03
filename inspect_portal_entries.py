import asyncio
import json
import websockets

async def inspect():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        for entry_name in ['Entry 1', 'Entry 2', 'Entry 3']:
            # click entry button
            await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': f'''(() => {{
                const btn = Array.from(document.querySelectorAll("button")).find(b => b.innerText.trim() === "{entry_name}");
                if (btn) {{ btn.click(); return 'clicked'; }}
                return 'not found';
            }})()''', 'returnByValue': True}}))
            await ws.recv()
            await asyncio.sleep(1)

            # read textarea
            await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': '''(() => {
                const ta = document.querySelector("textarea");
                return {
                    val: ta ? ta.value : null,
                    images: ta ? (ta.value.match(/!\\[[^\\]]*\\]\\([^)]+\\)/g) || []) : []
                };
            })()''', 'returnByValue': True}}))
            res = json.loads(await ws.recv())
            val = res.get('result', {}).get('result', {}).get('value', {})
            print(f'=== {entry_name} ===')
            print('Images count:', len(val.get('images', [])))
            print('Images:', val.get('images'))
            print('Text sample:', (val.get('val') or '')[:300])
            print('Full text len:', len(val.get('val') or ''))

            # close modal by clicking CANCEL or close button
            await ws.send(json.dumps({'id': 3, 'method': 'Runtime.evaluate', 'params': {'expression': '''(() => {
                const btn = Array.from(document.querySelectorAll("button")).find(b => b.innerText.includes("CANCEL") || b.innerText.includes("Close"));
                if (btn) btn.click();
            })()''', 'returnByValue': True}}))
            await ws.recv()
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(inspect())
