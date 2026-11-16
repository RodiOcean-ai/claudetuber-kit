"""Whiteboard tracer: turn a black-marker line drawing into ordered centre-line pen strokes.

  py -3.13 tools/wb_trace.py <drawing.png> <out_clean.png> <out.strokes.json> <check.png>

Steps: flatten the paper to pure white, binarize, drop specks, Zhang-Suen thinning (numpy), remove staircase pixels,
walk the skeleton graph into edges, prune short spurs, join edges straight through junctions, join strokes whose
ends nearly touch, drop bits under 12 px, smooth + Ramer-Douglas-Peucker (1.2 px), order like a person draws
(outer silhouette first, then long inner lines, then small details; each group chained nearest-next from top-left).
The stroke width is the median measured line thickness; "widths" (extra, optional) is each stroke's own measured
thickness. Check image: original | all strokes at strokeWidth | drawing order (blue first -> red last) | own widths.
"""
import json
import math
import sys

import cv2
import numpy as np

MIN_LEN = 12.0
RDP_EPS = 1.2


# ---------- image clean-up ----------
def clean_drawing(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
    # paper brightness estimate (lines are thin, so a big closing removes them)
    bg = cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    bg = cv2.GaussianBlur(bg, (0, 0), 15)
    norm = np.clip(img / np.maximum(bg, 1) * 255.0, 0, 255)
    # soft levels: <=95 black, >=175 white (keeps anti-aliasing, kills paper tint and light colour tints)
    soft = np.clip((norm - 95.0) / (175.0 - 95.0), 0, 1)
    ink = (cv2.GaussianBlur(norm, (0, 0), 1.0) < 140).astype(np.uint8)
    # drop specks (crumb dots, paper noise)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        keep[i] = a >= 120 and max(w, h) >= 16
    ink = keep[lab].astype(np.uint8)
    # fill pin-holes inside the ink
    inv = (1 - ink).astype(np.uint8)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    for i in range(1, n2):
        if st2[i][4] < 30:
            ink[lab2 == i] = 1
    # clean picture = soft levels, but specks removed (white where no kept ink nearby)
    near = cv2.dilate(ink, np.ones((5, 5), np.uint8))
    soft = np.where(near > 0, soft, 1.0)
    clean = (soft * 255).astype(np.uint8)
    return clean, ink


# ---------- thinning ----------
def zhang_suen(b):
    img = np.pad(b.astype(np.uint8), 1)
    while True:
        changed = False
        for step in (0, 1):
            P2 = img[:-2, 1:-1]; P3 = img[:-2, 2:]; P4 = img[1:-1, 2:]; P5 = img[2:, 2:]
            P6 = img[2:, 1:-1]; P7 = img[2:, :-2]; P8 = img[1:-1, :-2]; P9 = img[:-2, :-2]
            nb = [P2, P3, P4, P5, P6, P7, P8, P9]
            B = sum(x.astype(np.int32) for x in nb)
            seq = nb + [P2]
            A = sum(((seq[k] == 0) & (seq[k + 1] == 1)).astype(np.int32) for k in range(8))
            if step == 0:
                c1 = (P2 * P4 * P6) == 0
                c2 = (P4 * P6 * P8) == 0
            else:
                c1 = (P2 * P4 * P8) == 0
                c2 = (P2 * P6 * P8) == 0
            core = img[1:-1, 1:-1]
            m = (core == 1) & (B >= 2) & (B <= 6) & (A == 1) & c1 & c2
            if m.any():
                core[m] = 0
                changed = True
        if not changed:
            break
    return img[1:-1, 1:-1].astype(bool)


OFFS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]  # N NE E SE S SW W NW


def remove_staircase(sk):
    sk = sk.copy()
    H, W = sk.shape
    ys, xs = np.nonzero(sk)
    for y, x in zip(ys, xs):
        if y == 0 or x == 0 or y == H - 1 or x == W - 1 or not sk[y, x]:
            continue
        nb = [sk[y + dy, x + dx] for dy, dx in OFFS]
        if sum(nb) < 2:
            continue
        four = [nb[0], nb[2], nb[4], nb[6]]
        if sum(four) < 2:
            continue
        # number of 8-connected groups of neighbours around the ring (4-neighbours bridge diagonals)
        pts = [k for k in range(8) if nb[k]]
        seen, groups = set(), 0
        for p in pts:
            if p in seen:
                continue
            groups += 1
            stack = [p]
            seen.add(p)
            while stack:
                q = stack.pop()
                for r in pts:
                    if r in seen:
                        continue
                    dy = abs(OFFS[q][0] - OFFS[r][0]); dx = abs(OFFS[q][1] - OFFS[r][1])
                    if dy <= 1 and dx <= 1:
                        seen.add(r); stack.append(r)
        if groups == 1:
            sk[y, x] = False
    return sk


# ---------- graph walking ----------
def skeleton_edges(sk):
    H, W = sk.shape
    k = np.ones((3, 3), np.float32); k[1, 1] = 0
    deg = cv2.filter2D(sk.astype(np.float32), -1, k, borderType=cv2.BORDER_CONSTANT).astype(np.int32) * sk
    is_node = sk & (deg != 2)
    # cluster junction pixels into nodes
    nlab_n, nlab = cv2.connectedComponents(is_node.astype(np.uint8), connectivity=8)
    node_center = {}
    for i in range(1, nlab_n):
        yy, xx = np.nonzero(nlab == i)
        node_center[i] = (float(xx.mean()), float(yy.mean()))

    def nbrs(y, x):
        out = []
        for dy, dx in OFFS:
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and sk[yy, xx]:
                out.append((yy, xx))
        return out

    visited = np.zeros_like(sk)
    edges = []  # (points[(x,y)], node_a, node_b)
    ys, xs = np.nonzero(is_node)
    for y0, x0 in zip(ys, xs):
        na = nlab[y0, x0]
        for (y1, x1) in nbrs(y0, x0):
            if is_node[y1, x1] or visited[y1, x1]:
                continue
            path = [node_center[na], (float(x1), float(y1))]
            visited[y1, x1] = True
            prev, cur = (y0, x0), (y1, x1)
            nb_end = 0
            while True:
                cand = [p for p in nbrs(*cur) if p != prev]
                nodes = [p for p in cand if is_node[p] and not (nlab[p] == na and len(path) < 3)]
                if nodes:
                    nb_end = nlab[nodes[0]]
                    path.append(node_center[nb_end])
                    break
                nxt = [p for p in cand if not visited[p] and not is_node[p]]
                if not nxt:
                    break
                nxt.sort(key=lambda p: abs(p[0] - cur[0]) + abs(p[1] - cur[1]))
                p = nxt[0]
                visited[p] = True
                path.append((float(p[1]), float(p[0])))
                prev, cur = cur, p
            edges.append([path, na, nb_end])
    # pure loops (no nodes)
    ys, xs = np.nonzero(sk & ~is_node & ~visited)
    for y0, x0 in zip(ys, xs):
        if visited[y0, x0]:
            continue
        path = [(float(x0), float(y0))]
        visited[y0, x0] = True
        cur = (y0, x0)
        while True:
            nxt = [p for p in nbrs(*cur) if not visited[p]]
            if not nxt:
                break
            p = nxt[0]
            visited[p] = True
            path.append((float(p[1]), float(p[0])))
            cur = p
        path.append(path[0])
        edges.append([path, -1, -1])
    return edges, node_center


def plen(pts):
    a = np.asarray(pts)
    return float(np.sqrt((np.diff(a, axis=0) ** 2).sum(1)).sum()) if len(a) > 1 else 0.0


def end_dir(pts, at_start, look=12.0):
    """unit vector pointing OUT of the polyline at the given end"""
    seq = pts if at_start else pts[::-1]
    x0, y0 = seq[0]
    acc = 0.0
    px, py = x0, y0
    for (x, y) in seq[1:]:
        acc += math.hypot(x - px, y - py)
        px, py = x, y
        if acc >= look:
            break
    dx, dy = x0 - px, y0 - py
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def prune_spurs(edges, spur_len):
    for _ in range(3):
        deg = {}
        for e in edges:
            for n in (e[1], e[2]):
                if n > 0:
                    deg[n] = deg.get(n, 0) + 1
        out = []
        for e in edges:
            pts, a, b = e
            a_end = a > 0 and deg.get(a, 0) == 1
            b_end = b > 0 and deg.get(b, 0) == 1
            a_j = a > 0 and deg.get(a, 0) >= 3
            b_j = b > 0 and deg.get(b, 0) >= 3
            if ((a_end and b_j) or (b_end and a_j)) and plen(pts) < spur_len:
                continue
            out.append(e)
        if len(out) == len(edges):
            break
        edges = out
    return edges


def merge_at_nodes(edges):
    """join edges straight through nodes; returns list of polylines"""
    ends = {}  # node -> list of (edge idx, at_start)
    for i, (pts, a, b) in enumerate(edges):
        if a > 0:
            ends.setdefault(a, []).append((i, True))
        if b > 0:
            ends.setdefault(b, []).append((i, False))
    link = {}  # (i, at_start) -> (j, at_start)
    for n, lst in ends.items():
        lst = [e for e in lst]
        dirs = {e: end_dir(edges[e[0]][0], e[1]) for e in lst}
        pairs = []
        for u in range(len(lst)):
            for v in range(u + 1, len(lst)):
                if lst[u][0] == lst[v][0]:
                    continue
                d = dirs[lst[u]][0] * dirs[lst[v]][0] + dirs[lst[u]][1] * dirs[lst[v]][1]
                pairs.append((d, lst[u], lst[v]))
        pairs.sort()
        used = set()
        thr = 1.0 if len(lst) == 2 else -0.45  # a plain corner always joins; at forks only near-straight
        for d, u, v in pairs:
            if d > thr or u in used or v in used:
                continue
            used.add(u); used.add(v)
            link[u] = v; link[v] = u
    # chain edges
    done = set()
    polys = []
    for i in range(len(edges)):
        if i in done:
            continue
        # walk backwards from start end to find a chain head
        cur, cur_start = i, True
        seen = {i}
        while (cur, cur_start) in link:
            j, j_start = link[(cur, cur_start)]
            if j in seen:
                break
            seen.add(j)
            cur, cur_start = j, not j_start
        # now (cur, cur_start) is a free end (or loop): walk forward
        head, head_start = cur, cur_start
        chain = []
        e, entering_start = head, head_start
        while True:
            if e in done:
                break
            done.add(e)
            pts = edges[e][0] if entering_start else edges[e][0][::-1]
            chain.extend(pts if not chain else pts[1:])
            out_end = (e, not entering_start)
            if out_end not in link:
                break
            j, j_start = link[out_end]
            e, entering_start = j, j_start
        if chain:
            polys.append(chain)
    return polys


def join_close_ends(polys, gap):
    changed = True
    while changed:
        changed = False
        best = None
        for i in range(len(polys)):
            for j in range(i, len(polys)):
                for ai in (True, False):
                    for bj in (True, False):
                        if i == j and ai == bj:
                            continue
                        p = polys[i][0] if ai else polys[i][-1]
                        q = polys[j][0] if bj else polys[j][-1]
                        dist = math.hypot(p[0] - q[0], p[1] - q[1])
                        if i == j:
                            if dist < gap and plen(polys[i]) > 4 * gap and polys[i][0] != polys[i][-1]:
                                best = best if best and best[0] <= dist else (dist, i, j, ai, bj)
                            continue
                        if dist >= gap:
                            continue
                        da = end_dir(polys[i], ai); db = end_dir(polys[j], bj)
                        if da[0] * db[0] + da[1] * db[1] > -0.2:
                            continue
                        if best is None or dist < best[0]:
                            best = (dist, i, j, ai, bj)
        if best:
            _, i, j, ai, bj = best
            if i == j:
                polys[i] = polys[i] + [polys[i][0]]
            else:
                a = polys[i] if not ai else polys[i][::-1]  # a ends at the joining end
                b = polys[j] if bj else polys[j][::-1]      # b starts at the joining end
                polys[i] = a + b
                del polys[j]
            changed = True
    return polys


def smooth(pts, win=2):
    a = np.asarray(pts, float)
    if len(a) < 5:
        return a
    closed = np.hypot(*(a[0] - a[-1])) < 1.5
    out = a.copy()
    n = len(a)
    for k in range(n):
        if not closed and (k < win or k >= n - win):
            continue
        idx = [(k + d) % n if closed else k + d for d in range(-win, win + 1)]
        out[k] = a[idx].mean(0)
    if closed:
        out[-1] = out[0]
    return out


def rdp(a, eps):
    a = np.asarray(a, float)
    if len(a) < 3:
        return a
    keep = np.zeros(len(a), bool); keep[0] = keep[-1] = True
    stack = [(0, len(a) - 1)]
    while stack:
        s, e = stack.pop()
        if e <= s + 1:
            continue
        p, q = a[s], a[e]
        seg = q - p
        L = np.hypot(*seg)
        pts = a[s + 1:e]
        if L < 1e-9:
            d = np.hypot(*(pts - p).T)
        else:
            d = np.abs(seg[0] * (pts[:, 1] - p[1]) - seg[1] * (pts[:, 0] - p[0])) / L
        k = int(np.argmax(d))
        if d[k] > eps:
            m = s + 1 + k
            keep[m] = True
            stack.append((s, m)); stack.append((m, e))
    return a[keep]


def order_strokes(polys, ink, sw, wid):
    H, W = ink.shape
    # outside region = background reachable from the border
    bgm = (1 - ink).astype(np.uint8)
    ff = bgm.copy()
    mask = np.zeros((H + 2, W + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 2)
    outside = (ff == 2).astype(np.uint8)
    near_out = cv2.dilate(outside, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(sw * 2 + 3),) * 2))
    groups = {0: [], 1: [], 2: []}
    for p in polys:
        a = np.asarray(p)
        xi = np.clip(a[:, 0].round().astype(int), 0, W - 1); yi = np.clip(a[:, 1].round().astype(int), 0, H - 1)
        frac = near_out[yi, xi].mean()
        L = plen(p)
        g = 0 if frac > 0.6 else (1 if L > 120 else 2)
        groups[g].append(p)
    ordered = []
    pen = (0.0, 0.0)
    for g in (0, 1, 2):
        rest = list(groups[g])
        while rest:
            best, bi, brev = None, 0, False
            for i, p in enumerate(rest):
                for rev in (False, True):
                    s = p[-1] if rev else p[0]
                    # distance from the pen, with a pull towards top-left (reading order)
                    d = math.hypot(s[0] - pen[0], s[1] - pen[1]) + 0.25 * (s[0] + s[1]) * (1 if not ordered else 0)
                    if best is None or d < best:
                        best, bi, brev = d, i, rev
            p = rest.pop(bi)
            w = wid[id(p)]
            p = p[::-1] if brev else p
            ordered.append((p, w))
            pen = p[-1]
    return ordered


def main(src, out_clean, out_json, out_check):
    clean, ink = clean_drawing(src)
    H, W = ink.shape
    # thickness: distance transform sampled on the skeleton
    dist = cv2.distanceTransform(ink, cv2.DIST_L2, 5)
    sk = zhang_suen(ink)
    sk = remove_staircase(sk)
    th = 2.0 * dist[sk] - 1.0
    sw = float(np.median(th[th > 1])) if (th > 1).any() else 6.0
    edges, _ = skeleton_edges(sk)
    edges = prune_spurs(edges, spur_len=max(10.0, 1.6 * sw))
    polys = merge_at_nodes(edges)
    polys = join_close_ends(polys, gap=max(5.0, 0.9 * sw))
    polys = [p for p in polys if plen(p) >= MIN_LEN]
    simp, wid = [], {}
    for p in polys:
        s = rdp(smooth(p), RDP_EPS)
        if len(s) >= 2 and plen(s) >= MIN_LEN:
            q = [(float(x), float(y)) for x, y in s]
            a = np.asarray(p)
            xi = np.clip(a[:, 0].round().astype(int), 0, W - 1); yi = np.clip(a[:, 1].round().astype(int), 0, H - 1)
            d = dist[yi, xi]
            wid[id(q)] = max(2.0, float(np.median(2.0 * d[d > 0] - 1.0)) if (d > 0).any() else sw)
            simp.append(q)
    ordered = order_strokes(simp, ink, sw, wid)
    strokes = [[round(v, 1) for xy in p for v in xy] for p, _ in ordered]
    widths = [round(w, 1) for _, w in ordered]
    swr = round(sw, 1)
    json.dump({'w': W, 'h': H, 'strokeWidth': swr, 'strokes': strokes, 'widths': widths}, open(out_json, 'w'),
              separators=(',', ':'))
    ordered = [p for p, _ in ordered]
    cv2.imwrite(out_clean, clean)
    # check image: original | traced at stroke width | order (blue -> red)
    tr = np.full((H, W), 255, np.uint8)
    tr2 = np.full((H, W), 255, np.uint8)
    col = np.full((H, W, 3), 255, np.uint8)
    n = len(ordered)
    for k, p in enumerate(ordered):
        a = np.round(np.asarray(p) * 16).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(tr, [a], False, 0, int(round(sw)), cv2.LINE_AA, shift=4)
        cv2.polylines(tr2, [a], False, 0, max(2, int(round(widths[k]))), cv2.LINE_AA, shift=4)
        t = k / max(1, n - 1)
        c = (int(255 * (1 - t)), 60, int(255 * t))
        cv2.polylines(col, [a], False, c, max(2, int(round(sw * 0.6))), cv2.LINE_AA, shift=4)
        cv2.putText(col, str(k + 1), (int(p[0][0]) + 3, int(p[0][1]) - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    orig = cv2.cvtColor(cv2.imread(src, cv2.IMREAD_GRAYSCALE), cv2.COLOR_GRAY2BGR)
    check = np.hstack([orig, np.full((H, 12, 3), 80, np.uint8), cv2.cvtColor(tr, cv2.COLOR_GRAY2BGR),
                       np.full((H, 12, 3), 80, np.uint8), col, np.full((H, 12, 3), 80, np.uint8),
                       cv2.cvtColor(tr2, cv2.COLOR_GRAY2BGR)])
    cv2.imwrite(out_check, check)
    # coverage numbers
    trm = (tr < 128).astype(np.uint8)
    cov = (trm & cv2.dilate(ink, np.ones((3, 3), np.uint8))).sum() / max(1, trm.sum())
    hit = (ink & cv2.dilate(trm, np.ones((5, 5), np.uint8))).sum() / max(1, ink.sum())
    npts = sum(len(s) // 2 for s in strokes)
    print(f'{src}: strokeWidth {swr}px, {len(strokes)} strokes, {npts} points, '
          f'ink covered {hit:.1%}, strokes on ink {cov:.1%}')


if __name__ == '__main__':
    main(*sys.argv[1:5])
