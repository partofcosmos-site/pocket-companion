import asyncio
import json
import websockets

async def inspect():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': 'document.querySelector("textarea").value',
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', '')
        lines = val.split('\n')
        for i, l in enumerate(lines):
            if '![' in l:
                print(f'{i}: {l}')

if __name__ == '__main__':
    asyncio.run(inspect())
