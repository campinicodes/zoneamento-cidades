#!/usr/bin/env python3
"""Extrai os polígonos vetoriais (preenchimentos) e as linhas ZCLMe/ZCLMu do PDF oficial
LOUOS Mapa 01A (Anexo 02 da Lei 9.148/2016, versão alterada até ATA 12/2022 CNLU),
em coordenadas do PDF (pontos). Saída: geo_raw/mapa01a_pdf_coords.json"""
import pymupdf, json, os, collections
import shapely
from shapely.geometry import Polygon, LineString, MultiLineString, mapping
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, 'fontes', 'LOUOS_MAPA_01A_ZONAS-DE-USO_MODIFICADO_CNLU_ESALVADOR_compressed.pdf')
LEG = {  # cor de preenchimento da legenda (RGB 0-1, 3 casas) -> zona
 (1.0, 0.404, 0.004): 'ZCMe', (0.286, 0.216, 0.545): 'ZCMu', (0.871, 0.071, 0.0): 'ZEIS',
 (0.961, 0.666, 0.008): 'ZPR-1', (0.961, 0.828, 0.153): 'ZPR-2', (0.969, 0.984, 0.518): 'ZPR-3',
 (0.789, 0.42, 0.859): 'ZDE-1', (0.689, 0.294, 0.6): 'ZDE-2', (0.953, 0.65, 0.697): 'ZIT',
 (0.49, 0.545, 0.561): 'ZEM', (0.2, 0.392, 0.0): 'ZUSI', (0.561, 0.777, 0.537): 'ZPAM',
 (0.682, 0.435, 0.298): 'ZUE'}
LIN = {(1.0, 0.404, 0.004): 'ZCLMe', (0.541, 0.514, 0.805): 'ZCLMu'}
MAP_XMAX = 2850  # legenda/carimbo à direita

def rings(items):
    out, cur = [], []
    for it in items:
        k = it[0]
        if k == 're':
            r = it[1]; out.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]); continue
        if k == 'qu':
            q = it[1]; out.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]); continue
        p0, p1 = it[1], it[-1]
        if cur and (abs(cur[-1][0] - p0.x) > 1e-3 or abs(cur[-1][1] - p0.y) > 1e-3):
            out.append(cur); cur = []
        if not cur: cur.append((p0.x, p0.y))
        if k == 'c':  # bezier -> amostra 4 pontos
            a, b, c, d = it[1:5]
            for t in (0.25, 0.5, 0.75, 1.0):
                mt = 1 - t
                cur.append((mt**3*a.x + 3*mt*mt*t*b.x + 3*mt*t*t*c.x + t**3*d.x, mt**3*a.y + 3*mt*mt*t*b.y + 3*mt*t*t*c.y + t**3*d.y))
        else:
            cur.append((p1.x, p1.y))
    if cur: out.append(cur)
    return [r for r in out if len(r) >= 3]

def main():
    page = pymupdf.open(PDF)[0]
    dr = page.get_drawings()
    polys = collections.defaultdict(list); lines = collections.defaultdict(list)
    for seq, x in enumerate(dr):
        r = x['rect']
        if r.x0 > MAP_XMAX: continue
        fill = tuple(round(c, 3) for c in x['fill']) if x.get('fill') else None
        if fill in LEG and x['type'] in ('f', 'fs'):
            g = None
            for rg in rings(x['items']):
                p = Polygon(rg)
                if not p.is_valid: p = shapely.make_valid(p)
                if p.area <= 0: continue
                g = p if g is None else g.symmetric_difference(p)  # regra par-ímpar
            if g is not None and not g.is_empty:
                polys[LEG[fill]].append((seq, g))
        col = tuple(round(c, 3) for c in x['color']) if x.get('color') else None
        if x['type'] == 's' and col in LIN and (x.get('width') or 0) > 3:
            segs = []
            cur = []
            for it in x['items']:
                if it[0] not in ('l', 'c'): continue
                p0, p1 = it[1], it[-1]
                if cur and (abs(cur[-1][0] - p0.x) > 1e-3 or abs(cur[-1][1] - p0.y) > 1e-3):
                    segs.append(cur); cur = []
                if not cur: cur.append((p0.x, p0.y))
                cur.append((p1.x, p1.y))
            if cur: segs.append(cur)
            for s in segs:
                if len(s) >= 2: lines[LIN[col]].append(LineString(s))
    out = {"pdf_rect": list(page.rect), "polys": {k: [mapping(g) for _, g in v] for k, v in polys.items()}, "seq": {k: [s for s, _ in v] for k, v in polys.items()},
           "lines": {k: [mapping(g) for g in v] for k, v in lines.items()}}
    json.dump(out, open(os.path.join(BASE, 'geo_raw', 'mapa01a_pdf_coords.json'), 'w'))
    print({k: (len(v), round(sum(g.area for _, g in v))) for k, v in polys.items()}, {k: len(v) for k, v in lines.items()})
main()
