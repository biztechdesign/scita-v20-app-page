"""Extra demo captures: predictive search dropdown (furniture) and scrolled sections of each demo (for the collage)."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "shots"; OUT.mkdir(parents=True, exist_ok=True)
DEMOS = {
    "electronics": "https://theme-scita-v19.appjetty.com/",
    "grocery": "https://theme-scita-grocery-v19.appjetty.com/",
    "furniture": "https://theme-scita-furniture-v19.appjetty.com/",
    "webtoprint": "https://theme-scita-w2p-v19.appjetty.com/",
}

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        # predictive search
        pg = await ctx.new_page(); await pg.goto(DEMOS["furniture"], timeout=60000)
        try: await pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception: pass
        inp = None
        for sel in ["input[name='search']", "input.oe_search_box", "input[type='search']", "input[placeholder*='Search']"]:
            inp = await pg.query_selector(sel)
            if inp and await inp.is_visible(): break
        if inp:
            await inp.click(); await pg.keyboard.type("chai", delay=120); await pg.wait_for_timeout(3500)
            await pg.screenshot(path=str(OUT / "furniture_search.png")); print("search ok")
        else:
            print("search input not found")
        await pg.close()
        # scrolled sections
        for name, url in DEMOS.items():
            pg = await ctx.new_page(); await pg.goto(url, timeout=60000)
            try: await pg.wait_for_load_state("networkidle", timeout=20000)
            except Exception: pass
            await pg.wait_for_timeout(1500)
            for i, y in enumerate((800, 1600, 2400, 3200, 4000)):
                await pg.evaluate(f"""() => {{ const w = document.getElementById('wrapwrap');
                    if (w && w.scrollHeight > w.clientHeight) w.scrollTop = {y}; else window.scrollTo(0, {y}); }}""")
                await pg.wait_for_timeout(1800)
                await pg.screenshot(path=str(OUT / f"{name}_s{i+1}.png"))
            print(name, "sections ok"); await pg.close()
        await br.close()

asyncio.run(main())
