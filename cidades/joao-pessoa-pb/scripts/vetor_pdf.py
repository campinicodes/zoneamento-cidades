"""Utilitários para vetorizar mapas oficiais em PDF vetorial (PyMuPDF get_drawings)
e georreferenciar por regressão linear sobre os rótulos da grade UTM impressos no mapa.
Uso autorizado pela tarefa: geometria aproximada, oficial:false, com erro estimado."""
import re, math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, mapping, shape
from shapely.ops import unary_union, transform as shp_transform
from shapely.validation import make_valid
from pyproj import Transformer

TOL = 0.05

def _bez(p0, p1, p2, p3, n=6):
    pts = []
    for k in range(1, n + 1):
        t = k / n; u = 1 - t
        pts.append((u**3*p0.x + 3*u*u*t*p1.x + 3*u*t*t*p2.x + t**3*p3.x,
                    u**3*p0.y + 3*u*u*t*p1.y + 3*u*t*t*p2.y + t**3*p3.y))
    return pts

def rings_from_items(items):
    rings, cur = [], []
    def close():
        nonlocal cur
        if len(cur) >= 3:
            rings.append(cur)
        cur = []
    for it in items:
        op = it[0]
        if op == 're':
            close(); r = it[1]
            rings.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]); continue
        if op == 'qu':
            close(); q = it[1]
            rings.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]); continue
        p0 = it[1]
        if cur and (abs(cur[-1][0] - p0.x) > TOL or abs(cur[-1][1] - p0.y) > TOL):
            close()
        if not cur:
            cur = [(p0.x, p0.y)]
        if op == 'l':
            cur.append((it[2].x, it[2].y))
        elif op == 'c':
            cur.extend(_bez(it[1], it[2], it[3], it[4]))
    close()
    return rings

def _signed_area(r):
    a = 0.0
    for i in range(len(r)):
        x1, y1 = r[i]; x2, y2 = r[(i + 1) % len(r)]
        a += x1 * y2 - x2 * y1
    return a / 2

def path_to_geom(items, even_odd=True):
    rings = rings_from_items(items)
    polys = []
    for r in rings:
        pg = make_valid(Polygon(r))
        if not pg.is_empty and pg.area > 1e-6:
            polys.append((pg, _signed_area(r)))
    if not polys:
        return None
    if even_odd:
        g = None
        for pg, _ in sorted(polys, key=lambda t: -t[0].area):
            g = pg if g is None else g.symmetric_difference(pg)
        return make_valid(g)
    # nonzero: orientação majoritária (por área) = preenchido; oposta = furo
    pos = sum(p.area for p, s in polys if s > 0); neg = sum(p.area for p, s in polys if s < 0)
    sign = 1 if pos >= neg else -1
    fill = unary_union([p for p, s in polys if s * sign > 0])
    holes = unary_union([p for p, s in polys if s * sign < 0]) if any(s * sign < 0 for _, s in polys) else None
    return make_valid(fill.difference(holes) if holes is not None else fill)

def fit_grid(page, xpat=r'^\d{6}$', ypat=r'^\d{7}$'):
    """Regressão linear coordenada UTM ~ posição do centro do rótulo da grade."""
    xs, ys = [], []
    for w in page.get_text('words'):
        t = w[4].replace('.', '')
        cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
        if re.match(xpat, t) and 150000 < int(t) < 400000 and (w[3] - w[1]) < (w[2] - w[0]):
            xs.append((cx, int(t)))
        elif re.match(ypat, t) and 9000000 < int(t) < 9300000:
            ys.append((cy, int(t)))
    ax = np.polyfit([a for a, _ in xs], [b for _, b in xs], 1)
    ay = np.polyfit([a for a, _ in ys], [b for _, b in ys], 1)
    rx = max(abs(np.polyval(ax, a) - b) for a, b in xs)
    ry = max(abs(np.polyval(ay, a) - b) for a, b in ys)
    return ax, ay, len(xs), len(ys), rx, ry

def make_pdf2utm(ax, ay):
    def f(x, y, z=None):
        return (ax[0] * np.asarray(x) + ax[1], ay[0] * np.asarray(y) + ay[1])
    return f

_T = Transformer.from_crs('EPSG:31985', 'EPSG:4326', always_xy=True)
def utm2wgs(g):
    return shp_transform(lambda x, y, z=None: _T.transform(x, y), g)

def clean(g, simplify_m=1.5, min_area=1.0):
    g = make_valid(g)
    if g.geom_type == 'GeometryCollection':
        g = unary_union([p for p in g.geoms if p.geom_type in ('Polygon', 'MultiPolygon')])
    g = g.simplify(simplify_m, preserve_topology=True)
    g = make_valid(g)
    if g.geom_type == 'GeometryCollection':
        g = unary_union([p for p in g.geoms if p.geom_type in ('Polygon', 'MultiPolygon')])
    if g.geom_type == 'Polygon':
        g = MultiPolygon([g])
    if g.geom_type == 'MultiPolygon':
        g = MultiPolygon([p for p in g.geoms if p.area >= min_area])
    return g

def round_geom(gj, nd=6):
    def r(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            return [round(c[0], nd), round(c[1], nd)]
        return [r(x) for x in c]
    return {'type': gj['type'], 'coordinates': r(gj['coordinates'])}

def path_to_geom_fast(items):
    """Even-odd rápido para caminhos com milhares de anéis: profundidade de aninhamento via STRtree;
    resultado = ((D0 - D1) U D2) - D3 ... (equivalente à regra par-ímpar para anéis que não se cruzam)."""
    from shapely.strtree import STRtree
    rings = rings_from_items(items)
    polys = [p for p in (make_valid(Polygon(r)) for r in rings) if not p.is_empty and p.area > 1e-6]
    if not polys:
        return None
    tree = STRtree(polys); depth = []
    for i, p in enumerate(polys):
        pt = p.representative_point(); a = p.area
        depth.append(sum(1 for j in tree.query(pt) if j != i and polys[j].area > a and polys[j].contains(pt)))
    g = None
    for d in range(max(depth) + 1):
        u = unary_union([p for p, k in zip(polys, depth) if k == d])
        g = u if g is None else (g.union(u) if d % 2 == 0 else g.difference(u))
    return make_valid(g)
