"""Compara mapas vetoriais do PD LC 164/2024 (SAPL) com os anexos substitutos da LC 171/2025 (só imagem no DOM):
  mz   : PD p.74 (Anexo I macrozoneamento)  x  LC171 p.2 imagem xref 34
  zeis : PD p.76 (Anexo II ZEIS)            x  LC171 p.3 imagem xref 40
Método (igual a comparar_lc169.py): renderiza a imagem do DOM via PyMuPDF na escala da prancha A0
(S=0,5 px/pt ≈ 17,6 m/px), registro ECC afim, paleta da imagem aprendida pela mediana dos pixels onde o vetor
do PD tem cada classe (a maioria do mapa não muda), classificação por cor mais próxima, manchas divergentes
>=5 ha rotuladas por par (classe PD -> classe LC171). Rodar com /workspace/.venv_ocr/bin/python.
Saída: geo_raw/dif_lc171_<tag>.json, dif_lc171_<tag>_manchas_utm.geojson, thumbs/dif_lc171_<tag>.png"""
import os, sys, json
import numpy as np, cv2, pymupdf as fitz
from PIL import Image
from scipy import ndimage
from shapely.geometry import box, mapping
from shapely.ops import unary_union
from shapely import affinity
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AX = (8.81945, 279883.07); AY = (-8.81945, 9219830.13)
CFG = {'mz': (74, 1, 34, {(0.804, 0.537, 0.4): 'MAD-1', (1.0, 0.498, 0.498): 'MAD-2', (1.0, 0.659, 0.0): 'MAD-3',
                          (0.447, 0.537, 0.267): 'MPA', (1.0, 1.0, 0.576): 'MBD'}),
       'zeis': (76, 2, 40, {(0.859, 0.29, 0.29): 'ZEIS', (0.847, 0.91, 0.831): 'MPA_FUNDO', (0.941, 0.941, 0.902): 'FUNDO'})}
S = 0.5
def run(tag):
    pn, p171, xref, cores = CFG[tag]
    p = fitz.open(f'{B}/fontes/LC164_2024_PlanoDiretor_SAPL.pdf')[pn - 1]
    pg = fitz.open(f'{B}/fontes/LC171_2025_AlteraPD.pdf')[p171]
    bb = pg.get_image_bbox([i for i in pg.get_images(full=True) if i[0] == xref][0])
    z = S * p.rect.width / bb.width
    pb = pg.get_pixmap(matrix=fitz.Matrix(z, z), clip=bb, alpha=False)
    img = np.frombuffer(pb.samples, np.uint8).reshape(pb.height, pb.width, 3)
    pr = p.get_pixmap(matrix=fitz.Matrix(S, S), alpha=False)
    ref = np.frombuffer(pr.samples, np.uint8).reshape(pr.height, pr.width, 3)
    g1 = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY).astype(np.float32); g2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    hh, ww = min(g1.shape[0], g2.shape[0]), min(g1.shape[1], g2.shape[1])
    g2p = np.full_like(g1, 255); g2p[:hh, :ww] = g2[:hh, :ww]
    A = np.eye(2, 3, dtype=np.float32)
    cc, A = cv2.findTransformECC(cv2.GaussianBlur(g1, (5, 5), 0), cv2.GaussianBlur(g2p, (5, 5), 0), A, cv2.MOTION_AFFINE,
                                 (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
    print(tag, 'ECC', round(cc, 3), A.round(4).tolist())
    ip = np.full_like(ref, 255); ip[:hh, :ww] = img[:hh, :ww]
    wp = cv2.warpAffine(ip, A, (ref.shape[1], ref.shape[0]), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, borderValue=(255, 255, 255))
    names = list(cores.values()); pal = np.array([[c * 255 for c in k] for k in cores], float)
    def classify(im, P, thr):
        a = im.astype(float); best = np.full(a.shape[:2], 1e9); cls = np.full(a.shape[:2], -1)
        for j, c in enumerate(P):
            dd = ((a - c) ** 2).sum(-1); u = dd < best; best[u] = dd[u]; cls[u] = j
        cls[np.sqrt(best) > thr] = -1
        return cls
    c1 = classify(ref, pal, 20)
    core = [ndimage.binary_erosion(c1 == j, iterations=2) for j in range(len(names))]
    pal2 = np.array([np.median(wp[m].reshape(-1, 3), 0) if m.sum() > 50 else pal[j] for j, m in enumerate(core)])
    for n_, a_, b_ in zip(names, pal, pal2): print(f'  {n_:10s}', a_.round(), b_.round())
    c2 = ndimage.median_filter(classify(wp, pal2, 45), 3)
    frame = np.zeros(c1.shape, bool); frame[int(20 * S):int(2356 * S), int(259 * S):int(2505 * S)] = True
    valid = (c1 >= 0) & (c2 >= 0) & frame; diff = valid & (c1 != c2)
    mpx = AX[0] / S; frac = float(diff.sum() / valid.sum()); print('  frac divergente', round(frac, 4))
    d2 = ndimage.binary_opening(diff, iterations=2)
    pair = np.where(d2, c1 * 100 + c2, -1); lab = np.zeros(d2.shape, np.int32); n = 0
    for pv in np.unique(pair[pair >= 0]):
        l_, k_ = ndimage.label(pair == pv); lab[l_ > 0] = l_[l_ > 0] + n; n += k_
    feats, out = [], []
    for i in range(1, n + 1):
        mk = lab == i; ha = mk.sum() * mpx ** 2 / 1e4
        if ha < 5: continue
        a = names[np.bincount(c1[mk], minlength=len(names)).argmax()]; b = names[np.bincount(c2[mk], minlength=len(names)).argmax()]
        ys, xs = np.nonzero(mk); sq = []
        for yy in np.unique(ys):
            xr = np.sort(xs[ys == yy])
            for run_ in np.split(xr, np.where(np.diff(xr) > 1)[0] + 1):
                sq.append(box(run_[0] / S, yy / S, (run_[-1] + 1) / S, (yy + 1) / S))
        g = affinity.affine_transform(unary_union(sq), [AX[0], 0, 0, AY[0], AX[1], AY[1]]).buffer(0).simplify(10)
        c = g.centroid; r = {'ha': round(float(ha), 1), 'pd_164': a, 'lc_171': b, 'utm_31985': [round(c.x), round(c.y)]}
        out.append(r); feats.append({'type': 'Feature', 'properties': r, 'geometry': mapping(g)})
    out.sort(key=lambda r: -r['ha'])
    for r in out: print('  ', r)
    json.dump({'ecc': float(cc), 'frac_divergente': frac, 'm_por_pixel': mpx, 'manchas': out},
              open(f'{B}/geo_raw/dif_lc171_{tag}.json', 'w'), ensure_ascii=False, indent=1)
    json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'features': feats}, open(f'{B}/geo_raw/dif_lc171_{tag}_manchas_utm.geojson', 'w'))
    vis = (ref * 0.5 + 127).astype(np.uint8); vis[d2] = [255, 0, 0]
    Image.fromarray(vis).resize((vis.shape[1] // 2, vis.shape[0] // 2)).save(f'{B}/geo_raw/thumbs/dif_lc171_{tag}.png')
for t in (sys.argv[1:] or ['mz', 'zeis']): run(t)
