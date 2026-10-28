"""Vetoriza o Anexo II (mapa de ZEIS) da LC 171/2025, em vigor, publicado só como imagem (DOM, LC171 p.3, xref 40).
O layout da prancha difere do PD original, então o registro é SIFT + RANSAC (afim) contra a prancha vetorial
do PD p.76 (mesma base cartográfica), cuja grade UTM é conhecida. Pixels de ZEIS = vermelho saturado.
Rodar com /workspace/.venv_ocr/bin/python. Saída: geo_raw/lc171_zeis_utm.geojson (EPSG:31985)."""
import os, json
import numpy as np, cv2, pymupdf as fitz
from scipy import ndimage
from shapely.geometry import box, mapping
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AX = (8.81945, 279883.07); AY = (-8.81945, 9219830.13)
S = 0.5
p = fitz.open(f'{B}/fontes/LC164_2024_PlanoDiretor_SAPL.pdf')[75]
pg = fitz.open(f'{B}/fontes/LC171_2025_AlteraPD.pdf')[2]
bb = pg.get_image_bbox([i for i in pg.get_images(full=True) if i[0] == 40][0])
z = 1144 / bb.width * 1.5                      # ~1,5x a resolução nativa da imagem
pb = pg.get_pixmap(matrix=fitz.Matrix(z, z), clip=bb, alpha=False)
img = np.frombuffer(pb.samples, np.uint8).reshape(pb.height, pb.width, 3).copy()
pr = p.get_pixmap(matrix=fitz.Matrix(S, S), alpha=False)
ref = np.frombuffer(pr.samples, np.uint8).reshape(pr.height, pr.width, 3)
sift = cv2.SIFT_create(20000)
k1, d1 = sift.detectAndCompute(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), None)
k2, d2 = sift.detectAndCompute(cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY), None)
mt = cv2.BFMatcher().knnMatch(d1, d2, k=2)
good = [m for m, n in mt if m.distance < 0.75 * n.distance]
src = np.float32([k1[m.queryIdx].pt for m in good]); dst = np.float32([k2[m.trainIdx].pt for m in good])
A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=3.0, maxIters=20000)
inl = inl.ravel().astype(bool)
res = np.sqrt((((src[inl] @ A[:, :2].T + A[:, 2]) - dst[inl]) ** 2).sum(1))
mpx = AX[0] / S
print('matches', len(good), 'inliers', inl.sum(), 'resid px ref med/p90', np.median(res).round(2), np.percentile(res, 90).round(2),
      '-> m', (np.median(res) * mpx).round(1), (np.percentile(res, 90) * mpx).round(1))
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
red = ((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 70) & (hsv[..., 2] > 80)
# exclui legenda/quadros (fora da área do mapa): mapa ocupa ~x<84% da largura
red[:, int(0.845 * red.shape[1]):] = False
red = ndimage.binary_closing(red, iterations=2)    # fecha vazios das ruas brancas dentro das ZEIS
red = ndimage.binary_fill_holes(red)
# sem abertura: preserva ZEIS estreitas
lab, n = ndimage.label(red)
T = [A[0, 0] / S, A[0, 1] / S, A[1, 0] / S, A[1, 1] / S, A[0, 2] / S, A[1, 2] / S]   # img px -> pt PDF
feats = []
for i in range(1, n + 1):
    mk = lab == i
    ys, xs = np.nonzero(mk)
    sq = []
    for yy in np.unique(ys):
        xr = np.sort(xs[ys == yy])
        for run in np.split(xr, np.where(np.diff(xr) > 1)[0] + 1):
            sq.append(box(run[0], yy, run[-1] + 1, yy + 1))
    g = affinity.affine_transform(unary_union(sq), T)
    g = affinity.affine_transform(g, [AX[0], 0, 0, AY[0], AX[1], AY[1]]).buffer(0)
    if g.area < 2000: continue                       # descarta ruídos < 0,2 ha
    g = g.simplify(5)
    feats.append({'type': 'Feature', 'properties': {'codigo': 'ZEIS', 'area_ha': round(g.area / 1e4, 2)}, 'geometry': mapping(g)})
feats.sort(key=lambda f: -f['properties']['area_ha'])
for k, f in enumerate(feats): f['properties']['parte'] = k + 1
tot = sum(f['properties']['area_ha'] for f in feats)
print('manchas ZEIS', len(feats), 'área total ha', round(tot, 1), 'px/m imagem', round(mpx * np.sqrt(abs(np.linalg.det(A[:, :2]))), 1))
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'registro': {'afim_img_para_ref': A.tolist(),
           'inliers': int(inl.sum()), 'resid_med_m': float(np.median(res) * mpx), 'resid_p90_m': float(np.percentile(res, 90) * mpx),
           'm_por_px_imagem': float(mpx * np.sqrt(abs(np.linalg.det(A[:, :2]))))}, 'features': feats},
          open(f'{B}/geo_raw/lc171_zeis_utm.geojson', 'w'))
Image.fromarray((red * 255).astype(np.uint8)).save(f'{B}/geo_raw/thumbs/lc171_zeis_mask.png')
