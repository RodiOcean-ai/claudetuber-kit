"""Light-switch props for the blocky world (built 13 Nov 2026 for the Khaby Lame light-switch Short): a ceiling lamp, a wall
switch, a toy bow, a toy suction-cup arrow, a chain of dominoes, a desk globe, a factory conveyor belt and a cardboard box.
Nothing carries a word, a letter, a number or a logo: every mark on them is a shape.
Each builder returns (P, objects) like the builders in props.py; P['setup'] runs once the prop has its root, P['actions'] maps an
action name to f(P, t, opt). scene.py registers BUILDERS and hands the builder the first row's keywords listed in KW; an
action row's options arrive as lists of numbers ('to 1 2 3' -> [1.0, 2.0, 3.0]; a bare word -> True; '@name' stays a word).
Checked by eye 13 Nov 2026 (lookdev folder of an earlier episode: props_test.md + props_test_lab.md).

Kinds, their actions and options (table rows: '| 0.0 | @name | kind | | at X Y Z; turn N | |', then '| t | @name | action | | options | |'):
- lamp (a ceiling pendant: cup on the ceiling, cord, teal cone shade, warm bulb): origin = where the cord meets the ceiling, so
  'at X Y 5.0' in a room. First row 'drop N' (cord length, default 1.3; the shade's lip hangs 0.52 below it, the bulb pokes out
  0.1 under the lip), 'dim N' (share of the ROOM's ceiling light left when the lamp is off, default 0.2; 'dim 1' leaves the room
  alone), 'power N' (its own warm point light, watts, default 220). Starts ON. off (a 3-frame flicker, dark by 0.1 s: bulb, the
  glowing inside of the shade, its light and the room light) | on (the same flicker the other way). Framing: the camera looks
  UP at it from in front and below (view_up -0.45), so a close shows the bulb and the lit inside; the aim point is the lip.
  Its light is added right after the scene's light preset (scene.py's light() is wrapped when this module is imported, because
  the preset removes every light; a persistent frame handler is the fallback).
- switch (a wall light switch, white plate 0.25 x 0.38, amber rocker): origin = the middle of the plate's BACK, so 'at' is a
  point ON the wall: the bedroom's back wall is y = Y + 4.5 ('at 240.3 4.5 1.6', turn 0), a side wall x = X -/+ 6 with turn 90 /
  -90. flip (the rocker snaps over in 0.08 s, a tiny white click-flash). P['target'] = the rocker's face (the plate's 'at' moved
  0.11 forward): an arrow's 'to @switch' lands its cup there. Framing: size 0.32 (a close fills about half the picture); the aim
  is 0.16 under the rocker so an arrow stuck on it does not block the view.
- bow (a toy bow 0.92 tall: orange limbs, yellow grip and tips, white string; it stands in the x-z plane facing -y and shoots
  toward +x): made for a hand: '| t | @bow | bow | | hold hero; tilt 125 | |' with the move 'show' (e.g. 'sit+show') holds it
  upright beside the head, the grip in the fist (P['grip'] = (0, 0, 1.13), like the magnifier). First row 'aim left' mirrors it
  (shoots toward -x, for 'hold <who>; left'). draw (for S, default 0.4: the string pulls back 0.2 over 70 % of S with an arrow
  nocked on it, snaps forward at t + S and the nocked arrow vanishes; 'empty' = no arrow on the string). Time the arrow's
  shoot at the draw's t + S. A held prop is not tracked by the camera bank: frame the holder (medium/close hero), not @bow.
- arrow (a toy suction-cup arrow 0.7 long: yellow shaft, green fletching, red cup; it points -y): origin = the cup's face. First
  row 'at X Y Z' (where it appears; hidden until shot). shoot (to X Y Z or to @prop; for S, default 0.35; optional from X Y Z or
  from @bow): it appears at 'at' (or, with 'from @bow', with its back on the bow's string at that moment), points at the target,
  flies point first in a straight line with a tiny arc (6 % of the distance) and a white speed streak behind it, sticks by its cup
  and the shaft wobbles (damped, about 4 wiggles in 0.6 s), then stays. 'to @switch' hits the switch's rocker; another prop's
  name aims at its 'at' + focus. Recommended: '| 18.85 | @arrow | shoot | | from @bow; to @switch; for 0.35 | |'. Framing after
  the hit: the camera bank films it side-on from the open side of the room (size 0.45).
- dominoes (a chain standing on the floor along a gentle S-curve, 0.62 tall, 0.3 wide, colours red/yellow/blue/green/orange/
  purple with white lines and pips): origin = the MIDDLE of the chain on the floor ('at X Y 0'); the chain runs along local x
  from P['start'] = (-L/2, 0, 0) (the first domino, the one to push) to P['end'] = (L/2, 0, 0) (the last); it swings 0.45 to
  either side (y). First row 'count N' (default 24), 'length L' (default 6). topple (for S, default 2.0): the first tips toward the
  next, each starts falling when the one before touches it, they come to rest leaning on each other and the last falls flat
  (it reaches 0.62 past P['end']). Framing: size 0.28 x L, seen a little from above (view_up 0.32): a medium shows the whole
  chain small across the picture; a wide of the room shows it best in a tall picture.
- globe (a desk globe 1.0 across on a gold stand, its centre 1.8 high; blue oceans, green land with sand coasts, white poles,
  gold half-meridian; the axis leans 23.5 degrees): 'at X Y 0'. spin (from t: one turn every 3 s about its tilted axis, to the
  end of the scene) | glow (a golden ring of light rises round it in 0.5 s and the globe brightens a little). Framing: aim 1.7,
  size 0.95 (a close shows the whole ball and the top of the stand).
- conveyor (a factory belt 4.2 long along x and 0.9 high on blue legs: grey belt with light stripes, dark rollers, yellow rails,
  orange hoods with black rubber flaps at both ends, five cardboard boxes): 'at X Y 0'. Starts still. run (from t: speeds up in
  0.3 s to 0.8 a second, the boxes slide toward +x and the stripes move; a box goes in under the right hood's flaps and comes
  back out of the left one) | stop (slows to a stop in 0.25 s from t). Run and stop can repeat. Framing: aim 0.95, size 1.25
  (a medium shows the whole belt).
- box (a cardboard box 0.55 cube, tape across the top and down the front and back): origin = the middle of its bottom, so
  'at X Y 0' stands it on the floor. Made for a hand: 'hold <who>; tilt 55' with the move 'carry' ('stand+carry',
  'walk+carry') holds it in front of the chest, its side in the right hand (it leans 6 degrees with the arm). Framing: frame the
  holder; standing alone, aim 0.28, size 0.4.

Someone sitting IN the bedroom's bed, legs under the orange blanket, facing the camera: 'at 236.8 2.6 0; seat 0.65; turn 0'
(the blanket ends at y 2.85: from y 2.6 its edge hides the lap; seat 0.65 sinks the legs into it so no shoe pokes through).
Weak spots: held props can't be framed by name; with LOOK=chess the night room gets the look's own sun lights, so the light-off
change is smaller there; the arrow re-aims at its target in one frame when it leaves the bow; the conveyor's boxes vanish for
two frames inside a hood when they wrap round (hidden by the hood)."""
import math, sys
import bpy, bmesh
from mathutils import Vector, Euler
from common import FPS, hexrgb
from sf_world import box, cyl, empty, parent
from blocky_kit import M
from props import _keys, _sphere, visible, F
from props_story import _torus, _cone, _num, _socket_keys, _stay, _group

ss = lambda u: 0 if u <= 0 else 1 if u >= 1 else u * u * (3 - 2 * u)
KW = {'lamp': {'drop': float, 'dim': float, 'power': float},
      'dominoes': {'count': float, 'length': float},
      'bow': {'aim': str}}
REG = {}                                              # this module's props by table name ('@switch'): 'shoot | to @switch; from @bow'
LAMPS = []                                            # the lamps of this scene: their lights are added once the light preset is set


# ---------------------------------------------------------------- helpers
def _fcurves(idb):
    ad = getattr(idb, 'animation_data', None); act = ad.action if ad else None
    if act is None:
        return []
    return list(getattr(act, 'fcurves', None) or [fc for ly in act.layers for s in ly.strips for cb in s.channelbags for fc in cb.fcurves])


def _interp(idb, kind='CONSTANT', path=None):
    for fc in _fcurves(idb):
        if path is None or fc.data_path.endswith(path):
            for k in fc.keyframe_points:
                k.interpolation = kind


def _register(P):
    REG[P['name'].lower()] = P


def _tube(pts, r, m, segs=14, name='Tube', caps=True):
    """A round tube along a line of points; r is one radius or one per point."""
    P = [Vector(p) for p in pts]; n = len(P); rs = r if isinstance(r, (list, tuple)) else [r] * n
    bm = bmesh.new(); rings, prev = [], None
    for i, p in enumerate(P):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        if prev is None:
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0)); nrm = t.cross(ref).normalized()
        else:
            nrm = (prev - t * prev.dot(t)).normalized()
        prev = nrm; bn = t.cross(nrm)
        rings.append([bm.verts.new(p + rs[i] * (math.cos(a) * nrm + math.sin(a) * bn)) for a in (2 * math.pi * k / segs for k in range(segs))])
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    if caps:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(m)
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    return o


def _vane(pts, thick, roll, m):
    """A flat fin in the plane of the arrow's axis (y) and the direction 'roll' degrees round it; pts = [(along y, out from the axis)]."""
    u = Vector((0, 1, 0)); v = Vector((math.sin(math.radians(roll)), 0, math.cos(math.radians(roll)))); w = u.cross(v)
    bm = bmesh.new(); n = len(pts)
    vs = [bm.verts.new(a * u + b * v + s * thick / 2 * w) for s in (-1, 1) for a, b in pts]
    bm.faces.new(vs[:n]); bm.faces.new(vs[n:])
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((vs[i], vs[j], vs[n + j], vs[n + i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('Vane'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('Vane', me); bpy.context.collection.objects.link(o); me.materials.append(m)
    bv = o.modifiers.new('bev', 'BEVEL'); bv.width = 0.004; bv.segments = 2
    return o


def _open_cone(z_top, z_bot, r_top, r_bot, m, verts=48):
    bpy.ops.mesh.primitive_cone_add(radius1=r_bot, radius2=r_top, depth=z_top - z_bot, location=(0, 0, (z_top + z_bot) / 2), vertices=verts,
                                    end_fill_type='NOTHING')
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def _burst(name, size, m):
    """A tiny white click-flash: a ball and eight streaks, hidden (scale 0) until keyed."""
    parts = [_sphere((0, 0, 0), 0.3 * size, m, segs=12)]
    for i in range(8):
        a = 2 * math.pi * i / 8; L = (0.9 if i % 2 == 0 else 0.55) * size
        parts.append(box(((0.38 * size + L / 2) * math.sin(a), 0, (0.38 * size + L / 2) * math.cos(a)), (0.12 * size, 0.12 * size, L), m,
                         rot=(0, math.degrees(a), 0), bevel=0))
    for o in parts:
        o.visible_shadow = False
    g = _group(name, parts, (0, 0, 0)); g.scale = (0.001,) * 3
    return g


def _flash_keys(g, t):
    _keys(g, 'scale', [(t - 0.02, (0.001,) * 3), (t + 0.05, (1.25,) * 3), (t + 0.11, (1.0,) * 3), (t + 0.2, (0.001,) * 3)], 'LINEAR')


def _where(v, t, want):
    """An option's point: 'X Y Z' as numbers, or '@name' of a prop of this module (want = 'target' or 'nock')."""
    if not isinstance(v, list) or not v:
        return None
    if isinstance(v[0], str) and v[0].startswith('@'):
        Q = REG.get(v[0].lower())
        if Q is None:
            raise SystemExit(f"arrow: there is no prop '{v[0]}' (only lamp, switch, bow, dominoes, globe, conveyor, box can be named here)")
        if want == 'nock' and 'nock_mark' in Q:
            sc = bpy.context.scene; keep = sc.frame_current; sc.frame_set(F(t))
            p = Q['nock_mark'].matrix_world.translation.copy(); sc.frame_set(keep)
            return p, True
        if want == 'target' and 'target' in Q:
            return Vector(Q['target']), False
        x, y, z = Q['loc']
        return Vector((x, y, z + Q.get('focus_z', 0.0))), False
    if len(v) >= 3:
        return Vector([float(a) for a in v[:3]]), False
    return None


def _rz(turn, p):
    a = math.radians(turn); x, y, z = p
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z)


# ---------------------------------------------------------------- lamp
LAMP_SHADE, LAMP_LIGHT = '#22b8a7', '#ffc47a'
BULB_EMIT, INNER_EMIT = 9.0, 0.6
FLICK_OFF = ((0, 1.0), (1, 0.25), (2, 0.8), (3, 0.0))       # frames after the cue, share of full brightness
FLICK_ON = ((0, 0.0), (1, 0.65), (2, 0.15), (3, 1.0))


def _flick(owner, path, full, events, keep=0.0, idb=None, start=True):
    def put(f, frac):
        setattr(owner, path, full * (keep + (1 - keep) * frac)); owner.keyframe_insert(path, frame=f)
    if start:
        put(0, 1.0)
    for t, on in events:
        for df, frac in (FLICK_ON if on else FLICK_OFF):
            put(F(t) + df, frac)
    _interp(idb)


def lamp(drop=1.3, dim=0.2, power=220.0):
    drop = max(0.2, drop)
    white, dark, brass = M('#f4f1ea', 0.4), M('#2b2b33', 0.5), M('#f2c230', 0.3, metal=0.5)
    shade = M(LAMP_SHADE, 0.35, coat=0.6)
    inner = M('#e8902e', 0.6, emit=hexrgb('#ffae42'), emit_strength=INNER_EMIT).copy(); inner.name = 'LampShadeInside'
    bulb_m = M('#fff6df', 0.25, emit=hexrgb('#ffcf6a'), emit_strength=BULB_EMIT).copy(); bulb_m.name = 'LampBulb'
    zt, zb = -drop - 0.08, -drop - 0.52                   # the shade: top and lip
    parts = [cyl((0, 0, -0.03), 0.15, 0.06, white, verts=32),                              # the ceiling cup
             cyl((0, 0, -(0.06 + drop) / 2), 0.018, drop - 0.06, dark, verts=12),          # the cord
             cyl((0, 0, -drop - 0.04), 0.075, 0.14, brass, verts=24),                      # the socket cap
             _open_cone(zt, zb, 0.09, 0.47, shade), _open_cone(zt - 0.012, zb, 0.075, 0.452, inner),
             _torus((0, 0, zb), 0.462, 0.022, shade)]
    bulb = _sphere((0, 0, zb + 0.02), 0.13, bulb_m, segs=32); bulb.visible_shadow = False   # the light sits inside it
    parts.append(bulb)
    P = {'focus_z': zb, 'size': 0.55, 'view_up': -0.45, 'bulb': bulb_m, 'inner': inner, 'events': [], 'power': power, 'dim': dim, 'bulb_z': zb + 0.02,
         'actions': {}}

    def setup(P):
        _register(P); LAMPS.append(P)
        b, i = bulb_m.node_tree.nodes['Principled BSDF'], inner.node_tree.nodes['Principled BSDF']
        _flick(b.inputs['Emission Strength'], 'default_value', BULB_EMIT, [], idb=bulb_m.node_tree)
        _flick(i.inputs['Emission Strength'], 'default_value', INNER_EMIT, [], idb=inner.node_tree)

    def switch_to(P, t, on):
        P['events'].append((t, on))
        b, i = bulb_m.node_tree.nodes['Principled BSDF'], inner.node_tree.nodes['Principled BSDF']
        _flick(b.inputs['Emission Strength'], 'default_value', BULB_EMIT, [(t, on)], idb=bulb_m.node_tree, start=False)
        _flick(i.inputs['Emission Strength'], 'default_value', INNER_EMIT, [(t, on)], idb=inner.node_tree, start=False)
    P['setup'] = setup
    P['actions'].update(off=lambda P, t, o: switch_to(P, t, False), on=lambda P, t, o: switch_to(P, t, True))
    return P, parts


def _install_lamps(*_):
    """Each lamp's own warm point light (inside the bulb) and, in a room, the room's ceiling light dimmed with it."""
    import places as PL
    for o in [o for o in bpy.data.objects if o.type == 'LIGHT' and o.name.startswith('PendantLight')]:
        bpy.data.objects.remove(o)
    ceilings = [o for o in bpy.data.objects if o.type == 'LIGHT' and o.name.startswith('Ceiling')]
    for P in LAMPS:
        x, y, z = P['loc']
        d = bpy.data.lights.new('PendantLight', 'POINT'); d.energy = P['power']; d.color = hexrgb(LAMP_LIGHT); d.shadow_soft_size = 0.1
        o = bpy.data.objects.new('PendantLight', d); bpy.context.collection.objects.link(o); o.location = (x, y, z + P['bulb_z'])
        _flick(d, 'energy', P['power'], sorted(P['events']), idb=d)
        if P['dim'] >= 0.999:
            continue
        for (X, Y), (w, dd, h) in PL.ROOMS:
            if abs(x - X) < w / 2 + 0.01 and abs(y - Y) < dd / 2 + 0.01:
                for c in ceilings:
                    if abs(c.location.x - X) < 0.01 and abs(c.location.y - Y) < 0.01:
                        base = c.data.get('lamp_base', c.data.energy); c.data['lamp_base'] = base
                        _flick(c.data, 'energy', base, sorted(P['events']), keep=P['dim'], idb=c.data)


def _hook_light():
    """scene.py sets the light preset (places.light, which removes every light) after the props are built: wrap scene's
    light() so the lamps add their lights right after it."""
    f = sys._getframe(1)
    while f is not None:
        g = f.f_globals
        if 'KW_ALL' in g and callable(g.get('light')) and g.get('light').__module__ in ('places', __name__):
            if not getattr(g['light'], 'lamps_hook', False):
                orig = g['light']

                def light(*a, **k):
                    out = orig(*a, **k); _install_lamps(); return out
                light.lamps_hook = True; g['light'] = light
            return True
        f = f.f_back
    return False


HOOKED = _hook_light()
if not HOOKED:                                        # fallback: add the lamp lights on the first frame change after the preset
    @bpy.app.handlers.persistent
    def _late(scene, *_):
        if LAMPS and any(o.type == 'LIGHT' and o.name.startswith('Sun') for o in bpy.data.objects) and \
                not any(o.type == 'LIGHT' and o.name.startswith('PendantLight') for o in bpy.data.objects):
            _install_lamps()
    bpy.app.handlers.frame_change_pre.append(_late)


# ---------------------------------------------------------------- wall switch
SW_ANG = 13.0                                         # the rocker's tilt either way (degrees)


def switch():
    plate_m, slot_m = M('#f8f8f4', 0.3, coat=0.5), M('#cfd5de', 0.5)
    tog_m, screw = M('#ffb000', 0.3, coat=0.6), M('#c9ced6', 0.3, metal=0.6)
    parts = [box((0, -0.025, 0), (0.25, 0.05, 0.38), plate_m, bevel=0.018),               # the plate, its back on local y=0 (the wall)
             box((0, -0.051, 0), (0.13, 0.006, 0.21), slot_m, bevel=0)]                   # the slot the rocker sits in
    parts += [cyl((0, -0.051, z), 0.013, 0.006, screw, rot=(90, 0, 0), verts=16) for z in (-0.155, 0.155)]
    tog = box((0, -0.08, 0), (0.1, 0.06, 0.17), tog_m, bevel=0.016)
    toggle = _group('SwitchToggle', [tog], (0, -0.05, 0)); toggle.rotation_euler = (math.radians(-SW_ANG), 0, 0)
    flash = _burst('SwitchFlash', 0.12, M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=9.0)); flash.location = (0, -0.13, 0)
    P = {'focus_z': -0.16, 'size': 0.32, 'toggle': toggle, 'flash': flash, 'ang': -SW_ANG, 'actions': {}}

    def setup(P):
        _register(P); x, y, z = P['loc']; dx, dy, dz = _rz(P['turn'], (0, -0.11, 0))
        P['target'] = (x + dx, y + dy, z + dz)               # the rocker's face: where an arrow's cup lands

    def flip(P, t, o):
        a0 = P['ang']; a1 = -a0
        _keys(P['toggle'], 'rotation_euler', [(t, (math.radians(a0), 0, 0)), (t + 0.08, (math.radians(a1), 0, 0))], 'LINEAR')
        _flash_keys(P['flash'], t + 0.02); P['ang'] = a1
    P['setup'] = setup; P['actions']['flip'] = flip
    return P, parts + [toggle, flash]


# ---------------------------------------------------------------- toy bow
BOW_D, BOW_H = 0.32, 0.42                             # riser to string, half the height (tips)
ARROW_L = 0.7


def _arrow_parts(trail=False):
    """A toy suction-cup arrow, its cup's face on the origin, the shaft back along +y (it points -y)."""
    shaft, fl = M('#ffe14d', 0.35, coat=0.5), M('#36c95a', 0.45, coat=0.3)
    cup, nock = M('#e63946', 0.4, coat=0.3), M('#2b2b33', 0.4)
    parts = [cyl((0, 0.012, 0), 0.085, 0.024, cup, rot=(90, 0, 0), verts=32),
             _cone((0, 0.06, 0), 0.075, 0.03, 0.07, cup, rot=(-90, 0, 0)),
             cyl((0, (0.09 + ARROW_L) / 2, 0), 0.024, ARROW_L - 0.09, shaft, rot=(90, 0, 0), verts=16),
             cyl((0, ARROW_L - 0.012, 0), 0.034, 0.035, nock, rot=(90, 0, 0), verts=16)]
    for k in range(3):
        parts.append(_vane([(ARROW_L - 0.25, 0.02), (ARROW_L - 0.05, 0.02), (ARROW_L - 0.02, 0.115), (ARROW_L - 0.15, 0.115)], 0.014, 120 * k, fl))
    return parts


def bow(aim='right'):
    s = -1 if str(aim).lower().startswith('l') else 1
    orange, yellow, white = M('#ff7a1a', 0.35, coat=0.6), M('#ffd23a', 0.35, coat=0.6), M('#ffffff', 0.5)
    c = -(BOW_D ** 2 + BOW_H ** 2) / (2 * BOW_D); R = -c; amax = math.asin(BOW_H / R)
    angs = [-amax + 2 * amax * k / 28 for k in range(29)]
    limbs = _tube([(s * (c + R * math.cos(a)), 0, R * math.sin(a)) for a in angs], [0.026 + 0.016 * (1 - abs(a) / amax) for a in angs], orange, name='BowLimbs')
    parts = [limbs, box((0, 0, 0), (0.1, 0.11, 0.3), yellow, bevel=0.03)]
    parts += [_sphere((-s * BOW_D, 0, sz * BOW_H), 0.045, yellow, segs=16) for sz in (1, -1)]
    tips = []
    for sz in (1, -1):                                   # the string: two halves hanging from the tips to the nock point
        seg = cyl((-s * BOW_D, 0, sz * BOW_H / 2), 0.011, BOW_H, white, verts=8)
        tips.append(_group('BowString', [seg], (-s * BOW_D, 0, sz * BOW_H)))
    nock = empty('BowNock', (-s * BOW_D, 0, 0))
    mark = empty('BowNockMark', (-s * BOW_D, -0.07, 0))
    decoy = _group('BowArrow', _arrow_parts(), (0, 0, 0)); decoy.rotation_euler = (0, 0, math.radians(90 * s))
    decoy.location = (s * (-BOW_D + ARROW_L), -0.07, 0)  # nocked: its back on the string, resting in front of the riser
    parent([mark, decoy], nock); decoy.scale = (0.001,) * 3
    P = {'focus_z': 0.0, 'size': 0.4, 'grip': (0.0, 0.0, 1.13), 'tips': tips, 'nock': nock, 'nock_mark': mark, 'decoy': decoy, 's': s,
         'actions': {}}

    def string_at(P, k):
        """k = share of the full pull (0 = rest, 1 = drawn 0.2 back)."""
        x = -s * (BOW_D + 0.2 * k); dx = x + s * BOW_D; L = math.hypot(dx, BOW_H)
        P['nock'].location = (x, 0, 0)
        for pv, sz in zip(P['tips'], (1, -1)):
            pv.rotation_euler = (0, -sz * math.atan2(dx, BOW_H), 0); pv.scale = (1, 1, L / BOW_H)

    def draw(P, t, o):
        S = max(_num(o, 'for', 0.4), 0.15); t1 = t + S
        for tt, k in ((t, 0.0), (t + 0.7 * S, 1.0), (t1 - 1 / FPS, 1.0), (t1, -0.25), (t1 + 2 / FPS, 0.1), (t1 + 4 / FPS, 0.0)):
            string_at(P, k); f = F(tt)
            P['nock'].keyframe_insert('location', frame=f)
            for pv in P['tips']:
                pv.keyframe_insert('rotation_euler', frame=f); pv.keyframe_insert('scale', frame=f)
        if not o.get('empty'):                            # an arrow sits on the string while it is drawn; it leaves at the release
            _keys(P['decoy'], 'scale', [(t - 1 / FPS, (0.001,) * 3), (t, (1, 1, 1)), (t1, (0.001,) * 3)], 'CONSTANT')
    P['setup'] = _register; P['actions']['draw'] = draw
    return P, parts + tips + [nock]


# ---------------------------------------------------------------- toy arrow
def arrow():
    parts = _arrow_parts()
    tm = M('#ffffff', 0.5, emit=hexrgb('#ffffff'), emit_strength=2.5).copy(); tm.name = 'ArrowTrail'
    tm.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.35; tm.surface_render_method = 'BLENDED'
    streak = _cone((0, ARROW_L + 0.55, 0), 0.05, 0.0, 1.1, tm, rot=(-90, 0, 0)); streak.visible_shadow = False
    trail = _group('ArrowTrail', [streak], (0, ARROW_L, 0)); trail.scale = (0.001,) * 3
    P = {'focus_z': 0.0, 'size': 0.45, 'trail': trail, 'actions': {}}

    def setup(P):
        _register(P); visible([P['root']], [(0, False)])

    def shoot(P, t, o):
        dur = max(_num(o, 'for', 0.35), 0.1)
        hit = _where(o.get('to'), t, 'target')
        tgt = hit[0] if hit else Vector(P['loc']) + Vector(_rz(P['turn'], (0, -3.0, 0)))
        src = _where(o.get('from'), t, 'nock')
        if src and src[1]:                                # from a bow's string: the arrow's back on the string, pointing at the target
            start = src[0] + (tgt - src[0]).normalized() * ARROW_L
        else:
            start = src[0] if src else Vector(P['loc'])
        L = (tgt - start).length; arc = min(0.06 * L, 0.3)

        def angles(d):
            d = d.normalized(); return -math.degrees(math.asin(max(-1.0, min(1.0, d.z)))), math.degrees(math.atan2(d.x, -d.y))
        phi_e, psi_e = angles((tgt - start) + Vector((0, 0, -4 * arc)))
        side = [psi_e + 90, psi_e - 90]
        cam = max(side, key=lambda a: math.cos(math.radians(a)))    # the camera bank films it side-on, from the room's open side
        locs, rots = [], []
        for f in range(F(t), F(t + dur + 0.6) + 1):
            tt = (f - 1) / FPS; u = min(max((tt - t) / dur, 0.0), 1.0)
            if tt <= t + dur:
                p = start.lerp(tgt, u) + Vector((0, 0, arc * 4 * u * (1 - u)))
                phi, psi = angles((tgt - start) + Vector((0, 0, arc * 4 * (1 - 2 * u))))
            else:                                         # stuck: the shaft wobbles round the cup, a few damped wiggles
                p = tgt; w = tt - t - dur; e = math.exp(-6.5 * w) * math.sin(2 * math.pi * 8.5 * w)
                phi, psi = phi_e + 7 * e, psi_e + 3.5 * math.exp(-6.5 * w) * math.sin(2 * math.pi * 8.5 * w + 1.3)
            locs.append((tt, tuple(p))); rots.append((tt, (math.radians(phi), 0, math.radians(psi))))
            if 'track' in P:
                P['track'][f] = (*p, cam)
        _keys(P['root'], 'location', locs, 'LINEAR'); _keys(P['root'], 'rotation_euler', rots, 'LINEAR')
        _keys(P['trail'], 'scale', [(t - 1 / FPS, (0.001,) * 3), (t, (1, 1, 1)), (t + dur - 1 / FPS, (1, 1, 1)), (t + dur, (0.001,) * 3)], 'CONSTANT')
        visible([P['root']], [(0, False), (t, True)])
        P['loc'], P['turn'] = tuple(tgt), cam; _stay(P, t + dur + 0.6)
    P['setup'] = setup; P['actions']['shoot'] = shoot
    return P, parts + [trail]


# ---------------------------------------------------------------- dominoes
DOM_H, DOM_W, DOM_T = 0.62, 0.3, 0.09
DOM_COLS = ('#e63946', '#ffd23a', '#2f7cf6', '#36c95a', '#ff8a3d', '#9b5de5')


def dominoes(count=24, length=6.0):
    n = max(2, int(round(count))); L = max(1.0, length); A = 0.45 * min(1.0, L / 6.0)
    white = M('#ffffff', 0.4)
    cy_ = lambda x: A * math.sin(2 * math.pi * (x + L / 2) / L)
    dcy = lambda x: A * 2 * math.pi / L * math.cos(2 * math.pi * (x + L / 2) / L)
    pts = [Vector((-L / 2 + L * i / (n - 1), cy_(-L / 2 + L * i / (n - 1)), 0)) for i in range(n)]
    pivots, parts_all = [], []
    for i, c in enumerate(pts):
        T = Vector((1, dcy(c.x), 0)).normalized(); psi = math.atan2(T.y, T.x); deg = math.degrees(psi)
        col = M(DOM_COLS[i % len(DOM_COLS)], 0.35, coat=0.5)
        parts = [box((c.x, c.y, DOM_H / 2), (DOM_T, DOM_W, DOM_H), col, rot=(0, 0, deg), bevel=0.02)]
        for sg in (-1, 1):                                # a white line and two pips on both big faces
            fc = c + T * sg * (DOM_T / 2 + 0.003)
            parts.append(box((fc.x, fc.y, DOM_H / 2), (0.006, DOM_W - 0.07, 0.022), white, rot=(0, 0, deg), bevel=0))
            parts += [cyl((fc.x, fc.y, DOM_H / 2 + dz), 0.034, 0.008, white, rot=(0, 90, deg), verts=16) for dz in (0.15, -0.15)]
        pv = empty(f'Domino{i}', tuple(c + T * DOM_T / 2)); pv.rotation_euler = (0, 0, psi)
        parent(parts, pv); pivots.append((pv, psi)); parts_all.append(pv)
    gaps = [(pts[i + 1] - pts[i]).length for i in range(n - 1)]
    P = {'focus_z': 0.35, 'size': 0.28 * L, 'view_up': 0.32, 'dom': pivots, 'gaps': gaps, 'start': (-L / 2, 0.0, 0.0), 'end': (L / 2, 0.0, 0.0), 'actions': {}}

    def topple(P, t, o):
        S = max(_num(o, 'for', 2.0), 0.3); dom, gaps = P['dom'], P['gaps']; n = len(dom); FULL = 90.0
        touch = [math.degrees(math.asin(max(0.0, min(0.95, (g - DOM_T) / DOM_H)))) for g in gaps]
        k = sum(math.sqrt(a / FULL) for a in touch)
        T = S / (k + 1.0)                                  # one domino's fall; the next starts when this one touches it
        starts = [t]
        for a in touch:
            starts.append(starts[-1] + T * math.sqrt(a / FULL))
        for f in range(F(t) - 1, F(starts[-1] + T) + 3):
            tt = (f - 1) / FPS
            th = [FULL * min(max((tt - s0) / T, 0.0), 1.0) ** 2 for s0 in starts]
            for i in range(n - 2, -1, -1):                 # leaning on the next one: never through it
                lim = th[i + 1] - math.degrees(math.asin(max(-1.0, min(1.0, (DOM_T - gaps[i] * math.cos(math.radians(th[i + 1]))) / DOM_H))))
                th[i] = min(th[i], lim)
            for (pv, psi), a in zip(dom, th):
                pv.rotation_euler = (0, math.radians(a), psi); pv.keyframe_insert('rotation_euler', frame=f)
        for pv, _ in dom:
            for fc in _fcurves(pv):
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'
    P['setup'] = _register; P['actions']['topple'] = topple
    return P, parts_all


# ---------------------------------------------------------------- globe
GLOBE_Z, GLOBE_R, GLOBE_TILT = 1.8, 0.5, 23.5
GLOBE_GLOW, GLOBE_HALO = 0.18, 0.7


def _ring_halo_material(color):
    """A glowing ring round a ball: nothing over the ball's middle (so its colours stay), brightest just outside it, fading
    to nothing at the edge. 'Amount' (a Value node) turns it up and down."""
    m = bpy.data.materials.new('RingHalo'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*hexrgb(color), 1); em.inputs['Strength'].default_value = 1.6
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; inv.use_clamp = True
    L.new(lw.outputs['Facing'], inv.inputs[1])
    bell = nt.nodes.new('ShaderNodeMath'); bell.operation = 'MULTIPLY'; L.new(lw.outputs['Facing'], bell.inputs[0]); L.new(inv.outputs[0], bell.inputs[1])
    k4 = nt.nodes.new('ShaderNodeMath'); k4.operation = 'MULTIPLY'; k4.inputs[1].default_value = 4.0; L.new(bell.outputs[0], k4.inputs[0])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0; L.new(k4.outputs[0], pw.inputs[0])
    amt = nt.nodes.new('ShaderNodeValue'); amt.name = 'Amount'; amt.outputs[0].default_value = 0.0
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.use_clamp = True
    L.new(pw.outputs[0], mul.inputs[0]); L.new(amt.outputs[0], mul.inputs[1]); L.new(mul.outputs[0], mix.inputs['Fac'])
    L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = True
    return m


def _globe_material():
    m = bpy.data.materials.new('GlobeMap'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.32
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 0.6
    L = nt.links
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 2.0; nz.inputs['Detail'].default_value = 1.2; nz.inputs['Roughness'].default_value = 0.45
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L.new(sep.outputs['Z'], ab.inputs[0])
    cap = nt.nodes.new('ShaderNodeMath'); cap.operation = 'GREATER_THAN'; cap.inputs[1].default_value = 0.44; L.new(ab.outputs[0], cap.inputs[0])
    sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY_ADD'; sc.inputs[1].default_value = 0.8
    L.new(nz.outputs['Fac'], sc.inputs[0])
    c2 = nt.nodes.new('ShaderNodeMath'); c2.operation = 'MULTIPLY'; c2.inputs[1].default_value = 2.0; L.new(cap.outputs[0], c2.inputs[0])
    L.new(c2.outputs[0], sc.inputs[2])
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'; el = cr.color_ramp.elements
    el[0].position, el[0].color = 0.0, (*hexrgb('#2b7cf0'), 1)          # ocean
    el[1].position, el[1].color = 0.42, (*hexrgb('#f3d08a'), 1)         # sand at the coast
    e = el.new(0.437); e.color = (*hexrgb('#46c24a'), 1)                # land
    e = el.new(0.97); e.color = (*hexrgb('#f4fbff'), 1)                 # the ice caps
    L.new(sc.outputs[0], cr.inputs['Fac']); L.new(cr.outputs['Color'], b.inputs['Base Color'])
    L.new(cr.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 0.0
    return m


def globe():
    gold, navy = M('#f2c230', 0.28, metal=0.6), M('#24324f', 0.45, coat=0.5)
    mapm = _globe_material()
    ball = _sphere((0, 0, 0), GLOBE_R, mapm, segs=64)
    spin = _group('GlobeSpin', [ball], (0, 0, 0))
    Rm = GLOBE_R + 0.07
    ring = _tube([(Rm * math.sin(a), 0, Rm * math.cos(a)) for a in (math.pi * k / 40 for k in range(41))], 0.026, gold, name='GlobeMeridian')
    pins = [cyl((0, 0, sz * (GLOBE_R + 0.03)), 0.022, 0.09, gold, verts=12) for sz in (1, -1)]
    pins += [_sphere((0, 0, sz * Rm), 0.042, gold, segs=16) for sz in (1, -1)]
    tilt = _group('GlobeTilt', [spin, ring] + pins, (0, 0, 0))
    tilt.location = (0, 0, GLOBE_Z); tilt.rotation_euler = (0, math.radians(-GLOBE_TILT), 0)
    a = math.radians(GLOBE_TILT); sx, sz_ = Rm * math.sin(a), GLOBE_Z - Rm * math.cos(a)        # where the meridian's lower end meets the stand
    parts = [cyl((sx, 0, (0.1 + sz_) / 2), 0.04, sz_ - 0.1, gold, verts=20), _sphere((sx, 0, sz_), 0.055, gold, segs=16),
             cyl((sx, 0, 0.05), 0.42, 0.1, navy, verts=48), cyl((sx, 0, 0.13), 0.13, 0.07, gold, verts=32)]
    hm = _ring_halo_material('#ffd36b'); halo = _sphere((0, 0, GLOBE_Z), 1.05, hm, segs=48); halo.visible_shadow = False
    amount = hm.node_tree.nodes['Amount'].outputs[0]; em = mapm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    P = {'focus_z': GLOBE_Z - 0.1, 'size': 0.95, 'spin': spin, 'ang': 0.0, 'glow_now': 0.0, 'actions': {}}

    def spin_(P, t, o):
        t1 = P.get('t_end', t + 6.0) + 0.2; a0 = P['ang']; a1 = a0 + 2 * math.pi * (t1 - t) / 3.0
        _keys(P['spin'], 'rotation_euler', [(t, (0, 0, a0)), (t1, (0, 0, a1))], 'LINEAR'); P['ang'] = a1

    def glow(P, t, o):
        _socket_keys(amount, [(t, P['glow_now'] * GLOBE_HALO), (t + 0.5, GLOBE_HALO)])
        _socket_keys(em, [(t, P['glow_now'] * GLOBE_GLOW), (t + 0.5, GLOBE_GLOW)]); P['glow_now'] = 1.0
    P['setup'] = _register; P['actions'].update(spin=spin_, glow=glow)
    return P, parts + [tilt, halo]


# ---------------------------------------------------------------- cardboard box
def _carton(w, d, h):
    cb, tape = M('#c8955a', 0.7), M('#ecdcae', 0.4, coat=0.3)
    return [box((0, 0, h / 2), (w, d, h), cb, bevel=0.025),
            box((0, 0, h + 0.003), (0.13, d + 0.012, 0.008), tape, bevel=0),            # tape across the top, front to back
            box((0, -d / 2 - 0.003, h - 0.09), (0.13, 0.008, 0.18), tape, bevel=0),     # ... and down the front and back
            box((0, d / 2 + 0.003, h - 0.09), (0.13, 0.008, 0.18), tape, bevel=0)]


def _grip_for(fwd, side, want):
    """P['grip'] that puts a held prop's origin at `want` (the holder's own space, scale 1) with the right arm at forward fwd, sideways side."""
    v = Vector(want) - Vector((0.745, 0, 1.92))
    loc = Euler((math.radians(-fwd), math.radians(-side), 0), 'XYZ').to_matrix().inverted() @ v
    return (loc.x, loc.y, loc.z + 1.92)


BOX = 0.55
BOX_GRIP = _grip_for(55, 6, (0.3, -0.6, 1.17))       # 'carry' (arm 55 forward, 6 out): in front of the chest, its side in the right hand


def box_():
    return {'focus_z': BOX / 2, 'size': 0.4, 'grip': BOX_GRIP, 'setup': _register}, _carton(BOX, BOX, BOX)


# ---------------------------------------------------------------- conveyor belt
CONV_LOOP, CONV_SPEED, CONV_TOP, CONV_MOUTH = 3.6, 0.8, 0.9, 1.3
CONV_STRIPE = 0.36
CONV_BOXES = ((0.46, 0.44, 0.42, 6), (0.5, 0.46, 0.5, -5), (0.4, 0.4, 0.36, 9), (0.48, 0.42, 0.46, -8), (0.44, 0.44, 0.4, 3))


def conveyor():
    frame_m, rail, belt_m = M('#3d7be0', 0.4, coat=0.4), M('#ffc61a', 0.35, coat=0.5), M('#4a4f59', 0.75)
    stripe_m, roll, hood_m, flap_m = M('#9aa1ac', 0.6), M('#24272e', 0.4, metal=0.3), M('#ff7a2f', 0.4, coat=0.5), M('#20262e', 0.7)
    half, top = CONV_LOOP / 2, CONV_TOP
    parts = [box((0, 0, top - 0.035), (CONV_LOOP, 0.9, 0.07), belt_m, bevel=0.02)]
    parts += [cyl((sx * half, 0, top - 0.1), 0.1, 0.92, roll, rot=(90, 0, 0), verts=24) for sx in (-1, 1)]        # end rollers (inside the hoods)
    parts += [cyl((x, 0, top - 0.17), 0.065, 0.92, roll, rot=(90, 0, 0), verts=20) for x in (-0.9, -0.3, 0.3, 0.9)]   # rollers under the belt
    for sy in (-1, 1):
        parts += [box((0, sy * 0.5, top - 0.08), (CONV_LOOP + 0.1, 0.1, 0.2), frame_m, bevel=0.025),               # the frame's side beams
                  box((0, sy * 0.5, top + 0.06), (2 * CONV_MOUTH, 0.06, 0.06), rail, bevel=0.02)]                 # low guard rails
        for x in (-1.45, 1.45):
            parts += [box((x, sy * 0.42, (top - 0.18) / 2), (0.1, 0.1, top - 0.18), frame_m, bevel=0.02),
                      box((x, sy * 0.42, 0.02), (0.2, 0.2, 0.04), flap_m, bevel=0.01)]
    parts += [box((x, 0, 0.32), (0.08, 0.84, 0.08), frame_m, bevel=0.02) for x in (-1.45, 1.45)]
    parts.append(box((0, 0.42, 0.32), (2.9, 0.06, 0.06), frame_m, bevel=0.015))
    for sx in (-1, 1):                                    # hoods over both ends: the boxes go in under rubber flaps and come back out
        xc = sx * (CONV_MOUTH + 2.1) / 2; ln = 2.1 - CONV_MOUTH
        parts += [box((xc, 0, top + 0.78), (ln + 0.04, 1.2, 0.1), hood_m, bevel=0.04),
                  box((sx * 2.07, 0, top + 0.33), (0.06, 1.2, 0.9), hood_m, bevel=0.02)]
        parts += [box((xc, sy * 0.57, top + 0.33), (ln + 0.04, 0.06, 0.9), hood_m, bevel=0.02) for sy in (-1, 1)]
        parts += [box((sx * CONV_MOUTH, y, top + 0.37), (0.02, 0.165, 0.7), flap_m, bevel=0.005) for y in (-0.42, -0.21, 0.0, 0.21, 0.42)]
    stripes = [box((-half + CONV_STRIPE * k + 0.12, 0, top + 0.004), (0.05, 0.86, 0.012), stripe_m, bevel=0) for k in range(10)]
    sg = _group('ConveyorStripes', stripes, (0, 0, 0))
    boxes = []
    for i, (w, d, h, rz) in enumerate(CONV_BOXES):
        x0 = -1.08 + 0.72 * i
        g = _group(f'ConveyorBox{i}', _carton(w, d, h), (0, 0, 0)); g.location = (x0, 0.02 * ((i % 3) - 1), top); g.rotation_euler = (0, 0, math.radians(rz))
        boxes.append((g, x0))
    P = {'focus_z': 0.95, 'size': 1.25, 'stripes': sg, 'boxes': boxes, 'events': [], 'actions': {}}

    def rekey(P):
        ev = sorted(P['events']); t0 = ev[0][0]; t1 = P.get('t_end', ev[-1][0] + 6.0) + 0.2
        for ob in [P['stripes']] + [g for g, _ in P['boxes']]:
            ob.animation_data_clear()
        d, v, rows = 0.0, 0.0, []
        for f in range(F(t0), F(t1) + 1):
            tt = (f - 1) / FPS; run = [r for tr, r in ev if tr <= tt + 1e-6]
            goal = CONV_SPEED if run and run[-1] else 0.0
            step = (CONV_SPEED / 0.3 if goal > v else CONV_SPEED / 0.25) / FPS          # starts in 0.3 s, stops in 0.25 s
            v = min(goal, v + step) if goal > v else max(goal, v - step)
            rows.append((f, d)); d += v / FPS
        wrap = lambda x0, dd: math.floor((x0 + half + dd) / CONV_LOOP)
        for f, dd in rows:
            P['stripes'].location = (dd % CONV_STRIPE, 0, 0); P['stripes'].keyframe_insert('location', frame=f)
        for g, x0 in P['boxes']:
            y0, z0 = g.location.y, g.location.z
            for k, (f, dd) in enumerate(rows):
                n0 = wrap(x0, dd); nb = wrap(x0, rows[max(k - 1, 0)][1]); na = wrap(x0, rows[min(k + 1, len(rows) - 1)][1])
                g.location = (-half + (x0 + half + dd) % CONV_LOOP, y0, z0); g.keyframe_insert('location', frame=f)
                g.scale = (0.001,) * 3 if (n0 != nb or n0 != na) else (1, 1, 1); g.keyframe_insert('scale', frame=f)   # wraps round hidden in a hood
        for ob in [P['stripes']] + [g for g, _ in P['boxes']]:
            _interp(ob, 'LINEAR')

    def run(P, t, o):
        P['events'].append((t, True)); rekey(P)

    def stop(P, t, o):
        P['events'].append((t, False)); rekey(P)
    P['setup'] = _register; P['actions'].update(run=run, stop=stop)
    return P, parts + [sg] + [g for g, _ in boxes]


BUILDERS = dict(lamp=lamp, switch=switch, bow=bow, arrow=arrow, dominoes=dominoes, globe=globe, conveyor=conveyor, box=box_)
