import asyncio
import json
import websockets

async def check_dialog_state():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SAVE CHANGES'));
                    const ta = document.querySelector('textarea');
                    const hoursInput = document.querySelector('input[inputmode="decimal"], input[type="text"]');
                    const charCount = document.body.innerText.match(/\\d+\\s*\\/\\s*\\d+\\s*characters/);
                    const imgCount = document.body.innerText.match(/\\d+\\s*\\/\\s*\\d+\\s*images/);
                    const errorMsgs = Array.from(document.querySelectorAll('.error, [role="alert"], .text-red-500, p')).filter(p => p.innerText.includes('error') || p.innerText.includes('Error') || p.innerText.includes('minimum') || p.innerText.includes('least')).map(p => p.innerText);

                    return {
                        saveBtnDisabled: saveBtn ? saveBtn.disabled : null,
                        hoursValue: hoursInput ? hoursInput.value : null,
                        charCount: charCount ? charCount[0] : null,
                        imgCount: imgCount ? imgCount[0] : null,
                        textareaLength: ta ? ta.value.length : 0,
                        textareaValueSnippet: ta ? ta.value.slice(0, 100) : null,
                        errorMsgs: errorMsgs.slice(0, 5)
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
    asyncio.run(check_dialog_state())
