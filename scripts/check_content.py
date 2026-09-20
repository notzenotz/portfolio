"""Checks site/content.json before it goes live.

Catches the mistakes that would otherwise break the live page:
  - JSON that does not parse (a stray comma, a missing quote)
  - a field with the wrong shape, e.g. "images": "a.webp" instead of a list
  - an image path that does not exist, including wrong upper/lower case.
    Windows forgives "Me-1.webp" vs "me-1.webp"; S3 and CloudFront do not.

Run locally:   python scripts/check_content.py site
Exit code 1 on any problem. In GitHub Actions, problems show up as annotations.
"""
import json
import os
import sys
from pathlib import Path

site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
content_file = site / "content.json"
problems = []


def problem(msg, line=None):
    problems.append(msg)
    where = f"file=site/content.json,line={line}" if line else "file=site/content.json"
    print(f"::error {where}::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"x {msg}")


try:
    data = json.loads(content_file.read_text(encoding="utf-8"))
except FileNotFoundError:
    print(f"x {content_file} tidak ditemukan")
    sys.exit(1)
except json.JSONDecodeError as e:
    problem(f"content.json tidak valid di baris {e.lineno}, kolom {e.colno}: {e.msg}", e.lineno)
    sys.exit(1)


# ---------------------------------------------------------------- shape checks
def expect(value, kind, where):
    ok = {"text": isinstance(value, str),
          "list": isinstance(value, list),
          "object": isinstance(value, dict)}[kind]
    if not ok:
        label = {"text": "teks", "list": "daftar [ ... ]", "object": "objek { ... }"}[kind]
        problem(f"{where} harus berupa {label}")
    return ok


def text_list(value, where):
    if expect(value, "list", where):
        for i, x in enumerate(value):
            expect(x, "text", f"{where}[{i}]")


CARD_TEXT = ("title", "meta", "caption")
CARD_LISTS = ("images", "paragraphs", "points", "stack")


def card(c, where):
    if not expect(c, "object", where):
        return
    if not c.get("title"):
        problem(f"{where} belum punya title")
    for k in CARD_TEXT:
        if k in c:
            expect(c[k], "text", f"{where}.{k}")
    for k in CARD_LISTS:
        if k in c:
            text_list(c[k], f"{where}.{k}")
    if "link" in c and expect(c["link"], "object", f"{where}.link"):
        for k in ("text", "url"):
            if not isinstance(c["link"].get(k), str):
                problem(f"{where}.link butuh {k} berupa teks")


def items(section, key="items"):
    block = data.get(section)
    if block is None:
        problem(f"bagian {section} tidak ada")
        return []
    value = block.get(key, [])
    return value if expect(value, "list", f"{section}.{key}") else []


for section in ("projects", "organization", "bangkit", "honours"):
    for i, c in enumerate(items(section)):
        card(c, f"{section}.items[{i}]")

for i, p in enumerate(items("posters")):
    for k in ("image", "title", "meta"):
        expect(p.get(k), "text", f"posters.items[{i}].{k}")

for i, c in enumerate(items("honours", "certificates")):
    for k in ("image", "caption"):
        expect(c.get(k), "text", f"honours.certificates[{i}].{k}")

for i, t in enumerate(items("skills", "tools")):
    expect(t.get("name"), "text", f"skills.tools[{i}].name")
    if "icon" in t:
        expect(t["icon"], "text", f"skills.tools[{i}].icon")

for i, p in enumerate(data.get("about", {}).get("photos", [])):
    expect(p.get("image"), "text", f"about.photos[{i}].image")

if not isinstance(data.get("about", {}).get("bio"), str):
    problem("about.bio harus berupa teks")


# ---------------------------------------------------------------- image paths
def exists_exact_case(rel):
    """True only if every part of the path matches a real name, letter case included."""
    here = site
    for part in Path(rel).parts:
        try:
            names = os.listdir(here)
        except (FileNotFoundError, NotADirectoryError):
            return False
        if part not in names:
            return False
        here = here / part
    return here.is_file()


def walk(value, where="content"):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from walk(v, f"{where}.{k}" if where != "content" else k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk(v, f"{where}[{i}]")
    elif isinstance(value, str) and value.startswith("assets/"):
        yield where, value


used = list(walk(data))
for where, rel in used:
    if not exists_exact_case(rel):
        problem(f"{where} menunjuk ke {rel}, tapi file itu tidak ada (cek juga huruf besar/kecil)")

if problems:
    print(f"\n{len(problems)} masalah ditemukan di content.json.")
    sys.exit(1)
print(f"content.json valid. {len(used)} rujukan gambar, semuanya ada.")
