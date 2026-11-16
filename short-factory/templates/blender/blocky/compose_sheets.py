"""Lays out cast_sheets.py renders: one character sheet per cast member (turnaround on top, three faces below, name and role),
plus the lineup and the talking/blinking strip.  Run: python -I compose_sheets.py <render_dir> <out_dir>"""
import glob, json, os, sys
from PIL import Image, ImageDraw, ImageFont

RD, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
CAST = json.load(open(os.path.join(HERE, 'cast.json'), encoding='utf-8'))
BG, INK, SUB = (34, 38, 50), (255, 255, 255), (170, 182, 204)
font = lambda size, bold=True: ImageFont.truetype('C:/Windows/Fonts/Montserrat-' + ('Black' if bold else 'Bold') + '.ttf', size)
os.makedirs(OUT, exist_ok=True)

KEYS = os.environ["KEYS"].split(",") if os.environ.get("KEYS") else list(CAST)
for k, rec in ((k, CAST[k]) for k in KEYS):
    views = [Image.open(os.path.join(RD, f'{k}_{v}.png')).convert('RGB').resize((405, 720)) for v in ('front', 'three_quarter', 'side', 'back')]
    faces = sorted(glob.glob(os.path.join(RD, f'{k}_face*.png')))
    sheet = Image.new('RGB', (4 * 405 + 50, 150 + 720 + 30 + 520 + 40), BG); d = ImageDraw.Draw(sheet)
    d.text((25, 28), rec['name'].upper(), font=font(64), fill=INK); d.text((25, 104), rec['role'], font=font(26, False), fill=SUB)
    for i, im in enumerate(views):
        sheet.paste(im, (25 + i * 405, 150))
    for i, f in enumerate(faces):
        sheet.paste(Image.open(f).convert('RGB').resize((520, 520)), (25 + i * 535, 150 + 720 + 30))
        d.text((25 + i * 535 + 14, 150 + 720 + 30 + 470), os.path.basename(f).split('_', 2)[-1][:-4], font=font(30, False), fill=(30, 30, 40))
    sheet.save(os.path.join(OUT, f'sheet_{k}.jpg'), quality=88)

Image.open(os.path.join(RD, 'lineup.png')).convert('RGB').save(os.path.join(OUT, 'lineup.jpg'), quality=88)
if glob.glob(os.path.join(RD, "track_*.png")):
    strip = [Image.open(f).convert('RGB').resize((480, 480)) for f in sorted(glob.glob(os.path.join(RD, 'track_*.png')))]
    s = Image.new('RGB', (480 * len(strip), 480)); [s.paste(im, (i * 480, 0)) for i, im in enumerate(strip)]
    s.save(os.path.join(OUT, 'talk_blink_check.jpg'), quality=88)
print('sheets ->', OUT)
