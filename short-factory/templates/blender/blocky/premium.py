"""LOOK=premium: the optional high-end look for the blocky world (look test, 12 Nov 2026). Opt-in: scene.py calls apply()
only when the environment has LOOK=premium; without it nothing here runs and every picture and check stays as it was.

It is a pass over what the scene table already built (places, cast, props, camera), so nothing has to be rewritten:
- renderer(): Cycles on the graphics card (scene.cycles_look), denoised, a film-like picture style (TONE below), a gentle
  glow on bright things only.
- materials(): the same colours, new finishes, picked from each material's own numbers: glossy toy plastic with a clear coat,
  real metal for anything marked metallic (the satellite's body becomes crinkled gold foil), real glass for the thought
  bubbles, soft cloth kept for the things that were built rough (lab coats, beanies, aprons), animals as soft vinyl toys.
  Heads stay a little less shiny so the drawn faces read. Bevelled edges are shaded round, so they catch a highlight.
- stage(): the void gets a slightly reflective floor in its own colour that melts into a smooth backdrop of the same hue
  (lighter low, deeper high; no horizon line); the lab's round floor becomes subtly reflective. Other places only get the
  softer sky light.
- lights(): one warm key from the upper front left with soft shadows (the one shadow under everything), a cool rim from
  behind on the right, a soft fill from the camera side and even sky light, so nothing goes black. They are sun-type lights:
  the same wherever the camera travels.
  Shiny things do not mirror those suns (a sun's glint is a hard spark) but two big soft lights in the sky (_sky_light).
- focus(): depth of field that follows the shot. The focus point is the camera's own aim point (it already travels with the
  framed subject, also during the flights between framings); the lens opening is set per frame from the distance and the depth
  of what the shot frames, so the subject stays sharp from its nearest to its farthest part and things far behind go soft.

Switches (environment): TONE=neutral (default: 'Khronos PBR Neutral', keeps the toy colours as they are and still rolls bright
spots off softly) | agx (AgX 'Punchy', the chess Short's style: tried first, 12 Nov 2026, and it greys this world's light
pastel colours: the void's light blue and the satellite's gold are colours AgX cannot show, measured); SAMPLES=n; DOF=0
turns the depth of field off.
Tested only on the lab and the void (the squirrel episode's scene_a / scene_b); the street and the rooms are untested.

LOOK=chess (round 2, 12 Nov 2026; owner on round 1: "still not like the chess"): the same pass, pushed to the chess Short's
recipe. Everything in CHESS_SET below replaces round 1's numbers, and these things are built differently:
- the floor (the void's, and the lab's round floor under the cast) is glossy marble in a checker of deep navy and pale
  aqua-white tiles with veins, mirroring whatever stands on it (_marble_floor);
- the void's backdrop is dusk over the ocean: a warm peach glow at the horizon, through teal, to deep blue-violet high up,
  mirrored in the floor; the far floor fades into the glow, so there is no horizon line (_dusk); the lab's water is deepened;
- the light is a low warm sunset key from the front left with long soft shadows, a strong cool rim from behind on the right
  that shiny things mirror as a bright edge (the floor is kept out of it by light linking: no flare), low fill;
- gold is polished (no crinkle), dark hair is satin (no pale blob), the grade is AgX 'Punchy', the focus a touch shallower."""
import math, os, time
import bpy
from mathutils import Vector
from common import FPS, hexrgb, bloom
import places as PL

TONE = os.environ.get('TONE', 'neutral').lower()
TONES = {'agx': dict(view='AgX', look='AgX - Punchy', exposure=1.0),
         'neutral': dict(view='Khronos PBR Neutral', look='None', exposure=0.0),
         'chess': dict(view='AgX', look='AgX - Punchy', exposure=0.5)}             # LOOK=chess: the lights are tuned for it
SAMPLES, NOISE = 64, 0.03                          # Cycles samples per pixel (most pixels stop earlier) and where they stop
TONE = TONE if TONE in TONES else 'neutral'
GLOW = dict(threshold=1.6, strength=0.35, size=0.5)   # only what is brighter than a sunlit white wall glows
KEY = dict(energy=2.6, color='#ffe6c8', angle=9, toward=(-0.5, -0.75, 0.6))       # 'toward' = where the light stands, seen from the cast
RIM = dict(energy=3.4, color='#a9cdff', angle=14, toward=(0.62, 0.7, 0.4))        # casts no shadow: one clear shadow, the key's
FILL = dict(energy=0.5, color='#ffffff', angle=40, toward=(0.3, -0.8, 0.45))      # casts no shadow
AMBIENT = 0.25                                     # even light from everywhere
FLOOR_LIT = 1.03                                   # what those lights add up to on a bare floor (measured on a still), so the void's floor reads as its own colour
SOFTBOXES = ((KEY, 6.0, 15, 21), (RIM, 4.5, 14, 26))   # round soft lights that only shiny things mirror, where the key and the rim stand:
#                                                    (light, brightness, full inside this angle, gone outside this one; degrees)
CLAMP = 0.0                                        # cap on one light sample's brightness (0 = none): tames sparkles on thin shiny things
PALE = 0.35                                        # how far the sky that shiny things mirror is washed toward white
AMBIENT_ELSEWHERE = AMBIENT                        # LOOK=chess: the sky's light in a place that is not the void (the lab)
CHESS = False                                      # LOOK=chess: set by apply(); the numbers below then replace the ones above
CHESS_SET = dict(
    TONE='chess', SAMPLES=128, NOISE=0.015,
    GLOW=dict(threshold=2.4, strength=0.45, size=0.55),
    KEY=dict(energy=7.5, color='#ffc48a', angle=5, toward=(-0.75, -0.62, 0.34)),       # a low sunset sun: long shadows to the right
    RIM=dict(energy=9.0, color='#9dc4ff', angle=30, toward=(0.5, 0.85, 0.17)),        # a big soft cool light, low behind on the right:
    #                                                 low, so the upright edges of the blocks mirror it toward the camera (the outline)
    FILL=dict(energy=1.3, color='#dfe8ff', angle=40, toward=(0.3, -0.8, 0.45)),
    AMBIENT=0.55,                                  # the dusk sky's own light on matt surfaces (times its colour)
    SOFTBOXES=((dict(color='#ffd2a0', toward=(-0.75, -0.62, 0.34)), 16.0, 10, 14),),     # the sun's glow as shiny things mirror it
    PALE=0.0, B_MAX=0.022, CLAMP=10.0, AMBIENT_ELSEWHERE=0.3)
TILE = 1.35                                        # one marble tile (a person is 1 wide)
MARBLE = dict(dark=('#0c1a38', '#2b4a7d'), light=('#e2f1f5', '#9ebfcc'))               # (stone, veins): deep navy, pale aqua-white
DUSK = (('#ff9a55', 0.0, 1.8), ('#ff9a7a', 0.1, 1.2), ('#c9a5a0', 0.2, 0.9), ('#3fa3ad', 0.36, 0.8), ('#3558c0', 0.6, 0.75),
        ('#3b2f9a', 1.0, 0.7))                     # (colour, height 0..1 up the picture's sky, brightness): peach glow -> teal -> blue-violet
DEEP = (0.22, 0.5, 0.8)                           # another place's sky (the lab's water) is deepened and tinted by this
DUSK_TOP = 0.55                                    # the top colour is reached this far up (sine of the angle above the horizon)
B_MAX, B_SHARP = 0.014, 0.002                      # blur of things endlessly far behind / allowed on the subject's own depth (parts of the picture height)


def _bsdf(m):
    return next((n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'), None) if m.node_tree else None


def _set(node, **kw):
    for name, v in kw.items():
        s = node.inputs.get(name.replace('_', ' '))
        if s is not None and not s.is_linked:
            s.default_value = v


def _fcurves(ob):
    act = ob.animation_data.action if ob.animation_data else None
    if act is None:
        return []
    return list(getattr(act, 'fcurves', None) or [fc for ly in act.layers for s in ly.strips for cb in s.channelbags for fc in cb.fcurves])


# ---------------------------------------------------------------- renderer
def renderer(sc):
    cy = sc.cycles
    cy.samples = int(os.environ.get('SAMPLES', SAMPLES)); cy.adaptive_threshold = NOISE
    for k, v in (('glossy_bounces', 4), ('transmission_bounces', 8), ('transparent_max_bounces', 12), ('sample_clamp_indirect', 6.0), ('blur_glossy', 0.5)):
        try:
            setattr(cy, k, v)
        except Exception:
            pass
    cy.sample_clamp_direct = CLAMP
    T = TONES[TONE]
    sc.view_settings.view_transform = T['view']
    try:
        sc.view_settings.look = T['look']
    except Exception:
        pass
    sc.view_settings.exposure = T['exposure']
    bloom(sc)
    for ng in (getattr(sc, 'compositing_node_group', None), getattr(sc, 'node_tree', None)):
        for n in (ng.nodes if ng else []):
            if n.bl_idname == 'CompositorNodeGlare':
                for name, v in (('Threshold', GLOW['threshold']), ('Strength', GLOW['strength']), ('Size', GLOW['size'])):
                    if name in n.inputs:
                        n.inputs[name].default_value = v
                if hasattr(n, 'threshold'):
                    n.threshold = GLOW['threshold']
    t = {}

    def pre(*_):
        t['t0'] = time.time()

    def post(*_):
        print(f'PREMIUM frame {bpy.context.scene.frame_current}: rendered in {time.time() - t["t0"]:.2f} s ({cy.samples} samples)', flush=True)
    bpy.app.handlers.render_pre.append(pre); bpy.app.handlers.render_post.append(post)


# ---------------------------------------------------------------- materials
def _finish(b, vinyl=False):
    """New finish from the material's own numbers; the colour is never touched."""
    if b.inputs['Alpha'].is_linked or b.inputs['Alpha'].default_value < 0.999 or b.inputs['Roughness'].is_linked:
        return                                        # see-through things and textured finishes stay
    r, metal = b.inputs['Roughness'].default_value, b.inputs['Metallic'].default_value
    if metal >= 0.3 and CHESS:                        # polished metal: sharp highlights, mirrors the sky
        _set(b, Metallic=1.0, Roughness=min(max(r * 0.5, 0.12), 0.2), Coat_Weight=0.0)
    elif metal >= 0.3:                                # marked metallic: real metal
        _set(b, Metallic=1.0, Roughness=min(max(r * 0.6, 0.1), 0.26), Coat_Weight=0.0)
    elif r >= 0.88:                                   # grass, sand, walls, wool: matt as built
        pass
    elif vinyl and r >= 0.55:                         # animals: soft vinyl toys
        _set(b, Roughness=0.42, Coat_Weight=0.35, Coat_Roughness=0.12)
    elif r >= 0.78:                                   # cloth: lab coats, aprons, hats
        _set(b, Roughness=0.62, Sheen_Weight=0.35, Sheen_Roughness=0.45)
    elif CHESS and r >= 0.72:                         # hair: satin (as glossy plastic a dark flat side mirrored the key as a pale blob)
        _set(b, Roughness=0.5, Coat_Weight=0.25, Coat_Roughness=0.3)
    elif r >= 0.55:                                   # toy plastic: clothes, hair, wood, cash
        _set(b, Roughness=0.3, Coat_Weight=0.8, Coat_Roughness=0.07)
    else:                                             # already smooth: glossy plastic, enamel
        _set(b, Roughness=max(0.1, r * 0.45), Coat_Weight=1.0, Coat_Roughness=0.03)


def _foil(m):
    """The satellite's body: crinkled gold foil (its colour and glow keys stay as the prop set them)."""
    b = _bsdf(m); nt = m.node_tree
    if CHESS:                                         # round 2: polished like the chess king, no crinkle
        _set(b, Metallic=1.0, Roughness=0.12, Coat_Weight=0.0); return
    _set(b, Metallic=1.0, Roughness=0.2, Coat_Weight=0.0)
    tc = nt.nodes.new('ShaderNodeTexCoord'); vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 5.5
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.22; bump.inputs['Distance'].default_value = 0.05
    nt.links.new(tc.outputs['Object'], vor.inputs['Vector']); nt.links.new(vor.outputs['Distance'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])


def _glass(m):
    """A thought bubble: a real glass ball (a weak lens, so the icon inside stays readable) with clear reflections; the bright
    rim the prop animates ('Rim', warmed up by 'flare') stays as a soft edge glow."""
    nt = m.node_tree; rim = nt.nodes.get('Rim'); out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial')
    for n in [n for n in nt.nodes if n not in (rim, out)]:
        nt.nodes.remove(n)
    g = nt.nodes.new('ShaderNodeBsdfPrincipled')
    _set(g, Base_Color=(0.93, 0.98, 1.0, 1.0), Roughness=0.0, IOR=1.12, Transmission_Weight=1.0, Coat_Weight=1.0, Coat_Roughness=0.02, Coat_IOR=1.6)
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.3
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.4
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 0.55; k.use_clamp = True
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lw.outputs['Facing'], pw.inputs[0]); nt.links.new(pw.outputs[0], k.inputs[0]); nt.links.new(k.outputs[0], mix.inputs['Fac'])
    nt.links.new(g.outputs[0], mix.inputs[1])
    if rim is not None:
        nt.links.new(rim.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])


def materials(chars):
    vinyl = set()
    for R in chars.values():
        if R.get('kind') in ('quad', 'bird'):
            for o in R['root'].children_recursive:
                if o.type == 'MESH':
                    vinyl.update(m for m in o.data.materials if m)
    for m in bpy.data.materials:
        b = _bsdf(m); name = m.name.split('.')[0]
        if name == 'ThoughtBubble':
            _glass(m)
        elif b is None or name in ('VoidFloor', 'LabScreen', 'LabSand', 'Mystery_shadow'):
            continue
        elif name == 'SatelliteFoil':
            _foil(m)
        elif name.startswith(('Head_', 'Muzzle')) or b.inputs['Base Color'].is_linked and any(n.bl_idname == 'ShaderNodeAttribute' for n in m.node_tree.nodes):
            _set(b, Roughness=0.36, Coat_Weight=0.3, Coat_Roughness=0.1)      # heads: a soft sheen, the drawn face stays clear
        else:
            _finish(b, vinyl=m in vinyl)
    for o in bpy.data.objects:                        # bevelled edges shaded round (the flat faces stay flat)
        if o.type == 'MESH':
            bevs = [md for md in o.modifiers if md.type == 'BEVEL']
            if bevs and not all(p.use_smooth for p in o.data.polygons):
                o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
                for md in bevs:
                    md.harden_normals = True
            elif not bevs and any(p.use_smooth for p in o.data.polygons):
                o.data.set_sharp_from_angle(angle=math.radians(40))   # round things keep crisp rims: no smeared mirror at a cylinder's end


# ---------------------------------------------------------------- floor, backdrop, sky light
def _mix(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def _void_colours(c):
    """-> (floor, low, high): the void's colour for the floor, a lighter tint low on the backdrop, a deeper one high up."""
    if TONE == 'neutral':
        return tuple(v / FLOOR_LIT for v in c), _mix(c, (1, 1, 1), 0.4), tuple(v ** 1.9 for v in c)
    mx = max(c); sat = lambda p, k: tuple((v / mx) ** p * mx * k for v in c)          # AgX greys bright colours: feed it purer ones
    return sat(2.5, 1.0), _mix(sat(2.0, 1.6), (1.6,) * 3, 0.3), sat(3.0, 0.8)


def _void_stage(sc):
    c = hexrgb(PL.VOID['color']); floor_c, low, high = _void_colours(c)
    m = PL.VOID['floor'].data.materials[0]; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    _set(p, Base_Color=(*floor_c, 1), Roughness=0.24, Specular_IOR_Level=0.6)
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*low, 1)
    cd = nt.nodes.new('ShaderNodeCameraData'); mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = 12.0, 90.0
    mix = nt.nodes.new('ShaderNodeMixShader')                # far away the floor melts into the backdrop's lowest colour: no horizon line
    nt.links.new(cd.outputs['View Distance'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], mix.inputs['Fac'])
    nt.links.new(p.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs['Surface'])
    w = sc.world; nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = 0.0, 0.5
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'EASE'
    ramp.color_ramp.elements[0].color = (*low, 1); ramp.color_ramp.elements[1].color = (*high, 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    seen = nt.nodes.new('ShaderNodeBackground'); nt.links.new(ramp.outputs['Color'], seen.inputs['Color'])
    _sky_light(nt, out, seen, ramp.outputs['Color'], AMBIENT, white=True)


def _sky_light(nt, out, seen, colour, ambient, white=False, wash=None):
    """The camera (and glass) sees the sky as built; shiny things mirror a paler sky with two round soft lights in it (SOFTBOXES:
    warm where the key stands, cool where the rim stands: the broad highlights and the cool edge on glossy plastic and metal);
    matt surfaces get even light of strength `ambient` (white in the void, the sky's own tint elsewhere)."""
    lp = nt.nodes.new('ShaderNodeLightPath'); N, L = nt.nodes, nt.links
    amb = N.new('ShaderNodeBackground'); amb.inputs['Strength'].default_value = ambient
    if white:
        amb.inputs['Color'].default_value = (1, 1, 1, 1)
    else:
        L.new(colour, amb.inputs['Color'])
    pale = N.new('ShaderNodeMix'); pale.data_type = 'RGBA'; pale.inputs['Factor'].default_value = PALE if wash is None else wash; pale.inputs['B'].default_value = (1, 1, 1, 1)
    L.new(colour, pale.inputs['A'])
    tc = N.new('ShaderNodeTexCoord'); glossy = pale.outputs['Result']
    for P, bright, inner, outer in SOFTBOXES:         # round soft lights in the mirrored sky, where the key and the rim stand
        dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; dot.inputs[1].default_value = Vector(P['toward']).normalized()
        box = N.new('ShaderNodeMapRange'); box.interpolation_type = 'SMOOTHSTEP'
        box.inputs['From Min'].default_value, box.inputs['From Max'].default_value = math.cos(math.radians(outer)), math.cos(math.radians(inner))
        L.new(tc.outputs['Generated'], dot.inputs[0]); L.new(dot.outputs['Value'], box.inputs['Value'])
        add = N.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['B'].default_value = (*(v * bright for v in hexrgb(P['color'])), 1)
        L.new(box.outputs['Result'], add.inputs['Factor']); L.new(glossy, add.inputs['A']); glossy = add.outputs['Result']
    gl = N.new('ShaderNodeBackground'); L.new(glossy, gl.inputs['Color'])
    m1 = N.new('ShaderNodeMixShader'); L.new(lp.outputs['Is Glossy Ray'], m1.inputs['Fac']); L.new(amb.outputs[0], m1.inputs[1]); L.new(gl.outputs[0], m1.inputs[2])
    direct = N.new('ShaderNodeMath'); direct.operation = 'MAXIMUM'
    L.new(lp.outputs['Is Camera Ray'], direct.inputs[0]); L.new(lp.outputs['Is Transmission Ray'], direct.inputs[1])
    m2 = N.new('ShaderNodeMixShader'); L.new(direct.outputs[0], m2.inputs['Fac']); L.new(m1.outputs[0], m2.inputs[1]); L.new(seen.outputs[0], m2.inputs[2])
    L.new(m2.outputs[0], out.inputs['Surface'])


def _marble(nt, vec, stone, vein):
    """Soft marble veins (the chess Short's recipe): noise -> wave -> ramp."""
    N, L = nt.nodes, nt.links
    noise = N.new('ShaderNodeTexNoise'); _set(noise, Scale=1.6, Detail=12.0, Distortion=4.0)
    wave = N.new('ShaderNodeTexWave'); _set(wave, Scale=0.9, Distortion=9.0, Detail=6.0)
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (*hexrgb(vein), 1)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.22, (*hexrgb(stone), 1)
    L.new(vec, noise.inputs['Vector']); L.new(noise.outputs['Color'], wave.inputs['Vector']); L.new(wave.outputs[1], ramp.inputs[0])
    return ramp.outputs['Color']


def _marble_floor(name, haze=None):
    """Glossy marble tiles in a checker of MARBLE's two stones, thin dark joints between them, a tile's middle on the floor's
    own origin. haze = (colour, from, to): far away the floor fades into that colour (the void: no horizon line)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = _bsdf(m)
    _set(b, Roughness=0.08, Coat_Weight=1.0, Coat_Roughness=0.03)
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])

    def op(kind, a, c=None):
        n = N.new('ShaderNodeMath'); n.operation = kind
        for i, v in enumerate((a, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    fx, fy = op('ADD', op('DIVIDE', sep.outputs['X'], TILE), 0.5), op('ADD', op('DIVIDE', sep.outputs['Y'], TILE), 0.5)
    parity = op('MODULO', op('ADD', op('ADD', op('FLOOR', fx), op('FLOOR', fy)), 1000.0), 2.0)
    gx, gy = op('FRACT', fx), op('FRACT', fy)
    edge = op('MINIMUM', op('MINIMUM', gx, op('SUBTRACT', 1.0, gx)), op('MINIMUM', gy, op('SUBTRACT', 1.0, gy)))
    mr = N.new('ShaderNodeMapRange'); L.new(edge, mr.inputs['Value'])
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = 0.0, 0.008
    mr.inputs['To Min'].default_value, mr.inputs['To Max'].default_value = 1.0, 0.0
    joint = mr.outputs['Result']
    sock = lambda socks, ident: next(x for x in socks if x.identifier == ident)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    L.new(parity, sock(mx.inputs, 'Factor_Float')); L.new(_marble(nt, tc.outputs['Object'], *MARBLE['dark']), sock(mx.inputs, 'A_Color'))
    L.new(_marble(nt, tc.outputs['Object'], *MARBLE['light']), sock(mx.inputs, 'B_Color'))
    mx2 = N.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; sock(mx2.inputs, 'B_Color').default_value = (0.012, 0.014, 0.02, 1)
    L.new(joint, sock(mx2.inputs, 'Factor_Float')); L.new(sock(mx.outputs, 'Result_Color'), sock(mx2.inputs, 'A_Color'))
    L.new(sock(mx2.outputs, 'Result_Color'), b.inputs['Base Color'])
    L.new(op('ADD', 0.07, op('MULTIPLY', joint, 0.5)), b.inputs['Roughness'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.01
    L.new(op('SUBTRACT', 1.0, joint), bump.inputs['Height']); L.new(bump.outputs['Normal'], b.inputs['Normal'])
    if haze:
        out = next(n for n in N if n.bl_idname == 'ShaderNodeOutputMaterial')
        em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*haze[0], 1)
        cd = N.new('ShaderNodeCameraData'); far = N.new('ShaderNodeMapRange'); far.interpolation_type = 'SMOOTHSTEP'
        far.inputs['From Min'].default_value, far.inputs['From Max'].default_value = haze[1], haze[2]
        mix = N.new('ShaderNodeMixShader'); L.new(cd.outputs['View Distance'], far.inputs['Value']); L.new(far.outputs['Result'], mix.inputs[0])
        L.new(b.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs['Surface'])
    return m


def _dusk(sc):
    """The void in LOOK=chess: dusk over the ocean (DUSK) for the camera, the mirrors and (dimmer) the matt surfaces, and the
    marble floor fading into the horizon's glow."""
    glow = tuple(v * DUSK[0][2] for v in hexrgb(DUSK[0][0]))
    fl = PL.VOID['floor']; fl.data.materials.clear(); fl.data.materials.append(_marble_floor('MarbleFloor', haze=(glow, 30.0, 170.0)))
    nt = sc.world.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = 0.0, DUSK_TOP
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'B_SPLINE'; el = ramp.color_ramp.elements
    for k, (hx, pos, bright) in enumerate(DUSK):
        e = el[k] if k < 2 else el.new(pos)
        e.position = pos; e.color = (*(v * bright for v in hexrgb(hx)), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], ramp.inputs[0])
    seen = nt.nodes.new('ShaderNodeBackground'); nt.links.new(ramp.outputs['Color'], seen.inputs['Color'])
    _sky_light(nt, out, seen, ramp.outputs['Color'], AMBIENT)


def _chess_stage(sc):
    if PL.VOID:
        _dusk(sc)
    else:                                             # another place: its own sky, deepened (pale water greys out under AgX)
        nt = sc.world.node_tree; out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputWorld')
        seen = out.inputs['Surface'].links[0].from_node
        if seen.inputs['Color'].is_linked:
            g = nt.nodes.new('ShaderNodeGamma'); g.inputs['Gamma'].default_value = 2.2
            tint = nt.nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MULTIPLY'; tint.inputs['Factor'].default_value = 1.0
            tint.inputs['B'].default_value = (*DEEP, 1)
            nt.links.new(seen.inputs['Color'].links[0].from_socket, g.inputs['Color']); nt.links.new(g.outputs[0], tint.inputs['A'])
            nt.links.new(tint.outputs['Result'], seen.inputs['Color'])
            _sky_light(nt, out, seen, tint.outputs['Result'], AMBIENT_ELSEWHERE, wash=0.55)    # mirrors see a paler sky: gold stays gold, not sea-green
    for m in bpy.data.materials:                      # the lab's screen and light shafts: dimmer, or AgX washes them pale
        for n in (m.node_tree.nodes if m.node_tree else []):
            if m.name.split('.')[0] == 'LabScreen' and n.bl_idname == 'ShaderNodeBsdfPrincipled':
                n.inputs['Emission Strength'].default_value *= 0.6; _set(n, Specular_IOR_Level=0.0)      # no white veil of mirrored light on the picture
            if m.name.split('.')[0] == 'LabRay' and n.bl_idname == 'ShaderNodeEmission':
                n.inputs['Strength'].default_value *= 0.4
    mm = None
    for o in bpy.data.objects:                        # the lab's round floor under the cast: the same marble
        if o.type == 'MESH' and any(m and m.name.startswith('C_#dff1f9_0.55') for m in o.data.materials):
            mm = mm or _marble_floor('MarbleLab'); o.data.materials.clear(); o.data.materials.append(mm); o['marble'] = True


def stage(sc):
    if CHESS:
        return _chess_stage(sc)
    if PL.VOID:
        _void_stage(sc)
    else:                                             # any other place keeps the sky its light preset built
        nt = sc.world.node_tree; out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputWorld')
        seen = out.inputs['Surface'].links[0].from_node
        col = seen.inputs['Color'].links[0].from_socket if seen.inputs['Color'].is_linked else None
        if col is not None:
            _sky_light(nt, out, seen, col, AMBIENT)
    for m in bpy.data.materials:                      # the lab's round floor: subtly reflective
        if m.name.startswith('C_#dff1f9_0.55'):
            _set(_bsdf(m), Roughness=0.3, Coat_Weight=0.0)


# ---------------------------------------------------------------- lights
def _mirror(o):
    """Polished metal (a flat gold face would mirror the rim as one blown-out patch, thin steel bars as sparkles) or a screen."""
    for m in o.data.materials:
        b = _bsdf(m) if m else None
        if b is not None and (m.name.split('.')[0] == 'LabScreen' or (not b.inputs['Metallic'].is_linked and b.inputs['Metallic'].default_value > 0.99)):
            return True
    return False


def lights():
    for o in [o for o in bpy.data.objects if o.type == 'LIGHT' and o.name.split('.')[0] in ('Sun', 'Fill', 'VoidKey', 'VoidFill')]:
        bpy.data.objects.remove(o)                    # the preset's sun and fill go; room ceilings and street lamps stay
    for name, P, shadow in (('PremiumKey', KEY, True), ('PremiumRim', RIM, False), ('PremiumFill', FILL, False)):   # one clear shadow: the key's
        d = bpy.data.lights.new(name, 'SUN'); d.energy = P['energy']; d.color = hexrgb(P['color']); d.angle = math.radians(P['angle'])
        d.use_shadow = shadow
        o = bpy.data.objects.new(name, d); bpy.context.collection.objects.link(o)
        o.rotation_euler = (-Vector(P['toward'])).to_track_quat('-Z', 'Y').to_euler()
        o.visible_glossy = False                      # shiny things mirror the sky's big softbox instead: a sun's own glint is a
                                                      # hard spark (grainy when out of focus), and a low back light in a glossy floor a flare
        if CHESS and name == 'PremiumRim':            # round 2: the rim is big and soft, casts shadows, and shiny things DO mirror
            d.use_shadow = True; o.visible_glossy = True                # it (the bright cool edge on every figure); the mirror floors
            skip = bpy.data.collections.new('RimSkips')                 # are kept out of its light, so it is no flare in them;
            for fl in [x for x in bpy.data.objects if x.type == 'MESH' and (x.get('marble') or (PL.VOID and x is PL.VOID['floor']) or _mirror(x))]:
                skip.objects.link(fl); skip.collection_objects[-1].light_linking.link_state = 'EXCLUDE'   # so are metal and screens
            o.light_linking.receiver_collection = skip


# ---------------------------------------------------------------- depth of field
HUMAN, QUAD = ((-0.8, -0.38, 0.0), (0.8, 0.38, 2.8)), ((-0.45, -1.0, 0.0), (0.45, 0.9, 1.6))     # a figure's box round its feet (scale 1)


def _extent(R):
    """The subject's box in its own space (x, y, z min and max), so the lens knows how deep the thing it frames is."""
    if 'dof_box' not in R:
        if not R.get('prop'):
            lo, hi = QUAD if R.get('kind') in ('quad', 'bird') else HUMAN; s = R.get('scale', 1.0)
            R['dof_box'] = (tuple(v * s for v in lo), tuple(v * s for v in hi))
        else:
            inv = R['root'].matrix_world.inverted(); pts = []
            for o in R['root'].children_recursive:
                if o.type == 'MESH' and o.visible_shadow:          # glows and flashes are not part of its body
                    pts += [inv @ (o.matrix_world @ Vector(c)) for c in o.bound_box]
            R['dof_box'] = (tuple(min(p[k] for p in pts) for k in range(3)), tuple(max(p[k] for p in pts) for k in range(3))) if pts else ((0,) * 3, (0,) * 3)
    return R['dof_box']


def focus(cam, holds, T_END, flight):
    """Key the lens opening every frame: as wide as B_MAX allows (how soft things far behind get), closed down until the
    framed subject is sharp from its nearest to its farthest corner (B_SHARP). The focus distance itself is the aim point."""
    if os.environ.get('DOF') == '0':
        cam.data.dof.use_dof = False; return
    bpy.context.view_layer.update()
    tgt = cam.data.dof.focus_object
    cf = {fc.array_index: fc for fc in _fcurves(cam) if fc.data_path == 'location'}
    tf = {fc.array_index: fc for fc in _fcurves(tgt) if fc.data_path == 'location'}
    lf = next(fc for fc in _fcurves(cam.data) if fc.data_path == 'lens')
    H = cam.data.sensor_height; n_frames = round(T_END * FPS) + 1; stops = []
    for f in range(1, n_frames + 1):
        t = (f - 1) / FPS
        i = max((k for k, h in enumerate(holds) if h[0] <= t), default=0)
        if i + 1 < len(holds) and t > holds[i + 1][0] - flight:
            i += 1                                    # flying to the next framing: its subject counts already
        c = Vector([cf[k].evaluate(f) for k in range(3)]); l = Vector([tf[k].evaluate(f) for k in range(3)])
        s = max((l - c).length, 0.05); v = (l - c) / s
        b = B_MAX if holds[i][3] else B_MAX * 0.25    # a wide of the place itself (no subject): nearly everything sharp
        for R in (holds[i][3][1:] if holds[i][2] == 'ots' else holds[i][3]):     # over the shoulder: only the one we look at must be sharp
            tr = R['track']; x, y, z, turn = tr.get(f) or tr[max(tr)]
            (x0, y0, z0), (x1, y1, z1) = _extent(R); a = math.radians(turn); ca, sa = math.cos(a), math.sin(a)
            for px in (x0, x1):
                for py in (y0, y1):
                    for pz in (z0, z1):
                        d = (Vector((x + px * ca - py * sa, y + px * sa + py * ca, z + pz)) - c).dot(v) - s      # how far in front of / behind the focus
                        if abs(d) > 1e-3 and s + d > 0.05:
                            b = min(b, B_SHARP * (s + d) / abs(d))
        lens = lf.evaluate(f)
        stops.append(math.log(lens * lens / (max(b, 1e-4) * s * 1000.0 * H)))
    for k, f in enumerate(range(1, n_frames + 1)):    # a short average, so the opening never jumps
        w = stops[max(0, k - 3):k + 4]
        cam.data.dof.aperture_fstop = math.exp(sum(w) / len(w)); cam.data.keyframe_insert('dof.aperture_fstop', frame=f)


def apply(sc, places, chars, props, cam, holds, T_END, flight, look='premium'):
    if look == 'chess':
        globals().update(CHESS_SET, CHESS=True)
    renderer(sc)
    materials(chars)
    stage(sc)
    lights()
    focus(cam, holds, T_END, flight)
