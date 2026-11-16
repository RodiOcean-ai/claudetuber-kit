"""Finish a generated thumbnail locally (the thumbnail-design finishing steps) and preview it on a mock YouTube home page.
Usage: python -I thumb_finish.py <in.jpg|png> <out.jpg> [options]
  --text "20M VIEWS"         headline across the top third (bold caps, dark outline, outer glow)
  --text-area x,y,w          put the headline in a box instead (fractions: left, top, max width), e.g. 0.03,0.05,0.55 to keep it off a hero on the right
  --bright 1.0               overall brightness lift before the text (1.1 = 10 % brighter)
  --text "STOP|POSTING"      a | stacks lines (each sized to fill the width, all in the text colour)
  --tilt 4                   tilt the headline N degrees (positive = anticlockwise) for drama
  --size-max 420             largest letter size for a one-line headline (raise it for narrow fonts so they fill the width)
  --stretch 1.3              make the letters taller (vertical stretch from the top of the text), for a blockier look
  --front mask.png           white = subject drawn IN FRONT of the headline (the text-behind-the-character look)
  --font <ttf>               headline font (default Impact: blocky and tall, owner's pick 7 Nov 2026; Montserrat Black was the wide option)
  --main "#FEF401"           text colour, top of the letters (owner's house style: lemon yellow with an ORANGE glow, always)
  --main2 "#FFE400"          text colour at the bottom of the letters (soft vertical gradient)
  --extrude 0.07             3D edge dropping down-right, as a fraction of the letter size (0 = flat)
  --edge "#B04800"           colour of that 3D edge     --outline 0   dark outline width in px (0 = none, the house look)
  --glow "#FF8A1F"           glow colour (orange)                   --glow-size 18
  --darken x,y,w,h[;...]     soft dark patch(es) behind text/face (fractions 0-1 of width/height); the text area is darkened automatically
  --hue 15                   shift the background hue by N degrees  --sat 1.15  --contrast 1.08   (final colour pass)
  --pixelate x,y,w,h         pixelate the hidden detail (fractions)  --blur x,y,w,h  Gaussian blur instead
  --light x,y,r,"#FF8A3D"    soft coloured light blended as overlay (fractions; r = fraction of width)
  --keep-case                keep the text's own letter case (default: CAPITALS)
  --preview "Video title"    also write <out>_preview.jpg: the thumbnail among 8 others at home-page size, plus a 160 px copy
  --others <folder>          thumbnails to surround it with in the preview (default: the study's thumbs folder)"""
import argparse, glob, os, random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageChops
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out')
HOUSE = 'C:/Windows/Fonts/impact.ttf'
ap.add_argument('--text'); ap.add_argument('--font', default=HOUSE if os.path.exists(HOUSE) else sfconfig.FONTS['caption'])
ap.add_argument('--text-area'); ap.add_argument('--bright', type=float, default=1.0); ap.add_argument('--tilt', type=float, default=0)
ap.add_argument('--front'); ap.add_argument('--stretch', type=float, default=1.0); ap.add_argument('--size-max', type=int, default=420)
ap.add_argument('--main', default='#FEF401'); ap.add_argument('--main2', default='#FFE400')
ap.add_argument('--extrude', type=float, default=0.07); ap.add_argument('--edge', default='#B04800'); ap.add_argument('--outline', type=int, default=0); ap.add_argument('--glow', default='#FF8A1F'); ap.add_argument('--glow-size', type=int, default=18)
ap.add_argument('--darken'); ap.add_argument('--hue', type=float, default=0); ap.add_argument('--sat', type=float, default=1.12)
ap.add_argument('--contrast', type=float, default=1.06); ap.add_argument('--pixelate'); ap.add_argument('--blur'); ap.add_argument('--light')
ap.add_argument('--keep-case', action='store_true');  # keep the text as typed (e.g. a lowercase command like </make a video>)
ap.add_argument('--preview'); ap.add_argument('--others', default=os.path.join(sfconfig.REFERENCE, 'creators', 'faceless-channel', 'thumbs'))
a = ap.parse_args()

im = Image.open(a.src).convert('RGB').resize((1920, 1080), Image.LANCZOS)
W, H = im.size
box = lambda s: [float(v) for v in s.split(',')]
px = lambda b: (int(b[0] * W), int(b[1] * H), int((b[0] + b[2]) * W), int((b[1] + b[3]) * H))

if a.hue:                                            # background colour shift (whole image; text is drawn after)
    hsv = im.convert('HSV'); h, s, v = hsv.split()
    h = h.point(lambda x: (x + int(a.hue / 360 * 255)) % 256)
    im = Image.merge('HSV', (h, s, v)).convert('RGB')
for opt, fn in ((a.pixelate, 'pix'), (a.blur, 'blur')):
    if opt:
        r = px(box(opt)); reg = im.crop(r)
        reg = reg.resize((max(1, reg.width // 28), max(1, reg.height // 28)), Image.NEAREST).resize(reg.size, Image.NEAREST) if fn == 'pix' \
            else reg.filter(ImageFilter.GaussianBlur(28))
        im.paste(reg, r[:2])

patches = [box(p) for p in a.darken.split(';')] if a.darken else []
TA = box(a.text_area) if a.text_area else None
if a.text and not a.front:                          # no dark patch when the subject sits in front (it would dim the subject)
    patches.append([TA[0], max(0, TA[1] - 0.06), TA[2], 0.36] if TA else [0.08, 0.0, 0.84, 0.36])
if patches:                                           # big soft brush at low strength, on its own layer
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for b in patches:
        d.ellipse(px(b), fill=150)
    m = m.filter(ImageFilter.GaussianBlur(W // 18))
    im = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, m)

if a.light:                                           # light reflection, overlay blend
    x, y, r, col = a.light.split(',')
    L = Image.new('RGB', (W, H), (128, 128, 128)); d = ImageDraw.Draw(L)
    cx, cy, rr = float(x) * W, float(y) * H, float(r) * W
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    L = L.filter(ImageFilter.GaussianBlur(rr / 2))
    im = ImageChops.overlay(im, L)

im = ImageEnhance.Brightness(im).enhance(a.bright)
im = ImageEnhance.Color(im).enhance(a.sat)
im = ImageEnhance.Contrast(im).enhance(a.contrast)

if a.text:
    # "STOP|POSTING" stacks lines: each line is sized to fill the width, all in the main colour
    under = im.copy()
    lines = [s.strip() if a.keep_case else s.strip().upper() for s in a.text.split('|')]
    maxw = W * (TA[2] if TA else 0.86)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(shade)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
    y = (TA[1] * H) if TA else H * 0.06
    for k, t in enumerate(lines):
        size = 420 if len(lines) > 1 else a.size_max
        font = ImageFont.truetype(a.font, size)
        while d.textlength(t, font=font) > maxw and size > 60:
            size -= 6; font = ImageFont.truetype(a.font, size)
        tw = d.textlength(t, font=font)
        x0 = (TA[0] * W + (maxw - tw) / 2) if TA else (W - tw) / 2
        ex = int(size * a.extrude)
        ds.text((x0 + size * 0.05 + ex, y + size * 0.06 + ex), t, font=font, fill=(0, 0, 0, 230), stroke_width=12, stroke_fill=(0, 0, 0, 230))
        dg.text((x0, y), t, font=font, fill=a.glow, stroke_width=14, stroke_fill=a.glow)
        edge = Image.new('RGB', (1, 1), a.edge).getpixel((0, 0))
        for i in range(ex, 0, -1):                    # 3D edge: stacked copies, darker further back
            f = 0.55 + 0.45 * (1 - i / max(ex, 1))
            d.text((x0 + i * 0.6, y + i), t, font=font, fill=tuple(int(c * f) for c in edge) + (255,))
        if a.outline:
            d.text((x0, y), t, font=font, fill='#111111', stroke_width=a.outline, stroke_fill='#111111')
        fm_ = Image.new('L', (W, H), 0); ImageDraw.Draw(fm_).text((x0, y), t, font=font, fill=255)
        top, bot = Image.new('RGB', (1, 1), a.main).getpixel((0, 0)), Image.new('RGB', (1, 1), a.main2).getpixel((0, 0))
        g = Image.new('RGBA', (1, 256))
        for r in range(256):
            u = r / 255; g.putpixel((0, r), tuple(int(top[c] + (bot[c] - top[c]) * u) for c in range(3)) + (255,))
        bb = fm_.getbbox() or (0, 0, W, H)
        grad = Image.new('RGBA', (W, H), (0, 0, 0, 0)); grad.paste(g.resize((W, bb[3] - bb[1])), (0, bb[1]))
        layer = Image.composite(grad, layer, fm_); d = ImageDraw.Draw(layer)
        y += size * 1.02
    if a.stretch != 1:                                # taller letters, anchored at the top of the text
        t0 = (TA[1] * H) if TA else H * 0.06
        aff = (1, 0, 0, 0, 1 / a.stretch, t0 * (1 - 1 / a.stretch))
        shade, glow, layer = (L.transform((W, H), Image.AFFINE, aff, resample=Image.BICUBIC) for L in (shade, glow, layer))
        y = t0 + (y - t0) * a.stretch
    shade = shade.filter(ImageFilter.GaussianBlur(10))
    glow = glow.filter(ImageFilter.GaussianBlur(a.glow_size))
    if a.tilt:
        cx, cy = (TA[0] + TA[2] / 2) * W if TA else W / 2, (TA[1] * H + y) / 2 if TA else H * 0.2
        shade, glow, layer = (L.rotate(a.tilt, resample=Image.BICUBIC, center=(cx, cy)) for L in (shade, glow, layer))
    im = im.convert('RGBA')
    for L in (shade, glow, glow, layer):
        im = Image.alpha_composite(im, L)
    im = im.convert('RGB')
    if a.front:                                       # put the subject back on top of the text
        fm = Image.open(a.front).convert('L').resize((W, H), Image.LANCZOS)
        im = Image.composite(under, im, fm)

im.save(a.out, quality=95)
print('saved', a.out)

if a.preview:                                         # mock home page: 3x3 grid at 360 px wide, ours in the middle
    others = [f for f in glob.glob(os.path.join(a.others, '*.jpg')) if 'all_thumbs' not in f and 'preview' not in f]
    random.seed(1); random.shuffle(others)
    labels = [os.path.splitext(os.path.basename(f))[0].replace('_', ' ') for f in others[:8]]  # the file name as the label
    tiles = [Image.open(f).convert('RGB') for f in others[:8]]
    tiles.insert(4, im); labels.insert(4, a.preview)
    tw_, th_ = 360, 203
    page = Image.new('RGB', (3 * tw_ + 4 * 24, 3 * (th_ + 70) + 24), (15, 15, 15)); d = ImageDraw.Draw(page)
    f2 = ImageFont.truetype(sfconfig.FONTS['bold'], 17)
    for i, t in enumerate(tiles):
        x, y = 24 + (i % 3) * (tw_ + 24), 24 + (i // 3) * (th_ + 70)
        page.paste(t.resize((tw_, th_), Image.LANCZOS), (x, y))
        words, rows = labels[i].split(), ['']             # wrap like YouTube: up to 2 lines
        for wd in words:
            if d.textlength((rows[-1] + ' ' + wd).strip(), font=f2) > tw_ and rows[-1]: rows.append(wd)
            else: rows[-1] = (rows[-1] + ' ' + wd).strip()
        for j, row in enumerate(rows[:2]):
            d.text((x, y + th_ + 8 + j * 22), row, font=f2, fill='white' if i == 4 else '#AAAAAA')
    base = os.path.splitext(a.out)[0]
    page.save(base + '_preview.jpg', quality=92)
    im.resize((160, 90), Image.LANCZOS).save(base + '_160px.png')
    print('preview', base + '_preview.jpg')
