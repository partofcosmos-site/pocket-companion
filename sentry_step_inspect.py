import asyncio
import json
import urllib.request
import websockets

def get_live_ws_url():
    try:
        with urllib.request.urlopen("http://127.0.0.1:9100/json/list", timeout=3) as resp:
            targets = json.loads(resp.read().decode("utf-8"))
            for t in targets:
                url = t.get("url", "").lower()
                if "halflife" in url or "cmuqw217z02uz01rlatu9wyrg" in url:
                    ws = t.get("webSocketDebuggerUrl")
                    if ws:
                        return ws
            # Fallback to first page
            for t in targets:
                if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                    return t.get("webSocketDebuggerUrl")
    except Exception as e:
        print(f"[ERROR] Could not query CDP json/list: {e}")
    return 'ws://127.0.0.1:9100/devtools/page/93FA310AC7FB1470DF24F339DB313D66'

async def inspect():
    ws_url = get_live_ws_url()
    print(f"[CDP] Connecting to: {ws_url}")
    async with websockets.connect(ws_url) as ws:
        cmd = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const text = document.body.innerText;
                    const modal = document.querySelector('[role="dialog"]');
                    const modalText = modal ? modal.innerText : '';
                    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                        text: b.innerText.trim(),
                        disabled: b.disabled
                    })).filter(b => b.text);
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, [class*="step"]')).map(h => h.innerText.trim());
                    return {
                        hasModal: !!modal,
                        modalTextSnippet: modalText.slice(0, 300),
                        buttons: buttons.slice(-10),
                        headings: headings.slice(0, 10),
                        isSubmitted: text.includes('SUBMITTED') || text.includes('Submitted') || text.includes('IN REVIEW') || text.includes('In Review'),
                        hasUnsubmit: text.includes('UNSUBMIT') || text.includes('Unsubmit')
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
    asyncio.run(inspect())
