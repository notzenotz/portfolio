"""After a deploy: is the live site really serving the new files?

Checks the home page, content.json, and the first image content.json points to.
Usage:  python scripts/smoke_test.py https://dxxxxxxxxxxxx.cloudfront.net
"""
import json
import sys
import time
import urllib.error
import urllib.request

base = sys.argv[1].rstrip("/")


def get(path, tries=5):
    url = base + path
    req = urllib.request.Request(url, headers={"User-Agent": "portfolio-smoke-test"})
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as e:
            if attempt == tries:
                sys.exit(f"x {url} menjawab HTTP {e.code}")
        except urllib.error.URLError as e:
            if attempt == tries:
                sys.exit(f"x {url} tidak bisa dihubungi: {e.reason}")
        time.sleep(3 * attempt)


status, ctype, body = get("/")
if b"<title>" not in body:
    sys.exit("x halaman utama terbuka, tapi isinya bukan index.html")
print(f"ok  /              {status} {ctype}")

status, ctype, body = get("/content.json")
try:
    data = json.loads(body)
except ValueError:
    sys.exit("x content.json di situs live tidak bisa dibaca")
print(f"ok  /content.json  {status} {ctype}")


def first_asset(value):
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        for v in value:
            found = first_asset(v)
            if found:
                return found
    elif isinstance(value, str) and value.startswith("assets/"):
        return value
    return None


image = first_asset(data)
if image:
    status, ctype, _ = get("/" + image)
    if not ctype.startswith("image/"):
        sys.exit(f"x {image} dikirim dengan Content-Type {ctype!r}, seharusnya image/...")
    print(f"ok  /{image}  {status} {ctype}")

print(f"\nSitus live: {base}")
