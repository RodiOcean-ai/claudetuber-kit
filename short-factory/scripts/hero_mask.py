"""Mask of the hero (beige block head + green hoodie + what they enclose) right of x0 (fraction).
Usage: hero_mask.py <in> <out_mask.png> 0.48  -> use with thumb_finish.py --front
The head is traced as one smooth convex outline (it's a block), including its pale shiny rim, and drawn
anti-aliased so the edge over the headline is clean, not jagged."""
import sys, cv2, numpy as np
src, out, x0 = sys.argv[1], sys.argv[2], float(sys.argv[3])
W, H_ = 1920, 1080
im = cv2.resize(cv2.imread(src), (W, H_), interpolation=cv2.INTER_LANCZOS4)
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
H, S, V = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
beige = (H >= 3) & (H <= 30) & (S >= 25) & (V >= 90)
pale = (V >= 150) & (S < 80)                                  # the shiny rim and highlights of the head
green = (H >= 35) & (H <= 78) & (S >= 60) & (V >= 45)
left = int(x0 * W)

# head: the topmost big beige/pale blob, replaced by its convex outline
hm = ((beige | pale).astype(np.uint8) * 255); hm[:, :left] = 0
hm = cv2.morphologyEx(hm, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lbl, st, _ = cv2.connectedComponentsWithStats(hm)
cands = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 20000]
head = min(cands, key=lambda i: st[i, cv2.CC_STAT_TOP])
pts = cv2.findNonZero((lbl == head).astype(np.uint8))
hull = cv2.convexHull(pts)
big = np.zeros((H_ * 4, W * 4), np.uint8)                     # draw at 4x, shrink = smooth edge
cv2.fillPoly(big, [hull * 4], 255, lineType=cv2.LINE_AA)
headm = cv2.resize(cv2.erode(big, np.ones((9, 9), np.uint8)), (W, H_), interpolation=cv2.INTER_AREA)  # pull in ~1 px: drops the dark background fringe

# body: hoodie and whatever it encloses (hands, tank)
bm = (green.astype(np.uint8) * 255); bm[:, :left] = 0
bm = cv2.morphologyEx(bm, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
n, lbl, st, _ = cv2.connectedComponentsWithStats(bm)
bm = (lbl == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
m = cv2.morphologyEx(bm | (headm > 127).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
ff = m.copy(); cv2.floodFill(ff, np.zeros((H_ + 2, W + 2), np.uint8), (5, 5), 255); m = m | cv2.bitwise_not(ff)
m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (0, 0), 1.2)
m = np.maximum(m, headm)                                       # keep the head's smooth edge exactly
cv2.imwrite(out, m)
prev = im.copy(); prev[m < 128] = (prev[m < 128] * 0.3).astype(np.uint8); prev[m < 128, 2] = 170
cv2.imwrite(out.replace('.png', '_check.jpg'), cv2.resize(prev, (960, 540)))
