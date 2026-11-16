"""Renders the place bank for approval: the street in day, golden hour and night, and the five rooms (bedroom also at night),
each with cast members for scale.  Run: blender -b --factory-startup --python place_sheets.py -- <out_dir>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import bpy
from common import reset, camera, look_at, render
from sf_world import empty
from blocky_kit import build, hero, set_face, pose
from moves import animate
from places import place, light

OUT = sys.argv[sys.argv.index('--') + 1]
os.makedirs(OUT, exist_ok=True)
sc = reset(2)
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
P = {n: place(n) for n in ('street', 'classroom', 'bedroom', 'kitchen', 'office', 'shop')}
target = empty('Focus'); cam = camera(lens=28, focus_obj=target, fstop=8.0)


def shot(fn, c, l, lens=28):
    cam.data.lens = lens; cam.location = c; target.location = l; look_at(cam, l)
    render(os.path.join(OUT, fn), 1); print('still', fn)


def stand(R, spot, face, **kw):
    x, y, z, turn = spot; pose(R, turn=kw.pop('turn', turn), at=(x, y, z), **kw); set_face(R, face)


def sit(R, spot, seat, face, turn=None):
    x, y, z, t = spot; R['base'] = (x, y, z); animate(R, [(0.0, 'sit', {'turn': t if turn is None else turn, 'seat': seat})], 0.05)
    set_face(R, face)


# street cast (moved between the three street pictures)
H, MY, K = hero(None, (0, 0, 0)), build('mayor', (0, 0, 0)), build('kid', (0, 0, 0))
# room cast
T, K2, H2 = build('teacher', (0, 0, 0)), build('kid', (0, 0, 0)), hero(None, (0, 0, 0))
stand(T, P['classroom']['spots']['teacher'], 'calm', shR=(80, 30), turn=20)
sit(K2, P['classroom']['spots']['seat_0_0'], 0.75, 'happy'); sit(H2, P['classroom']['spots']['seat_0_2'], 0.75, 'calm')
H3 = hero(None, (0, 0, 0)); sit(H3, P['bedroom']['spots']['bed_edge'], 1.03, 'sleepy')
MY2, K3 = build('mayor', (0, 0, 0)), build('kid', (0, 0, 0))
stand(MY2, P['kitchen']['spots']['fridge'], 'smug'); sit(K3, P['kitchen']['spots']['table_seat'], 0.75, 'happy', turn=150)
I1 = build('inspector', (0, 0, 0)); sit(I1, P['office']['spots']['desk_chair'], 0.75, 'smug')
H4 = hero(None, (0, 0, 0)); stand(H4, P['office']['spots']['standing'], 'scared')
I2, K4 = build('inspector', (0, 0, 0)), build('kid', (0, 0, 0))
stand(I2, P['shop']['spots']['cashier'], 'angry'); stand(K4, P['shop']['spots']['customer'], 'confused')

light('day')
stand(H, (-7.6, 0.4, 0.06, -15), 'happy', shR=(10, 150)); stand(MY, (-5.0, 0.8, 0.06, 20), 'calm'); stand(K, (-9.6, 1.6, 0.06, 10), 'happy')
shot('1_street_day.png', (-7.6, -8.0, 2.4), (-7.6, 6.0, 3.2))
for name in ('classroom', 'bedroom', 'kitchen', 'office', 'shop'):
    c, l = P[name]['cams']['from_door']; shot(f'2_{name}_day.png', c, l, lens=24)
light('golden')
stand(H, (22.5, 0.6, 0.06, 25), 'determined'); stand(MY, (25.2, 0.9, 0.06, -20), 'smug'); stand(K, (24.0, 2.6, 0.06, 0), 'calm')
shot('3_street_golden.png', (24.0, -8.0, 2.4), (24.0, 6.0, 3.4))
light('night')
stand(H, (-17.6, 0.6, 0.06, 15), 'scared'); stand(MY, (-20.2, 1.5, 0.06, 30), 'angry'); stand(K, (-15.4, 1.8, 0.06, -10), 'shocked')
shot('4_street_night.png', (-18.0, -8.0, 2.4), (-18.0, 6.0, 3.2))
c, l = P['bedroom']['cams']['from_door']; shot('5_bedroom_night.png', c, l, lens=24)
