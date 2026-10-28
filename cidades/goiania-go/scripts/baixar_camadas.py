#!/usr/bin/env python3
"""Baixa camadas oficiais públicas (ArcGIS REST, sem login) do Portal Mapa de Goiânia
(https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer) para geo_raw/*.geojson (EPSG:4326).
Uso: python3 baixar_camadas.py [--force]"""
import json, os, sys, time, urllib.parse, urllib.request
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, mapping
from shapely.validation import make_valid

BASE = "https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer"
OUT = os.path.join(os.path.dirname(__file__), "..", "geo_raw")
CAMADAS = {
    # nome_arquivo: (servico/tipo, layer_id)
    "ut_simplifica": ("Mapa_Simplifica_Goiania_UsoDoSolo/FeatureServer", 3),
    "me_bem_tombado_apac": ("Mapa_ModeloEspacial/MapServer", 28),
    "me_ooau": ("Mapa_ModeloEspacial/MapServer", 32),
    "me_macrozoneamento": ("Mapa_ModeloEspacial/MapServer", 33),
    "me_limite_municipio": ("Mapa_ModeloEspacial/MapServer", 34),
    "me_aeis": ("Mapa_ModeloEspacial/MapServer", 7),
    "me_pe_urbanistico": ("Mapa_ModeloEspacial/MapServer", 8),
    "me_pe_ambiental": ("Mapa_ModeloEspacial/MapServer", 9),
    "me_pe_economico": ("Mapa_ModeloEspacial/MapServer", 10),
    "me_aede": ("Mapa_ModeloEspacial/MapServer", 12),
    "me_abadee": ("Mapa_ModeloEspacial/MapServer", 13),
    "me_arau_app": ("Mapa_ModeloEspacial/MapServer", 21),
    "me_arau_arct": ("Mapa_ModeloEspacial/MapServer", 22),
    "me_arau_upi": ("Mapa_ModeloEspacial/MapServer", 24),
    "me_arau_uus": ("Mapa_ModeloEspacial/MapServer", 25),
    "me_arau_areas_verdes": ("Mapa_ModeloEspacial/MapServer", 26),
    "me_arau_jardim_botanico": ("Mapa_ModeloEspacial/MapServer", 27),
    "me_arar_app": ("Mapa_ModeloEspacial/MapServer", 14),
    "me_arar_upi": ("Mapa_ModeloEspacial/MapServer", 17),
    "me_arar_uus": ("Mapa_ModeloEspacial/MapServer", 18),
    "me_ive": ("Mapa_ModeloEspacial/MapServer", 5),
    "me_corredores": ("Mapa_ModeloEspacial/MapServer", 1),
    "me_eixo_desenvolvimento": ("Mapa_ModeloEspacial/MapServer", 4),
    "me_declividade30": ("Mapa_ModeloEspacial/MapServer", 2),
    "me_aero_aproximacao": ("Mapa_ModeloEspacial/MapServer", 38),
    "me_aero_ruido": ("Mapa_ModeloEspacial/MapServer", 39),
    "me_aero_seguranca": ("Mapa_ModeloEspacial/MapServer", 40),
    "me_restricao_militar": ("Mapa_ModeloEspacial/MapServer", 44),
    "med_entorno_bem_tombado": ("Mapa_ModeloEspacial_Desenvolvimento/MapServer", 46),
    "med_bem_tombado": ("Mapa_ModeloEspacial_Desenvolvimento/MapServer", 45),
}

def get(url, params, tries=4):
    data = urllib.parse.urlencode(params).encode()
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers={"User-Agent": "curl/8.5.0"}), timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("  retry", i, e); time.sleep(3 * (i + 1))
    raise RuntimeError(url)

def ring_area(r):
    return sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1)) / 2.0

def esri2shape(g):
    if g is None: return None
    if "rings" in g:
        ext, holes = [], []
        for r in g["rings"]:
            if len(r) < 4: continue
            (ext if ring_area(r) < 0 else holes).append(r)  # esri: horário = exterior
        polys = [[Polygon(e), []] for e in ext]
        for h in holes:
            hp = Polygon(h)
            for p in polys:
                if p[0].contains(hp.representative_point()):
                    p[1].append(h); break
            else:
                polys.append([hp, []])
        out = [Polygon(p[0].exterior.coords, p[1]) for p in polys]
        geom = MultiPolygon(out) if len(out) > 1 else (out[0] if out else None)
        return make_valid(geom) if geom is not None and not geom.is_valid else geom
    if "paths" in g:
        ls = [LineString(p) for p in g["paths"] if len(p) >= 2]
        return MultiLineString(ls) if len(ls) > 1 else (ls[0] if ls else None)
    if "x" in g: return Point(g["x"], g["y"])

def baixar(nome, svc, lid, force=False):
    dst = os.path.join(OUT, nome + ".geojson")
    if os.path.exists(dst) and not force:
        print("cache", nome); return
    url = f"{BASE}/{svc}/{lid}/query"
    r0 = get(url, {"where": "1=1", "returnIdsOnly": "true", "f": "json"})
    ids = r0.get("objectIds") or []
    oidf = r0.get("objectIdFieldName", "OBJECTID")
    feats = []
    ids.sort()
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        print("  ", nome, i, "/", len(ids), flush=True)
        d = get(url, {"objectIds": ",".join(map(str, chunk)), "outFields": "*", "outSR": "4326",
                      "returnGeometry": "true", "geometryPrecision": "7", "f": "json"})
        for f in d.get("features", []):
            g = esri2shape(f.get("geometry"))
            if g is None or g.is_empty: continue
            props = {k: v for k, v in f["attributes"].items() if not k.lower().startswith(("shape", "created", "last_edit"))}
            feats.append({"type": "Feature", "properties": props, "geometry": mapping(g)})
    meta = {"fonte_url": f"{BASE}/{svc}/{lid}", "baixado_em": time.strftime("%Y-%m-%d %H:%M %z"), "n": len(feats), "oid_field": oidf}
    json.dump({"type": "FeatureCollection", "meta": meta, "features": feats}, open(dst, "w"))
    print(nome, len(ids), "ids ->", len(feats), "features")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    force = "--force" in sys.argv
    for n, (s, l) in CAMADAS.items():
        baixar(n, s, l, force)
