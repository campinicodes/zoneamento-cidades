"""Etapa 3: Zonas especiais (Mapas 3A/3B/3C finais - Parecer de Redação Final 75/2025) e SMUP (Mapa 6)."""
from vetorizar_lib import *
city = np.load(G + '_city.npy')
def layer(img, pal, thr, minpx, close=1, med=3):
    L, nm = classify(img, pal, thr, city)
    if med > 1: L = ndi.median_filter(L, size=med)
    out = {}
    for i, n_ in enumerate(nm):
        m = ndi.binary_closing(L == i + 1, iterations=close) if close else (L == i + 1)
        out[n_] = rm_small(m & city, minpx)
    return out
viz = np.full(city.shape + (3,), 255, np.uint8); viz[city] = (235, 235, 235)
# ZEIS (Mapa 3A final, registrado)
z = layer(register('RF_m3a_zeis', 'PLE_m3a_zeis'), {'ZEIS-1-MORRO': (244, 6, 190), 'ZEIS-1-PLANICIE': (246, 186, 224), 'ZEIS-2': (176, 0, 146)}, 48, 6)
z['ZEIS-2'] = rm_small(ndi.binary_opening(z['ZEIS-2'], iterations=1), 6)  # remove linhas de contorno escuras
z['ZEIS-1-MORRO'] |= ndi.binary_closing(z['ZEIS-1-MORRO'], iterations=2) & city
save('zeis', [({'codigo': k}, polygonize(v)) for k, v in z.items()], dict(fonte='RF_m3a_zeis registrado sobre PLE_m3a_zeis'))
for k, c in zip(z, [(244, 6, 190), (246, 186, 224), (176, 0, 146)]): viz[z[k]] = c
# ZEC: PLE (alta resolução) U ampliações do mapa final (arts. 20-A e 20-B)
zp = layer(load('PLE_m3b_zec'), {'ZEC-1': (247, 7, 12), 'ZEC-1x': (151, 5, 6), 'ZEC-2-3': (231, 150, 3)}, 60, 4)
zec_ple = zp['ZEC-1'] | zp['ZEC-1x']
zr = layer(register('RF_m3b_zec', 'PLE_m3b_zec'), {'ZEC-1': (240, 10, 10)}, 90, 2, close=1, med=1)
acres = rm_small(zr['ZEC-1'] & ~ndi.binary_dilation(zec_ple, iterations=4), 4)
LOG['zec_acrescimo_rf_px'] = int(acres.sum())
save('zec', [({'codigo': 'ZEC-1'}, polygonize(zec_ple | acres))], dict(fonte='PLE_m3b_zec U acréscimos RF_m3b_zec'))
save('zec23_indicacao', [({'codigo': 'ZEC-2-3'}, polygonize(zp['ZEC-2-3']))], dict(fonte='PLE_m3b_zec (indicação de localização, perímetro não definido - art. 20 §2º)'))
viz[zec_ple | acres] = (247, 7, 12); viz[zp['ZEC-2-3']] = (231, 150, 3)
# ZEPH (Mapa 3C final)
zz = layer(register('RF_m3c_zeph', 'PLE_m3c_zeph'), {'ZEPH-SPA': (193, 158, 214), 'ZEPH-SPM': (206, 116, 245), 'ZEPH-SPS': (72, 0, 112), 'ZEPH-SPPI': (111, 7, 74)}, 40, 6)
save('zeph', [({'codigo': k}, polygonize(v)) for k, v in zz.items()], dict(fonte='RF_m3c_zeph registrado sobre PLE_m3c_zeph'))
# SMUP (Mapa 6)
u = layer(load('PLE_m6_unidades_protegidas'), {'UCN': (37, 114, 7), 'JARDIM-HISTORICO': (56, 160, 10), 'PARQUE-PRACA': (70, 226, 1), 'IPAV': (61, 174, 110), 'UCP': (143, 239, 140)}, 30, 6)
save('unidades_protegidas', [({'codigo': k}, polygonize(v)) for k, v in u.items()], dict(fonte='PLE_m6_unidades_protegidas'))
cv2.imwrite(G + '_preview_especiais.png', cv2.cvtColor(viz, cv2.COLOR_RGB2BGR))
dump_log()
