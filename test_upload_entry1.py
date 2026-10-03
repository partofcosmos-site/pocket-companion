import asyncio
import json
import websockets
import re

async def test_upload_entry1():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Step 1: Remove old image markdown tags from textarea
        remove_cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const ta = document.querySelector('textarea');
                    if (!ta) return 'no textarea';
                    // Strip all ![]() markdown lines
                    const oldVal = ta.value;
                    const cleaned = oldVal.replace(/!\\[[^\\]]*\\]\\([^)]+\\)\\n*/g, '').trim();
                    ta.value = cleaned;
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'Cleaned: ' + ta.value.slice(0, 80);
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(remove_cmd))
        print("Cleaned old images:", await ws.recv())

        await asyncio.sleep(1)

        # Step 2: Find file input objectId
        file_input_cmd = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': "document.querySelector('input[type=\"file\"][multiple]')",
                'returnByValue': False
            }
        }
        await ws.send(json.dumps(file_input_cmd))
        res2 = json.loads(await ws.recv())
        obj_id = res2.get("result", {}).get("result", {}).get("objectId")
        print("File input objectId:", obj_id)

        if not obj_id:
            return

        # Step 3: Set files via DOM.setFileInputFiles
        files = [
            r"C:\Users\white\pocket-companion\assets\journal_media\01_system_architecture_block_diagram.png",
            r"C:\Users\white\pocket-companion\assets\journal_media\02_rp2040_pinout_peripheral_matrix.png",
            r"C:\Users\white\pocket-companion\assets\journal_media\03_power_budget_battery_discharge_curve.png",
            r"C:\Users\white\pocket-companion\assets\journal_media\04_breadboard_prototype_wiring.png"
        ]
        upload_cmd = {
            'id': 3,
            'method': 'DOM.setFileInputFiles',
            'params': {
                'files': files,
                'objectId': obj_id
            }
        }
        await ws.send(json.dumps(upload_cmd))
        print("setFileInputFiles resp:", await ws.recv())

        # Step 4: Dispatch change and input events on file input
        trigger_cmd = {
            'id': 4,
            'method': 'Runtime.callFunctionOn',
            'params': {
                'objectId': obj_id,
                'functionDeclaration': """function() {
                    this.dispatchEvent(new Event('input', { bubbles: true }));
                    this.dispatchEvent(new Event('change', { bubbles: true }));
                }"""
            }
        }
        await ws.send(json.dumps(trigger_cmd))
        print("trigger event resp:", await ws.recv())

        # Step 5: Wait for upload to progress and poll textarea
        for sec in range(1, 15):
            await asyncio.sleep(1)
            poll_cmd = {
                'id': 10 + sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const ta = document.querySelector('textarea');
                        const imgCount = document.body.innerText.match(/(\\d+)\\s*\\/\\s*4\\s*images/);
                        return {
                            valLength: ta ? ta.value.length : 0,
                            imgCountMatch: imgCount ? imgCount[0] : null,
                            first100: ta ? ta.value.slice(0, 150) : null
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(poll_cmd))
            poll_res = json.loads(await ws.recv())
            print(f"[{sec}s] upload state:", poll_res.get("result", {}).get("result", {}).get("value"))

asyncio.run(test_upload_entry1())
