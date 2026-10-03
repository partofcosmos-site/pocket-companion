import asyncio
import json
import websockets

async def dump_dialog_elements():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const dialog = document.querySelector('[role="dialog"]');
                    if (!dialog) return 'No dialog';

                    // Collect all child elements with classes, tag, innerText snippet
                    const list = [];
                    dialog.querySelectorAll('*').forEach(el => {
                        if (el.children.length === 0 || el.tagName === 'BUTTON' || el.tagName === 'INPUT' || el.tagName === 'IMG') {
                            list.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.innerText ? el.innerText.trim().slice(0, 50) : '',
                                aria: el.getAttribute('aria-label'),
                                title: el.getAttribute('title'),
                                src: el.getAttribute('src')
                            });
                        }
                    });
                    return list;
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', [])
        for item in val:
            if any([item.get('text'), item.get('aria'), item.get('title'), item.get('src')]):
                print(item)

if __name__ == '__main__':
    asyncio.run(dump_dialog_elements())
