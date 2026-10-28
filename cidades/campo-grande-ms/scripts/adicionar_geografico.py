"""Adiciona/atualiza o bloco 'geografico' em campo-grande-ms.json (idempotente)."""
import json, os
B = "/workspace/legislacao"; G = B + "/geo/campo-grande"
J = json.load(open(B + "/campo-grande-ms.json", encoding="utf-8"))
log = json.load(open(G + "/raw/_log_download.json"))
S = "https://simgeoctm.campogrande.ms.gov.br/server/rest/services"
def u(svc, lid): return f"{S}/{svc}/MapServer/{lid}"
PD, LA, MA = "PLANO_DIRETOR_PPDUA/PLANO_DIRETOR__PDDUA", "LIMITES_ADMINISTRATIVOS", "MEIO_AMBIENTE"
def n(arq):
    return len(json.load(open(G + "/" + arq))["features"])
tema = [
 ("zonas", "zonas.geojson", [(PD,12,"Zonas urbanas (Z1–Z5) – Anexo 6"),(PD,6,"ZEIE – Anexo 13"),(PD,4,"Zona de Expansão Urbana – Anexo 3"),(LA,4,"Perímetro Distrito Anhanduí – Anexo 2.2")], "codigo = Z1..Z5, ZEIE (subcodigo ZEIE 1–7), ZEU, ANHANDUI → chave de 'zonas[].codigo'"),
 ("macrozonas", "macrozonas.geojson", [(PD,24,"Macrozonas urbanas MZ1–MZ3 – Anexo 5.2"),(PD,23,"Macrozoneamento do município – Anexo 5.1")], "codigo = MZ1..MZ3 → chave de 'macrozonas'; MZS/MZRA/MZRC/MZRGL/MZRRL (escala municipal)"),
 ("zonas_ambientais", "zonas_ambientais.geojson", [(PD,15,"Zonas Ambientais ZA1–ZA5 – Anexo 7")], "codigo = ZA1..ZA5; taxa_permeabilidade e tra_minima conferem com Anexo 7.1 do JSON"),
 ("zeis", "zeis.geojson", [(PD,13,"ZEIS 1 e 2 – Anexos 10.1 e 10.2")], "codigo = ZEIS1/ZEIS2 (sigla oficial 'ZEIS 1'/'ZEIS 2' sem espaço) → 'zonas[].codigo'; identificador = nº da mancha"),
 ("eixos_centralidades", "eixos_centralidades.geojson", [(PD,14,"Zonas de Centralidade – ZC (polígonos)"),(PD,3,"Eixos de Adensamento EA1–EA3 (LINHAS)")], "codigo = ZC, EA1, EA2, EA3 → 'zonas[].codigo'"),
 ("zeia", "zeia.geojson", [(PD,11,"ZEIA 1–5 – Anexo 15")], "codigo = ZEIA1..ZEIA5 (só ZEIA2 tem ficha em 'zonas'; demais: PDDUA arts. 37–43)"),
 ("zeic", "zeic.geojson", [(PD,10,"ZEIC Anexo 12.1"),(PD,9,"ZEIC Anexo 12.2"),(PD,8,"ZEIC Anexo 12.3"),(PD,7,"ZEIC Anexo 12.4")], "codigo = ZEIC; categoria = ZEIC n nnn"),
 ("zepa", "zepa.geojson", [(PD,5,"ZEPA – Proteção do Aeródromo")], "codigo = ZEPA"),
 ("zeiu", "zeiu.geojson", [(PD,29,"ZEIU")], "codigo = ZEIU"),
 ("ooaus_areas", "ooaus_areas.geojson", [(PD,22,"Outorga Onerosa de Alteração de Uso")], "codigo = OOAUS"),
 ("peuc", "peuc.geojson", [(PD,19,"PEUC – Anexo 21")], "codigo = PEUC"),
 ("iptu_progressivo", "iptu_progressivo.geojson", [(PD,25,"IPTU progressivo – Anexo 22")], "codigo = IPTU_PROG"),
 ("operacao_urbana_consorciada", "operacao_urbana_consorciada.geojson", [(PD,20,"OUC")], "codigo = OUC"),
 ("tdc_transferir", "tdc_transferir.geojson", [(PD,17,"TDC – áreas que transferem (Anexo 17.1)")], "codigo = TDC_CED"),
 ("tdc_receber", "tdc_receber.geojson", [(PD,18,"TDC – áreas receptoras (Anexo 17.2)")], "codigo = TDC_REC"),
 ("perimetro_urbano", "perimetro_urbano.geojson", [(LA,3,"Perímetro urbano da Sede – Anexo 2.1")], "codigo = PERIM"),
 ("bairros", "bairros.geojson", [(LA,7,"Bairros – Anexo 4.2")], "bairro, regiao_urb"),
 ("apa_lajeado", "apa_lajeado.geojson", [(MA,2,"APA do Lajeado")], "codigo = APA"),
 ("hidrografia", "hidrografia.geojson", [(MA,1,"Hidrografia (linhas)")], "referência para APP/ZEIA1"),
]
def data(svc, lid):
    for x in log:
        if x["servico"] == svc and x["layer_id"] == lid: return x["baixado_em"]
camadas = []
for nome, arq, srcs, cod in tema:
    camadas.append({"tema": nome, "arquivo": "geo/campo-grande/" + arq, "n_feicoes": n(arq), "status": "oficial",
                    "fonte_oficial": "SIMGEO – Prefeitura Municipal de Campo Grande / PLANURB (ArcGIS Server público, sem autenticação)",
                    "camadas_origem": [{"descricao": d, "servico": s, "layer_id": l, "url": u(s, l), "baixado_em": data(s, l)} for s, l, d in srcs],
                    "codigos": cod})
# verificação cruzada: índices nos atributos da camada oficial × JSON (Anexo 8.2)
Z = {z["codigo"]: z["parametros"] for z in J["zonas"]}
zg = json.load(open(G + "/zonas.geojson"))["features"] + json.load(open(G + "/eixos_centralidades.geojson"))["features"]
vc = {}
for f in zg:
    p = f["properties"]; c = p["codigo"]
    if c not in Z or "cabas" not in p: continue
    try:
        j = (Z[c]["ca_basico"]["valor"], Z[c]["ca_maximo"]["valor"])
        g = (float(p["cabas"]), float(p["camax"]))
        vc.setdefault(c, set()).add("confere" if (float(j[0]), float(j[1])) == g else f"DIVERGE camada={g} json={j}")
    except Exception as e:
        vc.setdefault(c, set()).add("não comparável")
J["geografico"] = {
  "descricao": "Camadas vetoriais OFICIAIS do zoneamento do PDDUA (LC 341/2018 consolidada) para consulta 'em que zona está o terreno'. Nenhum polígono foi digitalizado ou inventado: todas as geometrias vêm do SIMGEO/PLANURB.",
  "crs": "EPSG:4326 (WGS 84, lon/lat) – obtido com outSR=4326 no próprio servidor; distâncias calculadas em EPSG:31981 (SIRGAS 2000 / UTM 21S)",
  "data_download": "2026-10-27 (America/Sao_Paulo, UTC-3)",
  "servidor_oficial": {"diretorio_servicos": S, "servico_pddua": u(PD, "").rstrip("/"), "visualizador_publico": "https://simgeoctm.campogrande.ms.gov.br/portal/apps/webappviewer/index.html?id=cc13c124c8414dc7b61d016be3629366",
                       "sisgran_mapas": "https://sisgranmaps.campogrande.ms.gov.br/", "mapas_pdf_lei": "F04 (LC 341/2018 – republicação dos mapas/anexos)"},
  "digitalizacao": "Autorizada pelo usuário para temas sem vetor oficial, marcando como 'aproximada (digitalização de mapa oficial)'. NÃO foi necessária: todos os temas pedidos (zonas, macrozonas, zonas ambientais, ZEIS, eixos/centralidades, ZEIA) e os complementares existem como vetor oficial no SIMGEO. Nenhuma camada é aproximada.",
  "camadas": camadas,
  "camadas_brutas": {"pasta": "geo/campo-grande/raw/", "log": "geo/campo-grande/raw/_log_download.json", "scripts": ["geo/campo-grande/baixar_camadas.py", "geo/campo-grande/montar_camadas.py"]},
  "regras_de_consulta": {
    "precedencia_zona": "ZEIE > ZC > (Eixo de Adensamento, se o lote for lindeiro) > Z1–Z5 do bairro; fora do perímetro urbano: ZEU ou ANHANDUI; fora destes: macrozona rural (sem índices urbanos). Base: Decreto 15.123/2022 arts. 4º, 6º, 7º e 11 (F09) e PDDUA Anexo 8.2 (F01).",
    "zeis2_sobre_z5": "Aplicam-se os índices da Z4 (LC 516/2023 art. 8º, alterando LC 421/2021 – F07).",
    "eixos": "Eixos (EA1–EA3) são LINHAS no SIMGEO: o script alerta se o ponto está a ≤ 50 m do eixo (parâmetro --raio-eixo) e mostra os índices do EA como alternativa; a aplicação depende da testada do lote para a via.",
    "permeabilidade": "Vem da Zona Ambiental (ZA1–ZA5) do ponto (PDDUA art. 25 e Anexo 7.1).",
    "alerta_divisa": "Se o ponto estiver a < 30 m (parâmetro --raio-limite) de outra zona/macrozona/ZA/ZEIS/ZEIA, emite alerta de divisa."
  },
  "como_consultar": {
    "script": "python3 consulta_zona_cg.py --lat -20.4581 --lon -54.6182   |   python3 consulta_zona_cg.py --endereco \"Rua 14 de Julho, 2000, Centro, Campo Grande, MS\"   (opções: --compacto, --saida arquivo.json, --raio-limite 30, --raio-eixo 50)",
    "dependencias": "python3, shapely>=2, pyproj (pip install --user shapely pyproj)",
    "geocodificacao": "Nominatim/OpenStreetMap (https://nominatim.openstreetmap.org, © colaboradores OSM, ODbL) com User-Agent identificável, 1 req/s, cache local e viewbox da Sede – resultado APROXIMADO.",
    "mapa": "geo/campo-grande/mapa.html (Leaflet; clique para consultar; geometrias simplificadas ~1,5 m só para exibição)",
    "imagem": "geo/campo-grande/visao_geral_zoneamento.png",
    "testes": ["geo/campo-grande/teste1_centro_14julho.json", "geo/campo-grande/teste2_zeis2_taruma.json", "geo/campo-grande/teste3_z5_nova_campo_grande.json", "geo/campo-grande/teste_extra_eixo_EA1.json", "geo/campo-grande/teste_extra_divisa_Z4_Z2.json"]
  },
  "verificacao_cruzada_indices": {"descricao": "CA básico/máximo nos atributos das camadas oficiais × valores do Anexo 8.2 no JSON", "resultado": {k: sorted(v) for k, v in sorted(vc.items())}},
  "limitacoes": [
    "As camadas SIMGEO são a base cartográfica oficial da Prefeitura, mas o instrumento legal é o texto e os mapas anexos da LC 341/2018 consolidada; em divergência, prevalece a lei e a manifestação da PLANURB (GDU).",
    "Consulta por PONTO: não há cadastro de lotes público aqui; terrenos que cruzam limites ou têm testada para eixo exigem análise do polígono do lote.",
    "Zonas urbanas Z1–Z5 seguem o limite de BAIRRO (Anexo 6); ZEIS/ZEIA/ZEIC são manchas sobrepostas.",
    "Geocodificação Nominatim é aproximada (frequentemente nível de logradouro, sem número).",
    "A camada 'Macrozoneamento do município' (id 23) tem sobreposição MZRA × MZS; dentro da Sede o script usa MZS.",
    "3 feições ZEIA1 da camada oficial têm auto-interseção; o script aplica make_valid (correção topológica, sem mover vértices).",
    "Pasta AMHASF do servidor exige token (HTTP 499 'Token Required') – não acessada, por regra (sem contornar bloqueios). Lotes/loteamentos HIS ali não foram usados.",
    "Atualização: camadas baixadas em 27/10/2026; leis posteriores que alterem anexos (ex.: novas ZEIS) só aparecem após nova execução de baixar_camadas.py.",
  ],
}
fl = J["fontes"]
if not any(f["id"] == "F32" for f in fl):
    fl.append({"id": "F32", "titulo": "SIMGEO – Serviço ArcGIS REST do Plano Diretor (PDDUA): zonas, macrozonas, ZA, ZEIS, ZEIA, ZEIC, ZC, EA, ZEIE, ZEU, instrumentos",
               "lei": "Base cartográfica oficial dos anexos da LC 341/2018 (PLANURB/PMCG)", "data": "consultado em 2026-10-27", "url": u(PD, "").rstrip("/")})
json.dump(J, open(B + "/campo-grande-ms.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps(J["geografico"]["verificacao_cruzada_indices"], ensure_ascii=False))
