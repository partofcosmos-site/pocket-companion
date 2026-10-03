import asyncio
import json
import websockets

async def check():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const buttons = Array.from(document.querySelectorAll('button, a')).map(b => b.innerText.trim()).filter(Boolean);
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, [class*="status"], [class*="badge"]')).map(h => h.innerText.trim()).filter(Boolean);
                    const text = document.body.innerText;
                    return {
                        url: window.location.href,
                        title: document.title,
                        headings: headings.slice(0, 20),
                        buttons: buttons.slice(0, 30),
                        hasUnsubmit: text.includes('UNSUBMIT') || text.includes('Unsubmit'),
                        hasSubmitted: text.includes('SUBMITTED') || text.includes('Submitted'),
                        hasInReview: text.includes('IN REVIEW') || text.includes('In Review')
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
    asyncio.run(check())
