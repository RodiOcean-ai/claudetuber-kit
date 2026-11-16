"""The Colin episode as ONE bright Blender world and ONE continuous camera, timed to the voice.

Stations along x (camera looks toward +y): kitchen table K (0) -> backyard Y (14) -> giant phone P (28)
-> cone and glass brain C (40) -> ping-pong table T (52) -> thumb over a phone H (64) -> back to the backyard
for the reveal -> home to the kitchen table, where the camera settles on the exact frame-one view (loop).

The bottle on the kitchen table is mid-flip on frame one; the same flip is launched just before the last frame.
The brothers are black silhouettes until "Colin", then they light up as faceless toy figures (no real likeness).

Usage: blender -b --factory-startup --python world.py -- <out path> [--still FRAME]   (STILLS=1,200,... for several)"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import bpy
from common import *

WORDS = json.load(open(os.path.join(HERE, '..', 'voice', 'final_voice.words.json'), encoding='utf-8'))
ws = lambda i: WORDS[i]['s']
find = lambda word, after=0: next(i for i, w in enumerate(WORDS) if i >= after and w['w'].lower().strip('.,?') == word)
END = WORDS[-1]['e'] + 0.5
FRAMES = round(END * FPS)
T_LOOP = FRAMES / FPS
fr = lambda t: 1 + round(t * FPS)
T_BUT = ws(find('but'))
T_INTO = ws(find('into'))
T_BIGGEST = ws(find('their'))
T_AND8 = ws(find('and', find('billion', 20)))
T_AS = ws(find('as'))
T_LANDS = ws(find('lands'))
T_REWARD = ws(find('reward'))
T_BUT2 = ws(find('but', 40))
T_SO = ws(find('so', 40))
T_THATS = ws(find("that's"))
T_COLIN = ws(find('colin'))
T_FAMILY = ws(find('and', find('owen')))

OUT, STILL = args()
sc = reset(FRAMES)
w = world(top='#5aa8ff', horizon='#eaf5ff', strength=1.3)
floor(color='#dcecff')
sn = sun(energy=3.2, rot=(48, 0, 160))
fill = area((0, -6, 5), (60, 0, 0), size=8, energy=600)
FONT = bpy.data.fonts.load('C:/Windows/Fonts/Montserrat-Black.ttf')


def box(loc, size, m, rot=(0, 0, 0), bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=tuple(math.radians(r) for r in rot)); o = bpy.context.object
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 3
    o.data.materials.append(m)
    return o


def cyl(loc, r, depth, m, rot=(0, 0, 0), smooth=True, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.data.materials.append(m)
    if smooth:
        bpy.ops.object.shade_smooth()
    return o


def cone(loc, r1, r2, depth, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=loc, vertices=48, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def sphere(loc, r, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24); o = bpy.context.object
    o.scale = scale; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def torus(loc, R, r, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=tuple(math.radians(a) for a in rot), major_segments=64, minor_segments=16)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    return e


def parent(objs, root):
    bpy.context.view_layer.update()
    for o in objs:
        o.parent = root; o.matrix_parent_inverse = root.matrix_world.inverted()


def text(body, loc, size, m, rot=(90, 0, 0), extrude=0.03, align='CENTER'):
    cu = bpy.data.curves.new('T_' + body[:8], 'FONT'); cu.body = body; cu.font = FONT
    cu.align_x = align; cu.align_y = 'CENTER'; cu.size = size; cu.extrude = extrude
    o = bpy.data.objects.new('T_' + body[:8], cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = tuple(math.radians(r) for r in rot); o.data.materials.append(m)
    return o


def pop(root, t_in, t_out=None, grow=0.25):
    """Scale 0 -> 1 with a small overshoot at t_in; back to 0 at t_out (so nothing shows where it shouldn't)."""
    keys = [(0, 0.0), (t_in - 0.01, 0.0), (t_in + grow * 0.7, 1.12), (t_in + grow, 1.0)]
    if t_out:
        keys += [(t_out, 1.0), (t_out + 0.2, 0.0)]
    for t, s in keys:
        root.scale = (s, s, s); root.keyframe_insert('scale', frame=max(1, fr(t)))


# ---------------------------------------------------------------- materials
wood = mat('Wood', hexrgb('#c88a52'), rough=0.45, coat=0.3)
plastic = mat('Bottle', hexrgb('#bfe6ff'), rough=0.05, coat=1.0)
water = mat('Water', hexrgb('#3fa9ff'), rough=0.1, emit=hexrgb('#3fa9ff'), emit_strength=0.3)
cap_m = mat('Cap', hexrgb('#1f6fff'), rough=0.3)
label_m = mat('Label', hexrgb('#ff4a5a'), rough=0.4)
phone_m = mat('Phone', hexrgb('#1b1f2a'), rough=0.25, coat=0.8)
screen_m = mat('Screen', hexrgb('#ffffff'), rough=0.3, emit=hexrgb('#f4f8ff'), emit_strength=1.6)
ink = mat('Ink', hexrgb('#121826'), rough=0.4)
red = mat('Red', hexrgb('#ff2d3d'), rough=0.25, coat=0.8)
gold = mat('Gold', hexrgb(GOLD), rough=0.25, emit=hexrgb(GOLD), emit_strength=2.5)
white = mat('White', (1, 1, 1), rough=0.3, emit=(1, 1, 1), emit_strength=1.2)
orange = mat('Orange', hexrgb('#ff7a1a'), rough=0.35, coat=0.4)
stripe = mat('Stripe', (1, 1, 1), rough=0.3)
grass = mat('Grass', hexrgb('#5fc35a'), rough=0.9)
fence_m = mat('Fence', hexrgb('#f6efe6'), rough=0.6)
metal = mat('Metal', hexrgb('#a9b4c4'), rough=0.25, metal=1.0)
ball_m = mat('Basketball', hexrgb('#ff7b22'), rough=0.6)
blue_table = mat('PongTable', hexrgb('#1f5fd1'), rough=0.35, coat=0.5)
skin = mat('Thumb', hexrgb('#e9a07a'), rough=0.5, coat=0.15)
nail = mat('Nail', hexrgb('#ffe3d6'), rough=0.15, coat=1.0)
brain_m = mat('Brain', hexrgb('#ff9fc0'), rough=0.15, emit=hexrgb('#ff7fb0'), emit_strength=0.4, coat=1.0)
if 'Transmission Weight' in brain_m.node_tree.nodes['Principled BSDF'].inputs:
    brain_m.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.25
TILE_COLS = ['#ff5a5f', '#ffb020', '#2ec27e', '#28a8ff', '#a66bff', '#ff7ac8', '#00c2b8', '#ff8a2a']


def make_bottle(name, loc):
    root = empty(name, loc)
    parts = [cyl((loc[0], loc[1], loc[2] + 0.11), 0.045, 0.22, plastic),
             cyl((loc[0], loc[1], loc[2] + 0.07), 0.046, 0.12, water),
             cyl((loc[0], loc[1], loc[2] + 0.12), 0.0465, 0.06, label_m),
             cone((loc[0], loc[1], loc[2] + 0.245), 0.045, 0.018, 0.05, plastic),
             cyl((loc[0], loc[1], loc[2] + 0.28), 0.02, 0.025, cap_m)]
    parent(parts, root)
    return root


BOTTLES = []                                         # (root, base, launch times, duration, height): posed every frame in per_frame


def flip(root, base, launch, dur=0.95, height=0.55):
    for b in BOTTLES:
        if b[0] is root:
            b[2].append(launch); return
    BOTTLES.append((root, base, [launch], dur, height))


def bottle_pose(base, launches, dur, height, t):
    """Up in a parabola and one full turn; at rest (upright) between flips."""
    for l in launches:
        u = (t - l) / dur
        if 0 <= u <= 1:
            return (base[0], base[1], base[2] + 4 * height * u * (1 - u)), 2 * math.pi * (1 - (1 - u) ** 1.6)
    return base, wobble(t, [l + dur for l in launches])


def wobble(t, hits, amp=9.0, freq=3.2, decay=5.5):
    """Damped rock on the base after each landing (radians): it lands, rocks, settles."""
    for h in hits:
        d = t - h
        if 0 <= d < 1.2:
            return math.radians(amp) * math.exp(-decay * d) * math.sin(2 * math.pi * freq * d)
    return 0.0


def figure(name, loc, h, m, arm_up=False, rot_z=0):
    """A faceless toy kid: rounded legs and body, a big ball head, arms hinged at the shoulders."""
    x, y, z = loc
    root = empty(name, loc)
    parts = []
    for sx in (-1, 1):
        parts += [cyl((x + sx * 0.08 * h, y, z + 0.2 * h), 0.065 * h, 0.34 * h, m), sphere((x + sx * 0.08 * h, y, z + 0.035 * h), 0.07 * h, m, scale=(1, 1.3, 0.6))]
    parts += [sphere((x, y, z + 0.56 * h), 0.2 * h, m, scale=(1, 0.8, 1.35)), cyl((x, y, z + 0.84 * h), 0.05 * h, 0.08 * h, m),
              sphere((x, y, z + 1.02 * h), 0.19 * h, m)]
    L = 0.36 * h
    for sx, ang in ((-1, -14), (1, 160 if arm_up else 14)):
        sh = (x + sx * 0.19 * h, y, z + 0.74 * h)
        d = (math.sin(math.radians(ang)), 0, -math.cos(math.radians(ang)))
        parts.append(cyl(tuple(sh[i] + d[i] * L / 2 for i in range(3)), 0.048 * h, L, m, rot=(0, -ang, 0)))
        parts.append(sphere(tuple(sh[i] + d[i] * L for i in range(3)), 0.06 * h, m))
        parts.append(sphere(sh, 0.055 * h, m))
    parent(parts, root)
    root.rotation_euler = (0, 0, math.radians(rot_z))
    return root


# ---------------------------------------------------------------- K. kitchen table: your bottle flip and a phone with 10 views
KX = 0.0
box((KX, 0.4, 0.73), (2.4, 1.2, 0.06), wood, bevel=0.03)
for dx in (-1.05, 1.05):
    for dy in (-0.1, 0.9):
        box((KX + dx, dy, 0.36), (0.07, 0.07, 0.72), wood, bevel=0.01)
TOP = 0.76
BOT = (KX + 0.15, 0.25, TOP)
bottle = make_bottle('MyBottle', BOT)
LAUNCH = -0.45                                      # mid-flip on frame one; the same flip relaunches at T_LOOP + LAUNCH
flip(bottle, BOT, LAUNCH); flip(bottle, BOT, T_LOOP + LAUNCH)
phone1 = empty('Phone1', (KX - 0.22, 0.02, TOP))
p1 = [box((KX - 0.16, 0.0, TOP + 0.16), (0.2, 0.015, 0.36), phone_m, rot=(-12, 0, 18), bevel=0.016),
      box((KX - 0.157, -0.009, TOP + 0.16), (0.18, 0.004, 0.33), screen_m, rot=(-12, 0, 18), bevel=0.008)]
v10 = text('10\nviews', (KX - 0.152, -0.016, TOP + 0.165), 0.065, ink, rot=(78, 0, 18), extrude=0.003)
parent(p1 + [v10], phone1)
# a toy family by the far end of the table (out of the frame-one view): they flip bottles in the last scene
FAM = [('Mum', KX + 1.7, 1.25, '#ff6fa8'), ('Dad', KX + 2.3, 1.35, '#2fb9ff'), ('Kid3', KX + 2.9, 0.95, '#ffd23a')]
fam_bottles = []
for i, (nm, fx, fh, col) in enumerate(FAM):
    figure(nm, (fx, 1.25, 0), fh, mat(nm, hexrgb(col), rough=0.35, coat=0.6), arm_up=True, rot_z=0)
    box((fx, 0.9, 0.73), (0.5, 0.45, 0.06), wood, bevel=0.02)
    b = make_bottle(f'FamBottle{i}', (fx, 0.85, TOP))
    for k in range(3):                                # three quick flips each, staggered, all done before the settle
        flip(b, (fx, 0.85, TOP), T_FAMILY + 0.2 + 0.25 * i + 1.05 * k, dur=0.9, height=0.5)
    fam_bottles.append(b)

# ---------------------------------------------------------------- Y. backyard: two silhouettes, a hoop, the sky counter
YX = 14.0
cyl((YX, 1.6, 0.005), 4.2, 0.01, grass, smooth=False, verts=96)
for k in range(-6, 7):
    box((YX + k * 0.6, 4.6, 0.55), (0.12, 0.05, 1.1), fence_m, bevel=0.01)
box((YX, 4.6, 0.85), (8.0, 0.06, 0.08), fence_m, bevel=0.01); box((YX, 4.6, 0.35), (8.0, 0.06, 0.08), fence_m, bevel=0.01)
HOOP = (YX + 1.7, 3.0, 2.6)
HOOP_PARTS = [cyl((HOOP[0], HOOP[1] + 0.45, 1.4), 0.05, 2.8, metal),
              box((HOOP[0], HOOP[1] + 0.3, HOOP[2] + 0.35), (0.9, 0.04, 0.6), white, bevel=0.01),
              torus((HOOP[0], HOOP[1], HOOP[2]), 0.2, 0.015, orange)]
sil = mat('Silhouette', hexrgb('#0b0d14'), rough=0.6)
sil2 = mat('Silhouette2', hexrgb('#0b0d14'), rough=0.6)
BRO = [figure('BroA', (YX - 0.55, 1.6, 0.01), 1.25, sil, arm_up=True), figure('BroB', (YX + 0.45, 1.9, 0.01), 1.4, sil2)]
for m_, lit in ((sil, '#2f8cff'), (sil2, '#ff8a2a')):
    sin_ = m_.node_tree.nodes['Principled BSDF'].inputs
    for t, col, e in ((0, '#0b0d14', 0.0), (T_COLIN - 0.35, '#0b0d14', 0.0), (T_COLIN + 0.1, lit, 0.3)):
        sin_['Base Color'].default_value = (*hexrgb(col), 1); sin_['Base Color'].keyframe_insert('default_value', frame=fr(t))
        sin_['Emission Color'].default_value = (*hexrgb(lit), 1); sin_['Emission Strength'].default_value = e
        sin_['Emission Strength'].keyframe_insert('default_value', frame=fr(t))
back = area((YX, 6.5, 2.2), (-80, 0, 0), size=6, energy=2500, color='#fff1d6')     # sun behind the brothers: they read as silhouettes
A0 = (YX - 0.45, 1.6, 1.55)
T_SHOT1, T_SHOT2 = T_BUT - 0.6, T_THATS - 0.2
BALLS = []                                           # (ball, flight start): keyed flight to the rim, then real physics takes over
for k, t0 in enumerate((T_SHOT1, T_SHOT2)):
    bb = sphere(A0, 0.12, ball_m); bb.name = f'Basketball{k}'
    for f in range(1, FRAMES + 2):
        t = (f - 1) / FPS
        u = min(max((t - t0) / 1.6, 0.0), 1.0)
        bb.location = (A0[0] + (HOOP[0] - A0[0]) * u, A0[1] + (HOOP[1] - A0[1]) * u, A0[2] + (HOOP[2] + 0.05 - A0[2]) * u + 1.3 * 4 * u * (1 - u))
        bb.keyframe_insert('location', frame=f)
        if t > t0 + 1.6:
            break
    BALLS.append((bb, t0 + 1.6))
    if k == 1:                                       # the second ball only exists for the reveal
        for t, h in ((0, True), (t0 - 0.05, True), (t0, False)):
            bb.hide_render = h; bb.keyframe_insert('hide_render', frame=max(1, fr(t)))
counter_root = empty('CounterRoot', (YX, 5.5, 5.2))
cnt_cur = bpy.data.curves.new('Count', 'FONT'); cnt_cur.body = '10'; cnt_cur.font = FONT; cnt_cur.align_x = 'CENTER'; cnt_cur.align_y = 'CENTER'; cnt_cur.size = 0.85; cnt_cur.extrude = 0.08
cnt = bpy.data.objects.new('Count', cnt_cur); bpy.context.collection.objects.link(cnt)
cnt.location = (YX, 5.5, 5.4); cnt.rotation_euler = (math.radians(100), 0, 0); cnt.data.materials.append(gold)
lbl = text('VIEWS', (YX, 5.5, 4.55), 0.5, white, rot=(100, 0, 0), extrude=0.05)
parent([cnt, lbl], counter_root)
pop(counter_root, T_INTO - 0.35, T_BIGGEST + 0.2)
name_root = empty('NameRoot', (YX, 1.2, 2.45))
nm = text('COLIN & OWEN', (YX, 1.2, 2.45), 0.26, gold, extrude=0.05)
parent([nm], name_root)
pop(name_root, T_COLIN, T_FAMILY + 0.6)

# ---------------------------------------------------------------- P. giant phone: the count-up to 5.2B, then the clip's 8 shots as 8 live tiles
PX = 28.0
phone = box((PX, 2.0, 2.0), (1.7, 0.12, 3.4), phone_m, bevel=0.12)
scr = box((PX, 1.93, 2.0), (1.5, 0.02, 3.1), screen_m, bevel=0.06)
badge_root = empty('Badge', (PX, 1.85, 2.2))
rec_cur = bpy.data.curves.new('Rec', 'FONT'); rec_cur.body = '0.0B'; rec_cur.font = FONT; rec_cur.align_x = 'CENTER'; rec_cur.align_y = 'CENTER'; rec_cur.size = 0.5; rec_cur.extrude = 0.06
rec = bpy.data.objects.new('Rec', rec_cur); bpy.context.collection.objects.link(rec)
rec.location = (PX, 1.85, 2.75); rec.rotation_euler = (math.radians(90), 0, 0); rec.data.materials.append(red)
bv = text('VIEWS', (PX, 1.85, 2.3), 0.2, ink, extrude=0.03)
yt_root = empty('YTButton', (PX, 1.86, 1.55))
yt_bg = box((PX, 1.86, 1.55), (0.8, 0.05, 0.56), red, bevel=0.16)
tm = bpy.data.meshes.new('PlayTri')                  # a proper flat play triangle, pointing right
tm.from_pydata([(-0.1, 0, -0.13), (-0.1, 0, 0.13), (0.14, 0, 0)], [], [(0, 1, 2)])
tri = bpy.data.objects.new('PlayTri', tm); bpy.context.collection.objects.link(tri); tri.location = (PX + 0.01, 1.83, 1.55)
tri.data.materials.append(mat('PlayWhite', (1, 1, 1), rough=0.3, emit=(1, 1, 1), emit_strength=1.5))
so = tri.modifiers.new('thick', 'SOLIDIFY'); so.thickness = 0.02
parent([yt_bg, tri], yt_root)
parent([rec, bv, yt_root], badge_root)
pop(badge_root, T_BIGGEST - 0.3, T_AND8 + 0.1)
T_COUNT0, T_COUNT1 = T_BIGGEST - 0.15, T_AND8 - 0.6
confetti = []
for k in range(26):                                   # a burst of confetti when the count lands on 5.2B
    a = 2 * math.pi * k / 26; col = TILE_COLS[k % len(TILE_COLS)]
    c = box((PX, 1.8, 2.75), (0.07, 0.01, 0.04), mat(f'Conf{k}', hexrgb(col), rough=0.4, emit=hexrgb(col), emit_strength=0.6), bevel=0)
    rr = 0.9 + 0.5 * ((k * 37) % 7) / 7
    for t, d in ((0, 0.0), (T_COUNT1, 0.0), (T_COUNT1 + 0.8, 1.0)):
        c.location = (PX + rr * d * math.cos(a), 1.75 - 0.3 * d, 2.75 + rr * d * math.sin(a) - 0.6 * d * d); c.keyframe_insert('location', frame=fr(t))
        c.rotation_euler = (0, 6 * d + k, 3 * d); c.keyframe_insert('rotation_euler', frame=fr(t))
    for t, z in ((0, 0.0), (T_COUNT1 - 0.02, 0.0), (T_COUNT1, 1.0), (T_COUNT1 + 0.75, 1.0), (T_COUNT1 + 0.85, 0.0)):
        c.scale = (z, z, z); c.keyframe_insert('scale', frame=fr(t))

cup_m = mat('CupRed', hexrgb('#e8202f'), rough=0.3, coat=0.6)
bluecup_m = mat('CupBlue', hexrgb('#1d5fe0'), rough=0.3, coat=0.6)
barrel_m = mat('Barrel', hexrgb('#1a6ff0'), rough=0.35, coat=0.4)
tramp_m = mat('Tramp', hexrgb('#1f2a44'), rough=0.5)
table_m = mat('Patio', hexrgb('#eeeeee'), rough=0.5)
TRICKS = ['Hoop shot', 'Trampoline bounce', 'Barrel throw', 'Cone flip', 'Double bottle flip', 'Cup stack flip', 'Cup slam', 'Ping-pong cup']
TILE_ANIMS = []
TILE_T0 = T_AND8
PERIOD = 2.3


def arc(p0, p1, h, u):
    return tuple(p0[i] + (p1[i] - p0[i]) * u for i in range(3))[:2] + (p0[2] + (p1[2] - p0[2]) * u + 4 * h * u * (1 - u),)


for i in range(8):
    cx, cz = PX + (-0.37 if i % 2 == 0 else 0.37), 2.0 + 1.11 - (i // 2) * 0.74
    Y = 1.80
    P = (lambda cx, cz: (lambda dx, dz, y=Y: (cx + dx, y, cz + dz)))(cx, cz)
    SC = 1.0
    tr = empty(f'Tile{i}', (cx, 1.88, cz))
    tb = box((cx, 1.88, cz), (0.68, 0.02, 0.66), mat(f'TileM{i}', hexrgb(TILE_COLS[i]), rough=0.4, emit=hexrgb(TILE_COLS[i]), emit_strength=0.35), bevel=0.04)
    parts = [tb]
    if i == 0:                                       # hoop shot
        parts += [box(P(0.19, 0.24, 1.84), (0.22, 0.01, 0.15), white, bevel=0.005), torus(P(0.17, 0.15), 0.07, 0.009, orange, rot=(70, 0, 0))]
        ball = sphere(P(0, 0), 0.05, ball_m); parts.append(ball)
        def anim(u, ball=ball, P=P):
            ball.location = arc(P(-0.22, -0.2), P(0.17, 0.17), 0.22, min(u, 1)) if u < 1 else P(0.17, 0.17 - 0.4 * min(1, (u - 1) / 0.25) - 0.0)
            if u >= 1.25: ball.location = P(0.17, -0.25)
    elif i == 1:                                     # bounce off a mini trampoline into a bucket
        parts += [box(P(-0.08, -0.215), (0.2, 0.06, 0.015), tramp_m, bevel=0.005), cyl(P(-0.15, -0.26), 0.006, 0.07, metal), cyl(P(-0.01, -0.26), 0.006, 0.07, metal),
                  cyl(P(0.2, -0.2), 0.08, 0.13, barrel_m)]
        ball = sphere(P(0, 0), 0.048, ball_m); parts.append(ball)
        def anim(u, ball=ball, P=P):
            if u < 0.4: ball.location = arc(P(-0.24, 0.24), P(-0.08, -0.2), 0.0, (u / 0.4) ** 2)
            elif u < 1: ball.location = arc(P(-0.08, -0.2), P(0.2, -0.15), 0.25, (u - 0.4) / 0.6)
            else: ball.location = P(0.2, -0.16)
    elif i == 2:                                     # long throw into a barrel
        parts += [cyl(P(0.2, -0.18), 0.09, 0.22, barrel_m)]
        ball = sphere(P(0, 0), 0.048, ball_m); parts.append(ball)
        def anim(u, ball=ball, P=P):
            ball.location = arc(P(-0.25, -0.15), P(0.2, -0.1), 0.38, min(u, 1)) if u < 1 else P(0.2, -0.13)
    elif i == 3:                                     # cone flip on a patio table
        parts += [box(P(0, -0.27), (0.4, 0.06, 0.025), table_m, bevel=0.01)]
        cn = cone(P(0, -0.2), 0.08, 0.012, 0.18, orange); parts.append(cn)
        def anim(u, cn=cn, P=P):
            v = min(u, 1); cn.location = arc(P(-0.12, -0.18), P(0.0, -0.18), 0.22, v); cn.rotation_euler = (0, 2 * math.pi * (1 - (1 - v) ** 1.5), 0)
    elif i == 4:                                     # two bottles flipped together onto a cooler box
        parts += [box(P(0, -0.25), (0.34, 0.06, 0.08), barrel_m, bevel=0.01)]
        bts = []
        for sx in (-1, 1):
            b = make_bottle(f'TileBottle{sx}', P(sx * 0.055, -0.205)); b.scale = (0.62, 0.62, 0.62); bts.append(b); parts.append(b)
        def anim(u, bts=bts, P=P):
            v = min(u, 1)
            for b, sx in zip(bts, (-1, 1)):
                b.location = arc(P(sx * 0.055 - 0.08, -0.205), P(sx * 0.055, -0.205), 0.2, v); b.rotation_euler = (0, 2 * math.pi * (1 - (1 - v) ** 1.5), 0)
    elif i == 5:                                     # flip a red cup to land on top of another
        base = cone(P(0.08, -0.22), 0.04, 0.065, 0.13, cup_m); parts.append(base)
        cp = cone(P(0, 0), 0.04, 0.065, 0.13, cup_m); parts.append(cp)
        def anim(u, cp=cp, P=P):
            v = min(u, 1); cp.location = arc(P(-0.2, -0.22), P(0.08, -0.17), 0.22, v); cp.rotation_euler = (0, 3 * math.pi * (1 - (1 - v) ** 1.5) - math.pi if v < 1 else 0, 0)
            if v >= 1: cp.rotation_euler = (0, 0, 0)
    elif i == 6:                                     # a blue cup tossed spinning, slams mouth-down on a wooden table
        parts += [box(P(0, -0.27), (0.4, 0.06, 0.03), wood, bevel=0.01)]
        cp = cone(P(0, 0), 0.045, 0.07, 0.14, bluecup_m); parts.append(cp)
        def anim(u, cp=cp, P=P):
            v = min(u, 1); cp.location = arc(P(-0.22, 0.05), P(0.02, -0.19), 0.15, v); cp.rotation_euler = (0, math.pi * 2.5 * v + 0.5 * math.pi * (1 - v) if v < 1 else math.pi, 0)
            if v >= 1: cp.rotation_euler = (0, math.pi, 0)
    else:                                            # ping-pong bounce into a cup on a stand
        parts += [cyl(P(0.18, -0.2), 0.006, 0.08, metal), cyl(P(0.18, -0.24), 0.03, 0.006, metal)]
        cp = cone(P(0.17, -0.1), 0.04, 0.065, 0.13, cup_m); parts.append(cp)
        ball = sphere(P(0, 0), 0.032, white); parts.append(ball)
        def anim(u, ball=ball, P=P):
            if u < 0.45: ball.location = arc(P(-0.24, 0.12), P(-0.03, -0.24), 0.05, u / 0.45)
            elif u < 1: ball.location = arc(P(-0.03, -0.24), P(0.17, -0.06), 0.2, (u - 0.45) / 0.55)
            else: ball.location = P(0.17, -0.07)
    parent(parts, tr)
    pop(tr, T_AND8 + 0.12 * i, T_AS + 0.35)
    TILE_ANIMS.append((anim, TILE_T0 + 0.12 * i + 0.1))

# ---------------------------------------------------------------- C. the impressive trick: a bottle flipped across the room lands ON another bottle
CX = 40.0
box((CX, 1.0, 0.45), (2.2, 1.0, 0.9), wood, bevel=0.04)
CTOP = 0.9
BOT_A = (CX + 0.45, 1.0, CTOP)
ba = make_bottle('BottleA', BOT_A); ba.scale = (1.6, 1.6, 1.6)
LAND = (BOT_A[0], 1.0, CTOP + 0.3 * 1.6)
thrower = figure('Thrower', (CX - 1.9, 1.0, 0), 1.3, mat('Thrower', hexrgb('#2fb9ff'), rough=0.35, coat=0.6), arm_up=True)
bottle_b = make_bottle('BottleB', (0, 0, 0)); bottle_b.scale = (1.6, 1.6, 1.6)
B0 = (CX - 1.5, 1.0, 1.35)
T_THROW0, T_THROW1 = T_AS - 0.5, T_LANDS + 0.12      # one throw stretched into slow motion across "can't tell if it'll land"
q_root = empty('Question', (CX - 0.2, 0.95, 2.05))
qm = text('?', (CX - 0.2, 0.95, 2.05), 0.45, white, extrude=0.06)
parent([qm], q_root)
pop(q_root, T_AS, T_LANDS)
brain_m = mat('BrainPink', hexrgb('#f39ab4'), rough=0.42, coat=0.35, emit=hexrgb('#ff7aa8'), emit_strength=0.0)
gyri = bpy.data.textures.new('Gyri', 'VORONOI'); gyri.noise_scale = 0.16
for k, v in (('distance_metric', 'DISTANCE'), ('color_mode', 'INTENSITY'), ('weight_1', -1.0), ('weight_2', 1.0), ('noise_intensity', 1.6)):
    try:
        setattr(gyri, k, v)
    except Exception:
        pass
BR = (CX - 0.2, 1.7, 3.05)                          # high and behind the throw, so the bottle passes under it
cerebrum = sphere(BR, 0.5, brain_m, scale=(1.0, 0.72, 0.74))      # side view: front to the left, cerebellum and stem at the back
for o, lv, st in ((cerebrum, 4, 0.06),):
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = 2; sub.render_levels = lv
    dm = o.modifiers.new('gyri', 'DISPLACE'); dm.texture = gyri; dm.strength = st; dm.mid_level = 0.6
groove = cyl((BR[0] + 0.05, BR[1] - 0.2, BR[2] - 0.08), 0.42, 0.02, mat('Fissure', hexrgb('#c96b86'), rough=0.6), rot=(90, 0, 0))
groove.scale = (1.0, 0.25, 1.0)
cereb = sphere((BR[0] + 0.33, BR[1], BR[2] - 0.27), 0.2, brain_m, scale=(1.0, 1.2, 0.65))
stem = cyl((BR[0] + 0.15, BR[1], BR[2] - 0.45), 0.06, 0.32, brain_m, rot=(0, 25, 0))
brain_e = brain_m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
ring = torus((LAND[0], 0.95, LAND[2] + 0.1), 0.3, 0.025, gold, rot=(90, 0, 0))
T_HIT = T_THROW1
for t, s in ((0, 0.0), (T_HIT - 0.02, 0.0), (T_HIT + 0.03, 0.3), (T_HIT + 0.65, 3.0), (T_HIT + 0.7, 0.0)):
    ring.scale = (s, s, s); ring.keyframe_insert('scale', frame=fr(t))
for k in range(16):
    s = sphere((LAND[0], 0.95, LAND[2] + 0.1), 0.035, gold); a = 2 * math.pi * k / 16
    for t, d in ((0, 0.0), (T_HIT, 0.0), (T_HIT + 0.75, 1.0)):
        s.location = (LAND[0] + 1.3 * d * math.cos(a), 0.9, LAND[2] + 0.1 + 1.3 * d * math.sin(a)); s.keyframe_insert('location', frame=fr(t))
    for t, z in ((0, 0.0), (T_HIT - 0.01, 0.0), (T_HIT + 0.02, 1.0), (T_HIT + 0.7, 1.0), (T_HIT + 0.75, 0.0)):
        s.scale = (z, z, z); s.keyframe_insert('scale', frame=fr(t))


def bottle_b_pose(t):
    if t < T_THROW0:
        return B0, 0.0
    if t < T_THROW1:
        u = (t - T_THROW0) / (T_THROW1 - T_THROW0)
        return arc(B0, LAND, 0.5, u), 4 * math.pi * u
    return LAND, wobble(t, [T_THROW1], amp=7.0)


# ---------------------------------------------------------------- T. ping-pong: the next shot is already flying
TX = 52.0
box((TX, 1.2, 0.72), (2.6, 1.4, 0.05), blue_table, bevel=0.02)
box((TX, 1.2, 0.36), (2.2, 0.08, 0.7), phone_m, bevel=0.01)
box((TX, 1.2, 0.85), (0.02, 1.4, 0.2), white, bevel=0.0)
CUPS = [(TX + 0.9, 1.2), (TX + 1.05, 1.08), (TX + 1.05, 1.32), (TX + 1.2, 0.96), (TX + 1.2, 1.2), (TX + 1.2, 1.44)]
for cx, cy in CUPS:
    cone((cx, cy, 0.81), 0.05, 0.065, 0.16, red)
pball = sphere((0, 0, 0), 0.045, white)
P0, P1 = (TX - 1.1, 1.2, 1.0), (CUPS[0][0], CUPS[0][1], 0.86)
for f in range(1, FRAMES + 2):
    t = (f - 1) / FPS
    u = min(max((t - (T_BUT2 - 0.45)) / 1.9, 0), 1)
    pball.location = (P0[0] + (P1[0] - P0[0]) * u, P0[1], P0[2] + (P1[2] - P0[2]) * u + 0.9 * 4 * u * (1 - u))
    pball.keyframe_insert('location', frame=f)

# ---------------------------------------------------------------- H. glued to the screen: the phone pulls the viewer in
HX = 64.0
bean = sphere((HX, 1.25, 0.3), 0.6, mat('BeanBag', hexrgb('#ff8a5c'), rough=0.7), scale=(1.0, 1.0, 0.55))
viewer_m = mat('Viewer', hexrgb('#eef2f8'), rough=0.35, coat=0.5)
viewer = figure('Viewer', (HX, 1.3, 0.2), 1.25, viewer_m)
eye_w = mat('EyeWhite', (1, 1, 1), rough=0.2, coat=1.0); pupil_m = mat('Pupil', hexrgb('#101420'), rough=0.2)
H0 = (HX, 1.3, 0.2 + 1.02 * 1.25)
eyes = []
for sx in (-1, 1):
    eyes.append(sphere((H0[0] + sx * 0.08, H0[1] - 0.2, H0[2] + 0.03), 0.065, eye_w, scale=(1, 0.6, 1.2)))
    eyes.append(sphere((H0[0] + sx * 0.08, H0[1] - 0.245, H0[2] + 0.0), 0.03, pupil_m))
parent(eyes, viewer)
PH = (HX - 0.16, 0.75, 1.18)
held = empty('HeldPhone', PH)
hp = [box(PH, (0.17, 0.02, 0.32), phone_m, bevel=0.02), box((PH[0], PH[1] + 0.012, PH[2]), (0.15, 0.004, 0.29), mat('Hypno', hexrgb('#a66bff'), emit=hexrgb('#c49bff'), emit_strength=2.0), bevel=0.01)]
parent(hp, held)
beam_m = mat('Beam', hexrgb('#b07bff'), rough=0.3, emit=hexrgb('#b07bff'), emit_strength=4.0)
bsdf = beam_m.node_tree.nodes['Principled BSDF']
if 'Alpha' in bsdf.inputs:
    bsdf.inputs['Alpha'].default_value = 0.45
for k, v in (('surface_render_method', 'BLENDED'), ('blend_method', 'BLEND')):
    if hasattr(beam_m, k):
        try:
            setattr(beam_m, k, v)
        except Exception:
            pass
RINGS = [torus((0, 0, 0), 0.11, 0.016, beam_m, rot=(90, 0, 0)) for _ in range(6)]
arrow_root = empty('SwipeArrow', (PH[0], PH[1], PH[2] + 0.35))
arr = [cyl((PH[0], PH[1] - 0.02, PH[2] + 0.3), 0.018, 0.14, white), cone((PH[0], PH[1] - 0.02, PH[2] + 0.4), 0.05, 0.0, 0.08, white)]
parent(arr, arrow_root)

# ---------------------------------------------------------------- real physics (Bullet rigid bodies), baked to keyframes
# The basketballs drop through the hoop and bounce on the grass; on the reveal a shower of trick objects rains down
# behind the name card and bounces off the brothers. Everything is simulated once, then baked to plain keys.
import random
rng = random.Random(7)
RAIN = []
T_RAIN = T_THATS + 0.1
rain_kinds = [lambda p: sphere(p, 0.12, ball_m), lambda p: sphere(p, 0.045, white), lambda p: cone(p, 0.1, 0.015, 0.24, orange),
              lambda p: cone(p, 0.045, 0.07, 0.15, red)]
for k in range(26):
    p = (YX + rng.uniform(-1.9, 1.9), rng.uniform(1.75, 2.9), rng.uniform(3.6, 5.2))
    o = rain_kinds[k % 4](p); o.name = f'Rain{k}'; o.rotation_euler = (rng.uniform(0, 3), rng.uniform(0, 3), 0)
    rel = T_RAIN + 0.05 * k
    for t, h in ((0, True), (rel - 0.04, True), (rel, False)):
        o.hide_render = h; o.keyframe_insert('hide_render', frame=max(1, fr(t)))
    RAIN.append((o, rel))
with bpy.context.temp_override(scene=sc):
    bpy.ops.rigidbody.world_add()
rbw = sc.rigidbody_world
rbw.collection = bpy.data.collections.new('RigidBodyWorld')
rbw.point_cache.frame_start, rbw.point_cache.frame_end = 1, FRAMES + 1
rbw.substeps_per_frame, rbw.solver_iterations = 10, 10


def rigid(ob, kind, shape, friction=0.6, bounce=0.5, density=None):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.rigidbody.object_add(type=kind)
    rb = ob.rigid_body
    rb.collision_shape = shape; rb.friction, rb.restitution = friction, bounce
    rb.use_margin, rb.collision_margin = True, 0.001
    if density:
        rb.mass = max(ob.dimensions.x * ob.dimensions.y * ob.dimensions.z * 0.52 * density, 0.01)
    return rb


ground = [o for o in bpy.data.objects if o.name.startswith('Floor')][0]
rigid(ground, 'PASSIVE', 'BOX', friction=0.8, bounce=0.6)
for root in BRO:
    for part in root.children_recursive:
        if part.type == 'MESH':
            rigid(part, 'PASSIVE', 'CONVEX_HULL', bounce=0.4)
for part in HOOP_PARTS:
    rigid(part, 'PASSIVE', 'MESH', bounce=0.5)
DYN = []
for bb, rel in BALLS:                                   # basketball: hollow, lively bounce
    rb = rigid(bb, 'ACTIVE', 'SPHERE', bounce=0.72, density=110); DYN.append((bb, rel))
for o, rel in RAIN:
    shape = 'SPHERE' if o.data.name.startswith('Sphere') else 'CONVEX_HULL'
    rigid(o, 'ACTIVE', shape, bounce=0.55 if shape == 'SPHERE' else 0.25, density=300); DYN.append((o, rel))
for o, rel in DYN:                                      # held by the animation until released, then physics
    for t, kin in ((0, True), (rel - 1 / FPS, True), (rel, False)):
        o.rigid_body.kinematic = kin; o.rigid_body.keyframe_insert('kinematic', frame=max(1, fr(t)))
samples = {o: [] for o, _ in DYN}
for f in range(1, FRAMES + 2):
    sc.frame_set(f)
    for o, _ in DYN:
        samples[o].append((f, o.matrix_world.copy()))
for o in [o for o in bpy.data.objects if o.rigid_body]:
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
        bpy.ops.rigidbody.object_remove()
with bpy.context.temp_override(scene=sc):
    bpy.ops.rigidbody.world_remove()
for o, smp in samples.items():
    if o.animation_data and o.animation_data.action:
        o.animation_data_clear() if False else None
    o.rotation_mode = 'QUATERNION'
    for f, m in smp:
        o.matrix_world = m
        o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_quaternion', frame=f)
low = min(m.translation.z for smp in samples.values() for _, m in smp)
print('physics: baked', len(samples), 'bodies, lowest centre z', round(low, 3))

smooth_all()

# ---------------------------------------------------------------- optional cartoon outline (inverted hull), OUTLINE=1
if os.environ.get('OUTLINE'):
    ol = bpy.data.materials.new('Outline'); ol.use_backface_culling = True
    nt = ol.node_tree; nt.nodes.clear()                  # dark ink for the camera, invisible to shadow rays (no shading of the surfaces inside)
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*hexrgb('#1a2033'), 1); em.inputs['Strength'].default_value = 1.0
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0]); nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    mo = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(mx.outputs[0], mo.inputs['Surface'])
    for o in [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('Floor')]:
        if len(o.data.users_collection if hasattr(o.data, 'users_collection') else []) > 1:
            continue
        o.data.materials.append(ol)
        sol = o.modifiers.new('outline', 'SOLIDIFY')
        sol.thickness = -min(0.016, max(0.004, 0.03 * max(o.dimensions)))
        sol.use_flip_normals = True; sol.use_rim = False; sol.material_offset = len(o.data.materials) - 1

# ---------------------------------------------------------------- the camera: drifting holds joined by fast whips
target = empty('Target')
cam = camera(lens=32, focus_obj=target, fstop=2.8)
tcn = cam.constraints.new('TRACK_TO'); tcn.target = target; tcn.track_axis = 'TRACK_NEGATIVE_Z'; tcn.up_axis = 'UP_Y'
add = lambda a, b, k=1.0: tuple(x + k * y for x, y in zip(a, b))
CW, TW = (KX - 0.05, -0.95, 1.12), (KX - 0.02, 0.2, 0.97)      # wide: your bottle and the phone showing 10 views
CLOSE = (0.0, -0.78, 0.06)                                      # close-up: the camera rides with the bottle in the air
T_OPEN = T_BUT - 0.35
lerp3 = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))


def ease(u, k=7.0):
    return (math.tanh(k * (u - 0.5)) / math.tanh(k / 2) + 1) / 2


def open_pose(t):
    """Opening: tight on the bottle mid-flip, follow it down, then pull back to reveal the 10 views (and keep drifting)."""
    bl, a = bottle_pose(BOT, [LAUNCH], 0.95, 0.55, t)
    bc = (bl[0] + 0.15 * math.sin(a), bl[1], bl[2] + 0.15 * math.cos(a))
    rest = (BOT[0], BOT[1], BOT[2] + 0.15)
    if t <= 0.6:
        g = lerp3(bc, rest, max(0.0, (t - 0.35) / 0.25)) if t > 0.35 else bc
        return add(g, CLOSE), g
    k = ease(min(1.0, (t - 0.6) / 1.9), 5.0)
    c = lerp3(add(rest, CLOSE), CW, k); g = lerp3(rest, TW, k)
    d = max(0.0, t - 2.5)
    return add(c, (0.06, 0.05, -0.012), d), add(g, (0.05, 0.0, 0.0), d)


OC1, OT1 = open_pose(T_OPEN)
C0, T0 = open_pose(0.0)
V = tuple((a - b) * FPS for a, b in zip(open_pose(1 / FPS)[0], C0)); VT = tuple((a - b) * FPS for a, b in zip(open_pose(1 / FPS)[1], T0))
SHOTS = [  # (start, end, camera from, camera to, look-at from, look-at to, lift of the whip INTO this hold)
    (0.0, T_OPEN, C0, OC1, T0, OT1, 0),
    (T_BUT - 0.05, T_INTO - 0.3, (YX + 0.2, -3.2, 0.7), (YX - 0.1, -2.8, 0.75), (YX, 1.8, 1.3), (YX, 1.8, 1.4), 0.4),        # silhouettes, low
    (T_INTO - 0.1, T_BIGGEST - 0.35, (YX, -2.6, 1.2), (YX, -2.2, 1.6), (YX, 5.5, 4.6), (YX, 5.5, 5.0), 0),                   # tilt up: the counter
    (T_BIGGEST - 0.05, T_AND8 - 0.2, (PX - 0.5, -3.2, 2.35), (PX - 0.15, -2.5, 2.3), (PX, 1.9, 2.25), (PX, 1.9, 2.2), 0.6),  # the count-up
    (T_AND8, T_AS - 0.35, (PX + 0.15, -1.25, 2.02), (PX + 0.02, -1.05, 2.0), (PX, 1.9, 2.0), (PX, 1.9, 2.0), 0),             # the 8 shots
    (T_AS - 0.05, T_LANDS - 0.15, (CX - 0.55, -1.75, 1.8), (CX - 0.2, -1.55, 1.75), (CX - 0.45, 1.0, 2.0), (CX + 0.05, 1.0, 1.95), 0.5),  # the throw + brain
    (T_LANDS - 0.05, T_BUT2 - 0.3, (CX + 0.3, -1.15, 1.55), (CX + 0.36, -0.95, 1.5), (CX + 0.45, 1.0, 1.4), (CX + 0.45, 1.0, 1.4), 0),  # it lands
    (T_BUT2 - 0.05, T_SO - 0.3, (TX - 0.3, -1.1, 1.55), (TX + 0.2, -0.95, 1.5), (TX + 0.1, 1.2, 1.1), (TX + 0.7, 1.2, 0.95), 0.5),  # ping-pong
    (T_SO - 0.05, T_THATS - 0.3, (HX + 0.75, -1.05, 1.62), (HX + 0.6, -0.85, 1.58), (HX - 0.05, 0.95, 1.3), (HX - 0.05, 0.95, 1.33), 0.4),      # glued to the screen
    (T_THATS, T_FAMILY - 0.3, (YX, -2.4, 1.6), (YX, -2.0, 1.65), (YX, 1.6, 1.6), (YX, 1.6, 1.7), 1.2),                       # reveal
    (T_FAMILY - 0.05, T_FAMILY + 2.2, (KX + 2.2, -2.2, 1.6), (KX + 1.6, -2.0, 1.5), (KX + 2.2, 1.0, 1.0), (KX + 1.4, 0.8, 0.95), 0.8),  # family
]
T_SETTLE = SHOTS[-1][1]


def hermite(p0, m0, p1, m1, T, u):
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return tuple(h00 * a + h10 * T * b + h01 * c + h11 * T * d for a, b, c, d in zip(p0, m0, p1, m1))


def ease(u, k=7.0):
    return (math.tanh(k * (u - 0.5)) / math.tanh(k / 2) + 1) / 2


def pose(t):
    lerp = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
    if t > T_SETTLE:                                  # ease from the family shot into the exact frame-one move
        s = SHOTS[-1]; T = T_LOOP - T_SETTLE
        vc = tuple((b - a) / (s[1] - s[0]) for a, b in zip(s[2], s[3]))
        vg = tuple((b - a) / (s[1] - s[0]) for a, b in zip(s[4], s[5]))
        u = (t - T_SETTLE) / T
        return hermite(s[3], vc, C0, V, T, u), hermite(s[5], vg, T0, VT, T, u)
    if t <= T_OPEN:
        return open_pose(t)
    for n, (t0, t1, c0, c1, g0, g1, lift) in enumerate(SHOTS):
        if t <= t1 or n == len(SHOTS) - 1:
            if t >= t0 or n == 0:
                u = (t - t0) / (t1 - t0)
                return lerp(c0, c1, u), lerp(g0, g1, u)
            p = SHOTS[n - 1]
            u = ease((t - p[1]) / (t0 - p[1]))
            c = lerp(p[3], c0, u); g = lerp(p[5], g0, u); h = lift * math.sin(math.pi * u)
            return (c[0], c[1], c[2] + h), (g[0], g[1] + 1.0 * h, g[2] + 0.4 * h)


bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f in range(1, FRAMES + 2):
    c, g = pose((f - 1) / FPS)
    cam.location = c; cam.keyframe_insert('location', frame=f)
    target.location = g; target.keyframe_insert('location', frame=f)
WHIPS = [round(SHOTS[n - 1][1], 2) for n in range(1, len(SHOTS))]
for k, v in (('use_motion_blur', True), ('motion_blur_shutter', 0.5)):
    if hasattr(sc.render, k):
        setattr(sc.render, k, v)
for k, v in (('use_motion_blur', True), ('motion_blur_shutter', 0.5), ('motion_blur_steps', 1), ('motion_blur_max', 512)):
    if hasattr(sc.eevee, k):
        setattr(sc.eevee, k, v)


# ---------------------------------------------------------------- per-frame: the counter rolls, the brain flickers, tile icons bounce
def per_frame(scene, *_):
    t = (scene.frame_current - 1 + scene.frame_subframe) / FPS
    k = min(1.0, max(0.0, (t - T_INTO) / 1.3))
    cnt.data.body = f'{int(10 + (13_000_000_000 - 10) * (1 - (1 - k) ** 4)):,}' if t > T_INTO else '10'
    kc = min(1.0, max(0.0, (t - T_COUNT0) / (T_COUNT1 - T_COUNT0)))                 # 0.0B -> 5.2B
    rec.data.body = f'{5.2 * (1 - (1 - kc) ** 3):.1f}B'
    pulse = 1.0 + (0.12 * math.sin(math.pi * min(1.0, (t - T_COUNT1) / 0.3)) if T_COUNT1 < t < T_COUNT1 + 0.3 else 0.0)
    yt_root.scale = (pulse, pulse, pulse)
    flick = 0.3 + 0.3 * abs(math.sin(2 * math.pi * 3.1 * t) * math.sin(2 * math.pi * 1.3 * t))
    brain_e.default_value = 3.0 if T_HIT < t < T_HIT + 1.4 else (flick if t > T_AS - 0.5 else 0.0)
    for root, base, launches, dur, height in BOTTLES:
        loc, a = bottle_pose(base, launches, dur, height, t)
        root.location = loc; root.rotation_euler = (0, a, 0)
    bl, a = bottle_b_pose(t)
    bottle_b.location = bl; bottle_b.rotation_euler = (0, a, 0)
    for anim, t0 in TILE_ANIMS:                                  # each tile replays its trick every PERIOD seconds
        anim(((t - t0) % PERIOD) / 1.0 if t > t0 else 0.0)
    lean = min(1.0, max(0.0, (t - (T_SO - 0.4)) / 2.2))         # the phone pulls the viewer in
    viewer.rotation_euler = (math.radians(10 * lean), 0, 0)
    held.location = (PH[0], PH[1] - 0.15 * lean, PH[2])             # the phone backs off as the viewer leans in: never touching
    head = (H0[0], H0[1] - 0.2 - 1.3 * math.sin(math.radians(10 * lean)), H0[2] - 0.05 * lean)
    for k, r in enumerate(RINGS):
        u = ((t * 0.9 + k / len(RINGS)) % 1.0)
        src = (PH[0], PH[1] - 0.15 * lean + 0.03, PH[2])
        r.location = lerp3(src, head, 0.8 * u); sz = 0.45 + 0.45 * u; r.scale = (sz, sz, sz)   # stop short of the face so the eyes stay visible
    ua = (t * 1.1) % 1.0                                        # a swipe arrow tries to rise and is pulled back into the screen
    arrow_root.location = (PH[0], PH[1] - 0.15 * lean, PH[2] + 0.35 + 0.1 * math.sin(math.pi * min(1, ua / 0.5)) - 0.12 * max(0, (ua - 0.5) / 0.5))   # shrinks into the top edge, never through the phone
    sa = 1.0 - max(0.0, (ua - 0.5) / 0.5); arrow_root.scale = (sa, sa, sa)


bpy.app.handlers.frame_change_pre.append(per_frame)

def world_box(objs):
    from mathutils import Vector
    dg = bpy.context.evaluated_depsgraph_get(); lo = [1e9] * 3; hi = [-1e9] * 3
    for o in objs:
        if o.type != 'MESH':
            continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            p = oe.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
    return lo, hi


def overlap(a, b, shrink=0.02):
    (al, ah), (bl, bh) = a, b
    return all(al[i] + shrink < bh[i] - shrink and bl[i] + shrink < ah[i] - shrink for i in range(3))


kids = lambda root: [root] + list(root.children_recursive)
CHECKS = [('thrown bottle vs brain', kids(bottle_b), [cerebrum, cereb, stem, groove]),
          ('viewer vs phone', kids(viewer), kids(held)), ('swipe arrow vs phone', kids(arrow_root), kids(held)),
          ('thrown bottle vs table', kids(bottle_b), [o for o in bpy.data.objects if o.type == 'MESH' and abs(o.location.x - CX) < 1.2 and o.dimensions.x > 2.0])]
if os.environ.get('CHECK'):
    hits = {}
    for f in range(1, FRAMES + 1, 2):
        sc.frame_set(f)
        for name, A, B in CHECKS:
            if A and B and overlap(world_box(A), world_box(B)):
                hits.setdefault(name, []).append(f)
    for name, *_ in CHECKS:
        fs = hits.get(name, [])
        print('CHECK', name, ':', 'clear' if not fs else f'{len(fs)} frames overlap, first {fs[:6]}')
    sys.exit(0)

if os.environ.get('FRAME_START'):
    sc.frame_start, sc.frame_end = int(os.environ['FRAME_START']), int(os.environ['FRAME_END'])
print('world: frames', FRAMES, 'end', round(END, 2), 'whips at', WHIPS)
if os.environ.get('STILLS'):
    for f in map(int, os.environ['STILLS'].split(',')):
        render(os.path.join(OUT, f'{f:04d}.png'), f)
else:
    render(OUT, STILL)
