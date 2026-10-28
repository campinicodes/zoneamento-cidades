#!/usr/bin/env python3
"""Vetoriza (aproximado) o Mapa 03 do Anexo 02 da LOUOS (Gabarito de Altura Máxima na ABM), que no PDF
oficial é só imagem raster. Classifica pixels pela cor da legenda, filtra ruído, poligoniza e georreferencia
com a MESMA afim do Mapa 01A (mesmo layout/moldura; conferido contra o vetor oficial 'Limite da Borda Marítima').
Saída: geo_raw/mapa03_abm_gabarito.geojson (EPSG:4326)."""
import json, os, numpy as np, pymupdf, io
from PIL import Image
from scipy import ndimage
import rasterio.features
from affine import Affine
from shapely.geometry import shape, mapping
from shapely import make_valid
from pyproj import Transformer
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, 'fontes', 'SSA_LOUOS_03_GABARITO-ABM.compressed.pdf')
CLASSES = [  # (codigo, rgb da legenda medido no próprio PDF, gabarito m ou None)
 ('ABM-FAIXA-PRAIA', (254, 217, 102), None), ('ABM-GAB-06', (254, 254, 148), 6), ('ABM-GAB-09', (255, 254, 3), 9),
 ('ABM-GAB-12', (155, 196, 230), 12), ('ABM-GAB-15', (122, 135, 213), 15), ('ABM-GAB-18', (0, 113, 193), 18),
 ('ABM-GAB-24', (105, 236, 68), 24), ('ABM-GAB-30', (0, 175, 79), 30), ('ABM-GAB-36', (249, 136, 223), 36),
 ('ABM-GAB-45', (133, 56, 152), 45), ('ABM-GAB-51', (215, 27, 136), 51), ('ABM-APR', (168, 1, 0), None),
 ('ABM-ENCOSTA', (171, 101, 59), None), ('ABM-GAB-60', (205, 214, 0), 60), ('ABM-GAB-75', (231, 111, 24), 75)]
OUTROS = [(226, 226, 226), (255, 255, 255), (0, 0, 0), (190, 220, 235), (128, 128, 128), (255, 0, 0)]
THR = 38
def main():
    doc = pymupdf.open(PDF); x = doc.extract_image(doc[0].get_images()[0][0])
    im = np.array(Image.open(io.BytesIO(x['image'])).convert('RGB')).astype(np.float32)
    H, W, _ = im.shape
    pal = np.array([c for _, c, _ in CLASSES] + OUTROS, dtype=np.float32)
    lab = np.full((H, W), -1, np.int16)
    for y0 in range(0, H, 512):
        blk = im[y0:y0 + 512]
        d = np.sqrt(((blk[:, :, None, :] - pal[None, None]) ** 2).sum(-1))
        j = d.argmin(-1); dm = d.min(-1)
        j[(dm > THR) | (j >= len(CLASSES))] = -1
        lab[y0:y0 + 512] = j
    lab[1530:3865, 338:2052] = -1      # quadro de detalhe "Centro Antigo 1:12.500" (fora de posição)
    lab[:, 5700:] = -1                 # legenda/carimbo
    # ruído: abertura por classe e remoção de manchas < 60 px (~3.000 m²)
    out = np.full_like(lab, -1)
    for k in range(len(CLASSES)):
        m = ndimage.binary_opening(lab == k, iterations=1)
        m = ndimage.binary_closing(m, iterations=2)
        cc, n = ndimage.label(m)
        if n:
            sz = ndimage.sum(m, cc, range(1, n + 1)); keep = np.isin(cc, np.where(sz >= 60)[0] + 1)
            out[keep & (out == -1)] = k
    A = np.array(json.load(open(os.path.join(BASE, 'geo_raw', 'georref_mapa01a.json')))['afim_pdf_para_31984'])
    s = doc[0].get_image_rects(doc[0].get_images()[0][0])[0].width / W
    aff = Affine(A[0, 0] * s, A[0, 1] * s, A[0, 2], A[1, 0] * s, A[1, 1] * s, A[1, 2])
    T = Transformer.from_crs(31984, 4326, always_xy=True)
    tr = lambda g, TT: __import__('shapely').transform(g, lambda c: np.c_[TT.transform(c[:, 0], c[:, 1])])
    Tin = Transformer.from_crs(4326, 31984, always_xy=True)
    LIM = {f['properties']['cod']: tr(shape(f['geometry']), Tin) for f in
           json.load(open(os.path.join(BASE, 'geo_raw', 'limite_borda_maritima.geojson')))['features']}
    feats = []
    for geom, v in rasterio.features.shapes(out.astype(np.int16), mask=out >= 0, transform=aff):
        g = make_valid(shape(geom)).simplify(4)
        if g.area < 2500: continue
        cod, _, gab = CLASSES[int(v)]
        dmin = min(g.distance(LIM['BAT']), g.distance(LIM['BTS']))
        # o mapa desenha lagoas/rios/represas em azul-claro quase igual ao de 12 m: descarta manchas 12 m
        # fora da faixa da BTS (a leste do fim da linha oficial BTS ou a > 3 km dela); demais classes: > 3 km
        if cod == 'ABM-GAB-12' and (g.centroid.x > 559100 or g.distance(LIM['BTS']) > 3000): continue
        if dmin > 3000: continue
        g4 = __import__('shapely').transform(g, lambda c: np.c_[T.transform(c[:, 0], c[:, 1])])
        feats.append({'type': 'Feature', 'properties': {'codigo': cod, 'gabarito_m': gab}, 'geometry': mapping(g4)})
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(BASE, 'geo_raw', 'mapa03_abm_gabarito.geojson'), 'w'))
    import collections; c = collections.Counter(f['properties']['codigo'] for f in feats); print(len(feats), dict(c))
main()
