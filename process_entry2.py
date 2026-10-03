import asyncio
import json
import websockets

async def process_entry2():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Step 1: Click "Entry 2" button
        click_cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Entry 2');
                    if (!btn) return 'Entry 2 button not found';
                    btn.click();
                    return 'Clicked Entry 2';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(click_cmd))
        print("Click Entry 2:", await ws.recv())

        await asyncio.sleep(1.5)

        # Step 2: Clear old images from textarea
        clean_cmd = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const ta = document.querySelector('textarea');
                    if (!ta) return 'no textarea';
                    const oldVal = ta.value;
                    const cleaned = oldVal.replace(/!\\[[^\\]]*\\]\\([^)]+\\)\\n*/g, '').trim();
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                    setter.call(ta, cleaned);
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'Textarea cleaned: ' + ta.value.slice(0, 60);
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(clean_cmd))
        print("Clean response:", await ws.recv())

        await asyncio.sleep(1)

        # Step 3: Find file input objectId
        input_cmd = {
            'id': 3,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': "document.querySelector('input[type=\"file\"][multiple]')",
                'returnByValue': False
            }
        }
        await ws.send(json.dumps(input_cmd))
        res3 = json.loads(await ws.recv())
        obj_id = res3.get("result", {}).get("result", {}).get("objectId")
        print("File input objectId:", obj_id)
        if not obj_id:
            print("Failed to get file input objectId")
            return

        # Step 4: Set files
        files = [
            r"C:\Users\white\pocket-companion\assets\journal_media\05_easyeda_schematic_capture.png",
            r"C:\Users\white\pocket-companion\assets\journal_media\06_easyeda_erc_report.png",
            r"C:\Users\white\pocket-companion\assets\journal_media\07_easyeda_pcb_2d_layout.png",
            r"C:\Users\white\pocket-companion\assets\journal_media\08_pcb_3d_render_isometric.png"
        ]
        upload_cmd = {
            'id': 4,
            'method': 'DOM.setFileInputFiles',
            'params': {
                'files': files,
                'objectId': obj_id
            }
        }
        await ws.send(json.dumps(upload_cmd))
        print("setFileInputFiles:", await ws.recv())

        # Step 5: Dispatch input and change
        trigger_cmd = {
            'id': 5,
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
        print("Trigger response:", await ws.recv())

        # Step 6: Wait for upload to complete
        new_img_urls = []
        for sec in range(1, 20):
            await asyncio.sleep(1)
            poll_cmd = {
                'id': 20 + sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const ta = document.querySelector('textarea');
                        if (!ta) return { count: 0, imgs: [] };
                        const matches = ta.value.match(/!\\[[^\\]]*\\]\\([^)]+\\)/g) || [];
                        return { count: matches.length, imgs: matches };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(poll_cmd))
            poll_res = json.loads(await ws.recv())
            val = poll_res.get("result", {}).get("result", {}).get("value", {})
            print(f"[{sec}s] upload state: {val.get('count')} images found")
            if val.get('count') >= 4:
                new_img_urls = val.get('imgs')
                print(f"Upload complete! Got {len(new_img_urls)} images.")
                break

        if len(new_img_urls) < 4:
            print("Upload did not finish in time!")
            return

        # Step 7: Clean textarea and set exactly the 4 new images + body
        clean_final_script = f"""(() => {{
            const ta = document.querySelector('textarea');
            const newImages = {json.dumps(new_img_urls[-4:])};
            const bodyOnly = ta.value.replace(/!\\[[^\\]]*\\]\\([^)]+\\)\\n*/g, '').trim();
            const finalVal = newImages.join('\\n\\n') + '\\n\\n' + bodyOnly;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            setter.call(ta, finalVal);
            ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return {{
                valLen: ta.value.length,
                imgLines: newImages.length
            }};
        }})()"""

        cmd_format = {'id': 50, 'method': 'Runtime.evaluate', 'params': {'expression': clean_final_script, 'returnByValue': True}}
        await ws.send(json.dumps(cmd_format))
        print("Final formatting:", await ws.recv())

        await asyncio.sleep(1)

        # Step 8: Click SAVE CHANGES
        save_cmd = {
            'id': 51,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SAVE CHANGES'));
                    if (!saveBtn) return 'Save button not found';
                    if (saveBtn.disabled) return 'Save button disabled';
                    saveBtn.click();
                    return 'Clicked SAVE CHANGES';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(save_cmd))
        print("Save button clicked:", await ws.recv())

        # Step 9: Verify dialog closes
        for i in range(1, 8):
            await asyncio.sleep(1)
            poll_dialog = {
                'id': 60 + i,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': "!!document.querySelector('[role=\"dialog\"]')",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(poll_dialog))
            d_res = json.loads(await ws.recv())
            open_state = d_res.get('result', {}).get('result', {}).get('value')
            print(f"[{i}s] Dialog open: {open_state}")
            if not open_state:
                print("Modal closed! Entry 2 successfully updated and saved.")
                break

if __name__ == '__main__':
    asyncio.run(process_entry2())
