"""Place bank for the blocky world: a street and five rooms built from short recipes, plus three lighting presets.
place('street', at=(x, y)) / place('classroom') ... returns {'spots': {name: (x, y, z, turn)}, 'cams': {name: (cam, look)}}:
spots are where characters stand or sit (turn = the way they face), cams are ready framings for step 4's camera bank.
light('day' | 'golden' | 'night' | 'indoor_day' | 'indoor_night') sets sky, sun, fill, glowing windows and lamp lights.
Scale: a person is 2.85 units tall (1 unit is about 0.63 m); doors 3.4, rooms 5 high, seats 0.75, desks 1.2.
Places: street, classroom, bedroom, kitchen, office, shop, lab (the underwater lab), void.
The void (12 Nov 2026): place('void', color='#9ad8f5') is an endless floor and backdrop in ONE flat colour, centred on 0 0
(so it cannot share a scene with the street), with its own soft even light and only soft shadows under things (light() swaps
the preset's sun and sky for it; write 'light: day'). Spots: left, centre, right, far_left, far_right (a front row, 1.35 apart,
each step outward 0.6 further back so neighbours' arms never cross), back_left, back_mid, back_right (a back row 3 behind left,
centre and right: someone there is hidden by a person on the spot in front). Made to be the only place of a scene."""
import math, os, random
import bpy, bmesh
from common import hexrgb, world
from sf_world import box, cyl, empty, parent, text
from blocky_kit import M

GLASS = None                                   # shared window material: light() makes it sky-blue by day, warm and glowing at night
LAMPS = []                                     # lamp-head positions for the night preset
ROOMS = []                                     # (centre, size) of each room, for the indoor presets
CEILS = []                                     # every room's ceiling, hidden while the camera looks down from above ('top')
VOID = None                                    # set by void(): its colour and floor; light() then lights it its own way
BUILT = []                                     # names of the places built so far


def _glass():
    global GLASS
    if GLASS is None:
        GLASS = M('#9fd8ff', 0.08, emit=hexrgb('#cfeaff'), emit_strength=0.4)
    return GLASS


def prism(base, w, d, h, m, along='x'):
    """Gable roof: a triangular prism sitting on base (centre of the wall top), ridge along x (or y)."""
    x, y, z = base
    me = bpy.data.meshes.new('Roof'); bm = bmesh.new()
    if along == 'x':
        v = [bm.verts.new((x + sx * w / 2, y + py, z + pz)) for sx in (-1, 1) for py, pz in ((-d / 2, 0), (d / 2, 0), (0, h))]
    else:
        v = [bm.verts.new((x + px, y + sy * d / 2, z + pz)) for sy in (-1, 1) for px, pz in ((w / 2, 0), (-w / 2, 0), (0, h))]
    for f in ((v[0], v[1], v[2]), (v[3], v[5], v[4]), (v[0], v[3], v[4], v[1]), (v[1], v[4], v[5], v[2]), (v[2], v[5], v[3], v[0])):
        bm.faces.new(f)
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('Roof', me); bpy.context.collection.objects.link(o); me.materials.append(m)
    o.modifiers.new('bev', 'BEVEL').width = 0.06
    return o


def window(c, w, h, frame='#ffffff', normal='y'):
    """A framed window on a wall facing -y (normal='y') or -x/+x (normal='x' / '-x'): glass plus a cross frame."""
    x, y, z = c; fm = M(frame, 0.5)
    if normal == 'y':
        return [box((x, y, z), (w, 0.1, h), _glass(), bevel=0.02), box((x, y - 0.04, z), (w + 0.2, 0.06, 0.12), fm, bevel=0.01),
                box((x, y - 0.04, z), (0.12, 0.06, h + 0.2), fm, bevel=0.01), box((x, y - 0.03, z - h / 2 - 0.08), (w + 0.4, 0.2, 0.12), fm, bevel=0.02)]
    s = 1 if normal == 'x' else -1
    return [box((x, y, z), (0.1, w, h), _glass(), bevel=0.02), box((x + s * 0.04, y, z), (0.06, w + 0.2, 0.12), fm, bevel=0.01),
            box((x + s * 0.04, y, z), (0.06, 0.12, h + 0.2), fm, bevel=0.01)]


def door(c, color='#7a4a2a', w=1.7, h=3.4):
    x, y, z = c
    return [box((x, y, z + h / 2), (w, 0.12, h), M(color, 0.6), bevel=0.04), cyl((x + w * 0.32, y - 0.1, z + h * 0.48), 0.07, 0.06, M('#f2c230', 0.3, metal=0.6), rot=(90, 0, 0))]


# ---------------------------------------------------------------- street pieces (fronts face -y, toward the street)
HOUSE_COLOURS = [('#f4e3c8', '#d6453d'), ('#bfe1ff', '#3d6fd6'), ('#ffd0d6', '#7a4bd1'), ('#d8f0c8', '#e0832f'), ('#fff1a8', '#2f9e7a')]


def house(kind, c, wall=None, roof=None):
    """kind 0 cottage, 1 two-storey flat roof, 2 wide bungalow, 3 narrow tall, 4 porch house. c = centre of the front at the ground."""
    x, y, z = c; wall = wall or HOUSE_COLOURS[kind % 5][0]; roof = roof or HOUSE_COLOURS[kind % 5][1]
    W, D, H = [(9, 7, 6.2), (8, 7, 9.4), (12, 7, 5.4), (5.6, 6, 10.5), (9, 7, 6.6)][kind]
    yc = y + D / 2; wm, rm = M(wall, 0.85), M(roof, 0.6)
    box((x, yc, z + H / 2), (W, D, H), wm, bevel=0.08)
    if kind == 1:
        box((x, yc, z + H + 0.25), (W + 0.3, D + 0.3, 0.5), rm, bevel=0.05)
        for wx in (-2.2, 2.2):
            window((x + wx, y - 0.05, z + 6.6), 1.9, 1.7)
        window((x + 2.2, y - 0.05, z + 2.4), 1.9, 1.7); door((x - 2.2, y - 0.06, z))
    elif kind == 3:
        prism((x, yc, z + H), W + 0.8, D + 0.8, 4.2, rm)
        window((x, y - 0.05, z + 7.4), 1.6, 1.6); window((x + 1.3, y - 0.05, z + 4.6), 1.2, 1.4); door((x - 1.2, y - 0.06, z), w=1.5)
    elif kind == 2:
        prism((x, yc, z + H), W + 0.8, D + 0.8, 2.2, rm)
        for wx in (-3.6, 3.6):
            window((x + wx, y - 0.05, z + 2.6), 2.4, 1.6)
        door((x, y - 0.06, z))
    else:
        prism((x, yc, z + H), W + 0.8, D + 0.8, 3.0, rm)
        window((x + 1.9, y - 0.05, z + H * 0.58), 2.2, 1.7); door((x - 2.0, y - 0.06, z))
        if kind == 4:                                 # porch: a little roof on two posts
            box((x - 2.0, y - 1.3, z + 3.9), (3.4, 2.8, 0.25), rm, bevel=0.04)
            for px in (-3.4, -0.6):
                box((x + px, y - 2.5, z + 1.95), (0.25, 0.25, 3.9), M('#ffffff', 0.5), bevel=0.03)
    return W


def shop(c, sign='SHOP', colour='#ff5a5f', wall='#fff7ec'):
    x, y, z = c; W, D, H = 10, 7, 6.0
    box((x, y + D / 2, z + H / 2), (W, D, H), M(wall, 0.85), bevel=0.08)
    box((x, y + D / 2, z + H + 0.2), (W + 0.3, D + 0.3, 0.4), M('#5b6474', 0.6), bevel=0.05)
    box((x + 1.6, y - 0.05, z + 2.2), (5.0, 0.1, 2.6), _glass(), bevel=0.02); door((x - 3.2, y - 0.06, z), '#3a4a5c')
    for i in range(10):                               # striped awning
        box((x - 4.5 + i + 0.5, y - 0.9, z + 4.1), (1.0, 1.8, 0.14), M(colour if i % 2 == 0 else '#ffffff', 0.6), rot=(-14, 0, 0), bevel=0.01)
    box((x, y - 0.12, z + 5.15), (6.0, 0.14, 1.0), M(colour, 0.5), bevel=0.04)
    text(sign, (x, y - 0.22, z + 5.15), 0.75, M('#ffffff', 0.4), extrude=0.04)
    return W


def school(c, sign='SCHOOL'):
    x, y, z = c; W, D, H = 18, 8, 9.4; brick = M('#d9775b', 0.85); trim = M('#fff4e2', 0.6)
    box((x, y + D / 2, z + H / 2), (W, D, H), brick, bevel=0.08)
    box((x, y + D / 2, z + H + 0.25), (W + 0.4, D + 0.4, 0.5), trim, bevel=0.05)
    prism((x, y + 0.8, z + H), 6.4, 2.4, 2.4, M('#7d3b2f', 0.6), along='y')
    for wx in (-6.5, -3.8, 3.8, 6.5):
        for wz in (2.6, 6.6):
            window((x + wx, y - 0.05, z + wz), 1.9, 1.8)
    door((x - 0.9, y - 0.06, z), '#2d4a7a', w=1.8); door((x + 0.9, y - 0.06, z), '#2d4a7a', w=1.8)
    box((x, y - 0.12, z + 5.0), (7.0, 0.14, 1.1), trim, bevel=0.04)
    text(sign, (x, y - 0.22, z + 5.0), 0.8, M('#2d4a7a', 0.4), extrude=0.04)
    cyl((x, y - 0.05, z + 10.6), 0.75, 0.15, trim, rot=(90, 0, 0)); cyl((x, y - 0.14, z + 10.6), 0.62, 0.05, M('#ffffff', 0.3), rot=(90, 0, 0))
    box((x + 0.18, y - 0.18, z + 10.7), (0.36, 0.04, 0.07), M('#20222c'), bevel=0.01); box((x, y - 0.18, z + 10.8), (0.06, 0.04, 0.42), M('#20222c'), bevel=0.01)
    return W


def tree(c, kind='round', leaf='#56b84a'):
    x, y, z = c
    box((x, y, z + 1.5), (0.7, 0.7, 3.0), M('#8b5a34', 0.8), bevel=0.05)
    if kind == 'pine':
        for k, (s, h) in enumerate(((3.4, 2.0), (2.5, 1.8), (1.5, 1.6))):
            box((x, y, z + 3.4 + k * 1.5), (s, s, h), M('#2f8f4e', 0.8), bevel=0.12)
    else:
        box((x, y, z + 3.9), (3.2, 3.2, 2.6), M(leaf, 0.8), bevel=0.15); box((x, y, z + 5.5), (2.1, 2.1, 1.5), M(leaf, 0.8), bevel=0.12)


def lamp(c):
    x, y, z = c; pole = M('#2d3340', 0.4, metal=0.5)
    cyl((x, y, z + 2.6), 0.09, 5.2, pole); box((x, y - 0.45, z + 5.2), (0.12, 1.0, 0.12), pole, bevel=0.02)
    box((x, y - 0.9, z + 5.0), (0.55, 0.55, 0.35), M('#fff2c8', 0.3, emit=hexrgb('#ffd88a'), emit_strength=0.0), bevel=0.05)
    LAMPS.append((x, y - 0.9, z + 4.75))


def bench(c, turn=0):
    x, y, z = c; wood, iron = M('#b5763d', 0.7), M('#2d3340', 0.5)
    parts = [box((x, y, z + 0.75), (2.4, 0.8, 0.12), wood, bevel=0.02), box((x, y + 0.42, z + 1.3), (2.4, 0.1, 0.7), wood, bevel=0.02)]
    for sx in (-1, 1):
        parts.append(box((x + sx * 1.0, y, z + 0.37), (0.12, 0.7, 0.75), iron, bevel=0.01))
    if turn:
        piv = empty('Bench', (x, y, z))
        for o in parts:
            o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
        piv.rotation_euler = (0, 0, math.radians(turn))


def car(c, colour='#e63946', turn=0):
    x, y, z = c; body = M(colour, 0.25, coat=1.0); tyre = M('#1b1d24', 0.8); piv = empty('Car', (x, y, z))
    parts = [box((x, y, z + 0.95), (4.4, 2.0, 0.9), body, bevel=0.15), box((x - 0.2, y, z + 1.75), (2.4, 1.8, 0.8), body, bevel=0.15),
             box((x - 0.2, y, z + 1.78), (2.45, 1.7, 0.6), _glass(), bevel=0.1)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(cyl((x + sx * 1.4, y + sy * 0.95, z + 0.5), 0.5, 0.35, tyre, rot=(90, 0, 0)))
        parts.append(box((x + 2.2 * sx, y + 0.0, z + 1.0), (0.06, 1.6, 0.25), M('#fff7d6' if sx > 0 else '#ff4a4a', 0.3), bevel=0.02))
    for o in parts:
        o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
    piv.rotation_euler = (0, 0, math.radians(turn))


def street(at=(0, 0)):
    """Near pavement where people walk (y -3..4.5), a road, a far pavement, and a row of buildings (fronts at y=12)."""
    X, Y = at; G = 0.0
    bpy.ops.mesh.primitive_plane_add(size=400, location=(X, Y, 0)); g = bpy.context.object; g.name = 'Floor'; g.data.materials.append(M('#79c95a', 0.95))
    box((X, Y + 0.75, 0.03), (160, 7.5, 0.06), M('#d9dde3', 0.9), bevel=0)
    box((X, Y + 4.65, 0.1), (160, 0.3, 0.2), M('#f3f5f8', 0.8), bevel=0.02)
    box((X, Y + 7.2, 0.02), (160, 4.8, 0.04), M('#7f8898', 0.9), bevel=0)
    for k in range(-20, 21):
        box((X + k * 4.0, Y + 7.2, 0.045), (2.0, 0.18, 0.01), M('#ffffff', 0.6), bevel=0)
    box((X, Y + 9.75, 0.1), (160, 0.3, 0.2), M('#f3f5f8', 0.8), bevel=0.02); box((X, Y + 10.8, 0.03), (160, 2.2, 0.06), M('#d9dde3', 0.9), bevel=0)
    xs = X - 46.0; doors = {}
    for kind in (0, 1, 'shop', 4, 2, 'school', 3, 0, 1):
        w = {'shop': 10, 'school': 18}.get(kind) or [9, 8, 12, 5.6, 9][kind]
        cx = xs + w / 2
        if kind == 'shop':
            shop((cx, Y + 12.0, G)); doors.setdefault('shop', (cx - 3.2, Y + 12.0 - 0.06))
        elif kind == 'school':
            school((cx, Y + 12.0, G)); doors.setdefault('school', (cx, Y + 12.0 - 0.06))
        else:
            house(kind, (cx, Y + 12.0, G))
            if kind == 2:
                doors.setdefault('house', (cx, Y + 12.0 - 0.06))
        xs += w + 2.6
        tree((xs - 1.3, Y + 13.5, G), 'pine' if int(xs) % 3 == 0 else 'round', '#56b84a' if int(xs) % 2 else '#3fa34d')
    for k in range(-4, 5):
        lamp((X + k * 9.0 + 2.0, Y + 4.1, 0.06))
    bench((X - 4.6, Y + 3.5, 0.06)); bench((X + 9.4, Y + 3.5, 0.06))
    car((X - 9.0, Y + 6.0, 0.04), '#e63946'); car((X + 14.0, Y + 6.0, 0.04), '#2f7cf6'); car((X + 3.5, Y + 8.4, 0.04), '#ffcc33', turn=180)
    return {'spots': {'centre': (X, Y, 0.06, 0), 'left': (X - 1.35, Y + 0.3, 0.06, 0), 'right': (X + 1.35, Y + 0.3, 0.06, 0),
                      'bench': (X - 4.6, Y + 3.3, 0.06, 0), 'shop_door': (X - 18.8, Y + 10.6, 0.06, 0)},
            'cams': {'wide': ((X, Y - 9.0, 2.4), (X, Y + 2, 1.6)), 'two_shot': ((X, Y - 5.4, 1.8), (X, Y + 0.6, 1.55))},
            'doors': doors}                       # (x, y) of each front door's centre plane; doors face -y


# ---------------------------------------------------------------- portal doors (the camera's way from the street into a room)
# A room is entered through the street door of its building: the camera flies into that door until it fills the picture,
# then continues from an identical door standing in front of the room, which swings open (the 'portal'). Same door, same
# distance, so the jump is invisible. Leaves: (offset along the door, colour, width).
DOOR_STYLES = {'school': dict(leaves=[(-0.9, '#2d4a7a', 1.8), (0.9, '#2d4a7a', 1.8)], wall='#d9775b'),
               'shop': dict(leaves=[(0.0, '#3a4a5c', 1.7)], wall='#fff7ec'),
               'house': dict(leaves=[(0.0, '#7a4a2a', 1.7)], wall=HOUSE_COLOURS[2][0])}
ROOM_DOOR = dict(classroom='school', shop='shop', bedroom='house', kitchen='house', office='house')


def portal(style, at, heading):
    """A wall with the street door of `style` in it, its centre plane at `at` (x, y), the outside facing -y turned by heading (deg).
    Returns (root, hinges, meshes): hinges swing the leaves inward (+angle opens), meshes are hidden when not in use."""
    S = DOOR_STYLES[style]; root = empty('Portal'); hinges, meshes = [], []
    half = sum(w for _, _, w in S['leaves']) / 2; wm = M(S['wall'], 0.85)
    for c, size in (((-half - 4.0, 0.26, 3.5), (8.0, 0.4, 7.0)), ((half + 4.0, 0.26, 3.5), (8.0, 0.4, 7.0)), ((0, 0.26, 5.2), (2 * half, 0.4, 3.6))):
        meshes.append(box(c, size, wm, bevel=0))
    for k, (dx, col, w) in enumerate(S['leaves']):
        side = -1 if k == 0 else 1                     # first leaf hinged on its left edge, second on its right
        h = empty('Hinge', (dx + side * w / 2, 0, 0)); leaf = door((dx, 0, 0), col, w=w)
        parent(leaf, h); parent([h], root); hinges.append((h, -side)); meshes += leaf
    parent(meshes[:3], root)
    root.location = (at[0], at[1], 0); root.rotation_euler = (0, 0, math.radians(heading))
    return root, hinges, meshes


# ---------------------------------------------------------------- rooms (open toward -y, where the camera stands)
def room_shell(at, w=12.0, d=9.0, h=5.0, wall='#f3ead8', floor='#c9a26b', win_side='x-'):
    X, Y = at; wm = M(wall, 0.9)
    box((X, Y, -0.035), (w + 0.4, d + 0.4, 0.1), M(floor, 0.75), bevel=0)   # top 1.5 cm above any outdoor ground
    box((X, Y - d / 2 - 7.0, -0.04), (w + 16, 14.0, 0.1), M(floor, 0.75), bevel=0)   # floor in front, so no grass shows at the edges
    for k in range(-int(w // 2), int(w // 2) + 1):    # floor boards
        box((X + k * 1.0, Y, 0.017), (0.02, d, 0.004), M('#a8834f', 0.8), bevel=0)
    box((X, Y + d / 2 + 0.1, h / 2), (w + 0.4, 0.2, h), wm, bevel=0)
    box((X - w / 2 - 0.1, Y, h / 2), (0.2, d + 0.4, h), wm, bevel=0); box((X + w / 2 + 0.1, Y, h / 2), (0.2, d + 0.4, h), wm, bevel=0)
    ceil = box((X, Y, h + 0.1), (w + 0.4, d + 0.4, 0.2), M('#ffffff', 0.9), bevel=0); ceil.name = 'Ceiling'; CEILS.append(ceil)
    box((X, Y + d / 2 - 0.02, 0.2), (w, 0.08, 0.4), M('#ffffff', 0.6), bevel=0.01)   # skirting
    sx = -1 if win_side == 'x-' else 1
    window((X + sx * (w / 2 - 0.02), Y + 0.5, 2.8), 2.6, 2.2, normal='x' if sx < 0 else '-x')
    ROOMS.append(((X, Y), (w, d, h)))
    return X, Y, w, d, h


def classroom(at=(200, 0)):
    X, Y, w, d, h = room_shell(at, wall='#eef3e2')
    wood, dark = M('#b5763d', 0.7), M('#3a3f4c', 0.6)
    box((X, Y + d / 2 - 0.12, 2.9), (6.2, 0.1, 2.4), M('#2f5d4a', 0.85), bevel=0.02); box((X, Y + d / 2 - 0.03, 2.9), (6.5, 0.06, 2.7), wood, bevel=0.02)
    box((X, Y + d / 2 - 0.25, 1.68), (5.8, 0.3, 0.08), wood, bevel=0.01)
    for i, cx in enumerate((-2.0, -0.2, 1.6)):       # chalk doodles: arrow, plus, a rising line
        box((X + cx, Y + d / 2 - 0.18, 3.0 + 0.3 * i), (1.0, 0.02, 0.07), M('#ffffff', 0.9), rot=(0, -20 * i, 0), bevel=0)
    cyl((X + 4.2, Y + d / 2 - 0.05, 3.9), 0.45, 0.1, M('#ffffff', 0.4), rot=(90, 0, 0))
    box((X - 3.4, Y + 2.6, 0.6), (2.6, 1.3, 1.2), wood, bevel=0.04)
    spots = {'teacher': (X - 1.2, Y + 3.0, 0, 180 + 180)}
    for r, ry in enumerate((-0.4, -2.6)):
        for cx in (-2.6, 0.0, 2.6):
            box((X + cx, Y + ry, 1.18), (1.5, 0.95, 0.08), wood, bevel=0.02)
            for lx in (-0.65, 0.65):
                box((X + cx + lx, Y + ry, 0.58), (0.08, 0.8, 1.16), dark, bevel=0.01)
            box((X + cx, Y + ry - 1.05, 0.7), (0.95, 0.9, 0.1), M('#ff8a3d' if r else '#2f7cf6', 0.6), bevel=0.02)
            box((X + cx, Y + ry - 1.5, 1.2), (0.95, 0.08, 0.9), M('#ff8a3d' if r else '#2f7cf6', 0.6), bevel=0.02)
            for lx in (-0.4, 0.4):
                box((X + cx + lx, Y + ry - 1.05, 0.34), (0.07, 0.07, 0.68), dark, bevel=0.01)
            spots[f'seat_{r}_{int(cx)}'] = (X + cx, Y + ry - 1.15, 0, 180)
    spots['teacher'] = (X - 1.2, Y + 3.0, 0, 0)
    return {'spots': spots, 'cams': {'from_door': ((X + 1.6, Y - d / 2 - 3.4, 4.3), (X - 0.4, Y + 1.2, 1.5))}, 'seat': 0.75}


def bedroom(at=(240, 0)):
    X, Y, w, d, h = room_shell(at, wall='#dfe9ff', floor='#c9a26b', win_side='x+')
    wood = M('#9a6a3c', 0.7)
    box((X - 3.2, Y + 2.2, 0.35), (3.0, 4.6, 0.7), wood, bevel=0.05); box((X - 3.2, Y + 2.2, 0.85), (2.8, 4.4, 0.35), M('#ffffff', 0.8), bevel=0.1)
    box((X - 3.2, Y + 1.4, 1.08), (2.9, 2.9, 0.16), M('#ff8a3d', 0.85), bevel=0.06); box((X - 3.2, Y + 3.8, 1.15), (2.0, 0.8, 0.3), M('#ffffff', 0.8), bevel=0.12)
    box((X - 3.2, Y + 4.45, 1.5), (3.0, 0.2, 2.0), wood, bevel=0.05)
    box((X - 0.9, Y + 3.9, 0.6), (1.0, 1.0, 1.2), wood, bevel=0.04); cyl((X - 0.9, Y + 3.9, 1.5), 0.25, 0.6, M('#ffd23a', 0.5))
    box((X + 4.2, Y + 3.6, 2.1), (2.6, 1.4, 4.2), M('#7aa6d6', 0.7), bevel=0.06); box((X + 4.2, Y + 2.88, 2.1), (0.05, 0.05, 3.8), M('#ffffff', 0.4), bevel=0)
    cyl((X + 0.6, Y + 0.6, 0.02), 2.4, 0.04, M('#ff6f91', 0.9), verts=64)
    box((X + 0.8, Y + d / 2 - 0.02, 3.2), (2.0, 0.06, 1.4), M('#2f7cf6', 0.6), bevel=0.02); box((X + 0.8, Y + d / 2 - 0.06, 3.2), (1.6, 0.04, 1.0), M('#ffcc33', 0.6), bevel=0.01)
    return {'spots': {'bed_edge': (X - 2.7, Y + 1.0, 0, 90), 'middle': (X + 0.8, Y + 0.4, 0, 0)},
            'cams': {'from_door': ((X + 0.8, Y - d / 2 - 3.0, 4.0), (X - 1.0, Y + 1.6, 1.4))}, 'seat': 1.0}


def kitchen(at=(280, 0), chairs=True, bowl=True):
    """chairs / bowl = False leave the table bare (a clear view of the table from the front)."""
    X, Y, w, d, h = room_shell(at, wall='#fff1d6', floor='#e9e2d6')
    cab, top = M('#2f9e7a', 0.6), M('#f3f5f8', 0.3)
    box((X - 1.0, Y + d / 2 - 0.75, 0.72), (8.0, 1.4, 1.45), cab, bevel=0.04); box((X - 1.0, Y + d / 2 - 0.75, 1.5), (8.2, 1.5, 0.1), top, bevel=0.02)
    box((X - 1.0, Y + d / 2 - 0.4, 3.6), (8.0, 0.8, 1.4), cab, bevel=0.04)
    for k in range(4):
        box((X - 4.0 + k * 2.0, Y + d / 2 - 1.47, 0.95), (0.6, 0.04, 0.08), M('#f2c230', 0.3, metal=0.6), bevel=0.01)
    box((X + 1.2, Y + d / 2 - 0.75, 1.57), (1.8, 1.0, 0.05), M('#1b1d24', 0.4), bevel=0.01)
    for sx in (-0.45, 0.45):
        cyl((X + 1.2 + sx, Y + d / 2 - 0.75, 1.61), 0.3, 0.02, M('#3a3f4c', 0.5))
    box((X + 4.6, Y + d / 2 - 0.85, 1.8), (1.7, 1.5, 3.6), M('#f3f5f8', 0.3), bevel=0.08); box((X + 4.0, Y + d / 2 - 1.62, 2.4), (0.08, 0.06, 1.2), M('#9aa3b2', 0.3, metal=0.6), bevel=0.01)
    box((X - 0.6, Y + 0.2, 1.15), (3.2, 2.0, 0.12), M('#b5763d', 0.6), bevel=0.03)
    for sx, sy in ((-1.3, -0.8), (1.3, -0.8), (-1.3, 0.8), (1.3, 0.8)):
        box((X - 0.6 + sx, Y + 0.2 + sy, 0.55), (0.12, 0.12, 1.1), M('#8b5a34', 0.7), bevel=0.01)
    for cx in ((-1.4, 0.2) if chairs else ()):
        box((X - 0.6 + cx, Y - 1.35, 0.7), (0.9, 0.9, 0.1), M('#ff5a5f', 0.6), bevel=0.02); box((X - 0.6 + cx, Y - 1.78, 1.2), (0.9, 0.08, 0.9), M('#ff5a5f', 0.6), bevel=0.02)
    if bowl:
        cyl((X - 0.6, Y + 0.2, 1.4), 0.35, 0.3, M('#ffffff', 0.3)); cyl((X - 0.6, Y + 0.2, 1.58), 0.3, 0.1, M('#ff8a3d', 0.6))
    return {'spots': {'stove': (X + 1.2, Y + d / 2 - 2.0, 0, 180), 'table_seat': (X - 2.0, Y - 1.45, 0, 180), 'fridge': (X + 3.0, Y + 1.2, 0, -30)},
            'cams': {'from_door': ((X + 0.4, Y - d / 2 - 3.4, 4.0), (X + 0.4, Y + 1.2, 1.6))}, 'seat': 0.75}


def office(at=(320, 0)):
    X, Y, w, d, h = room_shell(at, wall='#e7ebf2', floor='#7f8898', win_side='x+')
    desk = M('#f3f5f8', 0.4)                          # the boss sits behind the desk, facing the camera
    box((X, Y + 1.6, 1.18), (3.6, 1.7, 0.1), desk, bevel=0.03)
    for sx in (-1.6, 1.6):
        box((X + sx, Y + 1.6, 0.58), (0.12, 1.5, 1.16), M('#3a3f4c', 0.5), bevel=0.01)
    box((X + 1.3, Y + 1.15, 1.9), (1.4, 0.1, 0.9), M('#1b1d24', 0.3), bevel=0.03); box((X + 1.3, Y + 1.21, 1.9), (1.25, 0.02, 0.75), M('#2f7cf6', 0.3, emit=hexrgb('#5ab0ff'), emit_strength=1.2), bevel=0)
    box((X + 1.3, Y + 1.1, 1.35), (0.12, 0.12, 0.35), M('#3a3f4c', 0.4), bevel=0.01); box((X + 0.4, Y + 1.95, 1.25), (1.2, 0.4, 0.04), M('#3a3f4c', 0.5), bevel=0.01)
    cyl((X - 0.4, Y + 2.8, 0.75), 0.5, 0.12, M('#1b1d24', 0.5)); box((X - 0.4, Y + 3.3, 1.5), (0.95, 0.12, 1.3), M('#1b1d24', 0.5), bevel=0.05); cyl((X - 0.4, Y + 2.8, 0.35), 0.06, 0.7, M('#9aa3b2', 0.3))
    box((X - 4.0, Y + d / 2 - 0.45, 2.2), (3.2, 0.8, 4.4), M('#9a6a3c', 0.7), bevel=0.04)
    for shelf in range(4):
        z = 0.6 + shelf * 1.05
        for k in range(7):
            box((X - 5.3 + k * 0.4, Y + d / 2 - 0.55, z + 0.38), (0.3, 0.6, 0.75 - 0.08 * (k % 3)), M(['#e63946', '#2f7cf6', '#ffcc33', '#2f9e7a'][(k + shelf) % 4], 0.6), bevel=0.02)
    cyl((X + 4.5, Y + 3.4, 0.5), 0.5, 1.0, M('#ffffff', 0.4)); box((X + 4.5, Y + 3.4, 1.6), (1.1, 1.1, 1.2), M('#3fa34d', 0.8), bevel=0.2)
    return {'spots': {'desk_chair': (X - 0.4, Y + 2.75, 0, 0), 'standing': (X + 2.4, Y + 0.2, 0, -30)},
            'cams': {'from_door': ((X + 0.8, Y - d / 2 - 3.2, 4.0), (X + 0.6, Y + 1.4, 1.6))}, 'seat': 0.8}


def shop_inside(at=(360, 0)):
    X, Y, w, d, h = room_shell(at, wall='#fff7ec', floor='#e9e2d6')
    box((X + 1.0, Y + 1.0, 0.7), (5.0, 1.3, 1.4), M('#ff5a5f', 0.6), bevel=0.04); box((X + 1.0, Y + 1.0, 1.45), (5.2, 1.4, 0.1), M('#f3f5f8', 0.3), bevel=0.02)
    box((X + 2.4, Y + 1.1, 1.75), (1.0, 0.8, 0.5), M('#3a3f4c', 0.4), bevel=0.05); box((X + 2.4, Y + 0.85, 2.15), (0.7, 0.08, 0.4), M('#2f9e7a', 0.3, emit=hexrgb('#4ad6a0'), emit_strength=1.0), bevel=0.02)
    for row in range(4):
        z = 0.8 + row * 1.0
        box((X, Y + d / 2 - 0.5, z - 0.08), (10.0, 0.9, 0.08), M('#9a6a3c', 0.7), bevel=0.01)
        for k in range(18):
            cl = ['#e63946', '#2f7cf6', '#ffcc33', '#2f9e7a', '#ff8a3d', '#7a4bd1'][(k * 7 + row * 3) % 6]
            box((X - 4.7 + k * 0.55, Y + d / 2 - 0.55, z + 0.3), (0.42, 0.55, 0.6 - 0.1 * ((k + row) % 3)), M(cl, 0.6), bevel=0.03)
    for cx, col in ((-3.8, '#ff8a3d'), (-2.2, '#e63946')):
        box((X + cx, Y - 0.6, 0.4), (1.3, 1.0, 0.8), M('#b5763d', 0.7), bevel=0.03)
        for k in range(6):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(X + cx - 0.4 + (k % 3) * 0.4, Y - 0.75 + (k // 3) * 0.35, 0.95))
            o = bpy.context.object; o.data.materials.append(M(col, 0.5)); bpy.ops.object.shade_smooth()
    return {'spots': {'cashier': (X + 1.0, Y + 2.3, 0, 0), 'customer': (X - 1.3, Y - 0.3, 0, 145)},
            'cams': {'from_door': ((X - 0.6, Y - d / 2 - 3.2, 4.0), (X + 0.2, Y + 1.2, 1.6))}, 'seat': 0.75}


# ---------------------------------------------------------------- the underwater lab (RodiOcean world, owner 10 Nov 2026)
# Owner: "its seems so nice the underwater lab - create the world and make a huge screen this is what the videos will be
# about after all". Light-blue water, NO radar (owner: "AI always go to this radar when I talk about ocean").
# The huge screen shows the episode's content: scene line 'screen: <picture or video file>'.
_BRAND_TPL = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'assets', 'brand', 'templates'))
LAB_DEFAULT_SCREEN = {False: os.path.join(_BRAND_TPL, 'bg_A_ocean_rays_wide.jpg'), True: os.path.join(_BRAND_TPL, 'bg_A_ocean_rays_tall.jpg')}
# The screen takes the video's shape (owner, 10 Nov 2026: "The screen should be 9:16 for 9:16 videos"):
# Owner, 10 Nov 2026: "Even bigger screen" -> about 40 % bigger than the first version.
LAB_SCREEN = {False: dict(w=17.6, h=9.9, bottom=1.4, y=6.0),           # wide videos: 16:9, about six people wide
              True: dict(w=15.0 * 9 / 16, h=15.0, bottom=1.4, y=6.0)}  # Shorts: 9:16, about five people tall


def _is_tall():
    r = bpy.context.scene.render
    return r.resolution_y > r.resolution_x


def _lab_screen_material(path, tall=False):
    m = bpy.data.materials.new('LabScreen'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage')
    path = path if path and os.path.exists(path) else LAB_DEFAULT_SCREEN[tall]
    if os.path.exists(path):
        img = bpy.data.images.load(path, check_existing=True)
        tex.image = img
        if path.lower().endswith(('.mp4', '.mov', '.webm', '.mkv', '.avi')):    # a video plays on the screen
            img.source = 'MOVIE'
            tex.image_user.frame_duration = max(1, img.frame_duration)
            tex.image_user.frame_start = 1
            tex.image_user.use_auto_refresh = True
            tex.image_user.use_cyclic = True
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color']); nt.links.new(tex.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.4
    return m


def _lab_sand():
    m = bpy.data.materials.new('LabSand'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*hexrgb('#b5def0'), 1); b.inputs['Roughness'].default_value = 0.9
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value = 0.9
    rmp = nt.nodes.new('ShaderNodeValToRGB')                 # rippling light on the sand (caustics)
    rmp.color_ramp.elements[0].position, rmp.color_ramp.elements[0].color = 0.0, (1, 1, 1, 1)
    rmp.color_ramp.elements[1].position, rmp.color_ramp.elements[1].color = 0.06, (0, 0, 0, 1)
    nt.links.new(vor.outputs['Distance'], rmp.inputs['Fac'])
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 0.6
    nt.links.new(rmp.outputs['Color'], k.inputs[0]); nt.links.new(k.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (*hexrgb('#e8fbff'), 1)
    return m


def _see_through(name, color, strength, fac_from):
    """Emission mixed with transparency; fac_from(nt) returns the socket that says how solid it is."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*hexrgb(color), 1); em.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(fac_from(nt), mix.inputs['Fac']); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m


def _ray_fac(nt):
    """Light shafts: bright at the top, fading downward and toward the sides."""
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['UV'], sep.inputs[0])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.2; nt.links.new(sep.outputs['Y'], pw.inputs[0])
    pp = nt.nodes.new('ShaderNodeMath'); pp.operation = 'PINGPONG'; pp.inputs[1].default_value = 0.5; nt.links.new(sep.outputs['X'], pp.inputs[0])
    sf = nt.nodes.new('ShaderNodeMath'); sf.operation = 'MULTIPLY'; sf.inputs[1].default_value = 2.0; nt.links.new(pp.outputs[0], sf.inputs[0])
    f = nt.nodes.new('ShaderNodeMath'); f.operation = 'MULTIPLY'; nt.links.new(pw.outputs[0], f.inputs[0]); nt.links.new(sf.outputs[0], f.inputs[1])
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 0.4; nt.links.new(f.outputs[0], k.inputs[0])
    return k.outputs[0]


def _bubble_fac(nt):
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
    return lw.outputs['Facing']


LAB_LOGO = os.path.normpath(os.path.join(_BRAND_TPL, '..', 'world_logo.png'))


def _decal(path, loc, size, rot, alpha=1.0, emit=0.15, name='Decal'):
    """A see-through picture lying on a surface (paint on the floor, print on a box)."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=tuple(math.radians(r) for r in rot))
    p = bpy.context.object; p.name = name; p.scale = (size[0], size[1], 1)
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(path, check_existing=True)
    tex.extension = 'CLIP'
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color']); nt.links.new(tex.outputs['Color'], b.inputs['Emission Color'])
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = alpha
    nt.links.new(tex.outputs['Alpha'], k.inputs[0]); nt.links.new(k.outputs[0], b.inputs['Alpha'])
    b.inputs['Emission Strength'].default_value = emit; b.inputs['Roughness'].default_value = 0.6
    p.data.materials.append(m); p.visible_shadow = False
    return p


def _lab_logo(X, Y, S):
    """(Superseded 10 Nov 2026 by lab_dressing.py: the owner wanted the name 'more combined naturally with the surroundings'.)
    The channel's name in the world, like the format benchmark's name painted on the football field and on the boat's hull
    (owner, 10 Nov 2026: "his logo that he 'secretly' put in every footage"): never a corner badge."""
    if not os.path.exists(LAB_LOGO):
        return
    asp = 570 / 3452                                                  # world_logo.png height / width
    fw = min(S['w'] * 0.95, 10.0)
    _decal(LAB_LOGO, (X, Y + 1.7, 0.014), (fw, fw * asp), (0, 0, 0), alpha=0.8, emit=0.1, name='LogoFloor')       # painted floor
    pw = min(S['w'] * 0.8 - 0.6, 7.5)
    _decal(LAB_LOGO, (X, Y + S['y'] + 0.25 - 0.61, S['bottom'] * 0.5), (pw, pw * asp), (90, 0, 0), alpha=1.0, emit=0.2,
           name='LogoPedestal')                                       # printed on the screen's pedestal


LAB_DRESS = ('crates', 'buoy', 'sub')         # the lab's everyday things (lab_dressing.py); scene line 'dress: ...' changes them


def lab(at=(400, 0), screen=None, logo=True, dress=None, brand=None, t_end=20.0, seed=0):
    """The underwater lab: light-blue water (lighter toward the surface; light('underwater')), a sea-blue sand floor with
    rippling light, a soft round lab floor, the HUGE screen behind the cast, light shafts, glassy bubbles, pale far mounds,
    and real things that carry the channel's name and that Ginger can run into (lab_dressing.py):
    dress = which things (default crates, buoy, sub; also tank, hose), brand = which carries the name (default ONE, picked by seed;
    'floor' and 'pedestal' add worn floor paint and a maker's badge on the pedestal); logo=False: no name anywhere."""
    import lab_dressing
    X, Y = at; rnd = random.Random(7)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(X, Y, -0.002)); fl = bpy.context.object; fl.name = 'LabSand'
    fl.data.materials.append(_lab_sand())
    cyl((X, Y + 1.0, 0.0), 9.5, 0.01, M('#dff1f9', 0.55), verts=128)                  # the lab floor, flush with the sand
    bpy.ops.mesh.primitive_torus_add(major_radius=9.5, minor_radius=0.06, location=(X, Y + 1.0, 0.01), major_segments=128)
    bpy.context.object.data.materials.append(M('#7ed6ff', 0.3, emit=hexrgb('#9fe6ff'), emit_strength=2.0))
    tall = _is_tall(); S = LAB_SCREEN[tall]; cz = S['bottom'] + S['h'] / 2
    pieces = tuple(dress) if dress is not None else LAB_DRESS
    carriers = (None if brand is None else set(brand)) if logo else set()
    badge = [dict(img='badge.png', c=(0, -0.6, 0.0), w=min(S['w'] * 0.4, 3.2))] if carriers is not None and 'pedestal' in carriers else []
    (lab_dressing.box if badge else box)((X, Y + S['y'] + 0.25, S['bottom'] / 2), (S['w'] * 0.8, 1.2, S['bottom']),
        lab_dressing.printed('#eef7fc', 0.45, badge, name='Pedestal') if badge else M('#eef7fc', 0.45), bevel=0.12)   # pedestal
    box((X, Y + S['y'] + 0.12, cz), (S['w'] + 0.5, 0.22, S['h'] + 0.5), M('#f6fbfe', 0.35), bevel=0.15)              # bezel
    box((X, Y + S['y'] - 0.005, cz), (S['w'] + 0.16, 0.02, S['h'] + 0.16), M('#7ed6ff', 0.3, emit=hexrgb('#bfeeff'), emit_strength=1.6), bevel=0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(X, Y + S['y'] - 0.03, cz), rotation=(math.radians(90), 0, 0))
    sc = bpy.context.object; sc.name = 'LabScreen'; sc.scale = (S['w'], S['h'], 1); sc.data.materials.append(_lab_screen_material(screen, tall))
    bumps = lab_dressing.dress(X, Y, S, tall, pieces, carriers, t_end, seed)   # the things in the lab, the name on them, Ginger's bumps
    ray = _see_through('LabRay', '#ffffff', 1.5, _ray_fac)
    for x, y, rz, w in ((-9, 9, 12, 3.4), (-3, 13, -8, 4.2), (4, 10, 10, 3.0), (10, 15, -14, 4.6), (-14, 16, 6, 4.0), (15, 22, 9, 5)):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(X + x, Y + y, 9.0), rotation=(math.radians(90), math.radians(rz), 0))
        p = bpy.context.object; p.scale = (w, 18.0, 1); p.data.materials.append(ray); p.visible_shadow = False
    bub = _see_through('LabBubble', '#f2fcff', 1.4, _bubble_fac)
    for _ in range(46):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rnd.uniform(0.04, 0.13), location=(X + rnd.uniform(-10, 10), Y + rnd.uniform(-3, 14), rnd.uniform(1.0, 11.0)))
        o = bpy.context.object; o.data.materials.append(bub); o.visible_shadow = False; bpy.ops.object.shade_smooth()
    for x, y, s, hx in ((-16, 24, 6, '#b8e6f6'), (14, 26, 5.5, '#b8e6f6'), (-5, 36, 9, '#c8eef9'), (22, 42, 11, '#d2f2fb'),
                        (-26, 44, 10, '#d2f2fb'), (6, 55, 14, '#dbf5fc')):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=s, location=(X + x, Y + y, 0)); o = bpy.context.object
        o.scale = (1.3, 1.0, 0.55); o.data.materials.append(M(hx, 0.95, emit=hexrgb(hx), emit_strength=0.25)); o.visible_shadow = False
        bpy.ops.object.shade_smooth()
    wide = ((X, Y - 12.0, 6.0), (X, Y + 3.0, 7.0)) if tall else ((X, Y - 7.5, 4.2), (X, Y + 3.0, 5.0))   # a wide frame sees far more sideways
    side = S['w'] / 2 + 1.4                                          # beside the screen, whatever its shape
    lr = 2.4 if tall else 3.0                                        # a narrower frame in Shorts: left/right closer in
    bgx = S['w'] / 2 + 2.2                                           # just outside the shot, behind the cast
    return {'spots': {'left': (X - lr, Y - 0.6, 0, 0), 'centre': (X, Y - 1.0, 0, 0), 'right': (X + lr, Y - 0.6, 0, 0),
                      'presenter': (X + side, Y + 3.0, 0, -25), 'screen_left': (X - side, Y + 3.0, 0, 25),
                      # Ginger's background cameo (owner: like the format benchmark's girl on the bicycle who falls in most of its Shorts):
                      # bg_mid sits left of centre: her pounce carries her about 1.6 forward, so she lands in the gap between the cast
                      'bg_left': (X - bgx, Y + 3.2, 0, 90), 'bg_mid': (X - 2.0, Y + 3.2, 0, 90), 'bg_right': (X + bgx, Y + 3.2, 0, -90)},
            'cams': {'wide': wide, 'from_door': wide}, 'bumps': bumps,
            'screen': (X, Y + S['y'] - 0.05, cz), 'seat': 0.75}


# ---------------------------------------------------------------- the void (12 Nov 2026)
# An endless plain floor and backdrop in one flat colour, for pieces that need no place around them (a thought, a diagram
# made of props, a product shot). The floor is not lit like the other floors: it shows the flat colour everywhere and only
# darkens softly where the light on it is blocked (under and just behind things), so no horizon line and no hard shadows.
VOID_COLOR = '#9ad8f5'                                     # a light ocean blue
VOID_KEY = dict(energy=2.2, rot=(24, 0, 18), angle=38)     # the one light that casts (soft) shadows: almost straight down
VOID_FILL = dict(energy=1.5, rot=(66, 0, -22))             # from the camera side, no shadows: faces are never dark
VOID_AMBIENT = 0.5                                         # even light from everywhere (not tinted by the backdrop colour)
VOID_SHADE = 0.6                                           # how dark the floor gets in full shadow (1 = no shadow at all)


def _void_floor(color):
    """The flat colour, darkened only by how much of the light reaching the floor is blocked ('Shade' is set by light())."""
    m = bpy.data.materials.new('VoidFloor'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    dif = nt.nodes.new('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new('ShaderNodeShaderToRGB'); bw = nt.nodes.new('ShaderNodeRGBToBW')
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.name = 'Shade'; mr.interpolation_type = 'SMOOTHSTEP'
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.name = 'Tone'
    c = hexrgb(color)
    mix.inputs['A'].default_value = (*(v * VOID_SHADE for v in c), 1); mix.inputs['B'].default_value = (*c, 1)
    nt.links.new(dif.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs['Color'], bw.inputs[0]); nt.links.new(bw.outputs[0], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mix.inputs['Factor']); nt.links.new(mix.outputs['Result'], em.inputs['Color'])
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m


def void(at=(0, 0), color=None):
    """An endless floor and backdrop in one flat colour (default a light ocean blue; scene line 'void: #hex')."""
    global VOID
    X, Y = at; color = color or VOID_COLOR
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(X, Y, -0.001)); fl = bpy.context.object; fl.name = 'VoidFloor'
    fl.data.materials.append(_void_floor(color)); fl.visible_shadow = False
    VOID = dict(color=color, floor=fl)
    row = lambda dx, dy: (X + dx, Y + dy, 0.0, 0)
    # 1.35 apart like the street's, but each step outward also stands 0.6 further back (a shallow V, the middle in front):
    # side by side at 1.35 two adults' arms would run through each other
    return {'spots': {'centre': row(0, 0), 'left': row(-1.35, 0.6), 'right': row(1.35, 0.6), 'far_left': row(-2.7, 1.2), 'far_right': row(2.7, 1.2),
                      'back_left': row(-1.35, 3.6), 'back_mid': row(0, 3.0), 'back_right': row(1.35, 3.6)},
            'cams': {'wide': ((X, Y - 9.0, 2.4), (X, Y + 0.8, 1.6)), 'two_shot': ((X, Y - 5.4, 1.8), (X, Y + 0.6, 1.55))}, 'seat': 0.75}


def _void_light():
    """The void's own light, whatever the preset: the backdrop is the flat colour (to the camera only; the light that falls on
    the cast stays white), one soft light from almost straight above, a shadowless one from the camera side."""
    c = hexrgb(VOID['color']); w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); seen = nt.nodes.new('ShaderNodeBackground'); amb = nt.nodes.new('ShaderNodeBackground')
    seen.inputs['Color'].default_value = (*c, 1); seen.inputs['Strength'].default_value = 1.0
    amb.inputs['Color'].default_value = (1, 1, 1, 1); amb.inputs['Strength'].default_value = VOID_AMBIENT
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac']); nt.links.new(amb.outputs[0], mix.inputs[1]); nt.links.new(seen.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    for o in [o for o in bpy.data.objects if o.type == 'LIGHT' and o.name.split('.')[0] in ('Sun', 'Fill')]:
        bpy.data.objects.remove(o)
    lit = {}
    for name, L, shadow in (('VoidKey', VOID_KEY, True), ('VoidFill', VOID_FILL, False)):
        d = bpy.data.lights.new(name, 'SUN'); d.energy = L['energy']; d.color = (1, 1, 1); d.angle = math.radians(L.get('angle', 10))
        d.use_shadow = shadow
        if shadow and hasattr(d, 'use_shadow_jitter'):     # a wide light needs jittered shadows to come out soft
            d.use_shadow_jitter = True; d.shadow_jitter_overblur = 20
        o = bpy.data.objects.new(name, d); bpy.context.collection.objects.link(o); o.rotation_euler = tuple(math.radians(r) for r in L['rot'])
        lit[name] = L['energy'] * math.cos(math.radians(L['rot'][0])) / math.pi     # what it adds to a flat white floor
    full = lit['VoidKey'] + lit['VoidFill'] + VOID_AMBIENT                           # the floor's reading with nothing in the way
    sh = VOID['floor'].data.materials[0].node_tree.nodes['Shade']
    sh.inputs['From Min'].default_value = full - lit['VoidKey'] * 0.9; sh.inputs['From Max'].default_value = full - lit['VoidKey'] * 0.12


PLACES = dict(street=street, classroom=classroom, bedroom=bedroom, kitchen=kitchen, office=office, shop=shop_inside, lab=lab, void=void)


def place(name, at=None, **opts):
    BUILT.append(name)
    if {'void', 'street'} <= set(BUILT):
        raise SystemExit('the void and the street both sit at 0 0: use one or the other in a scene')
    return PLACES[name](at, **opts) if at is not None else PLACES[name](**opts)


# ---------------------------------------------------------------- lighting presets
LIGHT_PRESETS = {
    'day': dict(sky=('#3f93ff', '#bfe2ff', 0.55), sun=(2.6, '#fff6ea', (48, 0, 30)), fill=350, glass=('#cfeaff', 0.4), lamps=0),
    'golden': dict(sky=('#5a78d6', '#ffbf86', 0.5), sun=(2.4, '#ffb36b', (76, 0, -58)), fill=220, glass=('#ffd7a8', 0.8), lamps=0),
    'night': dict(sky=('#0b1236', '#2a3a6e', 0.22), sun=(0.25, '#9fb6ff', (40, 0, 20)), fill=140, glass=('#ffcf6a', 4.0), lamps=400),
    # the underwater lab: light aqua water, lighter toward the surface; the light comes from straight above
    'underwater': dict(sky=('#e2f7ff', '#8fd4ee', 1.0), sun=(2.4, '#eafaff', (22, 0, 25)), fill=300, glass=('#cfeaff', 0.4), lamps=0),
}


def light(preset='day'):
    """Sky, sun, a soft fill, window glow and street lamps for the street; indoor rooms get a big ceiling light as well."""
    P = LIGHT_PRESETS[preset]
    world(top=P['sky'][0], horizon=P['sky'][1], strength=P['sky'][2])
    for o in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(o)
    e, col, rot = P['sun']; d = bpy.data.lights.new('Sun', 'SUN'); d.energy = e; d.color = hexrgb(col); d.angle = math.radians(8)
    o = bpy.data.objects.new('Sun', d); bpy.context.collection.objects.link(o); o.rotation_euler = tuple(math.radians(r) for r in rot)
    if P['fill']:
        d = bpy.data.lights.new('Fill', 'AREA'); d.energy = P['fill']; d.size = 8
        o = bpy.data.objects.new('Fill', d); bpy.context.collection.objects.link(o); o.location = (-6, -8, 7); o.rotation_euler = (math.radians(55), 0, math.radians(-35))
    b = _glass().node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (*hexrgb(P['glass'][0]), 1); b.inputs['Emission Strength'].default_value = P['glass'][1]
    if preset == 'night':
        b.inputs['Base Color'].default_value = (*hexrgb('#ffcf6a'), 1)
    for m in bpy.data.materials:                      # lamp heads glow at night
        if m.name.startswith('C_#fff2c8'):
            m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 6.0 if P['lamps'] else 0.0
    for k, loc in enumerate(LAMPS if P['lamps'] else []):
        d = bpy.data.lights.new(f'Lamp{k}', 'POINT'); d.energy = P['lamps']; d.color = hexrgb('#ffcf8a'); d.shadow_soft_size = 0.4
        o = bpy.data.objects.new(f'Lamp{k}', d); bpy.context.collection.objects.link(o); o.location = loc
    for (X, Y), (w, dd, h) in ROOMS:                  # rooms: a warm ceiling light (day: soft, night: the only light)
        d = bpy.data.lights.new('Ceiling', 'AREA'); d.size = 6; d.energy = 350 if preset == 'night' else 600; d.color = hexrgb('#fff1dc')
        o = bpy.data.objects.new('Ceiling', d); bpy.context.collection.objects.link(o); o.location = (X, Y, h - 0.15)
    if VOID:                                          # the void lights itself: flat backdrop, soft light, soft shadows only
        _void_light()
