"""Top-down pictures for the 2.5D and collage fixes (owner's notes, 14 Nov 2026: "maybe try to do top view look",
"not corner to corner", "the PB doesn't look like real PB"). Run inside one graphics-card turn:
  py -3.13 assets_work/gen_top.py"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MP = os.environ.get('MAKE_PICTURE', r'<your-picture-maker>/make-picture.py')   # your local picture script
os.chdir(ROOT)
TOP = ('Photoreal food photograph shot from directly above (flat lay, top-down, 90 degrees), soft warm morning light from the '
       'top left, gentle soft shadows, sharp focus, natural colours.')
VIN = ('Vintage 1960s magazine advertisement print photograph, slightly faded warm colours, visible print grain and fine '
       'halftone dots, old printed paper look, seen from directly above (flat lay),')
GREEN = 'isolated on a solid flat pure green background, nothing else in frame, no text.'
WHITE = 'isolated on a pure white seamless background, nothing else in frame, no text.'
JOBS = [
    ('p25top/board', f'{TOP} A large rectangular wooden cutting board lying on a light marble kitchen counter, the EMPTY board '
                     'filling the middle of the frame, a folded linen tea towel at the right edge of the counter, no food, no '
                     'objects on the board, no text.', '1664x928', 3, 4101),
    ('p25top/bread', f'{TOP} One slice of white sandwich bread lying flat, the classic slice shape with a domed top, soft white '
                     f'crumb and a thin golden-brown crust all around, {GREEN}', '1328x1328', 3, 4201),
    ('p25top/slicepb', f'{TOP} One slice of white sandwich bread lying flat, covered edge to edge with smooth creamy tan-brown '
                       f'peanut butter with gentle knife swirl marks, the golden crust visible all around, {GREEN}', '1328x1328', 3, 4301),
    ('p25top/sandwich', f'{TOP} A whole peanut butter sandwich lying flat, the top slice of white sandwich bread with its '
                        f'golden-brown crust all around, a little peanut butter peeking out at the edges, {GREEN}', '1328x1328', 3, 4401),
    ('p25top/jar', f'{TOP} An open round glass jar of smooth creamy peanut butter, the round opening with the swirled creamy '
                   f'surface inside and the glass rim visible, no lid, {GREEN}', '1328x1328', 3, 4501),
    ('p25top/lid', f'{TOP} A round metal screw-top jar lid lying upside down, plain gold colour, {GREEN}', '1328x1328', 3, 4601),
    ('p25top/knife', f'{TOP} One stainless steel butter knife with a rounded tip lying flat and straight, horizontal, the tip '
                     f'pointing to the left, {GREEN}', '1664x928', 3, 4701),
    ('p25top/knifepb', f'{TOP} One stainless steel butter knife lying flat and straight, horizontal, the tip pointing to the '
                       f'left, a dollop of thick creamy tan-brown peanut butter on the end of the blade, {GREEN}', '1664x928', 3, 4801),
    ('p25top/basil', f'{TOP} A sprig of fresh green basil leaves, {WHITE}', '1328x1328', 3, 4901),
    ('collage2/vtbread', f'{VIN} one slice of white sandwich bread lying flat, classic slice shape with a domed top and a '
                         f'golden-brown crust all around, {GREEN}', '1328x1328', 3, 5101),
    ('collage2/vtslicepb', f'{VIN} one slice of white sandwich bread spread edge to edge with creamy tan-brown peanut butter '
                           f'with knife swirls, the crust visible all around, {GREEN}', '1328x1328', 3, 5201),
    ('collage2/vtsandwich', f'{VIN} a whole peanut butter sandwich, the top slice of white bread with its golden-brown crust all '
                            f'around, peanut butter peeking out at the edges, {GREEN}', '1328x1328', 3, 5301),
]
t0 = time.time()
for out, prompt, size, n, seed in JOBS:
    print(f"{time.strftime('%H:%M:%S')} {out}", flush=True)
    subprocess.run([sys.executable, MP, prompt, f'assets_work/{out}', '--size', size, '--n', str(n), '--seed', str(seed)], check=False)
print(f'all done in {time.time() - t0:.0f} s', flush=True)
