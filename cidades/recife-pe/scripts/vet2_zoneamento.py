"""Etapa 2: Mapa 2 (Zoneamento) + Mapa 4 (Setores) -> geo/zoneamento.geojson"""
from vetorizar_lib import *
city = np.load(G + '_city.npy'); L1 = np.load(G + '_L1.npy')
m2 = load('PLE_m2_zoneamento')
PAL2 = {'ZAN-ORLA': (19, 82, 45), 'ZAN-CAPIBARIBE': (19, 163, 78), 'ZAN-TEJIPIO': (80, 219, 132), 'ZAN-BEBERIBE': (186, 245, 209),
        'ZDS-TEJIPIO': (154, 194, 77), 'ZDS-CENTRO': (197, 219, 149), 'ZDS-CAPIBARIBE': (254, 254, 191), 'ZDS-BEBERIBE': (119, 206, 188),
        'ZONA-CENTRO': (249, 138, 6), 'ZRU-1': (132, 110, 69), 'ZAC-ORLA': (177, 179, 179), 'ZAC-PLANICIE-1': (156, 156, 156),
        'ZAC-PLANICIE-2': (225, 224, 224), 'ZAC-MORRO': (243, 202, 122)}
MANC = ['ZAN-ORLA', 'ZAN-CAPIBARIBE', 'ZAN-TEJIPIO', 'ZAN-BEBERIBE', 'ZDS-TEJIPIO', 'ZDS-CENTRO', 'ZDS-CAPIBARIBE', 'ZDS-BEBERIBE']
names = list(PAL2); L2 = np.zeros(city.shape, np.int64)
for mz, keys in ((1, MANC), (2, [k for k in names if k not in MANC])):
    reg = city & (L1 == mz)
    L, nm = classify(m2, {k: PAL2[k] for k in keys}, 22, reg)
    idx = np.array([names.index(k) + 1 for k in nm]); sub = np.where(L > 0, idx[np.maximum(L - 1, 0)], 0)
    L2 = np.where(reg, fill_nearest(sub, reg), L2)
L2 = drop_small(majority(L2, 5, len(names), city), 20, city)
# ZAN Orla é a faixa de praia (leste): pixels escuros do limite oeste confundidos com o verde-escuro são descartados
io = names.index('ZAN-ORLA') + 1; xx = np.arange(city.shape[1])[None, :].repeat(city.shape[0], 0)
L2[(L2 == io) & (xx < 850)] = 0; L2 = fill_nearest(L2, city)
m4 = load('PLE_m4_setores')
PAL4 = {'ZDS-CAPIBARIBE-A': (213, 211, 172), 'ZDS-CAPIBARIBE-B': (167, 245, 118), 'ZDS-CAPIBARIBE-C': (122, 242, 197),
        'ZAC-PLANICIE-1-A': (136, 136, 136), 'ZAC-PLANICIE-1-B': (179, 179, 179),
        'ZRU-1-A': (132, 108, 68), 'ZRU-1-B': (175, 112, 12), 'ZRU-1-C': (201, 166, 99)}
L4, n4 = classify(m4, PAL4, 26, city); L4 = majority(L4, 5, len(n4), city)
S = {n4[i]: rm_small(L4 == i + 1, 15) for i in range(len(n4))}
# ZAC Planície 1: cinzas do Mapa 4 confundem-se com o arruamento -> só dentro da ZAC P1 do Mapa 2 e após abertura morfológica
p1 = L2 == names.index('ZAC-PLANICIE-1') + 1
for k in ('ZAC-PLANICIE-1-A', 'ZAC-PLANICIE-1-B'): S[k] = rm_small(ndi.binary_opening(S[k] & p1, iterations=2), 150)
# ZRU-1-C aparece hachurado: fechamento para unir o padrão
S['ZRU-1-C'] = rm_small(ndi.binary_closing(S['ZRU-1-C'], iterations=3), 30)
LOG['setores_px'] = {k: int(v.sum()) for k, v in S.items()}
final = {}
for i, z in enumerate(names):
    mz = L2 == i + 1
    subs = [k for k in S if k.startswith(z + '-')]
    if not subs: final[z] = mz; continue
    union = np.logical_or.reduce([S[k] for k in subs])
    base = (mz | union) if z == 'ZRU-1' else mz  # ZRU-1 Setor C (antiga ZRU 2/ZAC Orla, art. 10) só no Mapa 4
    lab = np.zeros(mz.shape, np.int64)
    for j, k in enumerate(subs): lab[S[k] & base] = j + 1
    fl = fill_nearest(lab, base) if lab.max() else lab
    for j, k in enumerate(subs): final[k] = fl == j + 1
order = [k for k in final if k.startswith('ZRU-1')] + [k for k in final if not k.startswith('ZRU-1')]
taken = np.zeros(city.shape, bool); feats = []
for k in order:
    m = final[k] & ~taken & city; taken |= m; feats.append(({'codigo': k}, polygonize(m)))
np.save(G + '_L2.npy', L2)
save('zoneamento', feats, dict(fonte='PLE_m2_zoneamento + PLE_m4_setores'))
dump_log()
pal=np.array([[255,255,255]]+[list(PAL2[k]) for k in names],np.uint8)
viz=np.full(city.shape+(3,),255,np.uint8)
cols={k:(PAL2.get(k) or PAL4.get(k)) for k in final}
for k in order:
    viz[final[k]&city]=cols[k]
cv2.imwrite(G+'_preview_zoneamento.png',cv2.cvtColor(viz,cv2.COLOR_RGB2BGR))
