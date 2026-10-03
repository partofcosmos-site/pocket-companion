import asyncio
import json
import websockets

async def inspect_all():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # First ensure any open dialog is closed
        cmd_close = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = document.querySelector('button[aria-label="Close"]');
                    if (btn) { btn.click(); return true; }
                    return false;
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd_close))
        await ws.recv()
        await asyncio.sleep(1)

        entries_data = {}

        for entry_name in ['Entry 1', 'Entry 2', 'Entry 3']:
            # Open entry
            cmd_open = {
                'id': 10,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': f"""(() => {{
                        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === '{entry_name}');
                        if (btn) {{ btn.click(); return true; }}
                        return false;
                    }})()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_open))
            await ws.recv()
            await asyncio.sleep(1.5)

            # Read textarea and hours
            cmd_read = {
                'id': 11,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const ta = document.querySelector('textarea');
                        const hours = document.querySelector('input[inputmode="decimal"], input[aria-label*="Hours"]');
                        const title = document.querySelector('[role="dialog"] h2')?.innerText;
                        const header = document.querySelector('[role="dialog"] span.label')?.innerText;
                        return {
                            header: header,
                            title: title,
                            hours: hours ? hours.value : '',
                            val: ta ? ta.value : '',
                            images: ta ? (ta.value.match(/!\\[[^\\]]*\\]\\([^)]+\\)/g) || []) : []
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_read))
            res = json.loads(await ws.recv())
            data = res.get('result', {}).get('result', {}).get('value', {})
            entries_data[entry_name] = data

            # Close dialog
            await ws.send(json.dumps(cmd_close))
            await ws.recv()
            await asyncio.sleep(1)

        with open('portal_entries_dump.json', 'w', encoding='utf-8') as f:
            json.dump(entries_data, f, indent=2, ensure_ascii=False)
        print("Successfully dumped all entries to portal_entries_dump.json")

if __name__ == '__main__':
    asyncio.run(inspect_all())
