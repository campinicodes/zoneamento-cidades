"""Funções de vetorização raster->vetor para os mapas do Anexo II da LPUOS Recife (rodar com /workspace/.venv_ocr/bin/python)."""
import json, os, numpy as np, cv2
from scipy import ndimage as ndi
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union, transform as shp_transform
from shapely.validation import make_valid
from pyproj import Transformer
B = os.path.dirname(os.path.abspath(__file__)) + '/..'
M = B + '/fontes/mapas/'; G = B + '/geo/'; os.makedirs(G, exist_ok=True)
LOG = {}
XT = [(138.6, 278000), (299.3, 281000), (459.2, 284000), (619.2, 287000), (779.2, 290000), (940.0, 293000), (1100.1, 296000)]
YT = [(58.8, 9123000), (219.2, 9120000), (379.3, 9117000), (539.7, 9114000), (699.7, 9111000), (860.0, 9108000), (1020.2, 9105000), (1180.7, 9102000)]
ax, bx = np.polyfit([p for p, _ in XT], [e for _, e in XT], 1)
ay, by = np.polyfit([p for p, _ in YT], [n for _, n in YT], 1)
LOG['grade'] = dict(m_por_px_x=float(ax), m_por_px_y=float(ay), residuo_max_x_m=float(max(abs(ax*p+bx-e) for p, e in XT)), residuo_max_y_m=float(max(abs(ay*p+by-n) for p, n in YT)))
T = Transformer.from_crs(31985, 4326, always_xy=True)
def load(n): return cv2.cvtColor(cv2.imread(M + n + '.png'), cv2.COLOR_BGR2RGB).astype(np.int32)
def frame_mask(shape_):
    m = np.zeros(shape_[:2], bool); m[45:1368, 40:1152] = True; m[1250:1368, 40:250] = False; return m
def register(rf_name, ple_name):
    a = cv2.imread(M + ple_name + '.png', 0); b = cv2.imread(M + rf_name + '.png', 0)
    s = a.shape[1] / b.shape[1]
    bu = cv2.resize(b, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    orb = cv2.ORB_create(20000)
    ka, da = orb.detectAndCompute(a, None); kb, db = orb.detectAndCompute(bu, None)
    mt = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(db, da), key=lambda m: m.distance)[:3000]
    src = np.float32([kb[m.queryIdx].pt for m in mt]); dst = np.float32([ka[m.trainIdx].pt for m in mt])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=2.0, maxIters=20000)
    k = inl.ravel() == 1
    res = np.linalg.norm(src[k] @ A[:, :2].T + A[:, 2] - dst[k], axis=1)
    LOG['registro_' + rf_name] = dict(escala_ini=float(s), inliers=int(k.sum()), residuo_medio_px=float(res.mean()), residuo_p90_px=float(np.percentile(res, 90)), afim=A.tolist())
    rgb = cv2.cvtColor(cv2.imread(M + rf_name + '.png'), cv2.COLOR_BGR2RGB)
    rgbu = cv2.resize(rgb, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
    return cv2.warpAffine(rgbu, A, (a.shape[1], a.shape[0]), flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255)).astype(np.int32)
def classify(img, pal, thr, valid):
    names = list(pal); C = np.array([pal[n] for n in names], float)
    d = np.linalg.norm(img[..., None, :].astype(float) - C[None, None], axis=-1)
    return np.where((d.min(-1) < thr) & valid, d.argmin(-1) + 1, 0), names
def fill_nearest(L, region):
    idx = ndi.distance_transform_edt(L == 0, return_distances=False, return_indices=True)
    return np.where(region, L[idx[0], idx[1]], 0)
def majority(L, k, ncls, region):
    best = np.zeros(L.shape, float); out = L.copy()
    for c in range(1, ncls + 1):
        f = ndi.uniform_filter((L == c).astype(float), k); upd = f > best; best[upd] = f[upd]; out[upd] = c
    return np.where(region, out, 0)
def rm_small(mask, minpx):
    lab, n = ndi.label(mask)
    if n == 0: return mask
    sz = ndi.sum(np.ones_like(lab), lab, range(1, n + 1)); return mask & ~np.isin(lab, np.where(sz < minpx)[0] + 1)
def drop_small(L, minpx, region):
    L = L.copy()
    for c in np.unique(L):
        if c: L[(L == c) & ~rm_small(L == c, minpx)] = 0
    return fill_nearest(L, region)
def polygonize(mask, simplify_px=0.8, min_area_px=6):
    cs, h = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if h is None: return None
    h = h[0]; polys = []
    for i, c in enumerate(cs):
        if h[i][3] != -1 or len(c) < 3: continue
        holes = []; j = h[i][2]
        while j != -1:
            if len(cs[j]) >= 3: holes.append(cs[j][:, 0, :].astype(float))
            j = h[j][0]
        p = make_valid(Polygon(c[:, 0, :].astype(float), holes)).buffer(0.5, join_style=2).buffer(0)
        if p.area >= min_area_px: polys.append(p)
    return unary_union(polys).simplify(simplify_px, preserve_topology=True) if polys else None
def _clean(g):
    g = make_valid(g)
    if g.geom_type == 'GeometryCollection': g = unary_union([x for x in g.geoms if x.area > 0])
    return g
def save(name, feats, meta):
    fc = {'type': 'FeatureCollection', 'name': name, 'features': []}
    for props, gpx in feats:
        if gpx is None or gpx.is_empty: continue
        gu = _clean(shp_transform(lambda x, y, z=None: (ax*np.asarray(x)+bx, ay*np.asarray(y)+by), gpx))
        gw = shp_transform(lambda x, y, z=None: tuple(np.round(v, 6) for v in T.transform(x, y)), gu)
        fc['features'].append({'type': 'Feature', 'properties': dict(props, area_ha=round(gu.area/1e4, 2)), 'geometry': mapping(_clean(gw))})
    json.dump(fc, open(G + name + '.geojson', 'w'), ensure_ascii=False)
    LOG[name] = dict(meta, n=len(fc['features']), area_ha=round(sum(f['properties']['area_ha'] for f in fc['features']), 1),
                     por_codigo={f['properties']['codigo']: f['properties']['area_ha'] for f in fc['features']})
    print(name, LOG[name]['n'], LOG[name]['area_ha'], flush=True)
def dump_log():
    old = json.load(open(G + 'vetorizacao_log.json')) if os.path.exists(G + 'vetorizacao_log.json') else {}
    old.update(LOG); json.dump(old, open(G + 'vetorizacao_log.json', 'w'), ensure_ascii=False, indent=1, default=float)
