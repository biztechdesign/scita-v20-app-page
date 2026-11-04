"""Full-length homepage captures (tall viewport so Odoo's #wrapwrap shows everything) - textures for the curled-paper laptops."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "assets" / "shots"
DEMOS = {"webtoprint": "https://theme-scita-w2p-v19.appjetty.com/", "grocery": "https://theme-scita-grocery-v19.appjetty.com/",
         "furniture": "https://theme-scita-furniture-v19.appjetty.com/", "electronics": "https://theme-scita-v19.appjetty.com/"}
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for name, url in DEMOS.items():
            pg = await br.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
            await pg.goto(url, timeout=60000)
            try: await pg.wait_for_load_state("networkidle", timeout=20000)
            except Exception: pass
            # step through the page so lazy images load, then grow the viewport to the full height
            for y in range(0, 8000, 600):
                await pg.evaluate(f"() => {{ const w = document.getElementById('wrapwrap'); if (w) w.scrollTop = {y}; window.scrollTo(0, {y}); }}")
                await pg.wait_for_timeout(200)
            await pg.evaluate("() => { const w = document.getElementById('wrapwrap'); if (w) w.scrollTop = 0; window.scrollTo(0, 0); }")
            h = await pg.evaluate("() => { const w = document.getElementById('wrapwrap'); return Math.max(w ? w.scrollHeight : 0, document.body.scrollHeight); }")
            h = min(h, 5400)
            await pg.set_viewport_size({"width": 1440, "height": h}); await pg.wait_for_timeout(2500)
            await pg.screenshot(path=str(OUT / f"{name}_long.png")); print(name, h); await pg.close()
        await br.close()
asyncio.run(main())
