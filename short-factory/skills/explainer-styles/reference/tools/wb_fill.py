"""Colour fills for the whiteboard drawings: flat soft marker colours flood-filled into closed areas (seed points
picked by eye from assets_work/wb/regions_<name>.png), black lines kept on top (multiply).

  py -3.13 tools/wb_fill.py            (does all six: public/img/wb/wb_<name>.png -> wb_<name>_color.png)
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from wb_regions import regions  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')
PAL = {'bread': '#F4D79B', 'crust': '#C98B3A', 'pb': '#A8642C', 'metal': '#D9DEE3', 'glass': '#DDEFF7',
       'plate': '#FFFFFF', 'board': '#D9A86C', 'label': '#FFFFFF', 'handle': '#B9C0C7'}

SEEDS = {
    'bread': {'bread': [(440, 650), (800, 690)],
              'crust': [(300, 400), (1020, 410), (280, 790), (1055, 810)]},
    'jar': {'metal': [(795, 300), (950, 1065), (945, 1003)],
            'pb': [(630, 668), (612, 1008), (430, 622), (835, 617), (625, 1070), (610, 495), (715, 495), (705, 545)],
            'glass': [(600, 450), (608, 528), (605, 562), (632, 595)],
            'label': [(632, 840)],
            'metal_box': [(770, 1085, 1120, 1185)]},
    'spread': {'crust': [(560, 318), (230, 730), (1010, 520), (910, 385), (338, 863), (1015, 630), (950, 685)],
               'pb': [(700, 450), (610, 470), (840, 560), (470, 655), (628, 712), (550, 572), (510, 590), (612, 615)],
               'metal': [(720, 640), (1075, 815), (895, 718), (1075, 865), (1215, 920)],
               },
    'stack': {'bread': [(670, 510)],
              'crust': [(232, 548), (1053, 590), (478, 742), (863, 740), (686, 795), (1068, 780), (480, 925), (868, 930)],
              'pb': [(243, 718), (335, 808), (611, 912), (826, 898), (990, 770), (560, 855), (1050, 690)],
              'pb_small': [(200, 640, 1130, 960)]},
    'cut': {'board': [(300, 600), (680, 1100)],
            'bread': [(750, 490), (550, 780)],
            'crust': [(720, 360), (510, 365), (545, 945), (780, 945)],
            'metal': [(660, 645), (785, 715), (810, 820), (530, 505)],
            'handle': [(360, 390)]},
    'halves': {'bread': [(463, 553), (850, 510)],
               'crust': [(452, 692), (465, 810), (728, 572), (740, 714), (972, 642), (970, 762), (672, 845)],
               'pb': [(347, 720), (410, 718), (585, 790), (602, 817), (733, 624), (942, 744), (988, 673)],
               'plate': [(200, 760), (448, 858), (786, 826), (597, 462), (668, 1000)],
               'pb_small': [(225, 630, 665, 835), (615, 555, 1085, 865)]},
}


def hex2bgr(h):
    h = h.lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


def fill(name):
    src = os.path.join(ROOT, 'public/img/wb', f'wb_{name}.png')
    clean = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
    lab, st, cen, keep = regions(clean, min_area=40)
    keep = set(keep)
    H, W = clean.shape
    canvas = np.full((H, W, 3), 255, np.float32)
    painted = np.zeros((H, W), bool)
    used = {}
    small = []
    for key, pts in SEEDS[name].items():
        if key.endswith('_small'):
            small.append((key, pts))
            continue
        if key.endswith('_box'):
            col = hex2bgr(PAL[key[:-4]])
            for (x0, y0, x1, y1) in pts:
                for i in keep:
                    cx, cy = cen[i]
                    if x0 <= cx <= x1 and y0 <= cy <= y1 and i not in used:
                        used[i] = key
            continue
        for (x, y) in pts:
            i = lab[y, x]
            if i == 0 or i not in keep:  # seed sits on a line: snap to the nearest closed area within 30 px
                r = 30
                win = lab[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]
                yy, xx = np.nonzero(np.isin(win, list(keep)))
                if len(yy):
                    k = np.argmin((yy - min(r, y)) ** 2 + (xx - min(r, x)) ** 2)
                    i = win[yy[k], xx[k]]
            if i == 0 or i not in keep:
                print(f'  {name}: seed {key} ({x},{y}) is not inside a closed area (label {i})')
                continue
            if i in used and used[i] != key:
                print(f'  {name}: area {i} seeded twice ({used[i]} and {key})')
            used[i] = key
    # small leftover areas (white slivers between filling lines) inside the given boxes
    for key, boxes in small:
        for (x0, y0, x1, y1) in boxes:
            for i in keep:
                cx, cy = cen[i]
                if i not in used and st[i][4] < 2500 and x0 <= cx <= x1 and y0 <= cy <= y1:
                    used[i] = key
    for i, key in used.items():
        col = hex2bgr(PAL[key.replace('_box', '').replace('_small', '')])
        m = lab == i
        # grow under the (dilated) lines so the colour meets the ink
        m = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~painted
        canvas[m] = col
        painted |= m
    line = clean.astype(np.float32)[..., None] / 255.0
    out = (canvas * line).clip(0, 255).astype(np.uint8)
    dst = os.path.join(ROOT, 'public/img/wb', f'wb_{name}_color.png')
    cv2.imwrite(dst, out)
    print(dst, 'areas filled:', len(used))


if __name__ == '__main__':
    for n in (sys.argv[1:] or SEEDS.keys()):
        fill(n)
