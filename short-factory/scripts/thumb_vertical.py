"""Finish a vertical (9:16) Shorts thumbnail: crop/resize to 1080x1920 and add 1-2 short glowing lines (our first episode's look:
a yellow number line, a white question line, thick dark outline, warm glow), plus a phone-size preview to check it reads.
Usage: python -I thumb_vertical.py <in image> <out.jpg> --line1 "13 BILLION" [--line2 "WHO?"] [--top 0.17] [--gap 0.12]
       [--color1 #ffd21f] [--color2 #ffffff] [--glow #ff9a1f]
Writes <out.jpg> and <out>_phone.jpg (the size a viewer sees in the feed). Keep it to 0-3 words per line."""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

W, H = 1080, 1920


def cover(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def fit_font(text, max_w, size):
    while size > 40:
        f = ImageFont.truetype(sfconfig.FONTS['headline'], size)
        if ImageDraw.Draw(Image.new('L', (1, 1))).textlength(text, font=f) <= max_w:
            return f
        size -= 6
    return ImageFont.truetype(sfconfig.FONTS['headline'], size)


def line(base, text, cy, color, glow, size):
    f = fit_font(text, W * 0.9, size); stroke = max(6, f.size // 13)
    g = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.text((W / 2, cy), text, font=f, anchor='mm', fill=glow, stroke_width=stroke * 3, stroke_fill=glow)
    base.alpha_composite(g.filter(ImageFilter.GaussianBlur(f.size // 5)))        # the warm glow behind the letters
    d = ImageDraw.Draw(base)
    d.text((W / 2, cy), text, font=f, anchor='mm', fill=color, stroke_width=stroke, stroke_fill='#2a1408')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--line1', required=True)
    ap.add_argument('--line2', default=''); ap.add_argument('--top', type=float, default=0.17); ap.add_argument('--gap', type=float, default=0.12)
    ap.add_argument('--color1', default='#ffd21f'); ap.add_argument('--color2', default='#ffffff'); ap.add_argument('--glow', default='#ff9a1f')
    a = ap.parse_args()
    for l in (a.line1, a.line2):
        if len(l.split()) > 3:
            print(f'  WARNING: "{l}" has more than 3 words; it will be hard to read in the feed')
    im = cover(Image.open(a.src).convert('RGB')).convert('RGBA')
    line(im, a.line1.upper(), H * a.top, a.color1, a.glow, 170)
    if a.line2:
        line(im, a.line2.upper(), H * (a.top + a.gap), a.color2, a.glow, 170)
    im = im.convert('RGB'); im.save(a.out, quality=93)
    phone = os.path.splitext(a.out)[0] + '_phone.jpg'
    im.resize((180, 320), Image.LANCZOS).save(phone, quality=90)
    print('saved', a.out, 'and the feed-size preview', phone)


if __name__ == '__main__':
    main()
