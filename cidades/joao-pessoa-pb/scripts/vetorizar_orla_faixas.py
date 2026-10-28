"""Faixas de restrição de altura da orla — LUOS LC166/2024 arts. 61-62, Anexo III (p.48 do PDF republicado SAPL).
No PDF as 9 faixas são caminhos de recorte (clip) vetoriais preenchidos por hachura colorida
(legenda: 1ª faixa verde-escuro ... 9ª faixa vermelho-escuro). A prancha não tem rótulos de grade:
registro afim (escala x/y + translação) ajustado minimizando a diferença simétrica entre a união das 9
faixas e o polígono da faixa de 500 m vetorizado do Anexo II (p.46, georreferenciado pela grade UTM).
Obs.: o Anexo III foi substituído pelo Anexo II da LC169/2024 (raster de baixa resolução); a comparação visual
não mostra mudança de traçado, mas não foi possível verificar ao nível de faixa (ver lacunas)."""
import sys, json, pickle, numpy as np
sys.path.insert(0, '.')
from vetor_pdf import path_to_geom, clean
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.affinity import affine_transform
from scipy.optimize import minimize
B = '../'
dr = pickle.load(open(B + 'geo_raw/luos_p48_drawings_ext.pkl', 'rb'))
CLIPS = [49307, 49638, 49967, 50296, 50626, 50956, 51286, 51616, 51946]  # faixa 1..9 (mapa principal)
ALT = {1: 12.90, 2: 16.50, 3: 19.50, 4: 22.50, 5: 25.50, 6: 28.50, 7: 31.50, 8: 34.00, 9: 35.00}
fx = {k: clean(path_to_geom(dr[j]['items'], even_odd=True), 0.0, 0.0) for k, j in enumerate(CLIPS, 1)}
for k, g in fx.items(): print('pdf faixa', k, round(g.area, 2), g.bounds)
U = unary_union(list(fx.values()))
orla = shape(json.load(open(B + 'geo_raw/luos_overlays_utm.geojson'))['features'][0]['geometry'])
ub, ob = U.bounds, orla.bounds
sx = (ob[2] - ob[0]) / (ub[2] - ub[0]); sy = -(ob[3] - ob[1]) / (ub[3] - ub[1])
P0 = [sx, ob[0] - sx * ub[0], sy, ob[3] - sy * ub[1]]
def tf(g, P): return affine_transform(g, [P[0], 0, 0, P[2], P[1], P[3]])
def cost(P):
    return tf(U, P).symmetric_difference(orla).area / orla.area
print('custo inicial', round(cost(P0), 3))
res = minimize(cost, P0, method='Nelder-Mead', options={'maxiter': 2000, 'xatol': 1e-3, 'fatol': 1e-5,
               'initial_simplex': [P0] + [[P0[i] + (d if i == j else 0) for i in range(4)] for j, d in enumerate([0.3, 50, 0.3, 50])]})
P = list(res.x); print('custo final', round(res.fun, 4), P)
# erro: distância média entre bordas
g9 = tf(U, P)
bd = orla.boundary
d = [bd.distance(g9.boundary.interpolate(t, normalized=True)) for t in np.linspace(0, 1, 2000)]
print('dist borda: mediana', round(float(np.median(d)), 1), 'p90', round(float(np.percentile(d, 90)), 1))
feats = []; acc = None
for k in range(1, 10):
    g = tf(fx[k], P)
    if acc is not None: g = g.difference(acc)
    acc = g if acc is None else acc.union(g)
    g = clean(g, 2.0, 100)
    feats.append({'type': 'Feature', 'properties': {'codigo': f'FAIXA_{k}', 'faixa': k, 'altura_max_m': ALT[k], 'area_ha': round(g.area / 1e4, 1)},
                  'geometry': mapping(g)})
    print('faixa', k, round(g.area / 1e4, 1), 'ha')
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'registro': {'P': P, 'difsim_rel': res.fun, 'dist_borda_mediana_m': float(np.median(d)), 'dist_borda_p90_m': float(np.percentile(d, 90))},
           'features': feats}, open(B + 'geo_raw/orla_faixas_utm.geojson', 'w'))
