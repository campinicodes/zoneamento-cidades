"""Compara o zoneamento vetorial da LUOS (LC 166/2024, SAPL p.46) com o Anexo I da LC 169/2024
(mapa substituto em vigor, publicado só como JPEG 1103x780 px no DOM 0681).
Registro imagem->PDF por ORB + RANSAC (afim), calibração de cor pela legenda da própria imagem,
classificação por cor mais próxima e detecção de manchas divergentes.
Rodar com /workspace/.venv_ocr/bin/python (OpenCV). Saída: geo_raw/dif_lc169.json + thumbs/dif_lc169.png"""
import os, sys, io, json
import numpy as np, cv2, pymupdf as fitz
from PIL import Image
from scipy import ndimage
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vetorizar_luos_cores import CORES
AX = (8.81947063, 279883.027); AY = (-8.81947069, 9219830.15)   # grade da p.46 (vetorizar_luos.py)
d169 = fitz.open(f'{BASE}/fontes/LC169_2024_AlteraLUOS.pdf')
pg169 = d169[0]; bb = pg169.get_image_bbox([i for i in pg169.get_images(full=True) if i[0] == 23][0])
p = fitz.open(f'{BASE}/fontes/LC166_2024_LUOS_republicada_SAPL.pdf')[45]
S = 0.5                                   # px por pt da prancha A0 (≈ 17,6 m/px)
z = S * p.rect.width / bb.width           # zoom para renderizar a imagem do DOM (render trata CMYK corretamente)
pixb = pg169.get_pixmap(matrix=fitz.Matrix(z, z), clip=bb, alpha=False)
img = np.frombuffer(pixb.samples, np.uint8).reshape(pixb.height, pixb.width, 3)
pix = p.get_pixmap(matrix=fitz.Matrix(S, S), alpha=False)
ref = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
Image.fromarray(img).save(f'{BASE}/geo_raw/thumbs/lc169_anexoI_render.png')
# registro: mesma prancha -> escala ~1; refina translação/escala por correlação de bordas (ECC afim)
g1 = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY).astype(np.float32); g2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
g2p = np.full_like(g1, 255); hh, ww = min(g1.shape[0], g2.shape[0]), min(g1.shape[1], g2.shape[1]); g2p[:hh, :ww] = g2[:hh, :ww]
A = np.eye(2, 3, dtype=np.float32)
cc, A = cv2.findTransformECC(cv2.GaussianBlur(g1, (5, 5), 0), cv2.GaussianBlur(g2p, (5, 5), 0), A, cv2.MOTION_AFFINE,
                             (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
print('ECC', cc, A.round(4))
img_p = np.full_like(ref, 255); img_p[:hh, :ww] = img[:hh, :ww]
warped = cv2.warpAffine(img_p, A, (ref.shape[1], ref.shape[0]), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, borderValue=(255, 255, 255))
names = list(CORES.values()); pal = np.array([[c * 255 for c in k] for k in CORES], float)
def palette_from_legend(im):
    """mediana dos pixels mais saturados/escuros no símbolo de legenda de cada linha (x 2870..2960 pt)."""
    out = []
    for j in range(len(names)):
        yc = 301.5 + j * 23.55
        patch = im[int((yc - 6) * S):int((yc + 6) * S), int(2870 * S):int(2960 * S)].reshape(-1, 3).astype(float)
        sat = patch.max(1) - patch.min(1) + (255 - patch.mean(1)) * 0.5
        sel = patch[sat >= np.percentile(sat, 80)]
        out.append(np.median(sel, 0))
    return np.array(out, float)
pal2 = palette_from_legend(warped)
for n_, a_, b_ in zip(names, pal, pal2): print(f'{n_:7s}', a_.round(), b_.round())
def classify(im, P, thr=45):
    a = im.astype(float); best = np.full(a.shape[:2], 1e9); cls = np.full(a.shape[:2], -1)
    for j, c in enumerate(P):
        dd = ((a - c) ** 2).sum(-1); upd = dd < best; best[upd] = dd[upd]; cls[upd] = j
    cls[np.sqrt(best) > thr] = -1
    return cls
c1 = classify(ref, pal, 20); c2 = classify(warped, pal2, 45)
c2 = ndimage.median_filter(c2, 3)
frame = np.zeros(c1.shape, bool); frame[int(20 * S):int(2356 * S), int(259 * S):int(2505 * S)] = True
valid = (c1 >= 0) & (c2 >= 0) & frame
diff = valid & (c1 != c2)
mpx = 8.81947 / S
print('m/px', mpx, 'frac divergente', diff.sum() / valid.sum())
diff2 = ndimage.binary_opening(diff, iterations=2)
pair = np.where(diff2, c1 * 100 + c2, -1)
lab = np.zeros(diff2.shape, np.int32); n = 0
for pv in np.unique(pair[pair >= 0]):          # rotula separadamente cada par (zona LUOS -> zona LC169)
    l_, k_ = ndimage.label(pair == pv); lab[l_ > 0] = l_[l_ > 0] + n; n += k_
out = []
for i in range(1, n + 1):
    mk = lab == i; ha = mk.sum() * mpx ** 2 / 1e4
    if ha < 3: continue
    ys, xs = np.nonzero(mk)
    a = np.bincount(c1[mk], minlength=len(names)).argmax(); b = np.bincount(c2[mk], minlength=len(names)).argmax()
    cx, cy = xs.mean() / S, ys.mean() / S
    out.append({'ha': round(float(ha), 1), 'luos_166': names[a], 'lc_169': names[b], 'pdf_xy': [round(cx), round(cy)],
                'utm_31985': [round(AX[0] * cx + AX[1]), round(AY[0] * cy + AY[1])]})
out.sort(key=lambda r: -r['ha'])
for r in out[:60]: print(r)
json.dump({'metodo': 'ORB+RANSAC afim; paleta da legenda; mediana 5px; abertura 3; manchas>=3 ha',
           'm_por_pixel_ref': mpx, 'frac_divergente': float(diff.sum() / valid.sum()), 'manchas': out},
          open(f'{BASE}/geo_raw/dif_lc169.json', 'w'), ensure_ascii=False, indent=1)
vis = (ref * 0.5 + 127).astype(np.uint8); vis[diff2] = [255, 0, 0]
Image.fromarray(vis).resize((vis.shape[1] // 2, vis.shape[0] // 2)).save(f'{BASE}/geo_raw/thumbs/dif_lc169.png')

# ---- exporta manchas (>=5 ha) como polígonos UTM com a classe da LC 169 ----
from shapely.geometry import box, mapping
from shapely.ops import unary_union
feats = []
for i in range(1, n + 1):
    mk = lab == i; ha = mk.sum() * mpx ** 2 / 1e4
    if ha < 5: continue
    b = np.bincount(c2[mk], minlength=len(names)).argmax(); a = np.bincount(c1[mk], minlength=len(names)).argmax()
    ys, xs = np.nonzero(mk)
    sq = []
    for yy in np.unique(ys):                  # junta corridas horizontais de pixels
        xr = np.sort(xs[ys == yy]); br = np.split(xr, np.where(np.diff(xr) > 1)[0] + 1)
        for run in br:
            sq.append(box(run[0] / S, yy / S, (run[-1] + 1) / S, (yy + 1) / S))
    g = unary_union(sq)
    gu = __import__('shapely').affinity.affine_transform(g, [AX[0], 0, 0, AY[0], AX[1], AY[1]]).buffer(0).simplify(10)
    feats.append({'type': 'Feature', 'properties': {'luos_166': names[a], 'lc_169': names[b], 'ha': round(float(ha), 1)}, 'geometry': mapping(gu)})
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'features': feats}, open(f'{BASE}/geo_raw/dif_lc169_manchas_utm.geojson', 'w'))
print('manchas exportadas', len(feats))
