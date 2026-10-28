"""Etapa 1: Mapa 1 (Macrozonas) -> geo/macrozonas.geojson, máscara do município (geo/_city.npy, geo/_L1.npy)."""
from vetorizar_lib import *
m1 = load('PLE_m1_macrozona')
L1, n1 = classify(m1, {'MANC': (116, 172, 116), 'MAC': (176, 176, 176)}, 38, frame_mask(m1.shape))
city = ndi.binary_fill_holes(ndi.binary_opening(ndi.binary_closing(L1 > 0, iterations=4), iterations=3))
lab, n = ndi.label(city); sz = ndi.sum(np.ones_like(lab), lab, range(1, n + 1)); city = lab == (np.argmax(sz) + 1)
L1 = drop_small(fill_nearest(majority(L1, 5, 2, city), city), 300, city)
np.save(G + '_city.npy', city); np.save(G + '_L1.npy', L1)
save('macrozonas', [({'codigo': n1[c - 1]}, polygonize(L1 == c)) for c in (1, 2)], dict(fonte='PLE_m1_macrozona'))
save('limite_municipal_mapa', [({'codigo': 'RECIFE'}, polygonize(city))], dict(fonte='máscara do Mapa 1'))
dump_log()
