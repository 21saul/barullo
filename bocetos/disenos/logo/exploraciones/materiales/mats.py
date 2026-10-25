"""Barullo wordmark material study. blender -b --factory-startup --python mats.py -- <dir> <variant>"""
import bpy, json, math, os, sys, random
from mathutils import Vector

D, VAR = sys.argv[sys.argv.index('--') + 1:][:2]
TEX = os.path.join(D, 'tex')
data = json.load(open(os.path.join(D, 'wordmark.json')))
IW, IH = data['w'], data['h']
WIDTH = 8.0
S = WIDTH / IW
HEIGHT = IH * S

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 72
sc.cycles.use_denoising = True
sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = 1500, 720
try:
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'
except TypeError:
    pass

BG = (0.0045, 0.0045, 0.005)

def world(hdri='studio_small_09', strength=0.9, rot=0.6, cam_col=BG):
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, rot)
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(os.path.join(D, 'hdri', hdri + '.hdr'))
    b1 = nt.nodes.new('ShaderNodeBackground'); b1.inputs[1].default_value = strength
    b2 = nt.nodes.new('ShaderNodeBackground'); b2.inputs[0].default_value = (*cam_col, 1)
    lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader')
    out = nt.nodes.new('ShaderNodeOutputWorld')
    L = nt.links.new
    L(tc.outputs['Generated'], mp.inputs['Vector']); L(mp.outputs['Vector'], env.inputs['Vector'])
    L(env.outputs['Color'], b1.inputs['Color'])
    L(lp.outputs['Is Camera Ray'], mx.inputs['Fac'])
    L(b1.outputs[0], mx.inputs[1]); L(b2.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs[0])

def principled(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for k, v in kw.items():
        key = k.replace('_', ' ')
        if key in p.inputs:
            p.inputs[key].default_value = (*v, 1) if isinstance(v, tuple) and p.inputs[key].type == 'RGBA' else v
    return m, p

def tex_node(nt, path, closest=False):
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path)
    if closest: tx.interpolation = 'Closest'
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / WIDTH, 1 / HEIGHT, 1)
    mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tx.inputs['Vector'])
    return tx, tc

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
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.shade_auto_smooth() if hasattr(bpy.ops.object, 'shade_auto_smooth') else None
    return ob

def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

def camera(loc=(0.8, -12.5, 1.0), target=(0, 0, 0), lens=44, fstop=None):
    c = bpy.data.cameras.new('cam'); c.lens = lens
    o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o
    if fstop:
        c.dof.use_dof = True; c.dof.aperture_fstop = fstop; c.dof.focus_distance = d.length

def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; nt = m.node_tree
    [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False

def brand_rims(k=1.0):
    softbox((0, -15, 5.5), (22, 3.2), 2.2 * k)
    softbox((0, -15, -4.5), (22, 1.6), 1.0 * k, (1, 0.75, 0.85))
    softbox((-9, -9, 0.5), (1.2, 8), 1.6 * k, (1, 0.6, 0.25))
    area('key', (-4, -8, 6), 6, 1400 * k)
    area('rimP', (6, 3, 2), 3, 2600 * k, (1, 0.22, 0.55))
    area('rimO', (-6, 3, -1), 3, 1800 * k, (1, 0.5, 0.12))

def pose(ob, tilt=6, yaw=-9):
    ob.rotation_euler = (math.radians(90 + tilt), 0, math.radians(yaw))

def drips(ob, mat, n=6, seed=3):
    random.seed(seed)
    pts = [(x, y) for poly in data['polys'] for x, y in poly]
    lows = sorted(pts, key=lambda p: -p[1])
    chosen = []
    for x, y in lows:
        if y < IH * 0.84 and all(abs(x - c[0]) > IW * 0.09 for c in chosen):
            chosen.append((x, y))
        if len(chosen) >= n: break
    for x, y in chosen:
        L = random.uniform(0.25, 0.7); r = random.uniform(0.045, 0.075)
        X = (x - IW / 2) * S + random.uniform(-0.05, 0.05); Y = -(y - IH / 2) * S
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=L, location=(X, Y - L / 2 + 0.02, 0.06), rotation=(math.radians(90), 0, 0), vertices=24)
        c = bpy.context.object
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 1.35, location=(X, Y - L + 0.02, 0.06))
        s = bpy.context.object
        for o in (c, s):
            o.data.materials.append(mat); o.parent = ob
            bpy.context.view_layer.objects.active = o; bpy.ops.object.shade_smooth()

V = VAR
world()
camera()

if V in ('plata', 'plata-satinada', 'cromo-negro', 'cromo-rojo', 'tornasol'):
    ob = wordmark()
    spec = {
        'plata': dict(Base_Color=(0.92, 0.92, 0.94), Metallic=1.0, Roughness=0.04),
        'plata-satinada': dict(Base_Color=(0.9, 0.9, 0.92), Metallic=1.0, Roughness=0.26, Anisotropic=0.7),
        'cromo-negro': dict(Base_Color=(0.03, 0.03, 0.035), Metallic=1.0, Roughness=0.05, Coat_Weight=1.0, Coat_Roughness=0.02),
        'cromo-rojo': dict(Base_Color=(0.85, 0.03, 0.02), Metallic=1.0, Roughness=0.12, Coat_Weight=1.0, Coat_Roughness=0.02),
        'tornasol': dict(Base_Color=(0.9, 0.9, 0.92), Metallic=1.0, Roughness=0.07, Thin_Film_Thickness=520.0, Thin_Film_IOR=1.45),
    }[V]
    m, p = principled(V, **spec); ob.data.materials.append(m); pose(ob)
    brand_rims(0.6 if V == 'plata' else 1.0)

elif V in ('liquido', 'hinchable'):
    ob = wordmark(extrude=0.08, bevel=0.085, offset=-0.075, res=10)
    if V == 'liquido':
        m, p = principled(V, Base_Color=(0.93, 0.93, 0.95), Metallic=1.0, Roughness=0.03)
        tx = bpy.data.textures.new('wob', 'CLOUDS'); tx.noise_scale = 0.9
        dm = ob.modifiers.new('wobble', 'DISPLACE'); dm.texture = tx; dm.strength = 0.05; dm.texture_coords = 'GLOBAL'
        ob.data.materials.append(m)
        drips(ob, m)
    else:
        m, p = principled(V, Base_Color=(0.85, 0.04, 0.03), Roughness=0.32, Coat_Weight=1.0, Coat_Roughness=0.03, Subsurface_Weight=0.15, Subsurface_Radius=(1, 0.2, 0.1))
        ob.data.materials.append(m)
    pose(ob); brand_rims()

elif V == 'persa-grabado':
    ob = wordmark()
    m, p = principled(V, Base_Color=(0.92, 0.92, 0.94), Metallic=1.0, Roughness=0.05)
    nt = m.node_tree
    tx, _ = tex_node(nt, os.path.join(TEX, 'letters-engrave.png'), closest=False)
    # motif lines become dark oxidised silver (niello), slightly sunk
    mr = nt.nodes.new('ShaderNodeMix'); mr.data_type = 'RGBA'
    mr.inputs['A'].default_value = (0.92, 0.92, 0.94, 1); mr.inputs['B'].default_value = (0.09, 0.07, 0.07, 1)
    nt.links.new(tx.outputs['Color'], mr.inputs['Factor']); nt.links.new(mr.outputs['Result'], p.inputs['Base Color'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.05; rr.inputs['To Max'].default_value = 0.42
    nt.links.new(tx.outputs['Color'], rr.inputs['Value']); nt.links.new(rr.outputs['Result'], p.inputs['Roughness'])
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.6; bm.inputs['Distance'].default_value = 0.01; bm.invert = True
    nt.links.new(tx.outputs['Color'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], p.inputs['Normal'])
    ob.data.materials.append(m); pose(ob, tilt=8, yaw=-12); brand_rims(0.7)

elif V == 'esmalte-persa':
    ob = wordmark(extrude=0.22, bevel=0.025, offset=-0.02, res=3)
    m, p = principled(V, Roughness=0.08, Coat_Weight=1.0, Coat_Roughness=0.01)
    nt = m.node_tree
    tx, tc = tex_node(nt, os.path.join(TEX, 'letters-riso.png'), closest=True)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Normal'], sep.inputs['Vector'])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.92
    nt.links.new(sep.outputs['Z'], gt.inputs[0])
    mc = nt.nodes.new('ShaderNodeMix'); mc.data_type = 'RGBA'; mc.inputs['A'].default_value = (0.93, 0.93, 0.95, 1)
    nt.links.new(gt.outputs[0], mc.inputs['Factor']); nt.links.new(tx.outputs['Color'], mc.inputs['B'])
    nt.links.new(mc.outputs['Result'], p.inputs['Base Color'])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(gt.outputs[0], inv.inputs[1]); nt.links.new(inv.outputs[0], p.inputs['Metallic'])
    ob.data.materials.append(m); pose(ob, tilt=7, yaw=-11); brand_rims(0.8)

elif V == 'vidrio-rojo':
    ob = wordmark(extrude=0.26, bevel=0.05, offset=-0.045, res=6)
    m, p = principled(V, Base_Color=(1.0, 0.12, 0.08), Roughness=0.03, Transmission_Weight=1.0, IOR=1.5)
    ob.data.materials.append(m); pose(ob)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 6, 0), rotation=(math.radians(90), 0, 0))
    bd = bpy.context.object; bd.scale = (26, 26 * 1176 / 840, 1)
    bm_, bp = principled('carpet-bd', Roughness=0.9)
    t2 = bm_.node_tree.nodes.new('ShaderNodeTexImage'); t2.image = bpy.data.images.load(os.path.join(TEX, 'carpet-riso.jpg'))
    bm_.node_tree.links.new(t2.outputs['Color'], bp.inputs['Base Color'])
    bm_.node_tree.links.new(t2.outputs['Color'], bp.inputs['Emission Color']); bp.inputs['Emission Strength'].default_value = 0.25
    bd.data.materials.append(bm_)
    camera(fstop=1.4)
    brand_rims(0.8)

elif V == 'neumorfismo':
    world(strength=0.25, cam_col=(0.6, 0.05, 0.04))
    col = (0.62, 0.045, 0.035)
    m, p = principled(V, Base_Color=col, Roughness=0.62)
    ob = wordmark(extrude=0.05, bevel=0.07, offset=-0.065, res=10)
    ob.data.materials.append(m)
    ob.rotation_euler = (math.radians(90), 0, 0); ob.location = (0, 0.0, 0)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0.13, 0), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(m)
    camera(loc=(0, -12.5, 0), lens=44)
    area('key', (-6, -6, 6), 8, 1600, (1, 0.97, 0.94))
    area('fill', (6, -6, -5), 8, 260, (1, 0.9, 0.9))

sc.render.filepath = os.path.join(D, 'mats', f'{V}.png')
bpy.ops.render.render(write_still=True)
print('RENDERED', sc.render.filepath)
