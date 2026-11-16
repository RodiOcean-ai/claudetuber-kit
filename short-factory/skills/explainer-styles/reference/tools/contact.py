"""Contact sheet: py -3.13 tools/contact.py out.png img1 img2 ... [--w 640] [--cols 2] [--bg 255,255,255]
Puts the pictures in a grid, each scaled to --w wide, with its number in the corner (for picking by eye)."""
import sys
from PIL import Image, ImageDraw
args = sys.argv[1:]
w, cols, bg = 640, 2, (128, 128, 128)
if '--w' in args:
    i = args.index('--w'); w = int(args[i + 1]); del args[i:i + 2]
if '--cols' in args:
    i = args.index('--cols'); cols = int(args[i + 1]); del args[i:i + 2]
if '--bg' in args:
    i = args.index('--bg'); bg = tuple(int(v) for v in args[i + 1].split(',')); del args[i:i + 2]
out, files = args[0], args[1:]
ims = []
for f in files:
    im = Image.open(f)
    if im.mode == 'RGBA':
        b = Image.new('RGBA', im.size, bg + (255,)); b.alpha_composite(im); im = b
    im = im.convert('RGB')
    ims.append(im.resize((w, round(im.height * w / im.width))))
rows = (len(ims) + cols - 1) // cols
cell_h = max(i.height for i in ims)
sheet = Image.new('RGB', (cols * w + (cols + 1) * 8, rows * cell_h + (rows + 1) * 8), (60, 60, 60))
d = ImageDraw.Draw(sheet)
for k, im in enumerate(ims):
    x = 8 + (k % cols) * (w + 8); y = 8 + (k // cols) * (cell_h + 8)
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + 34, y + 24], fill=(255, 0, 0)); d.text((x + 8, y + 5), str(k + 1), fill=(255, 255, 255))
sheet.save(out)
print(out, sheet.size)
