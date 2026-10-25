"""
Mascota de Barullo v3, "cyber": busto de porcelana lila con ojos violetas que
brillan, trenzas negras, micro-piercings, cables en la boca y neón en el cuello.

Base: cabeza "head_animation_realistic" del pack oficial Human Base Meshes de
Blender (CC0). Todo lo demás (pelo, piercings, cables, neón, cascos, luz y
animación) se genera aquí.

  blender.exe -b --factory-startup --python barullo_cyber.py -- \
      --lib C:/.../human_base_meshes_bundle.blend --out C:/ruta/frames/ \
      --variant square|wide [--frames 1-240] [--save escena.blend]

Bucle perfecto de 8 s: todo depende de t = (frame-1)/240 con funciones periódicas.
"""

import argparse
import math
import random
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

FPS = 30
FRAMES = 240
BEATS = 16  # 120 BPM
WEB_BLACK = 5 / 255
HEAD = 'GEO-head_animation_realistic'


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h, a=1.0):
    h = h.lstrip('#')
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


def wrap(x):
    return (x + 0.5) % 1.0 - 0.5


def kick(phase, at=0.0, width=0.1):
    return math.exp(-(wrap(phase - at) / width) ** 2)


def link(obj, parent=None):
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
        if parent.name == HEAD:
            # Lo que cuelga de la cabeza se coloca en coordenadas de mundo.
            obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj


# ---------------------------------------------------------------- materiales

def principled(name, base, metal=0.0, rough=0.2, coat=0.0, coat_rough=0.03, emit=None, emit_strength=0.0, **extra):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = base
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = coat_rough
    if emit is not None:
        p.inputs['Emission Color'].default_value = emit
        p.inputs['Emission Strength'].default_value = emit_strength
    for k, v in extra.items():
        if k in p.inputs:
            p.inputs[k].default_value = v
    return m


def neon_material():
    """Neón blanco-violeta con un pulso que sube por el cuello (Wave con fase animable)."""
    m = bpy.data.materials.new('M_neon')
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.clear()
    out = N.new('ShaderNodeOutputMaterial')
    em = N.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = hex_lin('#E9E2FF')
    coord = N.new('ShaderNodeTexCoord')
    wave = N.new('ShaderNodeTexWave')
    wave.name = 'PULSE'
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = 1.2
    wave.inputs['Distortion'].default_value = 0.0
    L.new(coord.outputs['Object'], wave.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.8
    mr.inputs['To Max'].default_value = 5.0
    L.new(wave.outputs['Fac'], mr.inputs['Value'])
    L.new(mr.outputs['Result'], em.inputs['Strength'])
    L.new(em.outputs[0], out.inputs['Surface'])
    return m, wave


def materials():
    return {
        # Porcelana lila mojada: subsurface leve, capa de barniz y película fina iridiscente.
        'skin': principled('M_porcelain', hex_lin('#B3ADBD'), rough=0.3, coat=1.0, coat_rough=0.04,
                           **{'Subsurface Weight': 0.25, 'Subsurface Scale': 0.004,
                              'Subsurface Radius': Vector((1.0, 0.55, 0.75)),
                              'Thin Film Thickness': 420.0, 'Thin Film IOR': 1.4,
                              'Coat Tint': hex_lin('#FFFFFF')}),
        'hair': principled('M_hair', hex_lin('#050506'), rough=0.42, coat=0.25, coat_rough=0.2,
                           **{'Anisotropic': 0.6}),
        'lash': principled('M_lash', hex_lin('#3B44E0'), rough=0.3, emit=hex_lin('#6C63FF'), emit_strength=0.25),
        'sclera': principled('M_eye_glow', hex_lin('#D9CCFF'), rough=0.1, emit=hex_lin('#A88BFF'), emit_strength=4.0),
        'iris': principled('M_iris_glow', hex_lin('#FFFFFF'), rough=0.1, emit=hex_lin('#F4EEFF'), emit_strength=14.0),
        'chrome': principled('M_chrome', hex_lin('#F2F3F7'), metal=1.0, rough=0.08),
        'stud_dark': principled('M_stud_dark', hex_lin('#0B0B10'), metal=0.6, rough=0.1, coat=1.0),
        # Base del pelo mate: el brillo lo ponen las hebras de encima.
        'hair_base': principled('M_hair_base', hex_lin('#040405'), rough=0.75),
        'cable': principled('M_cable', hex_lin('#1A1A20'), metal=0.4, rough=0.25, coat=0.8),
        'red': principled('M_red_lacquer', hex_lin('#C40A22'), rough=0.22, coat=1.0, coat_rough=0.02),
        'cushion': principled('M_cushion', hex_lin('#0E0E12'), rough=0.45, coat=0.3),
    }


# ---------------------------------------------------------------- mundo / luces

def build_world():
    """Cámara: #050505 plano. Reflejos: estudio de tiras blancas y contraluz violeta."""
    w = bpy.data.worlds.new('W_cyber_studio')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    N.clear()
    out = N.new('ShaderNodeOutputWorld')
    coord = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(coord.outputs['Generated'], sep.inputs[0])

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
        L.new(b, n.inputs[1])
        return n.outputs[0]

    def band(sock, lo, hi, soft):
        return mul(mr(sock, lo - soft, lo + soft), mr(sock, hi + soft, hi - soft))

    X, Y, Z = sep.outputs
    lights = [
        (mr(Z, 0.55, 0.8), hex_lin('#FFFFFF'), 1.2),
        (mul(mul(mr(X, -0.7, -0.86), band(Z, -0.2, 0.8, 0.06)), mr(Y, -0.3, 0.0)), hex_lin('#9B7BFF'), 5.0),
        (mul(mul(mr(X, 0.7, 0.86), band(Z, -0.2, 0.8, 0.06)), mr(Y, -0.3, 0.0)), hex_lin('#E4E8FF'), 4.0),
        (mul(band(X, -0.35, 0.05, 0.05), mul(mr(Y, -0.6, -0.85), band(Z, 0.05, 0.6, 0.05))), hex_lin('#FFFFFF'), 1.6),
    ]
    acc = None
    for mask, col, strength in lights:
        sc = N.new('ShaderNodeVectorMath')
        sc.operation = 'SCALE'
        sc.inputs[0].default_value = tuple(c * strength for c in col[:3])
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
    base.inputs[1].default_value = (0.008, 0.007, 0.011)
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


def light(name, kind, loc, target, energy, color, size=0.5, spec=1.0):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = hex_lin(color)[:3]
    if kind == 'AREA':
        d.shape = 'DISK'
        d.size = size
    elif kind in ('POINT', 'SPOT'):
        d.shadow_soft_size = size
    d.specular_factor = spec
    o = link(bpy.data.objects.new(name, d))
    o.location = loc
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = (Vector(loc) - Vector(target)).to_track_quat('Z', 'Y')
    return o


# ---------------------------------------------------------------- base

def load_head(lib):
    with bpy.data.libraries.load(lib, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith(HEAD)]
    for o in dst.objects:
        link(o)
        o.hide_render = False
        o.hide_viewport = False
    head = bpy.data.objects[HEAD]
    # En el pack la cabeza está desplazada: se centra en X/Y y se apoya en z = 0.
    bpy.context.view_layer.update()
    bb = [head.matrix_world @ Vector(c) for c in head.bound_box]
    cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
    cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
    shift = Matrix.Translation(-Vector((cx, cy, min(v.z for v in bb))))
    # La geometría se lleva al origen y el objeto queda en la identidad: así el
    # pivote de los giros es la base del busto y no un punto lejano del pack.
    kids = [(c, c.matrix_world.copy()) for c in head.children]
    head.data.transform(shift @ head.matrix_world)
    head.matrix_world = Matrix.Identity(4)
    for c, cw in kids:
        c.matrix_parent_inverse = Matrix.Identity(4)
        c.matrix_world = shift @ cw
    bpy.context.view_layer.update()
    eyes = sorted((o for o in dst.objects if '.sclera.' in o.name), key=lambda o: o.matrix_world.translation.x)
    irises = {o.parent.name: o for o in dst.objects if '.iris.' in o.name}
    return head, eyes, irises


class Surface:
    """Raycasts contra la cabeza evaluada (con multires) para colocar cosas encima."""

    def __init__(self, head):
        self.head = head
        self.dg = bpy.context.evaluated_depsgraph_get()
        self.inv = head.matrix_world.inverted()

    def cast(self, origin, direction):
        o = self.inv @ Vector(origin)
        d = (self.inv.to_3x3() @ Vector(direction)).normalized()
        ok, loc, nor, _ = self.head.ray_cast(o, d, depsgraph=self.dg)
        if not ok:
            return None
        mw = self.head.matrix_world
        return mw @ loc, (mw.to_3x3() @ nor).normalized()

    def toward(self, center, direction, reach=0.4):
        d = Vector(direction).normalized()
        return self.cast(Vector(center) + d * reach, -d)

    def front(self, x, z):
        return self.cast((x, -0.5, z), (0, 1, 0))


def hair_object(name, strands, radius, mat, parent):
    """strands: lista de listas de Vector. Curvas de pelo nativas (EEVEE las pinta como hebras)."""
    strands = [s for s in strands if len(s) >= 2]
    print('HAIR', name, len(strands))
    if not strands:
        return None
    cv = bpy.data.hair_curves.new(name)
    sizes = [len(s) for s in strands]
    cv.add_curves(sizes)
    flat = [c for s in strands for p in s for c in p]
    cv.position_data.foreach_set('vector', flat)
    rad = cv.attributes.get('radius') or cv.attributes.new('radius', 'FLOAT', 'POINT')
    rvals = []
    for s in strands:
        n = len(s)
        for i in range(n):
            u = i / max(1, n - 1)
            rvals.append(radius * (1.0 - 0.75 * u))  # afinan hacia la punta
    rad.data.foreach_set('value', rvals)
    cv.materials.append(mat)
    return link(bpy.data.objects.new(name, cv), parent)


def tube(name, pts, bevel, mat, parent, radii=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
        if radii:
            sp.points[i].radius = radii[i]
    cu.materials.append(mat)
    return link(bpy.data.objects.new(name, cu), parent)


def sphere_obj(name, mat, loc, r, parent, scale=(1, 1, 1)):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.materials.append(mat)
    o = link(bpy.data.objects.new(name, me), parent)
    o.location = loc
    o.scale = (r * scale[0], r * scale[1], r * scale[2])
    return o


def torus_obj(name, mat, R, r, parent, arc=2 * math.pi, seg=96, ts=16):
    import bmesh
    closed = arc >= 2 * math.pi - 1e-6
    n = seg if closed else seg + 1
    bm = bmesh.new()
    rings = []
    for i in range(n):
        a = arc * i / seg
        c = Vector((math.cos(a), math.sin(a), 0))
        rings.append([bm.verts.new(c * (R + r * math.cos(2 * math.pi * j / ts)) + Vector((0, 0, r * math.sin(2 * math.pi * j / ts))))
                      for j in range(ts)])
    for i in (range(n) if closed else range(n - 1)):
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(ts):
            k = (j + 1) % ts
            bm.faces.new((a[j], b[j], b[k], a[k]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), parent)


def cylinder_obj(name, mat, r, depth, parent):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=64, radius1=r, radius2=r, depth=depth)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.materials.append(mat)
    o = link(bpy.data.objects.new(name, me), parent)
    b = o.modifiers.new('bevel', 'BEVEL')
    b.width = r * 0.25
    b.segments = 6
    return o


def slice_center(head, z, tol=0.004):
    """Centro y radio medio de la sección horizontal del busto a altura z."""
    me = head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    mw = head.matrix_world
    pts = [mw @ v.co for v in me.vertices]
    sl = [p for p in pts if abs(p.z - z) < tol]
    if not sl:
        return Vector((0, 0, z)), 0.06
    c = sum(sl, Vector()) / len(sl)
    c.z = z
    r = sum(((p - c).xy.length for p in sl)) / len(sl)
    return c, r


# ---------------------------------------------------------------- personaje

def build(lib, M):
    rnd = random.Random(16)
    head, eyes, irises = load_head(lib)
    head.data.materials.clear()
    head.data.materials.append(M['skin'])
    for e in eyes:
        e.data.materials.clear()
        e.data.materials.append(M['sclera'])
        ir = irises[e.name]
        ir.data.materials.clear()
        ir.data.materials.append(M['iris'])
    for mod in head.modifiers:
        if mod.type == 'MULTIRES':
            mod.levels = mod.render_levels = mod.total_levels
    head.data.shade_smooth()
    sub = head.modifiers.new('subsurf', 'SUBSURF')
    sub.levels = sub.render_levels = 2
    for e in eyes:
        e.data.shade_smooth()
    S = Surface(head)
    print('PROBE front', S.front(0.0, 0.25), 'bbox', [tuple(round(c, 3) for c in head.matrix_world @ Vector(v)) for v in (head.bound_box[0], head.bound_box[6])])

    eyeL, eyeR = eyes[0].matrix_world.translation.copy(), eyes[1].matrix_world.translation.copy()
    eye_z = (eyeL.z + eyeR.z) / 2
    eye_r = eyes[0].dimensions.x / 2
    print('LANDMARK eyes', tuple(round(c, 4) for c in eyeL), tuple(round(c, 4) for c in eyeR), 'r', round(eye_r, 4))

    # Centro del cráneo para coordenadas esféricas del pelo.
    me = head.data
    top_pts = [head.matrix_world @ v.co for v in me.vertices if (head.matrix_world @ v.co).z > eye_z + 0.04]
    C = sum(top_pts, Vector()) / len(top_pts)
    C.z = eye_z + 0.015
    C.x = 0.0
    print('LANDMARK cranium', tuple(round(c, 4) for c in C))

    def sph(theta, phi):
        """theta: azimut desde el frente (-Y) hacia +X; phi: polar desde +Z."""
        return Vector((math.sin(phi) * math.sin(theta), -math.sin(phi) * math.cos(theta), math.cos(phi)))

    def hairline(theta):
        f = math.cos(theta)  # 1 delante, -1 detrás
        return 1.5 - 0.6 * f + 0.0 * f * f

    # --- Gorro de pelo: copia de la cabeza recortada por la línea del pelo, engordada.
    cap_me = bpy.data.meshes.new_from_object(head.evaluated_get(S.dg))
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(cap_me)
    kill = []
    for v in bm.verts:
        d = (head.matrix_world @ v.co) - C
        phi = math.acos(max(-1, min(1, d.normalized().z)))
        theta = math.atan2(d.x, -d.y)
        if phi > hairline(theta):
            kill.append(v)
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(cap_me)
    bm.free()
    cap_me.materials.clear()
    cap_me.materials.append(M['hair_base'])
    cap = link(bpy.data.objects.new('GEO-hair_cap', cap_me), head)
    cap.matrix_parent_inverse = Matrix.Identity(4)  # la malla ya está en espacio local de la cabeza
    sol = cap.modifiers.new('solid', 'SOLIDIFY')
    sol.thickness = 0.0035
    sol.offset = 1.0

    # --- Mechones: salen de la raya al medio y bajan peinados hacia atrás.
    strands = []
    for i in range(2600):
        s = rnd.choice((-1, 1))
        root_theta = rnd.uniform(-0.15, 3.3)  # de la frente a la coronilla trasera
        root_phi = 0.06 + 0.03 * rnd.random()
        a_end = hairline(root_theta + s * 1.2) + rnd.uniform(-0.05, 0.12)
        pts = []
        layer = 0.004 + 0.003 * rnd.random()
        for k in range(16):
            u = k / 15
            phi = root_phi + (a_end - root_phi) * u
            theta = root_theta + s * (1.35 * math.sin(u * math.pi / 2)) + 0.35 * u * (1 if root_theta < 1.5 else 0.2)
            hit = S.toward(C, sph(theta, phi))
            if not hit:
                break
            p, n = hit
            pts.append(p + n * (layer + 0.0008 * math.sin(u * 9 + i)))
        if len(pts) > 4:
            strands.append(pts)
    hair_object('HAIR-scalp', strands, 0.00045, M['hair'], head)

    # --- Flequillo de hebras finas que cae sobre la frente y la cara (como en la ref).
    fly = []
    for i in range(18):
        theta = rnd.uniform(-0.6, 0.6)
        phi0 = hairline(theta) - 0.08
        drop = rnd.uniform(0.25, 0.75)
        lift = rnd.uniform(0.002, 0.012)
        pts = []
        for k in range(18):
            u = k / 17
            phi = phi0 + drop * u
            th = theta + 0.06 * math.sin(u * 2.3 + i) * u
            hit = S.toward(C, sph(th, phi))
            if not hit:
                break
            p, n = hit
            pts.append(p + n * (0.003 + lift * u * u))
        if len(pts) > 5:
            fly.append(pts)
    hair_object('HAIR-flyaways', fly, 0.00022, M['hair'], head)

    # --- Cejas: hebras cortas finas.
    brows = []
    for s, ec in ((-1, eyeL), (1, eyeR)):
        for i in range(90):
            u = rnd.random()
            x = ec.x + s * (-0.018 + 0.042 * u)
            z = eye_z + 0.021 + 0.007 * math.sin(math.pi * min(1, u * 1.2)) + rnd.uniform(-0.002, 0.002)
            hit = S.front(x, z)
            if not hit:
                continue
            p, n = hit
            d = Vector((s * 0.9, 0, 0.35 - 0.6 * u)).normalized()
            brows.append([p + n * 0.0006, p + n * 0.0012 + d * 0.005, p + n * 0.0008 + d * 0.009])
    hair_object('HAIR-brows', brows, 0.00017, M['hair'], head)

    # --- Pestañas azul-violeta, largas en el rabillo exterior.
    lashes = []
    for idx, (s, e) in enumerate(((-1, eyes[0]), (1, eyes[1]))):
        ec = e.matrix_world.translation
        for i in range(30):
            u = i / 29
            ang = math.pi * (0.1 + 0.8 * u)
            local = Vector((-s * math.cos(ang) * eye_r * 0.95, -eye_r * 0.9, math.sin(ang) * eye_r * 0.28))
            p = ec + local
            hit = S.cast(p + Vector((0, -0.03, 0)), (0, 1, 0))
            if hit and (hit[0] - p).length < 0.02:
                p = hit[0]
            outer = u if s > 0 else 1 - u
            ln = 0.004 + 0.011 * outer ** 1.6
            d = Vector((s * 0.7 * outer, -1.0, 0.25)).normalized()
            lashes.append([p, p + d * ln * 0.5 + Vector((0, 0, ln * 0.12)), p + d * ln + Vector((s * ln * 0.25 * outer, 0, ln * 0.25))])
    hair_object('HAIR-lashes', lashes, 0.00014, M['lash'], head)

    # --- Trenzas: tres lóbulos entrelazados que bajan por delante de los hombros.
    for s in (-1, 1):
        hit = S.toward(C, sph(s * 1.95, hairline(s * 1.95) - 0.05))
        start = hit[0] + hit[1] * 0.006 if hit else C + Vector((s * 0.07, 0.04, -0.05))
        path = [start,
                start + Vector((s * 0.012, -0.01, -0.06)),
                Vector((s * 0.095, -0.02, eye_z - 0.17)),
                Vector((s * 0.125, -0.05, eye_z - 0.28)),
                Vector((s * 0.13, -0.07, eye_z - 0.45))]
        # Interpolación Catmull-Rom del eje.
        axis = []
        for seg in range(len(path) - 1):
            p0 = path[max(0, seg - 1)]
            p1, p2 = path[seg], path[seg + 1]
            p3 = path[min(len(path) - 1, seg + 2)]
            for k in range(30):
                t = k / 30
                axis.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
        axis.append(path[-1])
        total = sum((axis[i + 1] - axis[i]).length for i in range(len(axis) - 1))
        dist = 0.0
        lobes = [[], [], []]
        radii = []
        for i, p in enumerate(axis):
            if i:
                dist += (axis[i] - axis[i - 1]).length
            tan = (axis[min(i + 1, len(axis) - 1)] - axis[max(i - 1, 0)]).normalized()
            side = tan.cross(Vector((0, 1, 0))).normalized()
            fwd = side.cross(tan).normalized()
            u = dist / total
            w = 0.011 * (1 - 0.45 * u)
            for k in range(3):
                ph = dist / 0.03 * 2 * math.pi + k * 2 * math.pi / 3
                lobes[k].append(p + side * math.sin(ph) * w + fwd * math.sin(2 * ph) * w * 0.45)
            radii.append(1 - 0.5 * u)
        for k in range(3):
            tube(f'GEO-braid-{s}-{k}', lobes[k], 0.0062, M['hair'], head, radii)
        # Hebras sueltas sobre la trenza para que no parezca plástico.
        fuzz = []
        for i in range(160):
            k = rnd.randrange(3)
            j0 = rnd.randrange(0, len(axis) - 20)
            off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * 0.0025
            fuzz.append([lobes[k][j] + off * (1 + (j - j0) * 0.05) for j in range(j0, j0 + 18, 3)])
        hair_object(f'HAIR-braid-{s}', fuzz, 0.00022, M['hair'], head)

    # --- Micro-piercings dispersos por mejillas, nariz y frente.
    k = 0
    for s_, ec in ((-1, eyeL), (1, eyeR)):
        for row, (count, drop, spread) in enumerate(((7, 0.016, 0.9), (5, 0.026, 0.7))):
            for j in range(count):
                u = j / (count - 1)
                ang = math.pi * (0.15 + spread * u)
                x = ec.x - s_ * math.cos(ang) * 0.022 + rnd.uniform(-0.0015, 0.0015)
                z = ec.z - drop - 0.006 * math.sin(ang) + rnd.uniform(-0.0015, 0.0015)
                hit = S.front(x, z)
                if not hit or rnd.random() < 0.25:
                    continue
                p, n = hit
                r = rnd.choice((0.0006, 0.0008, 0.0011, 0.0015))
                sphere_obj(f'GEO-stud-{k}', M['chrome'] if rnd.random() < 0.7 else M['stud_dark'], p + n * r * 0.4, r, head)
                k += 1
    for j, (x, z) in enumerate(((-0.004, eye_z + 0.005), (0.005, eye_z - 0.006), (-0.03, eye_z + 0.06), (0.024, eye_z + 0.072))):
        hit = S.front(x, z)
        if hit:
            sphere_obj(f'GEO-stud-x{j}', M['chrome'], hit[0] + hit[1] * 0.0004, 0.001, head)

    # --- Boca: fila de micro-piercings en el labio inferior y cables que cuelgan.
    mouth_z = None
    for dz in [i * 0.001 for i in range(40, 110)]:
        hit = S.front(0.0, eye_z - dz)
        if hit and hit[0].y > -0.15:
            pass
    # Comisura/labio: el punto más adelantado entre nariz y barbilla bajo la nariz.
    best = None
    for i in range(70, 105):
        z = eye_z - i * 0.001
        hit = S.front(0.0, z)
        if hit and (best is None or hit[0].y < best[1]):
            best = (z, hit[0].y)
    mouth_z = eye_z - 0.071  # comisura: proporción de la malla base (la detección automática cogía la barbilla)
    print('LANDMARK mouth_z', round(mouth_z, 4))
    for i in range(7):
        x = -0.015 + 0.03 * i / 6
        hit = S.front(x, mouth_z - 0.004 - 0.003 * (1 - (2 * i / 6 - 1) ** 2))
        if hit:
            p, n = hit
            sphere_obj(f'GEO-lipstud-{i}', M['chrome'], p + n * 0.0006, 0.0013, head)
    cables = []
    for i in range(6):
        x0 = rnd.uniform(-0.016, 0.016)
        drift = rnd.uniform(-0.025, 0.025)
        drop = rnd.uniform(0.05, 0.13)
        z0 = mouth_z + rnd.uniform(-0.006, 0.0)
        pts = []
        for j in range(26):
            u = j / 25
            hit = S.front(x0 + drift * u, z0 - drop * u)
            if not hit:
                break
            p, n = hit
            # Se separan un poco de la piel en la barbilla, como colgando.
            pts.append(p + n * (0.0012 + 0.006 * math.sin(math.pi * min(1, u * 1.6)) * (0.5 + 0.5 * (i % 2))))
        if len(pts) > 6:
            cables.append(pts)
    for i, pts in enumerate(cables):
        tube(f'GEO-cable-{i}', pts, 0.0007 if i % 3 else 0.0011, M['cable'] if i % 2 else M['chrome'], head)

    # --- Neón en el cuello: garabatos que abrazan la garganta y bajan al pecho.
    neon_mat, pulse = neon_material()
    for i in range(5):
        z = eye_z - 0.14 - i * 0.011 + rnd.uniform(-0.003, 0.003)
        c, r = slice_center(head, z)
        span = rnd.uniform(0.7, 1.2)
        a0 = rnd.uniform(-0.35, 0.35)
        f1, ph = rnd.uniform(1.2, 2.6), rnd.uniform(0, 6.28)
        pts = []
        for j in range(80):
            u = j / 79
            a_ = a0 + (u - 0.5) * span * 2
            zz = z + 0.007 * math.sin(2 * math.pi * f1 * u + ph) + 0.0025 * math.sin(2 * math.pi * 3.1 * u + i)
            d = Vector((math.sin(a_), -math.cos(a_), 0))
            hit = S.cast(Vector((c.x, c.y, zz)) + d * 0.3, -d)
            # Solo piel de cuello (normal casi horizontal): evita saltar a la mandíbula.
            if hit and abs(hit[1].z) < 0.55:
                pts.append(hit[0] + hit[1] * 0.0012)
        for _ in range(3):  # suavizado
            pts = [pts[0]] + [(pts[k - 1] + pts[k] * 2 + pts[k + 1]) / 4 for k in range(1, len(pts) - 1)] + [pts[-1]] if len(pts) > 3 else pts
        if len(pts) > 10:
            tube(f'GEO-neon-{i}', pts, 0.00045, neon_mat, head)

    # --- Cascos de DJ apoyados en el cuello: cromo, almohadillas negras y aro rojo Barullo.
    zc = eye_z - 0.2
    c, r = slice_center(head, zc)
    phones = bpy.data.objects.new('PHONES', None)
    link(phones, head)
    phones.location = (c.x, c.y + 0.01, zc)
    phones.rotation_euler = (math.radians(-12), 0, 0)
    band = torus_obj('GEO-phones_band', M['chrome'], r + 0.03, 0.0045, phones, arc=math.pi * 1.1)
    band.rotation_euler = (0, 0, math.radians(-9))
    for s in (-1, 1):
        a = math.radians(90 + 55 * s) if False else math.radians(-90 + 62 * s)
        pos = Vector((math.cos(a), math.sin(a), 0)) * (r + 0.04)
        cup = bpy.data.objects.new(f'CUP-{s}', None)
        link(cup, phones)
        cup.location = pos
        cup.rotation_mode = 'QUATERNION'
        cup.rotation_quaternion = pos.normalized().to_track_quat('Z', 'Y')
        body = cylinder_obj(f'GEO-cup-{s}', M['chrome'], 0.034, 0.022, cup)
        body.location = (0, 0, 0.0)
        cush = cylinder_obj(f'GEO-cushion-{s}', M['cushion'], 0.031, 0.014, cup)
        cush.location = (0, 0, -0.018)
        ring = torus_obj(f'GEO-cup_ring-{s}', M['red'], 0.016, 0.0028, cup)
        ring.location = (0, 0, 0.0115)

    return head, eyes, pulse


# ---------------------------------------------------------------- animación

def animate(head, eyes, pulse):
    rest = [e.rotation_euler.copy() for e in eyes]
    for e in eyes:
        e.rotation_mode = 'XYZ'
    glow = bpy.data.materials['M_eye_glow'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    head.rotation_mode = 'XYZ'
    for f in range(1, FRAMES + 1):
        t = (f - 1) / FRAMES
        beat = (t * BEATS) % 1.0
        nod = kick(beat, 0.1, 0.14)
        head.rotation_euler = (0.018 * nod - 0.03 + 0.01 * math.sin(4 * math.pi * t),
                               0.025 * math.sin(2 * math.pi * t + 1.0),
                               0.32 * math.sin(2 * math.pi * t))
        head.location = (0, 0, -0.002 * nod)
        head.keyframe_insert('rotation_euler', frame=f)
        head.keyframe_insert('location', frame=f)
        # Mirada: va por delante del giro de la cabeza, con sacadas rápidas.
        look = math.tanh(3.0 * math.sin(2 * math.pi * (t + 0.06)))
        for e, r0 in zip(eyes, rest):
            e.rotation_euler = (r0.x - 0.05, r0.y, r0.z + 0.28 * look)
            e.keyframe_insert('rotation_euler', frame=f)
        glow.default_value = 4.0 + 3.5 * kick(beat, 0.04, 0.12)
        glow.keyframe_insert('default_value', frame=f)
        # El pulso del neón sube por el cuello: dos ciclos de fase por bucle.
        pulse.inputs['Phase Offset'].default_value = -4 * math.pi * t
        pulse.inputs['Phase Offset'].keyframe_insert('default_value', frame=f)
    bpy.context.scene.frame_set(1)


# ---------------------------------------------------------------- render

def setup_render(variant, out, eye_z):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, FRAMES
    sc.render.resolution_x, sc.render.resolution_y = (1920, 824) if variant == 'wide' else (1080, 1080)
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.dither_intensity = 0.0
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = out
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    ee = sc.eevee
    for attr, val in (('taa_render_samples', 64), ('use_raytracing', True), ('use_shadows', True),
                      ('fast_gi_method', 'GLOBAL_ILLUMINATION')):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception as e:  # noqa: BLE001
                print('eevee', attr, e)
    try:
        ee.ray_tracing_options.resolution_scale = '1'
    except Exception as e:  # noqa: BLE001
        print('raytrace opts', e)

    cam_d = bpy.data.cameras.new('CAM-hero')
    cam_d.lens = 85
    cam_d.sensor_fit = 'VERTICAL'
    cam_d.sensor_height = 24
    cam = link(bpy.data.objects.new('CAM-hero', cam_d))
    target = Vector((0, 0, eye_z - 0.045))
    cam.location = target + Vector((0, -1.05, 0.07))
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = (cam.location - target).to_track_quat('Z', 'Y')
    sc.camera = cam

    light('LGT-key', 'AREA', (-0.6, -1.2, eye_z + 0.9), (0, 0, eye_z), 14, '#FFFFFF', size=0.8, spec=0.6)
    light('LGT-fill', 'AREA', (0.9, -0.8, eye_z - 0.2), (0, 0, eye_z), 3, '#F2F0F5', size=1.2, spec=0.3)
    light('LGT-rim_violet', 'AREA', (-0.8, 0.9, eye_z + 0.3), (0, 0, eye_z), 30, '#8B5CFF', size=0.5)
    light('LGT-rim_cool', 'AREA', (0.8, 0.9, eye_z + 0.4), (0, 0, eye_z), 22, '#E6ECFF', size=0.5)
    # Rebote violeta de los ojos sobre párpados y pómulos.
    light('LGT-eye_bounce', 'POINT', (0, -0.3, eye_z), (0, 0, eye_z), 0.8, '#B49BFF', size=0.05, spec=0.0)


def setup_glare():
    """
    Halo solo de lo que emite luz (ojos, neón, pestañas): el bloom se aplica al
    pase de emisión y se suma a la imagen. Los brillos del cromo no hacen halo,
    así el fondo sigue siendo #050505 exacto hasta en las esquinas.
    """
    sc = bpy.context.scene
    try:
        bpy.context.view_layer.use_pass_emit = True
        tree = bpy.data.node_groups.new('COMP-cyber', 'CompositorNodeTree')
        sc.compositing_node_group = tree
        tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = tree.nodes.new('CompositorNodeRLayers')
        gl = tree.nodes.new('CompositorNodeGlare')
        for key, val in (('Type', 'Bloom'), ('Quality', 'High'), ('Threshold', 0.6), ('Strength', 0.5), ('Size', 0.22)):
            if key in gl.inputs:
                try:
                    gl.inputs[key].default_value = val
                except Exception as e:  # noqa: BLE001
                    print('glare', key, e)
        emit = rl.outputs.get('Emit') or rl.outputs.get('Emission')
        tree.links.new(emit, gl.inputs['Image'])
        # El glare devuelve emisión + halo: se resta la emisión para sumar solo el halo.
        sub = tree.nodes.new('ShaderNodeMix')
        sub.data_type = 'RGBA'
        sub.blend_type = 'SUBTRACT'
        sub.inputs['Factor'].default_value = 1.0
        tree.links.new(gl.outputs['Image'], sub.inputs[6])
        tree.links.new(emit, sub.inputs[7])
        add = tree.nodes.new('ShaderNodeMix')
        add.data_type = 'RGBA'
        add.blend_type = 'ADD'
        add.inputs['Factor'].default_value = 1.0
        tree.links.new(rl.outputs['Image'], add.inputs[6])
        tree.links.new(sub.outputs[2], add.inputs[7])
        out = tree.nodes.new('NodeGroupOutput')
        tree.links.new(add.outputs[2], out.inputs[0])
        print('glare: ok (solo emisión)')
    except Exception as e:  # noqa: BLE001
        print('glare: omitido ->', e)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--lib', required=True)
    ap.add_argument('--out', default='//frames/')
    ap.add_argument('--variant', default='square', choices=('square', 'wide'))
    ap.add_argument('--frames', default='')
    ap.add_argument('--save', default='')
    args, _ = ap.parse_known_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    build_world()
    head, eyes, pulse = build(args.lib, M)
    eye_z = eyes[0].matrix_world.translation.z
    animate(head, eyes, pulse)
    setup_render(args.variant, args.out, eye_z)
    if "--noglare" not in sys.argv:
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


if __name__ == '__main__':
    main()
