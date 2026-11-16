"""Measure how the camera moves in a video (the format benchmark's Shorts vs ours).
Usage: python camera_motion.py <out.json> <video.mp4> [<video.mp4> ...]
Per frame pair it tracks ~200 background points and fits one similarity transform (shift, zoom, turn): that is the
camera's move. Each frame is then labelled:
  still  - the picture stands still (shift < 2 % of the width a second, zoom < 1 %/s, turn < 1 deg/s)
  drift  - a slow, steady move (push-in, pull-out, pan, slow orbit)
  fast   - a quick flight or swipe (shift > 60 % of the width a second, or zoom > 40 %/s)
  cut    - the tracking breaks (a hard cut or a full-frame flash)
Prints one line per video and writes all numbers to <out.json>."""
import json, math, sys
import cv2, numpy as np

W = 180  # analysis width in pixels


def measure(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    ok, frame = cap.read()
    if not ok:
        return None
    h = int(frame.shape[0] * W / frame.shape[1])
    prev = cv2.cvtColor(cv2.resize(frame, (W, h)), cv2.COLOR_BGR2GRAY)
    rows = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(frame, (W, h)), cv2.COLOR_BGR2GRAY)
        diff = float(np.mean(cv2.absdiff(g, prev)))
        pts = cv2.goodFeaturesToTrack(prev, maxCorners=200, qualityLevel=0.01, minDistance=6)
        label, sh, zm, tn = 'cut', 0.0, 0.0, 0.0
        if pts is not None and len(pts) >= 12:
            nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, pts, None, winSize=(15, 15), maxLevel=3)
            good = st.reshape(-1) == 1
            if good.sum() >= 12:
                M, inl = cv2.estimateAffinePartial2D(pts[good], nxt[good], method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if M is not None and inl is not None and inl.sum() >= 10:
                    s = math.hypot(M[0, 0], M[1, 0])
                    sh = math.hypot(M[0, 2], M[1, 2]) / W * fps      # share of the width per second
                    zm = abs(s - 1.0) * fps                          # zoom per second
                    tn = abs(math.degrees(math.atan2(M[1, 0], M[0, 0]))) * fps
                    label = None
        if label is None:
            if sh > 0.60 or zm > 0.40:
                label = 'fast'
            elif sh < 0.02 and zm < 0.01 and tn < 1.0:
                label = 'still'
            else:
                label = 'drift'
        if label == 'cut' and diff < 6:      # tracking failed on a flat frame, not a real cut
            label = 'still'
        rows.append((label, sh, zm, tn))
        prev = g
    cap.release()
    n = len(rows)
    dur = n / fps
    cnt = {k: sum(1 for r in rows if r[0] == k) for k in ('still', 'drift', 'fast', 'cut')}
    # events: runs of fast frames and cuts
    fast_runs, cut_events, run = 0, 0, False
    for r in rows:
        if r[0] == 'fast' and not run:
            fast_runs += 1
        run = r[0] == 'fast'
    prevl = None
    for r in rows:
        if r[0] == 'cut' and prevl != 'cut':
            cut_events += 1
        prevl = r[0]
    # longest stretch with the camera standing still
    longest, cur = 0, 0
    for r in rows:
        cur = cur + 1 if r[0] == 'still' else 0
        longest = max(longest, cur)
    drift = [r for r in rows if r[0] == 'drift']
    return {
        'video': path, 'seconds': round(dur, 1),
        'still_pct': round(100 * cnt['still'] / n, 1), 'moving_pct': round(100 * (cnt['drift'] + cnt['fast']) / n, 1),
        'drift_pct': round(100 * cnt['drift'] / n, 1), 'fast_pct': round(100 * cnt['fast'] / n, 1),
        'fast_moves_per_10s': round(10 * fast_runs / dur, 2), 'cuts_per_10s': round(10 * cut_events / dur, 2),
        'longest_still_s': round(longest / fps, 2),
        'drift_shift_median': round(float(np.median([r[1] for r in drift])), 3) if drift else 0,
        'drift_zoom_median': round(float(np.median([r[2] for r in drift])), 3) if drift else 0,
        'drift_turn_median': round(float(np.median([r[3] for r in drift])), 2) if drift else 0,
    }


if __name__ == '__main__':
    out, vids = sys.argv[1], sys.argv[2:]
    res = []
    for v in vids:
        r = measure(v)
        if r:
            res.append(r)
            name = v.replace('\\', '/').split('/')[-1][:40]
            print(f"{name:40s} {r['seconds']:5.1f}s  moving {r['moving_pct']:5.1f}%  still {r['still_pct']:5.1f}%  "
                  f"fast/10s {r['fast_moves_per_10s']:4.2f}  cuts/10s {r['cuts_per_10s']:4.2f}  longest still {r['longest_still_s']:4.2f}s  "
                  f"drift shift {r['drift_shift_median']:.3f} zoom {r['drift_zoom_median']:.3f}", flush=True)
    json.dump(res, open(out, 'w', encoding='utf-8'), indent=1)
