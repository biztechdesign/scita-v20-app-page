"""Build export/02-image-hotspot.gif from folds/02-image-hotspot.html.

Story (per client mockup): cursor clicks the teal hotspot -> product dialog opens with 3D preview
-> cursor drags to rotate -> cursor clicks the QR -> product is viewed in the room (AR).
  python tools/make_gif.py [--width 1288] [--frames-only]
"""
import sys, json, asyncio, urllib.parse
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "folds" / "02-image-hotspot.html"
OUT = ROOT / "export"; FR = OUT / "gif_frames"; FR.mkdir(parents=True, exist_ok=True)
WIDTH = int(sys.argv[sys.argv.index("--width") + 1]) if "--width" in sys.argv else 1288  # frames captured @2x, downscaled

def seq():
    """Yield (state, duration_ms)."""
    yield {"step": 0}, 900                                        # idle storefront
    for i in range(1, 9):                                         # move to sofa hotspot
        yield {"from": "rest", "to": "hs-sofa", "t": i / 8, "step": 0, "hot": 1 if i > 6 else 0}, 55
    for c in (0.4, 1.0, 0.6):                                     # click
        yield {"from": "hs-sofa", "to": "hs-sofa", "t": 1, "click": c, "step": 0}, 90
    for k in (0.35, 0.7, 1.0):                                    # dialog opens
        yield {"from": "hs-sofa", "to": "hs-sofa", "t": 1, "dialog": k, "step": 1}, 70
    yield {"from": "hs-sofa", "to": "hs-sofa", "t": 1, "dialog": 1, "step": 1}, 700
    for i in range(1, 7):                                         # move into 3D viewer
        yield {"from": "hs-sofa", "to": "viewer-l", "t": i / 6, "dialog": 1, "step": 1}, 55
    for i, ang in enumerate((1, 2)):                              # drag to rotate
        for j in range(1, 4):
            t = (i * 3 + j) / 6
            yield {"from": "viewer-l", "to": "viewer-r", "t": t, "dialog": 1, "angle": ang if j > 1 else (ang - 1), "step": 2, "click": 0.35}, 110
    yield {"from": "viewer-r", "to": "viewer-r", "t": 1, "dialog": 1, "angle": 2, "step": 2}, 650
    yield {"from": "viewer-r", "to": "viewer-r", "t": 1, "dialog": 1, "angle": 0, "step": 2}, 650
    for i in range(1, 9):                                         # move to QR
        yield {"from": "viewer-r", "to": "arbox", "t": i / 8, "dialog": 1, "angle": 0, "step": 2}, 55
    for c in (0.4, 1.0, 0.6):                                     # click QR
        yield {"from": "arbox", "to": "arbox", "t": 1, "dialog": 1, "click": c, "step": 3}, 90
    for k in (0.3, 0.6, 0.85, 1.0):                               # AR phone slides in
        yield {"from": "arbox", "to": "arbox", "t": 1, "dialog": 1, "ar": k, "step": 3}, 70
    yield {"from": "arbox", "to": "arbox", "t": 1, "dialog": 1, "ar": 1, "step": 3}, 2600

async def main():
    frames, durs = [], []
    async with async_playwright() as p:
        br = await p.chromium.launch()
        page = await (await br.new_context(viewport={"width": 1288, "height": 1000}, device_scale_factor=2)).new_page()
        for n, (state, ms) in enumerate(seq()):
            await page.goto(SRC.as_uri() + "?s=" + urllib.parse.quote(json.dumps(state)))
            await page.evaluate("document.fonts.ready"); await page.wait_for_timeout(60)
            f = FR / f"f{n:03d}.png"
            await (await page.query_selector(".fold")).screenshot(path=str(f))
            frames.append(f); durs.append(ms)
        await br.close()
    print("frames", len(frames))
    if "--frames-only" in sys.argv: return
    ims = []
    first = Image.open(frames[0]).convert("RGB")
    if WIDTH != first.width:
        sz = (WIDTH, round(first.height * WIDTH / first.width))
    else:
        sz = first.size
    # one shared palette from a few key frames keeps colours stable (no flicker between frames)
    key = [Image.open(frames[i]).convert("RGB").resize(sz, Image.LANCZOS) for i in sorted(set(range(0, len(frames), max(1, len(frames) // 8))) | {len(frames) - 1})]
    strip = Image.new("RGB", (sz[0], sz[1] * len(key)))
    for i, k in enumerate(key): strip.paste(k, (0, sz[1] * i))
    pal = strip.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE, kmeans=2)
    for f in frames:
        im = Image.open(f).convert("RGB").resize(sz, Image.LANCZOS)
        ims.append(im.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG))
    out = OUT / "02-image-hotspot.gif"
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("gif", out, sz, round(out.stat().st_size / 1e6, 2), "MB", "total", sum(durs) / 1000, "s")

asyncio.run(main())
