import asyncio
import json
import websockets

async def save_entry1():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Step 1: Clean text to keep ONLY the 4 new images and the journal body
        clean_script = """(() => {
            const ta = document.querySelector('textarea');
            if (!ta) return { error: 'No textarea' };

            const newImages = [
                '![01_system_architecture_block_diagram](https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/71f1e30cb4aaa1d3645ea29fa7da0e0f4d5774497b45c4ee4927fcc0c868b50f.png)',
                '![02_rp2040_pinout_peripheral_matrix](https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/378cd39cac2fd3ea545bb6c8136c01ec41206b467dacadc1b29e9c29417083aa.png)',
                '![03_power_budget_battery_discharge_curve](https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/e187ecc97d25d935846136cca57cd152e7e2bf0f34cf15355a435de18d82b91f.png)',
                '![04_breadboard_prototype_wiring](https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/31ce3a0aad3344d69b94c5da8ff59737bd36d12a0cb56e4f1ae70f1bebac14dd.png)'
            ];

            // Extract body text (remove all image lines)
            const bodyOnly = ta.value.replace(/!\\[[^\\]]*\\]\\([^)]+\\)\\n*/g, '').trim();

            const finalVal = newImages.join('\\n\\n') + '\\n\\n' + bodyOnly;

            // Use React setter to properly trigger react state update
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            nativeInputValueSetter.call(ta, finalVal);

            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));

            return {
                valLen: ta.value.length,
                first200: ta.value.slice(0, 200)
            };
        })()"""

        cmd = {'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': clean_script, 'returnByValue': True}}
        await ws.send(json.dumps(cmd))
        print("Updated textarea:", (await ws.recv()))

        await asyncio.sleep(1)

        # Check image counter in modal
        cmd_check = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const match = document.body.innerText.match(/(\\d+)\\s*\\/\\s*4\\s*images/);
                    const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SAVE CHANGES'));
                    return {
                        counter: match ? match[0] : null,
                        saveBtnDisabled: saveBtn ? saveBtn.disabled : null
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd_check))
        print("Status before saving:", (await ws.recv()))

        # Click SAVE CHANGES
        cmd_save = {
            'id': 3,
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
        await ws.send(json.dumps(cmd_save))
        print("Save button click:", (await ws.recv()))

        # Wait and check if modal closes
        for i in range(1, 6):
            await asyncio.sleep(1)
            cmd_poll = {
                'id': 10 + i,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const dialog = document.querySelector('[role="dialog"]');
                        return { dialogOpen: !!dialog };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_poll))
            res = json.loads(await ws.recv())
            val = res.get('result', {}).get('result', {}).get('value', {})
            print(f"[{i}s] dialog state:", val)
            if not val.get('dialogOpen'):
                print("Modal closed successfully! Entry 1 saved.")
                break

if __name__ == '__main__':
    asyncio.run(save_entry1())
