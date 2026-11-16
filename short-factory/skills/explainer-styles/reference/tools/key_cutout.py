"""Cut an object out of a generated picture (green screen, or white background as a fallback).

  py -3.13 tools/key_cutout.py <in.png> <out.png> [--mode green|white] [--keep all|1|2...] [--nodespill]
                               [--pad 10] [--check <check.png>] [--erode 0] [--minfrac 0.02]

green: alpha from how much greener than red/blue a pixel is (relative to the measured background), despill the
green fringe, feather ~1.5 px, keep the main component(s), trim with padding, save RGBA.
white: flood fill from the borders through near-white pixels, soft edge from the distance to white.
--check writes the cut-out composited on a dark and a light background side by side.
"""
import argparse

import cv2
import numpy as np


def largest_components(mask, keep, minfrac):
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    if n <= 1:
        return mask
    areas = st[1:, 4]
    order = np.argsort(-areas) + 1
    big = areas.max()
    if keep == 'all':
        ok = [i for i in order if st[i, 4] >= minfrac * big]
    else:
        ok = list(order[:int(keep)])
    return np.isin(lab, ok)


def fill_small_holes(mask, max_area):
    inv = (~mask).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    out = mask.copy()
    H, W = mask.shape
    for i in range(1, n):
        x, y, w, h, a = st[i]
        touches = x == 0 or y == 0 or x + w >= W or y + h >= H
        if not touches and a < max_area:
            out[lab == i] = True
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--mode', default='green')
    ap.add_argument('--keep', default='all')
    ap.add_argument('--minfrac', type=float, default=0.02)
    ap.add_argument('--nodespill', action='store_true')
    ap.add_argument('--pad', type=int, default=10)
    ap.add_argument('--erode', type=int, default=0)
    ap.add_argument('--holes', type=int, default=400, help='fill enclosed transparent holes smaller than this (px)')
    ap.add_argument('--check')
    a = ap.parse_args()

    bgr = cv2.imread(a.inp, cv2.IMREAD_COLOR).astype(np.float32)
    b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
    H, W = g.shape
    border = np.zeros((H, W), bool); border[:8] = border[-8:] = True; border[:, :8] = border[:, -8:] = True

    if a.mode == 'green':
        # how much greener than the other channels, relative to brightness (so green shadows still key out;
        # the floor of 60 keeps near-black objects like a marker opaque)
        key = (g - np.maximum(r, b)) / np.maximum(g, 60.0)
        bgk = float(np.median(key[border]))
        lo, hi = 0.30 * bgk, 0.70 * bgk
        alpha = 1.0 - np.clip((key - lo) / (hi - lo), 0, 1)
    else:  # white background: flood from borders through bright, low-saturation pixels
        bright = bgr.min(axis=2)
        sat = bgr.max(axis=2) - bgr.min(axis=2)
        cand = ((bright > 225) & (sat < 22)).astype(np.uint8)
        ff = cand.copy()
        m = np.zeros((H + 2, W + 2), np.uint8)
        for (x, y) in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (0, H // 2), (W - 1, H // 2), (W // 2, H - 1)]:
            if ff[y, x] == 1:
                cv2.floodFill(ff, m, (x, y), 2)
        bgm = ff == 2
        d = cv2.distanceTransform((~bgm).astype(np.uint8), cv2.DIST_L2, 3)
        alpha = np.clip(d / 2.0, 0, 1)

    hard = alpha > 0.5
    hard = largest_components(hard, a.keep, a.minfrac)
    hard = fill_small_holes(hard, a.holes)
    if a.erode:
        hard = cv2.erode(hard.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=a.erode).astype(bool)
    # soft alpha only in a thin band around the hard mask edge
    band = cv2.dilate(hard.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    inner = cv2.erode(hard.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    alpha = np.where(inner, 1.0, np.where(band, np.minimum(alpha, 1.0), 0.0))
    alpha = np.where(hard | band, alpha, 0.0)
    # feather ~1.5 px
    alpha = cv2.GaussianBlur(alpha.astype(np.float32), (0, 0), 0.9)
    alpha = np.where(inner, 1.0, alpha)

    out = bgr.copy()
    if a.mode == 'green' and not a.nodespill:
        mx = np.maximum(r, b)
        edge = cv2.dilate((alpha < 0.999).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        # full despill near the edge, gentle (only clear green cast) inside
        g_edge = np.minimum(g, mx)
        g_in = np.minimum(g, mx + 0.35 * np.maximum(g - mx, 0))
        out[..., 1] = np.where(edge, g_edge, np.where(g > mx + 6, g_in, g))
    out = np.clip(out, 0, 255).astype(np.uint8)
    rgba = np.dstack([out, (alpha * 255).round().astype(np.uint8)])

    ys, xs = np.nonzero(rgba[..., 3] > 8)
    x0, x1 = max(0, xs.min() - a.pad), min(W, xs.max() + 1 + a.pad)
    y0, y1 = max(0, ys.min() - a.pad), min(H, ys.max() + 1 + a.pad)
    crop = rgba[y0:y1, x0:x1]
    cv2.imwrite(a.out, crop)
    print(f'{a.out}: {crop.shape[1]}x{crop.shape[0]} (crop offset {x0},{y0})')

    if a.check:
        h, w = crop.shape[:2]
        al = crop[..., 3:4].astype(np.float32) / 255
        rgb = crop[..., :3].astype(np.float32)
        tiles = []
        for col in [(26, 26, 26), (242, 242, 242), (40, 90, 200)]:
            bgc = np.zeros_like(rgb); bgc[:] = col
            tiles.append((rgb * al + bgc * (1 - al)).astype(np.uint8))
            tiles.append(np.full((h, 10, 3), 128, np.uint8))
        cv2.imwrite(a.check, np.hstack(tiles[:-1]))


if __name__ == '__main__':
    main()
