"""Medalla «o» de plata joya con rubí: geometría y materiales compartidos por los carteles 01 y 03.

Sale de bocetos/scripts/medal.py (estilo plata-joya-rubi: plata, patrón 'rosa', esmalte de paleta, rubí).
Diferencia: grabado y rubí en las DOS caras, y la trasera lee la textura con x invertida, de modo que
tras medio giro sobre su eje vertical la medalla se ve idéntica (bucles de medio giro).
"""
import bpy, json, math, os

SILVER = (0.92, 0.92, 0.94)
NIELLO = (0.05, 0.04, 0.04)
RUBY = dict(Base_Color=(0.95, 0.02, 0.06), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77)
EXTRUDE = 0.17
# gemas de bocetos/scripts/medal.py; facet=False: cabujón liso
GEMS = {
    'rubi': dict(facet=True, Base_Color=(0.95, 0.02, 0.06), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77),
    'turquesa': dict(facet=False, Base_Color=(0.05, 0.6, 0.58), Roughness=0.18, Coat_Weight=1.0),
    'zafiro': dict(facet=True, Base_Color=(0.05, 0.18, 0.95), Roughness=0.0, Transmission_Weight=1.0, IOR=1.77),
    'esmeralda': dict(facet=True, Base_Color=(0.02, 0.75, 0.3), Roughness=0.0, Transmission_Weight=1.0, IOR=1.58),
    'coral': dict(facet=False, Base_Color=(1.0, 0.33, 0.28), Roughness=0.25, Coat_Weight=1.0),
    'perla': dict(facet=False, Base_Color=(0.95, 0.92, 0.87), Roughness=0.12, Coat_Weight=1.0, Sheen_Weight=0.6),
}


def estilo(name, path):
    """Un estilo de bocetos/scripts/estilos.json, con los colores resueltos."""
    est = json.load(open(path))
    c = lambda v: tuple(est['_colors'][v]) if isinstance(v, str) and v in est['_colors'] else v
    e = est[name]
    return dict(metal=c(e['metal']), rough=e['rough'], pat=e['medalla'], enamel=c(e['esmalte']),
                linecol=c(e['linea']), line_metal=e['linea_metal'], gem=e['gema'][0] if e['gema'] else None)


class Medal:
    def __init__(self, tex_dir, size=3.0):
        """tex_dir: .../logo-alfombra/tex/medal (frame.json + texturas de patrón)."""
        self.MT = tex_dir
        self.fr = json.load(open(os.path.join(tex_dir, 'frame.json')))
        self.SIZE = size
        self.S2 = size / (2 * self.fr['hs'])

    # ---------- materiales
    @staticmethod
    def plain(name, **kw):
        m = bpy.data.materials.new(name); m.use_nodes = True
        p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        for k, v in kw.items():
            if k == 'facet': continue
            s_ = p.inputs[k.replace('_', ' ')]
            s_.default_value = (*v, 1) if isinstance(v, tuple) and s_.type == 'RGBA' else v
        return m

    def engraved(self, name='st', metal=SILVER, rough=0.04, pat='rosa', enamel=None, linecol=None, line_metal=False):
        """Como engraved() de medal.py. enamel: None = paleta de la textura, 'none' = sin esmalte, o un color."""
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
        p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

        def math_(op, a, b=None):
            n = nt.nodes.new('ShaderNodeMath'); n.operation = op
            for i, v in enumerate((a, b)):
                if v is None: continue
                if isinstance(v, (int, float)): n.inputs[i].default_value = v
                else: nt.links.new(v, n.inputs[i])
            return n.outputs[0]

        def mix(kind, fac, a, b):
            n = nt.nodes.new('ShaderNodeMix'); n.data_type = kind; nt.links.new(fac, n.inputs['Factor'])
            for sock, v in (('A', a), ('B', b)):
                if isinstance(v, (tuple, int, float)): n.inputs[sock].default_value = (*v, 1) if isinstance(v, tuple) else v
                else: nt.links.new(v, n.inputs[sock])
            return n.outputs['Result']

        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Normal'], sep.inputs['Vector'])
        face = math_('GREATER_THAN', math_('ABSOLUTE', sep.outputs['Z']), 0.9)
        side = math_('SIGN', sep.outputs['Z'])
        sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs['Vector'])
        cm = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(math_('MULTIPLY', sp.outputs['X'], side), cm.inputs['X']); nt.links.new(sp.outputs['Y'], cm.inputs['Y'])
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / self.SIZE, 1 / self.SIZE, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)
        nt.links.new(cm.outputs['Vector'], mp.inputs['Vector']); uv = mp.outputs['Vector']

        def img(fn, nc=True):
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(self.MT, fn))
            if nc: t.image.colorspace_settings.name = 'Non-Color'
            nt.links.new(uv, t.inputs['Vector']); return t.outputs['Color']
        lines = math_('MULTIPLY', img(f'{pat}-lines.png'), face)
        if enamel == 'none':
            fill = math_('MULTIPLY', face, 0.0); ecol = (0, 0, 0)
        else:
            fill = math_('MULTIPLY', img(f'{pat}-fill.png'), face)
            ecol = img(f'{pat}-col.png', nc=False) if enamel is None else enamel
        col = mix('RGBA', fill, metal, ecol); col = mix('RGBA', lines, col, linecol or NIELLO)
        nt.links.new(col, p.inputs['Base Color'])
        nt.links.new(mix('FLOAT', lines, mix('FLOAT', fill, 1.0, 0.0), 1.0 if line_metal else 0.35), p.inputs['Metallic'])
        nt.links.new(mix('FLOAT', lines, mix('FLOAT', fill, rough, 0.05), 0.12 if line_metal else 0.5), p.inputs['Roughness'])
        nt.links.new(fill, p.inputs['Coat Weight']); p.inputs['Coat Roughness'].default_value = 0.02
        h = math_('ADD', lines, math_('MULTIPLY', fill, 0.45))
        bm = nt.nodes.new('ShaderNodeBump'); bm.invert = True
        bm.inputs['Strength'].default_value = 0.9; bm.inputs['Distance'].default_value = 0.01 * self.SIZE / 3
        nt.links.new(h, bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], p.inputs['Normal'])
        return m

    # ---------- geometría
    def star(self, bevel=0.03):
        fr, S2 = self.fr, self.S2
        k = self.SIZE / 3
        cu = bpy.data.curves.new('star', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
        for poly in (fr['outer'], fr['hole']):
            sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 2)
            for i, (x, y) in enumerate(poly[:-1]):
                sp.points[i].co = ((x - fr['cx']) * S2, -(y - fr['cy']) * S2, 0, 1)
            sp.use_cyclic_u = True
        cu.extrude = EXTRUDE * k; cu.bevel_depth = bevel * k; cu.bevel_resolution = 4; cu.offset = -bevel * k * 0.8
        ob = bpy.data.objects.new('star', cu); bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        bpy.ops.object.convert(target='MESH')
        return bpy.context.view_layer.objects.active

    def gem(self, parent, metal=SILVER, s=1, ruby_mat=None, kind='rubi'):
        """Gema (rubí facetado por defecto) + bisel + 8 garras; s=-1 en la cara trasera. Devuelve (gema, radio)."""
        hole = self.fr['hole']; k = self.SIZE / 3
        a = 0.5 * abs(sum(hole[i][0] * hole[i + 1][1] - hole[i + 1][0] * hole[i][1] for i in range(len(hole) - 1)))
        r = math.sqrt(a / math.pi) * self.S2 * 0.8
        z = 0.04 * k * s
        spec = GEMS[kind]
        if spec['facet']:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(0, 0, z))
            g = bpy.context.object; g.scale = (1, 1, 0.62)
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, z), segments=64, ring_count=32)
            g = bpy.context.object; g.scale = (1, 1, 0.55); bpy.ops.object.shade_smooth()
        g.name = f'ruby{s}'
        g.data.materials.append(ruby_mat or bpy.data.materials.get(kind) or self.plain(kind, **spec))
        bpy.ops.mesh.primitive_torus_add(major_radius=r * 1.02, minor_radius=r * 0.12, location=(0, 0, z), major_segments=64)
        b = bpy.context.object; bpy.ops.object.shade_smooth()
        bez = bpy.data.materials.get('bezel') or self.plain('bezel', Base_Color=metal, Metallic=1.0, Roughness=0.08)
        b.data.materials.append(bez)
        for i in range(8):
            ang = i * math.pi / 4 + math.pi / 8
            bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 0.11, location=(math.cos(ang) * r * 0.98, math.sin(ang) * r * 0.98, z + s * r * 0.3))
            pr = bpy.context.object; bpy.ops.object.shade_smooth(); pr.data.materials.append(bez); pr.parent = parent
        g.parent = parent; b.parent = parent
        return g, r

    def build(self, parent=None, two_sided=True, ruby_mat=None):
        """Medalla completa centrada en el origen, normal +Z. Devuelve (estrella, rubí, radio gema)."""
        s = self.star(); s.data.materials.append(self.engraved())
        if parent is not None:
            s.parent = parent
        ruby, r = self.gem(s, s=1, ruby_mat=ruby_mat)
        if two_sided:
            self.gem(s, s=-1, ruby_mat=ruby_mat)
        return s, ruby, r

    def build_style(self, st, parent=None):
        """Medalla de dos caras con un estilo de estilo(). Devuelve (estrella, gema o None, radio gema)."""
        s = self.star()
        s.data.materials.append(self.engraved('st', st['metal'], st['rough'], st['pat'], st['enamel'], st['linecol'], st['line_metal']))
        if parent is not None:
            s.parent = parent
        if not st['gem']:
            return s, None, 0.0
        g, r = self.gem(s, st['metal'], 1, kind=st['gem'])
        self.gem(s, st['metal'], -1, kind=st['gem'])
        return s, g, r
