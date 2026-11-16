"""Face bank for the blocky world: three sticker layers (brows, eyes, mouths), each a 4x4 atlas of 1024 px cells, plus
faces.json that names every cell and the 12 expressions. The head shader stacks the three layers and picks a cell per
layer from a keyframed number on the head, so faces can change, blink and talk frame by frame.
Run: python -I faces_bank.py [out_dir]   (default: ../../../assets/blocky)"""
import json, math, os, sys
from PIL import Image, ImageDraw

S = 2048                                   # draw size of one cell; saved at half (1024)
N = 4                                      # atlas is N x N cells
INK, WHITE, TEAR, BLUSH, TONGUE, SWEAT = (24, 22, 34, 255), (255, 255, 255, 255), (90, 190, 255, 255), (255, 110, 110, 95), (240, 90, 100, 255), (150, 215, 255, 255)
EX, EY = 330, 880                          # eye centres: +-EX from the middle, EY from the top
MY = 1290                                  # mouth centre height
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, '..', '..', '..', 'assets', 'blocky'))
C = S / 2


def ell(d, cx, cy, rx, ry, fill):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill)


def arc(d, cx, cy, w, h, a0, a1, th=58):
    d.arc((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), a0, a1, fill=INK, width=th)


def bar(d, x0, y0, x1, y1, th):
    d.line((x0, y0, x1, y1), fill=INK, width=th)
    for px, py in ((x0, y0), (x1, y1)):
        ell(d, px, py, th / 2, th / 2, INK)


# ---------------------------------------------------------------- brows
def brow(d, sx, tilt, lift=0, w=230, th=62):
    """tilt > 0 raises the inner end (sad, worried), < 0 lowers it (angry)."""
    cx, cy = C + sx * EX, EY - 270 - lift
    a = math.radians(tilt) * sx
    dx, dy = math.cos(a) * w / 2, math.sin(a) * w / 2
    bar(d, cx - dx, cy - dy, cx + dx, cy + dy, th)


def both(tilt, lift=0, w=230, th=62):
    return lambda d: [brow(d, sx, tilt, lift, w, th) for sx in (-1, 1)]


BROWS = {
    'neutral': both(4),
    'raised': both(10, lift=120),
    'angry': both(-24, lift=-60, w=260, th=72),
    'sad': both(22, lift=10),
    'confused': lambda d: (brow(d, -1, 4), brow(d, 1, -10, lift=140)),
    'smug': lambda d: (brow(d, -1, 0, lift=-40), brow(d, 1, 8, lift=70)),
    'determined': both(-12, lift=-30, th=70),
    'flat': both(0, lift=-20),
}


# ---------------------------------------------------------------- eyes
def ovals(d, rx=95, ry=150, look=(0, 0), shine=True):
    for sx in (-1, 1):
        cx = C + sx * EX + look[0]
        ell(d, cx, EY + look[1], rx, ry, INK)
        if shine:
            ell(d, cx + 30, EY + look[1] - 55, 34, 40, WHITE)


def wide(d, pupil=48):
    for sx in (-1, 1):
        cx = C + sx * EX
        ell(d, cx, EY, 165, 185, INK); ell(d, cx, EY, 125, 145, WHITE); ell(d, cx, EY + 10, pupil, pupil * 1.15, INK)


def blush(d):
    for sx in (-1, 1):
        ell(d, C + sx * 520, 1170, 120, 70, BLUSH)


def happy_eyes(d):
    for sx in (-1, 1):
        arc(d, C + sx * EX, EY + 60, 250, 260, 195, 345, th=68)
    blush(d)


def laugh_eyes(d):
    for sx in (-1, 1):                     # squeezed shut: > <
        cx = C + sx * EX; tip = cx + sx * -70
        bar(d, cx + sx * 80, EY - 90, tip, EY, 62); bar(d, tip, EY, cx + sx * 80, EY + 90, 62)
    blush(d)


def scared_eyes(d):
    wide(d, pupil=30)
    d.polygon([(C + 640, 560), (C + 590, 700), (C + 690, 700)], fill=SWEAT); ell(d, C + 640, 715, 52, 52, SWEAT)


def half_lid(d):
    for sx in (-1, 1):
        cx = C + sx * EX
        d.chord((cx - 100, EY - 130, cx + 100, EY + 150), 0, 180, fill=INK)
        bar(d, cx - 115, EY + 8, cx + 115, EY + 8, 44)


def squint(d):
    for sx, (a0, a1) in ((-1, (345, 215)), (1, (325, 195))):
        cx = C + sx * EX
        d.chord((cx - 95, EY - 140, cx + 95, EY + 140), a0, a1, fill=INK)


def crying(d):
    ovals(d, look=(0, 20))
    for sx in (-1, 1):
        cx = C + sx * EX
        d.rounded_rectangle((cx - 34, EY + 120, cx + 34, EY + 600), 34, fill=TEAR)


def closed(d):
    for sx in (-1, 1):
        arc(d, C + sx * EX, EY - 50, 240, 170, 20, 160, th=64)


def confused_eyes(d):
    ell(d, C - EX, EY, 95, 150, INK); ell(d, C - EX + 30, EY - 55, 34, 40, WHITE)
    ell(d, C + EX, EY + 10, 70, 105, INK); ell(d, C + EX + 22, EY - 30, 26, 30, WHITE)


EYES = {
    'open': ovals,
    'happy': happy_eyes,
    'wide': wide,
    'scared': scared_eyes,
    'half': half_lid,
    'squint': squint,
    'crying': crying,
    'closed': closed,
    'look_left': lambda d: ovals(d, look=(-55, 0)),
    'look_right': lambda d: ovals(d, look=(55, 0)),
    'laugh': laugh_eyes,
    'confused': confused_eyes,
}


# ---------------------------------------------------------------- mouths
def grin(d, w=260, h=420, tongue=True):
    d.chord((C - w, MY - 210, C + w, MY - 210 + h), 0, 180, fill=INK)
    if tongue:
        d.chord((C - w * 0.58, MY - 210 + h * 0.6, C + w * 0.58, MY - 210 + h * 0.98), 180, 360, fill=TONGUE)


def o_mouth(d, rx=120, ry=160, tongue=True):
    ell(d, C, MY + 40, rx, ry, INK)
    if tongue:
        ell(d, C, MY + 40 + ry * 0.35, rx * 0.58, ry * 0.42, TONGUE)


def gritted(d):
    d.rounded_rectangle((C - 250, MY - 70, C + 250, MY + 90), 60, fill=INK)
    d.rounded_rectangle((C - 200, MY - 35, C + 200, MY + 55), 30, fill=WHITE)
    for x in (-100, 0, 100):
        d.line((C + x, MY - 35, C + x, MY + 55), fill=INK, width=18)
    d.line((C - 200, MY + 10, C + 200, MY + 10), fill=INK, width=14)


def wail(d):
    d.chord((C - 230, MY - 20, C + 230, MY + 400), 180, 360, fill=INK)
    d.chord((C - 120, MY + 60, C + 120, MY + 200), 180, 360, fill=TONGUE)


def squiggle(d):
    pts = [(C - 200 + i * 10, MY + 30 + 45 * math.sin(i / 40 * 2 * math.pi * 1.5)) for i in range(41)]
    d.line(pts, fill=INK, width=52, joint='curve')
    for p in (pts[0], pts[-1]):
        ell(d, *p, 26, 26, INK)


MOUTHS = {
    'smile': lambda d: arc(d, C, MY - 20, 360, 200, 20, 160),
    'grin': grin,
    'laugh': lambda d: grin(d, w=320, h=560),
    'o': o_mouth,
    'small_o': lambda d: o_mouth(d, rx=70, ry=90, tongue=False),
    'gritted': gritted,
    'frown': lambda d: arc(d, C, MY + 110, 300, 200, 200, 340),
    'wail': wail,
    'smirk': lambda d: arc(d, C + 60, MY - 40, 300, 180, 10, 120),
    'squiggle': squiggle,
    'flat': lambda d: bar(d, C - 150, MY + 20, C + 150, MY + 20, 52),
    'talk_closed': lambda d: bar(d, C - 120, MY + 20, C + 120, MY + 20, 50),
    'talk_half': lambda d: d.chord((C - 170, MY - 60, C + 170, MY + 150), 0, 180, fill=INK),
    'talk_wide': lambda d: grin(d, w=230, h=360),
    'talk_o': lambda d: o_mouth(d, rx=95, ry=125),
}

EXPRESSIONS = {                            # name: (brows, eyes, mouth)
    'calm': ('neutral', 'open', 'smile'),
    'happy': ('neutral', 'happy', 'grin'),
    'laughing': ('raised', 'laugh', 'laugh'),
    'shocked': ('raised', 'wide', 'o'),
    'scared': ('sad', 'scared', 'small_o'),
    'angry': ('angry', 'squint', 'gritted'),
    'sad': ('sad', 'open', 'frown'),
    'crying': ('sad', 'crying', 'wail'),
    'smug': ('smug', 'half', 'smirk'),
    'confused': ('confused', 'confused', 'squiggle'),
    'sleepy': ('flat', 'half', 'flat'),
    'determined': ('determined', 'squint', 'flat'),
}
TALK = ['talk_closed', 'talk_half', 'talk_wide', 'talk_o']


def atlas(layer, out):
    assert len(layer) <= N * N, out
    big = Image.new('RGBA', (N * S // 2, N * S // 2), (0, 0, 0, 0))
    for i, (name, draw) in enumerate(layer.items()):
        cell = Image.new('RGBA', (S, S), (0, 0, 0, 0)); draw(ImageDraw.Draw(cell))
        big.alpha_composite(cell.resize((S // 2, S // 2), Image.LANCZOS), ((i % N) * S // 2, (i // N) * S // 2))
    big.save(out)
    return {name: i for i, name in enumerate(layer)}


def preview(index, out, skin=(242, 191, 140, 255), cell=320):
    """12 expressions, then the 4 talking mouths and a blink on the calm face (for checking by eye)."""
    layers = {k: Image.open(os.path.join(OUT, f'{k}.png')) for k in ('brows', 'eyes', 'mouths')}
    half = S // 2

    def crop(layer, i):
        return layers[layer].crop(((i % N) * half, (i // N) * half, (i % N + 1) * half, (i // N + 1) * half))
    rows = [(n, EXPRESSIONS[n]) for n in EXPRESSIONS] + [(m, ('neutral', 'open', m)) for m in TALK] + [('blink', ('neutral', 'closed', 'smile'))]
    cols = 6; sheet = Image.new('RGB', (cols * cell, -(-len(rows) // cols) * cell), (40, 44, 56))
    for k, (name, (b, e, m)) in enumerate(rows):
        face = Image.new('RGBA', (half, half), skin)
        for layer, key in (('brows', b), ('eyes', e), ('mouths', m)):
            face.alpha_composite(crop(layer, index[layer][key]))
        tile = face.resize((cell - 12, cell - 12)).convert('RGB')
        sheet.paste(tile, ((k % cols) * cell + 6, (k // cols) * cell + 6))
    sheet.save(out, quality=88)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    index = {k: atlas(v, os.path.join(OUT, f'{k}.png')) for k, v in (('brows', BROWS), ('eyes', EYES), ('mouths', MOUTHS))}
    json.dump({'grid': N, **index, 'expressions': EXPRESSIONS, 'talk': TALK, 'blink': 'closed'},
              open(os.path.join(OUT, 'faces.json'), 'w'), indent=1)
    preview(index, os.path.join(OUT, 'faces_preview.jpg'))
    print('face bank:', {k: len(v) for k, v in index.items()}, '->', OUT)
