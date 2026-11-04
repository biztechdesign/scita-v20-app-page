"""List product images on the grocery demo and download the 1024px originals."""
import asyncio, json, re, urllib.request
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "assets" / "products"; OUT.mkdir(parents=True, exist_ok=True)
URL = "https://theme-scita-grocery-v19.appjetty.com/shop"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 1440, "height": 900})
        await pg.goto(URL, timeout=60000)
        try: await pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception: pass
        items = await pg.evaluate("""() => [...document.querySelectorAll('img')].map(i => ({src: i.currentSrc || i.src, alt: i.alt}))
            .filter(x => /product\.(template|product)\//.test(x.src))""")
        await br.close()
    seen = {}
    for it in items:
        m = re.search(r"product\.(template|product)/(\d+)/", it["src"])
        if m and m.group(2) not in seen: seen[m.group(2)] = (m.group(1), it["alt"])
    for pid, (model, alt) in list(seen.items())[:40]:
        print(pid, model, alt)
    json.dump(seen, open(OUT / "index.json", "w"), indent=1)
asyncio.run(main())
