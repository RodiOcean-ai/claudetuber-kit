"""Draw story-block curves: one panel per video, the line coloured by block (hook, wrong belief, "But" twist, escalation...).
Usage: python -I story_blocks.py <blocks.json> <out.png> [--title "..."]
blocks.json: [{"title": "...", "views": "255M", "duration": 31.1, "start_level": 3,
               "blocks": [[start_s, "HOOK", level_at_end], [7.0, "LADDER", 8.5], ...], "ours": false}, ...]
Levels are 0-11 "how much you need to keep watching", judged sentence by sentence from the transcript."""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # noqa: E402,F401
import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from scipy.interpolate import PchipInterpolator  # noqa: E402

C = {'HOOK': '#2e9e5b', 'BELIEF': '#9aa4b5', 'BUT': '#d64545', 'LADDER': '#e8a020', 'TEASE': '#c9a227', 'TENSION': '#e0602f',
     'SETBACK': '#1f5f8b', 'COMEBACK': '#1f8f8a', 'PAYOFF': '#7b3fb8', 'LOOP': '#d14f9a'}
NAME = {'HOOK': 'HOOK', 'BELIEF': 'WRONG BELIEF', 'BUT': '"BUT" TWIST', 'LADDER': 'ESCALATION', 'TEASE': 'TEASE', 'TENSION': 'TENSION',
        'SETBACK': 'SETBACK', 'COMEBACK': 'COMEBACK', 'PAYOFF': 'PAYOFF', 'LOOP': 'LOOP'}
LEGEND = [('HOOK', 'a "you" situation or a question'), ('BELIEF', '"you might think..."'), ('BUT', 'the reversal, 5-9 s in'),
          ('LADDER', 'each step bigger or stranger'), ('TEASE', '"the real reason is genius"'), ('TENSION', '"can\'t tell if it\'ll land"'),
          ('SETBACK', 'things get worse'), ('COMEBACK', 'it turns around'), ('PAYOFF', 'scale surprise, reveal or sting'), ('LOOP', 'back to frame one')]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--title', default='Story blocks')
    a = ap.parse_args()
    V = json.load(open(a.src, encoding='utf-8'))
    n = len(V) + 1; cols = 3; rows = (n + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(12.5, 3.4 * rows), dpi=130, squeeze=False)
    for ax, v in zip(axs.flat, V):
        bl = v['blocks']; d = v['duration']
        ts = [0] + [(bl[k + 1][0] if k + 1 < len(bl) else d) for k in range(len(bl))]
        ys = [v.get('start_level', 3)] + [b[2] for b in bl]
        f = PchipInterpolator(np.array(ts, float), np.array(ys, float)); xmax = max(d, 31)
        for k, (s, comp, _) in enumerate(bl):
            e = ts[k + 1]; x = np.linspace(s, e, 80); ax.plot(x, f(x), color=C[comp], lw=9, solid_capstyle='butt')
            xm = (s + e) / 2; ym = float(f(xm))
            dy = (float(f(min(e, xm + 0.8))) - float(f(max(s, xm - 0.8)))) / 9.5 * 4.0; dx = 1.6 / xmax * 4.8
            lab = NAME[comp] if (e - s) > 5 else NAME[comp].split()[-1] if (e - s) > 2.8 else ''
            if lab:
                ax.text(xm, ym, lab, ha='center', va='center', fontsize=6.3, color='white', fontweight='bold', rotation=np.degrees(np.arctan2(dy, dx)),
                        rotation_mode='anchor', path_effects=[pe.withStroke(linewidth=1.6, foreground=C[comp])])
        ax.set_xlim(0, xmax); ax.set_ylim(1.5, 11); ax.set_yticks([]); ax.tick_params(labelsize=8)
        ax.set_title(f'{v["title"]}  {v.get("views", "")}', fontsize=10, fontweight='bold', color='#e8641e' if v.get('ours') else '#1f2a44')
        ax.spines[['top', 'right', 'left']].set_visible(False)
    for ax in list(axs.flat)[len(V):]:
        ax.axis('off')
    ax = list(axs.flat)[len(V)]; ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    for k, (c, txt) in enumerate(LEGEND):
        yy = 0.95 - k * 0.095; ax.add_patch(plt.Rectangle((0, yy - 0.022), 0.07, 0.044, color=C[c]))
        ax.text(0.1, yy, f'{NAME[c]}: {txt}', fontsize=7.6, va='center')
    fig.suptitle(a.title, fontsize=15, fontweight='bold')
    plt.tight_layout(rect=(0, 0, 1, 0.97)); plt.savefig(a.out); print('saved', a.out)


if __name__ == '__main__':
    main()
