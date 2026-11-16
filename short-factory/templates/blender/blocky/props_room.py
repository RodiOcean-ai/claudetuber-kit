"""More props for the blocky world (built 7 Nov 2026 for the survival trailer episode): a glass tank with four tiny worlds
inside (jungle that grows from a sprout, desert with a snapping scorpion, forest that catches fire, two ant armies that charge),
a wall calendar (every day crossed, or only three ticks), a phone that buzzes, and a "POST EVERY DAY" sign that breaks.
Each builder returns (P, objects) like the builders in props.py; P['setup'] runs once the prop has its root, and
P['actions'] maps an action name to f(P, t, opt). props.py registers them in BUILD."""
import math
import bpy
from common import hexrgb
from sf_world import box, cyl, empty, parent, text
from blocky_kit import M
from props import _keys, _sphere, visible, F

GLASS = None


def glass():
    global GLASS
    if GLASS is None:
        GLASS = M('#e9f6ff', 0.02, coat=1.0); b = GLASS.node_tree.nodes['Principled BSDF']
        b.inputs['Alpha'].default_value = 0.12                    # see-through: blended alpha reads in every render mode
        GLASS.surface_render_method = 'BLENDED'; GLASS.use_backface_culling = False
    return GLASS


def _group(name, objs, loc=(0, 0, 0)):
    g = empty(name, loc); parent(objs, g)
    return g


def _flicker(ob, t0, t1, base=(1, 1, 1), amp=0.25, step=0.07, seed=0):
    import random
    rnd = random.Random(seed); t = t0
    pts = []
    while t < t1:
        k = 1 + amp * (rnd.random() * 2 - 1); pts.append((t, (base[0] * (2 - k), base[1] * (2 - k), base[2] * k))); t += step
    _keys(ob, 'scale', pts, 'LINEAR')


# ---------------------------------------------------------------- the tank
TW, TD, TH = 0.9, 0.6, 0.62                          # inside the glass: width, depth, height (local; front faces -y)


def tank(kind='jungle'):
    wood, rim = M('#4a3322', 0.6), M('#1d1d24', 0.4)
    parts = [box((0, 0, 0.04), (TW + 0.08, TD + 0.08, 0.08), wood, bevel=0.02)]
    g = glass()
    for c, s in (((0, -TD / 2, 0.08 + TH / 2), (TW, 0.012, TH)), ((0, TD / 2, 0.08 + TH / 2), (TW, 0.012, TH)),
                 ((-TW / 2, 0, 0.08 + TH / 2), (0.012, TD, TH)), ((TW / 2, 0, 0.08 + TH / 2), (0.012, TD, TH))):
        o = box(c, s, g, bevel=0); o.visible_shadow = False; parts.append(o)
    for c, s in (((0, -TD / 2, 0.08 + TH), (TW + 0.02, 0.025, 0.025)), ((0, TD / 2, 0.08 + TH), (TW + 0.02, 0.025, 0.025)),
                 ((-TW / 2, 0, 0.08 + TH), (0.025, TD + 0.02, 0.025)), ((TW / 2, 0, 0.08 + TH), (0.025, TD + 0.02, 0.025))):
        parts.append(box(c, s, rim, bevel=0.005))
    ground = {'jungle': '#2f5d2a', 'desert': '#e6c77d', 'forest': '#4a3420', 'ants': '#ead9b0'}[kind]
    parts.append(box((0, 0, 0.11), (TW - 0.03, TD - 0.03, 0.06), M(ground, 0.95), bevel=0.01))
    P = {'focus_z': 0.38, 'size': 0.42, 'actions': {}}
    extra = globals()['_' + kind](P)
    return P, parts + extra


def _jungle(P):
    """Like his jungle tank: a mossy floor, a pool, ferns and palms, two orange crabs. A sprout alone at first; 'grow' fills
    the tank; 'ask' floats a glowing ? over the sprout."""
    green, dark, lime, stem = M('#3fa34d', 0.6), M('#1f6b2e', 0.6), M('#7cc242', 0.6), M('#6b8f2a', 0.6)
    sprout = [cyl((0, 0, 0.18), 0.008, 0.1, stem), _leaf((0.025, 0, 0.24), 0.03, lime, 30), _leaf((-0.025, 0, 0.24), 0.03, lime, -30)]
    plants = [cyl((0.2, -0.12, 0.172), 0.16, 0.012, M('#2f86c9', 0.05, coat=1.0))]           # the pool, front right
    for x, y, r in ((0.05, -0.2, 0.035), (0.36, -0.06, 0.04), (0.33, -0.22, 0.03), (0.06, -0.05, 0.03)):   # pool rocks
        o = _sphere((x, y, 0.17), r, M('#7d7f86', 0.8), segs=12); o.scale = (1.3, 1, 0.7); plants.append(o)
    for k in range(14):                                # moss bumps over the floor
        x, y = -0.38 + 0.06 * (k % 7) * 1.0, 0.04 + 0.11 * (k // 7)
        o = _sphere((x, y, 0.155), 0.04 + 0.01 * (k % 3), (dark, green, lime)[k % 3], segs=10); o.scale = (1.2, 1, 0.45); plants.append(o)
    for cx, cy, n, size in ((-0.28, 0.12, 7, 0.13), (0.0, 0.18, 8, 0.15), (-0.32, -0.15, 6, 0.1), (0.3, 0.2, 7, 0.12)):    # ferns
        for i in range(n):
            a = 2 * math.pi * i / n
            f = _sphere((cx + 0.6 * size * math.cos(a), cy + 0.6 * size * math.sin(a), 0.2 + 0.03 * (i % 2)), size, (green, dark)[i % 2], segs=12)
            f.scale = (1.0, 0.2, 0.07); f.rotation_euler = (0, math.radians(-30), a); plants.append(f)
    for x, y, h in ((-0.12, 0.2, 0.42), (0.18, 0.22, 0.36)):                                    # two small palms
        plants.append(cyl((x, y, 0.14 + h / 2), 0.016, h, M('#6b4a2a', 0.7)))
        for i in range(6):
            a = 2 * math.pi * i / 6
            f = _sphere((x + 0.06 * math.cos(a), y + 0.06 * math.sin(a), 0.14 + h - 0.01), 0.08, dark, segs=12)
            f.scale = (1.0, 0.25, 0.06); f.rotation_euler = (0, math.radians(-25), a); plants.append(f)
    crab, claw = M('#e8582a', 0.35, coat=0.6), M('#ff8a2a', 0.35, coat=0.6)
    for cx, cy in ((0.0, -0.14), (0.3, -0.03)):                                                 # orange crabs by the pool
        b = _sphere((cx, cy, 0.19), 0.04, crab, segs=14); b.scale = (1.35, 1.0, 0.55); plants.append(b)
        for sx in (-1, 1):
            plants.append(_sphere((cx + sx * 0.055, cy - 0.035, 0.195), 0.022, claw, segs=10))
            plants.append(cyl((cx + sx * 0.015, cy - 0.03, 0.215), 0.004, 0.03, crab))
            plants.append(_sphere((cx + sx * 0.015, cy - 0.03, 0.233), 0.007, M('#ffd23a', 0.3), segs=8))
    q = text('?', (0, 0, 0.48), 0.22, M('#ffd23a', 0.3, emit=hexrgb('#ffd23a'), emit_strength=3.0), extrude=0.02)
    P.update(sprout=sprout, plants=plants, q=q)

    def setup(P):
        g = _group('JunglePlants', P['plants'], (0, 0, 0.14)); g.parent = P['root']; g.scale = (0.001,) * 3; P['plants_g'] = g
        P['q'].parent = P['root']; visible([P['q']], [(0, False)])

    def grow(P, t, o):
        _keys(P['plants_g'], 'scale', [(t, (0.001,) * 3), (t + 0.7, (1.08,) * 3), (t + 0.9, (1.0,) * 3)])

    def ask(P, t, o):
        visible([P['q']], [(0, False), (t, True), (o.get('off', t + 1.2), False)])
        _keys(P['q'], 'location', [(t, (0, 0, 0.42)), (t + 0.3, (0, 0, 0.5))])
    P['setup'] = setup; P['actions'].update(grow=grow, ask=ask)
    return sprout + plants + [q]


def _leaf(loc, r, m, tilt):
    o = _sphere(loc, r, m, segs=12); o.scale = (1.0, 0.35, 0.5); o.rotation_euler = (0, math.radians(tilt), 0)
    return o


def _cactus(x, y, h, m, arms=1):
    parts = [cyl((x, y, 0.14 + h / 2), 0.04, h, m), _sphere((x, y, 0.14 + h), 0.04, m, segs=12)]
    for k in range(arms):
        sx = 1 if k % 2 == 0 else -1; z = 0.14 + h * (0.45 + 0.15 * k)
        parts += [cyl((x + sx * 0.055, y, z), 0.022, 0.06, m, rot=(0, 90, 0)), cyl((x + sx * 0.085, y, z + 0.05), 0.022, 0.1, m),
                  _sphere((x + sx * 0.085, y, z + 0.1), 0.022, m, segs=10)]
    parts.append(_sphere((x, y, 0.14 + h + 0.035), 0.016, M('#ff6fa0', 0.4), segs=10))      # a pink flower on top
    return parts


def _desert(P):
    """Like his desert tank: golden sand, tall cacti with pink flowers, succulents, pale layered rocks, and a yellow scorpion
    seen side-on so its curled tail reads; its claws snap ('snap', until off)."""
    cac, cac2, rock, succ = M('#4f9a48', 0.6), M('#2f7a3a', 0.6), M('#d8d2c6', 0.85), M('#86b97a', 0.5)
    parts = _cactus(-0.33, 0.17, 0.38, cac, 2) + _cactus(-0.14, 0.2, 0.26, cac2, 1) + _cactus(0.34, 0.18, 0.3, cac, 1)
    for x, y, w, h, r in ((0.22, 0.12, 0.22, 0.09, 12), (-0.02, 0.2, 0.18, 0.12, -8), (0.3, -0.18, 0.14, 0.06, 20)):  # layered rocks
        for k in range(2):
            parts.append(box((x + 0.01 * k, y - 0.005 * k, 0.14 + h * (0.3 + 0.5 * k)), (w * (1 - 0.25 * k), 0.12, h * 0.5), rock, rot=(0, r * (1 - 2 * k), 0), bevel=0.02))
    for cx, cy in ((-0.3, -0.16), (0.12, 0.05)):                                                # succulent rosettes
        for i in range(7):
            a = 2 * math.pi * i / 7
            l = _sphere((cx + 0.035 * math.cos(a), cy + 0.035 * math.sin(a), 0.165), 0.04, succ, segs=10)
            l.scale = (1.0, 0.45, 0.35); l.rotation_euler = (0, math.radians(-35), a); parts.append(l)
    for k in range(5):                                 # little sand dunes
        o = _sphere((-0.3 + 0.15 * k, -0.05 + 0.08 * (k % 2), 0.14), 0.08, M('#e6c77d', 0.95), segs=12); o.scale = (1.6, 1, 0.25); parts.append(o)
    gold, amber = M('#e8c35a', 0.3, coat=0.8), M('#c9952f', 0.3, coat=0.8)
    sc = []                                            # the scorpion, built facing -y, turned side-on in setup
    for k in range(5):
        sc.append(_sphere((0, -0.03 + 0.03 * k, 0.17), 0.028 - 0.002 * k, (gold, amber)[k % 2], segs=12))
    for y, z in ((0.125, 0.18), (0.15, 0.21), (0.163, 0.25), (0.155, 0.29), (0.125, 0.315), (0.09, 0.305)):   # the tail curls over the back
        sc.append(_sphere((0, y, z), 0.017, (amber, gold)[int(z * 100) % 2], segs=10))
    sc.append(cyl((0, 0.07, 0.29), 0.006, 0.04, M('#5a2a12', 0.3), rot=(60, 0, 0)))                         # the sting
    for sx in (-1, 1):
        for k in range(4):
            sc.append(box((sx * 0.045, -0.01 + 0.03 * k, 0.15), (0.07, 0.007, 0.007), amber, rot=(0, sx * 25, sx * (15 - 10 * k)), bevel=0))
    claws = []
    for sx in (-1, 1):
        arm = [box((sx * 0.035, -0.07, 0.17), (0.013, 0.07, 0.013), amber, bevel=0)]
        jaw = [_sphere((sx * 0.04, -0.115, 0.17), 0.022, gold, segs=10), box((sx * 0.03, -0.14, 0.17), (0.008, 0.035, 0.012), amber, bevel=0.002)]
        claws.append((sx, arm + jaw))
    P.update(scorpion=sc, claws=claws)

    def setup(P):
        from mathutils import Matrix
        P['claw_p'] = []
        body = empty('Scorpion', (0, 0, 0.14)); parent(P['scorpion'], body); body.parent = P['root']
        for sx, objs in P['claws']:
            p = empty('Claw', (sx * 0.03, -0.04, 0.17)); parent(objs, p)
            p.parent = body; p.matrix_parent_inverse = Matrix.Identity(4); p.location = (sx * 0.03, -0.04, 0.03)   # in the body's space
            P['claw_p'].append((sx, p))
        body.location = (-0.04, -0.06, 0.14); body.rotation_euler = (0, 0, math.radians(-60))           # side-on, claws to the left
        body.scale = (2.0,) * 3                        # big enough to read on a phone

    def snap(P, t, o):
        t1 = o.get('off', t + 3.0); s = 0.0; pts = {sx: [] for sx, _ in P['claw_p']}
        while t + s < t1:
            for sx, _ in P['claw_p']:
                ang = math.radians(sx * (18 if int(s / 0.18) % 2 else -6))
                pts[sx].append((t + s, (0, 0, ang)))
            s += 0.18
        for sx, p in P['claw_p']:
            _keys(p, 'rotation_euler', pts[sx], 'LINEAR')
    P['setup'] = setup; P['actions']['snap'] = snap
    return parts + sc + [o for _, objs in claws for o in objs]


def _forest(P):
    """Small trees; 'burn' lights flickering flames on them (until off)."""
    trunk, leaf = M('#6b4a2a', 0.7), M('#2f6b34', 0.7)
    fire_o, fire_y = M('#ff6a00', 0.4, emit=hexrgb('#ff6a00'), emit_strength=6.0), M('#ffd23a', 0.4, emit=hexrgb('#ffd23a'), emit_strength=6.0)
    fire_r = M('#e0301e', 0.4, emit=hexrgb('#ff3a1a'), emit_strength=5.0)
    trees, flames = [], []
    for x, y, h in ((-0.3, 0.12, 0.34), (-0.1, 0.18, 0.42), (0.12, 0.08, 0.38), (0.32, 0.16, 0.3), (-0.22, -0.12, 0.26), (0.22, -0.14, 0.28)):
        trees += [cyl((x, y, 0.14 + h * 0.3), 0.02, h * 0.6, trunk), cyl((x, y, 0.14 + h * 0.75), 0.08, h * 0.6, leaf, verts=10)]
        for k, (m, r, hh, dx) in enumerate(((fire_r, 0.13, 0.2, 0.0), (fire_o, 0.1, 0.34, -0.03), (fire_o, 0.07, 0.26, 0.05), (fire_y, 0.05, 0.2, 0.0))):
            bpy.ops.mesh.primitive_cone_add(radius1=r, depth=hh, location=(x + dx, y - 0.015 * k, 0.14 + h * 0.6 + hh / 2), vertices=12)
            o = bpy.context.object; o.data.materials.append(m); o.rotation_euler = (0, math.radians(8 * (k - 1.5)), 0); flames.append(o)
    P.update(flames=flames)

    def setup(P):
        visible(P['flames'], [(0, False)])

    def burn(P, t, o):
        t1 = o.get('off', t + 3.0)
        visible(P['flames'], [(0, False), (t, True), (t1, False)])
        for i, f in enumerate(P['flames']):
            _flicker(f, t, t1, amp=0.35, step=0.06, seed=i)
    P['setup'] = setup; P['actions']['burn'] = burn
    return trees + flames


def _ant(x, y, heading, m, k=1.0):
    """One ant: head, thorax, a long abdomen, six legs and two feelers, pointing along heading (degrees, 0 = +x)."""
    c, s = math.cos(math.radians(heading)), math.sin(math.radians(heading))
    at = lambda f, side=0.0, z=0.16: (x + (c * f - s * side) * k, y + (s * f + c * side) * k, z)
    parts = [_sphere(at(0.04), 0.016 * k, m, segs=10), _sphere(at(0.012), 0.012 * k, m, segs=10)]
    ab = _sphere(at(-0.03), 0.022 * k, m, segs=10); ab.scale = (1.5, 1.0, 0.9); ab.rotation_euler = (0, 0, math.radians(heading)); parts.append(ab)
    for side in (-1, 1):
        for f in (0.0, 0.012, 0.024):
            leg = box(at(f, side * 0.022, 0.15), (0.005 * k, 0.04 * k, 0.004 * k), m, rot=(0, 0, heading + side * (20 - 1500 * f)), bevel=0)
            parts.append(leg)
        parts.append(box(at(0.062, side * 0.012, 0.17), (0.03 * k, 0.003 * k, 0.003 * k), m, rot=(0, 0, heading + side * 30), bevel=0))
    return parts


def _ants(P):
    """Like his ant war cover, seen from above: pale speckled sand, a red army on the left and a black army on the right
    in lines; 'charge' runs them at each other and they scuffle."""
    red, black = M('#d2461f', 0.35, coat=0.6), M('#1b1414', 0.3, coat=0.8)
    P['view_up'] = 0.95                                # high enough that the tank's rim sits below the room behind, low enough to see it side-on
    specks = [box((-0.4 + 0.83 * ((k * 37) % 29) / 29, -0.26 + 0.52 * ((k * 17) % 23) / 23, 0.142), (0.008, 0.008, 0.003), M('#b89a6a', 0.9), bevel=0) for k in range(40)]
    armies = []
    for side, m in ((-1, red), (1, black)):
        ants = []
        for row in range(2):
            for k in range(5):
                x, y = side * (0.18 + 0.1 * row), -0.2 + 0.1 * k + 0.05 * row
                ants += _ant(x, y, 0 if side < 0 else 180, m, k=1.3)
        armies.append((side, ants))
    P.update(armies=armies)

    def setup(P):
        P['army_g'] = []
        for side, ants in P['armies']:
            g = _group('Army', ants); g.parent = P['root']; P['army_g'].append((side, g))

    def charge(P, t, o):
        for side, g in P['army_g']:
            pts = [(t, (0, 0, 0)), (t + 0.7, (-side * 0.1, 0, 0))]
            for k in range(1, 8):                     # a scuffle: small back-and-forth after they meet
                pts.append((t + 0.7 + 0.1 * k, (-side * (0.1 + (0.015 if k % 2 else -0.01)), 0, 0)))
            _keys(g, 'location', pts, 'LINEAR')
    P['setup'] = setup; P['actions']['charge'] = charge
    return specks + [o for _, ants in armies for o in ants]


# ---------------------------------------------------------------- calendar, phone, sign
def calendar(kind='full'):
    """A wall calendar facing -y. 'full': a red cross on every day; 'three': only three green ticks."""
    board, red, green, ink = M('#ffffff', 0.6), M('#e63946', 0.4), M('#14853a', 0.4), M('#c9ced8', 0.6)
    parts = [box((0, 0, 0), (1.6, 0.04, 1.3), board, bevel=0.02), box((0, -0.025, 0.52), (1.6, 0.02, 0.26), red if kind == 'full' else green, bevel=0.01)]
    parts.append(text('EVERY DAY' if kind == 'full' else 'THIS YEAR', (0, -0.04, 0.52), 0.15, M('#ffffff', 0.4), extrude=0.005))
    marks, cells = [], [(c, r) for r in range(5) for c in range(7)]
    for c, r in cells:
        x, z = -0.6 + 0.2 * c, 0.25 - 0.2 * r
        parts.append(box((x, -0.022, z), (0.17, 0.004, 0.17), ink, bevel=0))
        if kind == 'full':
            marks.append([box((x, -0.03, z), (0.18, 0.006, 0.03), red, rot=(0, a, 0), bevel=0) for a in (45, -45)])
        elif (c, r) in ((1, 0), (4, 2), (2, 4)):        # a bold check mark on a pale green day (owner: the first ones were unclear)
            parts.append(box((x, -0.024, z), (0.17, 0.004, 0.17), M('#d6f5df', 0.6), bevel=0))
            marks.append([box((x - 0.045, -0.032, z - 0.01), (0.075, 0.008, 0.035), green, rot=(0, 45, 0), bevel=0.004),
                          box((x + 0.018, -0.032, z + 0.015), (0.15, 0.008, 0.035), green, rot=(0, -58, 0), bevel=0.004)])
    P = {'focus_z': 0.0, 'size': 0.55, 'marks': marks, 'actions': {}}

    def stamp(P, t, o):                               # crosses slam on one after another (frantic posting)
        for i, mk in enumerate(P['marks']):
            for m in mk:
                _keys(m, 'scale', [(0, (1, 1, 1)), (max(0.0, t), (0.001,) * 3), (t + 0.06 * i, (0.001,) * 3), (t + 0.06 * i + 0.08, (1.3,) * 3), (t + 0.06 * i + 0.14, (1, 1, 1))], 'LINEAR')
    P['actions']['stamp'] = stamp
    return P, parts + [m for mk in marks for m in mk]


def phone():
    """A phone lying on a desk, screen up; 'buzz' shakes it and flashes the screen (until off)."""
    scr = M('#2f7cf6', 0.3, emit=hexrgb('#7cc4ff'), emit_strength=0.4); scr.name = 'PhoneScreen'
    parts = [box((0, 0, 0.018), (0.32, 0.6, 0.035), M('#1b1d24', 0.3), bevel=0.03), box((0, 0, 0.037), (0.28, 0.54, 0.004), scr, bevel=0)]
    P = {'focus_z': 0.03, 'size': 0.25, 'screen': scr, 'actions': {}}

    def buzz(P, t, o):
        t1, s, pts, rot = o.get('off', t + 2.0), 0.0, [], []
        x0, y0, z0 = P['loc']
        while t + s < t1:
            k = 1 if int(s / 0.033) % 2 else -1
            pts.append((t + s, (x0 + 0.008 * k, y0, z0))); rot.append((t + s, (0, 0, math.radians(P['turn'] + 3 * k))))
            s += 0.033
        pts.append((t1, (x0, y0, z0))); rot.append((t1, (0, 0, math.radians(P['turn']))))
        _keys(P['root'], 'location', pts, 'CONSTANT'); _keys(P['root'], 'rotation_euler', rot, 'CONSTANT')
        n = P['screen'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
        for tt, v in ((t, 0.4), (t + 0.05, 4.0), (t1, 4.0), (t1 + 0.05, 0.4)):
            n.default_value = v; n.keyframe_insert('default_value', frame=F(tt))
    P['actions']['buzz'] = buzz
    return P, parts


def sign():
    """A wooden 'POST EVERY DAY' sign on a wall (facing -y); 'break' cracks it in two and both halves fall to the floor."""
    wood, ink = M('#b5763d', 0.6), M('#1d1d24', 0.5)
    halves = []
    for sx, word in ((-1, 'POST EV'), (1, 'ERY DAY')):
        objs = [box((sx * 0.55, 0, 0), (1.1, 0.06, 0.45), wood, bevel=0.015),       # the crack runs between EV and ERY
                text(word, (sx * 0.008, -0.04, -0.01), 0.2, ink, extrude=0.01, align='RIGHT' if sx < 0 else 'LEFT')]
        halves.append((sx, objs))
    P = {'focus_z': 0.0, 'size': 0.55, 'halves': halves, 'actions': {}}

    def setup(P):
        P['pivots'] = []
        for sx, objs in P['halves']:
            p = empty('SignHalf', (sx * 1.1, 0, 0.2)); parent(objs, p); p.parent = P['root']; P['pivots'].append((sx, p))

    def brk(P, t, o):
        drop = -(P['loc'][2]) + 0.3                   # local z of the floor (plus a little)
        for sx, p in P['pivots']:
            base = (sx * 1.1, 0, 0.2)
            _keys(p, 'rotation_euler', [(t, (0, 0, 0)), (t + 0.1, (0, math.radians(-sx * 20), 0)), (t + 0.35, (0, math.radians(-sx * 70), 0)),
                                        (t + 0.75, (0, math.radians(-sx * 95), 0))])
            _keys(p, 'location', [(t + 0.3, base), (t + 0.75, (base[0] + sx * 0.1, -0.15, drop))])
    P['setup'] = setup; P['actions']['break'] = brk
    return P, [o for _, objs in halves for o in objs]


def bench(w=4.0):
    """A long low workbench (top at z 1.0) to stand tanks on; front faces -y."""
    top, leg = M('#9a6a3c', 0.6), M('#3a3f4c', 0.5)
    parts = [box((0, 0, 0.96), (w, 0.9, 0.08), top, bevel=0.02)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box((sx * (w / 2 - 0.1), sy * 0.35, 0.46), (0.08, 0.08, 0.92), leg, bevel=0.01))
    return {'focus_z': 1.0, 'size': 1.0}, parts


def uploads(n=12):
    """Video cards (a white thumbnail with a red play badge) that shoot up out of a desk one after another and fly off the
    top of the picture: someone posting non-stop. 'burst' (until off) launches one every 0.14 s, reusing the cards."""
    from props import play_badge
    cards = []
    for i in range(n):
        objs = [box((0, 0, 0), (0.46, 0.02, 0.28), M('#ffffff', 0.4), bevel=0.02)] + play_badge(0.0, 0.2, y=-0.035)
        cards.append(objs)
    P = {'focus_z': 0.0, 'size': 0.5, 'cards': cards, 'actions': {}}

    def setup(P):
        import random
        P['card_g'] = []
        for i, objs in enumerate(P['cards']):
            g = _group('UploadCard', objs); g.parent = P['root']; g.scale = (0.001,) * 3; P['card_g'].append(g)
        P['rnd'] = random.Random(11)

    def burst(P, t, o):
        t1, k, rnd = o.get('off', t + 2.0), 0, P['rnd']
        while t + 0.14 * k < t1:
            g = P['card_g'][k % len(P['card_g'])]; t0 = t + 0.14 * k
            side = 1 if k % 2 else -1                  # left and right in turn, never across the face in the middle
            x0 = side * rnd.uniform(0.45, 0.7); dx = side * rnd.uniform(0.75, 1.15); spin = rnd.uniform(-40, 40)
            _keys(g, 'location', [(t0, (x0, 0, 0)), (t0 + 0.55, (dx, -0.2, 1.5 + rnd.uniform(0, 0.5))), (t0 + 0.9, (dx * 1.3, -0.3, 2.6))], 'LINEAR')
            _keys(g, 'rotation_euler', [(t0, (0, 0, 0)), (t0 + 0.9, (0, math.radians(spin), 0))], 'LINEAR')
            _keys(g, 'scale', [(t0 - 0.01, (0.001,) * 3), (t0, (0.3,) * 3), (t0 + 0.15, (1.0,) * 3), (t0 + 0.8, (1.0,) * 3), (t0 + 0.9, (0.001,) * 3)], 'LINEAR')
            k += 1
    P['setup'] = setup; P['actions']['burst'] = burst
    return P, [o for objs in cards for o in objs]


BUILDERS = dict(tank_jungle=lambda: tank('jungle'), tank_desert=lambda: tank('desert'), tank_forest=lambda: tank('forest'),
                tank_ants=lambda: tank('ants'), calendar_full=lambda: calendar('full'), calendar_three=lambda: calendar('three'),
                phone=phone, sign=sign, bench=bench, uploads=uploads)
