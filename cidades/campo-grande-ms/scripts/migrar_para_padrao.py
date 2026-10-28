"""Migra o JSON de Campo Grande (v. app_zoneamento) para o padrão da plataforma multicidades (PADRAO_JSON.md; gera 1.0 e chama normalizar_schema_cg.py → 1.1).
Entrada : /workspace/legislacao/campo-grande-ms.json  (parâmetros + citações + geometrias)
          /workspace/legislacao/geo/campo-grande/*.geojson  (camadas oficiais SIMGEO p/ restrições)
Saída   : ../campo-grande-ms.json
Nada é inventado: só reorganiza chaves e traduz as regras de consulta já documentadas em geografico.regras_de_consulta."""
import copy, json, os
import shapely
from shapely.geometry import shape, mapping

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = "/workspace/legislacao/campo-grande-ms.json"
GEO = "/workspace/legislacao/geo/campo-grande"
SAIDA = os.path.join(AQUI, "..", "campo-grande-ms.json")
SIMPL = 0.00002   # ~2 m

src = json.load(open(ORIG, encoding="utf-8"))
out = {"schema_versao": "1.0", "municipio": src["municipio"], "uf": src["uf"], "slug": "campo-grande-ms",
       "codigo_ibge": "5002704", "data_levantamento": src["data_levantamento"],
       "centro_mapa": {"lat": -20.4697, "lon": -54.6201, "zoom": 13},
       "orgao_confirmacao": "PLANURB/SEMADUR – Guia de Diretrizes Urbanísticas (GDU)",
       "marco_legal_vigente": src["marco_legal_vigente"], "fontes": src["fontes"]}
FONTES = {f["id"] for f in src["fontes"]}

def corrige(geom_json, poligonal=True):
    """make_valid + precisão de 6 casas; para polígonos mantém só as partes poligonais."""
    g = shapely.set_precision(shapely.make_valid(shape(geom_json)), 0.000001)
    if poligonal and g.geom_type == "GeometryCollection":
        partes = [p for p in g.geoms if "Polygon" in p.geom_type]
        g = shapely.union_all(partes) if partes else g
    return mapping(g)

def geom_fc(feats, fonte, oficial=True):
    fs = []
    for f in feats:
        g = shapely.make_valid(shape(f["geometry"])).simplify(SIMPL, preserve_topology=True)
        g = shapely.set_precision(g, 0.000001)
        if g.is_empty:
            continue
        fs.append({"type": "Feature", "properties": f["properties"], "geometry": mapping(g)})
    return {"type": "FeatureCollection", "crs": "EPSG:4326 (lon, lat)", "fonte": fonte, "oficial": oficial, "features": fs}

# ---------------- regras (traduz geografico.regras_de_consulta) ----------------
R = lambda **k: {"efeito": None, "usa_indices_de": None, "aplica_sobre": None, "limiar_pct": None,
                 "requer_testada": False, "distancia_max_m": None, "fundamento": None, "alerta": None, **k}
REGRAS = {
 "ZEIE": ("sobreposta", 30, R(efeito="substitui", limiar_pct=50, fundamento="Decreto 15.123/2022 art. 6º (F09); PDDUA Anexo 8.2 (F01)",
          alerta="Parte do terreno em ZEIE: na porção sobreposta valem os índices próprios da ZEIE.")),
 "ZC":   ("sobreposta", 20, R(efeito="substitui", limiar_pct=50, fundamento="Decreto 15.123/2022 art. 4º (F09); PDDUA Anexo 8.2 (F01)",
          alerta="Parte do terreno em Zona de Centralidade: na porção sobreposta valem os índices da ZC.")),
 "ZEIS2": ("sobreposta", 5, R(efeito="usa_indices_de", usa_indices_de="Z4", aplica_sobre=["Z5"], limiar_pct=50,
          mantem_da_base=["outros.fator_oodc_fid"],  # a tabela de Fid da LC 469/2022 é por zona; não há regra que troque o Fid
          fundamento="LC 516/2023 art. 8º, alterando LC 421/2021 (F07); PDDUA art. 29 II e Anexo 10.2 (F01)",
          alerta="ZEIS 2 (HIS): sobre Z5 valem os índices da Z4. Fid da OODC (Z5 = 2,0 ou Z4 = 0,5) não definido pela LC 469/2022; HIS pode ser isenta (art. 8º II, redação ambígua) – confirmar com a PLANURB.")),
 "ZEIS1": ("sobreposta", 5, R(efeito="apenas_alerta", fundamento="PDDUA art. 29 I e Anexo 10.1 (F01)",
          alerta="ZEIS 1 (regularização fundiária): parâmetros dependem de plano de urbanização/regularização.")),
 "ZEIA2": ("sobreposta", 1, R(efeito="apenas_alerta", fundamento="PDDUA arts. 37–43 e Anexo 15 (F01)",
          alerta="ZEIA 2: supressão máxima de 40% da vegetação (art. 40); índices da zona subjacente.")),
}
for ea in ("EA1", "EA2", "EA3"):
    REGRAS[ea] = ("eixo", 10, R(efeito="substitui", requer_testada=True, distancia_max_m=50,
                  fundamento="Decreto 15.123/2022 art. 7º (F09); PDDUA Anexo 8.2 e Anexo 14 (F01)",
                  alerta="Eixos são LINHAS no SIMGEO: os índices do eixo só valem se o lote tiver testada para a via; caso contrário vale a zona base."))
fid = src["outorga_onerosa"]["fator_fid_por_zona"]

# ---------------- zonas ----------------
zonas = []
for z in src["zonas"]:
    z = copy.deepcopy(z)
    tipo, prio, regra = REGRAS.get(z["codigo"], ("base", 0, None))
    p = z["parametros"]
    outros = p.pop("outros", {}) or {}
    for k in ("indice_elevacao", "potencial_adicional_oodc_tdc"):
        if k in p:
            outros[k] = p.pop(k)
    if "gabarito_altura_max" in p:
        p["gabarito_altura_max_m"] = p.pop("gabarito_altura_max")
    p.setdefault("gabarito_pavimentos", {"valor": None, "fonte_id": "F01", "artigo_anexo": "Anexo 8.2",
                 "observacao": "O PDDUA não fixa nº de pavimentos; verticalização controlada pelo índice de elevação (ver outros.indice_elevacao) e pelo CA."})
    p.setdefault("ca_minimo", None)
    p.setdefault("densidade", {"valor": None, "fonte_id": "F01", "artigo_anexo": "art. 20",
                 "observacao": "Densidade líquida máxima definida pela MACROZONA (MZ1 330, MZ2 240, MZ3 120 hab/ha) – ver camadas_complementares.macrozonas."})
    if z["codigo"] in fid["valor"]:
        outros["fator_oodc_fid"] = {"valor": fid["valor"][z["codigo"]], "fonte_id": fid["fonte_id"], "artigo_anexo": fid["artigo_anexo"],
                                    "observacao": "Fator Fid da fórmula da outorga onerosa VO = ((Ac − Ap)/At) × (Fid × Vt)."}
    p["outros"] = outros
    geo = z.pop("geometria")
    zonas.append({"codigo": z["codigo"], "nome": z["nome"], "descricao": z.get("descricao"), "tipo": tipo, "prioridade": prio,
                  "regra_sobreposicao": regra, "parametros": p, "observacoes": z.get("observacoes"),
                  "geometria": {"type": "FeatureCollection", "crs": "EPSG:4326 (lon, lat)", "fonte": geo.get("fonte"), "oficial": True,
                                "features": [f2 for f2 in ({**f, "geometry": corrige(f["geometry"], tipo != "eixo")} for f in geo["features"])
                                             if tipo == "eixo" or ("Polygon" in f2["geometry"]["type"] and not shape(f2["geometry"]).is_empty)],
                                "observacao_geometria": "Feições degeneradas da base oficial (lascas < 1 m², ex.: ZEIS 2 82/91/95) removidas na migração; demais passaram por make_valid."}})
out["zonas"] = zonas

# ---------------- macrozonas (descritivo, lista) ----------------
mz = src["macrozonas"]
out["macrozonas"] = [{"codigo": k, **v} for k, v in mz.items() if isinstance(v, dict)]
if "observacao" in mz:
    out["macrozonas_observacao"] = mz["observacao"]

# ---------------- camadas complementares ----------------
cc = src["camadas_complementares"]
za_par = {}
for f in cc["zonas_ambientais"]["features"]:
    p = f["properties"]
    za_par[p["codigo"]] = {
        "taxa_permeabilidade": {"valor": p["taxa_permeabilidade"], "unidade": "fração da área do lote", "fonte_id": "F01",
                                "artigo_anexo": "PDDUA art. 25 e Anexo 7.1"},
        "tra_minima": {"valor": p["tra_minima"], "fonte_id": "F01", "artigo_anexo": "Anexo 7.1 (Taxa de Relevância Ambiental)",
                       "observacao": f"IA = V^{p.get('fator_alfa')} × D^{p.get('fator_beta')} (Lei 6.914/2022 – F18)"}}
camadas = {
 "zonas_ambientais": {"papel": "permeabilidade", "descricao": "Zonas Ambientais ZA1–ZA5: definem taxa de permeabilidade e TRA mínima (prevalece sobre a coluna da zona).",
                      "fonte": cc["zonas_ambientais"].get("obs"), "oficial": True, "parametros_por_codigo": za_par,
                      "features": cc["zonas_ambientais"]["features"]},
 "macrozonas": {"papel": "macrozona", "descricao": "Macrozonas urbanas MZ1–MZ3 (densidade e diretrizes de adensamento).",
                "fonte": cc["macrozonas"].get("obs"), "oficial": True,
                "parametros_por_codigo": {k: {"densidade_liquida_max_hab_ha": {"valor": v["densidade_liquida_max_hab_ha"], "unidade": "hab/ha",
                                              "fonte_id": v["fonte_id"], "artigo_anexo": v["artigo_anexo"]},
                                              "diretriz": {"valor": v["diretriz"], "fonte_id": v["fonte_id"], "artigo_anexo": v["artigo_anexo"]}}
                                          for k, v in mz.items() if isinstance(v, dict)},
                "features": [f for f in cc["macrozonas"]["features"] if f["properties"]["codigo"] in ("MZ1", "MZ2", "MZ3")]},
 "macrozoneamento_municipal": {"papel": "informativa", "descricao": "Macrozoneamento do município (Sede e macrozonas rurais) – Anexo 5.1.",
                "fonte": cc["macrozonas"].get("obs"), "oficial": True, "parametros_por_codigo": None,
                "observacao": "Contornos simplificados a ~10 m (camada só informativa).",
                "features": [{**f, "geometry": mapping(shapely.set_precision(shape(f["geometry"]).simplify(0.0001, preserve_topology=True), 0.000001))}
                             for f in cc["macrozonas"]["features"] if f["properties"]["codigo"] not in ("MZ1", "MZ2", "MZ3")]},
}
def gj(nome): return json.load(open(f"{GEO}/{nome}.geojson", encoding="utf-8"))["features"]
def limpa(feats, campos, codigo_fn=None):
    res = []
    for f in feats:
        p = {k: f["properties"].get(k) for k in campos if f["properties"].get(k) is not None}
        p["codigo"] = codigo_fn(f["properties"]) if codigo_fn else f["properties"]["codigo"]
        res.append({"type": "Feature", "properties": p, "geometry": f["geometry"]})
    return geom_fc(res, "")["features"]
fonte_simgeo = "SIMGEO/PLANURB – Prefeitura de Campo Grande (camada oficial), baixado em 2026-10-27; contornos simplificados ~2 m"
camadas["zeia_restricoes"] = {"papel": "restricao", "descricao": "ZEIA 1 (APP), 3, 4 e 5 – Anexo 15 do PDDUA. (ZEIA 2 está em zonas[].)",
    "fonte": fonte_simgeo, "oficial": True, "parametros_por_codigo": None,
    "alerta_por_codigo": {"ZEIA1": "ZEIA 1 = Área de Preservação Permanente – não edificável (PDDUA arts. 37–38; Código Florestal).",
                          "ZEIA3": "ZEIA 3 – potencial construtivo só transferível por TDC (PDDUA arts. 37–43).",
                          "ZEIA4": "ZEIA 4 – sujeita a OODC/TDC/direito de preempção (PDDUA arts. 37–43).",
                          "ZEIA5": "ZEIA 5 – ver PDDUA arts. 37–43 e Anexo 15."},
    "fonte_id": "F01", "artigo_anexo": "PDDUA arts. 37–43 e Anexo 15",
    "features": limpa([f for f in gj("zeia") if f["properties"]["codigo"] != "ZEIA2"], ["identificador", "nome"])}
camadas["zeic"] = {"papel": "restricao", "descricao": "ZEIC – Zonas Especiais de Interesse Cultural (patrimônio; Anexos 12.1–12.4).",
    "fonte": fonte_simgeo, "oficial": True, "parametros_por_codigo": None, "fonte_id": "F01", "artigo_anexo": "PDDUA Anexo 12",
    "alerta_por_codigo": {"ZEIC": "ZEIC (interesse cultural): análise especial de patrimônio histórico (PDDUA Anexo 12)."},
    "features": limpa(gj("zeic"), ["nome", "categoria", "zona", "bairro"])}
camadas["zepa"] = {"papel": "restricao", "descricao": "ZEPA – Zona Especial de Proteção do Aeródromo (Anexo 9).",
    "fonte": fonte_simgeo, "oficial": True, "parametros_por_codigo": None, "fonte_id": "F01", "artigo_anexo": "PDDUA Anexo 9",
    "alerta_por_codigo": {"ZEPA": "ZEPA: limites de altura dos planos aeronáuticos (COMAER/DECEA) – consultar antes de definir gabarito."},
    "features": limpa(gj("zepa"), ["zona"])}
camadas["apa_lajeado"] = {"papel": "restricao", "descricao": "APA do Lajeado (camada MEIO_AMBIENTE do SIMGEO).",
    "fonte": fonte_simgeo, "oficial": True, "parametros_por_codigo": None, "fonte_id": "F32", "artigo_anexo": "SIMGEO MEIO_AMBIENTE/MapServer/2",
    "alerta_por_codigo": {"APA": "APA do Lajeado: observar plano de manejo/licenciamento ambiental."},
    "features": limpa(gj("apa_lajeado"), ["nome"], lambda p: "APA")}
camadas["peuc_iptu_progressivo"] = {"papel": "informativa", "descricao": "Áreas de aplicação de PEUC / IPTU progressivo no tempo (Anexos 21–22).",
    "fonte": fonte_simgeo, "oficial": True, "parametros_por_codigo": None, "fonte_id": "F01", "artigo_anexo": "PDDUA Anexos 21–22",
    "features": limpa(gj("iptu_progressivo"), ["bairro", "zona"], lambda p: "IPTU_PROG")}
out["camadas_complementares"] = camadas

for k in ("outorga_onerosa", "zeis_his", "outros_parametros", "resumo_mcmv"):
    out[k] = src[k]

# ---------------- geografico ----------------
g = copy.deepcopy(src["geografico"])
g["crs"] = "EPSG:4326"
g["crs_area"] = "EPSG:31981"
g["raio_divisa_m"] = 30
g["camadas_detalhe"] = g.pop("camadas")
g["camadas"] = [{"nome": c["tema"], "campo": "zonas[].geometria" if c["tema"] in ("zonas", "zeis", "eixos_centralidades", "zeia") else
                 f"camadas_complementares.{c['tema']}", "fonte_url": c["camadas_origem"][0]["url"],
                 "data_download": (c["camadas_origem"][0]["baixado_em"] or "")[:10], "oficial": True, "metodo": "vetor oficial", "erro_estimado_m": 2}
                for c in g["camadas_detalhe"]]
g["regras_de_consulta_texto"] = g.pop("regras_de_consulta")
g["regras_de_consulta"] = ("Precedência genérica: maior 'prioridade' entre as zonas sobrepostas com efeito 'substitui' que cubram ≥ limiar_pct do terreno "
                          "e eixos a ≤ distancia_max_m (com testada); senão a zona base de maior área. 'usa_indices_de' troca os índices da base "
                          "indicada em aplica_sobre. Em Campo Grande: ZEIE(30) > ZC(20) > EA(10, testada) > Z1–Z5/ZEU/Anhanduí(0); ZEIS2 sobre Z5 → Z4 (≥ 50%). "
                          "Permeabilidade pela Zona Ambiental. Detalhe em regras_de_consulta_texto.")
g["limitacoes"] = g["limitacoes"] + ["Geometrias simplificadas (~2 m) no JSON para reduzir tamanho."]
out["geografico"] = g

# ---------------- lacunas no formato {item, motivo} ----------------
lac = []
for t in src["lacunas"]:
    if isinstance(t, dict):
        lac.append(t); continue
    import re as _re
    corte = None
    for m in _re.finditer(r":\s| – | — |;\s", t):            # 1º separador forte fora de parênteses
        if 3 <= m.start() <= 110 and t[:m.start()].count("(") == t[:m.start()].count(")"):
            corte = m; break
    if corte:
        lac.append({"item": t[:corte.start()].strip(), "motivo": t[corte.end():].strip()})
    else:   # sem separador: item = começo da frase cortado em palavra inteira; motivo = texto integral
        curto = t if len(t) <= 90 else t[:90].rsplit(" ", 1)[0] + "…"
        lac.append({"item": curto, "motivo": t if curto != t else ""})
out["lacunas"] = lac

json.dump(out, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("ok", os.path.getsize(SAIDA) // 1024, "KB")

# Etapa 2: normalização para o schema (schema/cidade.schema.json, versão 1.1)
import subprocess, sys
subprocess.run([sys.executable, os.path.join(AQUI, "normalizar_schema_cg.py")], check=True)
