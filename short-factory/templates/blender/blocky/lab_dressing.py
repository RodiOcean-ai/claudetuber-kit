"""Things in the underwater lab (owner, 10 Nov 2026): real objects that carry the channel's name the way the format benchmark paints its name on
a football field or a boat's hull, and things Ginger can run into (like the benchmark's girl on the bicycle who crashes in most Shorts).

dress(X, Y, S, tall, pieces, logo) builds the pieces and returns {'bumps': {...}, 'spots': {...}}.
Pieces (scene line 'dress: crates, buoy, sub'; that is the default):
  crates    a stack of supply crates on the left, "@RODIOCEAN" and "SUBSCRIBE" sprayed on with a stencil. Bump: Ginger runs into
            the side of the stack (move 'bonk') and the top crate rocks.
  buoy      a lifebuoy hanging on a post on the right, "@RODIOCEAN" / "SUBSCRIBE" printed round the ring like a ship's name and
            port. Bump: Ginger runs into the post ('bonk') and the ring swings.
  sub       a little submarine parked on the sand far behind, right of the screen; RODIOCEAN in the owner's water letters on the
            hull and SUBSCRIBE under it, like a ship's name and home port. Background only.
  tank      a fish tank on a low cabinet on the left (instead of the crates) with a fish swimming in it. Bump: Ginger pounces at
            the fish and hits the glass ('smack'); the tank shakes and the fish darts away.
  hose      a dive cylinder at the back left ("@RODIOCEAN" stencilled down it) with its air hose snaking across the floor.
            Bump: Ginger trips over the hose ('trip') and somersaults.
ONE piece carries the name per Short (owner, 10 Nov 2026: "One per Short"): without a 'logo:' line the scene picks one of the
pieces that are there (crates, buoy, sub, hose), a different one for each scene file; 'logo: buoy' names it; 'floor' and
'pedestal' are the older painted floor line and a maker's badge on the screen's pedestal; 'logo: none' for none.
crates, tank and hose share the left side: use one of them at a time."""
import math
import os
import random

import bpy

from common import hexrgb, FPS
from sf_world import cyl, empty, parent
from blocky_kit import M

PRINTS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'assets', 'brand', 'world_prints'))
NOSE = 1.12                     # Ginger's nose ahead of her middle (scale 1); she is drawn at scale 0.5
PAW = 0.72                      # her front paws ahead of her middle
REACH = 1.6                     # how far a 'smack' pounce flies before it meets the glass (scale 1)
LANE = 3.2                      # Ginger's background lane: this far behind the lab's centre line
SIDE_X = 3.0                    # the left and right things stand this far out from the middle: inside a Short's medium shot
                                # (a tall frame shows only about 6.5 units of background), so her run, the hit and the fall all show
CAT = 0.5


def box(loc, size, m, rot=(0, 0, 0), bevel=0.02):
    """Like sf_world.box, but the box keeps its own centre (sf_world's moves it to the world's middle), so prints are placed
    on it in its own measurements and a knock rocks it round itself."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=tuple(math.radians(r) for r in rot)); o = bpy.context.object
    o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 3
    o.data.materials.append(m)
    return o


# ---------------------------------------------------------------- printed materials
def printed(base_hex, rough, prints, name='Printed', metal=0.0, bands=None):
    """A material carrying prints, each projected onto the faces that point one way (object space), so the paint follows the
    object's own shading, curves and shadows instead of floating on top like a sticker.
    prints: [dict(img, n=(0,-1,0), right=(1,0,0), up=(0,0,1), c=(0,0,0), w=1.0)]: the picture's centre c and width w in
    the object's own units; its height follows the picture's shape. bands: (hex, fn(nt, coords) -> mask socket) for stripes."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    tc = nt.nodes.new('ShaderNodeTexCoord')
    col = nt.nodes.new('ShaderNodeRGB'); col.outputs[0].default_value = (*hexrgb(base_hex), 1); cur = col.outputs[0]
    if bands:
        bhex, fn = bands
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        nt.links.new(fn(nt, tc.outputs['Object']), mix.inputs['Factor']); nt.links.new(cur, mix.inputs['A'])
        mix.inputs['B'].default_value = (*hexrgb(bhex), 1); cur = mix.outputs['Result']
    for p in prints:
        path = os.path.join(PRINTS, p['img'])
        if not os.path.exists(path):
            continue
        img = bpy.data.images.load(path, check_existing=True); asp = img.size[1] / img.size[0]
        w = p['w']; h = w * asp
        sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = p.get('c', (0, 0, 0))
        nt.links.new(tc.outputs['Object'], sub.inputs[0])
        uv = []
        for axis, size in ((p.get('right', (1, 0, 0)), w), (p.get('up', (0, 0, 1)), h)):
            d = nt.nodes.new('ShaderNodeVectorMath'); d.operation = 'DOT_PRODUCT'; d.inputs[1].default_value = axis
            nt.links.new(sub.outputs[0], d.inputs[0])
            k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY_ADD'; k.inputs[1].default_value = 1 / size; k.inputs[2].default_value = 0.5
            nt.links.new(d.outputs['Value'], k.inputs[0]); uv.append(k.outputs[0])
        cxyz = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(uv[0], cxyz.inputs[0]); nt.links.new(uv[1], cxyz.inputs[1])
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.extension = 'CLIP'; tex.interpolation = 'Cubic'
        nt.links.new(cxyz.outputs[0], tex.inputs['Vector'])
        face = nt.nodes.new('ShaderNodeVectorMath'); face.operation = 'DOT_PRODUCT'; face.inputs[1].default_value = p.get('n', (0, -1, 0))
        nt.links.new(tc.outputs['Normal'], face.inputs[0])
        fm = nt.nodes.new('ShaderNodeMapRange'); fm.inputs['From Min'].default_value = 0.25; fm.inputs['From Max'].default_value = 0.55
        nt.links.new(face.outputs['Value'], fm.inputs['Value'])
        a = nt.nodes.new('ShaderNodeMath'); a.operation = 'MULTIPLY'
        nt.links.new(tex.outputs['Alpha'], a.inputs[0]); nt.links.new(fm.outputs['Result'], a.inputs[1])
        if p.get('ink'):                                    # one ink colour (white floor paint); else the picture's own colours
            ink = nt.nodes.new('ShaderNodeRGB'); ink.outputs[0].default_value = (*hexrgb(p['ink']), 1); src = ink.outputs[0]
            k2 = nt.nodes.new('ShaderNodeMath'); k2.operation = 'MULTIPLY'; k2.inputs[1].default_value = p.get('alpha', 1.0)
            nt.links.new(a.outputs[0], k2.inputs[0]); a = k2
        else:
            src = tex.outputs['Color']
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        nt.links.new(a.outputs[0], mix.inputs['Factor']); nt.links.new(cur, mix.inputs['A']); nt.links.new(src, mix.inputs['B'])
        cur = mix.outputs['Result']
    nt.links.new(cur, b.inputs['Base Color'])
    return m


def _keys(ob, path, frames_values):
    for f, v in frames_values:
        setattr(ob, path, v); ob.keyframe_insert(path, frame=f)


def wobble(ob, t0, amps=(0, 0, 0), hz=4.0, decay=3.0, dur=1.6, path='rotation_euler', hop=0.0):
    """A knocked object rocks and settles: per axis amp (degrees, or units for location) * e^(-decay t) * sin(2 pi hz t);
    hop lifts it a little at the hit."""
    base = list(getattr(ob, path)); f0 = 1 + round(t0 * FPS)
    for f in range(f0 - 1, f0 + round(dur * FPS) + 2):
        t = max(0.0, (f - f0) / FPS); s = math.exp(-decay * t) * math.sin(2 * math.pi * hz * t)
        v = [b + (math.radians(a * s) if path == 'rotation_euler' else a * s) for b, a in zip(base, amps)]
        setattr(ob, path, v); ob.keyframe_insert(path, frame=f)
    if hop:
        x, y, z = ob.location
        _keys(ob, 'location', [(f0 - 1, (x, y, z)), (f0 + 3, (x, y, z + hop)), (f0 + 7, (x, y, z))])


# ---------------------------------------------------------------- the pieces
def crates(X, Y, S, logo):
    """Left side: a big crate in Ginger's lane, a small one behind it, a third tipped on top."""
    lx = X - SIDE_X; wood = '#d9b583'; edge = M('#a8814f', 0.75)
    def crate(c, size, rz, prints):
        mat = printed(wood, 0.8, prints if logo else [], name='Crate')
        o = box(c, size, mat, bevel=0.04)
        w, d, h = size; parts = []
        for sx in (-1, 1):                                # the frame planks on the front and the sides
            parts.append(box((c[0] + sx * (w / 2 - 0.06), c[1] - d / 2 - 0.02, c[2]), (0.12, 0.05, h), edge, bevel=0.012))
        for sz in (-1, 1):
            parts.append(box((c[0], c[1] - d / 2 - 0.02, c[2] + sz * (h / 2 - 0.06)), (w, 0.05, 0.12), edge, bevel=0.012))
        parent(parts, o); o.rotation_euler = (0, 0, math.radians(rz))
        return o
    big = crate((lx + 0.78, Y + LANE + 0.2, 0.68), (1.56, 1.5, 1.36), 0,
                [dict(img='crate_name.png', c=(0, 0, -0.08), w=1.3)])
    crate((lx + 0.45, Y + LANE + 1.75, 0.55), (1.1, 1.1, 1.1), -9, [])
    top = crate((lx + 0.86, Y + LANE + 0.15, 1.36 + 0.52), (1.04, 1.04, 1.04), 11,
                [dict(img='crate_sub.png', c=(0, 0, 0.0), w=0.78)])
    contact = (lx, Y + LANE)
    def react(t):
        wobble(top, t, amps=(0, -14, 6), hz=3.0, decay=3.2, dur=1.5, hop=0.12)
        wobble(big, t, amps=(0.04, 0, 0), hz=9, decay=8, dur=0.6, path='location')
    return {'crates': dict(move='bonk', dir=(1, 0), contact=contact, start='bg_left', react=react,
                           spot=(contact[0] - NOSE * CAT, contact[1], 0, 90))}


def _buoy_bands(nt, co):
    """Two white reflective bands on the sides of the ring (|x| large, |y| small in the ring's own plane)."""
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(co, sep.inputs[0])
    ax = nt.nodes.new('ShaderNodeMath'); ax.operation = 'ABSOLUTE'; nt.links.new(sep.outputs['X'], ax.inputs[0])
    ay = nt.nodes.new('ShaderNodeMath'); ay.operation = 'ABSOLUTE'; nt.links.new(sep.outputs['Y'], ay.inputs[0])
    gx = nt.nodes.new('ShaderNodeMath'); gx.operation = 'GREATER_THAN'; gx.inputs[1].default_value = 0.5; nt.links.new(ax.outputs[0], gx.inputs[0])
    ly = nt.nodes.new('ShaderNodeMath'); ly.operation = 'LESS_THAN'; ly.inputs[1].default_value = 0.16; nt.links.new(ay.outputs[0], ly.inputs[0])
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; nt.links.new(gx.outputs[0], mm.inputs[0]); nt.links.new(ly.outputs[0], mm.inputs[1])
    return mm.outputs[0]


def buoy(X, Y, S, logo):
    """Right side: a lifebuoy on a post, like the ones on every ship's rail."""
    px, py = X + SIDE_X + 0.1, Y + LANE
    post = M('#eef4f8', 0.4, metal=0.3)
    cyl((px, py, 0.06), 0.42, 0.12, M('#9fb3c2', 0.6), verts=32)                     # the foot
    pole = cyl((px, py, 1.55), 0.1, 3.1, post, verts=24)
    arm = box((px, py - 0.22, 3.0), (0.12, 0.5, 0.12), post, bevel=0.03)
    hook = empty('BuoyHook', (px, py - 0.42, 2.98))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.74, minor_radius=0.21, major_segments=64, minor_segments=24,
                                     location=(px, py - 0.42, 2.98 - 0.98), rotation=(math.radians(90), 0, 0))
    ring = bpy.context.object; ring.name = 'Lifebuoy'; bpy.ops.object.shade_smooth()
    ring.data.materials.append(printed('#ff6a3d', 0.45, [dict(img='buoy_ring.png', n=(0, 0, 1), right=(1, 0, 0), up=(0, 1, 0),
                                                              c=(0, 0, 0), w=1.9)] if logo else [],
                                       name='Lifebuoy', bands=('#f4f7f9', _buoy_bands)))
    rope = cyl((px, py - 0.42, 2.98 - 0.12), 0.025, 0.24, M('#e8e1cf', 0.8), verts=12)  # the lanyard from the hook
    parent([ring, rope], hook)
    contact = (px + 0.1, py)
    def react(t):
        wobble(hook, t, amps=(6, -18, 0), hz=1.1, decay=1.4, dur=2.5)                 # the ring swings on its hook
    return {'buoy': dict(move='bonk', dir=(-1, 0), contact=contact, start='bg_right', react=react,
                         spot=(contact[0] + NOSE * CAT, contact[1], 0, -90))}


def sub(X, Y, S, tall, logo):
    """Far back on the right: a little research submarine parked on the sand."""
    hw = S['w'] / 2; cx, cy = (X + hw + 3.0, Y + 13.0) if tall else (X + hw + 3.2, Y + 14.0)
    L, R = 2.7, 1.1; cz = R + 0.25
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=(cx, cy, cz))
    hull = bpy.context.object; hull.name = 'MiniSub'; hull.scale = (L, R, R); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    stripe = lambda nt, co: _sub_stripe(nt, co)
    hull.data.materials.append(printed('#f3f7fa', 0.35, [dict(img='hull.png', n=(0, -1, 0), right=(1, 0, 0), up=(0, 0, 1),
                                                              c=(0.3, 0, 0.1), w=3.3)] if logo else [],
                                       name='SubHull', bands=('#0b2540', stripe)))
    tower = box((cx - 0.35, cy, cz + R + 0.28), (1.5, 0.95, 0.75), M('#f3f7fa', 0.35), bevel=0.3)
    for dx in (-0.35, 0.25):                                  # portholes in the tower
        cyl((cx - 0.35 + dx, cy - 0.48, cz + R + 0.3), 0.17, 0.06, M('#7ed6ff', 0.1, emit=hexrgb('#bfeeff'), emit_strength=1.2), rot=(90, 0, 0))
    cyl((cx - 0.75, cy, cz + R + 1.05), 0.06, 0.8, M('#9fb3c2', 0.4, metal=0.5))   # periscope
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.86, location=(cx + L - 0.55, cy, cz))
    dome = bpy.context.object; dome.data.materials.append(M('#bfeeff', 0.05, emit=hexrgb('#dff7ff'), emit_strength=0.5)); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0.18, depth=0.7, location=(cx - L - 0.15, cy, cz), rotation=(0, math.radians(-90), 0))
    bpy.context.object.data.materials.append(M('#f3f7fa', 0.35))
    for k in range(3):                                       # the propeller
        a = math.radians(30 + 120 * k)
        box((cx - L - 0.55, cy + 0.35 * math.cos(a), cz + 0.35 * math.sin(a)), (0.06, 0.18, 0.62), M('#0b2540', 0.4), rot=(math.degrees(a) - 90, 0, 0), bevel=0.02)
    for sy in (-1, 1):                                       # skids it rests on
        box((cx, cy + sy * 0.7, 0.12), (L * 1.3, 0.14, 0.14), M('#9fb3c2', 0.5, metal=0.4), bevel=0.05)
        for dx in (-1.2, 1.2):
            box((cx + dx, cy + sy * 0.6, 0.3), (0.1, 0.1, 0.45), M('#9fb3c2', 0.5, metal=0.4), bevel=0.02)
    return {}


def _sub_stripe(nt, co):
    """A navy band along the hull, low down (object z between -0.62 and -0.42)."""
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(co, sep.inputs[0])
    lo = nt.nodes.new('ShaderNodeMath'); lo.operation = 'GREATER_THAN'; lo.inputs[1].default_value = -0.66; nt.links.new(sep.outputs['Z'], lo.inputs[0])
    hi = nt.nodes.new('ShaderNodeMath'); hi.operation = 'LESS_THAN'; hi.inputs[1].default_value = -0.46; nt.links.new(sep.outputs['Z'], hi.inputs[0])
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; nt.links.new(lo.outputs[0], mm.inputs[0]); nt.links.new(hi.outputs[0], mm.inputs[1])
    return mm.outputs[0]


def _glass():
    g = M('#e9f6ff', 0.02, coat=1.0); b = g.node_tree.nodes['Principled BSDF']
    b.inputs['Alpha'].default_value = 0.14; g.surface_render_method = 'BLENDED'; g.use_backface_culling = False
    return g


def fish(c, colour='#ff7b2e'):
    """A small round fish (body, tail, a white band, an eye), its middle at the root."""
    root = empty('Fish', c); x, y, z = c; parts = []
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=c); b = bpy.context.object; b.scale = (0.2, 0.09, 0.15)
    b.data.materials.append(M(colour, 0.35)); bpy.ops.object.shade_smooth(); parts.append(b)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x + 0.02, y, z)); w = bpy.context.object; w.scale = (0.04, 0.095, 0.155)
    w.data.materials.append(M('#ffffff', 0.4)); parts.append(w)
    bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.0, depth=0.16, vertices=4, location=(x - 0.24, y, z), rotation=(0, math.radians(90), 0))
    t = bpy.context.object; t.scale = (1, 0.35, 1); t.data.materials.append(M(colour, 0.35)); parts.append(t)
    for sy in (-1, 1):
        parts.append(cyl((x + 0.12, y + sy * 0.08, z + 0.04), 0.03, 0.02, M('#0b1a2a', 0.2), rot=(90, 0, 0), verts=16))
    parent(parts, root)
    return root


def tank(X, Y, S, logo, t_end):
    """Left side (instead of the crates): a fish tank on a low cabinet, one fish swimming laps."""
    lx = X - SIDE_X - 0.2; w, d, h, base = 1.8, 1.1, 1.1, 0.48; cx, cy = lx + w / 2, Y + LANE + 0.1
    cab = box((cx, cy, base / 2), (w + 0.1, d + 0.1, base), M('#2a4d6e', 0.5), bevel=0.04)
    gl = box((cx, cy, base + h / 2), (w, d, h), _glass(), bevel=0.02)
    wm = bpy.data.materials.new('TankWater'); wm.use_nodes = True; wb = wm.node_tree.nodes['Principled BSDF']
    wb.inputs['Base Color'].default_value = (*hexrgb('#8fdcf5'), 1); wb.inputs['Roughness'].default_value = 0.05
    wb.inputs['Alpha'].default_value = 0.3; wm.surface_render_method = 'BLENDED'
    water = box((cx, cy, base + h * 0.44), (w - 0.06, d - 0.06, h * 0.86), wm, bevel=0)
    rim = box((cx, cy, base + h + 0.03), (w + 0.06, d + 0.06, 0.07), M('#2a4d6e', 0.5), bevel=0.02)
    rnd = random.Random(3)
    for _ in range(14):                                     # pebbles and weed
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rnd.uniform(0.05, 0.09),
                                              location=(cx + rnd.uniform(-0.8, 0.8), cy + rnd.uniform(-0.45, 0.45), base + 0.05))
        bpy.context.object.data.materials.append(M(rnd.choice(['#f2e6cf', '#d9c8a8', '#b9a98c']), 0.8))
    for k in range(4):
        x0 = cx + (-0.6 + 0.4 * k); hh = rnd.uniform(0.45, 0.7)
        box((x0, cy + 0.3, base + hh / 2), (0.06, 0.04, hh), M('#3fb37f', 0.6), rot=(0, rnd.uniform(-8, 8), 0), bevel=0.02)
    f = fish((cx, cy, base + 0.6))
    dart = {}
    def path(t):
        """Laps around the tank; after a hit it darts to the far end and hides behind the weed for a moment."""
        a = 2 * math.pi * t / 3.2
        p = [cx + 0.55 * math.cos(a), cy - 0.12 + 0.2 * math.sin(a), base + 0.6 + 0.06 * math.sin(3 * a)]
        heading = math.degrees(a) + 90
        if 't' in dart and t >= dart['t']:
            u = min((t - dart['t']) / 0.25, 1.0); back = min(max((t - dart['t'] - 1.4) / 0.8, 0.0), 1.0)
            q = [cx + 0.7, cy + 0.22, base + 0.45]; k = (1 - (1 - u) ** 2) * (1 - back)
            p = [pp + (qq - pp) * k for pp, qq in zip(p, q)]; heading = heading * (1 - k)
        return p, heading
    def key_fish():
        for fr in range(1, round(t_end * FPS) + 2, 2):
            p, hd = path((fr - 1) / FPS); f.location = p; f.rotation_euler = (0, 0, math.radians(hd))
            f.keyframe_insert('location', frame=fr); f.keyframe_insert('rotation_euler', frame=fr)
    key_fish()
    contact = (cx - w / 2, Y + LANE)
    def react(t):
        dart['t'] = t; key_fish()
        for o in (gl, water, rim, cab):
            wobble(o, t, amps=(0.035, 0, 0), hz=10, decay=7, dur=0.6, path='location')
    return {'tank': dict(move='smack', dir=(1, 0), contact=contact, start='bg_left', react=react, impact=0.3,
                         spot=(contact[0] - (NOSE + REACH) * CAT, contact[1], 0, 90))}


def hose(X, Y, S, logo):
    """Back left: a dive cylinder standing in a rack, its air hose snaking across the floor to a mask."""
    lx = X - SIDE_X - 0.6; tx, ty = lx + 1.0, Y + LANE + 1.6
    cylm = printed('#e3ecf1', 0.3, [dict(img='cylinder.png', n=(0, -1, 0), right=(1, 0, 0), up=(0, 0, 1),
                                                                    c=(0, 0, 0.05), w=0.2)] if logo else [], name='DiveCylinder', metal=0.4)
    c = cyl((tx, ty, 0.95), 0.3, 1.7, cylm, verts=48)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(tx, ty, 1.8)); top = bpy.context.object
    top.scale = (1, 1, 0.55); top.data.materials.append(cylm); bpy.ops.object.shade_smooth()
    cyl((tx, ty, 2.02), 0.07, 0.18, M('#c9ced6', 0.3, metal=0.8))
    box((tx, ty, 0.5), (0.8, 0.8, 0.08), M('#2a4d6e', 0.5), bevel=0.02)
    box((tx, ty + 0.34, 0.9), (0.8, 0.06, 1.2), M('#2a4d6e', 0.5), bevel=0.02)
    xh = lx + 1.55                                          # where the hose crosses Ginger's lane
    pts = [(tx, ty - 0.08, 2.05), (tx + 0.3, ty - 0.3, 1.6), (tx + 0.45, ty - 0.55, 0.06), (xh - 0.05, Y + LANE + 0.6, 0.06),
           (xh, Y + LANE, 0.06), (xh + 0.15, Y + LANE - 0.6, 0.06), (xh + 0.7, Y + LANE - 0.95, 0.06)]
    cu = bpy.data.curves.new('Hose', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.055; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    h = bpy.data.objects.new('Hose', cu); bpy.context.collection.objects.link(h); cu.materials.append(M('#1d2b3a', 0.55))
    mx, my = xh + 0.85, Y + LANE - 1.1                        # the mask at the hose's end
    box((mx, my, 0.12), (0.5, 0.36, 0.16), M('#1d2b3a', 0.5), bevel=0.06)
    box((mx, my - 0.17, 0.14), (0.4, 0.04, 0.12), M('#bfeeff', 0.05, emit=hexrgb('#dff7ff'), emit_strength=0.3), bevel=0.02)
    contact = (xh, Y + LANE)
    def react(t):
        wobble(h, t, amps=(0, 0, 0.07), hz=6, decay=6, dur=0.7, path='location')
    return {'hose': dict(move='trip', dir=(1, 0), contact=contact, start='bg_left', react=react,
                         spot=(contact[0] - PAW * CAT, contact[1], 0, 90))}


def floor_paint(X, Y, S):
    """The older idea, now worn floor paint instead of a glossy sticker: 'SUBSCRIBE @RODIOCEAN' behind the cast."""
    path = os.path.join(PRINTS, 'floor_paint.png')
    if not os.path.exists(path):
        return
    w = min(S['w'] * 0.85, 8.5)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(X, Y + 1.9, 0.012)); p = bpy.context.object; p.name = 'FloorPaint'
    p.scale = (w, w * 0.2, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m = printed('#dff1f9', 0.55, [dict(img='floor_paint.png', n=(0, 0, 1), right=(1, 0, 0), up=(0, 1, 0), c=(0, 0, 0), w=w,
                                       ink='#0b2540', alpha=0.75)], name='FloorPaint')
    nt = m.node_tree; b = nt.nodes['Principled BSDF']                 # only the paint shows; the rest lets the floor through
    tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 0.75
    nt.links.new(tex.outputs['Alpha'], k.inputs[0]); nt.links.new(k.outputs[0], b.inputs['Alpha'])
    p.data.materials.append(m)


CARRIERS = ('crates', 'buoy', 'sub', 'hose')     # the things that can carry the name


def pick_carrier(pieces, seed):
    """ONE thing carries the name in a Short (owner, 10 Nov 2026: 'One per Short', like the format benchmark's name hidden somewhere
    different in each footage). Without a 'logo:' line the scene's own name picks it, so each episode gets a different one."""
    can = [p for p in pieces if p in CARRIERS]
    return {can[seed % len(can)]} if can else set()


def dress(X, Y, S, tall, pieces=('crates', 'buoy', 'sub'), logo=None, t_end=20.0, seed=0):
    logo = pick_carrier(pieces, seed) if logo is None else set(logo)
    print('LAB NAME ON:', ', '.join(sorted(logo)) or 'nothing')
    bumps = {}
    for piece in pieces:
        if piece == 'crates':
            bumps.update(crates(X, Y, S, 'crates' in logo))
        elif piece == 'buoy':
            bumps.update(buoy(X, Y, S, 'buoy' in logo))
        elif piece == 'sub':
            sub(X, Y, S, tall, 'sub' in logo)
        elif piece == 'tank':
            bumps.update(tank(X, Y, S, 'tank' in logo, t_end))
        elif piece == 'hose':
            bumps.update(hose(X, Y, S, 'hose' in logo))
    if 'floor' in logo:
        floor_paint(X, Y, S)
    return bumps
