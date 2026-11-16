"""Give a cut-out a hand-cut white paper border (magazine-collage look).

  py -3.13 tools/paper_border.py <cutout.png> <out_border.png> [--px 16] [--seed 1]

The alpha is grown by --px, its outline is turned into short straight scissor cuts (a simplified polygon with a
little random wobble), filled with off-white paper, and the cut-out is laid back on top.
"""
import argparse

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--px', type=int, default=16)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    im = cv2.imread(a.inp, cv2.IMREAD_UNCHANGED)
    pad = a.px + 12
    im = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    H, W = im.shape[:2]
    alpha = im[..., 3]
    hard = (alpha > 100).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * a.px + 1, 2 * a.px + 1))
    grown = cv2.dilate(hard, k)
    # close small notches so the paper outline is a simple shape, like scissors would cut
    grown = cv2.morphologyEx(grown, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    cnts, _ = cv2.findContours(grown, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    paper = np.zeros((H, W), np.uint8)
    for c in cnts:
        if cv2.contourArea(c) < 200:
            continue
        poly = cv2.approxPolyDP(c, 3.5, True).reshape(-1, 2).astype(np.float32)
        # scissor wobble: move each corner a little outwards/inwards
        cen = poly.mean(0)
        out = []
        for p in poly:
            d = p - cen
            n = d / (np.linalg.norm(d) + 1e-6)
            out.append(p + n * rng.uniform(-2.0, 3.0))
        cv2.fillPoly(paper, [np.round(np.array(out) * 8).astype(np.int32)], 255, cv2.LINE_AA, shift=3)
    paper_a = paper.astype(np.float32) / 255.0
    pa = cv2.GaussianBlur(paper_a, (0, 0), 0.6)
    # off-white paper with a faint grain
    grain = rng.normal(0, 3.0, (H, W)).astype(np.float32)
    paper_rgb = np.dstack([np.full((H, W), 240, np.float32) + grain, np.full((H, W), 245, np.float32) + grain,
                           np.full((H, W), 247, np.float32) + grain])  # BGR, warm off-white
    fa = im[..., 3:4].astype(np.float32) / 255.0
    rgb = im[..., :3].astype(np.float32) * fa + paper_rgb * (1 - fa)
    out_a = np.maximum(pa, fa[..., 0])
    res = np.dstack([np.clip(rgb, 0, 255), out_a * 255]).astype(np.uint8)
    ys, xs = np.nonzero(res[..., 3] > 5)
    res = res[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
    cv2.imwrite(a.out, res)
    print(a.out, f'{res.shape[1]}x{res.shape[0]}')


if __name__ == '__main__':
    main()
