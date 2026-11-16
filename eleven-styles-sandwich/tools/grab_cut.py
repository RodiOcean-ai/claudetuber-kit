"""Cut a single object out of a generated photo whose background is NOT a clean green screen (the picture maker often
gives a dull green with a light patch). GrabCut, started from a box around everything that differs from the border
colour; then the biggest piece, holes filled, a soft 1.5 px edge, the green fringe pulled out, trimmed with padding.
Usage: py -3.13 tools/grab_cut.py <in.png> <out.png> [--check check.png] [--margin 0.03] [--iters 6]"""
import argparse
import cv2
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('inp'); ap.add_argument('out')
ap.add_argument('--check'); ap.add_argument('--margin', type=float, default=0.03); ap.add_argument('--iters', type=int, default=6)
ap.add_argument('--thresh', type=float, default=26.0)
ap.add_argument('--metal', action='store_true', help='thin steel objects (knives): keep neutral grey pixels and peanut-butter browns only')
a = ap.parse_args()

if a.metal:
    rgb0 = np.array(Image.open(a.inp).convert('RGB')).astype(int)
    R, G, B = rgb0[..., 0], rgb0[..., 1], rgb0[..., 2]
    neutral = (np.abs(R - G) < 20) & (np.abs(G - B) < 24) & (G - np.maximum(R, B) < 4)
    pbrown = (R > G) & (G > B) & (R - B > 55) & (R > 100)
    fg = (neutral | pbrown).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab_cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    i = 1 + int(np.argmax(st[1:, 4])); fg = (lab_cc == i).astype(np.uint8)
    hh, ww = fg.shape
    ff = fg.copy() * 255; m2 = np.zeros((hh + 2, ww + 2), np.uint8); cv2.floodFill(ff, m2, (0, 0), 128); fg = (ff != 128).astype(np.uint8)
    alpha = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.2)
    rgba = np.dstack([rgb0.astype(np.uint8), (alpha * 255).astype(np.uint8)])
    ys, xs = np.where(alpha > 0.02); pad = 10
    x0, y0, x1, y1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(ww, xs.max() + pad), min(hh, ys.max() + pad)
    Image.fromarray(rgba).crop((x0, y0, x1, y1)).save(a.out)
    print(f'{a.out}: {x1 - x0}x{y1 - y0} (crop {x0},{y0}) [metal]')
    if a.check:
        cut = Image.open(a.out); W, H = cut.size
        sheet = Image.new('RGB', (W * 2, H), (30, 30, 30)); sheet.paste(Image.new('RGB', (W, H), (240, 240, 240)), (W, 0))
        sheet.paste(cut, (0, 0), cut); sheet.paste(cut, (W, 0), cut); sheet.thumbnail((900, 450)); sheet.save(a.check)
    raise SystemExit

rgb = np.array(Image.open(a.inp).convert('RGB'))
h, w = rgb.shape[:2]
lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
# background colour from the picture's border (a local median so a light gradient still counts as background)
bw = max(8, int(0.03 * min(h, w)))
border = np.concatenate([lab[:bw].reshape(-1, 3), lab[-bw:].reshape(-1, 3), lab[:, :bw].reshape(-1, 3), lab[:, -bw:].reshape(-1, 3)])
bg = np.median(border, 0)
dist = np.linalg.norm(lab - bg, axis=2)
rough = (dist > a.thresh).astype(np.uint8)
rough = cv2.morphologyEx(rough, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
n, lab_cc, st, _ = cv2.connectedComponentsWithStats(rough, 8)
if n > 1:
    i = 1 + int(np.argmax(st[1:, 4])); x, y, ww, hh = st[i][:4]
else:
    x, y, ww, hh = int(w * 0.1), int(h * 0.1), int(w * 0.8), int(h * 0.8)
m = int(a.margin * max(w, h))
rect = (max(1, x - m), max(1, y - m), min(w - 2, ww + 2 * m) - max(0, x - m - 1) * 0, min(h - 2, hh + 2 * m))
rect = (rect[0], rect[1], min(rect[2], w - rect[0] - 1), min(rect[3], h - rect[1] - 1))
mask = np.zeros((h, w), np.uint8)
bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, rect, bgd, fgd, a.iters, cv2.GC_INIT_WITH_RECT)
fg = ((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)).astype(np.uint8)
# the object's cast shadow on the green card is green-dominant; food and metal are not: drop green-dominant pixels
ri, gi, bi = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
fg[(gi - np.maximum(ri, bi)) > 6] = 0
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab_cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
if n > 1:
    i = 1 + int(np.argmax(st[1:, 4])); fg = (lab_cc == i).astype(np.uint8)
ff = fg.copy() * 255; m2 = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(ff, m2, (0, 0), 128); fg = (ff != 128).astype(np.uint8)
alpha = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.5)
# pull the green fringe out of the edge pixels
out = rgb.astype(np.float32)
edge = (alpha > 0.02) & (alpha < 0.98)
g_over = out[..., 1] - np.maximum(out[..., 0], out[..., 2])
fix = edge & (g_over > 0)
out[..., 1][fix] -= g_over[fix]
rgba = np.dstack([np.clip(out, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
ys, xs = np.where(alpha > 0.02)
pad = 10
x0, y0, x1, y1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(w, xs.max() + pad), min(h, ys.max() + pad)
Image.fromarray(rgba).crop((x0, y0, x1, y1)).save(a.out)
print(f'{a.out}: {x1 - x0}x{y1 - y0} (crop {x0},{y0})')
if a.check:
    cut = Image.open(a.out)
    W, H = cut.size
    sheet = Image.new('RGB', (W * 2, H), (30, 30, 30))
    sheet.paste(Image.new('RGB', (W, H), (240, 240, 240)), (W, 0))
    sheet.paste(cut, (0, 0), cut); sheet.paste(cut, (W, 0), cut)
    sheet.thumbnail((900, 450)); sheet.save(a.check)
