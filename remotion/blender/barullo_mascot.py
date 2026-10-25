"""
Mascota de Barullo v2 en Blender (EEVEE): escena, materiales y animación.

Uso (desde WSL, Blender de Windows en segundo plano):
  blender.exe -b --factory-startup --python barullo_mascot.py -- \
      --out C:/ruta/frames/ --variant square|wide [--frames 1-240] [--save escena.blend]

Todo cuelga de una fase t = (frame-1)/240 y de funciones periódicas, así que el
fotograma 241 sería idéntico al 1: el vídeo hace bucle sin costura.
Unidades: la cabeza es una esfera de radio 1 en el origen, mirando a -Y.
"""

import argparse
import math
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

FPS = 30
FRAMES = 240  # 8 s
BEATS = 16  # 120 BPM
WEB_BLACK = 5 / 255  # #050505 en sRGB


# ---------------------------------------------------------------- utilidades

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h, a=1.0):
    h = h.lstrip('#')
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


def wrap(x):
    """Distancia periódica en [-0.5, 0.5)."""
    return (x + 0.5) % 1.0 - 0.5


def kick(phase, at=0.0, width=0.1):
    """Pulso gaussiano periódico centrado en `at` (fase 0..1)."""
    return math.exp(-(wrap(phase - at) / width) ** 2)


def link(obj, parent=None):
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def empty(name, parent=None, loc=(0, 0, 0), rot=None):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.2
    o.location = loc
    if rot is not None:
        o.rotation_mode = 'QUATERNION'
        o.rotation_quaternion = rot
    return link(o, parent)


def mesh_obj(name, bm, mat, parent=None, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), parent)


def sphere(name, mat, parent=None, loc=(0, 0, 0), scale=(1, 1, 1), seg=64, rings=32):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1)
    o = mesh_obj(name, bm, mat, parent)
    o.location = loc
    o.scale = scale
    return o


def cone(name, mat, length, radius, parent=None, seg=48):
    """Cono con la base en el origen y la punta en +Z."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=0.0, depth=length)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, length / 2))
    return mesh_obj(name, bm, mat, parent)


def cylinder(name, mat, radius, depth, parent=None, seg=96):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    return mesh_obj(name, bm, mat, parent)


def torus(name, mat, R, r, parent=None, arc=2 * math.pi, seg=128, tube_seg=24):
    """Toro en el plano XY (eje Z). `arc` < 2π da un arco abierto desde +X."""
    closed = arc >= 2 * math.pi - 1e-6
    n = seg if closed else seg + 1
    bm = bmesh.new()
    rings = []
    for i in range(n):
        a = arc * i / seg
        c = Vector((math.cos(a), math.sin(a), 0))
        ring = []
        for j in range(tube_seg):
            b = 2 * math.pi * j / tube_seg
            p = c * (R + r * math.cos(b)) + Vector((0, 0, r * math.sin(b)))
            ring.append(bm.verts.new(p))
        rings.append(ring)
    pairs = range(n) if closed else range(n - 1)
    for i in pairs:
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(tube_seg):
            k = (j + 1) % tube_seg
            bm.faces.new((a[j], b[j], b[k], a[k]))
    if not closed:
        for ring in (rings[0], rings[-1]):
            bm.faces.new(ring)
    bm.normal_update()
    return mesh_obj(name, bm, mat, parent)


def star4(name, mat, size, parent=None, thick=0.22):
    """Destello de 4 puntas facetado (bipirámide), como los brillos de las refs."""
    bm = bmesh.new()
    ring = []
    for i in range(8):
        a = i * math.pi / 4
        r = 1.0 if i % 2 == 0 else 0.26
        ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), 0)))
    top = bm.verts.new((0, 0, thick))
    bot = bm.verts.new((0, 0, -thick))
    for i in range(8):
        a, b = ring[i], ring[(i + 1) % 8]
        bm.faces.new((a, b, top))
        bm.faces.new((b, a, bot))
    bm.normal_update()
    o = mesh_obj(name, bm, mat, parent, smooth=False)
    o.scale = (size, size, size)
    return o


def rounded_box(name, mat, dims, parent=None, bevel=0.3):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    o = mesh_obj(name, bm, mat, parent)
    o.scale = dims
    m = o.modifiers.new('bevel', 'BEVEL')
    m.width = bevel
    m.segments = 5
    m.use_clamp_overlap = True
    m.limit_method = 'NONE'
    return o


def surf(x, z, r=1.0):
    """Punto de la cara (hemisferio -Y) de la esfera de radio r."""
    y = -math.sqrt(max(0.0, 1 - x * x - z * z))
    return Vector((x, y, z)) * r


def facing(n, roll=0.0):
    """Cuaternión: Z local a lo largo de la normal n, Y local hacia arriba, + giro."""
    q = n.normalized().to_track_quat('Z', 'Y')
    return q @ Quaternion((0, 0, 1), roll)


def along(d):
    return Vector(d).normalized().to_track_quat('Z', 'Y')


# ---------------------------------------------------------------- materiales

def principled(name, base, metal=0.0, rough=0.2, coat=0.0, coat_rough=0.03, emit=None, emit_strength=0.0,
               transmission=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = base
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = coat_rough
    p.inputs['IOR'].default_value = ior
    if transmission:
        p.inputs['Transmission Weight'].default_value = transmission
        for attr, val in (('use_raytrace_refraction', True), ('surface_render_method', 'DITHERED')):
            if hasattr(m, attr):
                setattr(m, attr, val)
    if emit is not None:
        p.inputs['Emission Color'].default_value = emit
        p.inputs['Emission Strength'].default_value = emit_strength
    return m


def materials():
    return {
        # Laca negra con un punto metálico: negro profundo que se llena de reflejos.
        'black': principled('M_black_lacquer', hex_lin('#050506'), metal=0.55, rough=0.14, coat=1.0),
        'chrome': principled('M_chrome', hex_lin('#F2F3F7'), metal=1.0, rough=0.09),
        'red': principled('M_red_lacquer', hex_lin('#C40A22'), rough=0.22, coat=1.0, coat_rough=0.02),
        'mouth': principled('M_mouth', hex_lin('#1A0205'), rough=0.35, coat=0.6),
        'eye': principled('M_eye_white', hex_lin('#F4F2F6'), rough=0.25, coat=1.0),
        'pupil': principled('M_pupil', hex_lin('#020203'), rough=0.08, coat=1.0),
        'glint': principled('M_glint', hex_lin('#FFFFFF'), emit=hex_lin('#FFFFFF'), emit_strength=6.0),
        'glass': principled('M_droplet', hex_lin('#FFFFFF'), rough=0.0, transmission=1.0, ior=1.33),
    }


# ---------------------------------------------------------------- mundo / estudio

def build_world():
    """
    Estudio procedural dentro del propio mundo (sin HDRI, funciona offline):
    la cámara ve #050505 plano; los reflejos ven softbox cenital, dos tiras de
    contraluz, un barrido vertical que da la vuelta en cada bucle y un brillo rojo.
    """
    w = bpy.data.worlds.new('W_barullo_studio')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    N = nt.nodes
    L = nt.links
    N.clear()

    out = N.new('ShaderNodeOutputWorld')
    coord = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(coord.outputs['Generated'], sep.inputs[0])

    rot = N.new('ShaderNodeVectorRotate')
    rot.name = 'SWEEP'
    rot.rotation_type = 'Z_AXIS'
    L.new(coord.outputs['Generated'], rot.inputs['Vector'])
    sep_r = N.new('ShaderNodeSeparateXYZ')
    L.new(rot.outputs[0], sep_r.inputs[0])

    def mr(sock, a, b):
        n = N.new('ShaderNodeMapRange')
        n.interpolation_type = 'SMOOTHSTEP'
        n.inputs['From Min'].default_value = a
        n.inputs['From Max'].default_value = b
        L.new(sock, n.inputs['Value'])
        return n.outputs['Result']

    def mul(a, b):
        n = N.new('ShaderNodeMath')
        n.operation = 'MULTIPLY'
        L.new(a, n.inputs[0])
        if isinstance(b, (int, float)):
            n.inputs[1].default_value = b
        else:
            L.new(b, n.inputs[1])
        return n.outputs[0]

    def band(sock, lo, hi, soft):
        return mul(mr(sock, lo - soft, lo + soft), mr(sock, hi + soft, hi - soft))

    def dot_mask(direction, cos_lo, cos_hi):
        d = N.new('ShaderNodeVectorMath')
        d.operation = 'DOT_PRODUCT'
        L.new(coord.outputs['Generated'], d.inputs[0])
        d.inputs[1].default_value = Vector(direction).normalized()
        return mr(d.outputs['Value'], cos_lo, cos_hi)

    X, Y, Z = sep.outputs
    Xr, Yr, Zr = sep_r.outputs
    lights = [
        (mr(Z, 0.62, 0.8), hex_lin('#FFFFFF'), 3.2),  # softbox cenital
        (mul(mul(mr(X, -0.72, -0.86), band(Z, -0.25, 0.75, 0.06)), mr(Y, -0.4, -0.1)), hex_lin('#DDE8FF'), 5.0),  # rim izq
        (mul(mul(mr(X, 0.72, 0.86), band(Z, -0.25, 0.75, 0.06)), mr(Y, -0.4, -0.1)), hex_lin('#DDE8FF'), 5.0),  # rim der
        (mul(mul(band(Xr, -0.07, 0.07, 0.025), mr(Yr, -0.2, -0.45)), band(Zr, -0.55, 0.85, 0.08)), hex_lin('#FFFFFF'), 7.0),  # barrido
        (dot_mask((-0.5, 0.82, -0.3), 0.9, 0.97), hex_lin('#FF2140'), 6.0),  # brillo rojo bajo
        (dot_mask((0.7, -0.6, 0.15), 0.94, 0.985), hex_lin('#FFFFFF'), 4.0),  # ventana frontal derecha
        (dot_mask((0.0, -1.0, 0.25), 0.7, 0.95), hex_lin('#FFFFFF'), 0.7),  # relleno frontal suave (grillz)
    ]
    acc = None
    for mask, col, strength in lights:
        rgb = N.new('ShaderNodeMix')
        rgb.data_type = 'RGBA'
        rgb.blend_type = 'MULTIPLY'
        rgb.inputs['Factor'].default_value = 1.0
        rgb.inputs[6].default_value = (1, 1, 1, 1)
        rgb.inputs[7].default_value = tuple(c * strength for c in col[:3]) + (1,)
        sc = N.new('ShaderNodeVectorMath')
        sc.operation = 'SCALE'
        L.new(rgb.outputs[2], sc.inputs[0])
        L.new(mask, sc.inputs['Scale'])
        if acc is None:
            acc = sc.outputs[0]
        else:
            add = N.new('ShaderNodeVectorMath')
            add.operation = 'ADD'
            L.new(acc, add.inputs[0])
            L.new(sc.outputs[0], add.inputs[1])
            acc = add.outputs[0]
    base = N.new('ShaderNodeVectorMath')
    base.operation = 'ADD'
    base.inputs[1].default_value = (0.012, 0.012, 0.014)
    L.new(acc, base.inputs[0])

    studio = N.new('ShaderNodeBackground')
    L.new(base.outputs[0], studio.inputs['Color'])
    flat = N.new('ShaderNodeBackground')
    flat.inputs['Color'].default_value = (srgb_to_linear(WEB_BLACK),) * 3 + (1,)
    path = N.new('ShaderNodeLightPath')
    mix = N.new('ShaderNodeMixShader')
    L.new(path.outputs['Is Camera Ray'], mix.inputs['Fac'])
    L.new(studio.outputs[0], mix.inputs[1])
    L.new(flat.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return rot


def area(name, loc, target, energy, size, color):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.size = size
    d.color = hex_lin(color)[:3]
    d.shape = 'DISK'
    d.specular_factor = 0.35
    o = link(bpy.data.objects.new(name, d))
    o.location = loc
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = (Vector(loc) - Vector(target)).to_track_quat('Z', 'Y')
    return o


def build_lights():
    area('LGT-key', (-3.5, -5.0, 4.5), (0, 0, 0.2), 900, 1.6, '#FFFFFF')
    area('LGT-fill', (4.5, -3.5, -0.5), (0, 0, 0), 180, 4.0, '#DDE8FF')
    area('LGT-rim_cool', (-4.0, 4.0, 2.5), (0, 0, 0.3), 1100, 1.5, '#DDE8FF')
    area('LGT-rim_red', (4.2, 3.5, 0.5), (0, 0, 0.0), 1400, 1.5, '#FF2140')


# ---------------------------------------------------------------- personaje

def build_mascot(M):
    root = empty('MASCOT')
    head = sphere('GEO-head', M['black'], root, seg=128, rings=64)
    head.scale = (1.0, 0.98, 0.97)

    # Corona de pinchos (ref poiandkeely): abanico radial en dos filas, delante y detrás.
    spikes = []
    for row, (tilt, count, lens) in enumerate(((-0.14, 9, (0.62, 1.1)), (0.42, 8, (0.5, 0.8)))):
        for i in range(count):
            u = i / (count - 1)
            a = math.radians(-82 + 164 * u)  # ángulo en el plano frontal, 0 = arriba
            d = Vector((math.sin(a), tilt, math.cos(a))).normalized()
            mid = 1 - abs(2 * u - 1)
            length = lens[0] + (lens[1] - lens[0]) * mid
            piv = empty(f'SPK-{row}-{i}', root, loc=d * 0.84, rot=along(d))
            c = cone(f'GEO-spike-{row}-{i}', M['chrome'], length, 0.12 + 0.03 * mid, piv)
            spikes.append((piv, row * 0.5 + u * 0.4))
    # Pinchos traseros sueltos para que la silueta no quede plana en el giro.
    for i, d in enumerate(((0.0, 0.95, 0.3), (-0.7, 0.7, -0.15), (0.7, 0.7, -0.15), (0.0, 0.6, -0.8))):
        d = Vector(d).normalized()
        piv = empty(f'SPK-back-{i}', root, loc=d * 0.9, rot=along(d))
        cone(f'GEO-spike-back-{i}', M['chrome'], 0.6, 0.12, piv)
        spikes.append((piv, 0.9 + i * 0.05))

    # Ojos: blanco lacado, párpado negro a media asta, pupila de reojo y pestañas-cuchilla.
    eyes = []
    for s in (-1, 1):
        x, z = 0.36 * s, 0.1
        n = surf(x, z)
        e = empty(f'EYE-{"L" if s < 0 else "R"}', root, loc=surf(x, z, 0.975), rot=facing(n, roll=0.28 * s))
        sphere(f'GEO-eye-{s}', M['eye'], e, scale=(0.2, 0.11, 0.065))
        pupil = empty(f'PUP-{s}', e)
        sphere(f'GEO-pupil-{s}', M['pupil'], pupil, loc=(0, -0.035, 0.05), scale=(0.062, 0.062, 0.03))
        sphere(f'GEO-glint-{s}', M['glint'], pupil, loc=(0.02, -0.015, 0.078), scale=(0.014, 0.014, 0.006), seg=16, rings=8)
        lid = empty(f'LID-{s}', e)
        sphere(f'GEO-lid-{s}', M['black'], lid, scale=(0.21, 0.122, 0.078))
        for j, (dx, dy, ln) in enumerate(((1.0, 0.35, 0.44), (0.85, 0.9, 0.36), (0.35, 1.0, 0.26))):
            base = Vector((0.13 * s, 0.07, 0.06))
            lash = empty(f'LASH-{s}-{j}', lid, loc=base, rot=along((dx * s, dy, 0.25)))
            c = cone(f'GEO-lash-{s}-{j}', M['chrome'], ln, 0.045, lash, seg=32)
            c.scale = (1.0, 0.32, 1.0)  # aplanado: cuchilla, no púa
        eyes.append((pupil, lid))

    # Boca ladeada: interior oscuro, labios rojos lacados y grillz cromado.
    def smile_z(x):
        return -0.42 + 0.13 * ((x - 0.03) / 0.34) ** 2 + 0.07 * x

    xs = [-0.3 + 0.66 * i / 24 for i in range(25)]

    def curve(name, mat, dz, r_surf, bevel, taper):
        cu = bpy.data.curves.new(name, 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = bevel
        cu.bevel_resolution = 6
        cu.use_fill_caps = True
        sp = cu.splines.new('POLY')
        sp.points.add(len(xs) - 1)
        for k, x in enumerate(xs):
            p = surf(x, smile_z(x) + dz, r_surf)
            u = k / (len(xs) - 1)
            sp.points[k].co = (*p, 1)
            sp.points[k].radius = (1 - taper) + taper * math.sin(math.pi * u) ** 0.6
        cu.materials.append(mat)
        return link(bpy.data.objects.new(name, cu), root)

    curve('GEO-mouth', M['mouth'], 0.0, 0.95, 0.092, 0.5)
    curve('GEO-lip_up', M['red'], 0.088, 1.0, 0.036, 0.85)
    curve('GEO-lip_low', M['red'], -0.092, 1.0, 0.042, 0.85)
    for k in range(6):
        x = -0.15 + 0.4 * k / 5
        p = surf(x, smile_z(x) + 0.004, 1.03)
        t = empty(f'TOOTH-{k}', root, loc=p, rot=facing(p))
        rounded_box(f'GEO-tooth-{k}', M['chrome'], (0.072, 0.13, 0.05), t, bevel=0.3)

    # Piercings: aro en el labio, puntitos bajo el ojo izquierdo, estrella en la mejilla.
    p = surf(0.27, smile_z(0.27) - 0.13, 1.03)
    ring = empty('PIERCE-lip', root, loc=p, rot=facing(p) @ Quaternion((1, 0, 0), math.pi / 2))
    torus('GEO-lip_ring', M['chrome'], 0.055, 0.012, ring, seg=48, tube_seg=12)
    for k, (x, z, r) in enumerate(((-0.52, -0.1, 0.028), (-0.45, -0.17, 0.022), (-0.56, -0.2, 0.018))):
        sphere(f'GEO-dot-{k}', M['chrome'], root, loc=surf(x, z, 1.005), scale=(r, r, r), seg=24, rings=12)
    p = surf(0.6, -0.16, 1.01)
    st = empty('PIERCE-star', root, loc=p, rot=facing(p))
    star4('GEO-cheek_star', M['chrome'], 0.09, st, thick=0.3)

    # Gotas de cristal sobre la laca (refs de gotas sobre la piel).
    for k, (x, z, r) in enumerate(((-0.18, 0.5, 0.05), (0.22, 0.62, 0.04), (0.55, 0.32, 0.035), (-0.62, 0.36, 0.04),
                                   (0.05, 0.38, 0.028), (-0.3, -0.62, 0.032))):
        p = surf(x, z, 1.0)
        d = empty(f'DROP-{k}', root, loc=p, rot=facing(p))
        sphere(f'GEO-drop-{k}', M['glass'], d, scale=(r, r * 1.15, r * 0.6), seg=32, rings=16)

    # Cascos de DJ: diadema roja + raíl cromado, copas lacadas con pinchos.
    band_parent = empty('PHONES', root, rot=Quaternion((1, 0, 0), math.pi / 2))
    band_parent.location = (0, 0.12, 0)
    torus('GEO-band', M['red'], 1.17, 0.07, band_parent, arc=math.pi)
    torus('GEO-band_rail', M['chrome'], 1.25, 0.025, band_parent, arc=math.pi)
    for i in range(7):
        a = 0.35 + i * (math.pi - 0.7) / 6
        d = Vector((math.cos(a), math.sin(a), 0))
        piv = empty(f'BANDSPK-{i}', band_parent, loc=d * 1.26, rot=along(d))
        cone(f'GEO-bandspike-{i}', M['chrome'], 0.2, 0.045, piv, seg=24)
    cups = []
    for s in (-1, 1):
        cup = empty(f'CUP-{s}', root, loc=(1.04 * s, 0.1, -0.02), rot=along((s, 0, 0)))
        body = cylinder(f'GEO-cup-{s}', M['red'], 0.48, 0.34, cup)
        bev = body.modifiers.new('bevel', 'BEVEL')
        bev.width = 0.1
        bev.segments = 8
        bev.limit_method = 'ANGLE'
        rim = torus(f'GEO-cup_rim-{s}', M['chrome'], 0.43, 0.035, cup)
        rim.location = (0, 0, 0.17)
        cone(f'GEO-cup_cone-{s}', M['chrome'], 0.34, 0.1, cup).location = (0, 0, 0.17)
        for k in range(8):
            a = k * math.pi / 4 + math.pi / 8
            d = Vector((math.cos(a), math.sin(a), 0))
            piv = empty(f'CUPSPK-{s}-{k}', cup, loc=d * 0.5, rot=along(d))
            cone(f'GEO-cupspike-{s}-{k}', M['chrome'], 0.17, 0.045, piv, seg=24)
        cups.append(cup)

    # Estrellas cromadas en órbita: pasan por detrás de la cabeza y dan profundidad.
    stars = []
    for k, (radius, height, size, phase) in enumerate(((1.75, 1.05, 0.16, 0.0), (1.7, -0.75, 0.13, 0.3),
                                                       (1.8, 0.2, 0.1, 0.55), (1.6, 1.55, 0.09, 0.78))):
        o = star4(f'GEO-star-{k}', M['chrome'], size)
        o.rotation_mode = 'XYZ'
        stars.append((o, radius, height, phase))

    return root, spikes, eyes, cups, stars


# ---------------------------------------------------------------- animación

def animate(root, spikes, eyes, cups, stars, sweep):
    sc = bpy.context.scene
    for f in range(1, FRAMES + 1):
        t = (f - 1) / FRAMES
        beat = (t * BEATS) % 1.0
        bar = (t * BEATS / 4) % 1.0
        nod = kick(beat, 0.1, 0.13)  # cabeceo de DJ justo después de cada golpe

        root.rotation_mode = 'XYZ'
        root.rotation_euler = (0.07 * nod - 0.02, 0.05 * math.sin(4 * math.pi * t), 0.3 * math.sin(2 * math.pi * t))
        root.location = (0, 0, -0.045 * nod)
        root.scale = (1 + 0.012 * nod, 1 + 0.012 * nod, 1 - 0.02 * nod)
        root.keyframe_insert('rotation_euler', frame=f)
        root.keyframe_insert('location', frame=f)
        root.keyframe_insert('scale', frame=f)

        # Onda por la corona en cada compás: cada pincho estira con un poco de retraso.
        for piv, delay in spikes:
            k = kick(bar, 0.05 + delay * 0.12, 0.06)
            piv.scale = (1 - 0.08 * k, 1 - 0.08 * k, 1 + 0.2 * k)
            piv.keyframe_insert('scale', frame=f)

        # Mirada de reojo hacia donde gira la cabeza, y dos parpadeos por bucle.
        look = math.tanh(3.0 * math.sin(2 * math.pi * (t - 0.04)))
        blink = max(kick(t, 0.31, 0.012), kick(t, 0.83, 0.012), kick(t, 0.86, 0.01))
        for pupil, lid in eyes:
            pupil.location = (0.07 * look, 0, 0)
            pupil.keyframe_insert('location', frame=f)
            lid.location = (0, 0.12 - 0.14 * blink, 0)
            lid.keyframe_insert('location', frame=f)

        for cup in cups:
            p = 1 + 0.07 * kick(beat, 0.04, 0.09)
            cup.scale = (p, p, 1 + 0.12 * kick(beat, 0.04, 0.09))
            cup.keyframe_insert('scale', frame=f)

        for o, radius, height, phase in stars:
            a = 2 * math.pi * (t + phase)
            o.location = (radius * math.sin(a), radius * 0.55 * math.cos(a), height + 0.12 * math.sin(4 * math.pi * (t + phase)))
            o.rotation_euler = (math.pi / 2, 0, 2 * math.pi * 2 * t)  # 2 vueltas por bucle (simetría de 4 → cierra)
            o.keyframe_insert('location', frame=f)
            o.keyframe_insert('rotation_euler', frame=f)

        sweep.inputs['Angle'].default_value = 2 * math.pi * t + 0.6
        sweep.inputs['Angle'].keyframe_insert('default_value', frame=f)
    sc.frame_set(1)


# ---------------------------------------------------------------- render

def setup_render(variant, out):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, FRAMES
    if variant == 'wide':
        sc.render.resolution_x, sc.render.resolution_y = 1920, 824
    else:
        sc.render.resolution_x, sc.render.resolution_y = 1080, 1080
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.dither_intensity = 0.0
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = out
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    ee = sc.eevee
    for attr, val in (('taa_render_samples', 48), ('use_raytracing', True), ('use_shadows', True),
                      ('use_gtao', True), ('fast_gi_method', 'GLOBAL_ILLUMINATION')):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception as e:  # noqa: BLE001
                print('eevee', attr, e)
    try:
        ee.ray_tracing_options.resolution_scale = '1'
        ee.ray_tracing_options.use_denoise = True
    except Exception as e:  # noqa: BLE001
        print('raytrace opts', e)

    cam_d = bpy.data.cameras.new('CAM-hero')
    cam_d.lens = 48
    cam_d.sensor_fit = 'VERTICAL'
    cam_d.sensor_height = 24
    cam = link(bpy.data.objects.new('CAM-hero', cam_d))
    cam.location = (0, -7.0, 0.42)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = cam


def setup_glare():
    """Destellos en los picos del cromo (compositor). Si la API cambia, se omite."""
    sc = bpy.context.scene
    try:
        tree = bpy.data.node_groups.new('COMP-barullo', 'CompositorNodeTree')
        sc.compositing_node_group = tree
        tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = tree.nodes.new('CompositorNodeRLayers')
        gl = tree.nodes.new('CompositorNodeGlare')
        out = tree.nodes.new('NodeGroupOutput')
        for key, val in (('Type', 'Streaks'), ('Quality', 'High'), ('Threshold', 6.0), ('Strength', 0.12),
                         ('Streaks', 4), ('Streaks Angle', math.radians(45)), ('Fade', 0.86)):
            if key in gl.inputs:
                try:
                    gl.inputs[key].default_value = val
                except Exception as e:  # noqa: BLE001
                    print('glare', key, e)
        tree.links.new(rl.outputs['Image'], gl.inputs['Image'])
        tree.links.new(gl.outputs['Image'], out.inputs[0])
        print('glare: ok')
    except Exception as e:  # noqa: BLE001
        print('glare: omitido ->', e)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='//frames/')
    ap.add_argument('--variant', default='square', choices=('square', 'wide'))
    ap.add_argument('--frames', default='')
    ap.add_argument('--save', default='')
    args = ap.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    sweep = build_world()
    build_lights()
    rig = build_mascot(M)
    animate(*rig, sweep)
    setup_render(args.variant, args.out)
    setup_glare()
    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=args.save)
        print('saved', args.save)
    if args.frames:
        sc = bpy.context.scene
        for part in args.frames.split(','):
            a, _, b = part.partition('-')
            for f in range(int(a), int(b or a) + 1):
                sc.frame_set(f)
                sc.render.filepath = f'{args.out}{f:04d}'
                bpy.ops.render.render(write_still=True)
                print('frame', f, flush=True)


main()
