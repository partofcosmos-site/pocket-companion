import asyncio
import json
import websockets

async def check_current():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const ta = document.querySelector('textarea');
                    return ta ? ta.value : 'No textarea';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value')
        print("Current open textarea content:")
        print(val)

        # Close dialog
        cmd_close = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = document.querySelector('button[aria-label="Close"]');
                    if (btn) { btn.click(); return 'Closed'; }
                    return 'Not found';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd_close))
        res_c = json.loads(await ws.recv())
        print("Close result:", res_c.get('result', {}).get('result', {}).get('value'))

if __name__ == '__main__':
    asyncio.run(check_current())
