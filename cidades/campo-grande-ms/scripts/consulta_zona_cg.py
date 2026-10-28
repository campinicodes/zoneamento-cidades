#!/usr/bin/env python3
"""Consulta geográfica de zoneamento – Campo Grande/MS (PDDUA LC 341/2018 consolidada).

Uso:
  python3 consulta_zona_cg.py --lat -20.4630 --lon -54.6160
  python3 consulta_zona_cg.py --endereco "Rua 14 de Julho, 1000, Centro, Campo Grande"
Opções: --raio-limite 30 (m, alerta de divisa)  --raio-eixo 50 (m, possível lote lindeiro a EA)
        --saida arquivo.json  --compacto (só zona/índices principais)

Fontes: camadas vetoriais OFICIAIS do SIMGEO/PLANURB (ArcGIS Server público,
https://simgeoctm.campogrande.ms.gov.br/server/rest/services/PLANO_DIRETOR_PPDUA/PLANO_DIRETOR__PDDUA/MapServer),
baixadas em 27/10/2026 para geo/campo-grande/*.geojson (EPSG:4326), e parâmetros normativos de
campo-grande-ms.json (com citação lei/artigo/anexo/URL).
Geocodificação (--endereco): Nominatim/OpenStreetMap (© colaboradores OSM, ODbL) – APROXIMADA.
Dependências: shapely>=2, pyproj.
O resultado é indicativo e NÃO substitui a Guia de Diretrizes Urbanísticas (GDU) da PLANURB/SEMADUR."""
import argparse, json, os, sys, time, hashlib, urllib.parse, urllib.request
from shapely.geometry import shape, Point
import numpy as np
import shapely
from shapely.strtree import STRtree
from pyproj import Transformer

BASE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(BASE, "geo", "campo-grande")
JSON_PARAM = os.path.join(BASE, "campo-grande-ms.json")
UA = "TendaSTAR-consulta-zona-cg/1.0 (levantamento urbanistico MCMV; uso pontual, baixo volume)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
VIEWBOX = "-54.80,-20.33,-54.47,-20.66"  # bbox da Sede (perímetro urbano + ZEU)
CACHE = os.path.join(GEO, ".cache_geocode.json")
TO_UTM = Transformer.from_crs(4326, 31981, always_xy=True).transform  # SIRGAS 2000 / UTM 21S (metros)
def _utm(xy):
    x, y = TO_UTM(xy[:, 0], xy[:, 1])
    return np.column_stack([x, y])
CAMADAS = ["zonas", "macrozonas", "zonas_ambientais", "zeis", "eixos_centralidades", "zeia", "zeic",
           "zepa", "zeiu", "perimetro_urbano", "bairros", "apa_lajeado", "peuc", "iptu_progressivo",
           "ooaus_areas", "operacao_urbana_consorciada", "tdc_transferir", "tdc_receber"]

class Camada:
    def __init__(self, nome):
        d = json.load(open(os.path.join(GEO, nome + ".geojson"), encoding="utf-8"))
        self.nome, self.meta = nome, d.get("metadata", {})
        self.props = [f["properties"] for f in d["features"]]
        # make_valid só corrige auto-interseções topológicas (3 feições ZEIA1 da camada oficial); não move vértices
        self.geoms = [shapely.make_valid(shapely.transform(shape(f["geometry"]), _utm)) for f in d["features"]]
        self.tree = STRtree(self.geoms)
    def contem(self, p):
        return [int(i) for i in self.tree.query(p, predicate="intersects")]
    def proximos(self, p, raio):
        return [(int(i), d) for i in self.tree.query(p.buffer(raio)) if (d := self.geoms[i].distance(p)) <= raio]

def geocodificar(endereco):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    k = hashlib.sha1(endereco.lower().encode()).hexdigest()
    if k in cache:
        return cache[k]
    q = urllib.parse.urlencode({"q": endereco, "format": "jsonv2", "limit": 1, "countrycodes": "br",
                                "viewbox": VIEWBOX, "bounded": 1, "addressdetails": 1})
    time.sleep(1.1)  # política Nominatim: máx. 1 requisição/s
    req = urllib.request.Request(NOMINATIM + "?" + q, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if not res:
        return None
    out = {"lat": float(res[0]["lat"]), "lon": float(res[0]["lon"]), "display_name": res[0]["display_name"],
           "tipo_osm": f'{res[0].get("category")}/{res[0].get("type")}', "precisao": res[0].get("addresstype"),
           "fonte": "Nominatim/OpenStreetMap (© colaboradores OSM, ODbL)", "consultado_em": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    cache[k] = out
    json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
    return out

def consultar(lat, lon, raio_lim=30.0, raio_eixo=50.0):
    P = json.load(open(JSON_PARAM, encoding="utf-8"))
    zonas_json = {z["codigo"]: z for z in P["zonas"]}
    fontes = {f["id"]: f for f in P["fontes"]}
    C = {n: Camada(n) for n in CAMADAS}
    p = Point(TO_UTM(lon, lat))
    alertas, res = [], {}

    def dentro(n):
        return [(i, C[n].props[i], C[n].geoms[i]) for i in C[n].contem(p)]
    def resumo(n, i):
        pr = C[n].props[i]
        return {k: v for k, v in pr.items() if k in ("codigo", "subcodigo", "identificador", "nome", "zona", "bairro", "legislacao", "categoria", "macrozona")}
    def limite(n, cod_atual, chave="codigo"):
        viz = {}
        for i, d in C[n].proximos(p, raio_lim):
            c = C[n].props[i].get(chave)
            g = C[n].geoms[i]
            if c != cod_atual and not g.intersects(p):
                viz[c] = min(viz.get(c, 1e9), round(d, 1))
        for i, pr, g in dentro(n):
            if pr.get(chave) == cod_atual:
                db = g.boundary.distance(p)
                if db <= raio_lim and viz:
                    pass
        return viz

    # --- perímetros / macrozona
    perim = dentro("perimetro_urbano")
    mz = [pr for _, pr, _ in dentro("macrozonas") if pr.get("escala") != "municipal"]
    mzm = [pr for _, pr, _ in dentro("macrozonas") if pr.get("escala") == "municipal"]
    res["perimetro_urbano_sede"] = bool(perim)
    res["macrozona"] = None
    if mz:
        m = mz[0]
        res["macrozona"] = {"codigo": m["codigo"], "nome": m["nome"], "bairro": m.get("bairro"),
                            "parametros": P["macrozonas"].get(m["codigo"]), "camada": "Macrozonas - Urbana (SIMGEO id 24)"}
    if any(m["codigo"] == "MZS" for m in mzm):  # a camada oficial (id 23) tem sobreposição MZRA × MZS; dentro da Sede vale MZS
        mzm = [m for m in mzm if m["codigo"] == "MZS"]
    res["macrozona_municipal"] = [{"codigo": m["codigo"], "nome": m["nome"], "classificacao": m.get("classificacao")} for m in mzm]
    b = dentro("bairros")
    res["bairro"] = b[0][1].get("bairro") or b[0][1].get("nome") if b else None
    if b:
        res["regiao_urbana"] = b[0][1].get("regiao_urb") or b[0][1].get("regiao")

    # --- zona (precedência: ZEIE > ZC > EA lindeiro > Z1–Z5; fora do perímetro: ZEU / Anhanduí)
    zonas_pt = dentro("zonas")
    zbase = [pr for _, pr, _ in zonas_pt if pr["tipo"] == "zona_urbana"]
    zeie = [pr for _, pr, _ in zonas_pt if pr["codigo"] == "ZEIE"]
    zeu = [pr for _, pr, _ in zonas_pt if pr["codigo"] in ("ZEU", "ANHANDUI")]
    ec = dentro("eixos_centralidades")
    zc = [pr for _, pr, _ in ec if pr["codigo"] == "ZC"]
    eixos = sorted([(C["eixos_centralidades"].props[i], d) for i, d in C["eixos_centralidades"].proximos(p, raio_eixo)
                    if C["eixos_centralidades"].props[i]["tipo"] == "eixo_adensamento"], key=lambda x: x[1])
    res["zona_urbana_base"] = {"codigo": zbase[0]["codigo"], "bairro": zbase[0].get("bairro"), "legislacao": zbase[0]["legislacao"]} if zbase else None
    res["zeie"] = {"codigo": "ZEIE", "subcodigo": zeie[0].get("subcodigo"), "nome": zeie[0].get("nome")} if zeie else None
    res["zona_centralidade"] = {"codigo": "ZC", "nome": zc[0]["nome"]} if zc else None
    res["eixo_adensamento_proximo"] = [{"codigo": e["codigo"], "nome": e["nome"], "distancia_m": round(d, 1)} for e, d in eixos]

    if zeie:
        cod, motivo = "ZEIE", "Ponto em ZEIE – índices próprios prevalecem (Decreto 15.123/2022 art. 6º; PDDUA Anexo 8.2)."
    elif zc:
        cod, motivo = "ZC", "Ponto em Zona de Centralidade – índices da ZC prevalecem (Decreto 15.123/2022 art. 4º; PDDUA Anexo 8.2)."
    elif zbase:
        cod, motivo = zbase[0]["codigo"], "Zona urbana do bairro (PDDUA Anexo 6 – camada oficial Zonas urbanas)."
    elif zeu:
        cod, motivo = zeu[0]["codigo"], "Fora do perímetro urbano da Sede: " + ("Zona de Expansão Urbana (Anexo 3)." if zeu[0]["codigo"] == "ZEU" else "perímetro do Distrito de Anhanduí (Anexo 2.2).")
    else:
        cod, motivo = None, "Ponto fora do perímetro urbano, da ZEU e de Anhanduí (macrozona rural) – sem índices urbanos no JSON."
    res["zona_aplicavel"] = {"codigo": cod, "criterio": motivo}
    if eixos and cod not in ("ZEIE",):
        e, d = eixos[0]
        alertas.append(f"Ponto a {d:.0f} m do {e['nome']} (camada é LINHA). Se o lote tiver testada para o eixo, aplicam-se os índices de {e['codigo']} "
                       f"(Decreto 15.123/2022 art. 7º; PDDUA Anexo 8.2). Confirmar testada no cadastro/GDU.")

    # --- parâmetros da zona aplicável (do JSON, com citações)
    def params(c):
        z = zonas_json.get(c)
        return None if not z else {"codigo": z["codigo"], "nome": z["nome"], "parametros": z["parametros"], "observacoes": z.get("observacoes")}
    res["parametros_zona"] = params(cod)
    if eixos and cod not in ("ZEIE",):
        res["parametros_eixo_se_lindeiro"] = params(eixos[0][0]["codigo"])

    # --- ZEIS
    zs = dentro("zeis")
    res["zeis"] = [{"codigo": pr["codigo"], "identificador": pr.get("identificador"), "nome": pr.get("nome")} for _, pr, _ in zs]
    if zs:
        c = zs[0][1]["codigo"]
        res["parametros_zeis"] = params(c)
        res["zeis_his_regras"] = P["zeis_his"].get(c.lower())
        if c == "ZEIS2" and cod == "Z5":
            res["parametros_zona_efetivos_zeis2"] = params("Z4")
            alertas.append("ZEIS 2 sobre Z5: aplicam-se os índices da Z4 (LC 516/2023 art. 8º, alterando LC 421/2021).")
        if c == "ZEIS1":
            alertas.append("ZEIS 1 = ocupação consolidada para regularização fundiária; parâmetros dependem de plano de urbanização (PDDUA art. 29 I).")

    # --- Zona Ambiental (permeabilidade/TRA)
    za = dentro("zonas_ambientais")
    if za:
        pr = za[0][1]
        res["zona_ambiental"] = {"codigo": pr["codigo"], "taxa_permeabilidade_minima": pr["taxa_permeabilidade"], "tra_minima": pr["tra_minima"],
                                 "fator_alfa": pr.get("fator_alfa"), "fator_beta": pr.get("fator_beta"),
                                 "fonte": "PDDUA LC 341/2018 consolidada, art. 25 e Anexo 7.1 (F01); IA = V^α × D^β (Lei 6.914/2022, F18); camada SIMGEO 'Zonas ambientais - ZA' (id 15)",
                                 "url_lei": fontes["F01"]["url"]}
    else:
        res["zona_ambiental"] = None

    # --- sobreposições especiais
    for n, rot in (("zeia", "zeia"), ("zeic", "zeic"), ("zepa", "zepa"), ("zeiu", "zeiu"), ("apa_lajeado", "apa"),
                   ("peuc", "peuc"), ("iptu_progressivo", "iptu_progressivo"), ("ooaus_areas", "ooaus"),
                   ("operacao_urbana_consorciada", "ouc"), ("tdc_transferir", "tdc_transferir"), ("tdc_receber", "tdc_receber")):
        res[rot] = [resumo(n, i) for i, _, _ in dentro(n)]
    if res["zeia"]:
        c = res["zeia"][0]["codigo"]
        txt = {"ZEIA1": "ZEIA 1 = APP – não edificável (PDDUA arts. 37–38; Código Florestal).",
               "ZEIA2": "ZEIA 2 – supressão máx. de 40% da vegetação; índices da zona subjacente (PDDUA arts. 38–43).",
               "ZEIA3": "ZEIA 3 – potencial construtivo só transferível via TDC (PDDUA arts. 37–43).",
               "ZEIA4": "ZEIA 4 – sujeita a OODC/TDC/preempção (PDDUA arts. 37–43).",
               "ZEIA5": "ZEIA 5 – ver PDDUA arts. 37–43 e Anexo 15."}.get(c, c)
        alertas.append("Sobreposição com " + txt)
        if c == "ZEIA2":
            res["parametros_zeia"] = params("ZEIA2")
    if res["zepa"]:
        alertas.append("Ponto em ZEPA (Zona Especial de Proteção do Aeródromo) – restrições de gabarito do COMAER/PBZPA; consultar DECEA.")
    if res["zeic"]:
        alertas.append("Ponto em ZEIC (interesse cultural) – análise especial de patrimônio (PDDUA Anexo 12).")
    if res["apa"]:
        alertas.append("Ponto em APA (Lajeado) – observar plano de manejo / licenciamento ambiental.")
    if res["peuc"] or res["iptu_progressivo"]:
        alertas.append("Área demarcada para PEUC / IPTU progressivo no tempo (PDDUA Anexos 21–22): terreno vazio/subutilizado pode ser notificado – verificar situação da inscrição imobiliária.")

    # --- OODC
    fid = P["outorga_onerosa"]["fator_fid_por_zona"]
    cod_fid = (res.get("parametros_zona_efetivos_zeis2") or {}).get("codigo") or cod
    res["oodc"] = {"fid": fid["valor"].get(cod), "zona_fid": cod,
                   **({"fid_alternativo_z4": fid["valor"].get("Z4"), "observacao": "ZEIS 2 sobre Z5 usa índices da Z4 (LC 516/2023), mas a LC 469/2022 não diz se o Fid "
                       "passa a ser o da Z4; HIS pode ser isenta de OODC (LC 469/2022 art. 8º II – redação ambígua). Confirmar com PLANURB."} if cod_fid != cod else {}), "formula": P["outorga_onerosa"]["formula"]["valor"],
                   "fonte_id": fid["fonte_id"], "artigo_anexo": fid["artigo_anexo"], "url": fontes[fid["fonte_id"]]["url"]}

    # --- proximidade de limites (< raio_lim)
    lim = {}
    for n, cur in (("zonas", cod if cod in ("Z1","Z2","Z3","Z4","Z5","ZEIE","ZEU","ANHANDUI") else (zbase[0]["codigo"] if zbase else None)),
                   ("macrozonas", res["macrozona"]["codigo"] if res["macrozona"] else None),
                   ("zonas_ambientais", res["zona_ambiental"]["codigo"] if res["zona_ambiental"] else None),
                   ("zeis", res["zeis"][0]["codigo"] if res["zeis"] else None),
                   ("zeia", res["zeia"][0]["codigo"] if res["zeia"] else None)):
        for i, d in C[n].proximos(p, raio_lim):
            g, pr = C[n].geoms[i], C[n].props[i]
            if pr.get("escala") == "municipal":
                continue
            if g.intersects(p):
                db = g.boundary.distance(p)
                if db <= raio_lim:
                    lim.setdefault(n, []).append({"borda_de": pr.get("codigo"), "distancia_m": round(db, 1), "tipo": "distância até a borda do polígono que contém o ponto"})
            elif pr.get("codigo") != cur or n in ("zeis", "zeia"):
                lim.setdefault(n, []).append({"vizinho": pr.get("codigo"), "distancia_m": round(d, 1)})
    for n, ec_ in (("eixos_centralidades", None),):
        for i, d in C[n].proximos(p, raio_lim):
            pr = C[n].props[i]
            if pr["codigo"] == "ZC":
                lim.setdefault(n, []).append({"codigo": "ZC", "nome": pr["nome"], "distancia_m": round(d, 1) if d > 0 else round(C[n].geoms[i].boundary.distance(p), 1)})
    # remove duplicatas e mantém o menor
    for n in lim:
        u = {}
        for x in lim[n]:
            k = json.dumps({kk: vv for kk, vv in x.items() if kk != "distancia_m"}, ensure_ascii=False)
            if k not in u or x["distancia_m"] < u[k]["distancia_m"]:
                u[k] = x
        lim[n] = sorted(u.values(), key=lambda x: x["distancia_m"])
    res["limites_a_menos_de_%dm" % raio_lim] = lim
    if lim:
        alertas.append(f"Ponto a menos de {raio_lim:.0f} m de limite de zoneamento ({', '.join(lim)}). O lote pode estar em mais de uma zona "
                       "ou na divisa – Decreto 15.123/2022 art. 11 (lote em divisa de zonas) e PDDUA; confirmar com PLANURB.")

    alertas += [
        "Geometrias: camadas oficiais SIMGEO/PLANURB (ArcGIS público), escala de cadastro não garantida; o texto legal e os mapas anexos do PDDUA (LC 341/2018 consolidada) prevalecem.",
        "Consulta por ponto, não por lote: a zona do lote depende da sua geometria/testada. Confirmar na Guia de Diretrizes Urbanísticas (GDU) – PLANURB/SEMADUR.",
    ]
    return res, alertas

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float); ap.add_argument("--lon", type=float); ap.add_argument("--endereco")
    ap.add_argument("--raio-limite", type=float, default=30.0); ap.add_argument("--raio-eixo", type=float, default=50.0)
    ap.add_argument("--saida"); ap.add_argument("--compacto", action="store_true")
    a = ap.parse_args()
    geo = None
    if a.endereco:
        geo = geocodificar(a.endereco)
        if not geo:
            print(json.dumps({"erro": "Endereço não encontrado no Nominatim dentro da área de Campo Grande", "endereco": a.endereco}, ensure_ascii=False)); sys.exit(2)
        lat, lon = geo["lat"], geo["lon"]
    elif a.lat is not None and a.lon is not None:
        lat, lon = a.lat, a.lon
    else:
        ap.error("informe --lat e --lon, ou --endereco")
    res, alertas = consultar(lat, lon, a.raio_limite, a.raio_eixo)
    if geo:
        alertas.insert(0, f"Coordenada obtida por geocodificação Nominatim/OSM (precisão: {geo.get('precisao')}) – APROXIMADA; pode cair no lote vizinho, "
                          "no eixo da rua ou em outra quadra." + ("" if geo.get("precisao") in ("house", "building") else " O NÚMERO do imóvel não foi localizado no OSM: o ponto é do trecho da via (centroide do logradouro).") + " Para decisão, use a coordenada/polígono do lote (matrícula, cadastro imobiliário ou levantamento).")
    out = {"consulta": {"coordenada_utilizada": {"lat": lat, "lon": lon, "crs": "EPSG:4326"}, "endereco_informado": a.endereco,
                        "geocodificacao": geo, "data_consulta": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "dados_geo": "SIMGEO/PLANURB – baixados em 27/10/2026 (ver campo-grande-ms.json › geografico)"},
           **res, "alertas": alertas}
    if a.compacto:
        pz = (out.get("parametros_zona_efetivos_zeis2") or out.get("parametros_zona") or {}).get("parametros", {})
        v = lambda k: (pz.get(k) or {}).get("valor") if isinstance(pz.get(k), dict) else None
        out = {"coordenada": out["consulta"]["coordenada_utilizada"], "bairro": out["bairro"], "macrozona": (out["macrozona"] or {}).get("codigo"),
               "zona": out["zona_aplicavel"], "zona_ambiental": (out["zona_ambiental"] or {}).get("codigo"),
               "zeis": out["zeis"], "eixo_proximo": out["eixo_adensamento_proximo"], "zeia": out["zeia"],
               "ca_basico": v("ca_basico"), "ca_maximo": v("ca_maximo"), "taxa_ocupacao": v("taxa_ocupacao"),
               "permeabilidade": (out["zona_ambiental"] or {}).get("taxa_permeabilidade_minima"), "fid_oodc": out["oodc"]["fid"], "fid_oodc_alternativo_z4": out["oodc"].get("fid_alternativo_z4"),
               "limites_proximos": out["limites_a_menos_de_%dm" % a.raio_limite], "alertas": out["alertas"]}
    s = json.dumps(out, ensure_ascii=False, indent=2)
    if a.saida:
        open(a.saida, "w", encoding="utf-8").write(s)
    print(s)

if __name__ == "__main__":
    main()
