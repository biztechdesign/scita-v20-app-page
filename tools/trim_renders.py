"""Trim transparent margins from the curled-paper laptop renders -> assets/renders/laptop_<name>_t.png"""
from PIL import Image
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "assets" / "renders"
for f in sorted(R.glob("laptop_*.png")):
    if f.stem.endswith("_t"): continue
    im = Image.open(f).convert("RGBA"); a = im.getchannel("A").point(lambda v: 255 if v > 48 else 0)
    bb = a.getbbox(); pad = 40
    bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad))
    im.crop(bb).save(R / f"{f.stem}_t.png"); print(f.stem, bb)
