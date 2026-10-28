"""Poligonais das ZEIS criadas pelas Leis 15.606/2025 (Democracia) e 15.607/2025 (Rio Sanhauá):
quadros de coordenadas UTM SIRGAS 2000 (fuso 25S, EPSG:31985) publicados nos Anexos das leis.
Democracia: transcrito do Anexo II (conferido visualmente). Rio Sanhauá: OCR do Anexo I (p.5), conferido
pelas distâncias entre pontos do próprio quadro e pela área declarada no art. 1º."""
import re, json, math
from shapely.geometry import Polygon, mapping
B = '../'
DEMO = [(298599.91, 9206732.13), (299110.98, 9206727.82), (299108.19, 9206668.27), (298811.24, 9206680.81),
        (298810.16, 9206655.83), (298789.17, 9206656.72), (298641.93, 9206674.17), (298599.91, 9206678.51)]
DEMO_D = [511.09, 59.62, 297.21, 25.00, 21.01, 148.27, 42.24, 53.62]
txt = open(B + 'fontes/Lei15607_2025_ZEIS_RioSanhaua.ocr.txt').read().split('===== página 6')[0].split('===== página 5')[1]
num = lambda s: float(s.replace('.', '').replace(',', '.')[:-2] + '.' + s.replace('.', '').replace(',', '.')[-2:]) if False else float(re.sub(r'[.,](\d{2})$', r'#\1', s).replace('.', '').replace(',', '').replace('#', '.'))
RIO, RIO_D = [], []
for m in re.finditer(r'^P(\d+) \| ([\d.,]+) \| ([\d.,]+) \| P\d+ \| P\d+ \| ([\d.,]+)', txt, re.M):
    RIO.append((num(m.group(2)), num(m.group(3)))); RIO_D.append(float(m.group(4).replace(',', '.')))
def chk(nome, pts, dist, area_decl):
    n = len(pts); err = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]; d = math.dist(a, b); err.append(abs(d - dist[i]))
    pol = Polygon(pts)
    print(nome, n, 'pontos; erro máx distância', round(max(err), 2), 'm; área', round(pol.area, 2), 'declarada', area_decl, 'válido', pol.is_valid)
    assert max(err) < 0.5 and abs(pol.area - area_decl) / area_decl < 0.01
    return pol
p1 = chk('ZEIS Democracia', DEMO, DEMO_D, 29920.83)
p2 = chk('ZEIS Rio Sanhauá', RIO, RIO_D, 10967.04)
json.dump({'type': 'FeatureCollection', 'crs': 'EPSG:31985', 'features': [
    {'type': 'Feature', 'properties': {'codigo': 'ZEIS-DEMOCRACIA', 'nome': 'ZEIS Democracia (Mangabeira/Costa do Sol)', 'lei': 'Lei 15.606/2025', 'area_m2': round(p1.area, 2)}, 'geometry': mapping(p1)},
    {'type': 'Feature', 'properties': {'codigo': 'ZEIS-RIO-SANHAUA', 'nome': 'ZEIS Rio Sanhauá (Varadouro)', 'lei': 'Lei 15.607/2025', 'area_m2': round(p2.area, 2)}, 'geometry': mapping(p2)}]},
    open(B + 'geo_raw/zeis_leis_2025_utm.geojson', 'w'))
