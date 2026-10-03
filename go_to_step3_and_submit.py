import asyncio
import json
import base64
import os
import websockets

async def main():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # Step 1: Click NEXT on Step 2
        click_cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                    if (!btn) return 'NEXT button not found';
                    if (btn.disabled) return 'NEXT button disabled';
                    btn.click();
                    return 'Clicked NEXT';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(click_cmd))
        print("Click NEXT Step 2:", await ws.recv())

        await asyncio.sleep(2)

        # Step 2: Inspect Step 3
        check_step3 = {
            'id': 2,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SUBMIT WARM-UP'));
                    const videoInput = document.querySelector('input[type="file"][accept*="video"]');
                    const text = document.body.innerText;
                    return {
                        hasSubmitBtn: !!submitBtn,
                        submitDisabled: submitBtn ? submitBtn.disabled : null,
                        hasVideoInput: !!videoInput,
                        textSnippet: text.slice(0, 400)
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(check_step3))
        res3 = json.loads(await ws.recv())
        val3 = res3.get('result', {}).get('result', {}).get('value', {})
        print("Step 3 State:", json.dumps(val3, indent=2))

        # Step 3: If video input exists and submit is disabled, upload video
        video_path = r"C:\Users\white\pocket-companion\assets\reels\pocket_companion_demo_reel.mp4"
        if val3.get('submitDisabled') and os.path.exists(video_path):
            print("Video upload needed. Finding video input objectId...")
            eval_v = {
                'id': 10,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': "document.querySelector('input[type=\"file\"][accept*=\"video\"]')",
                    'returnByValue': False
                }
            }
            await ws.send(json.dumps(eval_v))
            v_res = json.loads(await ws.recv())
            v_obj_id = v_res.get("result", {}).get("result", {}).get("objectId")
            print("Video input objectId:", v_obj_id)

            if v_obj_id:
                upload_cmd = {
                    'id': 11,
                    'method': 'DOM.setFileInputFiles',
                    'params': {
                        'files': [video_path],
                        'objectId': v_obj_id
                    }
                }
                await ws.send(json.dumps(upload_cmd))
                print("DOM.setFileInputFiles resp:", await ws.recv())

                trigger_cmd = {
                    'id': 12,
                    'method': 'Runtime.callFunctionOn',
                    'params': {
                        'objectId': v_obj_id,
                        'functionDeclaration': """function() {
                            this.dispatchEvent(new Event('input', { bubbles: true }));
                            this.dispatchEvent(new Event('change', { bubbles: true }));
                        }"""
                    }
                }
                await ws.send(json.dumps(trigger_cmd))
                print("Trigger video resp:", await ws.recv())

        # Step 4: Wait for SUBMIT WARM-UP button to become enabled
        print("Waiting for SUBMIT WARM-UP button to be enabled...")
        for sec in range(1, 25):
            await asyncio.sleep(1)
            poll_btn = {
                'id': 50 + sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SUBMIT WARM-UP'));
                        return {
                            found: !!submitBtn,
                            disabled: submitBtn ? submitBtn.disabled : true,
                            text: submitBtn ? submitBtn.innerText : ''
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(poll_btn))
            p_res = json.loads(await ws.recv())
            btn_state = p_res.get('result', {}).get('result', {}).get('value', {})
            print(f"[{sec}s] Submit button state:", btn_state)
            if btn_state.get('found') and not btn_state.get('disabled'):
                print(">>> SUBMIT WARM-UP IS ENABLED! Clicking now... <<<")
                break

        # Step 5: Click SUBMIT WARM-UP
        submit_exec = {
            'id': 99,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SUBMIT WARM-UP'));
                    if (!submitBtn) return 'Button not found';
                    if (submitBtn.disabled) return 'Button disabled';
                    submitBtn.click();
                    return 'Clicked SUBMIT WARM-UP';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(submit_exec))
        print("Submit click result:", await ws.recv())

        # Step 6: Poll for submission confirmation (SUBMITTED / IN REVIEW)
        for check_sec in range(1, 20):
            await asyncio.sleep(1)
            status_check = {
                'id': 150 + check_sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const text = document.body.innerText;
                        const isSubmitted = text.includes('SUBMITTED') || text.includes('Submitted') || text.includes('IN REVIEW') || text.includes('In Review');
                        const hasUnsubmit = text.includes('UNSUBMIT') || text.includes('Unsubmit');
                        const modal = !!document.querySelector('[role="dialog"]');
                        return {
                            isSubmitted,
                            hasUnsubmit,
                            hasModal: modal
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(status_check))
            s_res = json.loads(await ws.recv())
            s_val = s_res.get('result', {}).get('result', {}).get('value', {})
            print(f"[{check_sec}s] Submission confirmation:", s_val)
            if s_val.get('isSubmitted') or s_val.get('hasUnsubmit'):
                print(">>> SUBMISSION CONFIRMED! <<<")
                break

        # Step 7: Capture screenshot
        shot_cmd = {
            'id': 300,
            'method': 'Page.captureScreenshot',
            'params': {'format': 'png'}
        }
        await ws.send(json.dumps(shot_cmd))
        shot_res = json.loads(await ws.recv())
        img_b64 = shot_res.get('result', {}).get('data')
        if img_b64:
            out_img = r"C:\Users\white\pocket-companion\assets\submission_confirmed_final.png"
            with open(out_img, 'wb') as f:
                f.write(base64.b64decode(img_b64))
            print(f"Captured screenshot to: {out_img}")

if __name__ == '__main__':
    asyncio.run(main())
