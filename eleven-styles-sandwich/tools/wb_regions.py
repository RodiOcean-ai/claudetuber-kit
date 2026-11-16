"""Show the closed areas of a whiteboard drawing with numbers (to choose colour fills by eye).
  py -3.13 tools/wb_regions.py <clean drawing.png> <out preview.png>"""
import sys
import cv2
import numpy as np


def regions(clean, grow=2, min_area=250):
    ink = (clean < 140).astype(np.uint8)
    wall = cv2.dilate(ink, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats((1 - wall).astype(np.uint8), connectivity=4)
    H, W = clean.shape
    keep = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if x == 0 or y == 0 or x + w >= W or y + h >= H or a < min_area:
            continue
        keep.append(i)
    return lab, st, cen, keep


if __name__ == '__main__':
    clean = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
    lab, st, cen, keep = regions(clean)
    rng = np.random.default_rng(3)
    out = cv2.cvtColor(clean, cv2.COLOR_GRAY2BGR).astype(np.float32)
    for i in keep:
        c = rng.integers(120, 255, 3)
        out[lab == i] = out[lab == i] * 0.3 + c * 0.7
    out = out.astype(np.uint8)
    for i in keep:
        x, y = cen[i]
        cv2.putText(out, str(i), (int(x) - 12, int(y) + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 3)
        cv2.putText(out, str(i), (int(x) - 12, int(y) + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 1)
    cv2.imwrite(sys.argv[2], out)
    print(sys.argv[1], 'regions:', len(keep))
