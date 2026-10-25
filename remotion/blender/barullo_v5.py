"""
Mascota de Barullo v5: la cabeza de porcelana de la v4 sin cigarro, sin humo y
sin grillz. Labios carnosos y realistas (arco de cupido, brillo mojado y
arruguitas verticales), corona de pinchos curvos de cromo líquido con collarín,
cascos de DJ detallados (aro cromado, pinchitos, letras BARULLO, horquilla y
doble alambre) y más joyería en la cara.
Animación lenta y natural (10 s, bucle): los ojos se adelantan a la cabeza,
parpadeo al cambiar de mirada, vuelve a cámara con la barbilla baja; los
pinchos se quedan atrás un instante al girar.

Base: "head_stylized" del pack oficial Human Base Meshes de Blender (CC0).

  blender.exe -b --factory-startup --python barullo_v5.py -- \
      --lib C:/.../human_base_meshes_bundle.blend --out C:/ruta/frames/ \
      --variant square|wide [--frames 1-300] [--percent 100] [--samples 64] [--save escena.blend]
"""

import argparse
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import barullo_cyber as base  # noqa: E402
import barullo_v4 as v4  # noqa: E402  (cabeza, ojos y utilidades de la v4)

FPS, FRAMES, SECONDS = 30, 300, 10.0
MOUTH_Z = v4.MOUTH_Z
LIP_CORNER = 0.031  # semiancho de la boca (perfil medido con raycast)
hex_lin = base.hex_lin
smooth, track, empty, cone, cylinder, along = v4.smooth, v4.track, v4.empty, v4.cone, v4.cylinder, v4.along
new_mesh_obj = v4.new_mesh_obj


# ---------------------------------------------------------------- curvas

def spline(keys, sec, period=SECONDS):
    """
    Curva periódica Catmull-Rom por poses [(segundo, valor)]: pasa por cada pose
    sin pararse en seco (la v4 frenaba a cero en todas). Primera y última pose
    iguales: el bucle cierra con la misma velocidad.
    """
    ks = keys[:-1]
    n = len(ks)
    ext = [(t - period, v) for t, v in ks[-2:]] + ks + [(t + period, v) for t, v in ks[:3]]
    sec %= period
    for i in range(2, n + 2):
        (t0, p0), (t1, p1) = ext[i], ext[i + 1]
        if t0 <= sec <= t1:
            tm, pm = ext[i - 1]
            t2, p2 = ext[i + 2]
            m0 = (p1 - pm) / (t1 - tm)
            m1 = (p2 - p0) / (t2 - t0)
            h = t1 - t0
            u = (sec - t0) / h
            u2, u3 = u * u, u * u * u
            return ((2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * h * m0
                    + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * h * m1)
    return keys[-1][1]


def blink(sec, at, close=0.075, hold=0.035, open_=0.17):
    """0 → 1 → 0: cierra rápido, abre más despacio (como un parpadeo real)."""
    d = sec - at
    if d < 0 or d > close + hold + open_:
        return 0.0
    if d < close:
        return smooth(0, close, d)
    if d < close + hold:
        return 1.0
    return 1.0 - smooth(close + hold, close + hold + open_, d)


def frame_from(z, x=(1, 0, 0)):
    """Matriz 3x3 con Z = z y X lo más cerca posible de x."""
    z = Vector(z).normalized()
    x = Vector(x)
    x = (x - z * x.dot(z))
    if x.length < 1e-5:
        x = Vector((1, 0, 0)) - z * z.x
    x.normalize()
    y = z.cross(x)
    return Matrix((x, y, z)).transposed()


# ---------------------------------------------------------------- materiales

def skin_lips_material():
    """
    Porcelana lila con los labios pintados encima por un atributo de la malla
    ('lipmask' 0..1, 'lipdeep' más oscuro junto a la comisura). Los labios llevan
    arruguitas verticales en la base y una capa de brillo lisa encima: mojados.
    """
    m = bpy.data.materials.new('M_porcelain_lips')
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    p = N['Principled BSDF']

    def attr(name):
        a = N.new('ShaderNodeAttribute')
        a.attribute_name = name
        return a.outputs['Fac']

    def mix_col(fac, a, b):
        x = N.new('ShaderNodeMix')
        x.data_type = 'RGBA'
        x.inputs[6].default_value = a
        x.inputs[7].default_value = b
        L.new(fac, x.inputs['Factor'])
        return x

    def mix_f(fac, a, b):
        x = N.new('ShaderNodeMix')
        x.data_type = 'FLOAT'
        x.inputs[2].default_value = a
        x.inputs[3].default_value = b
        L.new(fac, x.inputs['Factor'])
        return x.outputs[0]

    mask, deep = attr('lipmask'), attr('lipdeep')
    lip = mix_col(deep, hex_lin('#A9628A'), hex_lin('#5A2149'))
    col = mix_col(mask, hex_lin('#CFC5E6'), (0, 0, 0, 1))
    L.new(lip.outputs[2], col.inputs[7])
    L.new(col.outputs[2], p.inputs['Base Color'])
    L.new(mix_f(mask, 0.26, 0.2), p.inputs['Roughness'])
    L.new(mix_f(mask, 0.03, 0.0), p.inputs['Coat Roughness'])
    # Sin barniz en la ranura: de canto reflejaba el estudio como una línea gris.
    L.new(mix_f(deep, 1.0, 0.0), p.inputs['Coat Weight'])
    p.inputs['Subsurface Weight'].default_value = 0.2
    p.inputs['Subsurface Scale'].default_value = 0.003
    p.inputs['Subsurface Radius'].default_value = Vector((1.0, 0.5, 0.7))
    p.inputs['Thin Film Thickness'].default_value = 380.0
    p.inputs['Thin Film IOR'].default_value = 1.35
    p.inputs['Specular IOR Level'].default_value = 0.5

    # Arruguitas: bandas verticales (eje X del objeto) deformadas con ruido.
    coord = N.new('ShaderNodeTexCoord')
    wave = N.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 210.0
    wave.inputs['Distortion'].default_value = 6.0
    wave.inputs['Detail'].default_value = 4.0
    wave.inputs['Detail Roughness'].default_value = 0.7
    L.new(coord.outputs['Object'], wave.inputs['Vector'])
    amp = N.new('ShaderNodeMath')
    amp.operation = 'MULTIPLY'
    L.new(wave.outputs['Fac'], amp.inputs[0])
    L.new(mask, amp.inputs[1])
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.0004
    L.new(amp.outputs[0], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def materials():
    M = v4.materials()
    for k in ('paper', 'filter', 'ash', 'ember', 'wisp', 'puff'):
        M.pop(k)
    P = base.principled
    M['skin_lips'] = skin_lips_material()
    M['black_lacquer'] = P('M_black_lacquer', hex_lin('#0A0A0E'), rough=0.15, coat=1.0, coat_rough=0.01)
    M['letters'] = P('M_letters', hex_lin('#F4F2F8'), rough=0.3, emit=hex_lin('#FFFFFF'), emit_strength=0.4)
    # Cromo líquido algo más oscuro que el de la v4 (ref cuernos negros cromados): más contraste.
    # Gotas: perla de barniz transparente (la transmisión de EEVEE las pintaba negras).
    M['drop'] = P('M_drop', hex_lin('#E9E4F4'), rough=0.0, coat=1.0, coat_rough=0.0,
                  **{'Specular IOR Level': 1.0, 'Subsurface Weight': 0.4, 'Subsurface Scale': 0.002})
    M['liquid_chrome'] = P('M_liquid_chrome', hex_lin('#C9CBD4'), metal=1.0, rough=0.06, coat=1.0, coat_rough=0.0)
    return M


# ---------------------------------------------------------------- cabeza y labios

def densify(head):
    """Aplica un nivel de subdivisión a la malla: más vértices para dibujar los labios."""
    sub = head.modifiers.new('pre', 'SUBSURF')
    sub.levels = 1
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(head.evaluated_get(dg))
    head.modifiers.remove(sub)
    old = head.data
    head.data = me
    bpy.data.meshes.remove(old)


def lip_profile(x):
    """Borde superior e inferior del labio en función de x (cupido incluido)."""
    u = min(1.0, abs(x) / LIP_CORNER)
    top = MOUTH_Z + 0.0215 * (1 - u ** 1.7)
    top += 0.0013 * math.exp(-((abs(x) - 0.0068) / 0.0032) ** 2)  # picos del arco de cupido
    top -= 0.0016 * math.exp(-(x / 0.0026) ** 2)  # valle central
    bot = MOUTH_Z - 0.0195 * (1 - u ** 2.3)
    return top, bot


def sculpt_lips(head):
    """
    Labios más carnosos y realistas: se empujan hacia delante con un perfil
    redondeado (más el inferior) y se guardan las máscaras para el material.
    """
    me = head.data
    mask = me.attributes.new('lipmask', 'FLOAT', 'POINT')
    deep = me.attributes.new('lipdeep', 'FLOAT', 'POINT')
    mv, dv = [0.0] * len(me.vertices), [0.0] * len(me.vertices)
    for i, v in enumerate(me.vertices):
        co = v.co
        if co.y > -0.085 or abs(co.x) > LIP_CORNER + 0.006 or not (MOUTH_Z - 0.026 < co.z < MOUTH_Z + 0.03):
            continue
        top, bot = lip_profile(co.x)
        soft = 0.0011
        m = smooth(bot - soft, bot + soft, co.z) * (1 - smooth(top - soft, top + soft, co.z))
        m *= 1 - smooth(LIP_CORNER - 0.004, LIP_CORNER + 0.002, abs(co.x))
        if m <= 0:
            continue
        mv[i] = m
        upper = co.z >= MOUTH_Z
        h = (co.z - MOUTH_Z) / max(1e-4, top - MOUTH_Z) if upper else (MOUTH_Z - co.z) / max(1e-4, MOUTH_Z - bot)
        h = max(0.0, min(1.0, h))
        dv[i] = m * (1 - smooth(0.0, 0.55, h)) * 0.85
        # Volumen: campana sobre la altura del labio, más hacia el centro de la boca.
        bulge = math.sin(math.pi * min(1.0, 0.15 + 0.85 * h)) * (1 - smooth(0.3, 1.0, abs(co.x) / LIP_CORNER) * 0.6)
        push = (0.0026 if upper else 0.0036) * bulge * m
        v.co = co + Vector((0, -push, 0))
    mask.data.foreach_set('value', mv)
    deep.data.foreach_set('value', dv)
    me.update()


# ---------------------------------------------------------------- piezas

def horn(name, mat, length, r0, bend, parent, seg=28, rings=18):
    """Pincho curvo con base acampanada: se dobla hacia +X local, apunta a +Z."""
    bm = bmesh.new()
    loops = []
    for i in range(rings):
        u = i / (rings - 1)
        c = Vector((bend * length * u * u, 0, length * u))
        r = r0 * (1 - u) ** 1.05 * (1 + 0.35 * (1 - smooth(0.0, 0.18, u)))
        if i == rings - 1:
            loops.append([bm.verts.new(c)])
            continue
        loops.append([bm.verts.new(c + Vector((math.cos(a) * r, math.sin(a) * r, 0)))
                      for a in (2 * math.pi * k / seg for k in range(seg))])
    for a, b in zip(loops, loops[1:]):
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(b) == 1:
                bm.faces.new((a[k], a[k2], b[0]))
            else:
                bm.faces.new((a[k], a[k2], b[k2], b[k]))
    bm.faces.new(list(reversed(loops[0])))
    return new_mesh_obj(name, bm, mat, parent)


def text_bm(body, size, extrude=0.0):
    cu = bpy.data.curves.new('TXT-tmp', 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    o = bpy.data.objects.new('TXT-tmp', cu)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(o)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    return bm


def on_surface(name, mat, S, center, direction, parent, size, kind='sphere', flat=0.5, up=(0, 0, 1)):
    """Pega una pieza a la cabeza (raycast) alineada con la normal."""
    h = S.toward(center, direction, 0.5)
    if not h:
        return None
    p, n = h
    if kind == 'sphere':
        o = base.sphere_obj(name, mat, p + n * size * flat * 0.6, size, parent, scale=(1, 1, flat))
    else:
        o = new_mesh_obj(name, kind, mat, parent)
        o.location = p + n * 0.0004
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = frame_from(n, Vector(up).cross(n)).to_quaternion()
    return o


def star_bm(r_out, r_in, depth, points=4):
    bm = bmesh.new()
    top, bot = [], []
    for k in range(points * 2):
        a = math.pi * k / points + math.pi / 2
        r = r_out if k % 2 == 0 else r_in
        top.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, depth)))
        bot.append(bm.verts.new((math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, 0)))
    ct = bm.verts.new((0, 0, depth * 1.8))
    n = len(top)
    for k in range(n):
        k2 = (k + 1) % n
        bm.faces.new((top[k], top[k2], ct))
        bm.faces.new((bot[k], bot[k2], top[k2], top[k]))
    bm.faces.new(list(reversed(bot)))
    return bm


# ---------------------------------------------------------------- escena

def build(lib, M):
    rnd = random.Random(16)
    head, eyes = v4.load_head(lib)
    v4.stylize(head)
    densify(head)
    sculpt_lips(head)
    head.data.materials.clear()
    head.data.materials.append(M['skin_lips'])
    jaw_key = v4.add_jaw_key(head)
    jaw_key.value = 0.0
    head.data.shade_smooth()
    sub = head.modifiers.new('subsurf', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    S = base.Surface(head)

    eye_r = eyes[0].dimensions.x / 2
    eye_c = [e.matrix_world.translation.copy() for e in eyes]
    rig = {'head': head, 'jaw_key': jaw_key, 'eyes': [], 'lids': [], 'spikes': [], 'cups': []}

    # --- Ojos (como la v4): globo violeta, iris blanco caliente, párpados con pestañas-cuchilla.
    for s, e in zip((-1, 1), eyes):
        e.data.materials.clear()
        e.data.materials.append(M['sclera'])
        e.data.shade_smooth()
        ec = e.matrix_world.translation.copy()
        pivot = empty(f'EYEPIV-{s}', head, loc=ec)
        e.parent = pivot
        e.matrix_parent_inverse = Matrix.Identity(4)
        e.location = (0, 0, 0)
        e.rotation_euler = (0, 0, 0)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
        iris = new_mesh_obj(f'GEO-iris-{s}', bm, M['iris'], pivot)
        iris.location = (0, -eye_r * 0.9, 0)
        iris.scale = (eye_r * 0.42, eye_r * 0.14, eye_r * 0.42)
        rig['eyes'].append(pivot)
        lids = []
        for kind in ('up', 'low'):
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=eye_r * 1.08)
            kill = [v for v in bm.verts if (v.co.z < -1e-5 if kind == 'up' else v.co.z > 1e-5)]
            bmesh.ops.delete(bm, geom=kill, context='VERTS')
            lid_e = empty(f'LID-{kind}-{s}', head, loc=ec)
            lid_e.rotation_mode = 'XYZ'
            lid = new_mesh_obj(f'GEO-lid-{kind}-{s}', bm, M['skin'], lid_e)
            sol = lid.modifiers.new('solid', 'SOLIDIFY')
            sol.thickness = eye_r * 0.06
            sol.offset = -1
            lids.append(lid_e)
            if kind == 'up':
                for j in range(7):
                    u = j / 6
                    phi = math.radians(-90 - s * (-60 + 135 * u))
                    p = Vector((math.cos(phi), math.sin(phi), 0)) * eye_r * 1.1
                    d = Vector((math.cos(phi) * 0.8 + s * 0.6 * u, math.sin(phi) * 0.5, 0.75 + 0.3 * u))
                    lash_e = empty(f'LASH-{s}-{j}', lid_e, loc=p, rot=along(d))
                    c = cone(f'GEO-lash-{s}-{j}', M['lash'], eye_r * (0.55 + 1.35 * u ** 1.5), eye_r * 0.12, lash_e, seg=16)
                    c.scale = (1.0, 0.28, 1.0)
        rig['lids'].append(lids)

    # --- Boca: solo el interior oscuro que se ve al entreabrir los labios (sin dientes).
    lips = [S.front(0.0, MOUTH_Z + dz) for dz in (0.004, -0.004)]
    seam_y = max(h[0].y for h in lips if h) + 0.003 if all(lips) else -0.119
    # Más metido que en la v4: con los labios más gruesos asomaba por delante.
    mouth = empty('MOUTH', head, loc=(0, seam_y + 0.006, MOUTH_Z - 0.001))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=16, radius=1)
    cav = new_mesh_obj('GEO-mouth_cavity', bm, M['mouth'], mouth)
    cav.scale = (0.021, 0.0015, 0.001)
    rig['cavity'] = cav

    # --- Corona: fila principal de pinchos curvos con collarín, fila trasera más corta y tachuelas.
    C = Vector((0, 0.005, 0.215))
    rows = [(9, -78, 156, -0.18, 1.0), (8, -70, 140, 0.55, 0.62)]
    for row, (n, a0, span, back, scale_) in enumerate(rows):
        for i in range(n):
            u = (i + (0.0 if row == 0 else 0.5)) / (n - (1 if row == 0 else 0))
            a = math.radians(a0 + span * u)
            d = Vector((math.sin(a), back, math.cos(a))).normalized()
            h = S.toward(C, d, 0.5)
            if not h:
                continue
            p, nrm = h
            mid = 1 - abs(2 * u - 1)
            length = (0.075 + 0.072 * mid) * scale_ * (0.92 + 0.16 * rnd.random())
            r0 = (0.012 + 0.004 * mid) * (0.85 + 0.15 * scale_)
            # Se curvan hacia atrás y un poco hacia fuera (ref cuernos de cromo líquido).
            sweep = Vector((0, 1, 0)) + Vector((math.sin(a), 0, 0)) * 0.6
            rot = frame_from(d, sweep).to_quaternion()
            piv = empty(f'SPK-{row}-{i}', head, loc=p - nrm * 0.004, rot=rot)
            horn(f'GEO-spike-{row}-{i}', M['liquid_chrome'], length, r0, 0.22 + 0.1 * mid, piv)
            col = base.torus_obj(f'GEO-spike_collar-{row}-{i}', M['black_lacquer'], r0 * 1.25, r0 * 0.33, piv, seg=48, ts=12)
            col.location = (0, 0, 0.004)
            rig['spikes'].append((piv, rot.copy(), p.copy(), length))
        if row == 0:
            # Tachuelas entre pinchos de la fila principal.
            for i in range(n - 1):
                a = math.radians(a0 + span * (i + 0.5) / (n - 1))
                d = Vector((math.sin(a), back - 0.05, math.cos(a))).normalized()
                on_surface(f'GEO-crown_stud-{i}', M['liquid_chrome'], S, C, d, head, 0.0042, flat=0.7)

    # --- Cascos: diadema elíptica blanca con doble alambre cromado y pinchitos;
    # horquilla cromada; carcasa blanca con aro cromado, placa negra con letras,
    # anillo rojo, pincho central y corona de pinchitos alrededor.
    phones = empty('PHONES', head, loc=(0, 0.035, 0.19))
    cup_x, cup_z, yoke_r = 0.158, -0.01, 0.057
    end_z = cup_z + yoke_r + 0.006
    top_z = 0.168

    def arc_pts(a_x, z0, z1, n=48):
        b = z1 - z0
        return [(a_x * math.cos(math.pi * k / n), 0, z0 + b * math.sin(math.pi * k / n)) for k in range(n + 1)]

    base.tube('GEO-phones_band', arc_pts(cup_x + 0.004, end_z, top_z), 0.0085, M['white_lacquer'], phones)
    for j, (dx, dz, dy) in enumerate(((0.014, 0.014, -0.006), (0.02, 0.022, 0.007))):
        base.tube(f'GEO-phones_wire-{j}', [(x, dy, z) for x, _, z in arc_pts(cup_x + dx, end_z - 0.004, top_z + dz)],
                  0.0019, M['chrome'], phones)
    # Pinchitos a lo largo del alambre exterior (solo por arriba).
    ax, z0, b = cup_x + 0.02, end_z - 0.004, top_z + 0.022 - (end_z - 0.004)
    for k in range(13):
        ang = math.pi * (0.18 + 0.64 * k / 12)
        p = Vector((ax * math.cos(ang), 0.007, z0 + b * math.sin(ang)))
        nrm = Vector((math.cos(ang) / ax, 0, math.sin(ang) / b)).normalized()
        e = empty(f'BANDSPK-{k}', phones, loc=p, rot=along(nrm))
        cone(f'GEO-band_spike-{k}', M['chrome'], 0.014, 0.0032, e, seg=16)

    for s in (-1, 1):
        # Girados hacia delante (como se llevan unos cascos de DJ): la cara decorada mira a cámara.
        cup = empty(f'CUP-{s}', phones, loc=(cup_x * s, -0.004, cup_z), rot=along((s, -0.42, 0)))
        cylinder(f'GEO-cup-{s}', M['white_lacquer'], 0.05, 0.034, cup, bevel=0.008)
        cush = cylinder(f'GEO-cushion-{s}', M['cushion'], 0.044, 0.014, cup, bevel=0.005)
        cush.location = (0, 0, -0.02)
        pleat = base.torus_obj(f'GEO-cushion_roll-{s}', M['cushion'], 0.041, 0.0075, cup, seg=64, ts=12)
        pleat.location = (0, 0, -0.026)
        rim = base.torus_obj(f'GEO-cup_rim-{s}', M['chrome'], 0.046, 0.0042, cup, seg=96, ts=16)
        rim.location = (0, 0, 0.0172)
        plate = cylinder(f'GEO-cup_plate-{s}', M['black_lacquer'], 0.043, 0.004, cup, bevel=0.0012)
        plate.location = (0, 0, 0.0175)
        letters = 'BARULLO · BARULLO · '
        for k, ch in enumerate(letters):
            if ch == ' ':
                continue
            ang = -2 * math.pi * k / len(letters) + math.pi / 2
            bm = text_bm(ch, 0.0085, extrude=0.0004)
            R = Matrix.Rotation(ang - math.pi / 2, 4, 'Z')
            bm.transform(Matrix.Translation((math.cos(ang) * 0.0335, math.sin(ang) * 0.0335, 0.0198)) @ R)
            new_mesh_obj(f'GEO-cup_letter-{s}-{k}', bm, M['letters'], cup, smooth_shade=False)
        inner = base.torus_obj(f'GEO-cup_inner-{s}', M['chrome'], 0.0255, 0.0018, cup, seg=64, ts=10)
        inner.location = (0, 0, 0.0198)
        red = cylinder(f'GEO-cup_red-{s}', M['red'], 0.0235, 0.004, cup, bevel=0.001)
        red.location = (0, 0, 0.0195)
        e = empty(f'CUPSPK-{s}', cup, loc=(0, 0, 0.021))
        horn(f'GEO-cup_spike-{s}', M['liquid_chrome'], 0.034, 0.0095, 0.0, e, seg=24, rings=12)
        col = base.torus_obj(f'GEO-cup_spike_collar-{s}', M['black_lacquer'], 0.0115, 0.0028, e, seg=48, ts=10)
        col.location = (0, 0, 0.002)
        for k in range(18):
            ang = 2 * math.pi * k / 18
            d = Vector((math.cos(ang), math.sin(ang), 0.25))
            pe = empty(f'CUPRING-{s}-{k}', cup, loc=(math.cos(ang) * 0.049, math.sin(ang) * 0.049, 0.004), rot=along(d))
            cone(f'GEO-cup_ring_spike-{s}-{k}', M['chrome'], 0.011, 0.003, pe, seg=12)
        # Horquilla: arco cromado por encima de la carcasa, con tornillos a los lados.
        yoke = base.torus_obj(f'GEO-yoke-{s}', M['chrome'], yoke_r, 0.0028, cup, arc=math.pi, seg=48, ts=12)
        yoke.location = (0, 0, -0.002)
        for sx in (-1, 1):
            sc = cylinder(f'GEO-yoke_screw-{s}-{sx}', M['chrome'], 0.0045, 0.006, cup, seg=24, bevel=0.0012)
            sc.location = (sx * yoke_r, 0, -0.002)
            sc.rotation_euler = (0, math.pi / 2, 0)
        rig['cups'].append(cup)

    # --- Tatuaje vertical "BARULLO" en la sien (de la v4).
    h = S.toward(Vector((0, 0, 0.215)), Vector((0.93, -0.25, 0.28)), 0.5)
    if h:
        p, n = h
        bm = text_bm('BARULLO', 0.017)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=3, use_grid_fill=True)
        up = Vector((0, 0, 1))
        xaxis = (up - n * up.dot(n)).normalized()
        yaxis = n.cross(xaxis).normalized()
        R = Matrix((xaxis, yaxis, n)).transposed().to_4x4()
        bm.transform(Matrix.Translation(p + n * 0.0006) @ R)
        tat = new_mesh_obj('GEO-tattoo', bm, M['tattoo'], head, smooth_shade=True)
        sw = tat.modifiers.new('wrap', 'SHRINKWRAP')
        sw.target = head
        sw.wrap_method = 'NEAREST_SURFACEPOINT'
        sw.offset = 0.0004

    # --- Joyería: arco de micro-piercings bajo los ojos (v4), barra en la ceja,
    # estrella de cromo en el pómulo, aro en el septum y gotas de cristal.
    k = 0
    for s, ec in zip((-1, 1), eye_c):
        for j in range(7):
            u = j / 6
            x = ec.x + s * eye_r * (0.1 + 1.0 * u)
            z = ec.z - eye_r * (1.15 - 0.55 * u * u)
            hit = S.front(x, z)
            if not hit or rnd.random() < 0.2:
                continue
            p, n = hit
            rr = rnd.choice((0.0009, 0.0012, 0.0016))
            base.sphere_obj(f'GEO-stud-{k}', M['chrome'] if rnd.random() < 0.75 else M['stud_dark'], p + n * rr * 0.4, rr, head)
            k += 1
    # Barra de la ceja: dos bolas en la cola de la ceja izquierda de la pantalla.
    ec = eye_c[0]
    for j, dz in enumerate((0.0, 0.011)):
        hit = S.front(ec.x - eye_r * 0.75, ec.z + eye_r * 1.25 + dz)
        if hit:
            p, n = hit
            base.sphere_obj(f'GEO-brow_ball-{j}', M['chrome'], p + n * 0.0015, 0.0026, head)
    # Estrella de cromo en el pómulo derecho de la pantalla (ref cara blanca con estrella).
    ec = eye_c[1]
    on_surface('GEO-cheek_star', M['liquid_chrome'], S, Vector((0, 0, ec.z)),
               Vector((ec.x + eye_r * 1.3, -0.1, -eye_r * 2.2)), head, 0, kind=star_bm(0.011, 0.0028, 0.0012))
    # Aro en el septum: cuelga de la columela (perfil medido: base de la nariz en z≈0.156).
    nose = S.front(0.0, 0.1565)
    if nose:
        ring_e = empty('SEPTUM', head, loc=nose[0] + Vector((0, 0.0015, -0.0042)))
        ring = base.torus_obj('GEO-septum', M['chrome'], 0.0052, 0.0011, ring_e, seg=48, ts=10)
        ring.rotation_euler = (math.pi / 2 + 0.35, 0, 0)
    # Gotas de cristal sobre la porcelana.
    for j, (cx, cz) in enumerate(((-0.058, 0.168), (0.066, 0.158), (0.072, 0.27))):
        on_surface(f'GEO-drop-{j}', M['drop'], S, Vector((0, 0.0, cz)), Vector((cx * 9, -1, 0)), head,
                   0.0032 + 0.0012 * (j % 2), flat=0.55)
    return rig


# ---------------------------------------------------------------- animación

# Cabeza (rad): los giros los dibujan splines; los ojos se adelantan con sacadas.
# Signos: yaw + = gira hacia su izquierda (derecha de la pantalla); pitch + = barbilla abajo.
HEAD_YAW = [(0, 0.0), (1.8, 0.01), (3.5, 0.25), (5.0, 0.22), (7.0, -0.07), (8.6, -0.05), (10, 0.0)]
HEAD_PITCH = [(0, 0.0), (1.8, 0.0), (3.5, -0.045), (5.0, -0.03), (7.0, 0.06), (8.6, 0.05), (10, 0.0)]
HEAD_ROLL = [(0, 0.0), (1.8, 0.0), (3.5, -0.045), (5.0, -0.035), (7.0, 0.05), (8.6, 0.04), (10, 0.0)]
# Ojos respecto a la cabeza: sacada, y mientras la cabeza alcanza la mirada, se recentran.
EYE_YAW = [(0, 0.0), (1.6, 0.0), (1.74, 0.36), (3.5, 0.12), (4.35, 0.12), (4.43, 0.18), (5.35, 0.17),
           (5.5, -0.21), (7.0, 0.06), (8.6, 0.05), (10, 0.0)]
LID = [(0, 0.12), (1.8, 0.12), (3.5, 0.16), (5.0, 0.16), (7.0, 0.25), (8.6, 0.23), (10, 0.12)]
BLINKS = (1.58, 5.32, 9.0)
JAW = [(0, 0.03), (3.6, 0.03), (4.5, 0.26), (5.5, 0.22), (6.4, 0.04), (10, 0.03)]


def animate(rig):
    head = rig['head']
    head.rotation_mode = 'XYZ'
    lag = 0.14
    for f in range(1, FRAMES + 1):
        sec = (f - 1) / FPS
        t = sec / SECONDS
        yaw = spline(HEAD_YAW, sec) + 0.006 * math.sin(2 * math.pi * 2 * t + 0.7)
        pitch = spline(HEAD_PITCH, sec) + 0.005 * math.sin(2 * math.pi * 3 * t)  # respiración
        roll = spline(HEAD_ROLL, sec)
        head.rotation_euler = (pitch, roll, yaw)
        head.keyframe_insert('rotation_euler', frame=f)

        eyaw = track(EYE_YAW, sec) + 0.012 * math.sin(2 * math.pi * 7 * t)
        for pivot in rig['eyes']:
            pivot.rotation_mode = 'XYZ'
            pivot.rotation_euler = (0.05 - 0.8 * pitch, 0, eyaw)
            pivot.keyframe_insert('rotation_euler', frame=f)
        b = max(blink(sec, a) for a in BLINKS)
        up = spline(LID, sec)
        up = up + (0.55 - up) * b
        for lid_up, lid_low in rig['lids']:
            lid_up.rotation_euler = (up, 0, 0)
            lid_up.keyframe_insert('rotation_euler', frame=f)
            lid_low.rotation_euler = (0.42 - 0.12 * b, 0, 0)
            lid_low.keyframe_insert('rotation_euler', frame=f)

        jaw = max(0.0, spline(JAW, sec))
        rig['jaw_key'].value = jaw
        rig['jaw_key'].keyframe_insert('value', frame=f)
        # Siempre detrás de la ranura: tapa el interior hueco de la cabeza.
        open_h = 0.0016 + 0.0055 * jaw
        rig['cavity'].scale = (0.015 + 0.004 * jaw, 0.004, open_h)
        rig['cavity'].location = (0, 0, -open_h * 0.8)
        rig['cavity'].keyframe_insert('scale', frame=f)
        rig['cavity'].keyframe_insert('location', frame=f)

        # Inercia: los pinchos se quedan atrás al girar (más los largos) y vuelven.
        dyaw = spline(HEAD_YAW, sec - lag) - spline(HEAD_YAW, sec)
        dpitch = spline(HEAD_PITCH, sec - lag) - spline(HEAD_PITCH, sec)
        for piv, rot0, p, length in rig['spikes']:
            k = 0.9 + 6.0 * length
            q = Quaternion((0, 0, 1), dyaw * k * 0.5) @ Quaternion((1, 0, 0), dpitch * k * 0.5)
            piv.rotation_quaternion = q @ rot0
            piv.keyframe_insert('rotation_quaternion', frame=f)
        for cup in rig['cups']:
            cup.scale = (1, 1, 1)
    bpy.context.scene.frame_set(1)


# ---------------------------------------------------------------- render

def setup_render(variant, out, percent=100, samples=64):
    v4.setup_render(variant, out)
    sc = bpy.context.scene
    sc.frame_end = FRAMES
    sc.render.resolution_percentage = percent
    sc.eevee.taa_render_samples = samples
    # Desenfoque de movimiento suave: los giros lentos se ven más fluidos.
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    # Luz de recorte fría desde arriba para que el cromo de la corona tenga brillos largos.
    # Algo más lejos que la v4: los pinchos curvos son más largos y no deben cortarse.
    cam = sc.camera
    target = Vector((0.006, 0, 0.258))
    yaw, elev, dist = math.radians(14), math.radians(7), 1.62
    cam.location = target + Vector((math.sin(yaw) * math.cos(elev), -math.cos(yaw) * math.cos(elev), math.sin(elev))) * dist
    cam.rotation_quaternion = (cam.location - target).to_track_quat('Z', 'Y')
    # Desde atrás: solo roza la corona, no quema la frente.
    base.light('LGT-top_chrome', 'AREA', (0.15, 0.45, 1.1), (0, 0, 0.36), 9, '#F4F0FF', size=0.6, spec=1.0)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--lib', required=True)
    ap.add_argument('--out', default='//frames/')
    ap.add_argument('--variant', default='square', choices=('square', 'wide'))
    ap.add_argument('--frames', default='')
    ap.add_argument('--percent', type=int, default=100)
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--close', default='', help='plano de prueba: lips|phones|crown')
    ap.add_argument('--save', default='')
    args, _ = ap.parse_known_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    base.build_world()
    rig = build(args.lib, M)
    animate(rig)
    setup_render(args.variant, args.out, args.percent, args.samples)
    base.setup_glare()
    if args.close:
        cam = bpy.context.scene.camera
        target, yaw, dist, lens = {
            'lips': (Vector((0, -0.11, 0.132)), 10, 0.32, 85),
            'phones': (Vector((0.15, 0.02, 0.2)), 55, 0.6, 70),
            'crown': (Vector((0, 0, 0.32)), 14, 0.9, 60),
        }[args.close]
        y = math.radians(yaw)
        cam.data.lens = lens
        cam.location = target + Vector((math.sin(y), -math.cos(y), 0.12)) * dist
        cam.rotation_quaternion = (cam.location - target).to_track_quat('Z', 'Y')
    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=args.save)
        print('saved', args.save)
    if args.frames:
        sc = bpy.context.scene
        for part in args.frames.split(','):
            a, _, b = part.partition('-')
            for f in range(int(a), int(b or a) + 1):
                sc.frame_set(f)
                sc.render.filepath = f'{args.out}{args.close}{f:04d}'
                bpy.ops.render.render(write_still=True)
                print('frame', f, flush=True)


if __name__ == '__main__':
    main()
