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
                'expression': """(() => {
                    const text = document.body.innerText;
                    const modal = document.querySelector('[role="dialog"]');
                    const modalText = modal ? modal.innerText : '';
                    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                        text: b.innerText.trim(),
                        disabled: b.disabled
                    })).filter(b => b.text);
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, [class*="step"]')).map(h => h.innerText.trim());
                    return {
                        hasModal: !!modal,
                        modalTextSnippet: modalText.slice(0, 300),
                        buttons: buttons.slice(-10),
                        headings: headings.slice(0, 10),
                        isSubmitted: text.includes('SUBMITTED') || text.includes('Submitted') || text.includes('IN REVIEW') || text.includes('In Review'),
                        hasUnsubmit: text.includes('UNSUBMIT') || text.includes('Unsubmit')
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
    asyncio.run(inspect())
