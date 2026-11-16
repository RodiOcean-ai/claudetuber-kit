"""Story props for the blocky world (built 12 Nov 2026 for the squirrel episode): a satellite, stacks of cash, a backyard
squirrel obstacle course, a shark cage, a shark, thought bubbles with an icon inside, a magnifying glass. Nothing carries a
word, a letter, a number or a logo: every mark on them is a shape.
Each builder returns (P, objects) like the builders in props.py; P['setup'] runs once the prop has its root, P['actions'] maps an
action name to f(P, t, opt). scene.py registers BUILDERS and hands the builder the first row's keywords listed in KW; an
action row's options arrive as lists of numbers ('to 1 2 3' -> opt['to'] == [1.0, 2.0, 3.0]; a bare word -> True).

Kinds, their actions and options (table rows: '| 0.0 | @name | kind | | at X Y Z; turn N | |', then '| t | @name | action | | options | |'):
- satellite (1.4 high, dish toward -y): glow (warm gold light rising over 0.4 s) | dim (light off over 0.4 s, the foil greys) |
  squash (flattened to 35 % in 0.12 s, a small bounce, stays flat) | float (up N, default 0.6: rises over 1 s, then bobs and
  turns slowly until the scene ends) | flash (a white burst at the dish, 0.25 s).
- cash (three banded stacks of green notes): slide (to X Y Z: moves there over 0.5 s and shrinks to nothing as it arrives).
- maze (a squirrel obstacle course on a round patch of grass, 4 long, 2 high): static.
- cage (a round shark cage of upright bars; first row 'tall N' (default 2.3) and 'radius N' (default 1.2)): static. A full-size
  person is 2.75 tall: give the cage 'tall 3.2' for an adult, or the top ring crosses the face.
- shark (2.6 long, nose toward -y, belly on z=0): circle (around X Y; radius R; height Z; for S; optional speed REVS_PER_S and
  'back' for the other way round): swims round that point nose first, tail wagging, then stays where it stopped.
- bubble (0.9 across, centred on its own origin; first row 'icon squirrel | shark | scammer | satellite'): orbit (around X Y Z;
  radius R; speed REVS_PER_S; phase DEG: circles that point in an upright ring facing -y whose lower half leans toward the
  camera, so the bubbles pass in front of a body and not through it; until the scene ends or a 'stop') | stop | flare (grows
  to 1.6x, the rim glows red-gold) | fade (shrinks to nothing over 0.4 s).
- magnifier: made for a hand: 'hold <who>; until T; tilt N' on its first row, with the move 'show' and 'tilt 125' (held up
  beside the head) or 'carry' and 'tilt 55' (in front of the chest)."""
import math
import bpy
from common import FPS, hexrgb
from sf_world import box, cyl, empty, parent
from blocky_kit import M
from animals import prism
from props import _keys, _sphere, visible, F

ss = lambda u: 0 if u <= 0 else 1 if u >= 1 else u * u * (3 - 2 * u)
KW = {'bubble': {'icon': str}, 'cage': {'tall': float, 'radius': float}}      # first-row keywords the table may pass to a builder


# ---------------------------------------------------------------- helpers
def _group(name, objs, loc=(0, 0, 0)):
    g = empty(name, loc); parent(objs, g)
    return g


def _torus(loc, R, r, m, rot=(0, 0, 0), segs=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=tuple(math.radians(a) for a in rot),
                                     major_segments=segs, minor_segments=12)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def _cone(loc, r1, r2, depth, m, rot=(0, 0, 0), verts=32, smooth=True):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=loc, vertices=verts, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.data.materials.append(m)
    if smooth:
        bpy.ops.object.shade_smooth()
    return o


def _rod(p, q, r, m):
    """A thin round bar from p to q (both in the x-z plane of the same y)."""
    dx, dz = q[0] - p[0], q[2] - p[2]
    return cyl(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2), r, math.hypot(dx, dz), m, rot=(0, math.degrees(math.atan2(dx, dz)), 0), verts=12)


def _socket_keys(sock, pts):
    for t, v in pts:
        sock.default_value = v; sock.keyframe_insert('default_value', frame=F(t))


def _num(o, key, default, i=0):
    v = o.get(key)
    return v[i] if isinstance(v, list) and len(v) > i and isinstance(v[i], float) else default


def _stay(P, t):
    """From t on the camera bank finds the prop where it is now."""
    if 'track' in P:
        for f in range(F(t), max(P['track']) + 1):
            P['track'][f] = (*P['loc'], P['turn'])


def _move(P, t0, t1, fn, turn=True):
    """Key the prop every frame from t0 to t1 along fn(t) -> ((x, y, z), (rx, ry, rz) in degrees) and tell the camera bank
    where it is. It stays where it ends."""
    locs, rots, rot = [], [], (0, 0, P['turn'])
    for f in range(F(t0), F(t1) + 1):
        tt = (f - 1) / FPS; loc, rot = fn(tt)
        locs.append((tt, tuple(loc))); rots.append((tt, tuple(math.radians(r) for r in rot)))
        if 'track' in P:
            P['track'][f] = (*loc, rot[2])
    _keys(P['root'], 'location', locs, 'LINEAR')
    if turn:
        _keys(P['root'], 'rotation_euler', rots, 'LINEAR'); P['turn'] = rot[2]
    P['loc'] = tuple(locs[-1][1]); _stay(P, t1)


# ---------------------------------------------------------------- satellite
def _sat_parts(gold):
    """A satellite around its own origin, standing on its engine bell on z=0, the dish toward -y."""
    blue, line, white, grey = M('#2f6fe0', 0.35, coat=0.6), M('#e9edf3', 0.45), M('#ffffff', 0.4), M('#8f98a8', 0.35, metal=0.5)
    parts = [box((0, 0, 0.62), (0.62, 0.56, 0.8), gold, bevel=0.07),                      # the gold-foil body
             _cone((0, 0, 0.11), 0.2, 0.1, 0.22, grey),                                   # the engine bell it stands on
             box((0, 0, 1.06), (0.36, 0.32, 0.1), white, bevel=0.03),
             cyl((0.1, 0.06, 1.24), 0.022, 0.28, grey, verts=12), _sphere((0.1, 0.06, 1.39), 0.05, M('#e63946', 0.4), segs=16)]   # the short antenna
    for sx in (-1, 1):                                                                    # two solar-panel wings
        parts += [box((sx * 0.4, 0, 0.66), (0.2, 0.06, 0.06), grey, bevel=0.015), box((sx * 0.84, 0, 0.66), (0.7, 0.05, 0.46), blue, bevel=0.02)]
        for sy in (-1, 1):                                                                # the cells, on both faces
            parts += [box((sx * 0.84 + dx, sy * 0.028, 0.66), (0.026, 0.012, 0.46), line, bevel=0) for dx in (-0.117, 0.117)]
            parts.append(box((sx * 0.84, sy * 0.028, 0.66), (0.7, 0.012, 0.026), line, bevel=0))
    parts += [_cone((0, -0.36, 0.66), 0.3, 0.07, 0.16, white, rot=(-90, 0, 0), verts=48),          # the dish, open toward -y
              cyl((0, -0.445, 0.66), 0.2, 0.012, M('#dfe5ee', 0.5), rot=(90, 0, 0)),
              cyl((0, -0.52, 0.66), 0.016, 0.17, grey, rot=(90, 0, 0), verts=12), _sphere((0, -0.61, 0.66), 0.045, grey, segs=16)]
    return parts


SAT_GOLD, SAT_GREY, SAT_GLOW, SAT_HALO = '#f0b429', '#a89f8c', 0.9, 0.4      # foil, dimmed foil, glow strength, halo strength


def _halo_material(color):
    """A soft round glow: light in the middle, nothing at the edge. 'Amount' (a Value node) turns it up and down."""
    m = bpy.data.materials.new('Halo'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*hexrgb(color), 1); em.inputs['Strength'].default_value = 1.2
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; inv.use_clamp = True
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.2
    amt = nt.nodes.new('ShaderNodeValue'); amt.name = 'Amount'; amt.outputs[0].default_value = 0.0
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    nt.links.new(lw.outputs['Facing'], inv.inputs[1]); nt.links.new(inv.outputs[0], pw.inputs[0]); nt.links.new(pw.outputs[0], mul.inputs[0])
    nt.links.new(amt.outputs[0], mul.inputs[1]); nt.links.new(mul.outputs[0], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = True
    return m


def satellite():
    gold = M(SAT_GOLD, 0.32, metal=0.6, emit=hexrgb('#ff8a1a'), emit_strength=0.0).copy(); gold.name = 'SatelliteFoil'   # its own: it glows and greys
    parts = _sat_parts(gold)
    hm = _halo_material('#ffc24a'); halo = _sphere((0, 0, 0.64), 0.95, hm, segs=32); halo.visible_shadow = False; parts.append(halo)   # the glow round the body
    amount = hm.node_tree.nodes['Amount'].outputs[0]
    white = M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=8.0)
    burst = [_sphere((0, 0, 0), 0.14, white, segs=16)]                                    # the flash at the dish: a ball and eight streaks
    for i in range(8):
        a = 2 * math.pi * i / 8; L = 0.34 if i % 2 == 0 else 0.2
        burst.append(box(((0.17 + L / 2) * math.sin(a), 0, (0.17 + L / 2) * math.cos(a)), (0.05, 0.05, L), white, rot=(0, math.degrees(a), 0), bevel=0))
    for o in burst:
        o.visible_shadow = False
    flash = _group('SatelliteFlash', burst, (0, 0, 0)); flash.location = (0, -0.66, 0.66); flash.scale = (0.001,) * 3
    P = {'focus_z': 0.7, 'size': 0.75, 'foil': gold, 'flash': flash, 'glow_now': 0.0, 'grey_now': 0.0, 'actions': {}}
    b = gold.node_tree.nodes['Principled BSDF']

    def tone(k):
        return (*(g + (d - g) * k for g, d in zip(hexrgb(SAT_GOLD), hexrgb(SAT_GREY))), 1)

    def glow(P, t, o):
        _socket_keys(b.inputs['Emission Strength'], [(t, P['glow_now']), (t + 0.4, SAT_GLOW)])
        _socket_keys(b.inputs['Base Color'], [(t, tone(P['grey_now'])), (t + 0.4, tone(0.0))])
        _socket_keys(amount, [(t, P['glow_now'] / SAT_GLOW * SAT_HALO), (t + 0.4, SAT_HALO)])
        P['glow_now'], P['grey_now'] = SAT_GLOW, 0.0

    def dim(P, t, o):
        _socket_keys(b.inputs['Emission Strength'], [(t, P['glow_now']), (t + 0.4, 0.0)])
        _socket_keys(b.inputs['Base Color'], [(t, tone(P['grey_now'])), (t + 0.4, tone(0.6))])
        _socket_keys(amount, [(t, P['glow_now'] / SAT_GLOW * SAT_HALO), (t + 0.4, 0.0)])
        P['glow_now'], P['grey_now'] = 0.0, 0.6

    def squash(P, t, o):
        _keys(P['root'], 'scale', [(t, (1, 1, 1)), (t + 0.12, (1.3, 1.3, 0.29)), (t + 0.22, (1.2, 1.2, 0.43)), (t + 0.32, (1.25, 1.25, 0.35))])

    def float_(P, t, o):
        up = _num(o, 'up', 0.6); (x0, y0, z0), a0 = P['loc'], P['turn']

        def fn(tt):
            u = tt - t; k = ss((u - 0.8) / 0.6)
            return (x0, y0, z0 + up * ss(u / 1.0) + 0.07 * k * math.sin(2 * math.pi * 0.45 * (u - 0.8))), (3 * k * math.sin(2 * math.pi * 0.3 * u), 0, a0 + 14 * max(u - 0.3, 0.0))
        _move(P, t, P.get('t_end', t + 6.0) + 0.1, fn)

    def flash_(P, t, o):
        _keys(P['flash'], 'scale', [(t - 0.02, (0.001,) * 3), (t + 0.05, (1.25,) * 3), (t + 0.14, (1.0,) * 3), (t + 0.25, (0.001,) * 3)], 'LINEAR')
    P['actions'].update(glow=glow, dim=dim, squash=squash, float=float_, flash=flash_)
    return P, parts + [flash]


# ---------------------------------------------------------------- cash
def cash():
    green, dark, band, pale = M('#3fae5a', 0.6), M('#2a8244', 0.6), M('#f6ecd2', 0.7), M('#93dba3', 0.6)
    parts = []
    for k, x in enumerate((-0.58, 0.0, 0.58)):
        h = 0.34 if k == 1 else 0.26                                                      # the middle stack a bundle taller
        parts.append(box((x, 0, h / 2), (0.5, 0.27, h), green, bevel=0.025))
        parts += [box((x, 0, z), (0.506, 0.276, 0.012), dark, bevel=0) for z in ([0.085, 0.17, 0.255] if k == 1 else [0.085, 0.17])]   # the bundles
        parts.append(box((x, 0, h / 2), (0.13, 0.285, h + 0.012), band, bevel=0.008))                                                  # the paper band
        for sx in (-1, 1):                                                                # the note's pale ovals, on top
            o = cyl((x + sx * 0.155, 0, h + 0.001), 0.06, 0.008, pale, verts=24); o.scale = (1.0, 1.35, 1.0); parts.append(o)
    P = {'focus_z': 0.16, 'size': 0.5, 'actions': {}}

    def slide(P, t, o):
        to = tuple(o['to'][:3]) if isinstance(o.get('to'), list) and len(o['to']) >= 3 else P['loc']
        _keys(P['root'], 'location', [(t, P['loc']), (t + 0.5, to)])
        _keys(P['root'], 'scale', [(t, (1, 1, 1)), (t + 0.22, (1, 1, 1)), (t + 0.5, (0.001,) * 3)])
        a = P['loc']
        if 'track' in P:
            for f in range(F(t), F(t + 0.5) + 1):
                u = ss(((f - 1) / FPS - t) / 0.5); P['track'][f] = (*(p + (q - p) * u for p, q in zip(a, to)), P['turn'])
        P['loc'] = to; _stay(P, t + 0.5)
    P['actions']['slide'] = slide
    return P, parts


# ---------------------------------------------------------------- the squirrel obstacle course
def maze():
    wood, plank, rope = M('#a8703a', 0.7), M('#dba85e', 0.65), M('#efe0b0', 0.8)
    grass, grass2, red, yellow, steel = M('#62c24c', 0.9), M('#48a83a', 0.9), M('#e63946', 0.4), M('#ffd23a', 0.4), M('#aab2bf', 0.3, metal=0.6)
    parts = [cyl((0, 0, 0.03), 2.35, 0.06, grass, verts=96)]                              # a round patch of grass
    for k in range(11):                                                                   # darker tufts
        a = 2.4 * k; r = 0.75 + 0.14 * k
        parts.append(box((r * math.cos(a), 0.55 * r * math.sin(a) - 0.5 * (1 if k % 2 else -1), 0.085), (0.16, 0.14, 0.09), grass2, rot=(0, 0, 40 * k), bevel=0.035))
    post = lambda x, y, h, w=0.14: parts.append(box((x, y, 0.06 + h / 2), (w, w, h), wood, bevel=0.03))
    deck = lambda x, z, w=0.5, d=0.5: parts.append(box((x, 0, z), (w, d, 0.07), plank, bevel=0.02))
    # a ramp with rungs up to the start tower
    parts.append(box((-1.86, 0, 0.53), (1.08, 0.3, 0.05), plank, rot=(0, -62, 0), bevel=0.015))
    for u in (0.2, 0.4, 0.6, 0.8):
        parts.append(box((-2.11 + 0.5 * u, 0, 0.07 + 0.95 * u + 0.03), (0.05, 0.34, 0.05), wood, rot=(0, -62, 0), bevel=0.012))
    post(-1.5, 0, 0.93); deck(-1.5, 1.03)
    # the rope bridge: sagging planks between two hand ropes
    pts = [(-1.27 + 1.14 * k / 7, 1.03 - 0.11 * math.sin(math.pi * k / 7)) for k in range(8)]
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        parts.append(box(((xa + xb) / 2, 0, (za + zb) / 2 + 0.005), (0.13, 0.4, 0.04), plank, rot=(0, -math.degrees(math.atan2(zb - za, xb - xa)), 0), bevel=0.012))
        for sy in (-1, 1):
            parts.append(_rod((xa, sy * 0.21, za + 0.3), (xb, sy * 0.21, zb + 0.3), 0.016, rope))
            parts.append(cyl(((xa + xb) / 2, sy * 0.21, (za + zb) / 2 + 0.16), 0.01, 0.3, rope, verts=8))
    for x in (-1.27, -0.13):                                                              # the posts the ropes hang from
        for sy in (-1, 1):
            parts.append(box((x, sy * 0.21, 1.2), (0.06, 0.06, 0.34), wood, bevel=0.015))
    post(0.1, 0, 0.93); deck(0.1, 1.03, w=0.46)
    # a small running wheel on an axle
    wx, wz, wr = 0.86, 1.27, 0.44
    wheel = [box((wx, 0.42, 0.06 + wz / 2), (0.12, 0.12, wz), wood, bevel=0.03), cyl((wx, 0.12, wz), 0.05, 0.68, steel, rot=(90, 0, 0), verts=16)]
    for sy in (-1, 1):
        wheel.append(_torus((wx, sy * 0.2, wz), wr, 0.04, yellow, rot=(90, 0, 0)))
        wheel += [box((wx, sy * 0.2, wz), (2 * wr, 0.02, 0.03), steel, rot=(0, a, 0), bevel=0.006) for a in (0, 60, 120)]
    for k in range(14):
        a = 2 * math.pi * k / 14
        wheel.append(cyl((wx + wr * math.cos(a), 0, wz + wr * math.sin(a)), 0.024, 0.42, red, rot=(90, 0, 0), verts=10))
    g = _group('MazeWheel', wheel, (wx, 0, 0)); g.rotation_euler = (0, 0, math.radians(-38)); parts.append(g)   # turned, so it reads as a drum to run in
    # the end platform with the walnut, under a little flag
    post(1.72, 0, 1.43, w=0.16); deck(1.72, 1.53, w=0.56)
    nut = _sphere((1.68, -0.05, 1.7), 0.14, M('#9a6232', 0.7), segs=20); nut.scale = (1.0, 0.92, 0.95)
    parts += [nut, _torus((1.68, -0.05, 1.7), 0.135, 0.017, M('#6e4320', 0.7), rot=(0, 90, 0), segs=32),
              cyl((1.93, 0.18, 1.8), 0.02, 0.5, steel, verts=10), prism([(0, 0), (0.3, -0.09), (0, -0.18)], 0.03, (1.95, 0.18, 2.04), red, bevel=0.008)]
    return {'focus_z': 1.0, 'size': 1.4}, parts


# ---------------------------------------------------------------- the shark cage
def cage(tall=2.3, radius=1.2):
    steel = M('#b9c2cf', 0.3, metal=0.7)
    n = max(10, round(2 * math.pi * radius / 0.63))                                       # bars about 0.63 apart: a figure inside stays clear
    parts = [_torus((0, 0, 0.06), radius, 0.06, steel), _torus((0, 0, tall - 0.06), radius, 0.06, steel)]
    for i in range(n):                                                                    # no bar straight in front of the face
        a = 2 * math.pi * (i + 0.5) / n
        parts.append(cyl((radius * math.cos(a), radius * math.sin(a), tall / 2), 0.035, tall - 0.12, steel, verts=16))
    parts += [cyl((0, 0, tall - 0.06), 0.03, 2 * radius, steel, rot=(0, 90, 0), verts=12), cyl((0, 0, tall - 0.06), 0.03, 2 * radius, steel, rot=(90, 0, 0), verts=12),
              _torus((0, 0, tall + 0.07), 0.11, 0.03, M('#ffd23a', 0.4), rot=(90, 0, 0), segs=24)]     # two cross bars and a lifting ring on top
    return {'focus_z': tall / 2, 'size': max(0.8, tall / 2.9)}, parts


# ---------------------------------------------------------------- shark
def _shark_shapes(detail=True):
    """A blocky shark in side view: nose toward -x, belly on z=0, 2.6 long, 0.7 thick along y. Returns (parts, tail parts)."""
    grey, white, dark = M('#8794a6', 0.6), M('#f4f6f8', 0.6), M('#5b6677', 0.6)
    T = 0.7
    parts = [prism([(-1.3, 0.46), (-1.12, 0.62), (-0.6, 0.8), (0.1, 0.8), (0.65, 0.62), (0.98, 0.48), (0.98, 0.4), (0.65, 0.36), (0.1, 0.3),
                    (-0.62, 0.3), (-1.25, 0.42)], T, (0, 0, 0), grey, bevel=0.05),        # the grey back and upper jaw
             prism([(-0.62, 0.3), (0.1, 0.3), (0.65, 0.36), (0.98, 0.4), (0.98, 0.34), (0.7, 0.2), (0.3, 0.04), (-0.3, 0.0), (-0.9, 0.05),
                    (-1.1, 0.14), (-1.08, 0.21)], T, (0, 0, 0), white, bevel=0.05),       # the white belly and lower jaw
             prism([(-0.66, 0.3), (-1.2, 0.405), (-1.05, 0.215)], T - 0.12, (0, 0, 0), M('#6a1522', 0.7), bevel=0),       # inside the mouth
             prism([(-0.2, 0.76), (0.4, 0.76), (0.52, 1.32), (0.3, 1.24)], 0.12, (0, 0, 0), grey, bevel=0.03)]            # the back fin
    for sy in (-1, 1):
        parts.append(prism([(0, 0), (0.48, 0), (0.62, -0.44)], 0.08, (-0.4, sy * (T / 2 - 0.03), 0.3), grey, rot=(sy * 55, 0, 0), bevel=0.025))   # side fins
        eye = cyl((-0.84, sy * (T / 2 + 0.002), 0.57), 0.07, 0.03, M('#15151c', 0.2, coat=1.0), rot=(90, 0, 0), verts=24); eye.scale = (1.0, 1.3, 1.0)
        parts += [eye, cyl((-0.86, sy * (T / 2 + 0.012), 0.605), 0.024, 0.014, white, rot=(90, 0, 0), verts=12)]         # the cast's eye: a dark oval and a shine
        if detail:
            parts += [box((x, sy * (T / 2 + 0.002), 0.5), (0.025, 0.012, 0.17), dark, rot=(0, -14, 0), bevel=0) for x in (-0.52, -0.43, -0.34)]   # gills
            for x in (-1.14, -1.02, -0.9, -0.78):                                         # teeth: the upper row points down, the lower row up
                zj = 0.3 + 0.12 * (-0.62 - x) / 0.63
                parts.append(_cone((x, sy * (T / 2 - 0.045), zj - 0.045), 0.05, 0.0, 0.11, white, rot=(180, 0, 45), verts=4, smooth=False))
            for x in (-0.99, -0.87, -0.75):
                zl = 0.3 - 0.09 * (-0.62 - x) / 0.46
                parts.append(_cone((x, sy * (T / 2 - 0.045), zl + 0.035), 0.042, 0.0, 0.09, white, rot=(0, 0, 45), verts=4, smooth=False))
    if detail:
        parts += [_cone((-1.2, y, 0.37), 0.05, 0.0, 0.11, white, rot=(180, 0, 45), verts=4, smooth=False) for y in (-0.2, -0.067, 0.067, 0.2)]   # front teeth
        parts += [_cone((-1.05, y, 0.245), 0.042, 0.0, 0.09, white, rot=(0, 0, 45), verts=4, smooth=False) for y in (-0.14, 0.0, 0.14)]
    tail = [prism([(0.86, 0.52), (1.3, 1.04), (1.14, 0.45), (1.3, -0.02), (0.86, 0.34)], 0.1, (0, 0, 0), grey, bevel=0.03)]
    return parts, tail


def shark():
    parts, tail = _shark_shapes()
    pivot = _group('SharkTail', tail, (0.9, 0, 0.43))
    body = _group('SharkBody', parts + [pivot]); body.rotation_euler = (0, 0, math.radians(90))      # nose toward -y like every prop's front
    P = {'focus_z': 0.5, 'size': 0.9, 'tail': pivot, 'actions': {}}

    def circle(P, t, o):
        (x0, y0, z0), turn0 = P['loc'], P['turn']
        cx, cy = (o['around'][:2] if isinstance(o.get('around'), list) and len(o['around']) >= 2 else (x0, y0))
        R, z1 = _num(o, 'radius', 2.5), _num(o, 'height', z0); sign = -1 if o.get('back') else 1
        dur = _num(o, 'for', P.get('t_end', t + 6.0) + 0.1 - t)
        revs = _num(o, 'speed', min(0.45, 3.4 / (2 * math.pi * max(R, 0.3))))
        a0 = math.atan2(y0 - cy, x0 - cx) if math.hypot(x0 - cx, y0 - cy) > 0.05 else -math.pi / 2
        head = lambda a: math.degrees(a) + (180 if sign > 0 else 0)                       # nose along the way it swims
        off = round((turn0 - head(a0)) / 360) * 360

        def fn(tt):
            u = tt - t; a = a0 + sign * 2 * math.pi * revs * u; k = ss(u / 0.5)
            p = (cx + R * math.cos(a), cy + R * math.sin(a), z1 + 0.05 * math.sin(2 * math.pi * 0.5 * u))
            h = head(a) + off + 4 * math.sin(2 * math.pi * 2.4 * u)                       # the whole body swings a little against the tail
            return tuple(s + (q - s) * k for s, q in zip((x0, y0, z0), p)), (0, 0, turn0 + (h - turn0) * k)
        _move(P, t, t + dur, fn)
        wag = [((f - 1) / FPS, (0, 0, math.radians(26 * math.sin(2 * math.pi * 2.4 * ((f - 1) / FPS - t))))) for f in range(F(t), F(t + dur) + 1)]
        _keys(P['tail'], 'rotation_euler', wag + [(t + dur + 0.2, (0, 0, 0))], 'LINEAR')
    P['actions']['circle'] = circle
    return P, [body]


# ---------------------------------------------------------------- thought bubbles
def _icon_squirrel():
    """Side view, looking left: an upright body, a nut in its paws, the big tail curling up behind."""
    brown, cream, tip, ink = M('#6e4428', 0.7), M('#f6e2c0', 0.7), M('#9a6a44', 0.7), M('#2a1a12', 0.4)   # the cast squirrel's dark brown (12 Nov 2026)
    return [box((0.0, 0, -0.3), (0.62, 0.42, 0.8), brown, rot=(0, -12, 0), bevel=0.16), box((-0.2, -0.02, -0.3), (0.3, 0.44, 0.56), cream, rot=(0, -12, 0), bevel=0.1),
            box((-0.3, 0, 0.38), (0.56, 0.44, 0.46), brown, bevel=0.14), box((-0.55, 0, 0.3), (0.2, 0.38, 0.22), cream, bevel=0.07),
            _sphere((-0.66, 0, 0.36), 0.055, ink, segs=12), cyl((-0.36, -0.225, 0.47), 0.06, 0.02, ink, rot=(90, 0, 0), verts=16),
            prism([(-0.11, 0), (0.11, 0), (0.05, 0.26)], 0.3, (-0.13, 0, 0.57), brown, bevel=0.04),
            box((-0.42, 0, -0.06), (0.32, 0.47, 0.12), brown, rot=(0, 20, 0), bevel=0.05), _sphere((-0.64, 0, 0.0), 0.11, M('#e0a35a', 0.6), segs=14),
            box((-0.12, 0, -0.74), (0.52, 0.47, 0.14), M('#4a2c18', 0.7), bevel=0.05),
            box((0.4, 0, -0.5), (0.34, 0.34, 0.5), brown, rot=(0, 25, 0), bevel=0.12), box((0.64, 0, 0.0), (0.5, 0.4, 0.86), brown, rot=(0, 6, 0), bevel=0.22),
            box((0.5, 0, 0.56), (0.58, 0.4, 0.5), brown, rot=(0, -32, 0), bevel=0.22), box((0.19, 0, 0.74), (0.36, 0.36, 0.3), tip, rot=(0, -62, 0), bevel=0.13)]


def _icon_scammer():
    """A dark hooded head with two cold slits for eyes, holding up a lit phone."""
    hood, face, lit, screen = M('#2b2d3a', 0.7), M('#0d0d14', 0.9), M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=3.0), M('#59e0ff', 0.3, emit=hexrgb('#59e0ff'), emit_strength=2.5)
    head = cyl((0, 0, 0.2), 0.5, 0.86, hood, verts=48)
    bv = head.modifiers.new('bev', 'BEVEL'); bv.width = 0.17; bv.segments = 6; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(40)
    opening = cyl((0, -0.47, 0.16), 0.33, 0.08, face, rot=(90, 0, 0), verts=40); opening.scale = (1.0, 1.15, 1.0)
    return [head, _cone((0, 0.02, 0.8), 0.4, 0.05, 0.36, hood), opening,
            box((-0.14, -0.515, 0.22), (0.15, 0.03, 0.055), lit, rot=(0, 16, 0), bevel=0), box((0.14, -0.515, 0.22), (0.15, 0.03, 0.055), lit, rot=(0, -16, 0), bevel=0),
            box((0, 0, -0.62), (1.3, 0.5, 0.62), hood, bevel=0.2),
            box((0.56, -0.36, -0.28), (0.3, 0.06, 0.52), M('#16171d', 0.3), rot=(0, -12, 0), bevel=0.05),
            box((0.56, -0.395, -0.28), (0.24, 0.02, 0.44), screen, rot=(0, -12, 0), bevel=0),
            box((0.5, -0.3, -0.58), (0.36, 0.18, 0.2), M('#3a3d4d', 0.7), rot=(0, -12, 0), bevel=0.06)]


def _bubble_material():
    """Glassy: almost clear in the middle, a bright rim. 'Rim' (the Emission node) is what 'flare' warms up."""
    m = bpy.data.materials.new('ThoughtBubble'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); em.name = 'Rim'
    em.inputs['Color'].default_value = (*hexrgb(BUBBLE_RIM), 1); em.inputs['Strength'].default_value = 1.25
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.32
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.6
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; ad.inputs[1].default_value = 0.1; ad.use_clamp = True
    nt.links.new(lw.outputs['Facing'], pw.inputs[0]); nt.links.new(pw.outputs[0], ad.inputs[0]); nt.links.new(ad.outputs[0], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = True       # smooth see-through, the front of the ball only
    return m


BUBBLE_RIM, BUBBLE_HOT = '#f4fcff', '#ff5a14'
LEAN = 0.4                                            # how far the orbit's lower half leans toward the camera (per unit of radius)


def bubble(icon='squirrel'):
    rim = _bubble_material()
    shell = _sphere((0, 0, 0), 0.45, rim, segs=48)
    glint = _sphere((-0.2, -0.36, 0.2), 0.07, M('#ffffff', 0.3, emit=hexrgb('#ffffff'), emit_strength=1.5), segs=12)
    glint.scale = (1.7, 0.25, 0.75); glint.rotation_euler = (0, math.radians(-40), 0)
    if icon == 'shark':
        sp, tail = _shark_shapes(detail=False); inner = _group('Icon', sp + tail, (0, 0, 0.55)); k, rot = 0.28, (0, 12, 0)
    elif icon == 'satellite':
        inner = _group('Icon', _sat_parts(M(SAT_GOLD, 0.32, metal=0.6)), (0, 0, 0.68)); k, rot = 0.3, (0, -16, 0)
    elif icon == 'scammer':
        inner = _group('Icon', _icon_scammer(), (0, 0, 0)); k, rot = 0.33, (0, 0, 0)
    elif icon == 'squirrel':
        inner = _group('Icon', _icon_squirrel(), (0, 0, 0)); k, rot = 0.34, (0, 0, 0)
    else:
        raise SystemExit(f"bubble: there is no icon '{icon}' (squirrel, shark, scammer, satellite)")
    inner.location = (0, 0, 0); inner.scale = (k,) * 3; inner.rotation_euler = tuple(math.radians(a) for a in rot)   # shrunk round its own middle
    for o in [shell, glint] + list(inner.children_recursive):
        o.visible_shadow = False                      # a thought casts no shadow
    P = {'focus_z': 0.0, 'size': 0.4, 'rim': rim, 's_now': 1.0, 'actions': {}}
    em = rim.node_tree.nodes['Rim']

    def orbit(P, t, o):
        c = list(o['around']) if isinstance(o.get('around'), list) else list(P['loc'])
        c = (c + list(P['loc'])[len(c):])[:3]
        R, revs, ph = _num(o, 'radius', 1.0), _num(o, 'speed', 0.25), math.radians(_num(o, 'phase', 0.0)); start = P['loc']

        def fn(tt):
            a = ph + 2 * math.pi * revs * (tt - t); k = ss((tt - t) / 0.4)
            p = (c[0] + R * math.cos(a), c[1] - LEAN * R * (1 - math.sin(a)), c[2] + R * math.sin(a))
            return tuple(s + (q - s) * k for s, q in zip(start, p)), (0, 0, P['turn'])
        _move(P, t, P.get('t_end', t + 6.0) + 0.1, fn, turn=False)

    def stop(P, t, o):
        root = P['root']; act = root.animation_data.action if root.animation_data else None
        if act is None:
            return
        for fc in getattr(act, 'fcurves', None) or [fc for ly in act.layers for s in ly.strips for cb in s.channelbags for fc in cb.fcurves]:
            if fc.data_path == 'location':
                for i in range(len(fc.keyframe_points) - 1, -1, -1):               # everything after the stop goes
                    if fc.keyframe_points[i].co.x > F(t) + 0.5:
                        fc.keyframe_points.remove(fc.keyframe_points[i])
        if 'track' in P:
            P['loc'] = tuple(P['track'][F(t)][:3])
        _stay(P, t)

    def flare(P, t, o):
        s = P['s_now']
        _keys(P['root'], 'scale', [(t, (s,) * 3), (t + 0.18, (s * 1.78,) * 3), (t + 0.32, (s * 1.6,) * 3)])
        _socket_keys(em.inputs['Color'], [(t, (*hexrgb(BUBBLE_RIM), 1)), (t + 0.25, (*hexrgb(BUBBLE_HOT), 1))])
        _socket_keys(em.inputs['Strength'], [(t, 1.25), (t + 0.25, 3.2)])
        P['s_now'] = s * 1.6

    def fade(P, t, o):
        _keys(P['root'], 'scale', [(t, (P['s_now'],) * 3), (t + 0.4, (0.001,) * 3)]); P['s_now'] = 0.001
    P['actions'].update(orbit=orbit, stop=stop, flare=flare, fade=fade)
    return P, [shell, glint, inner]


# ---------------------------------------------------------------- magnifying glass
_LENS = None


def _lens():
    global _LENS
    if _LENS is None:
        _LENS = M('#c9ecff', 0.03, coat=1.0).copy(); _LENS.name = 'MagnifierGlass'
        _LENS.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.3
        _LENS.surface_render_method = 'BLENDED'; _LENS.use_backface_culling = False
    return _LENS


def magnifier():
    """A magnifying glass standing on the end of its handle, the glass facing -y. Held (hold <who>) the end of the handle sits in
    the middle of the fist: with the move 'show' and 'tilt 125' it stands upright beside the head, with 'carry' and 'tilt 55'
    in front of the chest."""
    gold, dark, white = M('#f2c230', 0.3, metal=0.5), M('#2b2b33', 0.45), M('#ffffff', 0.3, emit=hexrgb('#ffffff'), emit_strength=0.6)
    glass = cyl((0, 0, 0.78), 0.3, 0.03, _lens(), rot=(90, 0, 0), verts=48); glass.visible_shadow = False
    parts = [cyl((0, 0, 0.2), 0.06, 0.4, dark, verts=24), cyl((0, 0, 0.3), 0.066, 0.05, M('#e63946', 0.4), verts=24), cyl((0, 0, 0.43), 0.075, 0.08, gold, verts=24),
             _torus((0, 0, 0.78), 0.31, 0.05, gold, rot=(90, 0, 0)), glass,
             box((-0.1, -0.02, 0.88), (0.2, 0.012, 0.04), white, rot=(0, 42, 0), bevel=0), box((-0.02, -0.02, 0.81), (0.1, 0.012, 0.03), white, rot=(0, 42, 0), bevel=0)]
    return {'focus_z': 0.7, 'size': 0.32, 'grip': (0.0, 0.0, 1.13)}, parts


BUILDERS = dict(satellite=satellite, cash=cash, maze=maze, cage=cage, shark=shark, bubble=bubble, magnifier=magnifier)
