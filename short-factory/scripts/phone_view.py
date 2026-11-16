"""Two phone screens (390 pt wide, drawn at 2x): YouTube home feed (full-width covers) and the Up next list (small covers).
Usage: phone_view.py <our_cover.jpg> <folder of others named creator_x.jpg> <out.jpg> "Our title"   (other titles: edit TITLES)"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
ours, mix, out, title = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
F = 'C:/Windows/Fonts/'
def font(n, s):
    for f in n:
        if os.path.exists(F + f): return ImageFont.truetype(F + f, s)
med = lambda s: font(['Roboto-Medium.ttf', 'arialbd.ttf'], s); reg = lambda s: font(['Roboto-Regular.ttf', 'arial.ttf'], s)
K = 2; PW, PH = 390 * K, 844 * K
BG, SUB = (15, 15, 15), (170, 170, 170)
# Your comparison covers: any <channel>_<video>.jpg files in the folder (other creators' covers you saved for a private
# check). Optional in the same folder: titles.json {"<file name without .jpg>": "Video title"} and
# channels.json {"<channel>": "Channel name"}. Without them the file names are used as labels.
def _j(name):
    p = os.path.join(mix, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
TITLES, NAMES = _j('titles.json'), _j('channels.json')
COVERS = sorted(f[:-4] for f in os.listdir(mix) if f.lower().endswith('.jpg'))
if not COVERS:
    sys.exit('put a few other covers (.jpg) in ' + mix)
pick = lambda i: COVERS[i % len(COVERS)]
def item(key):
    if key == 'ours': return Image.open(ours).convert('RGB'), title, 'Our channel'
    return Image.open(os.path.join(mix, key + '.jpg')).convert('RGB'), TITLES.get(key, key.replace('_', ' ')), NAMES.get(key.split('_')[0], key.split('_')[0])
def wrap(d, t, f, w, n=2):
    rows = ['']
    for wd in t.split():
        if d.textlength((rows[-1] + ' ' + wd).strip(), font=f) > w and rows[-1]: rows.append(wd)
        else: rows[-1] = (rows[-1] + ' ' + wd).strip()
    return rows[:n]
def bar(d):
    d.rectangle((0, 0, PW, 92 * K), fill=BG); d.text((24 * K, 14 * K), '9:41', font=med(15 * K), fill='white'); d.text((16 * K, 56 * K), 'YouTube', font=med(20 * K), fill='white')
# 1) home feed: full-width covers
home = Image.new('RGB', (PW, PH), BG); d = ImageDraw.Draw(home)
y = 92 * K - 120 * K                                  # previous video partly scrolled off the top
for key in [pick(0), 'ours', pick(1)]:
    im, t, ch = item(key); th = int(PW * 9 / 16)
    home.paste(im.resize((PW, th), Image.LANCZOS), (0, y)); y += th + 12 * K
    d.ellipse((12 * K, y, 48 * K, y + 36 * K), fill=(80, 80, 80))
    for j, row in enumerate(wrap(d, t, med(15 * K), PW - 80 * K)):
        d.text((60 * K, y + j * 20 * K), row, font=med(15 * K), fill='white')
    d.text((60 * K, y + 44 * K), ch, font=reg(12 * K), fill=SUB); y += 84 * K
bar(d)
# 2) up next list: small covers under a playing video
nxt = Image.new('RGB', (PW, PH), BG); d = ImageDraw.Draw(nxt)
pv = item(pick(2))[0].resize((PW, int(PW * 9 / 16)), Image.LANCZOS); nxt.paste(pv, (0, 44 * K)); y = 44 * K + pv.height + 60 * K
d.text((12 * K, y - 44 * K), 'Up next', font=med(16 * K), fill='white')
for key in [pick(3), pick(0), 'ours', pick(4), pick(5), pick(6)]:
    im, t, ch = item(key); tw = 168 * K; th = int(tw * 9 / 16)
    nxt.paste(im.resize((tw, th), Image.LANCZOS), (12 * K, y))
    for j, row in enumerate(wrap(d, t, med(14 * K), PW - tw - 36 * K, 3)):
        d.text((tw + 24 * K, y + j * 18 * K), row, font=med(14 * K), fill='white')
    d.text((tw + 24 * K, y + 58 * K), ch, font=reg(12 * K), fill=SUB); y += th + 14 * K
d.rectangle((0, 0, PW, 44 * K), fill=BG); d.text((24 * K, 14 * K), '9:41', font=med(15 * K), fill='white')
sheet = Image.new('RGB', (PW * 2 + 60, PH + 40), (40, 40, 40))
for i, s in enumerate((home, nxt)):
    sheet.paste(s, (20 + i * (PW + 20), 20))
sheet.save(out, quality=92); print('saved', out)
