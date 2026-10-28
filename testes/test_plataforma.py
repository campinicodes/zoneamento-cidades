"""Testes da plataforma (sem pytest obrigatório: `python3 test_plataforma.py`; também roda com pytest).

1. Campo Grande: os 3 casos da fase anterior (centro Z1, Tarumã ZEIS2/Z5→Z4, KMZ EA1) devem dar o mesmo resultado.
2. KMZ com VÁRIOS polígonos (2 em Campo Grande + 1 na cidade fictícia) → um resultado por polígono, cidade detectada em cada.
3. Cidade FICTÍCIA (testes/cidades/cidade-exemplo-xx – DADO FICTÍCIO DE EXEMPLO): cada efeito do padrão
   (substitui, usa_indices_de + mantem_da_base, apenas_alerta, eixo com testada, permeabilidade, macrozona,
   restricao, divisa, múltiplas bases, fora da cidade) – prova que o motor não tem regra por cidade.
4. Validador: aprova CG e a fictícia; reprova uma cópia quebrada.
5. JSON Schema (schema/cidade.schema.json): CG e fictícia passam 100%; valor solto/legado é reprovado;
   o normalizador genérico leva um JSON legado (1.0) a 1.1 válido sem inventar valores.
"""
import copy, io, json, os, sys, tempfile, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(AQUI)
os.environ["PLATAFORMA_CIDADES"] = os.pathsep.join([os.path.join(PLAT, "cidades"), os.path.join(AQUI, "cidades")])
sys.path.insert(0, os.path.join(PLAT, "app")); sys.path.insert(0, PLAT)
import app as A                                  # noqa: E402
from validar_cidade import validar, validar_schema   # noqa: E402
sys.path.insert(0, os.path.join(PLAT, "schema"))
from normalizar_cidade import normalizar          # noqa: E402

C = A.app.test_client()
EX = os.path.join(AQUI, "exemplos")
X0, Y0 = -33.0, -10.0


def box(x1, x2, y1, y2, base=(0, 0)):
    bx, by = base
    return {"type": "Polygon", "coordinates": [[[bx + x1, by + y1], [bx + x2, by + y1], [bx + x2, by + y2], [bx + x1, by + y2], [bx + x1, by + y1]]]}


def consulta(geo, cidade=None):
    r = C.post("/api/consulta", json={"geojson": geo, "cidade": cidade})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["resultados"]


def val(p, *cam):
    for k in cam:
        p = p[k]
    return p["valor"] if isinstance(p, dict) else p


def tipos(r):
    return [a["tipo"] for a in r["alertas"]]


# ---------------------------------------------------------------- Campo Grande
def test_cg_centro_z1():
    r = consulta(json.load(open(os.path.join(EX, "poligono_centro_z1.geojson"))))[0]
    R, P = r["resultado"], r["parametros"]["parametros"]
    assert r["cidade"]["slug"] == "campo-grande-ms"
    assert abs(r["terreno"]["area_m2"] - 1849.6) < 0.5
    assert (R["zona_aplicavel"], R["zona_dos_indices"], R["macrozona_predominante"], R["permeabilidade_codigo"]) == ("Z1", "Z1", "MZ1", "ZA1")
    assert (val(P, "ca_basico"), val(P, "ca_maximo"), val(P, "taxa_permeabilidade"), val(P, "outros", "fator_oodc_fid")) == (4, 5, 0.2, 0.1)
    assert r["sobreposicoes"]["zonas_base"][0]["pct_terreno"] == 100.0
    return r


def test_cg_taruma_zeis2():
    r = consulta(json.load(open(os.path.join(EX, "poligono_taruma_zeis2_z5.geojson"))))[0]
    R, P = r["resultado"], r["parametros"]["parametros"]
    assert abs(r["terreno"]["area_m2"] - 29112.9) < 0.5
    assert (R["zona_aplicavel"], R["zona_dos_indices"], R["zona_base_efetiva"]) == ("Z5", "Z4", "Z4")
    assert (val(P, "ca_basico"), val(P, "ca_maximo"), val(P, "taxa_permeabilidade")) == (2, 3, 0.3)
    assert val(P, "outros", "fator_oodc_fid") == 2.0 and "Mantido da base Z5" in P["outros"]["fator_oodc_fid"]["observacao"]
    z = r["sobreposicoes"]["sobrepostas"][0]
    det = {d["rotulo"]: d["pct_terreno"] for d in z["detalhes"]}
    assert z["codigo"] == "ZEIS2" and det == {"ZEIS 2 192": 48.55, "ZEIS 2 191": 8.3}
    assert 56 < z["pct_terreno"] <= 56.85          # união das 2 ZEIS (sobrepõem-se ~0,3% na base oficial)
    ea3 = next(e for e in r["sobreposicoes"]["eixos"] if e["codigo"] == "EA3")
    assert ea3["distancia_m"] == 230.2
    assert any("Fid da OODC" in a["texto"] for a in r["alertas"])
    return r


def test_cg_kmz_ea1():
    with open(os.path.join(EX, "gleba_teste.kmz"), "rb") as f:
        res = C.post("/api/consulta-kmz", data={"arquivo": (f, "gleba_teste.kmz")}).get_json()
    r = res["resultados"][0]
    R, P = r["resultado"], r["parametros"]["parametros"]
    assert abs(r["terreno"]["area_m2"] - 39301.4) < 0.5
    assert R["zona_aplicavel"] == "EA1" and R["requer_testada"] and r["sobreposicoes"]["eixos"][0]["toca"]
    base = {x["codigo"]: round(x["pct_terreno"]) for x in r["sobreposicoes"]["zonas_base"]}
    mz = {x["codigo"]: round(x["pct_terreno"]) for x in r["camadas_complementares"]["macrozonas"]["sobreposicoes"]}
    assert base == {"Z5": 90, "Z4": 10} and mz == {"MZ3": 90, "MZ2": 10}, (base, mz)
    assert (val(P, "ca_basico"), val(P, "ca_maximo"), val(P, "outros", "fator_oodc_fid")) == (2.8, 3.3, 0.25)
    assert r["parametros_zona_base"]["codigo"] == "Z5" and "testada" in tipos(r)
    return r


def test_kmz_varios_poligonos_varias_cidades():
    pls = [("Centro CG", box(-54.6162, -54.6158, -20.4622, -20.4618)),
           ("Tarumã CG", box(-54.6811, -54.6793, -20.5450, -20.5436)),
           ("Fictícia ZB1", box(0.001, 0.002, -0.004, -0.003, (X0, Y0)))]
    pm = "".join(f"<Placemark><name>{n}</name><Polygon><outerBoundaryIs><LinearRing><coordinates>"
                 + " ".join(f"{x},{y},0" for x, y in g["coordinates"][0]) + "</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>" for n, g in pls)
    kml = f'<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>{pm}</Document></kml>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("doc.kml", kml)
    os.makedirs(EX, exist_ok=True)
    open(os.path.join(EX, "tres_poligonos_duas_cidades.kmz"), "wb").write(buf.getvalue())
    buf.seek(0)
    res = C.post("/api/consulta-arquivo", data={"arquivo": (buf, "tres.kmz")}).get_json()
    got = [(x["nome"], x["cidade"]["slug"], x["resultado"]["zona_aplicavel"], x["resultado"]["zona_dos_indices"]) for x in res["resultados"]]
    assert got == [("Centro CG", "campo-grande-ms", "Z1", "Z1"), ("Tarumã CG", "campo-grande-ms", "Z5", "Z4"),
                   ("Fictícia ZB1", "cidade-exemplo-xx", "ZB1", "ZB1")], got
    return res


# ---------------------------------------------------------------- cidade fictícia
def F(x1, x2, y1, y2):
    return consulta(box(x1, x2, y1, y2, (X0, Y0)))[0]


def test_ficticia_base_simples_e_utm_calculada():
    r = F(0.001, 0.002, -0.004, -0.003)
    assert r["cidade"]["slug"] == "cidade-exemplo-xx" and r["resultado"]["zona_aplicavel"] == "ZB1"
    assert r["terreno"]["crs_area"].startswith("EPSG:31985")          # sem crs_area → UTM 25S pelo centro
    assert 12000 < r["terreno"]["area_m2"] < 12400                    # ~110 m × 110 m
    P = r["parametros"]["parametros"]
    assert val(P, "taxa_permeabilidade") == 0.15 and "perm" in P["taxa_permeabilidade"]["origem"]   # papel permeabilidade
    assert r["macrozona"]["codigo_predominante"] == "M1" and val(r["macrozona"]["parametros"], "densidade_max_hab_ha") == 200
    assert P["gabarito_altura_max_m"] is None and "ficticio" in tipos(r)
    assert r["camadas_complementares"]["info"]["sobreposicoes"][0]["codigo"] == "I1"


def test_ficticia_substitui():
    r = F(0.006, 0.007, -0.004, -0.003)
    assert r["resultado"]["zona_aplicavel"] == "ZS-SUB" and val(r["parametros"]["parametros"], "ca_basico") == 3.0


def test_ficticia_substitui_abaixo_do_limiar():
    r = F(0.0097, 0.0107, -0.004, -0.003)                    # só ~30% dentro da ZS-SUB (limiar 50%)
    assert r["resultado"]["zona_aplicavel"] == "ZB1" and any("abaixo do limiar" in a["texto"] for a in r["alertas"])


def test_ficticia_usa_indices_de_com_mantem_da_base():
    r = F(0.028, 0.029, -0.002, -0.001)
    R, P = r["resultado"], r["parametros"]["parametros"]
    assert (R["zona_aplicavel"], R["zona_dos_indices"]) == ("ZB2", "ZB1")
    assert val(P, "ca_basico") == 1.0 and val(P, "outros", "fator_x") == 2.0       # fator_x mantido da ZB2
    assert val(P, "taxa_permeabilidade") == 0.30                                     # permeabilidade da camada (P2)


def test_ficticia_eixo_requer_testada():
    r = F(0.001, 0.002, 0.0042, 0.0048)                       # ~22 m do eixo
    assert r["resultado"]["zona_aplicavel"] == "EX1" and r["resultado"]["requer_testada"]
    assert r["parametros_zona_base"]["codigo"] == "ZB1" and "testada" in tipos(r)


def test_ficticia_apenas_alerta_e_restricao():
    r = F(0.002, 0.003, -0.008, -0.007)
    assert r["resultado"]["zona_aplicavel"] == "ZB1" and any("ZS-ALERTA" in a["texto"] for a in r["alertas"])
    r = F(0.0125, 0.0135, -0.0075, -0.0065)
    assert any(a["tipo"] == "restricao" and "não edificável" in a["texto"] for a in r["alertas"])


def test_ficticia_divisa_e_multiplas_bases():
    r = F(0.0194, 0.0198, 0.006, 0.007)                       # ~22 m da ZB2 (raio padrão 30 m)
    assert any(a["tipo"] == "divisa" and "ZB2" in a["texto"] for a in r["alertas"]), r["alertas"]
    r = F(0.0195, 0.0205, 0.006, 0.007)
    assert {x["codigo"] for x in r["sobreposicoes"]["zonas_base"]} == {"ZB1", "ZB2"}
    assert any("mais de uma zona base" in a["texto"] for a in r["alertas"])


def test_fora_das_cidades_e_cidade_forcada():
    r = consulta(box(10, 10.001, 10, 10.001))[0]
    assert "fora das cidades" in r["erro"]
    r = consulta(box(0.001, 0.002, -0.004, -0.003, (X0, Y0)), cidade="campo-grande-ms")[0]
    assert r["resultado"]["zona_aplicavel"] is None                       # forçada a CG, sem zona


# ---------------------------------------------------------------- validador e rotas
def test_validador():
    assert validar(os.path.join(PLAT, "cidades", "campo-grande-ms", "campo-grande-ms.json"))["ok"]
    cam = os.path.join(AQUI, "cidades", "cidade-exemplo-xx", "cidade-exemplo-xx.json")
    assert validar(cam)["ok"]
    d = json.load(open(cam))
    d["zonas"][0]["parametros"]["ca_basico"]["fonte_id"] = "FX9"
    d["zonas"][1]["geometria"]["features"] = []
    anel = d["zonas"][2]["geometria"]["features"][0]["geometry"]["coordinates"][0]
    anel[1], anel[2] = anel[2], anel[1]                                   # anel em "gravata-borboleta" (auto-interseção)
    del d["centro_mapa"]
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "quebrada.json"); json.dump(d, open(p, "w"))
        res = validar(p)
    txt = " | ".join(res["erros"])
    assert not res["ok"] and "FX9" in txt and "ZB2: sem feições" in txt and "inválida" in txt and "centro_mapa" in txt, txt


def test_schema_e_normalizador():
    cg = json.load(open(os.path.join(PLAT, "cidades", "campo-grande-ms", "campo-grande-ms.json")))
    fic = json.load(open(os.path.join(AQUI, "cidades", "cidade-exemplo-xx", "cidade-exemplo-xx.json")))
    assert validar_schema(cg) == [] and validar_schema(fic) == []
    ruim = copy.deepcopy(fic)                                   # string solta onde o schema exige número estruturado
    ruim["zonas"][0]["parametros"]["ca_maximo"] = {"valor": "2 ou 3", "fonte_id": "FX1", "artigo_anexo": "x", "observacao": None,
                                                    "unidade": "coeficiente", "forma": "unico"}
    ruim["zonas"][0]["chave_inventada"] = 1
    txt = " | ".join(validar_schema(ruim))
    assert "ca_maximo" in txt and "chave_inventada" in txt, txt
    leg = copy.deepcopy(fic)                                    # formato legado 1.0 (como cidades geradas antes do schema)
    leg["schema_versao"] = "1.0"
    z = leg["zonas"][0]
    P = z["parametros"]
    P["ca_basico"] = {"valor": "1,5", "fonte_id": "FX1", "artigo_anexo": "art. 1º"}
    P["taxa_ocupacao"] = {"valor": "60%", "fonte_id": "FX1", "artigo_anexo": "art. 1º"}
    P["recuos"]["frontal"] = {"valor": "Livre", "fonte_id": "FX1", "artigo_anexo": "art. 2º"}
    P["testada_minima_m"] = {"valor": {"meio_de_quadra": 10, "esquina": 15}, "fonte_id": "FX1", "artigo_anexo": "art. 3º"}
    P["usos_permitidos"] = {"valor": {"residencial": ["R1", "R2"], "comercial": ["C1"]}, "fonte_id": "FX1", "artigo_anexo": "art. 4º"}
    z["observacoes"] = "uma observação"
    leg["resumo_mcmv"] = "texto corrido"
    leg["outorga_onerosa"] = {"base_legal": {"fonte_id": "FX1", "artigo_anexo": "art. 8º"},
                              "formula": {"valor": "VO = A x B", "fonte_id": "FX1", "artigo_anexo": "art. 8º"}}
    leg["macrozonas"] = [{"codigo": "M1", "densidade_hab_ha": 200, "diretriz": "fictícia", "fonte_id": "FX1", "artigo_anexo": "art. 3º"}]
    leg["lacunas"] = ["Gabarito não encontrado"]
    assert len(validar_schema(leg)) >= 8
    n = normalizar(copy.deepcopy(leg))
    assert validar_schema(n) == [], validar_schema(n)
    Q = n["zonas"][0]["parametros"]
    assert (Q["ca_basico"]["valor"], Q["ca_basico"]["texto_original"], Q["taxa_ocupacao"]["valor"]) == (1.5, "1,5", 0.6)
    assert Q["recuos"]["frontal"]["forma"] == "livre" and Q["testada_minima_m"]["forma"] == "condicional"
    assert [c["valor"] for c in Q["testada_minima_m"]["condicionais"]] == [10, 15]
    assert Q["usos_permitidos"]["valor"] == ["R1", "R2", "C1"]
    assert n["outorga_onerosa"]["fonte_id"] == "FX1" and n["outorga_onerosa"]["itens"][0]["forma"] == "formula"
    assert n["resumo_mcmv"] == ["texto corrido"] and n["lacunas"][0] == {"item": "Gabarito não encontrado", "motivo": ""}
    assert normalizar(copy.deepcopy(n)) == n                    # idempotente


def test_herda_da_base():
    """forma 'herda_da_base' numa sobreposta que substitui → o motor usa o parâmetro da base (genérico, sem regra por cidade)."""
    import shutil
    import motor
    from shapely.geometry import box as sbox
    with tempfile.TemporaryDirectory() as t:
        dst = os.path.join(t, "cidade-exemplo-xx")
        shutil.copytree(os.path.join(AQUI, "cidades", "cidade-exemplo-xx"), dst)
        p = os.path.join(dst, "cidade-exemplo-xx.json"); d = json.load(open(p))
        z = [z for z in d["zonas"] if z["codigo"] == "ZS-SUB"][0]
        H = lambda u: {"valor": None, "unidade": u, "fonte_id": "FX1", "artigo_anexo": "x", "observacao": None, "forma": "herda_da_base"}
        z["parametros"]["lote_minimo_m2"], z["parametros"]["recuos"]["frontal"] = H("m2"), H("m")
        json.dump(d, open(p, "w"))
        assert validar_schema(d) == []
        cid = list(motor.Registro([t]).cidades.values())[0]
        r = motor.analisar(cid, sbox(X0 + 0.006, Y0 - 0.004, X0 + 0.009, Y0 - 0.001))
    P = r["parametros"]["parametros"]
    assert r["resultado"]["zona_aplicavel"] == "ZS-SUB" and val(P, "ca_basico") == 3.0
    assert val(P, "lote_minimo_m2") == 200 and "herdado da base ZB1" in P["lote_minimo_m2"]["origem"]
    assert val(P, "recuos", "frontal") == 5 and P["recuos"]["frontal"]["origem"]


def test_rotas():
    cs = C.get("/api/cidades").get_json()
    assert {"campo-grande-ms", "cidade-exemplo-xx"} <= {c["slug"] for c in cs["cidades"]}
    h = C.get("/referencias/campo-grande-ms").get_data(as_text=True)
    assert "Lacunas declaradas" in h and "LC516-2023.pdf" in h and "<table>" in h
    assert C.get("/api/zonas/cidade-exemplo-xx").get_json()["features"]
    assert C.get("/").status_code == 200 and C.get("/referencias/nao-existe").status_code == 404


if __name__ == "__main__":
    falhas = 0
    for nome, fn in [(k, v) for k, v in dict(globals()).items() if k.startswith("test_")]:
        try:
            fn(); print("OK   ", nome)
        except AssertionError as e:
            falhas += 1; print("FALHA", nome, e)
    print(f"\n{falhas} falha(s)")
    sys.exit(1 if falhas else 0)
