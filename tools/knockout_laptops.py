"""Cut the supplied Live Preview laptop artwork (white background, no alpha) out to a transparent PNG.

  python tools/knockout_laptops.py assets/source_extra/live_laptops.webp assets/renders/live_laptops.png [close_px]
Builds a silhouette (non-white pixels, small gaps closed, interior filled), feathers it, upscales 1.6x with a light sharpen.
"""
import sys, numpy as np, cv2
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 21
im = np.asarray(Image.open(src).convert("RGB")).astype(np.int16); h, w = im.shape[:2]
gray = im.mean(2)
fg = (gray < 253.5).astype(np.uint8) * 255                      # background is pure white (255)
edges = cv2.Canny(gray.astype(np.uint8), 3, 10)                 # faint paper borders
fg = cv2.bitwise_or(fg, cv2.dilate(edges, np.ones((3, 3), np.uint8)))
closed = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (K, K)))
ff = 255 - closed; m = np.zeros((h + 2, w + 2), np.uint8)
for x in range(0, w, 5):
    for y in (0, h - 1):
        if ff[y, x] == 255: cv2.floodFill(ff, m, (x, y), 128)
for y in range(0, h, 5):
    for x in (0, w - 1):
        if ff[y, x] == 255: cv2.floodFill(ff, m, (x, y), 128)
sil = np.where(ff == 128, 0, 255).astype(np.uint8)
sil = cv2.morphologyEx(sil, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))   # drop hairlines in the source art
# drop small islands (compression specks)
n, lab, stats, _ = cv2.connectedComponentsWithStats((sil > 0).astype(np.uint8), 8)
keep = np.zeros_like(sil)
for k in range(1, n):
    if stats[k, cv2.CC_STAT_AREA] > 4000: keep[lab == k] = 255
sil = keep
# edge band: real transparency from distance-to-white, then remove the white matte from colours
inner = cv2.erode(sil, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
band = (sil > 0) & (inner == 0)
alpha = (sil > 0).astype(np.float32)
alpha[band] = np.clip((255.0 - gray[band]) / 28.0, 0, 1) ** 0.7
alpha = cv2.GaussianBlur(alpha, (0, 0), 0.6) * (sil > 0)
col = im.astype(np.float32)
a3 = np.maximum(alpha, 0.04)[..., None]
col = np.clip((col - (1 - a3) * 255.0) / a3, 0, 255)
rgba = Image.fromarray(np.dstack([col, alpha * 255]).astype(np.uint8), "RGBA")
big = rgba.resize((round(w * 1.6), round(h * 1.6)), Image.LANCZOS)
rgb = big.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2)); rgb.putalpha(big.getchannel("A"))
rgb.save(out); print("ok", rgb.size)
