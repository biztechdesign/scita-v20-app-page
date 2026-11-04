"""Crop hi-res collage tiles from assets/shots (2x captures, 2880x1800). Boxes measured on 280px-wide previews."""
from PIL import Image
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "assets"
K = 2880 / 280
TILES = {
    "tile_electronics": ("electronics_s2", (12, 33, 268, 83)),
    "tile_categories":  ("furniture_s1", (8, 76, 272, 134)),
    "tile_products":    ("furniture_s2", (12, 0, 262, 172)),
    "tile_collection":  ("furniture_s3", (12, 22, 268, 158)),
    "tile_grocery":     ("grocery_s3",   (12, 40, 268, 174)),
    "tile_webtoprint":  ("webtoprint_s1", (4, 14, 268, 175)),
}
out = R / "shots" / "tiles"; out.mkdir(exist_ok=True)
for name, (src, box) in TILES.items():
    im = Image.open(R / "shots" / f"{src}.png").convert("RGB")
    b = tuple(round(v * K) for v in box); c = im.crop(b); c.save(out / f"{name}.png"); print(name, c.size)
