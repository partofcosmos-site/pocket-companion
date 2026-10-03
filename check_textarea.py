import asyncio
import json
import websockets

async def check_textarea():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const ta = document.querySelector('textarea');
                    const fileInput = document.querySelector('input[type="file"][multiple]');
                    const addBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('ADD IMAGES'));
                    return {
                        textareaValue: ta ? ta.value : null,
                        addBtnDisabled: addBtn ? addBtn.disabled : null,
                        fileInputExists: !!fileInput
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(json.dumps(val, indent=2))

if __name__ == '__main__':
    asyncio.run(check_textarea())
