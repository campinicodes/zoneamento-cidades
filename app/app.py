"""Plataforma multicidades – consulta de zoneamento por polígono (Flask).

Descobre automaticamente  <PLATAFORMA_CIDADES>/<slug>/<slug>.json  (padrão ../PADRAO_JSON.md).
Padrão: ../cidades  (várias pastas separadas por ':' na variável de ambiente PLATAFORMA_CIDADES).
O motor (motor.py) é genérico: nada de regra por cidade aqui.

Rodar:  pip install -r requirements.txt && python app.py   →  http://127.0.0.1:5000
AVISO: resultado indicativo; não substitui a manifestação oficial da prefeitura.
"""
import html
import io
import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET

import shapely
from flask import Flask, abort, jsonify, render_template, request
from shapely.geometry import mapping, shape

import motor

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTAS = os.environ.get("PLATAFORMA_CIDADES", os.path.join(os.path.dirname(AQUI), "cidades")).split(os.pathsep)
REG = motor.Registro(PASTAS)
MAX_POLIGONOS = 200

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# ---------------------------------------------------------------------------
# Entrada: GeoJSON e KML/KMZ (todos os polígonos)
# ---------------------------------------------------------------------------
def poligonos_geojson(obj, nome=None):
    """[(nome, geometria shapely)] – um item por Feature/Geometry poligonal."""
    t = obj.get("type")
    if t == "FeatureCollection":
        out = []
        for i, f in enumerate(obj.get("features", [])):
            out += poligonos_geojson(f, (f.get("properties") or {}).get("name") or (f.get("properties") or {}).get("nome") or f"polígono {i + 1}")
        return out
    if t == "Feature":
        return poligonos_geojson(obj.get("geometry") or {}, nome or (obj.get("properties") or {}).get("name"))
    if t in ("Polygon", "MultiPolygon"):
        return [(nome or "polígono 1", shape(obj))]
    return []


def _local(el):
    return el.tag.rsplit("}", 1)[-1]


def _anel(texto):
    pts = []
    for tupla in texto.split():
        p = tupla.split(",")
        if len(p) >= 2:
            pts.append((float(p[0]), float(p[1])))
    return pts


def _poligonos_do_elemento(el):
    out = []
    for pol in (x for x in el.iter() if _local(x) == "Polygon"):
        ext, ints = None, []
        for sub in pol.iter():
            if _local(sub) in ("outerBoundaryIs", "innerBoundaryIs"):
                c = next((x for x in sub.iter() if _local(x) == "coordinates"), None)
                if c is not None and c.text:
                    anel = _anel(c.text)
                    if _local(sub) == "outerBoundaryIs":
                        ext = anel
                    elif len(anel) >= 3:
                        ints.append(anel)
        if ext and len(ext) >= 3:
            out.append(shapely.make_valid(shapely.Polygon(ext, ints)))
    return out


def poligonos_kml(kml_bytes):
    """Um item por Placemark com polígono(s) (MultiGeometry vira MultiPolygon); nome = <name> do Placemark."""
    raiz = ET.fromstring(kml_bytes)
    out = []
    for i, pm in enumerate(x for x in raiz.iter() if _local(x) == "Placemark"):
        polys = _poligonos_do_elemento(pm)
        if not polys:
            continue
        nome = next((x.text.strip() for x in pm if _local(x) == "name" and x.text), None) or f"polígono {len(out) + 1}"
        out.append((nome, polys[0] if len(polys) == 1 else shapely.union_all(polys)))
    if not out:   # KML sem Placemark (raro): polígonos soltos
        out = [(f"polígono {i + 1}", g) for i, g in enumerate(_poligonos_do_elemento(raiz))]
    return out


def ler_arquivo(nome, conteudo):
    n = (nome or "").lower()
    if n.endswith((".geojson", ".json")):
        return poligonos_geojson(json.loads(conteudo))
    if n.endswith(".kmz") or conteudo[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
            kmls = sorted((x for x in z.namelist() if x.lower().endswith(".kml")), key=lambda x: (x.lower() != "doc.kml", x))
            if not kmls:
                raise ValueError("KMZ sem .kml dentro.")
            out = []
            for k in kmls:       # todos os KML do KMZ
                out += poligonos_kml(z.read(k))
            return out
    return poligonos_kml(conteudo)


# ---------------------------------------------------------------------------
# Consulta de vários polígonos
# ---------------------------------------------------------------------------
def consultar(polys, slug=None):
    if not polys:
        raise ValueError("Nenhum polígono encontrado.")
    if len(polys) > MAX_POLIGONOS:
        raise ValueError(f"Máximo de {MAX_POLIGONOS} polígonos por consulta.")
    if slug and slug not in REG.cidades:
        raise ValueError(f"Cidade '{slug}' não cadastrada.")
    resultados = []
    for nome, g in polys:
        item = {"nome": nome, "geometria": mapping(g)}
        if slug:
            cid, como = REG.cidades[slug], "escolhida pelo usuário"
        else:
            cid, como = REG.detectar(g)
        if cid is None:
            item["erro"] = "Polígono fora das cidades cadastradas: " + ", ".join(sorted(REG.cidades)) + "."
        else:
            try:
                item.update(motor.analisar(cid, g))
                item["cidade"]["deteccao"] = como
            except ValueError as e:
                item["erro"] = str(e)
        resultados.append(item)
    return {"n_poligonos": len(resultados), "resultados": resultados,
            "aviso": "Resultado indicativo. Confirme na prefeitura antes de qualquer decisão."}


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/cidades")
def api_cidades():
    return jsonify({"cidades": [{**c.meta, "bbox": c.bbox, "carregada": c.carregada, "tamanho_mb": c.tamanho_mb,
                                 "avisos_validacao": len(c.avisos_validacao), "status": c.status} for c in REG.cidades.values()],
                    "invalidas": REG.invalidas, "pastas": PASTAS})


@app.get("/api/zonas/<slug>")
def api_zonas(slug):
    c = REG.cidades.get(slug) or abort(404)
    d = c.dados()
    feats = []
    for z in d["zonas"]:
        if request.args.get("tipo") and z["tipo"] != request.args["tipo"]:
            continue
        for f in z["geometria"]["features"]:
            feats.append({"type": "Feature", "geometry": f["geometry"],
                          "properties": {"codigo": z["codigo"], "tipo": z["tipo"], "rotulo": motor._rotulo(f.get("properties") or {})}})
    return jsonify({"type": "FeatureCollection", "features": feats})


@app.post("/api/consulta")
def api_consulta():
    """Corpo: GeoJSON (Geometry/Feature/FeatureCollection) ou {"geojson": ..., "cidade": "<slug>"}. Cidade opcional (?cidade=)."""
    try:
        corpo = request.get_json(force=True)
        slug = request.args.get("cidade") or (corpo.get("cidade") if isinstance(corpo, dict) else None) or None
        gj = corpo.get("geojson", corpo)
        return jsonify(consultar(poligonos_geojson(gj), slug))
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        return jsonify({"erro": str(e)}), 400


@app.post("/api/consulta-arquivo")
@app.post("/api/consulta-kmz")
def api_consulta_arquivo():
    f = request.files.get("arquivo")
    if not f:
        return jsonify({"erro": "Envie o campo 'arquivo' (KML, KMZ ou GeoJSON)."}), 400
    try:
        return jsonify(consultar(ler_arquivo(f.filename, f.read()), request.form.get("cidade") or request.args.get("cidade") or None))
    except (ValueError, ET.ParseError, zipfile.BadZipFile, json.JSONDecodeError) as e:
        return jsonify({"erro": f"Arquivo inválido: {e}"}), 400


# ---- /referencias/<slug>: REFERENCIAS.md + lacunas -------------------------
def md_para_html(md):
    """Markdown mínimo (títulos, listas, tabelas, citações, links, negrito, código) – sem dependências."""
    def inline(t):
        t = html.escape(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
        t = re.sub(r'(?<![">])(https?://[^\s<|]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
        return t
    out, tabela, lista = [], [], False
    def fecha():
        nonlocal tabela, lista
        if tabela:
            linhas = [l for l in tabela if not re.match(r"^\|[\s\-:|]+\|$", l)]
            cel = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
            out.append("<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cel(linhas[0])) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cel(l)) + "</tr>" for l in linhas[1:]) + "</table>")
            tabela = []
        if lista:
            out.append("</ul>"); lista = False
    for l in md.splitlines():
        if l.startswith("|"):
            tabela.append(l); continue
        if l.startswith("- "):
            if tabela: fecha()
            if not lista:
                out.append("<ul>"); lista = True
            out.append(f"<li>{inline(l[2:])}</li>"); continue
        fecha()
        m = re.match(r"^(#{1,4})\s+(.*)", l)
        if m:
            n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif l.startswith("> "):
            out.append(f"<blockquote>{inline(l[2:])}</blockquote>")
        elif l.strip():
            out.append(f"<p>{inline(l)}</p>")
    fecha()
    return "\n".join(out)


@app.get("/referencias/<slug>")
def referencias(slug):
    c = REG.cidades.get(slug) or abort(404)
    cam = os.path.join(c.pasta, "REFERENCIAS.md")
    md = open(cam, encoding="utf-8").read() if os.path.exists(cam) else "_Esta cidade ainda não tem REFERENCIAS.md._"
    d = c.dados()
    return render_template("referencias.html", cidade=c.meta, corpo=md_para_html(md), lacunas=d.get("lacunas") or [],
                           fontes=d.get("fontes") or [], avisos=c.avisos_validacao)


@app.get("/api/validar/<slug>")
def api_validar(slug):
    c = REG.cidades.get(slug) or abort(404)
    return jsonify(motor.validar(c.caminho))


if __name__ == "__main__":
    print("Cidades:", ", ".join(REG.cidades) or "(nenhuma)", "| inválidas:", ", ".join(REG.invalidas) or "nenhuma")
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)), debug=False)
