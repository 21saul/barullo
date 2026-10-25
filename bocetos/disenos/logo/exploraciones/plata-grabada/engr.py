"""Engraved-metal wordmark variants. blender -b --factory-startup --python engr.py -- <dir> <variant>"""
import bpy, json, math, os, sys
from mathutils import Vector

D, VAR = sys.argv[sys.argv.index('--') + 1:][:2]
ENG = os.path.join(D, 'tex', 'eng')
data = json.load(open(os.path.join(D, 'wordmark.json')))
IW, IH = data['w'], data['h']
WIDTH = 8.0
S = WIDTH / IW
HEIGHT = IH * S

SILVER = (0.92, 0.92, 0.94); GOLD = (1.0, 0.71, 0.33); ROSE = (0.97, 0.62, 0.52)
OLDGOLD = (0.85, 0.6, 0.3); BLACK = (0.03, 0.03, 0.035); REDM = (0.72, 0.04, 0.03)
NIELLO = (0.05, 0.04, 0.04)
# name: metal, metal rough, pattern, line colour (None = niello), line is metal?, enamel (None=palette / rgb / 'none'), gem
V = {
    'plata-rosetas-rojo': (SILVER, 0.05, 'rosetas', None, False, (0.8, 0.03, 0.02), None),
    'oro-girih-rubi': (GOLD, 0.08, 'girih', None, False, None, 'rubi'),
    'oro-rosa-arabesco': (ROSE, 0.07, 'arabesco', None, False, None, None),
    'cromo-negro-guilloche': (BLACK, 0.05, 'guilloche', SILVER, True, 'none', None),
    'plata-escamas': (SILVER, 0.05, 'escamas', None, False, None, None),
    'rojo-girih-plata': (REDM, 0.16, 'girih', SILVER, True, (1.0, 0.75, 0.82), None),
    'plata-todo-rubi': (SILVER, 0.04, 'todo', None, False, None, 'rubi'),
    'oro-turquesa': (OLDGOLD, 0.18, 'rosetas', None, False, (0.03, 0.55, 0.55), 'turquesa'),
    'plata-lapislazuli': (SILVER, 0.06, 'arabesco', (0.55, 0.42, 0.18), True, (0.04, 0.08, 0.45), None),
}
metal, mrough, pat, linecol, line_metal, enamel, gem = V[VAR.replace('-detalle', '')]
detail = VAR.endswith('-detalle')

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 80; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = (1500, 720) if not detail else (1200, 1200)
try:
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
except TypeError:
    pass

def world():
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, 0.6)
    env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(D, 'hdri', 'studio_small_09.hdr'))
    b1 = nt.nodes.new('ShaderNodeBackground'); b1.inputs[1].default_value = 0.9
    b2 = nt.nodes.new('ShaderNodeBackground'); b2.inputs[0].default_value = (0.0045, 0.0045, 0.005, 1)
    lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputWorld')
    L = nt.links.new
    L(tc.outputs['Generated'], mp.inputs['Vector']); L(mp.outputs['Vector'], env.inputs['Vector']); L(env.outputs['Color'], b1.inputs['Color'])
    L(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L(b1.outputs[0], mx.inputs[1]); L(b2.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs[0])

def wordmark(extrude=0.2, bevel=0.03, offset=-0.025, res=4):
    cu = bpy.data.curves.new('wm', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    for poly in data['polys']:
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 2)
        for i, (x, y) in enumerate(poly[:-1]):
            sp.points[i].co = ((x - IW / 2) * S, -(y - IH / 2) * S, 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = res; cu.offset = offset
    ob = bpy.data.objects.new('wordmark', cu); sc.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active

def img(nt, fn, uv, non_color=True):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(ENG, fn))
    if non_color: t.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(uv, t.inputs['Vector']); return t

def mixc(nt, fac, a, b):
    n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'; nt.links.new(fac, n.inputs['Factor'])
    for sock, v in (('A', a), ('B', b)):
        if isinstance(v, tuple): n.inputs[sock].default_value = (*v, 1)
        else: nt.links.new(v, n.inputs[sock])
    return n.outputs['Result']

def mixf(nt, fac, a, b):
    n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'FLOAT'; nt.links.new(fac, n.inputs['Factor'])
    for sock, v in (('A', a), ('B', b)):
        if isinstance(v, (int, float)): n.inputs[sock].default_value = v
        else: nt.links.new(v, n.inputs[sock])
    return n.outputs['Result']

def math_(nt, op, a, b=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]

def engraved_material():
    m = bpy.data.materials.new(VAR); m.use_nodes = True; nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / WIDTH, 1 / HEIGHT, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); uv = mp.outputs['Vector']
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Normal'], sep.inputs['Vector'])
    front = math_(nt, 'GREATER_THAN', sep.outputs['Z'], 0.9)
    Lt = img(nt, f'{pat}-lines.png', uv); Ft = img(nt, f'{pat}-fill.png', uv)
    lines = math_(nt, 'MULTIPLY', Lt.outputs['Color'], front)
    fill = math_(nt, 'MULTIPLY', Ft.outputs['Color'], front)
    if enamel == 'none':
        fill = math_(nt, 'MULTIPLY', fill, 0.0)
        ecol = (0, 0, 0)
    elif enamel is None:
        ecol = img(nt, f'{pat}-col.png', uv, non_color=False).outputs['Color']
    else:
        ecol = enamel
    lcol = linecol or NIELLO
    col = mixc(nt, fill, metal, ecol)
    col = mixc(nt, lines, col, lcol)
    nt.links.new(col, p.inputs['Base Color'])
    met = mixf(nt, fill, 1.0, 0.0)
    met = mixf(nt, lines, met, 1.0 if line_metal else 0.35)
    nt.links.new(met, p.inputs['Metallic'])
    rough = mixf(nt, fill, mrough, 0.06)
    rough = mixf(nt, lines, rough, 0.12 if line_metal else 0.5)
    nt.links.new(rough, p.inputs['Roughness'])
    if 'Coat Weight' in p.inputs:
        nt.links.new(fill, p.inputs['Coat Weight']); p.inputs['Coat Roughness'].default_value = 0.02
    h = math_(nt, 'ADD', lines, math_(nt, 'MULTIPLY', fill, 0.45))
    bm = nt.nodes.new('ShaderNodeBump'); bm.invert = True
    bm.inputs['Strength'].default_value = 0.8; bm.inputs['Distance'].default_value = 0.012
    nt.links.new(h, bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], p.inputs['Normal'])
    return m

def plain(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for k, v in kw.items():
        s_ = p.inputs[k.replace('_', ' ')]
        s_.default_value = (*v, 1) if isinstance(v, tuple) and s_.type == 'RGBA' else v
    return m

def area(name, loc, size, energy, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; nt = m.node_tree
    [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False

def add_gem(ob, kind):
    # centre of the star counter of the final "o"
    best = None
    for poly in data['polys']:
        xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        a = 0.5 * abs(sum(poly[i][0] * poly[i + 1][1] - poly[i + 1][0] * poly[i][1] for i in range(len(poly) - 1)))
        if cx > IW * 0.85 and (best is None or a < best[2]):
            best = (cx, cy, a)
    cx, cy, a = best
    r = math.sqrt(a / math.pi) * S * 0.78
    loc = ((cx - IW / 2) * S, -(cy - IH / 2) * S, 0.05)
    if kind == 'rubi':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=loc)
        g = bpy.context.object; g.scale = (1, 1, 0.62)
        g.data.materials.append(plain('ruby', Base_Color=(0.95, 0.02, 0.06), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24)
        g = bpy.context.object; g.scale = (1, 1, 0.55); bpy.ops.object.shade_smooth()
        g.data.materials.append(plain('turq', Base_Color=(0.05, 0.6, 0.58), Roughness=0.18, Coat_Weight=1.0))
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 1.02, minor_radius=r * 0.13, location=loc)
    b = bpy.context.object; bpy.ops.object.shade_smooth()
    b.data.materials.append(plain('bezel', Base_Color=metal, Metallic=1.0, Roughness=0.08))
    for o in (g, b):
        o.parent = ob

world()
ob = wordmark()
ob.data.materials.append(engraved_material())
if gem:
    add_gem(ob, gem)
ob.rotation_euler = (math.radians(98), 0, math.radians(-12))

c = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', c); sc.collection.objects.link(cam); sc.camera = cam
if detail:
    c.lens = 85; tgt = Vector((2.3, -0.4, 0.15)); cam.location = (3.6, -6.2, 1.0)
    c.dof.use_dof = True; c.dof.aperture_fstop = 2.8; c.dof.focus_distance = (tgt - Vector(cam.location)).length
else:
    c.lens = 44; tgt = Vector((0, 0, 0)); cam.location = (0.8, -12.5, 1.0)
cam.rotation_euler = (tgt - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()

softbox((0, -15, 5.5), (22, 3.2), 2.2)
softbox((0, -15, -4.5), (22, 1.6), 1.0, (1, 0.75, 0.85))
softbox((-9, -9, 0.5), (1.2, 8), 1.6, (1, 0.6, 0.25))
area('key', (-4, -8, 6), 6, 1100)
area('rimP', (6, 3, 2), 3, 2400, (1, 0.22, 0.55))
area('rimO', (-6, 3, -1), 3, 1600, (1, 0.5, 0.12))

sc.render.filepath = os.path.join(D, 'engr', f'{VAR}.png')
bpy.ops.render.render(write_still=True)
print('RENDERED', sc.render.filepath)
