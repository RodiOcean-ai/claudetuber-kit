"""Renders the cast for approval: per character a turnaround (front, 3/4, side, back) and three faces, a lineup of everyone
(with example hero restyles), and a talking/blinking check on the hero's face track. compose_sheets.py lays them out.
Run: blender -b --factory-startup --python cast_sheets.py -- <out_dir>
     env KEYS=pip,dog,cat renders only those cast members (and a lineup of just them)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import bpy
from common import reset, world, sun, area, camera, look_at, render, FPS
from sf_world import empty
from blocky_kit import CAST, HEAD_Z, M, build, hero, set_face, face_track, pose

OUT = sys.argv[sys.argv.index('--') + 1]
os.makedirs(OUT, exist_ok=True)
KEYS = os.environ['KEYS'].split(',') if os.environ.get('KEYS') else list(CAST)
sc = reset(1)
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
world(top='#9cc9ff', horizon='#eef6ff', strength=0.6)
sun(energy=2.6, angle_deg=10, rot=(50, 0, 28)); area((-5, -7, 6), (55, 0, -35), size=8, energy=300)
bpy.ops.mesh.primitive_plane_add(size=400); fl = bpy.context.object; fl.name = 'Floor'; fl.data.materials.append(M('#dfe9f5', 0.9))
target = empty('Focus'); cam = camera(lens=40, focus_obj=target, fstop=5.6)
FACES = {'hero': ('calm', 'happy', 'shocked'), 'mayor': ('smug', 'laughing', 'angry'), 'teacher': ('calm', 'confused', 'determined'),
         'kid': ('happy', 'scared', 'crying'), 'inspector': ('calm', 'smug', 'angry'), 'mom': ('angry', 'calm', 'shocked'),
         'tinychef': ('determined', 'angry', 'happy'), 'pip': ('happy', 'shocked', 'sleepy'), 'grandpa': ('smug', 'confused', 'laughing'),
         'grandma': ('happy', 'smug', 'shocked'), 'scientist': ('determined', 'confused', 'happy'), 'guard': ('angry', 'calm', 'smug'),
         'chef': ('happy', 'angry', 'determined'), 'boss': ('smug', 'angry', 'laughing'), 'fan': ('shocked', 'happy', 'crying'),
         'dog': ('happy', 'calm', 'sad'), 'cat': ('smug', 'angry', 'sleepy'), 'rabbit': ('scared', 'happy', 'calm'), 'pigeon': ('confused', 'angry', 'calm')}
EXAMPLES = {'hero_chess': {'name': 'HeroChess', 'top': '#1d1d24', 'pocket': '#f2f2f2', 'sleeve': '#f2f2f2', 'bottom': '#3a3a46', 'shoe': '#f2f2f2',
                           'accessories': [['hair', {'color': '#4a2c1a'}], ['glasses', {'shape': 'square'}]]},
            'hero_challenge': {'name': 'HeroChallenge', 'top': '#2f7cf6', 'pocket': '#2563c9', 'bottom': '#1d2333', 'shoe': '#ffffff',
                               'accessories': [['cap', {'color': '#ffffff'}]]}}


def shot(fn, cam_loc, look, lens=40, res=(720, 1280), frame=1):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.data.lens = lens; cam.location = cam_loc; target.location = look; look_at(cam, look)
    render(os.path.join(OUT, fn), frame); print('still', fn)


def size(R):
    """Height to the top of the head, in the scene (animals and small people get a closer camera)."""
    return (R.get('head_z', HEAD_Z) + 0.4) * R['scale']


R = {k: build(k, (i * 10.0, 0, 0)) for i, k in enumerate(KEYS)}
if 'hero' in KEYS:
    R.update({k: hero(v, ((len(KEYS) + i) * 10.0, 0, 0)) for i, (k, v) in enumerate(EXAMPLES.items())})
# turnarounds and faces
for k in KEYS:
    x = R[k]['base'][0]; s = R[k]['scale']; h = size(R[k]); d = 6.2 * max(h, 1.1) / 2.77; hz = R[k].get('head_z', HEAD_Z) * s
    for view, turn in (('front', 0), ('three_quarter', 35), ('side', 90), ('back', 180)):
        pose(R[k], shL=(0, 6), shR=(0, 6), turn=turn); set_face(R[k], 'calm')
        shot(f'{k}_{view}.png', (x, -d, h * 0.56), (x, 0, h * 0.52))
    for i, f in enumerate(FACES.get(k, ('calm', 'happy', 'shocked'))):
        pose(R[k], shL=(0, 6), shR=(0, 6), turn=14); set_face(R[k], f); bpy.context.view_layer.update()
        hy = R[k]['head'].matrix_world.translation.y            # an animal's head sits ahead of its body
        shot(f'{k}_face{i}_{f}.png', (x + 0.45 * s, hy - 2.3 * s, hz + 0.1 * s), (x, hy, hz), lens=55, res=(720, 720))
# lineup: everyone side by side, each with their own mood
if 'hero' in KEYS:
    order = [('hero', 'happy'), ('mayor', 'smug'), ('teacher', 'calm'), ('kid', 'happy'), ('inspector', 'angry'), ('hero_chess', 'determined'), ('hero_challenge', 'laughing')]
else:
    order = [(k, FACES.get(k, ('happy',))[0]) for k in KEYS]
xs, cx = [], 0.0
for k, f in order:                                    # people 2.15 apart; animals take their own length sideways
    w = 2.15 if not R[k].get('kind') else 1.9 * R[k]['scale'] + 0.6
    xs.append(cx + w / 2); cx += w
mid = cx / 2
for i, (k, f) in enumerate(order):
    pose(R[k], shL=(0, 6), shR=(0, 6), turn=-50 if R[k].get('kind') == 'quad' else (i - len(order) / 2) * -4, at=(xs[i] - mid, 0, 0)); set_face(R[k], f)
d = max(12.2, cx * 0.72)
shot('lineup.png', (0, -d, 2.0), (0, 0, 1.25), lens=40, res=(1920, 1080))
# talking and blinking check: keyed face track on the hero, rendered at chosen moments
if 'hero' in KEYS:
    for i, (k, f) in enumerate(order):
        pose(R[k], at=(100 + i * 10.0, 0, 0))
    pose(R['hero'], shL=(0, 6), shR=(0, 6), turn=14, at=(0, 0, 0))
    words = [{'w': 'what', 's': 0.3, 'e': 0.62}, {'w': 'no', 's': 1.2, 'e': 1.5}, {'w': 'way', 's': 1.55, 'e': 1.9}]
    blinks = face_track(R['hero'], [(0.0, 'calm'), (1.0, 'shocked'), (2.2, 'happy')], words, t_end=3.0, seed=3)
    moments = [('1_talk_what', 0.4), ('2_shocked', 1.1), ('3_talk_no', 1.4), ('4_blink', next(b for b in blinks if b < 2.2) + 0.03), ('5_happy_after', 2.5)]
    for name, t in moments:
        shot(f'track_{name}.png', (0.45, -2.3, HEAD_Z + 0.1), (0, 0, HEAD_Z), lens=55, res=(720, 720), frame=1 + round(t * FPS))
    print('blinks at', [round(b, 2) for b in blinks])
