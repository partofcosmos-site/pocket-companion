import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

def search_ddg(query):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'amazon\.in(?:/[^/]+)?/dp/(B0[A-Z0-9]{8})', html)
            return list(set(matches))
    except Exception as e:
        return []

def verify_amazon_url(asin):
    url = f"https://www.amazon.in/dp/{asin}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
            return resp.status == 200, url
    except Exception:
        return False, url

queries = [
    ('TP4056 Type-C', ['site:amazon.in TP4056 Type C module', 'site:amazon.in TP4056 1A lithium battery charging module']),
    ('Tactile Switch', ['site:amazon.in tactile push button switch 6x6x5mm', 'site:amazon.in momentary push button switch 6mm']),
    ('SPDT Switch', ['site:amazon.in SPDT micro slide switch', 'site:amazon.in mini slide switch on on 3 pin']),
    ('Passive Piezo Buzzer', ['site:amazon.in passive buzzer module arduino', 'site:amazon.in passive piezo buzzer 5v']),
    ('Perfboard', ['site:amazon.in double sided perfboard 4x6', 'site:amazon.in universal prototype pcb board 4x6cm']),
    ('30 AWG Wire', ['site:amazon.in 30 AWG wire wrapping spool', 'site:amazon.in 30awg silicone jumper wire']),
    ('LiPo Battery', ['site:amazon.in 3.7V 500mAh lipo battery', 'site:amazon.in 3.7V 400mAh lithium polymer battery'])
]

results = {}
for name, q_list in queries:
    found_url = None
    for q in q_list:
        asins = search_ddg(q)
        for asin in asins:
            ok, u = verify_amazon_url(asin)
            if ok:
                found_url = u
                break
        if found_url:
            break
    results[name] = found_url
    print(f"Product: {name} -> {found_url}")
