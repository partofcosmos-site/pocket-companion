import asyncio
import json
import websockets

async def inspect_entry_elements():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    // Find all journal entry cards or containers
                    const allCards = Array.from(document.querySelectorAll('*')).filter(el => {
                        return el.children.length > 0 && Array.from(el.children).some(c => c.innerText && c.innerText.includes('Journal entry'));
                    });

                    // Check clickable elements inside timeline
                    const timeline = Array.from(document.querySelectorAll('button, svg, [role="button"]')).map(b => ({
                        tag: b.tagName,
                        text: b.innerText ? b.innerText.trim() : '',
                        title: b.getAttribute('title') || '',
                        aria: b.getAttribute('aria-label') || '',
                        parentText: b.parentElement ? b.parentElement.innerText.slice(0, 50) : ''
                    })).filter(b => b.text || b.title || b.aria);

                    return {
                        timelineButtons: timeline.filter(b => 
                            b.text.includes('Edit') || b.text.includes('edit') || 
                            b.title.includes('Edit') || b.title.includes('edit') ||
                            b.aria.includes('Edit') || b.aria.includes('edit') ||
                            b.text.includes('Entry')
                        )
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
    asyncio.run(inspect_entry_elements())
