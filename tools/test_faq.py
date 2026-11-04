"""Check the FAQ chevron flips on open/close in odoo_description/preview.html (Bootstrap 5 accordion)."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
P = Path(__file__).resolve().parent.parent / "odoo_description" / "preview.html"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1300, "height": 900})
        await pg.goto(P.as_uri()); await pg.wait_for_load_state("networkidle")
        js = """i => getComputedStyle(document.querySelectorAll('#scita_faq .accordion-button')[i], '::after').transform"""
        print("Q1 open  :", await pg.evaluate(js, 0), "| Q2 closed:", await pg.evaluate(js, 1))
        await pg.click("#scita_faq_h2 a"); await pg.wait_for_timeout(600)
        print("after clicking Q2 -> Q1:", await pg.evaluate(js, 0), "| Q2:", await pg.evaluate(js, 1))
        await pg.click("#scita_faq_h2 a"); await pg.wait_for_timeout(600)
        print("after clicking Q2 again -> Q2:", await pg.evaluate(js, 1))
        await (await pg.query_selector("#scita_faq")).screenshot(path=str(P.parent.parent / "export" / "faq_test.png"))
        await b.close()
asyncio.run(main())
