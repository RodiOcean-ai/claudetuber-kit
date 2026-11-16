"""Props bank for the blocky world: everyday objects a scene table can place, frame and animate (built 5 Nov 2026 for the
toast episode). Every prop is built around its own origin (front facing -y, standing on z=0) and parented to a root.
- make(kind, loc, turn) -> P: {'root', 'kind', 'focus_z' (height the camera aims at), 'size' (framing scale), ...}
- act(P, action, t, opt): keys an action (see ACTIONS per kind). 'hide' / 'show' work on every prop.
- hold(P, R, t0, t1): the prop sits in R's right hand (or left with side='L') from t0 to t1, hidden outside that window.
Kinds: toaster, bread, toast, cloche, pasta, ice, card, frames, bulb, spatula, mark (an invisible camera target).
More kinds are registered in BUILD by scene.py:
- props_room.py: tank_jungle (grow, ask), tank_desert (snap), tank_forest (burn), tank_ants (charge), calendar_full (stamp),
  calendar_three, phone (buzz), sign (break), bench, uploads (burst).
- props_story.py (12 Nov 2026): satellite (glow, dim, squash, float 'up N', flash), cash (slide 'to X Y Z'), maze, cage (first row
  'tall N; radius N'), shark (circle 'around X Y; radius R; height Z; for S'), bubble (first row 'icon squirrel | shark | scammer |
  satellite'; orbit 'around X Y Z; radius R; speed REVS_PER_S; phase DEG', stop, flare, fade), magnifier (held: 'hold <who>').
  Their options are spelled out at the top of props_story.py."""
import math
import bpy
from common import FPS, hexrgb
from sf_world import box, cyl, empty, parent, text
from blocky_kit import M

ss = lambda u: 0 if u <= 0 else 1 if u >= 1 else u * u * (3 - 2 * u)
F = lambda t: 1 + round(t * FPS)                     # seconds -> frame


def _keys(ob, path, pts, interp='BEZIER'):
    """pts: [(seconds, value)]; value is a tuple for vector paths."""
    for t, v in pts:
        setattr(ob, path, v); ob.keyframe_insert(path, frame=F(t))
    act = ob.animation_data.action
    for fc in getattr(act, 'fcurves', None) or [fc for ly in act.layers for s in ly.strips for cb in s.channelbags for fc in cb.fcurves]:
        if fc.data_path == path:
            for k in fc.keyframe_points:
                k.interpolation = interp


def visible(objs, pts):
    """pts: [(seconds, shown?)] for every mesh/text below objs."""
    for o in objs:
        for c in [o] + list(o.children_recursive):
            if c.type in ('MESH', 'FONT'):
                for t, on in pts:
                    c.hide_render = c.hide_viewport = not on
                    c.keyframe_insert('hide_render', frame=max(0, F(t) if t > 0 else 0)); c.keyframe_insert('hide_viewport', frame=max(0, F(t) if t > 0 else 0))


def _sphere(loc, r, m, segs=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=segs // 2); o = bpy.context.object
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def _outline(w=0.5, h=0.56, r=0.05, n=28):
    """Bread-slice silhouette in x (width) and z (height), centred: square body, domed crown that overhangs a little."""
    zb, zs = -h / 2, h / 2 - 0.2                       # bottom, where the sides meet the crown
    pts = [(-w / 2 + r + r * math.cos(a), zb + r + r * math.sin(a)) for a in [math.pi + k * math.pi / 2 / 6 for k in range(7)]]
    pts += [(w / 2 - r + r * math.cos(a), zb + r + r * math.sin(a)) for a in [1.5 * math.pi + k * math.pi / 2 / 6 for k in range(7)]]
    a_, b_ = w / 2 + 0.035, h / 2 - zs                 # the crown: a wide half-ellipse sitting on the sides
    pts += [(w / 2, zs - 0.045)]
    pts += [(a_ * math.cos(t), zs + b_ * math.sin(t)) for t in [math.radians(-12 + k * 204 / n) for k in range(n + 1)]]
    pts += [(-w / 2, zs - 0.045)]
    return pts


def _plate_mesh(pts, y0, depth, m, name='Slice'):
    """Extrude a 2D outline (x, z) into a flat solid from y0 to y0 + depth."""
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new((x, y0, z)) for x, z in pts]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, depth, 0), verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(m)
    bv = o.modifiers.new('bev', 'BEVEL'); bv.width = min(0.012, depth / 3); bv.segments = 2; bv.limit_method = 'ANGLE'
    return o


def crumb_material(kind):
    """The cut face: a speckled crumb. Toast: charred patches over dark brown; bread: cream with golden pores."""
    key = 'Crumb_' + kind
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    stops = ([(0.30, '#120904'), (0.48, '#3d220f'), (0.62, '#6a3e1c'), (0.78, '#8a5a2c')] if kind == 'toast'
             else [(0.35, '#e2be7c'), (0.55, '#f4dfae'), (0.75, '#fbefcf')])
    m = bpy.data.materials.new(key); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.9
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 22.0; nz.inputs['Detail'].default_value = 8.0; nz.inputs['Roughness'].default_value = 0.65
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].position, el[0].color = stops[0][0], (*hexrgb(stops[0][1]), 1)
    el[1].position, el[1].color = stops[-1][0], (*hexrgb(stops[-1][1]), 1)
    for pos, col in stops[1:-1]:
        e = el.new(pos); e.color = (*hexrgb(col), 1)
    nt.links.new(nz.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35
    nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def _slice(loc, kind, k=1.0):
    """A slice of bread (kind 'bread') or burnt toast ('toast'), standing up, thin along y; k scales it."""
    crust = M('#a5642a', 0.75) if kind == 'bread' else M('#170d07', 0.85)
    pts = [(x * k, z * k) for x, z in _outline()]
    inner = [(x * 0.87, z * 0.87 - 0.012 * k) for x, z in pts]
    t = 0.055 * k; x0, y0, z0 = loc
    parts = [_plate_mesh(pts, -t / 2, t, crust, 'Crust'),
             _plate_mesh(inner, -t / 2 - 0.004 * k, 0.006 * k, crumb_material(kind), 'Crumb'),
             _plate_mesh(inner, t / 2 - 0.002 * k, 0.006 * k, crumb_material(kind), 'Crumb')]
    for o in parts:
        o.location = (x0, y0, z0)
    return parts


# ---------------------------------------------------------------- builders (local coordinates)
def toaster():
    red, chrome, dark = M('#e63946', 0.3, coat=0.5), M('#d9dde4', 0.15, metal=1.0), M('#1b1b22', 0.6)
    P = {'focus_z': 0.6, 'size': 0.8}
    parts = [box((0, 0, 0.34), (0.95, 0.55, 0.6), red, bevel=0.08), box((0, 0, 0.06), (0.99, 0.59, 0.1), chrome, bevel=0.03)]
    for sx in (-0.38, 0.38):
        for sy in (-0.2, 0.2):
            parts.append(box((sx, sy, 0.0), (0.1, 0.1, 0.03), dark, bevel=0.01))
    glow = M('#1b1b22', 0.6, emit=hexrgb('#ff7a1a'), emit_strength=0.0); glow.name = 'ToasterGlow'   # dark slots until they glow
    for sy in (-0.12, 0.12):
        parts.append(box((0, sy, 0.641), (0.6, 0.09, 0.006), glow, bevel=0))
    parts.append(box((0.478, 0, 0.36), (0.01, 0.05, 0.36), dark, bevel=0))
    parts.append(cyl((-0.28, -0.28, 0.24), 0.07, 0.03, chrome, rot=(90, 0, 0)))
    lever = box((0.52, 0, 0.0), (0.1, 0.16, 0.06), M('#1b1b22', 0.4), bevel=0.02)
    slices = [_slice((0, sy, 0.0), 'toast') for sy in (-0.12, 0.12)]
    bread = _slice((0, -0.12, 0.0), 'bread')
    smoke = [_sphere((0, 0, 0), 0.055, M('#a9a9b2', 1.0), segs=16) for _ in range(10)]
    P.update(parts=parts, lever=lever, slices=slices, bread=bread, smoke=smoke, glow=glow)
    return P, parts + [lever] + sum(slices, []) + bread + smoke


SLICE_REST, SLICE_UP, LEVER_UP, LEVER_DOWN = 0.31, 0.6, 0.56, 0.22    # slice top: z + 0.28


def _arc(major, minor, loc, m, frac=0.5, flat=0.3, rot=0):
    """A part of a flattened ring: a sauce swoosh or a syrup drizzle."""
    import bmesh
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, major_segments=48, minor_segments=10)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if math.atan2(v.co.y, v.co.x) % (2 * math.pi) > frac * 2 * math.pi], context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.scale = (1, 1, flat); o.rotation_euler = (0, 0, math.radians(rot))
    return o


def _leaf(loc, size, m, rot):
    o = _sphere(loc, size, m, segs=12); o.scale = (1.0, 0.45, 0.12); o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o


def _plate(r=0.55, well=0.36, col='#ffffff'):
    white = M(col, 0.25, coat=0.6)
    return [cyl((0, 0, 0.025), r, 0.05, white, verts=64), cyl((0, 0, 0.03), well, 0.052, M('#f4f4f2', 0.3, coat=0.6), verts=64)]


def plate_with(kind):
    silver, gold = M('#d9dde4', 0.15, metal=1.0), M('#e8b93a', 0.25, metal=1.0)
    green, dgreen = M('#5cb85c', 0.5), M('#2f7d3a', 0.5)
    if kind == 'cloche':                               # fine dining: a seared medallion, caviar, a wine-sauce swoosh, gold leaf
        parts = _plate()
        parts.append(_arc(0.24, 0.03, (0, 0, 0.058), M('#6e0f1f', 0.15, coat=1.0), frac=0.55, flat=0.22, rot=150))
        for k in range(5):                             # dots of golden puree along the swoosh
            a = math.radians(-40 + 22 * k); parts.append(cyl((0.31 * math.cos(a), 0.31 * math.sin(a), 0.058), 0.018 - 0.002 * k, 0.012, M('#f2a33a', 0.3, coat=0.6)))
        parts += [cyl((0.0, 0.02, 0.1), 0.12, 0.08, M('#6b3518', 0.55)), cyl((0.0, 0.02, 0.141), 0.115, 0.004, M('#2a1308', 0.7))]
        for k in range(14):                            # a quenelle of caviar on top
            a = k * 2.4; r = 0.035 * math.sqrt(k / 14)
            parts.append(_sphere((r * math.cos(a), 0.02 + r * math.sin(a), 0.155 + 0.01 * (k % 3)), 0.014, M('#0d0d12', 0.1, coat=1.0), segs=10))
        for k, (dx, dy) in enumerate(((0.09, 0.08), (-0.08, 0.1), (0.1, -0.05))):
            parts.append(_leaf((dx, 0.02 + dy, 0.15), 0.04, green if k % 2 else dgreen, (20, 10, 40 * k)))
        for dx, dy in ((0.05, -0.06), (-0.06, -0.03), (0.13, 0.15)):
            parts.append(box((dx, dy, 0.146), (0.03, 0.03, 0.002), M('#ffd23a', 0.2, metal=1.0, emit=hexrgb('#ffb000'), emit_strength=0.6), rot=(0, 0, 30), bevel=0))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, location=(0, 0, 0.05), segments=48, ring_count=24); dome = bpy.context.object
        dome.scale = (1, 1, 0.85); dome.data.materials.append(silver); bpy.ops.object.shade_smooth()
        import bmesh
        bm = bmesh.new(); bm.from_mesh(dome.data); bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.001], context='VERTS'); bm.to_mesh(dome.data); bm.free()
        knob = _sphere((0, 0, 0.5), 0.06, silver)
        lid = empty('ClocheLid'); parent([dome, knob], lid)
        return {'focus_z': 0.18, 'size': 0.42, 'lid': lid}, parts + [dome, knob]
    if kind == 'pasta':                                # one tiny bow-tie on a dot of tomato sauce, placed with tweezers
        parts = _plate(0.5, 0.32)
        parts.append(cyl((0, 0, 0.058), 0.045, 0.006, M('#c8321e', 0.2, coat=1.0)))
        for sx in (-1, 1):                             # farfalle: two little wings and a pinched middle
            w = cyl((sx * 0.009, 0, 0.066), 0.011, 0.004, M('#f2c86b', 0.45), rot=(0, 0, 90 + 90 * sx), smooth=False, verts=3); parts.append(w)
        parts.append(box((0, 0, 0.066), (0.005, 0.008, 0.006), M('#e0b050', 0.45), bevel=0))
        parts.append(_leaf((0.03, 0.02, 0.064), 0.012, green, (0, 0, 35)))
        for k in range(4):                             # olive oil drops
            a = 1.2 + 0.5 * k; parts.append(cyl((0.1 * math.cos(a), 0.1 * math.sin(a), 0.058), 0.008, 0.004, M('#e8c23a', 0.1, coat=1.0)))
        for sx in (-1, 1):                             # tweezers lying across the rim, tips toward the pasta
            parts.append(box((0.17, -0.1 + sx * 0.008, 0.07), (0.26, 0.009, 0.007), silver, rot=(0, 3, 32 + sx * 3), bevel=0.002))
        return {'focus_z': 0.06, 'size': 0.2, 'view_up': 0.85}, parts
    if kind == 'ice':                                  # one clear ice cube on black slate: mint, gold leaf, a syrup drizzle
        parts = [box((0, 0, 0.02), (0.95, 0.6, 0.04), M('#2a2c33', 0.9), bevel=0.01)]
        ice = M('#e8f6ff', 0.03, coat=1.0); ib = ice.node_tree.nodes['Principled BSDF']
        ib.inputs['Transmission Weight'].default_value = 0.92; ib.inputs['IOR'].default_value = 1.31
        cube = box((0, 0, 0.15), (0.22, 0.22, 0.22), ice, bevel=0.035); cube.rotation_euler = (0, 0, 0.35); parts.append(cube)
        parts.append(_arc(0.2, 0.008, (0.0, 0.0, 0.043), M('#c97a1a', 0.1, coat=1.0), frac=0.35, flat=0.4, rot=200))
        for k, (dx, dy) in enumerate(((0.2, -0.12), (0.24, -0.07), (0.17, -0.06))):
            parts.append(_leaf((dx, dy, 0.05), 0.04, green if k % 2 else dgreen, (0, 0, 60 * k)))
        for dx, dy in ((-0.2, 0.1), (0.05, 0.17), (0.12, 0.14)):
            parts.append(box((dx, dy, 0.043), (0.035, 0.035, 0.002), M('#ffd23a', 0.2, metal=1.0, emit=hexrgb('#ffb000'), emit_strength=0.6), rot=(0, 0, 25), bevel=0))
        for k in range(3):                             # flakes of sea salt
            parts.append(box((-0.15 + 0.04 * k, -0.15, 0.045), (0.012, 0.012, 0.008), M('#ffffff', 0.5), rot=(0, 0, 20 * k), bevel=0))
        return {'focus_z': 0.12, 'size': 0.32}, parts


def card(label='670M', sub='VIEWS', s=1.0):
    panel = box((0, 0, 0), (3.2, 0.16, 1.9), M('#1d1d24', 0.35), bevel=0.2)
    ring = box((0, 0.06, 0), (3.36, 0.1, 2.06), M('#36d17a', 0.4, emit=hexrgb('#36d17a'), emit_strength=2.5), bevel=0.22)
    big = text(label, (0, -0.1, 0.18), 0.95, M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=1.5), extrude=0.04)
    small = text(sub, (0, -0.1, -0.55), 0.38, M('#36d17a', 0.4, emit=hexrgb('#36d17a'), emit_strength=2.0), extrude=0.03)
    bpy.context.view_layer.update()
    for o, wmax in ((big, 2.8), (small, 2.9)):           # long words shrink to fit the card ("NEARLY 6M")
        if o.dimensions.x > wmax:
            o.scale = (wmax / o.dimensions.x,) * 3
    return {'focus_z': 0.0, 'size': 1.0 * s, 's': s}, [panel, ring, big, small]


def play_badge(cx, w, y=-0.105, cz=0.0):
    """The video-site play badge as a glossy 3D button: a red rounded rectangle (proportions 1 : 0.7, squircle corners)
    standing 5 cm proud of the frame, a white play triangle raised on its face (the real logo's shape)."""
    h = 0.7 * w; n = 4.0                               # a superellipse gives the logo's soft, wide corners
    pts = []
    for k in range(72):
        t = 2 * math.pi * k / 72; c, s = math.cos(t), math.sin(t)
        pts.append((cx + w / 2 * math.copysign(abs(c) ** (2 / n), c), cz + h / 2 * math.copysign(abs(s) ** (2 / n), s)))
    red = M('#ff0000', 0.22, coat=1.0)
    th = 0.43 * h; tw = 0.87 * th; x0 = cx - tw / 3 + 0.012 * w          # the triangle's middle sits on the badge's middle
    tri = [(x0, cz - th / 2), (x0 + tw, cz), (x0, cz + th / 2)]
    return [_plate_mesh(pts, y, 0.05, red, 'PlayBadge'), _plate_mesh(tri, y - 0.012, 0.013, M('#ffffff', 0.3, coat=0.6), 'PlayTriangle')]


def frames():
    """Two picture frames on a wall (the wall is at local y=+0.05, facing -y), the second stamped COPY, bars below."""
    wood, gold, grey = M('#7a4a2a', 0.6), M('#f2c230', 0.3, metal=0.4), M('#9aa3b2', 0.6)
    parts, bars = [], []
    for k, sx in enumerate((-1.1, 1.1)):
        parts += [box((sx, 0, 0), (1.5, 0.08, 1.1), wood, bevel=0.03), box((sx, -0.045, 0), (1.3, 0.02, 0.9), M('#bfe2ff', 0.6), bevel=0)]
        parts += play_badge(sx, 0.74)                  # owner, 7 Nov 2026: make it look like the real logo, as on the cover
        bar = box((sx, -0.02, -1.8), (0.7, 0.1, 1.0), gold if k == 0 else grey, bevel=0.03)
        bar_root = empty(f'Bar{k}', (sx, -0.02, -2.3)); parent([bar], bar_root); bars.append(bar_root)
    stamp = text('COPY', (1.1, -0.1, -0.02), 0.5, M('#e63946', 0.4, emit=hexrgb('#e63946'), emit_strength=1.0), rot=(90, -14, 0), extrude=0.02)
    return {'focus_z': -0.6, 'size': 1.25, 'bars': bars, 'stamp': stamp}, parts + [stamp] + bars


def bulb():
    glass = M('#fff3a6', 0.2, emit=hexrgb('#ffe14d'), emit_strength=0.0); glass.name = 'BulbGlass'
    return {'focus_z': 0.0, 'size': 0.5, 'glass': glass}, [_sphere((0, 0, 0.1), 0.26, glass, segs=32), cyl((0, 0, -0.2), 0.12, 0.18, M('#9aa3b2', 0.3, metal=0.8))]


def spatula():
    return {'focus_z': 0.0, 'size': 0.2}, [box((0, 0, 0.0), (0.03, 0.03, 0.4), M('#2b2b33', 0.5), bevel=0.008),
                                           box((0, 0, 0.27), (0.14, 0.02, 0.16), M('#d9dde4', 0.2, metal=0.9), bevel=0.01)]


def single_slice(kind):
    # held: with the 'show' move (arm up 125 deg) and tilt 125 the slice stands upright just in front of the fist,
    # its lower edge in the hand (grip worked out in the shoulder's own space)
    return {'focus_z': 0.0, 'size': 0.3, 'grip': (0.0, -0.028, 0.74)}, _slice((0, 0, 0), kind, k=1.2)


def back_wall():
    """The missing fourth wall of a room (faces +y), for shots filmed from the front of the class; a notice board at local x=+3."""
    return {'focus_z': 0.0, 'size': 1.0}, [box((0, 0, 0), (12.4, 0.2, 5.0), M('#eef3e2', 0.9), bevel=0), box((3.0, 0.12, 0.4), (2.6, 0.06, 1.7), M('#b5763d', 0.7), bevel=0.02),
                                           box((2.3, 0.17, 0.6), (0.7, 0.02, 0.9), M('#ffd166', 0.8), bevel=0), box((3.3, 0.17, 0.3), (0.8, 0.02, 0.6), M('#f4978e', 0.8), bevel=0), box((3.9, 0.17, 0.75), (0.5, 0.02, 0.5), M('#8ecae6', 0.8), bevel=0)]


BUILD = dict(toaster=toaster, cloche=lambda: plate_with('cloche'), pasta=lambda: plate_with('pasta'), ice=lambda: plate_with('ice'),
             mark=lambda: ({'focus_z': 0.0, 'size': 0.3}, []), card=card, frames=frames, back_wall=back_wall, bulb=bulb, spatula=spatula, bread=lambda: single_slice('bread'), toast=lambda: single_slice('toast'))


def make(kind, name, loc=(0, 0, 0), turn=0.0, **kw):
    P, objs = BUILD[kind](**kw)
    root = empty(name); parent([o for o in objs if o.parent is None], root)
    root.location = loc; root.rotation_euler = (0, 0, math.radians(turn))
    P.update(root=root, kind=kind, name=name, loc=tuple(loc), turn=turn, prop=True, scale=1.0)
    if kind == 'toaster':                              # rest state: toast down in the slots, lever down, no smoke, no bread
        for k, sl in enumerate(P['slices']):
            g = empty(f'Slice{k}', (0, 0, 0)); parent(sl, g); P['slices'][k] = g; g.location = (0, 0, SLICE_REST); g.parent = root
        g = empty('Bread', (0, 0, 0)); parent(P['bread'], g); g.parent = root; P['bread'] = g; visible([g], [(0, False)])
        P['lever'].parent = root; P['lever'].location = (0, 0, LEVER_DOWN)
        visible(P['smoke'], [(0, False)])
        for s in P['smoke']:
            s.parent = root
    if kind == 'cloche':
        P['lid'].parent = root
    if kind == 'frames':
        for b in P['bars']:
            b.parent = root; b.scale = (1, 1, 0.001)
        P['stamp'].parent = root; P['stamp'].scale = (0.001,) * 3
    if kind == 'card':
        root.scale = (0.001,) * 3
    if kind == 'bulb':
        root.scale = (0.001,) * 3
    if 'setup' in P:                                   # builders from props_room.py finish themselves here
        P['setup'](P)
    return P


# ---------------------------------------------------------------- actions
def act(P, action, t, opt=None):
    o = opt or {}
    if action == 'hide':                               # a second hide/show keeps the earlier ones (13 Nov 2026: a prop hidden,
        if not P.get('held'):                          # shown and hidden again came back from the start)
            visible([P['root']], ([] if P.get('vis_keyed') else [(0, True)]) + [(t, False)]); P['vis_keyed'] = True
        return
    if action == 'show':
        visible([P['root']], [(t, True)]); P['vis_keyed'] = True; return
    if action in P.get('actions', {}):                # props_room.py: tank grow/ask/snap/burn/charge, phone buzz, sign break
        P['actions'][action](P, t, o); return
    k = P['kind']
    if k == 'toaster':
        if action == 'pop':                            # lever jumps up, both slices shoot up and settle, smoke puffs
            _keys(P['lever'], 'location', [(t - 0.02, (0, 0, LEVER_DOWN)), (t + 0.04, (0, 0, LEVER_UP))], 'LINEAR')
            for i, g in enumerate(P['slices']):
                d = 0.02 * i
                _keys(g, 'location', [(t - 0.02, (0, 0, SLICE_REST)), (t + 0.1 + d, (0, 0, SLICE_UP + 0.1)), (t + 0.22 + d, (0, 0, SLICE_UP - 0.04)), (t + 0.32 + d, (0, 0, SLICE_UP))])
            for j, s in enumerate(P['smoke']):         # puffs rise, swell and vanish over about 1.4 s
                t0 = t + 0.05 * j; x0 = (j % 3 - 1) * 0.18; y0 = (-0.12, 0.12)[j % 2]
                visible([s], [(0, False), (t0, True), (t0 + 1.4, False)])
                _keys(s, 'location', [(t0, (x0, y0, 0.66)), (t0 + 1.4, (x0 * 1.4, y0 - 0.1, 1.15 + 0.04 * j))], 'LINEAR')
                _keys(s, 'scale', [(t0, (0.5,) * 3), (t0 + 0.7, (1.6,) * 3), (t0 + 1.39, (0.3,) * 3)])
        elif action == 'take':                         # one popped slice leaves (it is now in someone's hand)
            visible([P['slices'][o.get('slot', 0)]], [(0, True), (t, False)])
        elif action == 'empty':                        # the slices are gone, the lever is up
            visible(P['slices'], [(0, True), (t, False)])
        elif action == 'glow':
            n = P['glow'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
            for tt, v in ((t, 0.0), (t + 0.6, 6.0)):
                n.default_value = v; n.keyframe_insert('default_value', frame=F(tt))
            if 'off' in o:
                n.default_value = 0.0; n.keyframe_insert('default_value', frame=F(o['off']))
        elif action == 'load':                         # bread drops into the front slot, then the lever goes down
            visible([P['bread']], [(0, False), (t, True)])
            _keys(P['bread'], 'location', [(t, (0, 0, SLICE_REST + 0.75)), (t + 0.3, (0, 0, SLICE_UP)), (t + 0.42, (0, 0, SLICE_UP))])
            _keys(P['bread'], 'location', [(t + 0.42, (0, 0, SLICE_UP)), (t + 0.6, (0, 0, SLICE_REST))])
            _keys(P['lever'], 'location', [(t + 0.42, (0, 0, LEVER_UP)), (t + 0.6, (0, 0, LEVER_DOWN))])
    elif k == 'cloche' and action == 'lift':
        _keys(P['lid'], 'location', [(t, (0, 0, 0)), (t + 0.45, (0.25, 0.1, 0.75))]); _keys(P['lid'], 'rotation_euler', [(t, (0, 0, 0)), (t + 0.45, (0, math.radians(35), 0))])
    elif k in ('card', 'bulb') and action in ('rise', 'on'):
        c = P.get('s', 1.0)
        _keys(P['root'], 'scale', [(t, (0.001,) * 3), (t + 0.22, (1.12 * c,) * 3), (t + 0.35, (c,) * 3)])
        if k == 'card':
            z = P['loc'][2]; _keys(P['root'], 'location', [(t, (P['loc'][0], P['loc'][1], z - 1.2)), (t + 0.35, P['loc'])])
        else:
            n = P['glass'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
            for tt, v in ((t + 0.1, 0.0), (t + 0.3, 8.0), (t + 0.45, 5.0)):
                n.default_value = v; n.keyframe_insert('default_value', frame=F(tt))
    elif k == 'frames' and action == 'grow':
        _keys(P['bars'][0], 'scale', [(t, (1, 1, 0.001)), (t + 0.6, (1, 1, 1.5))])
        _keys(P['bars'][1], 'scale', [(t + 1.4, (1, 1, 0.001)), (t + 1.8, (1, 1, 0.09))])
        _keys(P['stamp'], 'scale', [(t + 0.5, (0.001,) * 3), (t + 0.62, (1.3,) * 3), (t + 0.75, (1.0,) * 3)])


def hold(P, R, t0, t1, side='R', offset=None, tilt=(0, 0, 0)):
    """The prop rides in R's hand from t0 to t1 (hidden outside). Parented to the shoulder pivot, so it follows the arm."""
    from mathutils import Matrix
    offset = offset or P.get('grip', (0.0, -0.32, 1.02))
    P['root'].parent = R['sh' + side]; P['root'].matrix_parent_inverse = Matrix.Identity(4)   # in the shoulder's own space
    P['root'].location = (offset[0], offset[1], offset[2] - 1.92)                             # the hand, below the shoulder
    P['root'].rotation_euler = tuple(math.radians(a) for a in tilt); P['root'].scale = (1, 1, 1)
    P['held'] = (R, t0, t1)
    visible([P['root']], [(0, False), (t0, True), (t1, False)] if t0 > 0 else [(0, True), (t1, False)])
