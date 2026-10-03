import asyncio
import datetime
import json
import os
import sys
import time
import urllib.request
import websockets

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WS_URL = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
HEARTBEAT_FILE = r'C:\Users\white\pocket-companion\sentry_heartbeat.json'
LOG_FILE = r'C:\Users\white\pocket-companion\sentry_status.log'
SCREENSHOT_FILE = r'C:\Users\white\pocket-companion\assets\submission_confirmed_live.png'

CDN_IMAGE_URLS = [
    "https://halflife.hackclub-assets.com/hackclub-half-life/covers/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/5e449e176c85c1d4a4318d1d9541141d42ec89aa26c34e6a881e93d6927da231.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/71f1e30cb4aaa1d3645ea29fa7da0e0f4d5774497b45c4ee4927fcc0c868b50f.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/378cd39cac2fd3ea545bb6c8136c01ec41206b467dacadc1b29e9c29417083aa.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/e187ecc97d25d935846136cca57cd152e7e2bf0f34cf15355a435de18d82b91f.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/31ce3a0aad3344d69b94c5da8ff59737bd36d12a0cb56e4f1ae70f1bebac14dd.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/40a35485c4da3ae9c094347a21e765887886bd8506811d5f87424882b952a344.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/d814b9455769c4e7c8d6c3503dc198a8bcbbfe616ed28c84804c287e9412863d.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/bc2db1c001d1d81bce4f2f16691ded51a47d57cbce4c1fcb1adfb49931ee5d99.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/cae16ce9705a4287b5d016bb042c39e04f065694f9e1196ce56d5cf533009ca5.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/f4fd3f28e1eb4d983b4e0c02e1d72f5e47a18cd43a5570abfe2c30a984876071.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/83ee80aaa95dd163d5ea2e2f3fed2f73f7b971ac7ab93308adfa669440d1617a.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/8b0883b320b9a22ea11839199b1c6237220fbd59cfaa9dd3f0a876422835b96f.png",
    "https://halflife.hackclub-assets.com/hackclub-half-life/sessions/gSMICPeKfFIX4r61sX8jLHHguUkM0Btr/663c98819a35280e7834c2e614e8f6ecaba066d9b0f043f7295a1e3015651059.png"
]

def verify_cdn_images():
    results = {}
    all_ok = True
    for idx, url in enumerate(CDN_IMAGE_URLS):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as r:
                code = r.status
                results[idx] = code
                if code != 200:
                    all_ok = False
        except Exception as e:
            results[idx] = str(e)
            all_ok = False
    return all_ok, results

async def inspect_portal_state():
    try:
        async with websockets.connect(WS_URL, max_size=50*1024*1024, open_timeout=5) as ws:
            cmd = {
                'id': 1,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const text = document.body.innerText;
                        const hasSubmitted = text.includes('Submitted. Where it stands with review is below.') || text.includes('In review, so it can\\'t be edited.');
                        const hasUnsubmit = text.includes('UNSUBMIT THIS WARM-UP PROJECT');
                        const hasInReview = text.includes('IN REVIEW') || text.includes('Design\\nIN REVIEW');
                        const hasWaitingReview = text.includes('This week is waiting for review') || text.includes('waiting for review');
                        
                        // Entries check
                        const e1 = text.includes('Bench Prototyping, Power Budgeting & Dialing In The Hardware');
                        const e2 = text.includes('EasyEDA Schematic Capture, BOM Selection & Layout Planning');
                        const e3 = text.includes('PCB Routing, JLCPCB DRC, Soldering Clearance & Firmware Polish');
                        
                        // Hackatime
                        const hIdx = text.indexOf('HACKATIME');
                        const bIdx = text.indexOf('BILL OF MATERIALS');
                        let ht = '';
                        if (hIdx !== -1 && bIdx !== -1) {
                            ht = text.slice(hIdx, bIdx).trim();
                        }
                        
                        // Total hours logged
                        const hrMatches = text.match(/([0-9.]+)h logged/g) || [];
                        
                        return {
                            url: window.location.href,
                            title: document.title,
                            hasSubmitted,
                            hasUnsubmit,
                            hasInReview,
                            hasWaitingReview,
                            entries: { e1, e2, e3 },
                            hackatimeSnippet: ht,
                            hoursLogged: hrMatches
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd))
            res = json.loads(await ws.recv())
            return res.get('result', {}).get('result', {}).get('value', {})
    except Exception as e:
        return {'error': str(e)}

async def sentry_loop(interval_sec=60, max_iterations=None):
    iteration = 0
    print(f"=== STARTING POCKET COMPANION PORTAL SENTRY (Interval: {interval_sec}s) ===")
    
    while True:
        iteration += 1
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Inspect portal state via CDP
        portal_state = await inspect_portal_state()
        
        # 2. Verify CDN images
        cdn_ok, cdn_details = verify_cdn_images()
        
        # 3. Check health metrics
        is_in_review = portal_state.get('hasInReview') or portal_state.get('hasSubmitted') or portal_state.get('hasUnsubmit')
        all_entries_ok = (portal_state.get('entries', {}).get('e1') and 
                          portal_state.get('entries', {}).get('e2') and 
                          portal_state.get('entries', {}).get('e3'))
        
        report = {
            "timestamp": now_str,
            "iteration": iteration,
            "status": "HEALTHY_SUBMITTED_IN_REVIEW" if (is_in_review and all_entries_ok and cdn_ok) else "ATTENTION_REQUIRED",
            "portal": {
                "in_review": is_in_review,
                "has_unsubmit": portal_state.get('hasUnsubmit'),
                "waiting_for_review": portal_state.get('hasWaitingReview'),
                "hours_logged": portal_state.get('hoursLogged'),
                "hackatime": portal_state.get('hackatimeSnippet', '').split('\n')[:4]
            },
            "journal_entries": {
                "entry1_live": portal_state.get('entries', {}).get('e1'),
                "entry2_live": portal_state.get('entries', {}).get('e2'),
                "entry3_live": portal_state.get('entries', {}).get('e3')
            },
            "cdn_images": {
                "verified_all_200": cdn_ok,
                "total_verified": len(CDN_IMAGE_URLS)
            }
        }
        
        # Write heartbeat
        with open(HEARTBEAT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        log_line = f"[{now_str}][Cycle #{iteration}] Status: {report['status']} | Portal In-Review: {is_in_review} | Entries: {all_entries_ok} | Images (13/13): {cdn_ok} | Hours: {portal_state.get('hoursLogged')}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
            
        print(log_line.strip())
        sys.stdout.flush()
        
        if max_iterations and iteration >= max_iterations:
            print(f"Reached max iterations ({max_iterations}). Exiting loop.")
            break
            
        await asyncio.sleep(interval_sec)

if __name__ == '__main__':
    max_it = None
    if len(sys.argv) > 1:
        max_it = int(sys.argv[1])
    asyncio.run(sentry_loop(interval_sec=60, max_iterations=max_it))
