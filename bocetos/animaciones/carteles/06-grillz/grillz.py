"""Grill de Barullo: el lettering kufi como joya de dientes (oro, pavé de diamantes, rubí en la «o»),
curvado sobre la arcada y visto de frente, para componerlo en la boca de la foto del cartel.

blender -b --factory-startup --python grillz.py -- <wordmark-kufi.svg> <hdri.hdr> <out_dir> [res%] [samples]

Sale <out_dir>/grill.png (RGBA) y <out_dir>/grill.json (caja del wordmark y centros de gemas en fracciones
de la imagen, para los destellos de Remotion).
"""
import bpy, bmesh, json, math, os, random, re, sys
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

A = sys.argv[sys.argv.index('--') + 1:]
SVG, HDRI, OUT = A[:3]
PCT = int(A[3]) if len(A) > 3 else 100
SPP = int(A[4]) if len(A) > 4 else 160
os.makedirs(OUT, exist_ok=True)
random.seed(3)

GOLD = (1.0, 0.71, 0.33)
RUBY = dict(Base_Color=(0.95, 0.02, 0.06), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77)
DIAMOND = dict(Base_Color=(1.0, 1.0, 1.0), Roughness=0.0, Transmission_Weight=1.0, IOR=2.42)

# ---------- contorno → unidades de escena. GRILL_TEXT=13.11 (+ GRILL_KUFI=kufi.json): placa con la fecha en kufi
TEXT = os.environ.get('GRILL_TEXT')
WIDTH = 8.0


def loops(d):
    out = []
    for sub in re.findall(r'M[^M]+', d):
        pts = [tuple(map(float, p.split())) for p in re.findall(r'-?[\d.]+ -?[\d.]+', sub)]
        if pts[0] == pts[-1]:
            pts = pts[:-1]
        out.append(pts)
    return out


raw = []
if TEXT:
    glyphs = json.load(open(os.environ['GRILL_KUFI']))
    x = 0.0
    for ch in TEXT:
        g = glyphs[ch]
        if g.get('d'):
            raw += [[(px + x, py) for px, py in lp] for lp in loops(g['d'])]
        x += g['w'] + 0.75
    IW, IH = x - 0.75, 5.0
else:
    IW, IH = 2906.0, 980.0
    raw = loops(re.search(r' d="([^"]+)"', open(SVG).read()).group(1))
S = WIDTH / IW
polys = [[((x - IW / 2) * S, -(y - IH / 2) * S) for x, y in lp] for lp in raw]

EXT = 0.07          # medio grosor de las letras
BEV = 0.018
R_ARCH = 6.0        # radio de la arcada

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'
sc.cycles.samples = SPP
sc.cycles.use_denoising = True
sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = 2600, 1100
sc.render.resolution_percentage = PCT
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
try:
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'
except TypeError:
    pass


def plain(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for k, v in kw.items():
        s_ = p.inputs[k.replace('_', ' ')]
        s_.default_value = (*v, 1) if isinstance(v, tuple) and s_.type == 'RGBA' else v
    return m


gold = plain('gold', Base_Color=GOLD, Metallic=1.0, Roughness=0.1)
gold_satin = plain('gold_satin', Base_Color=(0.92, 0.62, 0.28), Metallic=1.0, Roughness=0.28)
diamond = plain('diamond', **DIAMOND)
ruby = plain('ruby', **RUBY)


def link(ob):
    sc.collection.objects.link(ob); return ob


def curve_mesh(name, loops, extrude, bevel, z=0.0):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    for poly in loops:
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 1)
        for i, (x, y) in enumerate(poly):
            sp.points[i].co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 3; cu.offset = -bevel * 0.7
    ob = link(bpy.data.objects.new(name, cu)); ob.location.z = z
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def tessellate(ob, max_len=0.06):
    """Triangula y parte las aristas largas: las tapas planas tienen que doblarse con la arcada sin facetas."""
    bm_ = bmesh.new(); bm_.from_mesh(ob.data)
    bmesh.ops.triangulate(bm_, faces=bm_.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    for _ in range(8):
        long_ = [e for e in bm_.edges if e.calc_length() > max_len]
        if not long_:
            break
        bmesh.ops.subdivide_edges(bm_, edges=long_, cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm_, faces=[f for f in bm_.faces if len(f.verts) > 3])
    for f in bm_.faces:          # tapa delantera en oro blanco (asiento del pavé), cantos en oro
        f.material_index = 1 if f.normal.z > 0.9 else 0
    bm_.to_mesh(ob.data); bm_.free()


# letras
letters = curve_mesh('letters', polys, EXT, BEV)
letters.data.materials.append(gold)
letters.data.materials.append(plain('white_gold', Base_Color=(0.93, 0.93, 0.95), Metallic=1.0, Roughness=0.16))
tessellate(letters)

def rect(x0, y0, x1, y1):
    return [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]


extra = []
if TEXT:
    # placa de ónix con marco de oro detrás de la fecha, como la placa del nombre original
    P = 0.32
    hw, hh = WIDTH / 2 + P, IH / 2 * S + P
    bar = curve_mesh('frame', rect(-hw, -hh, hw, hh), EXT * 0.5, 0.05, z=-EXT * 0.9)
    bar.data.materials.append(gold)
    onyx = curve_mesh('onyx', rect(-hw + 0.1, -hh + 0.1, hw - 0.1, hh - 0.1), EXT * 0.5, 0.01, z=-EXT * 0.15)
    onyx.data.materials.append(plain('onyx', Base_Color=(0.012, 0.01, 0.012), Roughness=0.05, Coat_Weight=1.0))
    tessellate(onyx, 0.12)
    for f in onyx.data.polygons:
        f.material_index = 0
    extra.append(onyx)
else:
    # fundas de oro: seis dientes sobre la arcada, de la encía (arriba de las letras) al borde (bajo la base)
    def tooth(x0, x1, top, bot, rc):
        pts = [(x0, top), (x1, top)]
        for k in range(9):                                    # esquina inferior derecha
            a = -k / 8 * math.pi / 2
            pts.append((x1 - rc + rc * math.cos(a), bot + rc + rc * math.sin(a)))
        for k in range(9):                                    # esquina inferior izquierda
            a = -math.pi / 2 - k / 8 * math.pi / 2
            pts.append((x0 + rc + rc * math.cos(a), bot + rc + rc * math.sin(a)))
        return pts
    top_, bot_ = -(0 - IH / 2) * S, -(812 - IH / 2) * S
    widths = [1.2, 1.36, 1.44, 1.44, 1.36, 1.2]
    x = -sum(widths) / 2
    caps = []
    for i, wd in enumerate(widths):
        drop = 0.05 if i in (2, 3) else 0.0                   # los centrales bajan un poco más
        caps.append(tooth(x + 0.025, x + wd - 0.025, top_, bot_ - drop, 0.32))
        x += wd
    bar = curve_mesh('caps', caps, EXT * 0.9, 0.03, z=-EXT * 1.6)
    bar.data.materials.append(gold)
tessellate(bar, 0.12)
for f in bar.data.polygons:
    f.material_index = 0


# ---------- pavé: rejilla hexagonal dentro de las letras (par-impar), con margen al borde
def inside(px, py):
    c = False
    for poly in polys:
        n = len(poly)
        for i in range(n):
            (x1, y1_), (x2, y2) = poly[i], poly[(i + 1) % n]
            if (y1_ > py) != (y2 > py) and px < (x2 - x1) * (py - y1_) / (y2 - y1_) + x1:
                c = not c
    return c


segs = [(poly[i], poly[(i + 1) % len(poly)]) for poly in polys for i in range(len(poly))]


def edge_dist(px, py):
    best = 1e9
    for (x1, y1_), (x2, y2) in segs:
        dx, dy = x2 - x1, y2 - y1_
        L = dx * dx + dy * dy
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1_) * dy) / L))
        ex, ey = x1 + t * dx - px, y1_ + t * dy - py
        best = min(best, ex * ex + ey * ey)
    return math.sqrt(best)


GR, STEP, MARGIN = (0.034, 0.08, 0.06) if TEXT else (0.025, 0.06, 0.046)
bm = bmesh.new()
gem_pts = []
row = 0
yy = IH / 2 * S
while yy > -IH / 2 * S:
    xx = -IW / 2 * S + (STEP / 2 if row % 2 else 0)
    while xx < IW / 2 * S:
        if inside(xx, yy) and edge_dist(xx, yy) > MARGIN:
            jr = GR * random.uniform(0.92, 1.05)
            M = Matrix.Translation((xx, yy, EXT + BEV + jr * 0.1)) @ Matrix.Diagonal((1, 1, 0.62, 1)) @ Matrix.Rotation(random.uniform(0, 6.28), 4, 'Z')
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=jr, matrix=M)
            gem_pts.append((xx, yy, EXT + BEV + jr * 0.3))
        xx += STEP
    yy -= STEP * 0.866
    row += 1
pave = bpy.data.meshes.new('pave'); bm.to_mesh(pave); bm.free()
pave_ob = link(bpy.data.objects.new('pave', pave)); pave_ob.data.materials.append(diamond)

prongs = []
hcx = hcy = 0.0
if not TEXT:
    # rubí en el agujero de la «o» (el lazo que empieza en (2642.5, 614)) + bisel y garras
    hx, hy = (2642.5 - IW / 2) * S, -(614 - IH / 2) * S
    hole = min(polys, key=lambda p: (p[0][0] - hx) ** 2 + (p[0][1] - hy) ** 2)
    hcx = sum(p[0] for p in hole) / len(hole); hcy = sum(p[1] for p in hole) / len(hole)
    rr = 0.9 * min(math.hypot(p[0] - hcx, p[1] - hcy) for p in hole)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rr, location=(hcx, hcy, EXT * 0.35))
    gem = bpy.context.object; gem.scale = (1, 1, 0.62); gem.data.materials.append(ruby)
    bpy.ops.mesh.primitive_torus_add(major_radius=rr * 1.02, minor_radius=rr * 0.11, location=(hcx, hcy, EXT * 0.35), major_segments=64)
    bez = bpy.context.object; bpy.ops.object.shade_smooth(); bez.data.materials.append(gold)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rr * 0.1, location=(hcx + math.cos(a) * rr * 0.98, hcy + math.sin(a) * rr * 0.98, EXT * 0.35 + rr * 0.3))
        pr = bpy.context.object; bpy.ops.object.shade_smooth(); pr.data.materials.append(gold); prongs.append(pr)
    extra += [gem, bez]


def bend(x, y, z):
    """De pie (la cara +z mira a -Y) y curvado alrededor de un eje vertical que queda detrás."""
    X, Yf, Z = x, -z, y
    th = X / R_ARCH; rad = R_ARCH - Yf
    return Vector((rad * math.sin(th), R_ARCH - rad * math.cos(th), Z))


for ob in [letters, bar, pave_ob] + extra + prongs:
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for v in ob.data.vertices:
        v.co = bend(*v.co)
    ob.data.update()
    if ob in (letters, bar):
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
        except (AttributeError, RuntimeError):
            pass

# ---------- luz: estudio + rojos de la boca y del cartel
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, 0.9)
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI)
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs[1].default_value = 0.8
out = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
nt.links.new(env.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs[0], out.inputs[0])


def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; t = m.node_tree
    [t.nodes.remove(n) for n in list(t.nodes)]
    em = t.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    o_ = t.nodes.new('ShaderNodeOutputMaterial'); t.links.new(em.outputs[0], o_.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False


def area(name, loc, size, energy, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = link(bpy.data.objects.new(name, l)); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


softbox((0, -9, 6), (14, 2.6), 2.6)                       # cenital frontal: el brillo de arriba de la foto
softbox((0, -8, -5), (14, 2.0), 1.6, (1.0, 0.18, 0.12))    # lengua y labio: reflejo rojo desde abajo
softbox((-8, -4, 0.5), (1.2, 7), 2.2, (1.0, 0.08, 0.05))   # rim rojo
softbox((8, -4, 0.5), (1.2, 7), 2.2, (1.0, 0.08, 0.05))
area('key', (-3, -7, 4), 4, 1400, (1.0, 0.95, 0.9))
area('spark', (2.5, -7, 2.5), 0.4, 900)                     # puntos duros: chispa en los diamantes
area('spark2', (-1.5, -8, 1.0), 0.3, 500)
softbox((0, -12, 1.5), (5, 0.5), 3.0)                      # tira frontal: brillo en la cara de las letras

cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 135
cam = link(bpy.data.objects.new('cam', cam_d)); cam.location = (0, -34, float(os.environ.get('GRILL_CAMZ', -0.6)))
cam.rotation_euler = (Vector((0, 0, 0.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam

sc.render.filepath = os.path.join(OUT, 'grill.png')
bpy.ops.render.render(write_still=True)


def proj(v):
    c = world_to_camera_view(sc, cam, v)
    return [round(c.x, 5), round(1 - c.y, 5)]


random.seed(11)
sample = random.sample(gem_pts, min(70, len(gem_pts)))
data = {
    'w': sc.render.resolution_x, 'h': sc.render.resolution_y,
    'gems': [proj(bend(*p)) for p in sample],
    'ruby': proj(bend(hcx, hcy, EXT)),
    'npave': len(gem_pts),
}
json.dump(data, open(os.path.join(OUT, 'grill.json'), 'w'))
print('RENDERED', sc.render.filepath, len(gem_pts), 'gemas')
