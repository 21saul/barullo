"""The star 'o' of barullo as a medal / insignia. blender -b --factory-startup --python medal.py -- <dir> <variant>"""
import bpy, json, math, os, sys, random
from mathutils import Vector

_A = sys.argv[sys.argv.index('--') + 1:]
D, VAR = _A[:2]
OUT = _A[2] if len(_A) > 2 else None
MT = os.path.join(D, 'tex', 'medal')
fr = json.load(open(os.path.join(MT, 'frame.json')))
CX, CY, HS = fr['cx'], fr['cy'], fr['hs']
SIZE = 3.0
S2 = SIZE / (2 * HS)

SILVER = (0.92, 0.92, 0.94); GOLD = (1.0, 0.71, 0.33); OLDGOLD = (0.85, 0.6, 0.3); BLACK = (0.03, 0.03, 0.035)
NIELLO = (0.05, 0.04, 0.04)
GEMS = {
    'rubi': dict(facet=True, Base_Color=(0.95, 0.02, 0.06), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77),
    'turquesa': dict(facet=False, Base_Color=(0.05, 0.6, 0.58), Roughness=0.18, Coat_Weight=1.0),
    'zafiro': dict(facet=True, Base_Color=(0.05, 0.18, 0.95), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77),
    'esmeralda': dict(facet=True, Base_Color=(0.02, 0.75, 0.3), Roughness=0.0, Transmission_Weight=1.0, IOR=1.58),
    'coral': dict(facet=False, Base_Color=(1.0, 0.33, 0.28), Roughness=0.25, Coat_Weight=1.0),
    'perla': dict(facet=False, Base_Color=(0.95, 0.92, 0.87), Roughness=0.12, Coat_Weight=1.0, Sheen_Weight=0.6),
    'amatista': dict(facet=True, Base_Color=(0.55, 0.12, 0.85), Roughness=0.0, Transmission_Weight=1.0, IOR=1.54),
    'diamante': dict(facet=True, Base_Color=(1.0, 1.0, 1.0), Roughness=0.0, Transmission_Weight=1.0, IOR=2.42),
    'ambar': dict(facet=False, Base_Color=(1.0, 0.45, 0.05), Roughness=0.08, Transmission_Weight=0.7, IOR=1.54, Coat_Weight=1.0),
    'onix': dict(facet=False, Base_Color=(0.01, 0.01, 0.012), Roughness=0.04, Coat_Weight=1.0),
    'aguamarina': dict(facet=True, Base_Color=(0.45, 0.8, 1.0), Roughness=0.0, Transmission_Weight=1.0, IOR=1.58),
    'espinela': dict(facet=True, Base_Color=(0.5, 0.02, 0.25), Roughness=0.0, Transmission_Weight=1.0, IOR=1.72),
    'rubi_cabujon': dict(facet=False, Base_Color=(0.75, 0.01, 0.03), Roughness=0.06, Coat_Weight=1.0, Subsurface_Weight=0.3),
    'granate': dict(facet=True, Base_Color=(0.45, 0.0, 0.03), Roughness=0.0, Transmission_Weight=1.0, IOR=1.79),
    'opalo': dict(facet=False, Base_Color=(0.85, 0.93, 1.0), Roughness=0.1, Coat_Weight=1.0, Sheen_Weight=0.8, Thin_Film_Thickness=420.0),
}
# MEDAL_ESTILOS: otro catálogo (p. ej. propuestas); MEDAL_RES / MEDAL_SAMPLES: previews rápidas
_EST = json.load(open(os.environ.get('MEDAL_ESTILOS') or os.path.join(D, 'estilos.json')))
def _c(v):
    if isinstance(v, list) and v and isinstance(v[0], str):  # paleta: ["CARMIN", "GRANATE", ...]
        return ('pal', [_c(x) for x in v])
    return tuple(_EST['_colors'][v]) if isinstance(v, str) and v in _EST['_colors'] else v
def estilo(name):
    e = _EST[name]
    gem = tuple(e['gema']) if e['gema'] else None
    return dict(metal=_c(e['metal']), rough=e['rough'], letra=e['letra'], medalla=e['medalla'],
                enamel=_c(e['esmalte']), linecol=_c(e['linea']), line_metal=e['linea_metal'], gem=gem,
                raised=e.get('relieve', False), finish=e.get('acabado'),
                hole=e.get('hueco', True), thick=e.get('grosor', 0.17), depth=e.get('profundidad', 1.0),
                center=e.get('gema_centro', True))


sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get('MEDAL_SAMPLES', 112)); sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = (1100, 1540) if VAR == 'med-cinta' else (1400, 1400)
if os.environ.get('MEDAL_RES'):
    sc.render.resolution_percentage = int(os.environ['MEDAL_RES'])
sc.render.film_transparent = VAR not in ('med-pin',)
sc.render.image_settings.color_mode = 'RGBA'
try:
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
except TypeError:
    pass

def world():
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, 0.6)
    env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(D, 'hdri', 'studio_small_09.hdr'))
    b1 = nt.nodes.new('ShaderNodeBackground'); b1.inputs[1].default_value = 0.9
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], b1.inputs['Color']); nt.links.new(b1.outputs[0], out.inputs[0])

def plain(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for k, v in kw.items():
        if k == 'facet': continue
        s_ = p.inputs[k.replace('_', ' ')]
        s_.default_value = (*v, 1) if isinstance(v, tuple) and s_.type == 'RGBA' else v
    return m

def math_(nt, op, a, b=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]

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

def engraved(name, metal, rough, pat, enamel=None, linecol=None, line_metal=False, raised=False, scale=SIZE, folder=MT, finish=None, depth=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / scale, 1 / scale, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); uv = mp.outputs['Vector']
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Normal'], sep.inputs['Vector'])
    front = math_(nt, 'GREATER_THAN', sep.outputs['Z'], 0.9)
    def img(fn, nc=True):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(folder, fn))
        if nc: t.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(uv, t.inputs['Vector']); return t.outputs['Color']
    lines = math_(nt, 'MULTIPLY', img(f'{pat}-lines.png'), front)
    if enamel == 'none':
        fill = math_(nt, 'MULTIPLY', front, 0.0); ecol = (0, 0, 0)
    else:
        fill = math_(nt, 'MULTIPLY', img(f'{pat}-fill.png'), front)
        if isinstance(enamel, tuple) and enamel and enamel[0] == 'pal':
            # paleta: {pat}-idx.png vale 0 / 0.5 / 1 según la zona; una rampa constante le da su tono
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(folder, f'{pat}-idx.png'))
            t.image.colorspace_settings.name = 'Non-Color'; t.interpolation = 'Closest'; nt.links.new(uv, t.inputs['Vector'])
            ramp = nt.nodes.new('ShaderNodeValToRGB'); cr = ramp.color_ramp; cr.interpolation = 'CONSTANT'
            cols = enamel[1] + [enamel[1][-1]] * (3 - len(enamel[1]))
            cr.elements[0].position = 0.0; cr.elements[0].color = (*cols[0], 1)
            cr.elements[1].position = 0.25; cr.elements[1].color = (*cols[1], 1)
            e3 = cr.elements.new(0.75); e3.color = (*cols[2], 1)
            nt.links.new(t.outputs['Color'], ramp.inputs['Fac']); ecol = ramp.outputs['Color']
        else:
            ecol = img(f'{pat}-col.png', nc=False) if enamel is None else enamel
    col = mixc(nt, fill, metal, ecol); col = mixc(nt, lines, col, linecol or NIELLO)
    nt.links.new(col, p.inputs['Base Color'])
    met = mixf(nt, lines, mixf(nt, fill, 1.0, 0.0), 1.0 if line_metal else 0.35)
    nt.links.new(met, p.inputs['Metallic'])
    nt.links.new(mixf(nt, lines, mixf(nt, fill, rough, 0.05), 0.12 if line_metal else 0.5), p.inputs['Roughness'])
    nt.links.new(fill, p.inputs['Coat Weight']); p.inputs['Coat Roughness'].default_value = 0.02
    h = math_(nt, 'ADD', lines, math_(nt, 'MULTIPLY', fill, 0.45))
    bm = nt.nodes.new('ShaderNodeBump'); bm.invert = not raised
    bm.inputs['Strength'].default_value = min(1.0, 0.9 * depth); bm.inputs['Distance'].default_value = 0.01 * depth
    nt.links.new(h, bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], p.inputs['Normal'])
    if finish == 'martillado':  # metal batido a martillo: celdas de Voronoi en el metal visto
        vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 9.0; nt.links.new(uv, vo.inputs['Vector'])
        hb = nt.nodes.new('ShaderNodeBump'); hb.inputs['Strength'].default_value = 0.35; hb.inputs['Distance'].default_value = 0.02
        nt.links.new(math_(nt, 'MULTIPLY', vo.outputs['Distance'], math_(nt, 'SUBTRACT', 1.0, fill)), hb.inputs['Height'])
        nt.links.new(hb.outputs['Normal'], bm.inputs['Normal'])
    elif finish == 'cepillado':  # metal cepillado: rayado fino concéntrico + reflejo anisótropo
        gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
        mp2 = nt.nodes.new('ShaderNodeMapping'); mp2.inputs['Location'].default_value = (-0.5, -0.5, 0); nt.links.new(uv, mp2.inputs['Vector'])
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 2
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; nt.links.new(mp2.outputs['Vector'], ln.inputs[0])
        rings = math_(nt, 'MULTIPLY', ln.outputs['Value'], 900.0)
        nt.links.new(rings, nz.inputs['Vector'])
        hb = nt.nodes.new('ShaderNodeBump'); hb.inputs['Strength'].default_value = 0.25; hb.inputs['Distance'].default_value = 0.004
        nt.links.new(math_(nt, 'MULTIPLY', nz.outputs['Fac'], math_(nt, 'SUBTRACT', 1.0, fill)), hb.inputs['Height'])
        nt.links.new(hb.outputs['Normal'], bm.inputs['Normal'])
        if 'Anisotropic' in p.inputs: p.inputs['Anisotropic'].default_value = 0.6
    return m

def star(extrude=0.17, bevel=0.03, hole=True):
    cu = bpy.data.curves.new('star', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    for poly in ((fr['outer'], fr['hole']) if hole else (fr['outer'],)):
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 2)
        for i, (x, y) in enumerate(poly[:-1]):
            sp.points[i].co = ((x - CX) * S2, -(y - CY) * S2, 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 4; cu.offset = -bevel * 0.8
    ob = bpy.data.objects.new('star', cu); sc.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active

def gem(parent, kind, metal, z=0.04):
    hole = fr['hole']
    a = 0.5 * abs(sum(hole[i][0] * hole[i + 1][1] - hole[i + 1][0] * hole[i][1] for i in range(len(hole) - 1)))
    r = math.sqrt(a / math.pi) * S2 * 0.8
    spec = GEMS[kind]
    if spec['facet']:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(0, 0, z))
        g = bpy.context.object; g.scale = (1, 1, 0.62)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, z), segments=64, ring_count=32)
        g = bpy.context.object; g.scale = (1, 1, 0.55); bpy.ops.object.shade_smooth()
    g.data.materials.append(plain(kind, **spec))
    if z > 0.1 and spec['facet']:
        # medalla maciza: fondo de plata pulida bajo la gema transparente, si no refleja el metal oscuro y sale negra
        bpy.ops.mesh.primitive_cylinder_add(radius=r * 0.97, depth=0.01, location=(0, 0, z - r * 0.5), vertices=64)
        fo = bpy.context.object; fo.data.materials.append(plain('foil', Base_Color=(0.97, 0.97, 0.98), Metallic=1.0, Roughness=0.02)); fo.parent = parent
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 1.02, minor_radius=r * 0.12, location=(0, 0, z), major_segments=64)
    b = bpy.context.object; bpy.ops.object.shade_smooth(); b.data.materials.append(plain('bezel', Base_Color=metal, Metallic=1.0, Roughness=0.08))
    # prongs
    for k in range(8):
        ang = k * math.pi / 4 + math.pi / 8
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 0.11, location=(math.cos(ang) * r * 0.98, math.sin(ang) * r * 0.98, z + r * 0.3))
        pr = bpy.context.object; bpy.ops.object.shade_smooth(); pr.data.materials.append(b.data.materials[0]); pr.parent = parent
    g.parent = parent; b.parent = parent

def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; nt = m.node_tree
    [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False

def camera(loc, target=(0, 0, 0), lens=70):
    c = bpy.data.cameras.new('cam'); c.lens = lens
    o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = o

def lights(k=1.0):
    softbox((0, -9, 5), (12, 2.4), 2.4 * k)
    softbox((0, -9, -4), (12, 1.2), 1.0 * k, (1, 0.75, 0.85))
    softbox((-7, -5, 0.5), (1.0, 6), 1.6 * k, (1, 0.6, 0.25))
    area('key', (-3, -6, 5), 4, 700 * k)
    area('rimP', (4, 3, 2), 2.5, 1500 * k, (1, 0.22, 0.55))
    area('rimO', (-4, 3, -1), 2.5, 1000 * k, (1, 0.5, 0.12))

world()
root = bpy.data.objects.new('root', None); sc.collection.objects.link(root)

def pave(parent, kind, metal, n, z=0.2):
    """Anillo de n gemas pequeñas engastadas en la cara, alrededor del agujero central."""
    hole = fr['hole']
    a = 0.5 * abs(sum(hole[i][0] * hole[i + 1][1] - hole[i + 1][0] * hole[i][1] for i in range(len(hole) - 1)))
    R = math.sqrt(a / math.pi) * S2 * 1.32; rg = R * 0.13
    gm = plain(kind + '_p', **GEMS[kind]); bz = plain('bezel_p', Base_Color=metal, Metallic=1.0, Roughness=0.08)
    for k in range(n):
        ang = k * 2 * math.pi / n + math.pi / n
        x, y = math.cos(ang) * R, math.sin(ang) * R
        if GEMS[kind]['facet']:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rg, location=(x, y, z))
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=rg, location=(x, y, z), segments=24, ring_count=12); bpy.ops.object.shade_smooth()
        g = bpy.context.object; g.scale = (1, 1, 0.6); g.data.materials.append(gm); g.parent = parent
        bpy.ops.mesh.primitive_torus_add(major_radius=rg * 1.05, minor_radius=rg * 0.16, location=(x, y, z - rg * 0.15), major_segments=32, minor_segments=8)
        b = bpy.context.object; bpy.ops.object.shade_smooth(); b.data.materials.append(bz); b.parent = parent

def std_star(metal, rough, pat, enamel=None, gemkind='rubi', linecol=None, line_metal=False, raised=False, finish=None, gemn=1,
             hole=True, thick=0.17, depth=1.0, center=True):
    s = star(extrude=thick, hole=hole); s.parent = root
    s.data.materials.append(engraved('st', metal, rough, pat, enamel, linecol, line_metal, raised=raised, finish=finish, depth=depth))
    # maciza (sin hueco): la gema va engastada sobre la cara, no dentro del agujero
    # gema_centro: false deja el agujero abierto (se ve a través); el pavé, si lo hay, sigue
    if gemkind and center: gem(s, gemkind, metal, z=0.04 if hole else thick + 0.05)
    if gemkind and gemn >= 6: pave(s, gemkind, metal, gemn, z=thick + 0.03)
    return s

if VAR in _EST:
    _e = estilo(VAR)
    std_star(_e['metal'], _e['rough'], _e['medalla'], _e['enamel'], _e['gem'][0] if _e['gem'] else None, _e['linecol'], _e['line_metal'],
             raised=_e['raised'], finish=_e['finish'], gemn=_e['gem'][1] if _e['gem'] else 1,
             hole=_e['hole'], thick=_e['thick'], depth=_e['depth'], center=_e['center'])
elif VAR == 'med-plata-rubi':
    std_star(SILVER, 0.04, 'rosa')
elif VAR == 'med-oro-turquesa':
    std_star(OLDGOLD, 0.14, 'girih', enamel=(0.03, 0.55, 0.55), gemkind='turquesa')
elif VAR == 'med-negro-sol':
    std_star(BLACK, 0.05, 'sol', enamel='none', linecol=SILVER, line_metal=True)
elif VAR == 'med-puas':
    std_star(SILVER, 0.04, 'rosa')
    random.seed(7); chrome = plain('chrome', Base_Color=SILVER, Metallic=1.0, Roughness=0.04)
    for k in range(32):
        a = k * 2 * math.pi / 32 + math.pi / 32
        L = (1.1 if k % 2 == 0 else 0.7) * random.uniform(0.9, 1.1)
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.13, radius2=0.0, depth=L, location=(math.cos(a) * (1.05 + L / 2), math.sin(a) * (1.05 + L / 2), -0.06), rotation=(0, math.radians(90), a))
        c = bpy.context.object; c.data.materials.append(chrome); c.parent = root
elif VAR == 'med-moneda':
    bpy.ops.mesh.primitive_cylinder_add(radius=2.05, depth=0.16, location=(0, 0, -0.12), vertices=128)
    coin = bpy.context.object; bv = coin.modifiers.new('b', 'BEVEL'); bv.width = 0.03; bv.segments = 3
    bpy.ops.object.shade_smooth(); coin.parent = root
    coin.data.materials.append(engraved('coin', GOLD, 0.1, 'coin', enamel='none', scale=4.1))
    s = star(extrude=0.12); s.location.z = 0.12; s.parent = root
    s.data.materials.append(engraved('st', SILVER, 0.04, 'rosa')); gem(s, 'rubi', SILVER)
elif VAR == 'med-cinta':
    s = std_star(SILVER, 0.04, 'rosa'); s.location = (0, -1.25, 0)
    tip = max(fr['outer'], key=lambda q: -q[1])  # topmost point
    ty = -(tip[1] - CY) * S2 - 1.25
    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.035, location=(0, ty + 0.14, 0), rotation=(0, math.radians(90), 0))
    ring = bpy.context.object; bpy.ops.object.shade_smooth(); ring.data.materials.append(plain('ring', Base_Color=SILVER, Metallic=1, Roughness=0.06))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, ty + 1.45, 0.02))
    rb = bpy.context.object; rb.scale = (1.15, 2.3, 1); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=24); bpy.ops.object.mode_set(mode='OBJECT')
    bottom = ty + 1.45 - 1.15
    for v in rb.data.vertices:
        v.co.z = 0.05 * math.sin(v.co.y * 3.0) + 0.04 * (v.co.x ** 2)
        if v.co.y < -1.0:  # V-cut the ribbon bottom towards the ring
            f = (-1.0 - v.co.y) / 0.15
            v.co.x *= max(0.25, 1 - 0.75 * f)
    rm = bpy.data.materials.new('ribbon'); rm.use_nodes = True
    p = next(n for n in rm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'); p.inputs['Roughness'].default_value = 0.45
    if 'Sheen Weight' in p.inputs: p.inputs['Sheen Weight'].default_value = 0.6
    t = rm.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(MT, 'ribbon.png'))
    rm.node_tree.links.new(t.outputs['Color'], p.inputs['Base Color']); rb.data.materials.append(rm)
    so = rb.modifiers.new('s', 'SOLIDIFY'); so.thickness = 0.01
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, ty + 2.62, 0.05))
    bar = bpy.context.object; bar.scale = (1.3, 0.16, 0.1)
    bv = bar.modifiers.new('b', 'BEVEL'); bv.width = 0.03; bv.segments = 3
    bar.data.materials.append(plain('bar', Base_Color=SILVER, Metallic=1, Roughness=0.06))
    for o in (ring, rb, bar):
        o.parent = root
elif VAR == 'med-pin':
    s = star(extrude=0.05, bevel=0.018); s.parent = root
    s.data.materials.append(engraved('pin', GOLD, 0.08, 'rosa', linecol=GOLD, line_metal=True, raised=True))
    gem(s, 'rubi', GOLD, z=0.02)
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, -0.08))
    cl = bpy.context.object; cm = bpy.data.materials.new('cloth'); cm.use_nodes = True; nt = cm.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value = (0.012, 0.012, 0.016, 1); p.inputs['Roughness'].default_value = 0.9
    if 'Sheen Weight' in p.inputs: p.inputs['Sheen Weight'].default_value = 0.5
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 60; wv.inputs['Distortion'].default_value = 2
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35
    nt.links.new(wv.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], p.inputs['Normal'])
    cl.data.materials.append(cm)

if VAR == 'med-pin':
    root.rotation_euler = (0, 0, math.radians(-12))
    camera((0.6, -4.2, 6.2), (0, 0, 0), lens=58)
    area('key', (-3, -3, 6), 3, 900, (1, 0.96, 0.92)); area('rim', (4, 4, 3), 3, 600, (1, 0.3, 0.55))
    softbox((0, -6, 7), (8, 2), 2.0)
elif VAR == 'med-cinta':
    root.rotation_euler = (math.radians(90), 0, math.radians(-10))
    camera((0.9, -11, 0.4), (0, 0, 0.35), lens=66)
    lights()
else:
    root.rotation_euler = (math.radians(83), 0, math.radians(-14))
    camera((0.8, -9.5, 1.2), (0, 0, 0), lens=100 if VAR not in ('med-puas', 'med-moneda') else 70)
    lights()

sc.render.filepath = OUT or os.path.join(D, 'medal', f'{VAR}.png')
bpy.ops.render.render(write_still=True)
print('RENDERED', sc.render.filepath)
