"""Gera mapa.html (Leaflet) e visao_geral_zoneamento.png a partir das camadas oficiais + campo-grande-ms.json.
No HTML as geometrias são simplificadas (tolerância ~1,5 m) só para leveza visual; a consulta oficial usa as geometrias completas."""
import json, shapely
from shapely.geometry import shape, mapping
P = json.load(open("../../campo-grande-ms.json"))
Zj = {z["codigo"]: z for z in P["zonas"]}
fid = P["outorga_onerosa"]["fator_fid_por_zona"]["valor"]
def val(c, k):
    z = Zj.get(c); v = z and z["parametros"].get(k)
    return v.get("valor") if isinstance(v, dict) else None
def ficha(c):
    if c not in Zj: return None
    return {"nome": Zj[c]["nome"], "ca_min": val(c,"ca_minimo"), "ca_bas": val(c,"ca_basico"), "ca_max": val(c,"ca_maximo"),
            "to": val(c,"taxa_ocupacao"), "ie": val(c,"indice_elevacao"), "lote": val(c,"lote_minimo_m2"), "testada": val(c,"testada_minima_m"),
            "fid": fid.get(c), "cit": (Zj[c]["parametros"].get("ca_basico") or {}).get("artigo_anexo")}
def load(n, tol=0.000015):
    d = json.load(open(n + ".geojson"))
    for f in d["features"]:
        g = shapely.make_valid(shape(f["geometry"])).simplify(tol, preserve_topology=True)
        f["geometry"] = mapping(g)
        f["properties"] = {k: v for k, v in f["properties"].items() if k in ("codigo","nome","bairro","identificador","subcodigo","taxa_permeabilidade","tra_minima","tipo","legislacao","categoria","zona")}
    return d
L = {n: load(n) for n in ["zonas","macrozonas","zonas_ambientais","zeis","eixos_centralidades","zeia","zeic","zepa","perimetro_urbano"]}
L["macrozonas"]["features"] = [f for f in L["macrozonas"]["features"] if f["properties"]["codigo"] in ("MZ1","MZ2","MZ3")]
fichas = {c: ficha(c) for c in Zj}
fontes = {f["id"]: f["url"] for f in P["fontes"]}
html = open("mapa_template.html").read().replace("__DATA__", json.dumps(L, ensure_ascii=False, separators=(",", ":"))) \
    .replace("__FICHAS__", json.dumps(fichas, ensure_ascii=False)).replace("__F01__", fontes["F01"]).replace("__F08__", fontes["F08"])
open("mapa.html", "w").write(html)

# PNG
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
cores = {"Z1":"#7f0000","Z2":"#d7301f","Z3":"#fc8d59","Z4":"#fdcc8a","Z5":"#fef0d9","ZEIE":"#6a51a3","ZEU":"#e5f5e0","ANHANDUI":"#cccccc"}
fig, ax = plt.subplots(figsize=(13, 12), dpi=150)
def plot(g, **kw):
    gs = getattr(g, "geoms", [g])
    for p in gs:
        if p.geom_type == "Polygon":
            ax.fill(*p.exterior.xy, **kw)
        elif p.geom_type in ("LineString",):
            ax.plot(*p.xy, **kw)
        elif hasattr(p, "geoms"):
            plot(p, **kw)
Zf = json.load(open("zonas.geojson"))["features"]
for f in Zf:
    c = f["properties"]["codigo"]
    if c in ("ZEU", "ANHANDUI"): continue
    if c == "ZEIE": continue
    plot(shape(f["geometry"]), fc=cores[c], ec="#555", lw=0.3)
for f in Zf:
    if f["properties"]["codigo"] == "ZEIE": plot(shape(f["geometry"]), fc=cores["ZEIE"], ec="k", lw=0.4, alpha=0.85)
for f in json.load(open("eixos_centralidades.geojson"))["features"]:
    g = shape(f["geometry"])
    if f["properties"]["codigo"] == "ZC": plot(g, fc="#1f78b4", ec="k", lw=0.5, alpha=0.85)
    else: plot(g, color="#00e5ff", lw=2.2)
for f in json.load(open("zeis.geojson"))["features"]:
    plot(shape(f["geometry"]), fc="#33a02c" if f["properties"]["codigo"] == "ZEIS2" else "#b2df8a", ec="#1b5e20", lw=0.3, alpha=0.9)
for f in json.load(open("perimetro_urbano.geojson"))["features"]:
    g = shape(f["geometry"]); ax.plot(*g.exterior.xy, color="k", lw=1.2, ls="--")
for f in json.load(open("macrozonas.geojson"))["features"]:
    if f["properties"]["codigo"] in ("MZ1","MZ2","MZ3"):
        pass
ax.set_aspect(1 / 0.937); ax.set_xlim(-54.77, -54.495); ax.set_ylim(-20.60, -20.36)
leg = [Patch(fc=cores[k], ec="#555", label=k) for k in ("Z1","Z2","Z3","Z4","Z5")] + [Patch(fc=cores["ZEIE"], label="ZEIE"), Patch(fc="#1f78b4", label="ZC – Centralidades"),
       Line2D([0],[0], color="#00e5ff", lw=2.2, label="EA1–EA3 – Eixos de Adensamento"), Patch(fc="#33a02c", label="ZEIS 2"), Patch(fc="#b2df8a", label="ZEIS 1"),
       Line2D([0],[0], color="k", ls="--", label="Perímetro urbano (Sede)")]
ax.legend(handles=leg, loc="lower left", fontsize=9, framealpha=0.9)
ax.set_title("Campo Grande/MS – Zoneamento PDDUA (LC 341/2018 consolidada)\nZonas urbanas, ZEIE, ZC, Eixos de Adensamento e ZEIS", fontsize=13)
ax.text(0.99, 0.01, "Fonte: SIMGEO/PLANURB – Prefeitura de Campo Grande, ArcGIS REST público\n(PLANO_DIRETOR_PPDUA/PLANO_DIRETOR__PDDUA/MapServer), dados de 27/10/2026. EPSG:4326.\nIndicativo – não substitui a GDU/PLANURB.",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, bbox=dict(fc="white", alpha=0.8, ec="none"))
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.grid(alpha=0.2)
plt.tight_layout(); plt.savefig("visao_geral_zoneamento.png"); print("ok")
