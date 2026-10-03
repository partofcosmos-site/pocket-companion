import asyncio
import json
import websockets

async def inspect_journal():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const timeline = document.querySelector('[class*="timeline"]') || document.body;
                    const items = Array.from(document.querySelectorAll('div, section, article')).filter(el => {
                        const t = el.innerText || '';
                        return t.includes('Journal entry') && (t.includes('Hardware Blueprint') || t.includes('EasyEDA Schematic') || t.includes('PCB Layout'));
                    });
                    
                    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                        text: b.innerText.trim(),
                        className: b.className,
                        ariaLabel: b.getAttribute('aria-label')
                    }));

                    const editButtons = buttons.filter(b => b.text.toLowerCase().includes('edit') || b.text.toLowerCase().includes('entry'));

                    return {
                        entryMatches: items.length,
                        editButtons: editButtons,
                        allButtonsCount: buttons.length
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
    asyncio.run(inspect_journal())
