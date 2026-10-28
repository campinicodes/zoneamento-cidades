#!/usr/bin/env python3
"""Georreferencia o Mapa 01A (coords PDF) para EPSG:31984 por transformação afim ajustada por
mínimos quadrados em pontos de controle = centróides de ZEIS do PDF (vermelho) pareados com a camada
OFICIAL de ZEIS (Mapa_LOUOS_WFL1/29). ICP com rejeição de outliers. Saída: geo_raw/georref_mapa01a.json"""
import json, os, numpy as np
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = Transformer.from_crs(4326, 31984, always_xy=True)
def utm(g): return transform(lambda x, y, z=None: T.transform(x, y), g)
pdf = json.load(open(os.path.join(BASE, 'geo_raw', 'mapa01a_pdf_coords.json')))
pz = [shape(g) for g in pdf['polys']['ZEIS']]
pz = [g for g in pz if g.area > 0]
oz = [utm(shape(f['geometry'])) for f in json.load(open(os.path.join(BASE, 'geo_raw', 'zeis.geojson')))['features'] if f['geometry']]
P = np.array([[g.centroid.x, g.centroid.y] for g in pz]); PA = np.array([g.area for g in pz])
O = np.array([[g.centroid.x, g.centroid.y] for g in oz]); OA = np.array([g.area for g in oz])
# chute inicial: caixas envolventes ponderadas (y do PDF cresce para baixo)
def bbox(a): return a.min(0), a.max(0)
(p0, p1), (o0, o1) = bbox(P), bbox(O)
sx = (o1[0] - o0[0]) / (p1[0] - p0[0]); sy = (o1[1] - o0[1]) / (p1[1] - p0[1])
A = np.array([[sx, 0, o0[0] - sx * p0[0]], [0, -sy, o1[1] + sy * p0[1]]])
def ap(A, X): return X @ A[:, :2].T + A[:, 2]
for it in range(30):
    Q = ap(A, P)
    d = np.linalg.norm(Q[:, None, :] - O[None, :, :], axis=2)
    j = d.argmin(1); dm = d[np.arange(len(P)), j]
    det = abs(np.linalg.det(A[:, :2]))
    ratio = PA * det / OA[j]
    thr = max(np.percentile(dm, 60), 30 if it > 10 else 0)
    ok = (dm <= thr) & (ratio > 0.5) & (ratio < 2)
    X = np.c_[P[ok], np.ones(ok.sum())]
    sol, *_ = np.linalg.lstsq(X, O[j[ok]], rcond=None)
    A = sol.T
Q = ap(A, P); d = np.linalg.norm(Q[:, None, :] - O[None, :, :], axis=2); j = d.argmin(1); dm = d[np.arange(len(P)), j]
ok = dm < 50
res = dm[ok]
# validação independente: IoU por polígono pareado
from shapely.affinity import affine_transform
iou = []
for i in np.where(ok)[0]:
    g = affine_transform(pz[i], [A[0,0], A[0,1], A[1,0], A[1,1], A[0,2], A[1,2]]); h = oz[j[i]]
    if not g.is_valid: g = g.buffer(0)
    if not h.is_valid: h = h.buffer(0)
    iou.append(g.intersection(h).area / g.union(h).area)
out = {'afim_pdf_para_31984': A.tolist(), 'n_pontos_controle': int(ok.sum()), 'n_pdf': len(P), 'n_oficial': len(O),
       'residuo_centroide_m': {'mediana': float(np.median(res)), 'p90': float(np.percentile(res, 90)), 'max': float(res.max()),
                               'rms': float(np.sqrt((res**2).mean()))},
       'iou_zeis': {'mediana': float(np.median(iou)), 'p10': float(np.percentile(iou, 10))},
       'escala_m_por_pt': [float(np.hypot(A[0,0], A[1,0])), float(np.hypot(A[0,1], A[1,1]))]}
json.dump(out, open(os.path.join(BASE, 'geo_raw', 'georref_mapa01a.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
