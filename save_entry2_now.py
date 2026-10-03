import asyncio
import json
import websockets

async def click_save():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SAVE CHANGES'));
                    if (!saveBtn) return 'Button not found';
                    if (saveBtn.disabled) return 'Button is disabled';
                    saveBtn.click();
                    return 'Clicked SAVE CHANGES';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        print(await ws.recv())

        await asyncio.sleep(2)
        cmd2 = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': "!!document.querySelector('[role=\"dialog\"]')",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd2))
        res2 = json.loads(await ws.recv())
        print("Dialog open:", res2.get('result', {}).get('result', {}).get('value'))

if __name__ == '__main__':
    asyncio.run(click_save())
