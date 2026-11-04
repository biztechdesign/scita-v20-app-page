"""Render fold HTML files to images.

  python tools/render.py [fold-name ...]        # default: every folds/NN-*.html
Outputs:
  export/png/NN-name.png   2x master (2576px wide)
  export/NN-name.jpg       2000px wide, 4:4:4 (sharp coloured text), ready for the Odoo app page
  export/preview/NN-name.jpg  700px preview
"""
import sys, os, glob, asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
FOLDS, OUT = ROOT / "folds", ROOT / "export"
for d in (OUT, OUT / "png", OUT / "preview"): d.mkdir(parents=True, exist_ok=True)

def targets(args):
    files = sorted(FOLDS.glob("[0-9][0-9]-*.html"))
    if args: files = [f for f in files if any(a in f.name for a in args)]
    return files

async def main(args):
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 1288, "height": 900}, device_scale_factor=2)
        page = await ctx.new_page()
        for f in targets(args):
            await page.goto(f.as_uri())
            await page.evaluate("document.fonts.ready")
            await page.wait_for_timeout(300)
            el = await page.query_selector(".fold")
            png = OUT / "png" / (f.stem + ".png")
            await el.screenshot(path=str(png))
            im = Image.open(png).convert("RGB")
            im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS).save(OUT / (f.stem + ".jpg"), quality=92, subsampling=0, optimize=True, progressive=True)
            im.resize((700, round(im.height * 700 / im.width)), Image.LANCZOS).save(OUT / "preview" / (f.stem + ".jpg"), quality=80)
            print("rendered", f.stem, im.size)
        await br.close()

asyncio.run(main(sys.argv[1:]))
