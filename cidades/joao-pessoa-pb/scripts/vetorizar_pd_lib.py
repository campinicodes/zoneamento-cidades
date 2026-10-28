"""Vetoriza mapas do Plano Diretor LC 164/2024 (PDF SAPL, vetorial A0): Anexo I macrozoneamento (p.74),
Anexo II ZEIS (p.76), Anexo VII restrições ambientais (p.88) e Anexo VIII restrições adicionais (p.90).
ATENÇÃO: os Anexos I, II, VII e VIII foram substituídos pela LC 171/2025 (publicados só como imagem);
ver comparar_lc171.py. Saída: geo_raw/pd_<camada>_utm.geojson (EPSG:31985)."""
import json, pickle, os, sys
import pymupdf as fitz
from shapely.geometry import mapping
from shapely.ops import unary_union, transform as T
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vetor_pdf import path_to_geom, fit_grid, make_pdf2utm, clean
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); G = f'{B}/geo_raw'
doc = fitz.open(f'{B}/fontes/LC164_2024_PlanoDiretor_SAPL.pdf')
def load(pn):
    pk = f'{G}/pd_p{pn}_drawings_ext.pkl'
    return pickle.load(open(pk, 'rb')) if os.path.exists(pk) else doc[pn-1].get_drawings(extended=True)
def grid(pn):
    ax, ay, nx, ny, rx, ry = fit_grid(doc[pn-1]); print(f'p{pn} grade', nx, ny, 'resid', rx, ry)
    return make_pdf2utm(ax, ay), {'ax': list(ax), 'ay': list(ay), 'n': [nx, ny], 'resid_max_m': [rx, ry]}
def fills(dr, cores):
    seq = []
    for i, x in enumerate(dr):
        if x['type'] != 'f' or x['rect'].x0 > 2840: continue
        k = tuple(round(v, 3) for v in x['fill'])
        if k in cores:
            g = path_to_geom(x['items'], x.get('even_odd', True))
            if g is not None and not g.is_empty: seq.append((cores[k], g))
    return seq
def painter(seq):
    final, acc = {}, None
    for cod, g in reversed(seq):
        vis = g if acc is None else g.difference(acc)
        acc = g if acc is None else acc.union(g)
        final.setdefault(cod, []).append(vis)
    return final
def clips(dr, idxs):
    return unary_union([path_to_geom(dr[i]['items'], dr[i].get('even_odd', False)) for i in idxs if dr[i]['type'] == 'clip'])
def save(nome, grupos, f, meta, explode=False):
    feats = []
    for cod, g in grupos.items():
        gu = clean(T(f, unary_union(g) if isinstance(g, list) else g), 1.5, 25.0)
        if gu.is_empty: continue
        if explode:
            for k, part in enumerate(sorted(gu.geoms, key=lambda p: -p.area)):
                feats.append({'type': 'Feature', 'properties': {'codigo': cod, 'parte': k + 1, 'area_ha': round(part.area / 1e4, 2)}, 'geometry': mapping(part)})
        else:
            feats.append({'type': 'Feature', 'properties': {'codigo': cod, 'area_ha': round(gu.area / 1e4, 2)}, 'geometry': mapping(gu)})
        print(' ', nome, cod, round(gu.area / 1e4, 1), 'ha', len(getattr(gu, 'geoms', [gu])), 'partes')
    json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'grade': meta, 'features': feats}, open(f'{G}/pd_{nome}_utm.geojson', 'w'))
