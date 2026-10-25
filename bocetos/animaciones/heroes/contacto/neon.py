"""El neón de Barullo sobre la pared de pavés (héroe de /contacto).

Calcado de las fotos del club: el contorno del kufi en tubo rojo, delante de
una pared de bloques de vidrio con contraluz morado y azul, y las luces de la
sala barriendo por detrás. El neón zumba (pequeñas variaciones) y da dos
parpadeos por bucle; la cámara se mece muy poco para que el vidrio «viva».

Los bloques no son vidrio refractado de verdad (en EEVEE sale caro y sucio):
la cara de cada bloque emite la luz de detrás modulada por el dibujo ondulado
del vidrio, y lleva barniz para que el neón se refleje.

blender -b --factory-startup --python neon.py -- <wordmark.json> <out> <view> <frames> [samples] [scale%]
"""
import bpy, bmesh, json, math, os, sys
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
WM, OUT, VIEW, FR = argv[:4]
SAMPLES = int(argv[4]) if len(argv) > 4 else 64
SCALE = int(argv[5]) if len(argv) > 5 else 100
os.makedirs(OUT, exist_ok=True)
FPS, LOOP = 30, 240
TAU = 2 * math.pi
W0 = TAU / LOOP

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.fps = FPS
for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
    try:
        sc.render.engine = eng; break
    except TypeError:
        pass
ee = sc.eevee
for attr, val in (('use_raytracing', True), ('taa_render_samples', SAMPLES), ('use_shadows', True),
                  ('fast_gi_method', 'GLOBAL_ILLUMINATION')):
    if hasattr(ee, attr):
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
if VIEW == 'narrow':
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
else:
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = SCALE
for vt in ('Khronos PBR Neutral', 'AgX', 'Filmic'):
    try:
        sc.view_settings.view_transform = vt; break
    except TypeError:
        pass
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (0.002, 0.002, 0.003, 1)

# ---------------------------------------------------------------- pared de pavés
BLK, GAP = 0.19, 0.007              # bloque y llaga (m)
COLS, ROWS = 26, 18
Z0 = -1.0                            # la pared sigue por debajo del encuadre
WALL_W = COLS * (BLK + GAP); WALL_H = ROWS * (BLK + GAP)

# Luz de detrás: un valor por fotograma que se mete en los nodos.
glass = bpy.data.materials.new('pavés'); glass.use_nodes = True
nt = glass.node_tree; N = nt.nodes; Lk = nt.links.new
pb = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
pb.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1)
pb.inputs['Roughness'].default_value = 0.08
for k, v in (('Coat Weight', 1.0), ('Coat Roughness', 0.04), ('Specular IOR Level', 0.6)):
    if k in pb.inputs:
        pb.inputs[k].default_value = v
tc = N.new('ShaderNodeTexCoord'); geo = N.new('ShaderNodeNewGeometry')
# 1) dibujo del vidrio: ondas concéntricas por bloque (coordenadas del objeto)
sepw = N.new('ShaderNodeSeparateXYZ'); Lk(geo.outputs['Position'], sepw.inputs[0])
mod = []
for axis in ('X', 'Z'):
    m = N.new('ShaderNodeMath'); m.operation = 'WRAP'
    m.inputs[1].default_value = -(BLK + GAP) / 2; m.inputs[2].default_value = (BLK + GAP) / 2
    Lk(sepw.outputs[axis], m.inputs[0]); mod.append(m)
cmb = N.new('ShaderNodeCombineXYZ'); Lk(mod[0].outputs[0], cmb.inputs['X']); Lk(mod[1].outputs[0], cmb.inputs['Y'])
ln = N.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; Lk(cmb.outputs[0], ln.inputs[0])
ring = N.new('ShaderNodeMath'); ring.operation = 'MULTIPLY'; ring.inputs[1].default_value = 95.0
Lk(ln.outputs['Value'], ring.inputs[0])
sn = N.new('ShaderNodeMath'); sn.operation = 'SINE'; Lk(ring.outputs[0], sn.inputs[0])
rip = N.new('ShaderNodeMapRange'); rip.inputs['From Min'].default_value = -1; rip.inputs['To Min'].default_value = 0.75
Lk(sn.outputs[0], rip.inputs['Value'])
nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 38; nz.inputs['Detail'].default_value = 4
Lk(geo.outputs['Position'], nz.inputs['Vector'])
ripn = N.new('ShaderNodeMath'); ripn.operation = 'MULTIPLY_ADD'
Lk(nz.outputs['Fac'], ripn.inputs[0]); ripn.inputs[1].default_value = 0.6; Lk(rip.outputs[0], ripn.inputs[2])
# 2) contraluz: degradado morado→azul + dos focos que barren (posiciones por fotograma)
grad = N.new('ShaderNodeValToRGB'); cr = grad.color_ramp
cr.elements[0].color = (0.035, 0.022, 0.028, 1); cr.elements[1].color = (0.022, 0.02, 0.03, 1)
Lk(sepw.outputs['X'], grad.inputs['Fac'])
spots = []
for i, col in enumerate(((0.05, 0.025, 0.03), (0.035, 0.025, 0.035))):   # sin magenta: luz de sala tenue
    c = N.new('ShaderNodeCombineXYZ'); c.name = f'spot{i}'
    d = N.new('ShaderNodeVectorMath'); d.operation = 'DISTANCE'
    Lk(geo.outputs['Position'], d.inputs[0]); Lk(c.outputs[0], d.inputs[1])
    f = N.new('ShaderNodeMapRange'); f.inputs['From Max'].default_value = 0.9
    f.inputs['To Min'].default_value = 1.0; f.inputs['To Max'].default_value = 0.0
    Lk(d.outputs['Value'], f.inputs['Value'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'ADD'
    mx.inputs['B'].default_value = (*col, 1)
    Lk(f.outputs[0], mx.inputs['Factor'])
    spots.append((c, mx))
Lk(grad.outputs['Color'], spots[0][1].inputs['A']); Lk(spots[0][1].outputs['Result'], spots[1][1].inputs['A'])
# 3) el rojo del neón sobre los bloques cercanos
redd = N.new('ShaderNodeVectorMath'); redd.operation = 'DISTANCE'; redd.name = 'neon_d'
Lk(geo.outputs['Position'], redd.inputs[0])
redd.inputs[1].default_value = (0.0, 0.0, 0.0)
redf = N.new('ShaderNodeMapRange'); redf.inputs['From Max'].default_value = 0.45
redf.inputs['To Min'].default_value = 1.0; redf.inputs['To Max'].default_value = 0.0
Lk(redd.outputs['Value'], redf.inputs['Value'])
# (1 - d/R)^2: la caída llega a cero sin escalón, no hay disco con borde
redq = N.new('ShaderNodeMath'); redq.operation = 'POWER'; redq.inputs[1].default_value = 2.0
Lk(redf.outputs[0], redq.inputs[0])
redk = N.new('ShaderNodeMath'); redk.operation = 'MULTIPLY'; redk.inputs[1].default_value = 0.6
Lk(redq.outputs[0], redk.inputs[0])
redm = N.new('ShaderNodeMix'); redm.data_type = 'RGBA'; redm.blend_type = 'ADD'; redm.name = 'neon_mix'
redm.inputs['B'].default_value = (1.0, 0.08, 0.03, 1)
Lk(redk.outputs[0], redm.inputs['Factor']); Lk(spots[1][1].outputs['Result'], redm.inputs['A'])
emi = N.new('ShaderNodeMix'); emi.data_type = 'RGBA'; emi.blend_type = 'MULTIPLY'; emi.inputs['Factor'].default_value = 1
Lk(redm.outputs['Result'], emi.inputs['A']); Lk(ripn.outputs[0], emi.inputs['B'])
Lk(emi.outputs['Result'], pb.inputs['Emission Color'])
pb.inputs['Emission Strength'].default_value = 0.75
bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25
Lk(ripn.outputs[0], bump.inputs['Height']); Lk(bump.outputs['Normal'], pb.inputs['Normal'])

bm = bmesh.new()
for cx in range(COLS):
    for cz in range(ROWS):
        x = -WALL_W / 2 + (cx + 0.5) * (BLK + GAP); z = Z0 + (cz + 0.5) * (BLK + GAP)
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']:
            v.co = Vector((x + v.co.x * BLK, v.co.y * 0.08, z + v.co.z * BLK))
mw = bpy.data.meshes.new('pared'); bm.to_mesh(mw); bm.free()
wall = bpy.data.objects.new('pared', mw); sc.collection.objects.link(wall)
bv = wall.modifiers.new('bisel', 'BEVEL'); bv.width = 0.02; bv.segments = 4
wall.data.materials.append(glass)
wall.data.polygons.foreach_set('use_smooth', [True] * len(wall.data.polygons))
# mortero oscuro detrás de las llagas
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.03, Z0 + WALL_H / 2))
mo = bpy.context.object; mo.scale = (WALL_W + 1, WALL_H + 1, 1); mo.rotation_euler = (math.radians(90), 0, 0)
mm = bpy.data.materials.new('mortero'); mm.use_nodes = True
mp = next(n for n in mm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
mp.inputs['Base Color'].default_value = (0.05, 0.045, 0.045, 1); mp.inputs['Roughness'].default_value = 0.9
mo.data.materials.append(mm)

# ---------------------------------------------------------------- neón
wm = json.load(open(WM))
SIGN_W = 1.25 if VIEW == 'wide' else 1.15
s = SIGN_W / wm['w']
SIGN_C = Vector((0.55, -0.16, 1.18)) if VIEW == 'wide' else Vector((0.0, -0.16, 1.32))
cu = bpy.data.curves.new('neon', 'CURVE'); cu.dimensions = '3D'
cu.bevel_depth = 0.0055; cu.bevel_resolution = 4; cu.fill_mode = 'FULL'
for poly in wm['polys']:
    p = np.array(poly, float)
    # el tubo va un poco por dentro del contorno, como en el cartel real
    pts = [(SIGN_C.x + (x - wm['w'] / 2) * s, SIGN_C.y, SIGN_C.z - (y - wm['h'] / 2) * s) for x, y in p]
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, q in enumerate(pts):
        sp.points[i].co = (*q, 1)
    sp.use_cyclic_u = True
neon = bpy.data.objects.new('neon', cu); sc.collection.objects.link(neon)
nm = bpy.data.materials.new('neon'); nm.use_nodes = True
npb = next(n for n in nm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
npb.inputs['Base Color'].default_value = (1.0, 0.25, 0.15, 1)
npb.inputs['Emission Color'].default_value = (1.0, 0.13, 0.05, 1)
npb.inputs['Emission Strength'].default_value = 40.0
neon.data.materials.append(nm)
# la luz que el neón echa sobre la pared y la sala
nl = bpy.data.lights.new('neon_luz', 'AREA'); nl.shape = 'RECTANGLE'; nl.size = SIGN_W; nl.size_y = SIGN_W * 0.33
nl.color = (1.0, 0.12, 0.05); nl.energy = 22
nlo = bpy.data.objects.new('neon_luz', nl); sc.collection.objects.link(nlo)
# mirando a la pared (antes alumbraba hacia la cámara): un baño suave y
# difuso alrededor del letrero, sin borde
nlo.location = SIGN_C + Vector((0, -0.05, 0)); nlo.rotation_euler = (math.radians(-90), 0, 0)
nlb = bpy.data.lights.new('neon_rebote', 'AREA'); nlb.size = SIGN_W; nlb.color = (1.0, 0.12, 0.05); nlb.energy = 0
nlbo = bpy.data.objects.new('neon_rebote', nlb); sc.collection.objects.link(nlbo)
nlbo.location = SIGN_C + Vector((0, -0.02, 0)); nlbo.rotation_euler = (math.radians(90), 0, 0)
# el rojo en la pared: distancia al segmento horizontal del letrero
pos_ = N.new('ShaderNodeSeparateXYZ'); Lk(geo.outputs['Position'], pos_.inputs[0])
dxa = N.new('ShaderNodeMath'); dxa.operation = 'SUBTRACT'; dxa.inputs[1].default_value = SIGN_C.x
Lk(pos_.outputs['X'], dxa.inputs[0])
dxb = N.new('ShaderNodeMath'); dxb.operation = 'ABSOLUTE'; Lk(dxa.outputs[0], dxb.inputs[0])
dxc = N.new('ShaderNodeMath'); dxc.operation = 'SUBTRACT'; dxc.inputs[1].default_value = SIGN_W * 0.42
Lk(dxb.outputs[0], dxc.inputs[0])
dxd = N.new('ShaderNodeMath'); dxd.operation = 'MAXIMUM'; dxd.inputs[1].default_value = 0.0
Lk(dxc.outputs[0], dxd.inputs[0])
dz_ = N.new('ShaderNodeMath'); dz_.operation = 'SUBTRACT'; dz_.inputs[1].default_value = SIGN_C.z
Lk(pos_.outputs['Z'], dz_.inputs[0])
seg = N.new('ShaderNodeCombineXYZ'); Lk(dxd.outputs[0], seg.inputs['X']); Lk(dz_.outputs[0], seg.inputs['Y'])
sl = N.new('ShaderNodeVectorMath'); sl.operation = 'LENGTH'; Lk(seg.outputs[0], sl.inputs[0])
Lk(sl.outputs['Value'], redf.inputs['Value'])

# ---------------------------------------------------------------- compositor: halo
try:
    cg = bpy.data.node_groups.new('comp', 'CompositorNodeTree')
    cg.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = cg.nodes.new('CompositorNodeRLayers'); gl = cg.nodes.new('CompositorNodeGlare')
    go = cg.nodes.new('NodeGroupOutput')
    for val in ('Bloom', 'BLOOM', 'Fog Glow', 'FOG_GLOW'):
        try:
            gl.inputs['Type'].default_value = val; break
        except Exception:
            pass
    gl.inputs['Threshold'].default_value = 0.9
    gl.inputs['Strength'].default_value = 0.55
    gl.inputs['Size'].default_value = 0.6
    cg.links.new(rl.outputs['Image'], gl.inputs['Image']); cg.links.new(gl.outputs['Image'], go.inputs[0])
    sc.compositing_node_group = cg
    print('GLARE ok', gl.inputs['Type'].default_value)
except Exception as e:
    print('GLARE fallo', e)

# ---------------------------------------------------------------- cámara
cam_d = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
if VIEW == 'narrow':
    LOC, TGT, lens = Vector((0.35, -2.6, 0.95)), Vector((0.0, 0.0, 1.15)), 32
else:
    LOC, TGT, lens = Vector((-0.55, -2.9, 0.75)), Vector((-0.4, 0.0, 0.85)), 30
vec = lambda k: Vector(tuple(map(float, os.environ[k].split(','))))
if 'CAM' in os.environ: LOC = vec('CAM')
if 'TGT' in os.environ: TGT = vec('TGT')
if 'LENS' in os.environ: lens = float(os.environ['LENS'])
cam_d.lens = lens
cam_d.dof.use_dof = True
cam_d.dof.focus_distance = (SIGN_C - LOC).length; cam_d.dof.aperture_fstop = 2.2

# parpadeos: dos tropiezos por bucle, lejos del empalme
FLICK = {int(LOOP * 0.37) + k: v for k, v in enumerate((0.15, 1.0, 0.05, 0.6, 1.0))}
FLICK.update({int(LOOP * 0.78) + k: v for k, v in enumerate((0.3, 1.0))})

def set_frame(f):
    t = f * W0
    cam.location = LOC + Vector((0.12 * math.sin(t), 0.0, 0.04 * math.sin(2 * t + 0.5)))
    cam.rotation_euler = (TGT - cam.location).to_track_quat('-Z', 'Y').to_euler()
    hum = 1.0 + 0.03 * math.sin(7 * t) + 0.02 * math.sin(13 * t + 1)
    k = FLICK.get(f % LOOP, 1.0) * hum
    npb.inputs['Emission Strength'].default_value = 40.0 * k
    nl.energy = 22 * k
    redk.inputs[1].default_value = 0.6 * k   # el rojo en el vidrio sigue al neón
    for i, (c, _) in enumerate(spots):
        ph = i * math.pi
        c.inputs['X'].default_value = (WALL_W * 0.42) * math.sin(t * (1 + i) + ph)
        c.inputs['Y'].default_value = 0.0
        c.inputs['Z'].default_value = Z0 + WALL_H * (0.5 + 0.3 * math.sin(2 * t + ph + 1.0))

if '-' in FR:
    rng_, _, step = FR.partition(':')
    a, b = map(int, rng_.split('-'))
    frames = list(range(a, b + 1, int(step or 1)))
else:
    frames = [int(FR)]
for f in frames:
    set_frame(f)
    sc.frame_set(f)
    sc.render.filepath = os.path.join(OUT, f'{VIEW}_{f:04d}.png')
    if os.environ.get('SKIP') and os.path.exists(sc.render.filepath):
        continue   # reanudar: lo ya renderizado no se repite
    if os.environ.get('DRY'):
        print('DRY', f, flush=True); continue
    bpy.ops.render.render(write_still=True)
    print('FRAME', f, flush=True)
