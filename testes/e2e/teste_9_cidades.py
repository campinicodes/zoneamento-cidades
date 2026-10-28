"""E2E contra a app rodando (http://127.0.0.1:5000): 1 terreno realista por cidade (escolhido pela própria camada
de zonas – dentro de uma zona base mista/residencial), detecção automática, KMZ com 3 cidades e tempos (1ª e seguintes)."""
import json, os, sys, time, io, zipfile, urllib.request
from shapely.geometry import shape, mapping, box
import warnings; warnings.filterwarnings("ignore", category=DeprecationWarning)
from shapely.ops import transform
from pyproj import Transformer

URL = os.environ.get("APP_URL", "http://127.0.0.1:5000")
CID = os.path.join(os.path.dirname(__file__), "..", "..", "cidades")
PREF = ["mista_media_densidade", "residencial_media_densidade", "mista_alta_densidade", "mista_baixa_densidade",
        "residencial_baixa_densidade", "residencial_alta_densidade", "centralidade"]


def post(path, corpo=None, arquivo=None):
    if arquivo:
        b = "----x"; nome, dados = arquivo
        body = (f"--{b}\r\nContent-Disposition: form-data; name=\"arquivo\"; filename=\"{nome}\"\r\n"
                f"Content-Type: application/octet-stream\r\n\r\n").encode() + dados + f"\r\n--{b}--\r\n".encode()
        req = urllib.request.Request(URL + path, body, {"Content-Type": f"multipart/form-data; boundary={b}"})
    else:
        req = urllib.request.Request(URL + path, json.dumps(corpo).encode(), {"Content-Type": "application/json"})
    t = time.perf_counter(); r = json.load(urllib.request.urlopen(req, timeout=300)); return r, time.perf_counter() - t


def terreno(slug):
    """Quadrado ~50x60 m dentro do maior polígono de uma zona base de categoria urbana comum."""
    d = json.load(open(os.path.join(CID, slug, f"{slug}.json"), encoding="utf-8"))
    bases = [z for z in d["zonas"] if z["tipo"] == "base"]
    bases.sort(key=lambda z: PREF.index(z["categoria_normalizada"]) if z["categoria_normalizada"] in PREF else 99)
    c = d["centro_mapa"]; zona_utm = int((c["lon"] + 180) // 6) + 1
    fwd = Transformer.from_crs(4326, 32700 + zona_utm, always_xy=True).transform
    inv = Transformer.from_crs(32700 + zona_utm, 4326, always_xy=True).transform
    for z in bases:
        polys = sorted((shape(f["geometry"]) for f in z["geometria"]["features"]), key=lambda g: -g.area)
        for g in polys[:3]:
            gm = transform(fwd, g.buffer(0))
            if gm.area < 20000:
                continue
            p = gm.buffer(-60).representative_point() if not gm.buffer(-60).is_empty else gm.representative_point()
            q = box(p.x - 25, p.y - 30, p.x + 25, p.y + 30)
            if gm.contains(q):
                return z["codigo"], z["categoria_normalizada"], transform(inv, q)
    raise RuntimeError(f"{slug}: sem zona adequada")


def kml(pols):
    pm = "".join(f"<Placemark><name>{n}</name><Polygon><outerBoundaryIs><LinearRing><coordinates>"
                 + " ".join(f"{x:.7f},{y:.7f},0" for x, y in g.exterior.coords)
                 + "</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>" for n, g in pols)
    k = f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>{pm}</Document></kml>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("doc.kml", k)
    return buf.getvalue()


if __name__ == "__main__":
    slugs = sorted(s for s in os.listdir(CID) if os.path.isfile(os.path.join(CID, s, f"{s}.json")))
    falhas, linhas, ter = 0, [], {}
    for s in slugs:
        zona, cat, g = terreno(s); ter[s] = g
        r1, t1 = post("/api/consulta", mapping(g))                       # sem cidade → detecção automática
        r2, t2 = post("/api/consulta", mapping(g))
        r3, t3 = post("/api/consulta", {"geojson": mapping(g), "cidade": s})
        it = r1["resultados"][0]
        ok = ("erro" not in it and it["cidade"]["slug"] == s and it["resultado"]["zona_base_predominante"] == zona
              and r3["resultados"][0]["resultado"]["zona_aplicavel"] == it["resultado"]["zona_aplicavel"])
        falhas += not ok
        res = it.get("resultado", {})
        ca = (it.get("parametros") or {}).get("parametros", {}).get("ca_maximo") or {}
        linhas.append(f"{'OK ' if ok else 'FALHA'} {s:18} zona-alvo={zona:12} ({cat:27}) detectada={it.get('cidade',{}).get('slug')} "
                      f"base={res.get("zona_base_predominante")} aplicável={res.get('zona_aplicavel')} CAmáx={ca.get('valor')}/{ca.get('forma')} "
                      f"alertas={len(it.get('alertas') or [])} | 1ª={t1*1000:.0f} ms, 2ª={t2*1000:.0f} ms, 3ª={t3*1000:.0f} ms"
                      + ("" if ok else f" | {json.dumps(it, ensure_ascii=False)[:400]}"))
        print(linhas[-1], flush=True)
    # KMZ com 3 cidades + 1 polígono fora
    tres = ["curitiba-pr", "rio-de-janeiro-rj", "salvador-ba"]
    fora = box(-50.0, -15.0, -49.999, -14.999)
    r, t = post("/api/consulta-arquivo", arquivo=("terrenos.kmz", kml([(f"T-{s}", ter[s]) for s in tres] + [("fora", fora)])))
    det = [x.get("cidade", {}).get("slug") or "ERRO:" + x.get("erro", "")[:40] for x in r["resultados"]]
    ok = det[:3] == tres and "erro" in r["resultados"][3]
    falhas += not ok
    print(f"{'OK ' if ok else 'FALHA'} KMZ 4 polígonos (3 cidades + 1 fora) → {det} em {t*1000:.0f} ms")
    print(f"\n{falhas} falha(s)")
    sys.exit(1 if falhas else 0)
