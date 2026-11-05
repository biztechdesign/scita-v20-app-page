"""Render the v20 listing banners (538x269) at 1x, 2x and 4x.
  python banner/render_banners.py
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "export"; OUT.mkdir(exist_ok=True)

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for f in sorted(HERE.glob("banner-*.html")):
            for scale in (1, 2, 4):
                pg = await (await br.new_context(viewport={"width": 600, "height": 320}, device_scale_factor=scale)).new_page()
                await pg.goto(f.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
                suffix = "" if scale == 1 else f"@{scale}x"
                await (await pg.query_selector("#banner")).screenshot(path=str(OUT / f"{f.stem}{suffix}.png"))
                await pg.close()
            print("rendered", f.stem)
        await br.close()

asyncio.run(main())
