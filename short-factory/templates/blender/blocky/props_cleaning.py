"""Cleaning-episode props for the blocky world (built 13 Nov 2026 for the labelle-cleaning Short): a kid's bedroom mess with a
laundry basket, a wall clock, a stopwatch, a microwave on its stand, a race finish tape, a two-bar chart and a crumpled t-shirt
for a hand. Nothing carries a brand or a logo; the only words are the bar chart's own labels and values.
Each builder returns (P, objects) like the builders in props.py; P['setup'] runs once the prop has its root, P['actions'] maps an
action name to f(P, t, opt). scene.py registers BUILDERS and hands the builder the first row's keywords listed in KW (cast
'text' = the words as written); an action row's options arrive as lists of numbers ('for 2.0' -> opt['for'] == [2.0]; a bare
word -> True).

Kinds, their actions and options (table rows: '| 0.0 | @name | kind | | at X Y Z; turn N | |', then '| t | @name | action | | options | |'):
- mess (a kid's bedroom mess on the floor, 2.4 wide x 1.6 deep, origin = middle of the heap on the floor, 'at X Y 0'; 9 clothes,
  3 books, 3 toy blocks, a ball, and a round laundry basket 0.6 across, 0.5 high at local x +0.9): tidy (for S, default 2.0: the
  things hop one after another, top of the heap first, in arcs into the basket and vanish inside it, the basket squashes as each
  lands and fills up; the floor is clear after, the basket full). Camera rows '@mess' (medium is best) frame the whole heap
  and the basket from above (about 40 degrees down), so the shirts read as shirts. Test: lookdev/props_test.md (labelle-cleaning).
- clock (a round wall clock 0.9 across, the face's middle at the origin, its back flat on local y=0, so 'at X W Z' hangs it on a
  wall whose surface is at y=W; first row 'rim #hex' changes the rim colour, default red): whirl (for S, default 1.5: the minute
  hand spins 8 turns, the hour hand two-thirds of a turn, easing in and out). Shows ten past ten until then.
- stopwatch (0.45 across, 0.69 high with the crown and ring; origin = the bottom of the case, 'at X Y Z' stands it upright on
  that height; 'close' on it shows the whole watch): tick (until T, default the scene's end: the red hand jumps one tick (6 degrees) 5 times a second with a tiny bounce) |
  click (the crown presses in and back, 0.15 s) | pop (it appears from nothing with an overshoot, 0.35 s). A later 'pop' row
  keeps it invisible until then by itself; 'hidden yes' on the first row also starts it invisible (a bare 'hidden' never
  reaches the builder: scene.py drops keywords without a value). In a hand: 'hold <who>; tilt 125' with the move 'show' (or
  'stand+show'): it stands upright beside the head, its bottom resting in the top of the fist, the face fully clear. When held, frame the holder (a camera row on '@stopwatch' aims at
  where the prop was built, not at the hand). 'lie N' on the first row (13 Nov 2026, for views from above): it lies flat on the
  floor, face up, N times the size (no 'pop' then: use 'hide' / 'show'). 'big N': standing, N times the size.
- microwave (on its own little stand: stand top 1.2 high, the microwave 1.1 wide x 0.7 deep x 0.65 high; origin on the floor,
  'at X Y 0'): on (the inside lights up warm, seen through the window, the plate and bowl turn, the display glows; stays on until
  'ding' or the scene's end) | ding (inside light off, the plate stops, a white starburst pops over the top for 0.3 s, the
  display flashes 3 times) | open (the door swings open 100 degrees toward the camera in 0.3 s).
- tape (a race finish line: dark posts with gold tops at local x -1.3 and +1.3, 1.4 high, a red-and-white tape at 1.1 high
  between them, a white line on the floor; origin on the floor between the posts, 'at X Y 0'): break (the tape snaps in the middle with a small white
  flash; both halves spring back toward their posts and swing down, fluttering, over 0.5 s; they hang from the posts after).
- bars (a two-bar chart on the floor, 2.4 wide, one dark base 0.5 high with a label under each bar on its front; origin on the
  floor at the middle, 'at X Y 0'). First-row keywords: heights A B (bar heights, default 0.6 2.8); labels X, Y (default PART 1,
  PART 2); values X, Y (default 340M, 1.7B); colors #hex, #hex (default grey-blue #7f93b8 and green #36d17a). Both bars start
  at zero height (only their coloured tops show on the base). grow (bar 1 grows over 0.6 s, bar 2 starts 0.4 s after it ends
  and grows over 0.8 s; each value pops over its bar on a dark tag ringed in the bar's colour when that bar is done, so it reads
  on any background) | grow 'only 1' or 'only 2' (just that bar, from that moment). '@bars' frames the full-grown chart.
- shirt (a single crumpled t-shirt, 0.68 wide, 0.7 long, hanging from its collar at the origin; first row 'color #hex',
  default bright blue): made for a hand: 'hold <who>; tilt 55' with the move 'carry' (hangs in front of the legs), or
  'hold <who>; tilt 125; pose show' with the move 'show' (hangs beside the head; the raised fist needs its own grip, hence
  'pose show'). No actions. Like every held prop, frame the holder, not '@shirt'."""
import math, re
import bpy
from common import FPS, hexrgb
from sf_world import box, cyl, empty, parent, text
from blocky_kit import M
from animals import prism
from props import _keys, _sphere, F, visible
from props_story import _group, _torus, _cone, _socket_keys, _num

ss = lambda u: 0 if u <= 0 else 1 if u >= 1 else u * u * (3 - 2 * u)
KW = {'clock': {'rim': str}, 'stopwatch': {'hidden': str, 'lie': float, 'big': float}, 'pickup': {'what': str, 'grow': float}, 'shirt': {'color': str, 'pose': str},
      'bars': {'heights': 'text', 'labels': 'text', 'values': 'text', 'colors': 'text'}}


# ---------------------------------------------------------------- helpers
def _cut(ob, path, t, data=None):
    """Remove ob's keys on `path` after time t (an action that ends what an earlier one started)."""
    holder = data or ob
    act = holder.animation_data.action if holder.animation_data else None
    if act is None:
        return
    for fc in getattr(act, 'fcurves', None) or [fc for ly in act.layers for s in ly.strips for cb in s.channelbags for fc in cb.fcurves]:
        if fc.data_path == path:
            for i in range(len(fc.keyframe_points) - 1, -1, -1):
                if fc.keyframe_points[i].co.x > F(t) + 0.5:
                    fc.keyframe_points.remove(fc.keyframe_points[i])


def _frames(ob, path, t0, t1, fn, interp='LINEAR'):
    """Key ob.path every frame from t0 to t1 with fn(seconds since t0)."""
    pts = [((f - 1) / FPS, fn((f - 1) / FPS - t0)) for f in range(F(t0), F(t1) + 1)]
    _keys(ob, path, pts, interp)


def _burst(name, r=0.34, w=0.05, strength=8.0):
    """A white starburst in the x-z plane (facing -y): a ball and eight streaks, hidden (scale 0.001) until keyed."""
    white = M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=strength)
    parts = [_sphere((0, 0, 0), r * 0.4, white, segs=16)]
    for i in range(8):
        a = 2 * math.pi * i / 8; L = r if i % 2 == 0 else r * 0.6
        parts.append(box(((r * 0.5 + L / 2) * math.sin(a), 0, (r * 0.5 + L / 2) * math.cos(a)), (w, w, L), white, rot=(0, math.degrees(a), 0), bevel=0))
    for o in parts:
        o.visible_shadow = False
    g = _group(name, parts, (0, 0, 0)); g.scale = (0.001,) * 3
    return g


def _flash(g, t, dur=0.3, peak=1.25):
    _keys(g, 'scale', [(t - 0.02, (0.001,) * 3), (t + dur * 0.2, (peak,) * 3), (t + dur * 0.55, (1.0,) * 3), (t + dur, (0.001,) * 3)], 'LINEAR')


_CRUMPLE = None


def _crumple(o, strength=0.022, voxel=0.014):
    """Soft cloth: rounds the flat shape off and gives it small lumps (remesh + displace)."""
    global _CRUMPLE
    if _CRUMPLE is None:
        _CRUMPLE = bpy.data.textures.new('Crumple', 'CLOUDS'); _CRUMPLE.noise_scale = 0.09; _CRUMPLE.noise_depth = 1
    rm = o.modifiers.new('soft', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = voxel; rm.use_smooth_shade = True
    dp = o.modifiers.new('lumps', 'DISPLACE'); dp.texture = _CRUMPLE; dp.texture_coords = 'LOCAL'; dp.strength = strength; dp.mid_level = 0.5
    return o


def _flat(pts, thick, loc, m, turn=0.0, tilt=(0, 0), crumple=True):
    """A flat garment lying on the floor: outline pts in (x, y) seen from above, thickness along z, turned about z."""
    o = prism([(x, -y) for x, y in pts], thick, (0, 0, 0), m, bevel=min(0.02, thick / 2.5))
    o.rotation_euler = (math.radians(90 + tilt[0]), math.radians(tilt[1]), math.radians(turn)); o.location = loc
    if crumple:
        _crumple(o)
    return o


# garment outlines, seen from above (x right, y away from the camera = the garment's top)
TEE = [(-0.13, 0.3), (-0.36, 0.22), (-0.44, 0.06), (-0.31, -0.01), (-0.24, 0.09), (-0.25, -0.32), (0.25, -0.32), (0.24, 0.09),
       (0.31, -0.01), (0.44, 0.06), (0.36, 0.22), (0.13, 0.3), (0.07, 0.255), (0.0, 0.24), (-0.07, 0.255)]
HOODIE = [(-0.14, 0.33), (-0.36, 0.26), (-0.62, -0.12), (-0.53, -0.18), (-0.28, 0.06), (-0.29, -0.38), (0.29, -0.38), (0.28, 0.06),
          (0.53, -0.18), (0.62, -0.12), (0.36, 0.26), (0.14, 0.33), (0.0, 0.3)]
JEANS = [(-0.22, 0.46), (0.22, 0.46), (0.25, -0.46), (0.05, -0.46), (0.0, 0.08), (-0.05, -0.46), (-0.25, -0.46)]
SOCK = [(-0.055, 0.2), (0.055, 0.2), (0.055, -0.02), (0.16, -0.05), (0.19, -0.11), (0.15, -0.16), (-0.02, -0.15), (-0.055, -0.1)]


def _rot2(p, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


# ---------------------------------------------------------------- the bedroom mess and the laundry basket
BASKET = (0.9, 0.0)                       # where the basket stands (local), 0.6 across, 0.5 high


def _basket():
    blue, dark, rimc = M('#5ab8e8', 0.45), M('#2a6f99', 0.6), M('#ffffff', 0.4)
    bx, by = BASKET
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.48, location=(bx, by, 0.26), vertices=48, end_fill_type='NOTHING')
    wall = bpy.context.object; wall.data.materials.append(blue); bpy.ops.object.shade_smooth()
    so = wall.modifiers.new('wall', 'SOLIDIFY'); so.thickness = 0.035; so.offset = -1
    parts = [wall, cyl((bx, by, 0.03), 0.28, 0.04, dark, verts=48), _torus((bx, by, 0.5), 0.3, 0.035, rimc, segs=48)]
    for row, z in enumerate((0.17, 0.33)):                                              # the slots of a plastic laundry basket
        for k in range(16):
            a = 2 * math.pi * (k + 0.5 * row) / 16
            parts.append(box((bx + 0.302 * math.cos(a), by + 0.302 * math.sin(a), z), (0.03, 0.06, 0.11), dark, rot=(0, 0, math.degrees(a)), bevel=0.012))
    g = _group('Basket', parts, (bx, by, 0))
    # the laundry inside: a soft lumpy heap that rises as things land
    fill = [_sphere((bx + dx, by + dy, 0.0), r, M(c, 0.8), segs=16) for dx, dy, r, c in
            ((-0.1, 0.05, 0.16, '#ff6b6b'), (0.09, -0.06, 0.15, '#ffd23a'), (0.05, 0.11, 0.14, '#2fb5ff'), (-0.06, -0.1, 0.13, '#8e6cf0'))]
    for o in fill:
        o.scale = (1.0, 1.0, 0.5)
    fg = _group('BasketFill', fill, (bx, by, 0.0)); fg.parent = g; fg.matrix_parent_inverse = g.matrix_world.inverted()
    return g, fg


def mess():
    P = {'focus_z': 0.25, 'size': 0.7, 'view_up': 0.8, 'actions': {}}
    items = []                                                                          # (group, top z)

    def add(name, parts, centre, top):
        items.append((_group(name, parts, centre), top))
    th = 0.05
    lay = lambda k: 0.03 + k * 0.045                                                    # cloth layers, bottom up
    # clothes (bottom layer first)
    add('Jeans', [_flat(JEANS, 0.06, (-0.6, 0.12, lay(0)), M('#3a6fd8', 0.75), turn=28)], (-0.6, 0.12, lay(0)), lay(0))
    add('TeeTeal', [_flat(TEE, th, (-0.42, 0.52, lay(0)), M('#1fc8b4', 0.8), turn=100)], (-0.42, 0.52, lay(0)), lay(0))
    add('TeePurple', [_flat(TEE, th, (0.12, -0.42, lay(0)), M('#8e6cf0', 0.8), turn=14)], (0.12, -0.42, lay(0)), lay(0))
    hood = [_flat(HOODIE, 0.06, (-0.12, -0.05, lay(1)), M('#ff8a3d', 0.8), turn=-16),
            _flat([(math.cos(a) * 0.15, 0.36 + math.sin(a) * 0.11) for a in [math.pi * k / 10 for k in range(11)]] + [(-0.15, 0.3), (0.15, 0.3)],
                  0.055, (-0.12, -0.05, lay(1) + 0.01), M('#e8762e', 0.8), turn=-16)]
    hood.append(_flat([(x, y) for x, y in ((-0.16, -0.12), (0.16, -0.12), (0.12, -0.3), (-0.12, -0.3))], 0.02, (-0.12, -0.05, lay(1) + 0.035), M('#e8762e', 0.8), turn=-16, crumple=False))
    add('Hoodie', hood, (-0.12, -0.05, lay(1)), lay(1) + 0.04)
    add('TeeRed', [_flat(TEE, th, (-0.88, -0.36, lay(1)), M('#ff4d5e', 0.8), turn=62)], (-0.88, -0.36, lay(1)), lay(1))
    add('TeeYellow', [_flat(TEE, th, (0.22, 0.36, lay(1)), M('#ffd23a', 0.8), turn=-38)], (0.22, 0.36, lay(1)), lay(1))
    for nm, x, y, a, c, cuff in (('SockPink', -0.18, 0.42, 30, '#ff7eb6', '#ffffff'), ('SockGreen', 0.42, 0.02, -70, '#5fd35f', '#2b8a3e'), ('SockWhite', -1.02, 0.22, 140, '#f4f4f0', '#e63946')):
        z = lay(2)
        s = _flat(SOCK, 0.045, (x, y, z), M(c, 0.8), turn=a, crumple=False)
        cx, cy = _rot2((0.0, 0.17), a)
        cf = box((x + cx, y + cy, z + 0.005), (0.12, 0.05, 0.05), M(cuff, 0.8), rot=(0, 0, a), bevel=0.018)
        add(nm, [s, cf], (x, y, z), z)
    # books (closed, on the clothes)
    for nm, x, y, z, a, tilt, c in (('BookBlue', 0.3, -0.02, lay(2) + 0.04, 12, 0, '#2f7cf6'), ('BookGreen', 0.33, -0.04, lay(2) + 0.12, -8, 0, '#3fae5a'),
                                    ('BookRed', -0.72, -0.08, lay(2) + 0.06, 40, 8, '#e63946')):
        cover = box((x, y, z), (0.36, 0.27, 0.075), M(c, 0.5), rot=(tilt, 0, a), bevel=0.012)
        dx, dy = _rot2((0.012, 0), a)
        pages = box((x + dx, y + dy, z), (0.33, 0.25, 0.058), M('#f6ecd2', 0.8), rot=(tilt, 0, a), bevel=0.004)
        add(nm, [cover, pages], (x, y, z), z + 0.04)
    # toy blocks (plain bright cubes) and a ball
    for nm, x, y, z, a, c in (('BlockA', -1.05, -0.58, 0.09, 20, '#ffd23a'), ('BlockB', 0.47, 0.58, 0.09, -15, '#e63946'), ('BlockC', -0.3, -0.62, 0.09, 35, '#2f7cf6')):
        add(nm, [box((x, y, z), (0.18, 0.18, 0.18), M(c, 0.4, coat=0.5), rot=(0, 0, a), bevel=0.03)], (x, y, z), z + 0.09)
    bx, by, bz = -0.38, 0.08, lay(2) + 0.15
    ball = [_sphere((bx, by, bz), 0.17, M('#ff4d5e', 0.35, coat=0.6), segs=32), _torus((bx, by, bz), 0.158, 0.026, M('#ffffff', 0.4), rot=(90, 0, 30), segs=48),
            _torus((bx, by, bz), 0.158, 0.026, M('#ffd23a', 0.4), rot=(90, 0, -50), segs=48)]
    add('Ball', ball, (bx, by, bz), bz + 0.17)
    basket, fill = _basket()
    fill.location.z = -0.2                                                              # empty: the heap is hidden in the bottom
    P.update(basket=basket, fill=fill, items=items)

    def tidy(P, t, o):
        S = max(0.8, _num(o, 'for', 2.0)); hop, drop = 0.42, 0.14
        order = sorted(P['items'], key=lambda it: -it[1])                               # the top of the heap first
        n = len(order); gap = (S - hop - drop) / max(1, n - 1)
        top = (BASKET[0], BASKET[1], 0.68); inside = (BASKET[0], BASKET[1], 0.22)
        lands = []
        for i, (g, _) in enumerate(order):
            t0 = t + i * gap; p0 = tuple(g.location); r0 = tuple(g.rotation_euler)
            apex = max(p0[2], top[2]) + 0.55 + 0.25 * (abs(p0[0] - top[0]) > 1.0)
            spin = (math.radians(180 * (1 if i % 2 else -1)), math.radians(90 * ((i % 3) - 1)), math.radians(120))

            def path(u, p0=p0):
                e = ss(u) * 0.3 + u * 0.7
                x = p0[0] + (top[0] - p0[0]) * e; y = p0[1] + (top[1] - p0[1]) * e
                z = (1 - u) ** 2 * p0[2] + 2 * u * (1 - u) * apex + u * u * top[2]
                return (x, y, z)
            pts, rots, scs = [], [], []
            for f in range(F(t0), F(t0 + hop) + 1):
                u = min(1.0, max(0.0, ((f - 1) / FPS - t0) / hop))
                pts.append(((f - 1) / FPS, path(u))); rots.append(((f - 1) / FPS, tuple(a + b * ss(u) for a, b in zip(r0, spin))))
                scs.append(((f - 1) / FPS, (1 - 0.45 * ss(u),) * 3))
            pts.append((t0 + hop + drop, inside)); scs.append((t0 + hop + drop, (0.001,) * 3))
            _keys(g, 'location', [(t0 - 0.01, p0)] + pts, 'LINEAR')
            _keys(g, 'rotation_euler', [(t0 - 0.01, r0)] + rots, 'LINEAR')
            _keys(g, 'scale', [(t0 - 0.01, (1, 1, 1))] + scs, 'LINEAR')
            lands.append(t0 + hop + drop * 0.5)

        def squash(dt):
            a = 0.0
            for tl in lands:
                d = dt + t - tl
                if 0 <= d < 0.14:
                    a += 0.12 * math.sin(math.pi * d / 0.14)
                elif 0.14 <= d < 0.26:
                    a -= 0.035 * math.sin(math.pi * (d - 0.14) / 0.12)
            a = max(-0.06, min(0.16, a))
            return (1 + a * 0.45, 1 + a * 0.45, 1 - a)
        _frames(P['basket'], 'scale', t, lands[-1] + 0.3, squash)
        k_of = lambda tt: sum(1 for tl in lands if tl <= tt) / len(lands)
        _frames(P['fill'], 'location', t, lands[-1] + 0.3, lambda dt: (BASKET[0], BASKET[1], -0.2 + 0.64 * ss(k_of(t + dt) ** 0.8)))
    P['actions']['tidy'] = tidy
    objs = [g for g, _ in items] + [basket]
    return P, objs


# ---------------------------------------------------------------- the wall clock
def clock(rim='#e63946'):
    rc, white, ink = M(rim, 0.35, coat=0.6), M('#ffffff', 0.35), M('#22232b', 0.4)
    parts = [cyl((0, -0.05, 0), 0.43, 0.1, rc, rot=(90, 0, 0), verts=64),                # the body, its back on y=0
             _torus((0, -0.1, 0), 0.41, 0.05, rc, rot=(90, 0, 0)),                        # the round rim
             cyl((0, -0.101, 0), 0.38, 0.01, white, rot=(90, 0, 0), verts=64)]            # the white face
    for k in range(12):                                                                   # 12 tick marks, the quarters bigger
        a = 2 * math.pi * k / 12; big = k % 3 == 0; r = 0.3
        L, W = (0.085, 0.034) if big else (0.05, 0.022)
        parts.append(box((r * math.sin(a), -0.109, r * math.cos(a)), (W, 0.012, L), ink, rot=(0, math.degrees(a), 0), bevel=0.004))
    hour = box((0, -0.122, 0.085), (0.052, 0.014, 0.23), ink, bevel=0.012)
    minute = box((0, -0.136, 0.125), (0.036, 0.014, 0.32), ink, bevel=0.01)
    H = _group('ClockHour', [hour], (0, -0.12, 0)); Mn = _group('ClockMinute', [minute], (0, -0.13, 0))
    H.rotation_euler = (0, math.radians(305), 0); Mn.rotation_euler = (0, math.radians(60), 0)   # ten past ten
    cap = cyl((0, -0.142, 0), 0.04, 0.03, rc, rot=(90, 0, 0), verts=24)
    P = {'focus_z': 0.0, 'size': 0.45, 'hour': H, 'minute': Mn, 'actions': {}}

    def whirl(P, t, o):
        S = max(0.3, _num(o, 'for', 1.5))
        h0, m0 = P['hour'].rotation_euler[1], P['minute'].rotation_euler[1]
        _keys(P['minute'], 'rotation_euler', [(t, (0, m0, 0)), (t + S, (0, m0 + math.radians(8 * 360), 0))])
        _keys(P['hour'], 'rotation_euler', [(t, (0, h0, 0)), (t + S, (0, h0 + math.radians(240), 0))])
        P['hour'].rotation_euler = (0, h0 + math.radians(240), 0); P['minute'].rotation_euler = (0, m0 + math.radians(8 * 360), 0)
    P['actions']['whirl'] = whirl
    return P, parts + [H, Mn, cap]


# ---------------------------------------------------------------- the stopwatch
SW_R, SW_C = 0.225, 0.225                 # case radius, case centre height above the origin (the case's bottom)


def stopwatch(hidden=None, lie=0.0, big=0.0):
    chrome, white, ink, red = M('#e6eaf0', 0.18, metal=0.85), M('#ffffff', 0.35), M('#22232b', 0.4), M('#e63946', 0.3, coat=0.6)
    C = (0, 0, SW_C)
    parts = [cyl((0, 0, SW_C), SW_R, 0.16, chrome, rot=(90, 0, 0), verts=64),           # the chunky case
             _torus((0, -0.08, SW_C), SW_R - 0.02, 0.028, chrome, rot=(90, 0, 0)),         # the bezel round the face
             cyl((0, -0.083, SW_C), SW_R - 0.035, 0.01, white, rot=(90, 0, 0), verts=64)]  # the white face
    for k in range(12):
        a = 2 * math.pi * k / 12; big = k % 3 == 0; r = 0.145
        L, W = (0.05, 0.022) if big else (0.032, 0.014)
        parts.append(box((r * math.sin(a), -0.09, SW_C + r * math.cos(a)), (W, 0.01, L), ink, rot=(0, math.degrees(a), 0), bevel=0.003))
    hand = [box((0, -0.098, SW_C + 0.055), (0.018, 0.01, 0.19), red, bevel=0.004), cyl((0, -0.1, SW_C), 0.026, 0.02, red, rot=(90, 0, 0), verts=20)]
    Hd = _group('StopwatchHand', hand, (0, -0.098, SW_C))
    crown = [cyl((0, 0, SW_C + SW_R + 0.025), 0.035, 0.07, chrome, verts=20),             # the stem
             cyl((0, 0, SW_C + SW_R + 0.075), 0.065, 0.06, red, verts=32),                # the red button
             _torus((0, 0, SW_C + SW_R + 0.165), 0.06, 0.017, chrome, rot=(90, 0, 0), segs=32)]   # the ring on top
    Cr = _group('StopwatchCrown', crown, (0, 0, SW_C + SW_R))
    side = cyl((0.7071 * (SW_R + 0.02), 0, SW_C + 0.7071 * (SW_R + 0.02)), 0.026, 0.05, chrome, rot=(0, 45, 0), verts=16)   # a small side pusher
    body = _group('StopwatchBody', parts + [Hd, Cr, side], C)
    P = {'focus_z': SW_C + 0.09, 'size': 0.32, 'hand': Hd, 'crown': Cr, 'body': body, 'hand_a': 0.0, 'actions': {},
         'grip': (0.0, 0.09, 0.92)}
    # held with the move 'show' and 'tilt 125': the case stands upright, its bottom just above the middle of the fist and a
    # little in front of it, so the fingers close round the bottom of the case and the face stays clear

    def setup(P):
        if lie:                                       # 'lie N': flat on the floor, face up, N times the size (seen from above)
            P['body'].rotation_euler = (math.radians(-90), 0, 0); P['body'].scale = (lie,) * 3
            P['body'].location = (0, 0, 0.085 * lie); P['focus_z'] = 0.1 * lie; P['size'] = 0.32 * lie
        elif big:                                     # 'big N': standing up, N times the size (seen at eye level)
            P['body'].scale = (big,) * 3; P['body'].location = (0, 0, SW_C * big)
            P['focus_z'] = (SW_C + 0.09) * big; P['size'] = 0.32 * big
        elif hidden:
            P['body'].scale = (0.001,) * 3; P['body'].keyframe_insert('scale', frame=0)
    P['setup'] = setup

    def tick(P, t, o):
        t1 = _num(o, 'until', P.get('t_end', t + 6.0) + 0.1); a0 = P['hand_a']
        pts = []
        for f in range(F(t), F(t1) + 1):
            u = (f - 1) / FPS - t; n = int(u * 5 + 1e-6); d = round((u - n / 5) * FPS)     # jumps so far, frames since the last jump
            ang = a0 + 6 * n + (2.2 if d == 0 and n > 0 else -0.8 if d == 1 and n > 0 else 0.0)
            pts.append(((f - 1) / FPS, (0, math.radians(ang), 0)))
        _keys(P['hand'], 'rotation_euler', pts, 'CONSTANT')
        P['hand_a'] = a0 + 6 * int((t1 - t) * 5)

    def click(P, t, o):
        z0 = SW_C + SW_R
        _keys(P['crown'], 'location', [(t, (0, 0, z0)), (t + 0.06, (0, 0, z0 - 0.04)), (t + 0.15, (0, 0, z0))])

    def pop(P, t, o):
        _keys(P['body'], 'scale', [(t, (0.001,) * 3), (t + 0.22, (1.15,) * 3), (t + 0.35, (1.0,) * 3)])
    P['actions'].update(tick=tick, click=click, pop=pop)
    return P, [body]


# ---------------------------------------------------------------- the microwave on its stand
MW = dict(x0=-0.55, x1=0.55, y0=-0.35, y1=0.35, z0=1.2, z1=1.85, split=0.2)   # body; the door covers x0..split


def _glass():
    m = bpy.data.materials.new('MicrowaveWindow'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*hexrgb('#141820'), 1); b.inputs['Roughness'].default_value = 0.08
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Alpha'].default_value = 0.62
    b.inputs['Emission Color'].default_value = (*hexrgb('#ffb347'), 1); b.inputs['Emission Strength'].default_value = 0.0
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = False
    return m


def microwave():
    x0, x1, y0, y1, z0, z1, sp = (MW[k] for k in ('x0', 'x1', 'y0', 'y1', 'z0', 'z1', 'split'))
    wood, leg, shell, panel = M('#f2c27a', 0.6), M('#c98e4a', 0.6), M('#f3f5f8', 0.35, coat=0.4), M('#2b2f3a', 0.45)
    parts = [box((0, 0, 1.16), (1.3, 0.86, 0.08), wood, bevel=0.025), box((0, 0, 0.36), (1.18, 0.74, 0.05), wood, bevel=0.02)]   # the stand: top and shelf
    for sx in (-0.58, 0.58):
        for sy in (-0.36, 0.36):
            parts.append(box((sx, sy, 0.56), (0.07, 0.07, 1.12), leg, bevel=0.015))
    # the microwave's shell around a hollow inside
    t = 0.05
    parts += [box((0, 0, z1 - t / 2), (x1 - x0, y1 - y0, t), shell, bevel=0.02), box((0, 0, z0 + t / 2), (x1 - x0, y1 - y0, t), shell, bevel=0.02),
              box((x0 + t / 2, 0, (z0 + z1) / 2), (t, y1 - y0, z1 - z0), shell, bevel=0.02), box((0, y1 - t / 2, (z0 + z1) / 2), (x1 - x0, t, z1 - z0), shell, bevel=0.02),
              box(((sp + x1) / 2, 0, (z0 + z1) / 2), (x1 - sp, y1 - y0, z1 - z0), shell, bevel=0.02)]
    for sx in (x0 + 0.08, x1 - 0.08):                                                    # little feet
        parts.append(box((sx, 0, z0 - 0.0), (0.08, 0.5, 0.03), panel, bevel=0.008))
    inner = M('#3a3f4a', 0.5, emit=hexrgb('#ffd38a'), emit_strength=0.0).copy(); inner.name = 'MicrowaveInside'
    ix0, ix1 = x0 + t, sp
    parts += [box(((ix0 + ix1) / 2, y1 - t - 0.005, (z0 + z1) / 2), (ix1 - ix0, 0.01, z1 - z0 - 2 * t), inner, bevel=0),   # the lit inside walls
              box(((ix0 + ix1) / 2, 0, z1 - t - 0.005), (ix1 - ix0, y1 - y0 - 0.1, 0.01), inner, bevel=0),
              box((ix0 + 0.005, 0, (z0 + z1) / 2), (0.01, y1 - y0 - 0.1, z1 - z0 - 2 * t), inner, bevel=0),
              box((ix1 - 0.005, 0, (z0 + z1) / 2), (0.01, y1 - y0 - 0.1, z1 - z0 - 2 * t), inner, bevel=0)]
    # the turntable: a glass plate and a bowl of soup
    cx = (ix0 + ix1) / 2; zf = z0 + t
    tt = [cyl((cx, 0, zf + 0.012), 0.24, 0.02, M('#dfe9f2', 0.15, coat=1.0), verts=48), _cone((cx, 0, zf + 0.075), 0.08, 0.14, 0.11, M('#ffffff', 0.3, coat=0.5), verts=40),
          cyl((cx, 0, zf + 0.133), 0.125, 0.006, M('#ff8a3d', 0.4), verts=40), box((cx + 0.06, 0, zf + 0.138), (0.06, 0.04, 0.02), M('#5fd35f', 0.5), bevel=0.008)]
    TT = _group('Turntable', tt, (cx, 0, zf))
    lamp = bpy.data.lights.new('MicrowaveLight', 'POINT'); lamp.energy = 0.0; lamp.color = hexrgb('#ffcf80'); lamp.shadow_soft_size = 0.12
    lo = bpy.data.objects.new('MicrowaveLight', lamp); bpy.context.collection.objects.link(lo); lo.location = (cx, 0.05, z1 - 0.14)
    # the door, hinged on its left edge: a frame round a dark window, and a handle
    dz0, dz1, dy = z0 + 0.01, z1 - 0.01, y0 - 0.02
    wx0, wx1, wz0, wz1 = x0 + 0.1, sp - 0.14, z0 + 0.11, z1 - 0.11
    door = [box(((x0 + sp) / 2, dy, dz1 - (dz1 - wz1) / 2), (sp - x0, 0.04, dz1 - wz1), shell, bevel=0.012),
            box(((x0 + sp) / 2, dy, dz0 + (wz0 - dz0) / 2), (sp - x0, 0.04, wz0 - dz0), shell, bevel=0.012),
            box((x0 + (wx0 - x0) / 2, dy, (z0 + z1) / 2), (wx0 - x0, 0.04, wz1 - wz0 + 0.02), shell, bevel=0.012),
            box((wx1 + (sp - wx1) / 2, dy, (z0 + z1) / 2), (sp - wx1, 0.04, wz1 - wz0 + 0.02), shell, bevel=0.012)]
    win = box(((wx0 + wx1) / 2, dy, (wz0 + wz1) / 2), (wx1 - wx0, 0.012, wz1 - wz0), _glass(), bevel=0); win.visible_shadow = False
    door += [win, box((sp - 0.075, dy - 0.045, (z0 + z1) / 2), (0.04, 0.05, 0.36), M('#c9ced8', 0.25, metal=0.6), bevel=0.015)]
    Door = _group('MicrowaveDoor', door, (x0, dy, 0))
    # the control panel: a glowing green display bar and buttons
    disp = M('#0f3d22', 0.3, emit=hexrgb('#19e05a'), emit_strength=0.3).copy(); disp.name = 'MicrowaveDisplay'
    px = (sp + x1) / 2; fy = y0 - 0.005
    parts += [box((px, fy, (z0 + z1) / 2), (x1 - sp - 0.06, 0.012, z1 - z0 - 0.08), panel, bevel=0.01),
              box((px, fy - 0.01, z1 - 0.13), (0.24, 0.012, 0.075), disp, bevel=0.004)]
    for r in range(3):
        for c in range(3):
            parts.append(box((px - 0.085 + 0.085 * c, fy - 0.012, z1 - 0.26 - 0.07 * r), (0.06, 0.018, 0.045), M('#d9dde4', 0.4), bevel=0.01))
    parts.append(cyl((px, fy - 0.02, z0 + 0.12), 0.055, 0.03, M('#3fae5a', 0.35), rot=(90, 0, 0), verts=32))   # the big start button
    star = _burst('MicrowaveDing', r=0.17); star.location = (-0.15, -0.1, z1 + 0.36)
    P = {'focus_z': 1.5, 'size': 0.55, 'door': Door, 'tt': TT, 'lamp': lamp, 'inner': inner, 'glass': win.data.materials[0], 'disp': disp,
         'star': star, 'on_at': None, 'actions': {}}
    ib = inner.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    gb = P['glass'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    db = disp.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    SPIN = 0.35                                                                           # turns a second

    def lamp_keys(pts):
        for tt_, v in pts:
            lamp.energy = v; lamp.keyframe_insert('energy', frame=F(tt_))

    def on(P, t, o):
        _socket_keys(ib, [(t, 0.0), (t + 0.15, 2.6)]); _socket_keys(gb, [(t, 0.0), (t + 0.15, 0.35)]); _socket_keys(db, [(t, 0.3), (t + 0.1, 1.8)])
        lamp_keys([(t, 0.0), (t + 0.15, 25.0)])
        te = P.get('t_end', t + 6.0) + 0.1; a0 = P['tt'].rotation_euler[2]
        _keys(P['tt'], 'rotation_euler', [(t, (0, 0, a0)), (te, (0, 0, a0 + 2 * math.pi * SPIN * (te - t)))], 'LINEAR')
        P['on_at'] = (t, a0)

    def ding(P, t, o):
        _socket_keys(ib, [(t, 2.6), (t + 0.12, 0.0)]); _socket_keys(gb, [(t, 0.35), (t + 0.12, 0.0)]); lamp_keys([(t, 25.0), (t + 0.12, 0.0)])
        if P['on_at']:
            t0, a0 = P['on_at']; _cut(P['tt'], 'rotation_euler', t)
            a = a0 + 2 * math.pi * SPIN * (t - t0)
            _keys(P['tt'], 'rotation_euler', [(t, (0, 0, a)), (t + 0.25, (0, 0, a + 2 * math.pi * SPIN * 0.12))], 'LINEAR')
            P['on_at'] = None
        _flash(P['star'], t, 0.3)
        pts = []
        for k in range(3):                                                                # three flashes, then a calm glow
            pts += [(t + 0.2 * k, 2.6), (t + 0.2 * k + 0.1, 0.1)]
        _socket_keys(db, [(t - 0.01, 1.8)] + pts + [(t + 0.62, 0.9)])

    def open_(P, t, o):
        _keys(P['door'], 'rotation_euler', [(t, (0, 0, 0)), (t + 0.22, (0, 0, math.radians(-106))), (t + 0.3, (0, 0, math.radians(-100)))])
    P['actions'].update(on=on, ding=ding, open=open_)
    return P, parts + [TT, lo, Door, star]


# ---------------------------------------------------------------- the finish tape
TAPE_N, TAPE_Z, POST_X = 10, 1.1, 1.3


def tape():
    white, red, base, pole, gold = M('#ffffff', 0.45), M('#e63946', 0.4), M('#2b2f3a', 0.5), M('#3a4256', 0.4), M('#ffd23a', 0.35, coat=0.5)
    parts = [box((0, 0, 0.006), (2.5, 0.14, 0.012), M('#ffffff', 0.5), bevel=0)]          # the white line on the floor
    for sx in (-1, 1):
        x = sx * POST_X
        parts += [cyl((x, 0, 0.03), 0.17, 0.06, base, verts=40), cyl((x, 0, 0.72), 0.055, 1.32, pole, verts=24),
                  _sphere((x, 0, 1.42), 0.09, gold, segs=24)]
        parts.append(box((x, 0, TAPE_Z), (0.13, 0.13, 0.17), gold, bevel=0.03))           # where the tape is tied on
    L = (POST_X - 0.06) / TAPE_N
    halves = []
    for side in (-1, 1):                                                                  # each half: a chain of red and white pieces
        pivots, segs = [], []
        root = empty(f'TapeHalf{side}', (side * (POST_X - 0.06), 0, TAPE_Z))
        root.rotation_euler = (0, 0, math.pi if side > 0 else 0.0)                        # local +x runs from the post to the middle
        prev = root
        for i in range(TAPE_N):
            pv = empty(f'TapeJoint{side}_{i}'); pv.parent = prev; pv.location = (0 if i == 0 else L, 0, 0)
            sg = box((0, 0, 0), (L + 0.004, 0.012, 0.13), red if i % 2 == 0 else white, bevel=0.004)
            sg.parent = pv; sg.location = (L / 2, 0, 0)
            pivots.append(pv); segs.append(sg); prev = pv
        halves.append(dict(root=root, pivots=pivots, segs=segs))
    flash = _burst('TapeSnap', r=0.26, strength=6.0); flash.location = (0, -0.05, TAPE_Z)
    P = {'focus_z': 0.8, 'size': 0.95, 'halves': halves, 'flash': flash, 'actions': {}}

    def brk(P, t, o):
        _flash(P['flash'], t, 0.22, 1.1)
        T1 = 1.3                                                                          # main move 0.5 s, the flutter dies out by 1.3 s
        for h in P['halves']:
            def root_rot(tau):
                return (0, math.radians(62 * (1 - math.exp(-6 * tau) * math.cos(8 * tau))), 0)
            _frames(h['pivots'][0], 'rotation_euler', t, t + T1, root_rot)
            for i, pv in enumerate(h['pivots']):
                def fl(tau, i=i):
                    curl = 3.0 * ss(tau / 0.4)                                            # the free end curls down a little more
                    wave = 28 * math.exp(-3.5 * tau) * math.sin(2 * math.pi * 3.2 * tau - 0.8 * i) * min(1.0, i / 3) * ss(tau / 0.08)
                    s = 1 - 0.38 * ss(tau / 0.35)                                          # the stretched tape springs back
                    return (0 if i == 0 else L * s, 0, 0), (0, math.radians(curl + wave), 0), s
                if i > 0:
                    _frames(pv, 'location', t, t + T1, lambda tau, fl=fl: fl(tau)[0])
                    _frames(pv, 'rotation_euler', t, t + T1, lambda tau, fl=fl: fl(tau)[1])
                sg = h['segs'][i]
                _frames(sg, 'location', t, t + T1, lambda tau, fl=fl: (L * fl(tau)[2] / 2, 0, 0))
                _frames(sg, 'scale', t, t + T1, lambda tau, fl=fl: (fl(tau)[2], 1, 1))
    P['actions']['break'] = brk
    return P, parts + [h['root'] for h in halves] + [flash]


# ---------------------------------------------------------------- the two-bar chart
BASE_H = 0.5


def _split(s, n, cast=str, default=()):
    if not s:
        return list(default)
    v = [x.strip() for x in (s.split(',') if ',' in s else s.split())]
    v = [cast(x) for x in v if x]
    return (v + list(default)[len(v):])[:n]


def bars(heights=None, labels=None, values=None, colors=None):
    hs = _split(heights.replace(',', ' ') if heights else None, 2, float, (0.6, 2.8))
    ls = _split(labels, 2, str, ('PART 1', 'PART 2')); vs = _split(values, 2, str, ('340M', '1.7B'))
    cs = _split(colors.replace(',', ' ') if colors else None, 2, str, ('#7f93b8', '#36d17a'))
    dark = M('#1d1d24', 0.35)
    parts = [box((0, 0, BASE_H / 2), (2.4, 0.62, BASE_H), dark, bevel=0.06)]
    white = M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=1.5)
    groups, tops = [], []
    for k, (x, h, c) in enumerate(zip((-0.6, 0.6), hs, cs)):
        glow = (0.9, 2.5)[k]
        col = box((x, 0, BASE_H + h / 2), (0.78, 0.42, h), M(c, 0.4, emit=hexrgb(c), emit_strength=glow), bevel=min(0.09, h / 2.2))
        g = _group(f'Bar{k + 1}', [col], (x, 0, BASE_H)); g.scale = (1, 1, 0.001); groups.append(g)
        lab = text(ls[k], (x, -0.33, BASE_H / 2), 0.26, white, extrude=0.025)
        val = text(vs[k], (0, -0.02, 0), 0.44, white, extrude=0.035)
        bpy.context.view_layer.update()
        for o, wmax in ((lab, 1.08), (val, 1.0)):                                       # long words shrink to fit their bar
            if o.dimensions.x > wmax:
                o.scale = (wmax / o.dimensions.x,) * 3
        bpy.context.view_layer.update()
        pw = max(0.62, val.dimensions.x + 0.26)                                          # a dark tag behind the value, ringed in the bar's colour,
        tag = [val, box((0, 0.06, 0), (pw, 0.08, 0.6), dark, bevel=0.12),                # so it reads on any background
               box((0, 0.1, 0), (pw + 0.08, 0.05, 0.68), M(c, 0.4, emit=hexrgb(c), emit_strength=glow), bevel=0.14)]
        vg = _group(f'Value{k + 1}', tag, (0, 0, 0)); vg.location = (x, -0.05, BASE_H + h + 0.48); vg.scale = (0.001,) * 3
        parts.append(lab); tops.append(vg)
    total = BASE_H + max(hs) + 0.85
    P = {'focus_z': total / 2, 'size': max(0.9, total / 3.9), 'bars': groups, 'vals': tops, 'actions': {}}

    def grow(P, t, o):
        only = int(_num(o, 'only', 0))
        plan = {1: [(0, t, 0.6)], 2: [(1, t, 0.8)], 0: [(0, t, 0.6), (1, t + 1.0, 0.8)]}.get(only, [(0, t, 0.6), (1, t + 1.0, 0.8)])
        for k, t0, d in plan:
            _keys(P['bars'][k], 'scale', [(t0, (1, 1, 0.001)), (t0 + d * 0.85, (1, 1, 1.03)), (t0 + d, (1, 1, 1.0))])
            _keys(P['vals'][k], 'scale', [(t0 + d - 0.01, (0.001,) * 3), (t0 + d + 0.16, (1.18,) * 3), (t0 + d + 0.28, (1.0,) * 3)])
    P['actions']['grow'] = grow
    return P, parts + groups + tops


# ---------------------------------------------------------------- a crumpled t-shirt for a hand
def _shirt_body(color):
    m = M(color, 0.8)
    hem = [(0.23, -0.66), (0.12, -0.63), (0.0, -0.68), (-0.12, -0.64), (-0.23, -0.67)]
    pts = [(-0.08, 0.03), (0.08, 0.03), (0.2, -0.02), (0.34, -0.12), (0.3, -0.29), (0.21, -0.24), (0.22, -0.6)] + hem +           [(-0.22, -0.6), (-0.21, -0.24), (-0.3, -0.29), (-0.34, -0.12), (-0.2, -0.02)]
    body = prism(pts, 0.07, (0, 0, 0), m, bevel=0.03); _crumple(body, strength=0.02, voxel=0.012)
    return body


def shirt(color='#2fb5ff', pose='carry'):
    """Hangs from its collar at the origin (the collar sits in the fist), 0.6 wide, about 0.66 long, front toward -y.
    toss ('to X Y Z; for S', default 0.45; 14 Nov 2026): a held shirt leaves the hand where it is at that moment, flies in an
    arc, turning to lie flat, onto the spot (a heap of clothes), and stays there. Give the hold an 'until' at the toss."""
    g = _group('Shirt', [_shirt_body(color)], (0, 0, 0)); g.rotation_euler = (0, 0, math.radians(10))
    # 'carry' + 'tilt 55': the collar just under the front of the fist, the shirt hangs in front of the legs. The raised arm of
    # 'show' turns the fist differently, so 'pose show' (+ 'tilt 125') hangs it lower and further forward from that fist.
    grip = (0.0, 0.168, 1.064) if pose == 'show' else (0.0, -0.033, 1.03)
    P = {'focus_z': -0.3, 'size': 0.35, 'grip': grip, 'actions': {}}

    def toss(P, t, o):
        from mathutils import Vector, Euler
        S = max(0.2, _num(o, 'for', 0.45)); sc = bpy.context.scene
        now = sc.frame_current; sc.frame_set(F(t)); mw = P['root'].matrix_world.copy(); sc.frame_set(now)
        loc0, q0, _ = mw.decompose(); e0 = q0.to_euler('XYZ')
        to = Vector(o['to'][:3]) if isinstance(o.get('to'), list) and len(o['to']) >= 3 else loc0 + Vector((0, 0.8, -1.0))
        free = _group(P['name'] + '_free', [_shirt_body(color)], (0, 0, 0))
        free.location = loc0; free.rotation_euler = e0
        until = _num(o, 'until', 0.0)                 # 'until T': the tossed shirt is gone again from T (a loop back to frame one)
        visible([free], [(0, False), (t, True)] + ([(until, False)] if until > t else []))
        apex = max(loc0.z, to.z) + 0.55; locs, rots = [], []
        e1 = Euler((math.radians(90), 0.0, e0.z + math.radians(160)))
        for f in range(F(t), F(t + S) + 1):
            u = min(1.0, max(0.0, ((f - 1) / FPS - t) / S)); e = ss(u)
            p = loc0.lerp(to, u); p.z = (1 - u) ** 2 * loc0.z + 2 * u * (1 - u) * apex + u * u * to.z
            locs.append(((f - 1) / FPS, tuple(p))); rots.append(((f - 1) / FPS, tuple(a + (b - a) * e for a, b in zip(e0, e1))))
        _keys(free, 'location', [(t - 0.01, tuple(loc0))] + locs, 'LINEAR'); _keys(free, 'rotation_euler', [(t - 0.01, tuple(e0))] + rots, 'LINEAR')
    P['actions']['toss'] = toss
    return P, [g]


# ---------------------------------------------------------------- the unmade bed (13 Nov 2026: the cleaning race seen from above)
def unmade():
    """Lies on the bedroom's bed: 'at 236.8 1.4 1.16' (the middle of the blanket's top). A pale sheet over the blanket, the orange
    duvet kicked into a heap at the foot, a pillow thrown crooked. make ('for S', default 0.7): the heap spreads flat toward the
    head as the sheet rolls away under it (the bed's own neat orange blanket shows), the pillow flies to the head of the bed,
    and a white starburst pops over the bed. Seen best from above ('top')."""
    orange, sheet_m, white = M('#ff8a3d', 0.85), M('#dbe7f6', 0.8), M('#ffffff', 0.8)
    sh = box((0, 0, 0.018), (2.96, 2.96, 0.03), sheet_m, bevel=0.01)
    for x, y, a in ((-0.7, 0.6, 20), (0.5, 0.2, -10), (-0.1, 1.1, 5)):         # creases in the sheet
        sh2 = box((x, y, 0.036), (0.9, 0.035, 0.01), M('#c4d3e8', 0.8), rot=(0, 0, a), bevel=0); sh2.visible_shadow = False
        sh = sh if isinstance(sh, list) else [sh]; sh.append(sh2)
    sheet = _group('BedSheet', sh, (0, 1.48, 0.018))
    lumps = []
    for (x, y, z), (w, d, hh), a in (((-0.55, -0.95, 0.17), (1.3, 0.8, 0.34), 12), ((0.6, -1.05, 0.14), (1.1, 0.7, 0.28), -18),
                                      ((0.05, -0.5, 0.17), (0.9, 0.6, 0.3), 35), ((-1.0, -0.3, 0.12), (0.7, 0.5, 0.22), 60)):
        lumps.append(_crumple(box((x, y, z), (w, d, hh), orange, rot=(0, 0, a), bevel=0.08), strength=0.06, voxel=0.03))
    heap = _group('BedHeap', lumps, (0, -0.85, 0.0))
    pil = _crumple(box((0, 0, 0), (1.0, 0.55, 0.24), white, bevel=0.1), strength=0.03, voxel=0.025)
    pillow = _group('BedPillow', [pil], (0, 0, 0)); pillow.location = (0.78, 0.5, 0.13); pillow.rotation_euler = (0, 0, math.radians(32))
    burst = _burst('BedDone', r=0.7, w=0.07); burst.location = (0, 0.4, 0.45); burst.rotation_euler = (math.radians(90), 0, 0)
    P = {'focus_z': 0.1, 'size': 1.0, 'view_up': 0.9, 'sheet': sheet, 'heap': heap, 'pillow': pillow, 'burst': burst, 'actions': {}}

    def make(P, t, o):
        S = max(0.35, _num(o, 'for', 0.7))
        _keys(P['heap'], 'scale', [(t, (1, 1, 1)), (t + 0.45 * S, (1.15, 1.7, 0.06))], 'LINEAR')
        _keys(P['heap'], 'location', [(t, (0, -0.85, 0)), (t + 0.45 * S, (0, -0.2, 0.0))], 'LINEAR')
        visible([P['heap']], [(t - 0.02, True), (t + 0.5 * S, False)])
        _keys(P['sheet'], 'scale', [(t + 0.1 * S, (1, 1, 1)), (t + 0.85 * S, (1, 0.001, 1))], 'LINEAR')
        visible([P['sheet']], [(t - 0.02, True), (t + 0.86 * S, False)])
        _keys(P['pillow'], 'location', [(t, (0.78, 0.5, 0.13)), (t + 0.6 * S, (0.0, 2.38, 0.06))])
        _keys(P['pillow'], 'rotation_euler', [(t, (0, 0, math.radians(32))), (t + 0.6 * S, (0, 0, 0))])
        _keys(P['pillow'], 'scale', [(t, (1, 1, 1)), (t + 0.6 * S, (1.95, 1.4, 1.2))])
        visible([P['pillow']], [(t - 0.02, True), (t + 0.62 * S, False)])
        _flash(P['burst'], t + S, 0.35)
    P['actions']['make'] = make
    return P, [sheet, heap, pillow, burst]


# ---------------------------------------------------------------- toys into a toy box, trash into a bin (13 Nov 2026, more chores)
def pickup(what='toys', grow=1.0):
    """A chore on the floor: 'what toys' (four toy blocks, a ball, a toy car and a teddy around the origin, and an open red toy box at
    local x +0.9) or 'what trash' (crumpled paper balls, a can and a juice box, and a grey bin at local x +0.9) or 'what dishes'
    (four plates with food, two cups and a bowl on a table top: 'at X Y 1.21'; a grey tub on the floor in front of the table). collect ('for S',
    default 1.0): the things hop one after another in arcs into the box or bin and vanish inside it, the box squashes as each
    lands and its heap rises. Made to be seen from above ('top'); '@name' framings work too."""
    items = []
    C = (0.9, 0.0, 0.0)                                  # where the box / bin / tub stands (local)
    if what == 'dishes':
        white, rim = M('#f7f7f4', 0.3), M('#9ec9ef', 0.4)
        for k, (x, y) in enumerate(((-0.9, 0.35), (-0.3, -0.3), (0.25, 0.4), (0.8, -0.2))):
            pl = [cyl((x, y, 0.016), 0.17, 0.03, white, verts=32), _torus((x, y, 0.03), 0.155, 0.012, rim, segs=32),
                  _sphere((x + 0.03, y, 0.045), 0.05, M(('#e8a33d', '#d9534f', '#7cc36a', '#f2d16b')[k], 0.7), segs=12)]
            items.append((_group(f'Plate{k}', pl, (x, y, 0.016)), 0.05))
        for k, (x, y, c) in enumerate(((-0.55, -0.45, '#2f7cf6'), (0.55, 0.45, '#ff7eb6'))):
            items.append((_group(f'Cup{k}', [cyl((x, y, 0.07), 0.065, 0.14, M(c, 0.35), verts=24)], (x, y, 0.07)), 0.14))
        bowl = _sphere((0.0, 0.1, 0.06), 0.12, M('#ffd23a', 0.35), segs=24); bowl.scale = (1, 1, 0.55)
        items.append((_group('Bowl', [bowl], (0.0, 0.1, 0.06)), 0.1))
        C = (0.2, -1.45, -1.21)                          # a grey tub on the floor in front of the table
        grey = M('#a9b4c2', 0.45)
        W, D, H, T = 0.7, 0.5, 0.3, 0.035
        tub = [box((C[0], C[1], C[2] + 0.02), (W, D, 0.04), grey, bevel=0.01)]
        tub += [box((C[0], C[1] + sy * (D / 2 - T / 2), C[2] + H / 2), (W, T, H), grey, bevel=0.012) for sy in (-1, 1)]
        tub += [box((C[0] + sx * (W / 2 - T / 2), C[1], C[2] + H / 2), (T, D, H), grey, bevel=0.012) for sx in (-1, 1)]
        cont = _group('Tub', tub, C)
        heap = [cyl((C[0] + dx, C[1] + dy, C[2]), 0.16, 0.03, white, verts=24) for dx, dy in ((-0.1, 0.0), (0.08, 0.04), (0.0, -0.05))]
        TOP = H
    elif what == 'trash':
        paper = M('#f4f4ef', 0.85)
        for nm, x, y, r in (('PaperA', -0.7, 0.35, 0.11), ('PaperB', -0.35, -0.45, 0.1), ('PaperC', 0.05, 0.4, 0.12), ('PaperD', -0.95, -0.25, 0.09), ('PaperE', 0.3, -0.2, 0.1)):
            o = _crumple(_sphere((x, y, r), r, paper, segs=16), strength=0.035, voxel=0.02)
            items.append((_group(nm, [o], (x, y, r)), r))
        can = cyl((-0.15, 0.05, 0.06), 0.06, 0.2, M('#e63946', 0.3, metal=0.6), rot=(0, 90, 25), verts=24)
        items.append((_group('Can', [can], (-0.15, 0.05, 0.06)), 0.06))
        jb = box((-0.6, -0.65, 0.08), (0.11, 0.07, 0.16), M('#3fae5a', 0.5), rot=(0, 90, -30), bevel=0.01)
        items.append((_group('JuiceBox', [jb], (-0.6, -0.65, 0.08)), 0.08))
        grey, dark = M('#8f99a6', 0.4, metal=0.3), M('#3b4350', 0.5)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.5, location=(0.9, 0, 0.25), vertices=48, end_fill_type='NOTHING')
        wall = bpy.context.object; wall.data.materials.append(grey); bpy.ops.object.shade_smooth()
        so = wall.modifiers.new('wall', 'SOLIDIFY'); so.thickness = 0.03; so.offset = -1
        cont = _group('Bin', [wall, cyl((0.9, 0, 0.02), 0.25, 0.04, dark, verts=48), _torus((0.9, 0, 0.5), 0.26, 0.025, dark, segs=48),
                              box((0.9, -0.29, 0.04), (0.16, 0.08, 0.03), dark, bevel=0.01)], (0.9, 0, 0))
        heap = [_crumple(_sphere((0.9 + dx, dy, 0.0), r, paper, segs=12), strength=0.03, voxel=0.02) for dx, dy, r in ((-0.08, 0.05, 0.12), (0.08, -0.05, 0.11), (0.0, 0.1, 0.1))]
        TOP = 0.5
    else:
        cols = ('#ffd23a', '#e63946', '#2f7cf6', '#3fae5a')
        for k, (x, y, a) in enumerate(((-1.0, 0.4, 20), (-0.3, -0.55, -15), (0.2, 0.5, 35), (-0.75, -0.2, 50))):
            o = box((x, y, 0.09), (0.18, 0.18, 0.18), M(cols[k], 0.4, coat=0.5), rot=(0, 0, a), bevel=0.03)
            items.append((_group(f'Block{k}', [o], (x, y, 0.09)), 0.09))
        ball = _sphere((-0.45, 0.25, 0.15), 0.15, M('#ff7eb6', 0.35, coat=0.6), segs=32)
        items.append((_group('ToyBall', [ball], (-0.45, 0.25, 0.15)), 0.15))
        car = [box((0.25, -0.15, 0.09), (0.34, 0.17, 0.09), M('#2fb5ff', 0.35, coat=0.5), bevel=0.03), box((0.22, -0.15, 0.16), (0.16, 0.14, 0.07), M('#dff3ff', 0.2), bevel=0.02)]
        car += [cyl((0.25 + sx * 0.11, -0.15 + sy * 0.09, 0.045), 0.045, 0.03, M('#1d1d24', 0.6), rot=(90, 0, 0), verts=16) for sx in (-1, 1) for sy in (-1, 1)]
        items.append((_group('ToyCar', car, (0.25, -0.15, 0.09)), 0.16))
        fur = M('#b5763d', 0.9)
        bear = [_sphere((-1.0, -0.6, 0.13), 0.13, fur, segs=20), _sphere((-1.0, -0.6, 0.3), 0.1, fur, segs=20),
                _sphere((-1.07, -0.6, 0.38), 0.04, fur, segs=12), _sphere((-0.93, -0.6, 0.38), 0.04, fur, segs=12)]
        items.append((_group('Teddy', bear, (-1.0, -0.6, 0.13)), 0.3))
        red, yel = M('#e63946', 0.5), M('#ffd23a', 0.45)
        W, D, H, T = 0.72, 0.52, 0.4, 0.04
        walls = [box((0.9, 0, 0.02), (W, D, 0.04), red, bevel=0.01), box((0.9, D / 2 - T / 2, H / 2), (W, T, H), red, bevel=0.01), box((0.9, -D / 2 + T / 2, H / 2), (W, T, H), red, bevel=0.01),
                 box((0.9 - W / 2 + T / 2, 0, H / 2), (T, D, H), red, bevel=0.01), box((0.9 + W / 2 - T / 2, 0, H / 2), (T, D, H), red, bevel=0.01)]
        walls += [box((0.9, sy * (D / 2 - T / 2), H), (W + 0.02, T + 0.02, 0.03), yel, bevel=0.008) for sy in (-1, 1)]
        walls += [box((0.9 + sx * (W / 2 - T / 2), 0, H), (T + 0.02, D + 0.02, 0.03), yel, bevel=0.008) for sx in (-1, 1)]
        cont = _group('ToyBox', walls, (0.9, 0, 0))
        heap = [box((0.9 + dx, dy, 0.0), (0.16, 0.16, 0.16), M(c, 0.4), rot=(0, 0, a), bevel=0.02) for dx, dy, c, a in
                ((-0.15, 0.06, '#ffd23a', 10), (0.12, -0.05, '#2f7cf6', -20), (0.0, 0.1, '#e63946', 30), (0.18, 0.1, '#3fae5a', 5))]
        TOP = 0.4
    fg = _group('PickupHeap', heap, C); fg.parent = cont; fg.matrix_parent_inverse = cont.matrix_world.inverted()
    fg.location = (C[0], C[1], C[2] - 0.25)
    P = {'focus_z': 0.2, 'size': 0.7, 'view_up': 0.8, 'items': items, 'basket': cont, 'fill': fg, 'top': TOP, 'c': C, 'actions': {}}
    if grow != 1.0:                                   # 'grow N': everything N times bigger (floor chores only; reads at eye level)
        P['setup'] = lambda P: setattr(P['root'], 'scale', (grow,) * 3)

    def collect(P, t, o):
        S = max(0.5, _num(o, 'for', 1.0)); hop, drop = 0.34, 0.1
        cx, cy, cz = P['c']
        order = sorted(P['items'], key=lambda it: -((it[0].location.x - cx) ** 2 + (it[0].location.y - cy) ** 2))   # the farthest first
        n = len(order); gap = (S - hop - drop) / max(1, n - 1)
        top = (cx, cy, cz + P['top'] + 0.16); inside = (cx, cy, cz + P['top'] * 0.4); lands = []
        for i, (g, _) in enumerate(order):
            t0 = t + i * gap; p0 = tuple(g.location); r0 = tuple(g.rotation_euler); apex = max(p0[2], top[2]) + 0.5
            spin = (math.radians(160 * (1 if i % 2 else -1)), math.radians(70 * ((i % 3) - 1)), math.radians(110))
            pts, rots, scs = [], [], []
            for f in range(F(t0), F(t0 + hop) + 1):
                u = min(1.0, max(0.0, ((f - 1) / FPS - t0) / hop)); e = ss(u) * 0.3 + u * 0.7
                pts.append(((f - 1) / FPS, (p0[0] + (top[0] - p0[0]) * e, p0[1] + (top[1] - p0[1]) * e, (1 - u) ** 2 * p0[2] + 2 * u * (1 - u) * apex + u * u * top[2])))
                rots.append(((f - 1) / FPS, tuple(a + b * ss(u) for a, b in zip(r0, spin)))); scs.append(((f - 1) / FPS, (1 - 0.4 * ss(u),) * 3))
            pts.append((t0 + hop + drop, inside)); scs.append((t0 + hop + drop, (0.001,) * 3))
            _keys(g, 'location', [(t0 - 0.01, p0)] + pts, 'LINEAR'); _keys(g, 'rotation_euler', [(t0 - 0.01, r0)] + rots, 'LINEAR')
            _keys(g, 'scale', [(t0 - 0.01, (1, 1, 1))] + scs, 'LINEAR'); lands.append(t0 + hop + drop * 0.5)

        def squash(dt):
            a = 0.0
            for tl in lands:
                d = dt + t - tl
                if 0 <= d < 0.14:
                    a += 0.12 * math.sin(math.pi * d / 0.14)
            a = min(0.16, a)
            return (1 + a * 0.45, 1 + a * 0.45, 1 - a)
        _frames(P['basket'], 'scale', t, lands[-1] + 0.3, squash)
        k_of = lambda tt: sum(1 for tl in lands if tl <= tt) / len(lands)
        _frames(P['fill'], 'location', t, lands[-1] + 0.3, lambda dt: (cx, cy, cz - 0.25 + (P['top'] - 0.05) * ss(k_of(t + dt) ** 0.8)))
    P['actions']['collect'] = collect
    return P, [g for g, _ in items] + [cont]


BUILDERS = dict(mess=mess, clock=clock, stopwatch=stopwatch, microwave=microwave, tape=tape, bars=bars, shirt=shirt, unmade=unmade, pickup=pickup)
