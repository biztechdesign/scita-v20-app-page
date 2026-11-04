"""Capture hi-res screenshots of the live Scita demo stores (replaces low-res crops from the old page).

  python tools/capture_demos.py
Writes assets/shots/<demo>_desktop.png (1440x900 @2x), <demo>_full.png (full page, @1x),
       <demo>_mobile.png (390x844 @3x), furniture_search.png (search dropdown open).
"""
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

async def settle(pg):
    try: await pg.wait_for_load_state("networkidle", timeout=25000)
    except Exception: pass
    # dismiss cookie / popup overlays if any
    for sel in ["text=Accept", "text=I agree", "button.btn-close", ".modal .close", "text=OK"]:
        try:
            el = await pg.query_selector(sel)
            if el and await el.is_visible(): await el.click(timeout=1500)
        except Exception: pass
    await pg.wait_for_timeout(2500)

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch()
        desk = await br.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        mob = await br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True,
                                   user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        for name, url in DEMOS.items():
            pg = await desk.new_page(); await pg.goto(url, timeout=60000); await settle(pg)
            await pg.screenshot(path=str(OUT / f"{name}_desktop.png"))
            # scroll through to trigger lazy content, then full page at 1x via a second page
            for y in range(0, 6000, 700):
                await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(250)
            await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(800)
            await pg.screenshot(path=str(OUT / f"{name}_full.png"), full_page=True)
            print(name, "desktop ok", await pg.title())
            await pg.close()
            pm = await mob.new_page(); await pm.goto(url, timeout=60000); await settle(pm)
            await pm.screenshot(path=str(OUT / f"{name}_mobile.png")); print(name, "mobile ok"); await pm.close()
        await br.close()

asyncio.run(main())
