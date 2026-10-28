# Salvador-BA – Referências do levantamento (27/10/2026)

## Leis e normas (fontes do JSON)
| id | norma | link |
|---|---|---|
| F01 | Lei 9.148/2016 – LOUOS (texto, 08/09/2016) | https://pddu.salvador.ba.gov.br/img/arquivos/louos/LOUOS-2016.pdf |
| F02 | Lei 9.069/2016 – PDDU (texto + Quadros do Anexo 2) | https://pddu.salvador.ba.gov.br/img/arquivos/pddu/LEI-n.-9.069-PDDU-2016.pdf |
| F03 | LOUOS – Quadros do Anexo 01 (01 a 12; link do Quadro 06 como referência; demais em fontes/) | https://pddu.salvador.ba.gov.br/img/arquivos/louos/Quadro-06-Par%C3%A2metros-de-Ocupa%C3%A7%C3%A3o-do-Solo.pdf |
| F04 | LOUOS – Mapa 01A Zonas de Uso (com LC 074/2020, Leis 9.509 e 9.510/2020, ATAs CNLU 04 e 12/2022) | https://pddu.salvador.ba.gov.br/img/arquivos/louos/LOUOS_MAPA_01A_ZONAS-DE-USO_MODIFICADO_CNLU_ESALVADOR_compressed.pdf |
| F05 | LOUOS – Mapa 03 Gabarito na ABM | https://pddu.salvador.ba.gov.br/img/arquivos/louos/SSA_LOUOS_03_GABARITO-ABM.compressed.pdf |
| F06 | LOUOS – Mapa 01B ZEIS (ATA 12/2022) | https://pddu.salvador.ba.gov.br/img/arquivos/louos/SSA_LOUOS_01B_ZEIS_MODIFICADO_PROCESSO_ATA_N_12_2022_CNLU_compressed.pdf |
| F07 | PDDU – Mapas (macrozoneamento etc.) | https://pddu.salvador.ba.gov.br/img/arquivos/pddu/PDDU_MAPA_01_MACROZONEAMENTO.pdf |
| F08 | Portal oficial PDDU/LOUOS (índice dos arquivos) | https://pddu.salvador.ba.gov.br/louos-2016 |
| F09 | GeoSalvador – ArcGIS REST público (Mapa_LOUOS_WFL1, PDDU_2016, bens_tombados_a, idesh_risco_a) | https://geo.salvador.ba.gov.br/arcgis/rest/services |

As URLs exatas de cada camada (com a data de download) estão em `geo_raw/_log_download.json` e em `geografico.camadas` no JSON.

## Geometrias
- **Zoneamento (34 zonas base + 2 eixos ZCLMe/ZCLMu): oficial:false.** O vetor oficial `LOUOS_2016_OK` exige token e não foi usado. A geometria foi extraída dos vetores do PDF oficial do Mapa 01A (`extrair_pdf_mapa01a.py`), particionada pela ordem de desenho e georreferenciada por transformação afim (`georref_mapa01a.py`). Foram usados 234 pontos de controle: centroides das ZEIS do PDF × ZEIS oficiais. O resíduo mediano é 0,09 m (RMS 5,1 m) e o IoU mediano das ZEIS é 0,999. O erro estimado é de cerca de 5 m.
  - O tipo das ZEIS (1–5) vem do vetor oficial, pela maior sobreposição.
  - ZCMe-1/01…2/CA e ZCMu-1/2 são identificadas pela centralidade oficial mais próxima.
  - As ZUE são identificadas pelo índice e pela localização.
  - Juntas, as zonas cobrem cerca de 99,7% da área dos bairros oficiais.
- **Gabarito da ABM: oficial:false**, com erro de 10–15 m. Foi vetorizado do raster do Mapa 03 por classificação de cor (`vetorizar_mapa03_abm.py`). O detalhe do Centro Antigo/Barra não foi feito.
- **Entorno de 200 m de bens tombados: oficial:false.** É um buffer calculado sobre o vetor oficial.
- **Demais camadas: vetor oficial público do GeoSalvador.** São macrozonas, macroáreas, ZEIS, limite da ABM, APRN, APCP, UC, parques, Mata Atlântica, bens tombados, risco geológico, OUC, centralidades e bairros.

## Reprodução
```
cd cidades/salvador-ba
python3 scripts/baixar_camadas.py        # geo_raw/*.geojson + _log_download.json
python3 scripts/extrair_pdf_mapa01a.py   # geo_raw/mapa01a_pdf_coords.json
python3 scripts/georref_mapa01a.py       # geo_raw/georref_mapa01a.json
python3 scripts/vetorizar_mapa03_abm.py  # geo_raw/mapa03_abm_gabarito.geojson
python3 scripts/build_salvador.py        # salvador-ba.json
python3 ../../schema/normalizar_cidade.py salvador-ba.json --compacto
python3 ../../validar_cidade.py salvador-ba
```

## Avisos
- O portal sedur.salvador.ba.gov.br/leis bloqueia acesso automatizado (WAF). O bloqueio não foi contornado. Por isso, os textos da LC 074/2020, das Leis 9.509/2020, 9.510/2020 e 9.774/2023, da Lei 7.719/2009 e da Lei 9.562/2021 não foram lidos. Os parâmetros vêm do texto original da LOUOS/PDDU de 2016 e dos quadros publicados no portal PDDU. **Confirme na SEDUR (consulta prévia) antes de usar para decisão.**
- O CA mínimo da ZPR-1 diverge entre as leis: 0,10 na LOUOS (Quadro 06) e 0,20 no PDDU (Quadro 01). Foi adotado o valor da LOUOS.
