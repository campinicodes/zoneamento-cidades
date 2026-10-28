"""Gera testes/cidades/cidade-exemplo-xx/cidade-exemplo-xx.json – DADO FICTÍCIO DE EXEMPLO.
Cidade inventada, no oceano Atlântico (~10°S 33°O), só para provar que o motor é genérico.
Nenhum valor aqui é legislação real. NÃO copiar para ../cidades/."""
import json, os

X0, Y0 = -33.0, -10.0          # canto noroeste da "cidade"
F = "DADO FICTÍCIO DE EXEMPLO"
def box(x1, x2, y1, y2):
    return {"type": "Polygon", "coordinates": [[[X0 + x1, Y0 + y1], [X0 + x2, Y0 + y1], [X0 + x2, Y0 + y2], [X0 + x1, Y0 + y2], [X0 + x1, Y0 + y1]]]}
def fc(cod, *geoms, **props):
    return {"type": "FeatureCollection", "crs": "EPSG:4326", "fonte": F, "oficial": False,
            "features": [{"type": "Feature", "properties": {"codigo": cod, **props}, "geometry": g} for g in geoms]}
def P(v, art="art. 1º (fictício)", unidade=None, **k):
    """Parâmetro já no formato normalizado do schema 1.1."""
    forma = "sem_dado" if v is None else "lista" if isinstance(v, list) else "unico"
    return {"valor": v, "unidade": unidade, "fonte_id": "FX1", "artigo_anexo": art, "observacao": None, "forma": forma, **k}
def params(ca_b, ca_m, to, fx, perm=None):
    return {"ca_minimo": None, "ca_basico": P(ca_b, unidade="coeficiente"), "ca_maximo": P(ca_m, unidade="coeficiente"),
            "taxa_ocupacao": P(to, unidade="fracao"),
            "gabarito_altura_max_m": None, "gabarito_pavimentos": None,
            "taxa_permeabilidade": P(perm, unidade="fracao") if perm is not None else None,
            "recuos": {"frontal": P(5, unidade="m"), "lateral": None, "fundos": None},
            "lote_minimo_m2": P(200, unidade="m2"), "testada_minima_m": None,
            "usos_permitidos": P(["R1", "R2"], unidade="codigos_de_uso", observacao="usos fictícios"),
            "vagas": None, "densidade": None, "outros": {"fator_x": P(fx, "art. 9º (fictício)", unidade="coeficiente")}}
CAT = {"base": "mista_media_densidade", "sobreposta": "outra", "eixo": "eixo"}
def zona(cod, nome, tipo, prio, regra, par, geo):
    return {"codigo": cod, "nome": nome + " (FICTÍCIA)", "descricao": F, "tipo": tipo, "prioridade": prio,
            "categoria_normalizada": CAT[tipo], "categoria_criterio": F,
            "regra_sobreposicao": regra, "parametros": par, "observacoes": [F], "geometria": geo}
R = lambda **k: {"efeito": None, "usa_indices_de": None, "aplica_sobre": None, "limiar_pct": None, "requer_testada": False,
                 "distancia_max_m": None, "fundamento": "Lei fictícia 1/2000 (FX1)", "alerta": None, **k}

d = {
 "schema_versao": "1.1", "exemplo_ficticio": True,
 "aviso": "DADO FICTÍCIO DE EXEMPLO – cidade inexistente usada apenas nos testes automatizados da plataforma.",
 "municipio": "Cidade Exemplo (FICTÍCIA)", "uf": "XX", "slug": "cidade-exemplo-xx", "codigo_ibge": "0000000",
 "data_levantamento": "2026-10-27", "centro_mapa": {"lat": Y0 - 0.0, "lon": X0 + 0.02, "zoom": 14},
 "orgao_confirmacao": "Prefeitura FICTÍCIA (exemplo)",
 "marco_legal_vigente": "Lei fictícia 1/2000 – " + F,
 "fontes": [{"id": "FX1", "titulo": F, "lei": "Lei fictícia n. 1/2000", "data": "2000-01-01", "url": "https://example.org/lei-ficticia"}],
 "macrozonas": [{"codigo": "M1", "nome": "Macrozona fictícia", "descricao": F, "parametros": {}}],
 "zonas": [
  zona("ZB1", "Zona base 1", "base", 0, None, params(1.0, 2.0, 0.6, 1.0, 0.1), fc("ZB1", box(0, 0.02, -0.01, 0.01), bairro="Bairro Oeste")),
  zona("ZB2", "Zona base 2", "base", 0, None, params(0.5, 1.0, 0.5, 2.0, 0.1), fc("ZB2", box(0.02, 0.04, -0.01, 0.01), bairro="Bairro Leste")),
  zona("ZS-SUB", "Sobreposta que substitui", "sobreposta", 20, R(efeito="substitui", limiar_pct=50, alerta="Na porção sobreposta vale ZS-SUB."),
       params(3.0, 4.0, 0.8, 0.5), fc("ZS-SUB", box(0.005, 0.010, -0.005, 0.0), identificador="ZS-SUB 1")),
  zona("ZS-IDX", "Sobreposta que troca índices", "sobreposta", 5,
       R(efeito="usa_indices_de", usa_indices_de="ZB1", aplica_sobre=["ZB2"], limiar_pct=50, mantem_da_base=["outros.fator_x"],
         alerta="Sobre ZB2 valem os índices da ZB1 (fator_x mantido da ZB2)."),
       params(None, None, None, None), fc("ZS-IDX", box(0.025, 0.035, -0.005, 0.005), identificador="ZS-IDX A")),
  zona("ZS-ALERTA", "Sobreposta só de alerta", "sobreposta", 1, R(efeito="apenas_alerta", alerta="Área de atenção fictícia."),
       params(None, None, None, None), fc("ZS-ALERTA", box(0.001, 0.004, -0.009, -0.006))),
  zona("EX1", "Eixo fictício", "eixo", 10, R(efeito="substitui", requer_testada=True, distancia_max_m=40, alerta="Só com testada para a via."),
       params(2.0, 3.0, 0.7, 0.25), {**fc("EX1"), "features": [{"type": "Feature", "properties": {"codigo": "EX1", "nome": "Avenida fictícia"},
       "geometry": {"type": "LineString", "coordinates": [[X0, Y0 + 0.005], [X0 + 0.015, Y0 + 0.005]]}}]}),
 ],
 "camadas_complementares": {
  "perm": {"papel": "permeabilidade", "descricao": F, "fonte": F, "oficial": False, "fonte_id": "FX1", "artigo_anexo": "art. 5º (fictício)",
           "parametros_por_codigo": {"P1": {"taxa_permeabilidade": P(0.15, "art. 5º (fictício)", "fracao")}, "P2": {"taxa_permeabilidade": P(0.30, "art. 5º (fictício)", "fracao")}},
           "features": fc("P1", box(0, 0.02, -0.01, 0.01))["features"] + fc("P2", box(0.02, 0.04, -0.01, 0.01))["features"]},
  "macro": {"papel": "macrozona", "descricao": F, "fonte": F, "oficial": False,
            "parametros_por_codigo": {"M1": {"densidade_max_hab_ha": P(200, "art. 3º (fictício)", unidade="hab/ha")}},
            "features": fc("M1", box(0, 0.04, -0.01, 0.01))["features"]},
  "restr": {"papel": "restricao", "descricao": "Restrição fictícia", "fonte": F, "oficial": False, "parametros_por_codigo": None, "fonte_id": "FX1", "artigo_anexo": "art. 7º (fictício)",
            "alerta_por_codigo": {"R1": "R1 fictícia: área não edificável."}, "features": fc("R1", box(0.012, 0.014, -0.008, -0.006))["features"]},
  "info": {"papel": "informativa", "descricao": F, "fonte": F, "oficial": False, "parametros_por_codigo": None, "features": fc("I1", box(0, 0.04, -0.01, 0.01))["features"]},
 },
 **{b: {"resumo": F, "fonte_id": None, "artigo_anexo": None, "itens": []} for b in ("outorga_onerosa", "zeis_his", "outros_parametros")},
 "resumo_mcmv": [F],
 "geografico": {"descricao": F, "crs": "EPSG:4326", "servidor_oficial": None,
                "camadas": [{"nome": "zonas", "arquivo": "embutido", "fonte_url": "https://example.org", "data_download": "2026-10-27",
                             "oficial": False, "metodo": "inventado para teste", "erro_estimado_m": 0}],
                "regras_de_consulta": "Motor genérico (sem crs_area de propósito: a app calcula a UTM pelo centro).",
                "limitacoes": [F]},
 "lacunas": [{"item": "Gabarito", "motivo": "DADO FICTÍCIO: deixado null de propósito para testar a exibição de lacunas."}],
}
pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cidades", "cidade-exemplo-xx")
os.makedirs(pasta, exist_ok=True)
json.dump(d, open(os.path.join(pasta, "cidade-exemplo-xx.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(pasta, "REFERENCIAS.md"), "w", encoding="utf-8").write(
    "# Cidade Exemplo (FICTÍCIA) – DADO FICTÍCIO DE EXEMPLO\n\n> Nenhuma referência real. Esta pasta existe só para os testes da plataforma.\n\n"
    "| ID | Norma | Link |\n|---|---|---|\n| FX1 | Lei fictícia n. 1/2000 | https://example.org/lei-ficticia |\n")
print("ok", pasta)
