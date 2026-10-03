import asyncio
import json
import websockets

async def inspect_portal_entries():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const articles = Array.from(document.querySelectorAll('article, [class*="journal"], div')).filter(el => {
                        const t = el.innerText || '';
                        return t.includes('Hardware Blueprint') || t.includes('Bench Prototyping') || t.includes('EasyEDA Schematic') || t.includes('PCB Routing');
                    });
                    
                    const imgs = Array.from(document.querySelectorAll('img')).map(i => ({
                        src: i.src,
                        alt: i.alt
                    })).filter(i => i.src.includes('hackclub-assets'));

                    return {
                        articleCount: articles.length,
                        imgCount: imgs.length,
                        images: imgs
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
    asyncio.run(inspect_portal_entries())
