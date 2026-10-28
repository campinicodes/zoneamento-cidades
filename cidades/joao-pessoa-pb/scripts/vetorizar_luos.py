"""Vetoriza o Anexo II (Zoneamento Urbano) da LUOS LC 166/2024 (PDF republicado no SAPL, pág. 46).
O Anexo I da LC 169/2024 (substituto) foi publicado só como imagem no DOM 0681; ver comparar_lc169.py.
Saída: geo_raw/luos_zonas_utm.geojson e luos_overlays_utm.geojson (EPSG:31985)."""
import json, pickle, os, sys
import pymupdf as fitz
from shapely.geometry import mapping
from shapely.ops import unary_union, transform as T
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vetor_pdf import path_to_geom, fit_grid, make_pdf2utm, clean

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = f'{BASE}/fontes/LC166_2024_LUOS_republicada_SAPL.pdf'
OUT = f'{BASE}/geo_raw'
CORES = {
 (1.0,0.498,0.498):'ZBD',(0.777,0.859,0.938):'ZCS-1',(0.42,0.682,0.84):'ZCS-2',(0.031,0.271,0.58):'ZCS-3',
 (0.549,0.588,0.777):'ZCS-4',(0.549,0.42,0.693):'ZCS-5',(0.506,0.059,0.486):'ZCS-6',(0.302,0.0,0.294):'ZCS-7',
 (0.686,0.812,0.611):'ZEPA-1',(0.447,0.537,0.267):'ZEPA-2',(0.666,1.0,0.0):'ZEPA-3',(1.0,1.0,0.451):'ZH-1',
 (0.949,0.867,0.615):'ZH-2',(1.0,0.666,0.0):'ZH-3',(0.805,0.537,0.4):'ZH-4',(0.514,0.224,0.341):'ZH-5',
 (0.801,0.801,0.801):'ZI-1',(0.408,0.408,0.408):'ZI-2',(0.658,0.219,0.0):'ZDTRL',(0.844,0.762,0.619):'ZDTRS'}
doc = fitz.open(PDF); page = doc[45]
ax, ay, nx, ny, rx, ry = fit_grid(page)
print('grade', ax, ay, nx, ny, 'resid max', rx, ry)
f = make_pdf2utm(ax, ay)
pk = f'{OUT}/luos_p46_drawings_ext.pkl'
dr = pickle.load(open(pk, 'rb')) if os.path.exists(pk) else page.get_drawings(extended=True)
seq = []
for i, x in enumerate(dr):
    if x['type'] != 'f' or i > 31000 or x['rect'].x0 > 2840: continue
    k = tuple(round(v, 3) for v in x['fill'])
    if k in CORES:
        g = path_to_geom(x['items'], x.get('even_odd', True))
        if g is not None and not g.is_empty:
            seq.append((CORES[k], g))
print('fills de zona', len(seq))
final, acc = {}, None
for cod, g in reversed(seq):           # o que é pintado depois cobre o anterior
    vis = g if acc is None else g.difference(acc)
    acc = g if acc is None else acc.union(g)
    final.setdefault(cod, []).append(vis)
print('sobreposição entre fills (pt2):', round(sum(g.area for _, g in seq) - acc.area, 1), 'de', round(acc.area, 1))
feats = []
for cod in sorted(final):
    gu = clean(T(f, unary_union(final[cod])), 1.5, 25.0)
    feats.append({'type': 'Feature', 'properties': {'codigo': cod, 'area_ha': round(gu.area / 1e4, 2)}, 'geometry': mapping(gu)})
    print(cod, round(gu.area / 1e4, 1), 'ha', len(gu.geoms), 'partes')
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985',
           'grade': {'ax': list(ax), 'ay': list(ay), 'n': [nx, ny], 'resid_max_m': [rx, ry]},
           'features': feats}, open(f'{OUT}/luos_zonas_utm.geojson', 'w'))
# sobreposições hachuradas: limites = clip paths
CLIPS = {'FAIXA_PRAIA_500M': [32019], 'BORDAS_TABULEIRO': [32789],
         'SEAV': [32687, 32696, 32719, 32741, 32751, 32763, 32770, 32778, 33309, 33331, 33418]}
of = []
for cod, idxs in CLIPS.items():
    gs = []
    for idx in idxs:
        assert dr[idx]['type'] == 'clip', idx
        gs.append(path_to_geom(dr[idx]['items'], dr[idx].get('even_odd', False)))
    gu = clean(T(f, unary_union(gs)), 1.5, 25.0)
    print(cod, round(gu.area / 1e4, 1), 'ha', len(gu.geoms))
    of.append({'type': 'Feature', 'properties': {'codigo': cod, 'area_ha': round(gu.area / 1e4, 2)}, 'geometry': mapping(gu)})
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'features': of}, open(f'{OUT}/luos_overlays_utm.geojson', 'w'))
