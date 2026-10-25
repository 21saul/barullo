"""Serie MEDALLONES: un medallón «o» del catálogo de estilos girando despacio en bucle de 8 s.

Mismas luces, HDRI y materiales que bocetos/scripts/medal.py (los estilos de bocetos/disenos/logo/estilos/),
pero con la medalla de dos caras de comun/medalla_lib.py: la trasera es el espejo de la delantera,
así que medio giro (180°) cierra el bucle. El giro va lento de cara y más rápido de canto.
Los contraluces se tiñen con el color de fondo de cada flyer para que el metal "pertenezca" a él,
y una barra de luz cruza la cara dos veces por bucle (el brillo).

Escribe m_####.png (RGBA, fondo transparente) y pts_F0-F1.json con la posición en pantalla
de la gema y de las 8 puntas por frame (destellos en Remotion).

  blender.exe -b --factory-startup --python medallon_anim.py -- <logo-alfombra dir> <estilo> <out dir> <a-b[:step]> [samples=32] [res=1400]
"""
import bpy, json, math, os, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

_A = sys.argv[sys.argv.index('--') + 1:]
D, STYLE, OUTD = _A[0], _A[1], _A[2]
_fr = (_A[3] if len(_A) > 3 else '0-239').split(':')
F0, F1 = (int(x) for x in _fr[0].split('-'))
STEP = int(_fr[1]) if len(_fr) > 1 else 1
SAMPLES = int(_A[4]) if len(_A) > 4 else 32
RES = int(_A[5]) if len(_A) > 5 else 1400
LOOP = 240  # 8 s a 30 fps = medio giro
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'comun'))
from medalla_lib import Medal, estilo  # noqa: E402

# contraluces por flyer: (rim A, rim B), el color del fondo de cada cartel
RIMS = {
    'oro-turquesa': ((0.1, 0.85, 0.8), (1.0, 0.55, 0.15)),
    'oro-perlas': ((0.15, 0.75, 0.9), (1.0, 0.35, 0.6)),
    'oro-girih-rubi': ((1.0, 0.08, 0.06), (1.0, 0.5, 0.12)),
    'oro-esmeralda': ((0.1, 0.9, 0.45), (1.0, 0.6, 0.2)),
    'oro-rosa-coral': ((1.0, 0.25, 0.6), (1.0, 0.5, 0.2)),
}
rimA, rimB = RIMS.get(STYLE, ((1, 0.22, 0.55), (1, 0.5, 0.12)))

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
sc.cycles.max_bounces = 8; sc.cycles.transmission_bounces = 8; sc.cycles.glossy_bounces = 6
sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.film_transparent = True
sc.render.image_settings.color_mode = 'RGBA'
sc.render.fps = 30
sc.render.use_persistent_data = True  # BVH y texturas se reutilizan entre frames
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'


def world():
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, 0.6)
    env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(D, 'hdri', 'studio_small_09.hdr'))
    b1 = nt.nodes.new('ShaderNodeBackground'); b1.inputs[1].default_value = 0.9
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], b1.inputs['Color']); nt.links.new(b1.outputs[0], out.inputs[0])


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; nt = m.node_tree
    [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False
    return o, em


world()
root = bpy.data.objects.new('root', None); sc.collection.objects.link(root)
root.rotation_euler = (math.radians(83), 0, math.radians(-14))
spin = bpy.data.objects.new('spin', None); sc.collection.objects.link(spin); spin.parent = root
med = Medal(os.path.join(D, 'tex', 'medal'))
st = estilo(STYLE, os.path.join(D, 'estilos.json'))
s, gem, gem_r = med.build_style(st, spin)

c = bpy.data.cameras.new('cam'); c.lens = 104  # margen para las puntas durante el giro
cam = bpy.data.objects.new('cam', c); sc.collection.objects.link(cam); cam.location = (0.8, -9.5, 1.2)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam

# luces de medal.py, con los contraluces del color del flyer
softbox((0, -9, 5), (12, 2.4), 2.4)
softbox((0, -9, -4), (12, 1.2), 1.0, (1, 0.85, 0.75))
softbox((-7, -5, 0.5), (1.0, 6), 1.6, (1, 0.6, 0.25))
area('key', (-3, -6, 5), 4, 700)
area('rimA', (4, 3, 2), 2.5, 1500, rimA)
area('rimB', (-4, 3, -1), 2.5, 1000, rimB)
area('rimA2', (5, -3, -3), 3, 700, rimA)
# barra de brillo: cruza por delante de la cara (invisible a cámara)
sweep, sweep_em = softbox((0, -8, 1.5), (0.3, 9), 0.0, (1, 0.97, 0.9))


def ease(u):
    """cúbica in-out"""
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def pose(f):
    """Medio giro por bucle, lento de cara y más rápido de canto (derivada continua: bucle sin salto)."""
    t = (f % LOOP) / LOOP
    turn = math.pi * (t - 0.62 * math.sin(2 * math.pi * t) / (2 * math.pi))
    tilt = math.radians(4) * math.sin(2 * math.pi * t + 1.3)
    sway = math.radians(3) * math.sin(4 * math.pi * t)
    bob = 0.05 * math.sin(2 * math.pi * t + 0.4)
    return turn, tilt, sway, bob


def sweep_at(f):
    """Dos pasadas por bucle, cuando la medalla está casi de cara. Devuelve (x, intensidad)."""
    t = (f % LOOP) / LOOP
    for a in (0.86, 0.36):  # empieza antes de llegar de cara
        u = ((t - a) % 1.0) / 0.26
        if u <= 1:
            return -7 + 14 * ease(u), 2.5 * math.sin(math.pi * u) ** 2
    return 0, 0.0


# 8 puntas de la estrella (para los destellos): el vértice más alejado del centro en cada sector de 45°
fr = med.fr
tips = {}
for (x, y) in fr['outer'][:-1]:
    px, py = (x - fr['cx']) * med.S2, -(y - fr['cy']) * med.S2
    k = int(((math.atan2(py, px) + math.pi / 8) % (2 * math.pi)) // (math.pi / 4))
    if k not in tips or px * px + py * py > tips[k][0] ** 2 + tips[k][1] ** 2:
        tips[k] = (px, py)
tips = [tips[k] for k in sorted(tips)]

pts = {}
os.makedirs(OUTD, exist_ok=True)
for f in range(F0, F1 + 1, STEP):
    turn, tilt, sway, bob = pose(f)
    spin.rotation_euler = (tilt, turn, sway)
    root.location = (0, 0, bob)
    sx, se = sweep_at(f)
    sweep.location.x = sx; sweep_em.inputs[1].default_value = se
    bpy.context.view_layer.update()
    n = (s.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    to_cam = (cam.location - s.matrix_world.translation).normalized()
    facing = n.dot(to_cam)
    zt = math.copysign(med.SIZE / 3 * 0.04 + gem_r * 0.62, facing)
    def scr(v):
        p = world_to_camera_view(sc, cam, s.matrix_world @ Vector(v))
        return [round(p.x, 4), round(1 - p.y, 4)]
    pts[f] = dict(gem=scr((0, 0, zt)), tips=[scr((x, y, 0)) for x, y in tips], vis=round(abs(facing), 4),
                  sweep=round(se / 2.5, 3))
    sc.render.filepath = os.path.join(OUTD, f'm_{f:04d}.png')
    if not os.environ.get('NORENDER') and not os.path.exists(sc.render.filepath):
        bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)

gp = os.path.join(OUTD, f'pts_{F0:04d}-{F1:04d}.json')
json.dump(pts, open(gp, 'w'))
print('DONE', gp)
