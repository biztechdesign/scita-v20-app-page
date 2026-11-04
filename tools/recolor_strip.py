"""Recolor the navy Live Preview strip background to Scita hero teal, keeping the laptop renders."""
import sys, numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(np.float32) / 255
r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx, mn = a.max(-1), a.min(-1); L = (mx + mn) / 2
# navy / purple background: blue channel dominant and fairly dark
blueish = (b > r + 0.04) & (b > g + 0.04)
bg = blueish & (L < 0.55)
m = Image.fromarray((bg * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
m = np.asarray(m).astype(np.float32)[..., None] / 255
# target: teal #0F5C61 modulated by the original luminance (keeps glows / swirl lines)
teal = np.array([0x0F, 0x5C, 0x61], np.float32) / 255
lum = (0.3 * r + 0.59 * g + 0.11 * b)[..., None]
base_l = np.median(lum[bg]) if bg.any() else 0.1
new = np.clip(teal * (0.75 + 1.6 * (lum - base_l) / max(base_l, 1e-3) * 0.35), 0, 1)
res = a * (1 - m) + new * m
Image.fromarray((res * 255).astype(np.uint8)).save(out)
print("bg fraction", round(float(bg.mean()), 3))
