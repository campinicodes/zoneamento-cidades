# Referências legais – Goiânia/GO (`goiania-go`)

Levantamento: 2026-10-27 · IBGE 5208707 · schema 1.1 · gerado por `scripts/gerar_referencias.py`.

> Só fontes oficiais e públicas (SILEG – legislação compilada da Prefeitura de Goiânia, goiania.go.gov.br; Portal Mapa Goiânia/SEPLANH – ArcGIS REST público). Valores sem fonte = `null` e listados em *Lacunas*. Confirme sempre na SEPLANH – Secretaria Municipal de Planejamento Urbano e Habitação (Uso do Solo / Consulta Prévia) antes de decisão de compra.

## Marco legal vigente em 27/10/2026

Vigente em 27/10/2026: Plano Diretor LC 349/2022 (texto compilado SILEG, com LC 363/2023, 371/2024, 373/2024 e 379/2024); Código de Obras LC 364/2023; Parcelamento LC 363/2023; OODC LC 373/2024; HIS LC 379/2024; AEIS Lei 11.083/2023; EIV Lei 11.127/2024; TDC Lei 10.848/2022 (suspensa para novas concessões pelos Dec. 2.785/2025 e 82/2026); atividades Lei 10.845/2022; PUB Dec. 117/2026.

## Como ler os parâmetros

- Zonas base = unidades territoriais do Modelo Espacial (LC 349/2022 Anexo XIV): AA, ADD, AAB (resíduo da Macrozona Construída), AOS, APAC (ABT e entornos AEBT agrupados pelas linhas do Anexo XXII), ARAU (APP, Jardim Botânico, UUS) e as 7 Macrozonas Rurais; sobrepostas: AEIS III (HIS) e APA.
- IA (CA máximo): art. 196 (AA 6, ADD 5); CA básico = 1 (área não onerosa, arts. 242–244). TO, altura e densidade: arts. 190–196; recuos: Anexo XXI (altura × afastamento) e Anexo XXII (APAC); vagas: LC 364/2023 arts. 110–111; HIS: LC 379/2024 arts. 14–16 (em `parametros.condicionais` com código HIS).
- TDC suspensa para novas concessões (Dec. 2.785/2025 + Dec. 82/2026): o IA 7,5 da AA com TDC aparece como condicional, não como valor corrente.

## Fontes

| ID | Norma | Data | Título | Arquivo local | Link oficial |
|---|---|---|---|---|---|
| F01 | Lei Complementar Municipal nº 349/2022 | 2022-03-04 | Plano Diretor de Goiânia – texto compilado no SILEG (com as alterações das LC 363/2023, 371/2024, 373/2024 e 379/2024) | fontes/lc349.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2022/lc_20220304_000000349.html) |
| F02 | LC nº 349/2022, Anexos XXI e XXII (PDF original; Anexo XXI com redação da LC 371/2024 conferida no texto compilado) | 2022-03-04 | Plano Diretor – Anexos XXI (Tabela de Parâmetros Urbanísticos – afastamentos × altura) e XXII (Área de Entorno do Bem Tombado) | fontes/anexos/lc349_ane_21.pdf | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2022/lc_20220304_000000349_ane_000000021.pdf) |
| F03 | Lei Complementar Municipal nº 371/2024 | 2024-01-04 | Ocupação dos vazios urbanos – PDU I a IV, Conjuntos Residenciais (altera a LC 349/2022) | fontes/atos/lc_20240104_000000371.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2024/lc_20240104_000000371.html) |
| F04 | Lei Complementar Municipal nº 373/2024 | 2024-01-19 | Outorga Onerosa do Direito de Construir – OODC (fórmula VOO = Vm × Vi × Qsc) | fontes/atos/lc_20240119_000000373.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2024/lc_20240119_000000373.html) |
| F05 | Lei Complementar Municipal nº 379/2024 | 2024-06-12 | Parâmetros urbanísticos e edilícios para Habitação de Interesse Social – HIS (regulamenta o art. 288 da LC 349/2022; partes vetadas promulgadas em 12/02/2025) | fontes/atos/lc_20240612_000000379.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2024/lc_20240612_000000379.html) |
| F06 | Lei Municipal nº 11.083/2023 | 2023-11-06 | Áreas de Programas Especiais de Interesse Social – AEIS I, II e III | fontes/atos/lo_20231106_000011083.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2023/lo_20231106_000011083.html) |
| F07 | Lei Complementar Municipal nº 364/2023 (com alterações da LC 379/2024) | 2023-01-13 | Código de Obras e Edificações (vagas: arts. 110–112) | fontes/atos/lc_20230113_000000364.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2023/lc_20230113_000000364.html) |
| F08 | Lei Municipal nº 11.127/2024 | 2024-01-04 | Estudo de Impacto de Vizinhança – EIV/RIV | fontes/atos/lo_20240104_000011127.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2024/lo_20240104_000011127.html) |
| F09 | Lei Municipal nº 10.848/2022 (art. 14 com redação da LC 373/2024) | 2022-11-11 | Transferência do Direito de Construir – TDC | fontes/atos/lo_20221111_000010848.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2022/lo_20221111_000010848.html) |
| F10 | Decreto Municipal nº 2.785/2025 | 2025-06-11 | Suspensão da concessão de novas TDC por 18 meses a partir de 01/01/2025 e regras de CPC/CPC-S (até 50% da OODC; até 25% da altura no receptor) | fontes/atos/dc_20250611_000002785.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2025/dc_20250611_000002785.html) |
| F11 | Decreto Municipal nº 82/2026 | 2026-07-03 | Prorroga por mais 18 meses (efeitos a partir de 01/07/2026) a suspensão da TDC do Dec. 2.785/2025 | fontes/atos/dc_20260703_000000082.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2026/dc_20260703_000000082.html) |
| F12 | Lei Municipal nº 10.845/2022 | 2022-11-04 | Controle das atividades econômicas (graus de incomodidade × hierarquia viária) | fontes/atos/lo_20221104_000010845.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2022/lo_20221104_000010845.html) |
| F13 | Prefeitura de Goiânia – serviço ArcGIS REST público | 2026-10-27 | Portal Mapa Goiânia (SEPLANH) – "Simplifica Goiânia – Uso do Solo", camada 3 Unidades Territoriais (Modelo Espacial – Anexo XIV) | — | [link](https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_Simplifica_Goiania_UsoDoSolo/FeatureServer/3) |
| F14 | Prefeitura de Goiânia – serviço ArcGIS REST público | 2026-10-27 | Portal Mapa Goiânia – Mapa_ModeloEspacial (Plano Diretor 2022: APAC, ARAU, AEIS, programas especiais, macrozoneamento, OOAU, IVE, corredores, restrições aeroportuária e militar) | — | [link](https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer) |
| F15 | Lei Complementar Municipal nº 363/2023 | 2023-01-12 | Código de Parcelamento do Solo | fontes/atos/lc_20230112_000000363.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2023/lc_20230112_000000363.html) |
| F16 | Decreto Municipal nº 117/2026 | 2026-08-06 | Regulamenta o Plano Urbanístico Básico – PUB (projeto global ≥ 50 ha) | fontes/atos/dc_20260806_000000117.html | [link](https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/2026/dc_20260806_000000117.html) |

## Artigos/anexos citados por fonte (nº de parâmetros que citam)

- **F01** (Lei Complementar Municipal nº 349/2022): LC 349/2022 arts. 197 a 208 (art. 197 par. único incl. LC 371/2024) (84); LC 349/2022 art. 192 (25); LC 349/2022 art. 180 e Anexo XXI (red. LC 371/2024); arts. 182 e 183 (14); LC 349/2022 arts. 242 a 244 (13); LC 349/2022 arts. 162 e 163; Lei 10.845/2022 (13); LC 349/2022 arts. 142, 143 e 202 (13); LC 349/2022 arts. 149 e 163 (13); LC 349/2022 art. 120; Lei 11.083/2023 arts. 8º e 24 (9); LC 349/2022 art. 120; Lei 11.083/2023 (9); LC 349/2022 art. 131 (8); LC 349/2022 art. 179 III (7); LC 349/2022 arts. 201 a 208 (7); LC 349/2022 arts. 188, 196 e 244 §1º II (6); LC 349/2022 art. 244 §1º II (6); LC 349/2022 art. 187 (4) … (+45)
- **F02** (LC nº 349/2022, Anexos XXI e XXII (PDF original; Anexo XXI com redação da LC 371/2024 conferida no texto compilado)): LC 349/2022 arts. 181, 188 e Anexo XXII (17); LC 349/2022 art. 180 e Anexo XXI (red. LC 371/2024); arts. 180 §3º e 183 §§9º–11 (7); LC 349/2022 Anexo XXII (6); LC 349/2022 arts. 181, 188 e Anexo XXII (notas 3–34) (2); LC 349/2022 arts. 181, 188 e Anexo XXII (nota 26) (1)
- **F03** (Lei Complementar Municipal nº 371/2024): LC 371/2024 art. 17 e demais; LC 349/2022 arts. 159 e 174 (1)
- **F04** (Lei Complementar Municipal nº 373/2024): LC 373/2024 art. 4º §2º (14); LC 349/2022 arts. 241 a 250; LC 373/2024 (1); LC 373/2024 art. 4º (1); LC 373/2024 art. 4º §2º I (1); art. 4º §2º II (1); art. 4º §2º III (1); art. 4º §2º IV (1); art. 4º §3º I (1); art. 4º §3º II (1); art. 4º §3º III (1); LC 373/2024 Anexo – Grupo I (1); LC 373/2024 art. 4º §§4º–5º e Anexo (1); LC 373/2024 arts. 1º, 5º, 6º e 8º (1)
- **F05** (Lei Complementar Municipal nº 379/2024): LC 379/2024 art. 16 (4); LC 379/2024 art. 14 §1º IV e §2º; Lei 11.083/2023 arts. 22 a 34 (2); LC 379/2024 arts. 10 e 11 (2); LC 379/2024 art. 20 (2); LC 349/2022 art. 179 (AA não listada); LC 379/2024 art. 14 (1); LC 349/2022 art. 179 (ADD não listada); LC 379/2024 art. 14 (1); LC 379/2024 art. 14 §1º IV e §2º; Lei 11.083/2023 arts. 22 a 34; Lei 11.083/2023 art. 10 (1); LC 379/2024; Lei 11.083/2023; LC 349/2022 arts. 211–212 (1); LC 379/2024 art. 14 (1); LC 379/2024 art. 14 §§1º–2º (1)
- **F06** (Lei Municipal nº 11.083/2023): Lei 11.083/2023 arts. 8º §3º e 24 (1); Lei 11.083/2023 art. 24 (1); Lei 11.083/2023 art. 31 (1); Lei 11.083/2023 art. 34 (1); Lei 11.083/2023 arts. 8º e 10 (1); Lei 11.083/2023 arts. 24, 31 e 34; LC 379/2024 art. 24 (1)
- **F07** (Lei Complementar Municipal nº 364/2023 (com alterações da LC 379/2024)): LC 364/2023 arts. 110 a 112; LC 379/2024 arts. 16 e 29 (13); LC 364/2023 arts. 110 e 111 (1)
- **F08** (Lei Municipal nº 11.127/2024): Lei 11.127/2024 arts. 5º a 7º; LC 349/2022 art. 262 (1)
- **F09** (Lei Municipal nº 10.848/2022 (art. 14 com redação da LC 373/2024)): Lei 10.848/2022 art. 14 (1)
- **F10** (Decreto Municipal nº 2.785/2025): Dec. 2.785/2025 arts. 2º e 4º; Dec. 82/2026 art. 1º (1)
- **F14** (Prefeitura de Goiânia – serviço ArcGIS REST público): LC 349/2022 art. 131 e Anexo XIV (1); Planos de zona de proteção de aeródromo (COMAER/DECEA – Portaria 957/GC3); camada municipal de referência (1); Decreto-Lei federal 3.437/1941 arts. 1º e 2º (1)
- **F16** (Decreto Municipal nº 117/2026): Dec. 117/2026 arts. 1º a 5º; LC 363/2023 arts. 135–146 (1)

## Zonas (habitação coletiva)

| Código | Nome | Categoria | CA básico | CA máximo | TO | Altura (m) | Densidade | Feições |
|---|---|---|---|---|---|---|---|---|
| AA | Área Adensável (AA) | mista_alta_densidade | 1 | Geral (qualquer uso): 6 / Com recepção de TDC (até +25% da altura – art. 252): 7,5 / Faixa de 350 m da Av. Fued José Sebba (LC 379/2024 art. 34): 6 | Até 11 m de altura: 1 / Pavimento de estacionamento/instalações entre 11 e 14,5 m: 1 / Acima de 11 m de altura: 0,5 | livre | livre | 2 |
| ADD | Área de Desaceleração de Densidade (ADD) | mista_alta_densidade | 1 | 5 | Até 11 m de altura: 1 / Pavimento de estacionamento/instalações entre 11 e 14,5 m: 1 / Acima de 11 m de altura: 0,5 | livre | livre | 1 |
| AAB | Área de Adensamento Básico (AAB) | residencial_media_densidade | 1 | Geral (sem IA fixado): nao_aplicavel / HIS (LC 379/2024): 2 | 1,0 | Geral: 12 / Setores Jaó e Sul: 7,5 | Geral – 1 UH / 90 m² de terreno: 111,11 / Quitinete – 1 UH / 30 m²: 333,33 / HIS em vazio Grupo I (Anexo XXIII) ou Grupo III (Lei 9.123) – 1 UH / 30 m²: 333,33 / HIS nos demais casos – 1 UH / 45 m²: 222,22 / Chácara/sítio de recreio em via < 13 m: texto | 1 |
| AOS | Área de Ocupação Sustentável (AOS) | residencial_baixa_densidade | 1 | nao_aplicavel | 0,4 | Geral: 12 / Setores Jaó e Sul: 7,5 | 55,56 | 1 |
| ARAU-UUS | ARAU – Unidade de Uso Sustentável (UUS) | ambiental | 1 | nao_aplicavel | 0,4 | Geral: 12 / Setores Jaó e Sul: 7,5 | 55,56 | 1 |
| ARAU-APP | ARAU – Área de Preservação Permanente (APP) | ambiental | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| ARAU-JB | ARAU – Jardim Botânico | ambiental | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| APAC-ABT | APAC – Área do Bem Tombado (ABT) | patrimonio_cultural | sem_dado | sem_dado | sem_dado | sem_dado | 111,11 | 62 |
| APAC-AEBT-A | APAC – Entorno de Bem Tombado (7,5 m; recuo frontal 5 m) | patrimonio_cultural | 1 | nao_aplicavel | sem_dado | Geral: 7,5 / Entorno do Grande Hotel: 11 / Entorno do Cine Teatro Goiânia: 21,5 / Lotes 3/30/28, 26, 17/24, 19, 21, 23/25/5 e 57 da quadra 67 do Setor Central: 4 | 111,11 | 6 |
| APAC-AEBT-B | APAC – Entorno de Bem Tombado (11 m; frontal 5 m; lateral/fundo 2 m acima de 7,5 m) | patrimonio_cultural | 1 | nao_aplicavel | sem_dado | 11 | 111,11 | 6 |
| APAC-AEBT-C | APAC – Entorno de Bem Tombado (7,5 m; ocupação no alinhamento frontal e laterais) | patrimonio_cultural | 1 | nao_aplicavel | sem_dado | 7,5 | 111,11 | 1 |
| APAC-AEBT-SUB | APAC – Entorno da Subestação Goiânia (11 m; frontal 5 m) | patrimonio_cultural | 1 | nao_aplicavel | sem_dado | 11 | 111,11 | 1 |
| APAC-AEBT-BB | APAC – Entorno da Estátua de Bartolomeu Bueno (altura do Anexo XXI; alinhamento) | patrimonio_cultural | 1 | nao_aplicavel | sem_dado | altura do Anexo XXI | 111,11 | 1 |
| APAC-AEBT-ND | APAC – Entorno de Bem Tombado sem linha no Anexo XXII | patrimonio_cultural | 1 | nao_aplicavel | sem_dado | sem_dado | 111,11 | 3 |
| MR-MRA | Macrozona Rural do Alto Anicuns | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| MR-MRB | Macrozona Rural do Barreiro | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| MR-MRD | Macrozona Rural do Dourados | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| MR-MRL | Macrozona Rural do Lajeado | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| MR-MRC | Macrozona Rural do Capivara | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| MR-MRJ | Macrozona Rural do João Leite | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| MR-MRS | Macrozona Rural do São Domingos | rural | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | nao_aplicavel | 1 |
| AEIS-III | Área Especial de Interesse Social III (AEIS III) | especial_interesse_social | 1 | HIS em AEIS: 2 / Sobre AA/ADD: herda_da_base | 1,0 | HIS em AEIS – tabela de alturas da AA (Anexo XXI): livre / Sobre AOS/APA: 12 | HIS em AEIS – 1 UH / 30 m²: 333,33 / Sobre AOS ou APA – 1 UH / 180 m²: 55,56 / AEIS I/II (Reurb-S) – 1 UH / 90 m² (30 m² quitinete): 111,11 | 6 |
| ARAU-APA | ARAU – Área de Proteção Ambiental (APA) | ambiental | 1 | nao_aplicavel | 0,4 | Geral: 12 / Setores Jaó e Sul: 7,5 | 55,56 | 4 |

## Resumo MCMV

- Maior potencial: AEIS III (gravame HIS) – IA 2, 1 UH/30 m² (≈ 333 uh/ha), altura pela tabela da AA, 1 vaga/3 UH, isenções de OODC e ITBI; 115 polígonos no Modelo Espacial (decretos até 2026).
- AA (Eixos de Desenvolvimento ~350 m dos corredores): IA 6, sem altura máxima e sem controle de densidade; HIS com vaga facultada em corredor exclusivo; OODC mais barata (Vi 0,10) e HIS isenta – mas terra cara e TDC suspensa até 2027 (sem IA 7,5).
- AAB (maior parte da cidade): para HIS IA 2, altura 12 m (≈ 4 pavimentos), TO 100%, 1 UH/45 m² (30 m² em vazios do Grupo I/III) – bom para condomínios de 4 pavimentos sem elevador.
- Vazios urbanos via PDU (LC 371/2024): PDU I IA 6 (7,5 c/ TDC) e frações de 30–60 m² nos PDU II/III – exige projeto diferenciado.
- Evitar: AOS e APA (1 UH/180 m², TO 40%, 12 m; APA só com Plano de Manejo), APAC (AEBT 7,5–11 m; ABT pelo órgão de tombamento), APP/Jardim Botânico, Setores Sul e Jaó (7,5 m) e as Macrozonas Rurais (só chácaras; conversão por OOAU).
- Vagas: fora da HIS, 1 vaga/100 m² de área privativa (coletiva) – em HIS 1 vaga/3 UH (LC 379/2024 art. 16).

## Camadas geográficas

Servidor oficial: https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/ · CRS de área: EPSG:31982

| Camada | Arquivo bruto | Oficial | Método | Feições | Download | URL |
|---|---|---|---|---|---|---|
| Unidades territoriais – Simplifica Goiânia Uso do Solo (zonas base) | `geo_raw/ut_simplifica.geojson` | sim | vetor oficial | 2988 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_Simplifica_Goiania_UsoDoSolo/FeatureServer/3 |
| Macrozoneamento (Macrozona Construída, 7 rurais e OOAU) | `geo_raw/me_macrozoneamento.geojson` | sim | vetor oficial | 40 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/33 |
| Áreas de Patrimônio Cultural – APAC (ABT e AEBT) | `geo_raw/me_bem_tombado_apac.geojson` | sim | vetor oficial | 103 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/28 |
| Jardim Botânico | `geo_raw/me_arau_jardim_botanico.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/27 |
| AEIS III (Programas Especiais de Interesse Social) | `geo_raw/me_aeis.geojson` | sim | vetor oficial | 115 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/7 |
| OOAU (Anexo XI) | `geo_raw/me_ooau.geojson` | sim | vetor oficial | 27 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/32 |
| IVE (Anexo XVI) | `geo_raw/me_ive.geojson` | sim | vetor oficial | 22 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/5 |
| Corredores (linhas) | `geo_raw/me_corredores.geojson` | sim | vetor oficial | 36 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/1 |
| Eixos de Desenvolvimento (linhas) | `geo_raw/me_eixo_desenvolvimento.geojson` | sim | vetor oficial | 12 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/4 |
| Declividade > 30% (linhas) | `geo_raw/me_declividade30.geojson` | sim | vetor oficial | 15 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/2 |
| Restrição aeroportuária – AERO_APROXIMACAO | `geo_raw/me_aero_aproximacao.geojson` | sim | vetor oficial | 2 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/38 |
| Restrição aeroportuária – AERO_RUIDO | `geo_raw/me_aero_ruido.geojson` | sim | vetor oficial | 5 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/39 |
| Restrição aeroportuária – AERO_SEGURANCA | `geo_raw/me_aero_seguranca.geojson` | sim | vetor oficial | 2 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/40 |
| Restrição militar | `geo_raw/me_restricao_militar.geojson` | sim | vetor oficial | 3 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/44 |
| Programas Especiais – PE_URBANISTICO | `geo_raw/me_pe_urbanistico.geojson` | sim | vetor oficial | 3 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/8 |
| Programas Especiais – PE_AMBIENTAL | `geo_raw/me_pe_ambiental.geojson` | sim | vetor oficial | 12 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/9 |
| Programas Especiais – PE_ECONOMICO | `geo_raw/me_pe_economico.geojson` | sim | vetor oficial | 10 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/10 |
| AEDE | `geo_raw/me_aede.geojson` | sim | vetor oficial | 9 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/12 |
| ARAR – APP rural | `geo_raw/me_arar_app.geojson` | sim | vetor oficial | 103 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/14 |
| me_limite_municipio (baixada para conferência, não usada) | `geo_raw/me_limite_municipio.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/34 |
| me_arau_app (baixada para conferência, não usada) | `geo_raw/me_arau_app.geojson` | sim | vetor oficial | 609 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/21 |
| me_arar_uus (baixada para conferência, não usada) | `geo_raw/me_arar_uus.geojson` | sim | vetor oficial | 109 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial/MapServer/18 |
| med_bem_tombado (baixada para conferência, não usada) | `geo_raw/med_bem_tombado.geojson` | sim | vetor oficial | 54 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial_Desenvolvimento/MapServer/45 |
| med_entorno_bem_tombado (baixada para conferência, não usada) | `geo_raw/med_entorno_bem_tombado.geojson` | sim | vetor oficial | 14 | 2026-10-27 | https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/Mapa_ModeloEspacial_Desenvolvimento/MapServer/46 |

### Camadas complementares no JSON

- **macrozoneamento** (papel `macrozona`, 13 feições; F14 LC 349/2022 art. 131 e Anexo XIV): Macrozona Construída (urbana) e as sete Macrozonas Rurais (LC 349/2022 arts. 130–131 e Anexo XIV).
- **ooau** (papel `informativa`, 27 feições; F01 LC 349/2022 arts. 249 e 250; Anexo XI): Áreas rurais passíveis de Outorga Onerosa de Alteração de Uso (rural → urbano) – Anexo XI.
- **ive** (papel `informativa`, 21 feições; F01 LC 349/2022 art. 189; Anexo XVI; Lei 10.845/2022): Áreas de Influência das Vias Expressas (IVE) – Anexo XVI.
- **corredores** (papel `restricao`, 36 feições; F01 LC 349/2022 art. 183 §§6º–10; LC 364/2023 art. 110 §8º): Corredores estruturadores da macro rede viária (exclusivos, preferenciais, estratégicos) – linhas de eixo.
- **eixos_desenvolvimento** (papel `informativa`, 12 feições; F01 LC 349/2022 arts. 159 I, 244 §2º e 252 §1º): Eixos de Desenvolvimento (corredores que geram a AA com faixa de ~350 m) – linhas.
- **declividade_30** (papel `restricao`, 15 feições; F01 LC 349/2022 art. 121 II; Lei federal 6.766/1979 art. 3º par. único III): Áreas com declividade acima de 30% (contornos – linhas).
- **restricao_aeroportuaria** (papel `restricao`, 9 feições; F14 Planos de zona de proteção de aeródromo (COMAER/DECEA – Portaria 957/GC3); camada municipal de referência): Restrições aeroportuárias (áreas de aproximação, cone de ruído e área de segurança) – grupo "Plano Diretor 2007" do Portal Mapa.
- **restricao_militar** (papel `restricao`, 3 feições; F14 Decreto-Lei federal 3.437/1941 arts. 1º e 2º): Áreas de restrição militar (Decreto-Lei 3.437/1941 – 1ª zona 15 braças/33 m, 2ª zona 600 braças/1.320 m).
- **programas_especiais** (papel `informativa`, 25 feições; F01 LC 349/2022 arts. 209 a 214; art. 120 V): Áreas de Programas Especiais de interesse urbanístico (Setores Central, Campinas e Sul), ambiental e econômico (Aerotrópole, polos, AUE).
- **aede** (papel `informativa`, 9 feições; F01 LC 349/2022 arts. 201 III e 208): Área Especial de Desenvolvimento Econômico (faixas ao longo de rodovias na zona rural).
- **arar_app** (papel `restricao`, 101 feições; F01 LC 349/2022 arts. 202 e 203): APPs da zona rural (ARAR) publicadas no Modelo Espacial.

## Limitações

- AAB derivada por diferença (oficial:false).
- Simplificação ~1 m; 6 casas decimais; lascas < 5 m² descartadas.
- Corredores, eixos e declividade são linhas.
- Serviços ArcGIS 10.4 sem data de atualização por feição em parte das camadas.
- Precedência entre unidades sobrepostas na base definida pelo analista (ARAU > APAC > AOS > ADD > AA > AAB).

## Lacunas (não encontrado em fonte oficial – ficou `null`)

- **Áreas verdes, UPI e ARCT urbanas**: Camadas ModeloEspacial/22, 24 e 26 retornam 0 feições no serviço público em 27/10/2026; essas áreas caem na AAB (residual) – confirmar.
- **Camadas ARAU/ARAR do Modelo Espacial com conteúdo trocado**: Camadas 18 (UUS rural) e 25 (UUS urbana) retornam polígonos de APP/APA; não foram usadas (usou-se a base Simplifica).
- **AAB sem camada própria**: Derivada por diferença (Macrozona Construída − demais unidades), conforme art. 157; marcada oficial:false.
- **Índice de aproveitamento da AAB e da AOS**: LC 349/2022 art. 196 só fixa IA para ADD e AA; nas demais o potencial resulta de altura/TO/recuos (sem número de CA).
- **Taxa de ocupação na APAC**: Anexo XXII e art. 190 não fixam TO para APAC.
- **Área do Bem Tombado (ABT)**: Parâmetros pelas diretrizes do órgão de tombamento (art. 154 §2º) – não publicados por imóvel.
- **Bosque dos Buritis, Hipódromo da Lagoinha e um entorno sem nome**: Entornos (AEBT) presentes na base sem linha correspondente no Anexo XXII.
- **Plano de Manejo das APAs**: Ocupação em APA depende do Plano de Manejo (art. 179 §3º) – não lido.
- **Grupos I/II/III (OODC) e Grupos do Anexo XXIII (vazios)**: Listas de setores não espacializadas (sem camada de bairros vinculada).
- **Vazios urbanos/PDU**: Não há camada pública de vazios elegíveis a PDU I–IV; regra da LC 371/2024 descrita só em texto.
- **Setores Jaó e Sul (altura 7,5 m)**: Sem polígono de bairro no JSON; condição registrada nos parâmetros de altura.
- **Restrições aeroportuárias e militares**: Camadas do grupo "Plano Diretor 2007"; regra federal (DECEA/Exército) não transcrita.
- **Declividade > 30%**: Camada publicada só como contornos (linhas).
- **Lei 10.845/2022 (atividades × vias)**: Quadros de incomodidade por via não transcritos (foco habitação).
- **Lei 9.123/2011 (PUAMA) e lista Grupo III de vazios**: Não lidas em detalhe.
- **Alterações após 27/10/2026 / revisão do PD**: Texto compilado do SILEG consultado em 27/10/2026; decretos de novas AEIS III posteriores à camada podem faltar.
- **Operação Urbana Consorciada**: Nenhuma OUC vigente identificada.

## Conteúdo desta pasta

- `goiania-go.json` – dados no padrão da plataforma (schema 1.1).
- `fontes/` – leis, decretos e quadros oficiais (PDF/HTML + texto extraído).
- `geo_raw/` – camadas brutas GeoJSON EPSG:4326 do Portal Mapa Goiânia (Simplifica FeatureServer/3 e Mapa_ModeloEspacial).
- `scripts/` – `baixar_camadas.py` (ArcGIS REST), `html2txt.py` (SILEG→texto), `comum_gyn.py` (fontes e construtores), `tabelas_gyn.py` (parâmetros transcritos), `build_gyn.py` (monta o JSON), `gerar_referencias.py`.

Reprodução: `cd scripts && python3 baixar_camadas.py && python3 build_gyn.py && python3 gerar_referencias.py && python3 ../../../validar_cidade.py goiania-go`.
