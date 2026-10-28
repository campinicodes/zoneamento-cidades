"""Aplica ao vetor do Anexo II da LUOS (LC 166/2024) as alterações do Anexo I da LC 169/2024
(mapa publicado só como imagem no DOM). Entrada: geo_raw/luos_zonas_utm.geojson e
geo_raw/dif_lc169_manchas_utm.geojson (comparar_lc169.py). Regra: se as manchas de mudança cobrem
>=60% de uma parte (polígono) LUOS, a parte inteira recebe a classe LC169 dominante (contorno vetorial
preservado); senão só a mancha (contorno raster, ~17,6 m/px) é recortada e reatribuída.
Saída: geo_raw/zonas_lc169_corrigido_utm.geojson (EPSG:31985)."""
import json, os
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); G = f'{B}/geo_raw'
import sys
# uso: aplicar_lc169.py [zonas.geojson manchas.geojson chave_antiga chave_nova saida.geojson]
ZF, MF, KO, KN, OUT = (sys.argv[1:6] if len(sys.argv) > 5 else
    ('luos_zonas_utm.geojson', 'dif_lc169_manchas_utm.geojson', 'luos_166', 'lc_169', 'zonas_lc169_corrigido_utm.geojson'))
Z = json.load(open(f'{G}/{ZF}'))
M = json.load(open(f'{G}/{MF}'))
manchas = [(shape(f['geometry']).buffer(0), f['properties']) for f in M['features']]
zonas = {f['properties']['codigo']: shape(f['geometry']) for f in Z['features']}
novo = {k: [] for k in zonas}; ajustadas = {}; log = []
for cod, g in zonas.items():
    for part in getattr(g, 'geoms', [g]):
        hits = [(part.intersection(m), p) for m, p in manchas if p[KO] == cod and part.intersects(m)]
        hits = [(h, p) for h, p in hits if h.area > 1e4]
        if not hits:
            novo[cod].append(part); continue
        cov = sum(h.area for h, _ in hits) / part.area
        por = {}
        for h, p in hits: por[p[KN]] = por.get(p[KN], 0) + h.area
        dom = max(por, key=por.get)
        if cov >= 0.6:
            resto = part.difference(unary_union([h for h, p in hits if p[KN] != dom]))
            novo.setdefault(dom, []).append(resto); ajustadas.setdefault(dom, []).append(resto)
            for h, p in hits:
                if p[KN] != dom:
                    novo.setdefault(p[KN], []).append(h); ajustadas.setdefault(p[KN], []).append(h)
            log.append(f'{cod} parte {part.area/1e4:.1f} ha cobertura {cov:.0%} -> inteira {dom} (+ recortes {[(p[KN], round(h.area/1e4,1)) for h,p in hits if p[KN]!=dom]})')
        else:
            u = unary_union([h for h, _ in hits]); novo[cod].append(part.difference(u))
            for h, p in hits:
                novo.setdefault(p[KN], []).append(h); ajustadas.setdefault(p[KN], []).append(h)
            log.append(f'{cod} parte {part.area/1e4:.1f} ha cobertura {cov:.0%} -> recorte {[(p[KN], round(h.area/1e4,1)) for h,p in hits]}')
print('\n'.join(log))
feats = []
for cod in sorted(novo):
    gs = [x for x in novo[cod] if not x.is_empty]
    if not gs: print('zona sem área após LC169:', cod); continue
    gu = unary_union(gs).buffer(0)
    aj = unary_union(ajustadas[cod]).area / 1e4 if cod in ajustadas else 0
    feats.append({'type': 'Feature', 'properties': {'codigo': cod, 'area_ha': round(gu.area / 1e4, 2),
                  'area_ajustada_lc169_ha': round(aj, 2)}, 'geometry': mapping(gu)})
    print(cod, round(gu.area / 1e4, 1), 'ha; ajustado LC169', round(aj, 1))
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'features': feats,
           'log_lc169': log}, open(f'{G}/{OUT}', 'w'))
