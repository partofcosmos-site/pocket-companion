import asyncio
import json
import websockets

async def inspect_images_ui():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const dialog = document.querySelector('[role="dialog"]');
                    if (!dialog) return 'No dialog';
                    
                    // Find node containing 'images'
                    const walker = document.createTreeWalker(dialog, NodeFilter.SHOW_TEXT);
                    let node;
                    const results = [];
                    while (node = walker.nextNode()) {
                        if (node.nodeValue.includes('image') || node.nodeValue.includes('Image') || node.nodeValue.includes('4 / 4')) {
                            results.push({
                                text: node.nodeValue.trim(),
                                parent: node.parentElement.outerHTML.slice(0, 300)
                            });
                        }
                    }

                    // Look for image containers, remove icons, delete buttons, thumbnails
                    const allImgsOrSVGs = Array.from(dialog.querySelectorAll('ul, ol, div')).filter(d => {
                        return d.querySelector('img') || d.innerText.includes('image');
                    }).map(d => ({
                        tag: d.tagName,
                        className: d.className,
                        html: d.innerHTML.slice(0, 400)
                    }));

                    return { results, allImgsOrSVGs: allImgsOrSVGs.slice(0, 5) };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(json.dumps(val, indent=2))

if __name__ == '__main__':
    asyncio.run(inspect_images_ui())
