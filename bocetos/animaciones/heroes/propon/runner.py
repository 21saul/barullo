"""«Te extendemos la alfombra»: un corredor persa que se desenrolla sin fin.

Héroe de /eventos-privados (Propón una noche). El rollo avanza rodando sin
deslizar: lo que ya está en el suelo no se mueve, y la tela sale del rollo
por abajo. La cámara y las luces van con el rollo, y en LOOP fotogramas el
rollo avanza exactamente un periodo del dibujo (runner_tex.py), así que el
último fotograma empalma con el primero.

blender -b --factory-startup --python runner.py -- <tex> <out> <view> <frames> [samples] [scale%]
  view    wide | narrow
  frames  "12" | "0-239" | "0-239:4"
Variables: CAM / TGT (relativas al rollo, "x,y,z"), LENS.
"""
import bpy, math, os, sys
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
TEX, OUT, VIEW, FR = argv[:4]
SAMPLES = int(argv[4]) if len(argv) > 4 else 64
SCALE = int(argv[5]) if len(argv) > 5 else 100
os.makedirs(OUT, exist_ok=True)

FPS, LOOP = 30, 240
KNOT = 0.0065                       # metros por nudo
TILE_W, TILE_H = 343, 200           # nudos del trozo de runner_tex.py
P = TILE_W * KNOT                   # periodo del dibujo a lo largo (m)
WD = TILE_H * KNOT                  # ancho del corredor (m)
TH = 0.011                          # grosor de la alfombra
R0 = 0.19                           # radio de la vuelta exterior del rollo
PITCH = 0.0135                      # separación entre vueltas
TURNS = 3.6
FAR = 16.0                          # corredor tendido detrás del rollo
NXW = 56                            # divisiones a lo ancho

# ---------------------------------------------------------------- escena
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
                  ('shadow_ray_count', 2), ('shadow_step_count', 8), ('fast_gi_method', 'GLOBAL_ILLUMINATION')):
    if hasattr(ee, attr):
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
if hasattr(ee, 'ray_tracing_options'):
    ee.ray_tracing_options.resolution_scale = '1'
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
bg.inputs[0].default_value = (0.004, 0.003, 0.0035, 1); bg.inputs[1].default_value = 1.0

def img(name, colorspace='sRGB'):
    im = bpy.data.images.load(os.path.join(TEX, name))
    im.colorspace_settings.name = colorspace
    return im

def wool_material():
    m = bpy.data.materials.new('wool'); m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    uv = nt.nodes.new('ShaderNodeTexCoord')
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = img('runner_albedo.png'); ta.interpolation = 'Cubic'
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img('runner_normal.png', 'Non-Color')
    tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = img('runner_rough.png', 'Non-Color')
    for t in (ta, tn, tr):
        t.extension = 'REPEAT'
        nt.links.new(uv.outputs['UV'], t.inputs['Vector'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.2
    nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
    # el revés: el dibujo se intuye, más apagado y plano
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    back = nt.nodes.new('ShaderNodeMix'); back.data_type = 'RGBA'; back.blend_type = 'MIX'
    # el revés de una alfombra anudada: trama de yute, el dibujo apenas se
    # intuye. Así el rollo no enseña trozos blancos del logo cortado.
    back.inputs['B'].default_value = (0.16, 0.035, 0.025, 1)
    bf = nt.nodes.new('ShaderNodeMath'); bf.operation = 'MULTIPLY'; bf.inputs[1].default_value = 1.0
    # Lo enrollado enseña el revés: atributo «enrollado» (0 en el suelo, 1 en
    # el rollo, con transición en el punto de contacto), sumado a Backfacing.
    rolled = nt.nodes.new('ShaderNodeAttribute'); rolled.attribute_name = 'enrollado'
    mx_ = nt.nodes.new('ShaderNodeMath'); mx_.operation = 'MAXIMUM'
    nt.links.new(geo.outputs['Backfacing'], mx_.inputs[0]); nt.links.new(rolled.outputs['Fac'], mx_.inputs[1])
    nt.links.new(mx_.outputs[0], bf.inputs[0]); nt.links.new(bf.outputs[0], back.inputs['Factor'])
    # y sin el relieve ni la rugosidad del dibujo, que delatan el logo
    ns = nt.nodes.new('ShaderNodeMath'); ns.operation = 'MULTIPLY_ADD'
    ns.inputs[1].default_value = -1.2; ns.inputs[2].default_value = 1.2
    nt.links.new(bf.outputs[0], ns.inputs[0]); nt.links.new(ns.outputs[0], nm.inputs['Strength'])
    rmix = nt.nodes.new('ShaderNodeMix'); rmix.data_type = 'FLOAT'
    rmix.inputs['B'].default_value = 0.88
    nt.links.new(bf.outputs[0], rmix.inputs['Factor']); nt.links.new(tr.outputs['Color'], rmix.inputs['A'])
    nt.links.new(rmix.outputs['Result'], p.inputs['Roughness'])
    nt.links.new(ta.outputs['Color'], back.inputs['A'])
    nt.links.new(back.outputs['Result'], p.inputs['Base Color'])
    nt.links.new(tr.outputs['Color'], p.inputs['Roughness'])
    nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    for k, v in (('Sheen Weight', 0.5), ('Sheen Roughness', 0.45), ('Specular IOR Level', 0.12)):
        if k in p.inputs:
            p.inputs[k].default_value = v
    if 'Sheen Tint' in p.inputs:
        nt.links.new(back.outputs['Result'], p.inputs['Sheen Tint'])   # el revés tampoco brilla a logo
    return m

def plain(name, col, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*col, 1); p.inputs['Roughness'].default_value = rough
    return m

# ---------------------------------------------------------------- trayectoria
# Parámetro de la tela a lo largo: primero el tramo tendido (de lejos hacia
# el rollo, en -y), luego la espiral del rollo empezando por abajo.
nf = 260
far = np.geomspace(1e-3, FAR, nf)[::-1]          # denso cerca del rollo
far[-1] = 0.0
nphi = int(64 * TURNS)
phi = np.linspace(0, TURNS * 2 * math.pi, nphi + 1)[1:]
r = R0 - PITCH * phi / (2 * math.pi)
# longitud de arco a lo largo de la espiral
dphi = np.diff(np.concatenate([[0.0], phi]))
dr = -PITCH / (2 * math.pi)
arc = np.cumsum(np.sqrt(r ** 2 + dr ** 2) * dphi)
NP = nf + nphi
xs = np.linspace(-WD / 2, WD / 2, NXW + 1)

def path(yr):
    """(y, z, u) de cada muestra; yr = punto de contacto del rollo."""
    y = np.concatenate([yr + far, yr - r * np.sin(phi)])
    z = np.concatenate([np.full(nf, TH / 2), (R0 + TH / 2) - r * np.cos(phi)])
    u = np.concatenate([yr + far, yr - arc])
    # la tela tendida no queda perfecta: ondas suaves que van con el dibujo
    # (dependen de u, así que no se mueven en el suelo y el bucle cierra)
    lay = np.arange(NP) < nf
    wob = 0.004 * np.sin(2 * math.pi * u / P * 3 + 0.7) + 0.0025 * np.sin(2 * math.pi * u / P * 7 + 2.1)
    z = z + np.where(lay, np.clip(far_or_zero(lay, u, yr), 0, 1) * wob, 0.0)
    return y, z, u

def far_or_zero(lay, u, yr):
    # sin ondas justo al salir del rollo, para que apoye limpio
    return np.where(lay, (u - yr) / 0.6, 0.0)

me = bpy.data.meshes.new('runner')
verts = np.zeros(((NXW + 1) * NP, 3))
faces = [(j * (NXW + 1) + i, (j + 1) * (NXW + 1) + i, (j + 1) * (NXW + 1) + i + 1, j * (NXW + 1) + i + 1)
         for j in range(NP - 1) for i in range(NXW)]
me.from_pydata([tuple(v) for v in verts], [], faces)
me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
uvl = me.uv_layers.new(name='UV')
rug = bpy.data.objects.new('runner', me); sc.collection.objects.link(rug)
rug.data.materials.append(wool_material())
rug.data.materials.append(plain('binding', (0.12, 0.012, 0.008), 0.75))
so = rug.modifiers.new('thick', 'SOLIDIFY'); so.thickness = TH; so.offset = 0
so.material_offset_rim = 1; so.use_even_offset = True
loop_vi = np.zeros(len(me.loops), int); me.loops.foreach_get('vertex_index', loop_vi)
# enrollado: fijo por vértice (las muestras de la espiral son siempre las mismas)
ramp_ = np.clip((np.arange(NP) - nf + 2) / 4, 0, 1)
at_ = me.attributes.new('enrollado', 'FLOAT', 'POINT')
at_.data.foreach_set('value', np.repeat(ramp_, NXW + 1))

def set_runner(yr):
    y, z, u = path(yr)
    X = np.tile(xs, NP); Y = np.repeat(y, NXW + 1); Z = np.repeat(z, NXW + 1)
    me.vertices.foreach_set('co', np.column_stack([X, Y, Z]).reshape(-1))
    # El texto avanza hacia +y con el alto de las letras hacia -x: en la cámara
    # ancha se lee derecho, de izquierda a derecha. (Girarlo 180° lo pone del
    # revés en la ancha; en la vertical cualquiera de las dos es lectura vertical.)
    U = np.repeat(u / P, NXW + 1)
    V = np.tile((WD / 2 - xs) / WD, NP)          # así el wordmark no sale en espejo
    uv = np.column_stack([U[loop_vi], V[loop_vi]])
    uvl.data.foreach_set('uv', uv.reshape(-1))
    me.update()

# ---------------------------------------------------------------- suelo, luces, cámara
# Todo va colgado de un «carro» que avanza con el rollo. El suelo es liso y
# sin textura: moverlo con el carro no se nota.
rig = bpy.data.objects.new('rig', None); sc.collection.objects.link(rig)

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
fl = bpy.context.object; fl.scale = (60, 60, 1); fl.parent = rig
fm = bpy.data.materials.new('floor'); fm.use_nodes = True
fp = next(n for n in fm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
fp.inputs['Base Color'].default_value = (0.006, 0.005, 0.005, 1)
fp.inputs['Roughness'].default_value = 0.55
fl.data.materials.append(fm)

def light(name, kind, loc, energy, color, target=(0, 0, 0), size=1.0, spot=None):
    l = bpy.data.lights.new(name, kind); l.energy = energy; l.color = color
    if kind == 'AREA':
        l.size = size
    if kind == 'SPOT':
        l.spot_size = math.radians(spot or 40); l.spot_blend = 0.6; l.shadow_soft_size = size
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc; o.parent = rig
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

# cenital cálido sobre el rollo, contra rosa por detrás, relleno rojo bajo
light('key', 'SPOT', (1.6, -1.8, 3.4), 1400, (1.0, 0.82, 0.66), target=(0, 0.4, 0.1), size=0.6, spot=48)
light('rimPink', 'AREA', (-1.6, 3.2, 2.6), 90, (1.0, 0.3, 0.35), target=(0, 0, 0.2), size=1.2)
light('rimOrange', 'AREA', (2.6, 2.4, 0.9), 90, (1.0, 0.55, 0.3), target=(0, 0, 0.2), size=2.0)
# (sin foco al fondo: hacía un disco naranja que parecía un halo)
light('fill', 'AREA', (0.5, -3.5, 1.0), 25, (1.0, 0.75, 0.6), target=(0, 0, 0.2), size=3.0)

cam_d = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.parent = rig
if VIEW == 'narrow':
    loc, tgt, lens = Vector((1.15, -2.6, 2.2)), Vector((0.05, 1.3, -0.2)), 28
else:
    loc, tgt, lens = Vector((2.3, -2.2, 1.35)), Vector((-0.9, -0.2, 0.1)), 30
vec = lambda k: Vector(tuple(map(float, os.environ[k].split(','))))
if 'CAM' in os.environ: loc = vec('CAM')
if 'TGT' in os.environ: tgt = vec('TGT')
if 'LENS' in os.environ: lens = float(os.environ['LENS'])
cam.location = loc; cam_d.lens = lens
cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (Vector((0, 0, R0)) - loc).length
cam_d.dof.aperture_fstop = 4.0
cam_d.clip_end = 200

# ---------------------------------------------------------------- fotogramas
if '-' in FR:
    rng_, _, step = FR.partition(':')
    a, b = map(int, rng_.split('-'))
    frames = list(range(a, b + 1, int(step or 1)))
else:
    frames = [int(FR)]

for f in frames:
    # el rollo viene hacia la cámara: el contacto baja en y
    yr = -P * (f % LOOP) / LOOP
    rig.location = (0, yr, 0)
    set_runner(yr)
    sc.frame_set(f)
    sc.render.filepath = os.path.join(OUT, f'{VIEW}_{f:04d}.png')
    if os.environ.get('SKIP') and os.path.exists(sc.render.filepath):
        continue   # reanudar: lo ya renderizado no se repite
    if os.environ.get('DRY'):
        print('DRY', f, flush=True); continue
    bpy.ops.render.render(write_still=True)
    print('FRAME', f, flush=True)
