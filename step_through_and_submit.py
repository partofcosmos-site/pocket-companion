import asyncio
import json
import base64
import os
import websockets

WS_URL = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
CART_IMG = r"C:\Users\white\pocket-companion\assets\pocket_companion_cart_summary.png"
VIDEO_REEL = r"C:\Users\white\pocket-companion\assets\reels\pocket_companion_demo_reel.mp4"
CONFIRM_IMG = r"C:\Users\white\pocket-companion\assets\submission_confirmed_live.png"

async def execute_step_through():
    async with websockets.connect(WS_URL, max_size=50*1024*1024) as ws:
        print("[STEP 1] Checking current state / Step 1...")
        cmd_step1 = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const modal = document.querySelector('[role="dialog"]');
                    const text = modal ? modal.innerText : document.body.innerText;
                    const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                    return {
                        inModal: !!modal,
                        textSnippet: text.slice(0, 300),
                        nextFound: !!nextBtn,
                        nextDisabled: nextBtn ? nextBtn.disabled : true
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd_step1))
        res = json.loads(await ws.recv())
        val1 = res.get('result', {}).get('result', {}).get('value', {})
        print("[STEP 1] State:", json.dumps(val1, indent=2))

        # If NEXT button is available, click it
        if val1.get('nextFound') and not val1.get('nextDisabled'):
            print("[STEP 1] Clicking NEXT to advance to Step 2...")
            click_next = {
                'id': 2,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                        if (nextBtn) { nextBtn.click(); return 'Clicked NEXT'; }
                        return 'NEXT not found';
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(click_next))
            print("[STEP 1] Click res:", await ws.recv())

        await asyncio.sleep(2.5)

        # Inspect Step 2
        print("[STEP 2] Inspecting Step 2 (Tier & Cart)...")
        inspect_step2 = {
            'id': 10,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const modal = document.querySelector('[role="dialog"]') || document.body;
                    const text = modal.innerText;
                    const tierBtns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Tier') || b.innerText.includes('$30')).map(b => ({
                        text: b.innerText.trim(),
                        disabled: b.disabled,
                        className: b.className
                    }));
                    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
                        accept: i.accept,
                        hasFiles: i.files ? i.files.length : 0
                    }));
                    const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                    const images = Array.from(modal.querySelectorAll('img')).map(i => i.src);
                    return {
                        textSnippet: text.slice(0, 300),
                        tierBtns,
                        fileInputs,
                        imagesCount: images.length,
                        nextFound: !!nextBtn,
                        nextDisabled: nextBtn ? nextBtn.disabled : true
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(inspect_step2))
        res2 = json.loads(await ws.recv())
        val2 = res2.get('result', {}).get('result', {}).get('value', {})
        print("[STEP 2] State:", json.dumps(val2, indent=2))

        # Check if Tier 1 needs selection
        select_tier1 = {
            'id': 11,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const t1Btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Tier 1') || b.innerText.includes('$30'));
                    if (t1Btn) {
                        t1Btn.click();
                        return 'Clicked Tier 1';
                    }
                    return 'Tier 1 button not found';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(select_tier1))
        print("[STEP 2] Tier 1 select:", await ws.recv())

        await asyncio.sleep(1)

        # If NEXT is disabled and file input exists, upload cart screenshot
        inspect_next_s2 = {
            'id': 12,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                    return { disabled: nextBtn ? nextBtn.disabled : true };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(inspect_next_s2))
        n2_res = json.loads(await ws.recv())
        n2_disabled = n2_res.get('result', {}).get('result', {}).get('value', {}).get('disabled', True)

        if n2_disabled:
            print("[STEP 2] NEXT is disabled, uploading cart screenshot...")
            eval_file_input = {
                'id': 13,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': "document.querySelector('input[type=\"file\"][accept*=\"image\"]') || document.querySelector('input[type=\"file\"]')",
                    'returnByValue': False
                }
            }
            await ws.send(json.dumps(eval_file_input))
            f_res = json.loads(await ws.recv())
            f_obj_id = f_res.get("result", {}).get("result", {}).get("objectId")
            if f_obj_id:
                upload_cart = {
                    'id': 14,
                    'method': 'DOM.setFileInputFiles',
                    'params': {
                        'files': [CART_IMG],
                        'objectId': f_obj_id
                    }
                }
                await ws.send(json.dumps(upload_cart))
                print("[STEP 2] setFileInputFiles cart:", await ws.recv())

                trigger_cart = {
                    'id': 15,
                    'method': 'Runtime.callFunctionOn',
                    'params': {
                        'objectId': f_obj_id,
                        'functionDeclaration': """function() {
                            this.dispatchEvent(new Event('input', { bubbles: true }));
                            this.dispatchEvent(new Event('change', { bubbles: true }));
                        }"""
                    }
                }
                await ws.send(json.dumps(trigger_cart))
                print("[STEP 2] Trigger cart:", await ws.recv())

                # Wait for upload to complete
                await asyncio.sleep(3)

        # Click NEXT on Step 2
        print("[STEP 2] Clicking NEXT to advance to Step 3...")
        click_next_s2 = {
            'id': 20,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'NEXT');
                    if (nextBtn && !nextBtn.disabled) {
                        nextBtn.click();
                        return 'Clicked NEXT on Step 2';
                    }
                    return nextBtn ? 'NEXT disabled' : 'NEXT not found';
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(click_next_s2))
        res_next_s2 = json.loads(await ws.recv())
        print("[STEP 2] Advance res:", res_next_s2.get('result', {}).get('result', {}).get('value'))

        await asyncio.sleep(2.5)

        # Inspect Step 3 (Video reel & submit)
        print("[STEP 3] Inspecting Step 3 (Video Reel & Submit Warm-Up)...")
        inspect_step3 = {
            'id': 30,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const modal = document.querySelector('[role="dialog"]') || document.body;
                    const text = modal.innerText;
                    const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SUBMIT WARM-UP') || b.innerText.includes('SUBMIT'));
                    const videoInput = document.querySelector('input[type="file"][accept*="video"]') || document.querySelector('input[type="file"]');
                    const videos = Array.from(modal.querySelectorAll('video')).map(v => v.src);
                    return {
                        textSnippet: text.slice(0, 300),
                        hasSubmitBtn: !!submitBtn,
                        submitText: submitBtn ? submitBtn.innerText.trim() : null,
                        submitDisabled: submitBtn ? submitBtn.disabled : true,
                        hasVideoInput: !!videoInput,
                        videoCount: videos.length
                    };
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(inspect_step3))
        res3 = json.loads(await ws.recv())
        val3 = res3.get('result', {}).get('result', {}).get('value', {})
        print("[STEP 3] State:", json.dumps(val3, indent=2))

        # If submit is disabled and video input exists, upload video reel
        if val3.get('submitDisabled') and os.path.exists(VIDEO_REEL):
            print("[STEP 3] Video upload required. Setting file input...")
            eval_vid_input = {
                'id': 31,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': "document.querySelector('input[type=\"file\"][accept*=\"video\"]') || document.querySelector('input[type=\"file\"]')",
                    'returnByValue': False
                }
            }
            await ws.send(json.dumps(eval_vid_input))
            v_res = json.loads(await ws.recv())
            v_obj_id = v_res.get("result", {}).get("result", {}).get("objectId")
            if v_obj_id:
                upload_vid = {
                    'id': 32,
                    'method': 'DOM.setFileInputFiles',
                    'params': {
                        'files': [VIDEO_REEL],
                        'objectId': v_obj_id
                    }
                }
                await ws.send(json.dumps(upload_vid))
                print("[STEP 3] setFileInputFiles video:", await ws.recv())

                trigger_vid = {
                    'id': 33,
                    'method': 'Runtime.callFunctionOn',
                    'params': {
                        'objectId': v_obj_id,
                        'functionDeclaration': """function() {
                            this.dispatchEvent(new Event('input', { bubbles: true }));
                            this.dispatchEvent(new Event('change', { bubbles: true }));
                        }"""
                    }
                }
                await ws.send(json.dumps(trigger_vid))
                print("[STEP 3] Trigger video:", await ws.recv())

        # Wait for SUBMIT WARM-UP button to become enabled
        print("[STEP 3] Polling for SUBMIT WARM-UP button to be enabled...")
        submit_ready = False
        for sec in range(1, 30):
            await asyncio.sleep(1)
            poll_sub = {
                'id': 40 + sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SUBMIT WARM-UP'));
                        return {
                            found: !!submitBtn,
                            disabled: submitBtn ? submitBtn.disabled : true,
                            text: submitBtn ? submitBtn.innerText.trim() : ''
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(poll_sub))
            p_res = json.loads(await ws.recv())
            s_state = p_res.get('result', {}).get('result', {}).get('value', {})
            print(f"[{sec}s] Submit button: {s_state}")
            if s_state.get('found') and not s_state.get('disabled'):
                submit_ready = True
                print(">>> SUBMIT WARM-UP IS READY AND ENABLED! <<<")
                break

        if submit_ready:
            print("[STEP 3] Clicking SUBMIT WARM-UP...")
            click_sub = {
                'id': 100,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SUBMIT WARM-UP'));
                        if (submitBtn && !submitBtn.disabled) {
                            submitBtn.click();
                            return 'CLICKED_SUBMIT_WARMUP';
                        }
                        return 'Could not click submit';
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(click_sub))
            sub_res = json.loads(await ws.recv())
            print("[STEP 3] Submit click response:", sub_res.get('result', {}).get('result', {}).get('value'))
        else:
            print("[STEP 3] Warning: submit_ready was False after polling.")

        # Step 4: Verify page state updates to SUBMITTED · IN REVIEW
        print("[VERIFICATION] Waiting for page status update...")
        verified = False
        for sec in range(1, 25):
            await asyncio.sleep(1)
            check_status = {
                'id': 110 + sec,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const text = document.body.innerText;
                        const isSubmitted = text.includes('SUBMITTED') || text.includes('Submitted') || text.includes('IN REVIEW') || text.includes('In Review');
                        const hasUnsubmit = text.includes('UNSUBMIT') || text.includes('Unsubmit');
                        const statusBadges = Array.from(document.querySelectorAll('[class*="badge"], [class*="status"], h1, h2, h3, h4, span, div')).map(e => e.innerText.trim()).filter(t => t.includes('SUBMITTED') || t.includes('IN REVIEW') || t.includes('WARM-UP'));
                        return {
                            isSubmitted,
                            hasUnsubmit,
                            statusBadges: Array.from(new Set(statusBadges)).slice(0, 10),
                            url: window.location.href
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(check_status))
            st_res = json.loads(await ws.recv())
            st_val = st_res.get('result', {}).get('result', {}).get('value', {})
            print(f"[{sec}s] Portal status: {st_val}")
            if st_val.get('isSubmitted') or st_val.get('hasUnsubmit'):
                verified = True
                print(">>> VERIFIED: PROJECT IS SUBMITTED · IN REVIEW! <<<")
                break

        # Step 5: Capture confirmation screenshot
        print(f"[SCREENSHOT] Capturing visual confirmation screenshot to {CONFIRM_IMG}...")
        shot_cmd = {
            'id': 200,
            'method': 'Page.captureScreenshot',
            'params': {'format': 'png'}
        }
        await ws.send(json.dumps(shot_cmd))
        shot_res = json.loads(await ws.recv())
        img_b64 = shot_res.get('result', {}).get('data')
        if img_b64:
            with open(CONFIRM_IMG, 'wb') as f:
                f.write(base64.b64decode(img_b64))
            print(f"[SCREENSHOT] Saved visual confirmation to: {CONFIRM_IMG} ({os.path.getsize(CONFIRM_IMG)} bytes)")

        return verified

if __name__ == '__main__':
    res = asyncio.run(execute_step_through())
    print("Execution complete. Status verified:", res)
