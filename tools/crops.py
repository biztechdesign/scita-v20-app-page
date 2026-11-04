"""Crop reusable assets from the current Scita v19 page images (assets/source -> assets/crops)."""
import sys, os
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
T = 700  # crop boxes below were measured on 700px-wide previews
def crop(name, src, box, frame=None):
    im = Image.open(os.path.join(SRC, src))
    if frame is not None: im.seek(frame)
    im = im.convert("RGB"); k = im.width / T
    b = tuple(int(v * k) for v in box)
    im.crop(b).save(os.path.join(OUT, name), quality=95); print(name, b)
crop("qr_electronics.png", "1.jpg", (30, 710, 86, 768))
crop("qr_webtoprint.png",  "1.jpg", (230, 1243, 288, 1302))
crop("qr_grocery.png",     "1.jpg", (325, 1288, 383, 1346))
crop("qr_furniture.png",   "1.jpg", (412, 1243, 470, 1302))
crop("qr_snippet.png",     "4.jpg", (606, 52, 660, 106))
crop("live_strip.png",     "1.jpg", (0, 1170, 700, 1720))
crop("search_screen.png",  "5.jpg", (0, 228, 432, 508))
crop("pwa_screen.png",     "6.jpg", (46, 216, 276, 596))
crop("megamenu_screen.png","4.gif", (116, 357, 584, 665), frame=0)
crop("tile_watch.png",     "7.jpg", (52, 506, 432, 603))
crop("tile_categories.png","7.jpg", (56, 634, 506, 712))
crop("tile_products.png",  "7.jpg", (56, 748, 306, 976))
crop("tile_photos.png",    "7.jpg", (320, 728, 646, 853))
crop("tile_grocery.png",   "7.jpg", (404, 880, 646, 980))
crop("prod_vinegar.png",   "3.jpg", (330, 220, 432, 290))
crop("prod_chips.png",     "3.jpg", (436, 220, 538, 290))
crop("prod_choco.png",     "3.jpg", (542, 220, 650, 290))
crop("prod_tajin.png",     "2.jpg", (470, 40, 620, 140))

# QR codes: grow the box, then snap to the white card
import numpy as np
def snap_qr(name, src, box, pad=14):
    im = Image.open(os.path.join(SRC, src)).convert("RGB"); k = im.width / T
    b = [int(v * k) for v in box]; b = [b[0]-pad, b[1]-pad, b[2]+pad, b[3]+pad]
    c = im.crop(b); a = np.asarray(c.convert("L")) > 215
    rows = np.where(a.mean(1) > 0.35)[0]; cols = np.where(a.mean(0) > 0.35)[0]
    c = c.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
    # inset a few px to drop the rounded-corner anti-aliasing
    c = c.crop((3, 3, c.width - 3, c.height - 3)); c.save(os.path.join(OUT, name)); print("snap", name, c.size)
snap_qr("qr_electronics.png", "1.jpg", (26, 704, 94, 774), pad=4)
snap_qr("qr_webtoprint.png",  "1.jpg", (230, 1243, 288, 1302))
snap_qr("qr_grocery.png",     "1.jpg", (325, 1288, 383, 1346))
snap_qr("qr_furniture.png",   "1.jpg", (412, 1243, 470, 1302))
