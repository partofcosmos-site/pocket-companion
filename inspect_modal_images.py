import asyncio
import json
import websockets

async def inspect_modal_images():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const dialog = document.querySelector('[role="dialog"]');
                    if (!dialog) return 'No dialog found';
                    
                    const buttons = Array.from(dialog.querySelectorAll('button')).map(b => ({
                        text: b.innerText.trim(),
                        aria: b.getAttribute('aria-label') || '',
                        title: b.getAttribute('title') || '',
                        className: b.className
                    }));

                    const svgs = Array.from(dialog.querySelectorAll('button svg, [role="button"] svg')).map(s => {
                        const p = s.closest('button') || s.closest('[role="button"]') || s.parentElement;
                        return {
                            parentTag: p.tagName,
                            parentText: p.innerText ? p.innerText.trim() : '',
                            parentAria: p.getAttribute('aria-label') || '',
                            className: s.className.baseVal || ''
                        };
                    });

                    const imgThumbnails = Array.from(dialog.querySelectorAll('img')).map(i => ({
                        src: i.src,
                        parentHTML: i.parentElement.innerHTML.slice(0, 150)
                    }));

                    return { buttons, svgs, imgThumbnails };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(json.dumps(val, indent=2))

if __name__ == '__main__':
    asyncio.run(inspect_modal_images())
