"""Responsive QA for odoo_description/preview.html: horizontal overflow, clipped text, tap sizes; screenshots of HTML sections."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parent.parent; P = ROOT / "odoo_description" / "preview.html"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for w in (320, 375, 768, 1300):
            pg = await br.new_page(viewport={"width": w, "height": 900})
            await pg.goto(P.as_uri()); await pg.wait_for_load_state("networkidle")
            r = await pg.evaluate("""() => {
              const de = document.documentElement;
              const over = [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); return b.width && (b.right > de.clientWidth + 1 || b.left < -1); }).length;
              const clipped = [...document.querySelectorAll('.accordion-button, .accordion-body, h2, p, li, a')].filter(e => e.scrollWidth > e.clientWidth + 1).length;
              const taps = [...document.querySelectorAll('.accordion-button, a[href^=mailto]')].map(e => e.getBoundingClientRect().height);
              return {scrollW: de.scrollWidth, clientW: de.clientWidth, overflowing: over, clipped, minTap: Math.round(Math.min(...taps))};
            }""")
            print(w, r)
            if w in (320, 768):
                el = await pg.query_selector("#scita_faq"); box = await el.bounding_box()
                await pg.screenshot(path=str(ROOT / "export" / f"resp_{w}.png"), full_page=True,
                                    clip={"x": 0, "y": box["y"] - 140, "width": w, "height": 2600 if w == 320 else 1900})
            await pg.close()
        await br.close()
asyncio.run(main())
