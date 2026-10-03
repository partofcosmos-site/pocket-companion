import asyncio
import json
import websockets

async def check_step2_inputs():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const inputs = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
                        accept: i.accept,
                        multiple: i.multiple,
                        outerHTML: i.outerHTML
                    }));
                    const tierBtns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Tier 1')).map(b => ({
                        text: b.innerText,
                        ariaPressed: b.getAttribute('aria-pressed'),
                        className: b.className
                    }));
                    const selectFileBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SELECT FILES'));
                    return { inputs, tierBtns, hasSelectBtn: !!selectFileBtn };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(json.dumps(val, indent=2))

if __name__ == '__main__':
    asyncio.run(check_step2_inputs())
