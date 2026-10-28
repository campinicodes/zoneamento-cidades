# Referências legais – Curitiba/PR (`curitiba-pr`)

Levantamento: 2026-10-27 · IBGE 4106902 · schema 1.1 · gerado por `scripts/gerar_referencias.py`.

> Só fontes oficiais e públicas (Legisladoc da Prefeitura/Câmara de Curitiba, mid.curitiba.pr.gov.br, GeoCuritiba/IPPUC – serviços públicos). Valores sem fonte = `null` e listados em *Lacunas*. Confirme sempre na SMU – Secretaria Municipal de Urbanismo (Consulta Informativa de Lote / "Guia Amarela") antes de decisão de compra.

## Marco legal vigente em 27/10/2026

Vigente em 27/10/2026: Plano Diretor Lei 14.771/2015; Zoneamento, Uso e Ocupação do Solo Lei 15.511/2019 (Quadros I–XLIX); potencial construtivo adicional (OODC/TDC/CPC) Lei 16.361/2024; prêmios e incentivos Lei 16.448/2024; edificações Dec. 2.397/2023; estacionamentos Dec. 209/2024; HIS COHAB Dec. 297/2026; OUC Linha Verde Lei 13.909/2011 (Lei 14.773/2015); Programa Curitiba de Volta ao Centro LC 150/2025 (SERC – Dec. 418/2026; retrofit Dec. 1.109/2026); APAs: Dec. 1.025/2021 e 1.004/2023 (Iguaçu), Dec. 924/2021 (Passaúna). Revisão do Plano Diretor em tramitação (não vigente).

## Como ler os parâmetros

- Zona base = código do zoneamento na camada 35 do Mapa Cadastral (GeoCuritiba); sub-áreas (ex.: `POLO-LV - 3`) ficam em `properties.subarea`.
- CA básico, TO, altura, recuo, afastamento, permeabilidade e lote: Quadros da Lei 15.511/2019 (linha *Habitação Coletiva*). CA máximo e pavimentos máximos: Lei 16.361/2024 Quadros II/III (50% OODC + 50% TDC); na OUC-LV, CEPAC (Lei 13.909/2011).
- HIS da COHAB-CT (Dec. 297/2026) em `parametros.outros.*_his_cohab`; vagas pelo Dec. 2.397/2023 arts. 74–75; densidade de conjuntos pelo art. 212 (100 × CA).

## Fontes

| ID | Norma | Data | Título | Arquivo local | Link oficial |
|---|---|---|---|---|---|
| F01 | Lei Municipal nº 15.511/2019 | 2019-10-10 | Lei de Zoneamento, Uso e Ocupação do Solo – texto compilado (Legisladoc) e publicação original | fontes/Lei15511_2019_compilada.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=290871) |
| F02 | Lei Municipal nº 15.511/2019, Quadros I a XLIX | 2019-10-10 | Lei 15.511/2019 – Quadros de parâmetros (anexos): I–IX eixos estruturantes (anexo 19282), X–XIV eixos de adensamento/conectores (19281), XV–XXIV ZC/ZR (19286), XXV–XXX ZUM/ZSM/ZFR (19287), XXXI–XLI zonas especiais (19288), XLII–XLIII SEPE (19289), XLIV–XLVIII vias setoriais/coletoras (19285), XLIX SEHIS (19284) | fontes/L15511_Q01-09_Eixos_Estruturantes.pdf | [link](https://legisladocexterno.curitiba.pr.gov.br/DownloadAnexo.ashx?tipo=pdf&id=19282) |
| F03 | Lei Municipal nº 16.361/2024 | 2024 | Aquisição de potencial construtivo adicional – OODC, TDC e CPC (Quadros I a V) | fontes/Lei16361_2024_outorga.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=416150) |
| F04 | Decreto Municipal nº 297/2026 | 2026 | Condições especiais de ocupação para HIS em parceria com a COHAB-CT (regulamenta art. 224 par. único da Lei 15.511) – revoga o Dec. 1.449/2022; mapas Anexos II e III (anexo 73928) | fontes/Dec297_2026_HIS.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=465685) |
| F05 | Decreto Municipal nº 2.397/2023 (em vigor desde 03/01/2024) | 2023-12-19 | Regulamentação das Edificações (definições, afastamentos, permeabilidade, recuo, densidade, vagas, recreação) | fontes/Dec2397_2023_vagas.pdf | [link](https://mid.curitiba.pr.gov.br/2024/00427509.pdf) |
| F06 | Decreto Municipal nº 209/2024 | 2024 | Regulamenta os arts. 214 e 217 a 220 da Lei 15.511 – locais onde não se admitem novos estacionamentos | fontes/Dec209_2024_estacionamento.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=408040) |
| F07 | Lei Municipal nº 16.448/2024 | 2024-12-03 | Prêmios, incentivos construtivos e condições especiais de ocupação (revoga a Lei 15.824/2021) | fontes/Lei16448_2024_premios.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=436120) |
| F08 | Lei Municipal nº 14.771/2015 | 2015-12-17 | Plano Diretor de Curitiba (revisão) – macrozoneamento, instrumentos | fontes/Lei14771_2015_PD.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=209820) |
| F09 | Lei Municipal nº 13.909/2011 e Lei nº 14.773/2015 | 2011-12-19 | Operação Urbana Consorciada Linha Verde – CEPAC (com alterações da Lei 14.773/2015, ato 209830) | fontes/Lei13909_2011_OUCLV.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=143116) |
| F10 | Lei Complementar Municipal nº 150/2025 | 2025-12-18 | Programa Curitiba de Volta ao Centro – Setor Especial da Região Central (SERC), retrofit e incentivos fiscais | fontes/LC150_2025_VoltaCentro.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=461267) |
| F11 | Decreto Municipal nº 418/2026 | 2026 | Regulamenta o SERC – coeficientes adicionais não onerosos por setor (novas edificações e retrofit) | fontes/Dec418_2026_SERC.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=466849) |
| F12 | Decreto Municipal nº 1.109/2026 | 2026 | Regulamenta o retrofit da LC 150/2025 | fontes/Dec1109_2026_retrofit.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=476311) |
| F13 | Decreto Municipal nº 1.730/2020 | 2020 | Incentivos construtivos e prêmios na ZC e ZCC (arts. 35 e 78 da Lei 15.511) | fontes/Dec1730_2020_ZC_ZCC.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=320660) |
| F14 | Decreto Municipal nº 1.025/2021 e Decreto nº 1.004/2023 | 2021-06-22 | APA do Iguaçu – setores e parâmetros (Quadros I a VII), com alteração do Dec. 1.004/2023 (ato 380795, ST-Bairro Novo do Caximba) | fontes/Dec1025_2021_APA_Iguacu.txt | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=332649) |
| F15 | Decreto Municipal nº 924/2021 | 2021-06-21 | APA do Passaúna – zonas e parâmetros (Quadros I a XIII, anexo 30368) | fontes/Dec924_2021_anexo.pdf | [link](https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id=334390) |
| F16 | IPPUC – serviço ArcGIS REST público | 2026-10-27 | GeoCuritiba/IPPUC – Mapa Cadastral público (camadas de zoneamento, APAs, OUC-LV, SEPE, SEPP, SETP, sistema viário, Dec. 297/2026, SERC) | — | [link](https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer) |
| F17 | IPPUC/SMMA | 2026-10-27 | GeoCuritiba/IPPUC – Sistema Municipal de Unidades de Conservação (serviço público) | — | [link](https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer) |
| F18 | Câmara/Prefeitura de Curitiba – Legisladoc externo | 2026-10-27 | Legisladoc – consulta pública de atos (situação "Em Vigor" verificada em 27/10/2026) | — | [link](https://legisladocexterno.curitiba.pr.gov.br/AtosConsultaExterna.aspx) |

## Artigos/anexos citados por fonte (nº de parâmetros que citam)

- **F01** (Lei Municipal nº 15.511/2019): Lei 15.511/2019 arts. 209 e 212; Dec. 2.397/2023 art. 43 (54); Lei 15.511/2019, arts. 121 a 124 (30); Lei 15.511/2019 arts. 112 a 114 (3); Lei 15.511/2019, art. 34 (mapa de zoneamento) (2); Lei 15.511/2019 art. 113 (2); Lei 15.511/2019 (2); Lei 15.511/2019, arts. 92 a 95 (setores especiais) (1); Lei 15.511/2019 arts. 96 a 107; Dec. 209/2024 (1); Lei 15.511 arts. 221 a 224 (1); Lei 15.511 art. 48 (1); arts. 212 §2º, 227 e 228 (1); arts. 169, 209 a 212 (1); arts. 11 e 12 (1)
- **F02** (Lei Municipal nº 15.511/2019, Quadros I a XLIX): Lei 15.511/2019, Quadro IX (Lei 15.511, transcrito das Leis 13.909/2011 e 14.773/2015) / Anexo V (Lei 13.909) (linha Habitação Coletiva quando admitida); arts. 20 a 22 (Lei 15.511); arts. 7º, 8º e 14 (Lei 13.909) (60); Lei 15.511/2019, Quadro XII (linha Habitação Coletiva quando admitida); arts. 27 a 33 (44); Lei 15.511/2019, Quadro XXXIV (linha Habitação Coletiva quando admitida); arts. 71 a 77 (36); Lei 15.511/2019, Quadro XIX (linha Habitação Coletiva quando admitida); arts. 41 e 42 (33); Lei 15.511/2019, Quadro XX (linha Habitação Coletiva quando admitida); arts. 43 e 44 (33); Lei 15.511/2019, Quadro XXXVIII (linha Habitação Coletiva quando admitida); arts. 84 e 85 (24); Lei 15.511/2019, Quadro XVII (linha Habitação Coletiva quando admitida); art. 39 (24); Lei 15.511/2019, Quadro XVIII (linha Habitação Coletiva quando admitida); art. 40 (24); Lei 15.511/2019, Quadro XVI (linha Habitação Coletiva quando admitida); arts. 37 e 38 (13); Lei 15.511/2019, Quadro XLII (nota 3) (linha Habitação Coletiva quando admitida); arts. 96 a 99 (12); Lei 15.511/2019, Quadro XLII (linha Habitação Coletiva quando admitida); art. 101 (12); Lei 15.511/2019, Quadro XXX (linha Habitação Coletiva quando admitida); arts. 65 e 66 (12); Lei 15.511/2019, Quadro XXXV (linha Habitação Coletiva quando admitida); arts. 71 a 77 (12); Lei 15.511/2019, Quadros XXII e XXIII (linha Habitação Coletiva quando admitida); arts. 45 a 49 (12); Lei 15.511/2019, Quadro XXI (linha Habitação Coletiva quando admitida); art. 48 (12) … (+28)
- **F03** (Lei Municipal nº 16.361/2024): Lei 16.361/2024, Quadros II e III (21); Lei 16.361/2024, Quadro II; arts. 7º e 11 (19); Lei 16.361/2024, Quadros II e III; arts. 7º e 11 (15); Lei 16.361/2024, Quadro II (13); art. 9º (3); Lei 16.361/2024 arts. 7º a 19; Quadros II a V (1); art. 7º; Quadros II e III (1); art. 10 §§1º–2º (1); arts. 11 e 19 (1); art. 12 (1); art. 17 (1); art. 18 (1); arts. 26 a 35 (1); Lei 16.361/2024 art. 12 (1)
- **F04** (Decreto Municipal nº 297/2026): Dec. 297/2026 art. 5º (74); Dec. 297/2026 art. 6º caput e §1º (63); Dec. 297/2026 art. 7º (59); Dec. 297/2026 art. 9º (44); Dec. 297/2026 art. 12 §1º (43); Dec. 297/2026 art. 6º §§2º–3º (11); Dec. 297/2026 art. 4º §3º (5); Dec. 297/2026 art. 7º I (4); Dec. 297/2026 art. 4º §1º e Anexo II (1); Dec. 297/2026 arts. 7º §§2º–3º e 9º; Anexo III (1); Dec. 297/2026 art. 7º §2º (1); Lei 15.511/2019 arts. 158–159, 221–224; Dec. 297/2026 (1); Dec. 297/2026 arts. 7º e 8º (1); Dec. 297/2026 arts. 4º, 6º, 9º–12 (1); Dec. 297/2026 arts. 1º, 2º e 13 (1)
- **F05** (Decreto Municipal nº 2.397/2023 (em vigor desde 03/01/2024)): Dec. 2.397/2023 arts. 74 III e 75; Dec. 297/2026 art. 9º; Dec. 209/2024 arts. 5º–7º (76); Dec. 2.397/2023 arts. 74 e 75 (1)
- **F06** (Decreto Municipal nº 209/2024): Dec. 209/2024 arts. 5º a 7º (1)
- **F07** (Lei Municipal nº 16.448/2024): Lei 16.448/2024 arts. 5º–23 (1)
- **F08** (Lei Municipal nº 14.771/2015): Lei 14.771/2015 arts. 20 §2º e 149 (1)
- **F09** (Lei Municipal nº 13.909/2011 e Lei nº 14.773/2015): Lei 13.909/2011 arts. 7º e 13 §2º, Anexo V; Lei 15.511 Quadro IX ("Parâmetros Construtivos com Potencial Adicional") (5); Lei 13.909/2011 art. 7º §9º; Lei 15.511 Quadro IX (5); Lei 13.909/2011 art. 7º §6º e art. 8º VI; Lei 15.511 Quadro IX (nota 8: habitações por hectare) (4); Lei 13.909/2011 Anexo V; Lei 15.511/2019 Lei 13.909 Anexo V (1); Lei 13.909/2011 Anexo V; Lei 15.511 Quadro IX (1); Lei 13.909/2011 arts. 1º, 5º e 13–14 (1); Lei 13.909/2011 arts. 10, 13, 14 e 27 (1); Lei 13.909/2011 arts. 7º §§7º–9º, 13 e 14 (1)
- **F10** (Lei Complementar Municipal nº 150/2025): LC 150/2025 art. 4º (1); LC 150/2025 arts. 12–14 e 18; Dec. 418/2026 (1); LC 150/2025 arts. 22 a 24 (1)
- **F11** (Decreto Municipal nº 418/2026): Dec. 418/2026 arts. 4º a 31 (7); Dec. 418/2026 (artigo do setor) (6); LC 150/2025 arts. 4º e 12–14; Dec. 418/2026 arts. 4º–31 (1); Dec. 418/2026 arts. 4º VIII–XI e 32–43 (1)
- **F12** (Decreto Municipal nº 1.109/2026): LC 150/2025 art. 18; Dec. 1.109/2026 (1)
- **F14** (Decreto Municipal nº 1.025/2021 e Decreto nº 1.004/2023): Dec. 1.025/2021 art. 6º e Quadro I (13); Dec. 1.025/2021 art. 6º e Quadro II (13); Dec. 1.025/2021 art. 6º e Quadro V (red. Dec. 752/2023 e Dec. 1.004/2023) (13); Dec. 1.025/2021 art. 6º e Quadro VII (12); Dec. 1.025/2021 art. 6º e Quadro III (12); Dec. 1.025/2021 art. 6º e Quadro IV (12); Dec. 1.025/2021 art. 6º e Quadro VI (12); Dec. 1.025/2021 art. 6º VIII (2); Dec. 1.025/2021 art. 6º e Quadros I–VII (1); Dec. 1.025/2021 Quadro V (red. Dec. 1.004/2023) (1)
- **F15** (Decreto Municipal nº 924/2021): Dec. 924/2021 art. 3º e Anexo Quadro II (13); Dec. 924/2021 art. 3º e Anexo Quadro I (13); Dec. 924/2021 art. 3º e Anexo Quadro IV (11); Dec. 924/2021 art. 3º e Anexo Quadro III (10); Dec. 924/2021 art. 3º e Anexo Quadro XII (2); Dec. 924/2021 art. 3º e Anexo (Quadros I–XIII) (1)
- **F16** (IPPUC – serviço ArcGIS REST público): Dec. 2.070/2025 (texto não baixado – ver lacunas) (1); atributo pp_altitude da camada 31 (1); Lei 9.800/2000; Dec. 673/2002 (não lido) (1); Dec. 2.027/2021 (não lido) (1)
- **F17** (IPPUC/SMMA): Lei 9.804/2000 (SMUC) e atos de criação (atributo atolegal) (1)

## Zonas (habitação coletiva)

| Código | Nome | Categoria | CA básico | CA máximo | Pavimentos | HIS COHAB CA | Feições |
|---|---|---|---|---|---|---|---|
| APA-IGUAÇU SARU | APA do Iguaçu – Setor de Alta Restrição de Uso | ambiental | 0,2 | 0,2 | 2 | — | 2 |
| APA-IGUAÇU SMRU | APA do Iguaçu – Setor de Média Restrição de Uso | ambiental | 0,4 | 0,4 | 2 | — | 5 |
| APA-IGUAÇU SS | APA do Iguaçu – Setor de Serviço | especial_economica | 0,4 | 0,4 | 4 | — | 4 |
| APA-IGUAÇU ST | APA do Iguaçu – Setor de Transição | residencial_baixa_densidade | 1 | 1 | 2 | — | 5 |
| APA-IGUAÇU ST-BNC | APA do Iguaçu – Setor de Transição – Bairro Novo do Caximba | especial_interesse_social | 1 | 1 | 4 | — | 1 |
| APA-IGUAÇU STR | APA do Iguaçu – Setor de Transição Restrito | residencial_baixa_densidade | 1 | 1 | 2 | — | 1 |
| APA-IGUAÇU SUC | APA do Iguaçu – Setor de Unidades de Conservação | ambiental | sem_dado | sem_dado | sem_dado | — | 6 |
| APA-IGUAÇU SUE | APA do Iguaçu – Setor de Uso Especial | ambiental | 0,2 | 0,2 | 2 | — | 5 |
| APA-PASSAÚNA ZEI | APA do Passaúna – Zona Especial de Indústria | industrial | 1 | 1 | sem_dado | — | 1 |
| APA-PASSAÚNA ZES | APA do Passaúna – Zona Especial de Serviços | especial_economica | 1 | 1 | 2 | — | 1 |
| APA-PASSAÚNA ZOO | APA do Passaúna – Zona de Ocupação Orientada | ambiental | 0,4 | 0,4 | 2 | — | 1 |
| APA-PASSAÚNA ZRA | APA do Passaúna – Zona de Recuperação Ambiental | ambiental | sem_dado | sem_dado | sem_dado | — | 1 |
| APA-PASSAÚNA ZUC II | APA do Passaúna – Zona de Urbanização Consolidada II | residencial_baixa_densidade | 1 | 1 | 2 | — | 6 |
| EAC | Eixo Presidente Affonso Camargo | eixo | 1,5 | 2,5 | 4 | 2,5 | 1 |
| EACB | Eixo de Adensamento Eng. Costa Barros | eixo | 1 | 2 | 4 | 2 | 1 |
| EACF | Eixo de Adensamento Comendador Franco | eixo | 1 | 2,5 | 4 | 2,5 | 1 |
| ECL-3 | Eixo Conector Leste 3 | eixo | 1,5 | 2,5 | 4 | 2,5 | 1 |
| ECO-1 | Eixo Conector Oeste 1 | eixo | 1,5 | Demais lotes: 2,5 / Lote lindeiro à ZR4: 2,5 | Lote lindeiro à ZR4: 6 / Demais: 4 | 2,5 | 1 |
| ECO-2 | Eixo Conector Oeste 2 | eixo | 1,5 | Demais lotes: 2,5 / Lote lindeiro à ZR4: 2,5 | Lote lindeiro à ZR4: 6 / Demais: 4 | 2,5 | 2 |
| ECO-3 | Eixo Conector Oeste 3 | eixo | 1,5 | Demais lotes: 2,5 / Lote lindeiro à ZR4: 2,5 | Lote lindeiro à ZR4: 6 / Demais: 4 | 2,5 | 1 |
| ECO-4 | Eixo Conector Oeste 4 | eixo | 1,5 | Demais lotes: 2,5 / Lote lindeiro à ZR4: 2,5 | Lote lindeiro à ZR4: 6 / Demais: 4 | 2,5 | 1 |
| ECS-1 | Eixo Conector Sul 1 | eixo | 1 | 1,5 | 4 | 1,5 | 1 |
| EE | Eixo Estrutural | eixo | Trechos EE Norte (Funcionários–Mascarenhas de Moraes–João Gbur–Mariano Gardolinski) e EE Sul (Pres. Kennedy–Orlando Padilha–W. Churchill/André Ferreira Barbosa) – nota 4 do Quadro I / nota (2) Lei 16.361 Q II: 3 / Demais trechos: 4 | Demais trechos (nota 1): 6 / Trechos nota (2): EE Norte e EE Sul indicados: 3 | livre | 6 | 8 |
| EMF | Eixo Marechal Floriano | eixo | 1 | 2,5 | 4 | 2,5 | 2 |
| ENC | Eixo Nova Curitiba | eixo | 2 | 3 | livre | 3 | 1 |
| POLO-LV | Polo Linha Verde | eixo | 1 | Parâmetros básicos (sem CEPAC): 1 / Com potencial adicional adquirido por CEPAC: 4 | livre | — | 12 |
| SE-LV | Setor Especial Linha Verde | eixo | 1 | Parâmetros básicos (sem CEPAC): 1 / Com potencial adicional adquirido por CEPAC: 4 | 6 | — | 11 |
| SEDE-CFC | Setor Especial Desportivo – Centro de Formação/Coritiba (Alto da XV) | institucional | 1 | 1 | 4 | — | 1 |
| SEDE-ECS-1 | Setor Especial Desportivo (sobre ECS-1) | institucional | 1 | 1 | 4 | — | 1 |
| SEDE-ZR4 | Setor Especial Desportivo (sobre ZR4) | institucional | 1 | 1 | 4 | — | 2 |
| SEHIS | Setor Especial de Habitação de Interesse Social | especial_interesse_social | 1 | Demais vias (zona não listada no Quadro II da Lei 16.361 – sem aquisição): 1 / Via setorial 1/2 ou coletora 1/2 (Lei 16.361 Q III): 1,5 | 3 | Demais vias: 1 / Vias classificadas: 1,5 | 19 |
| SEPPFC | Setor Especial de Preservação da Paisagem Ferroviária | patrimonio_cultural | sem_dado | sem_dado | sem_dado | — | 1 |
| UC | Unidade de Conservação / Parque (zoneamento) | ambiental | sem_dado | sem_dado | sem_dado | — | 58 |
| ZC | Zona Central | centralidade | 5 | 7 | livre | 7 | 10 |
| ZC-SEPE-BR | Zona Central – SEPE Barão-Riachuelo | patrimonio_cultural | Lotes com testada para a Rua Riachuelo, uso habitacional (nota 4): 5 / Cruzamento Riachuelo × XV de Novembro (nota 4): 3,6 / Demais: 3,6 | Lotes com testada para a Rua Riachuelo, uso habitacional (nota 4): 5 / Cruzamento Riachuelo × XV de Novembro (nota 4): 3,6 / Demais: 3,6 | sem_dado | 7 | 2 |
| ZC-SEPE-C | Zona Central – Setor Especial Preferencial de Pedestres (Setor Central) | centralidade | 5 | 5 | 5 | 7 | 4 |
| ZC-SEPE-XV | Zona Central – SEPE Rua XV de Novembro | patrimonio_cultural | 3,6 | 3,6 | 5 | — | 1 |
| ZCC | Zona de Centro Cívico | centralidade | Lotes com testada para a Av. Cândido de Abreu (Quadro XXXVI): 4 / Demais (Quadro XXXVII): 2 | ZCC-Incentivo – Av. Cândido de Abreu: 5 / ZCC-Incentivo – demais (perímetro Anexo I-e): 2,5 | Av. Cândido de Abreu: livre / Demais: 6 | Av. Cândido de Abreu: 5 / Demais: 2,5 | 5 |
| ZCSF | Zona de Contenção São Francisco | residencial_baixa_densidade | 1 | 1 | 2 | 1 | 1 |
| ZCUM | Zona de Contenção de Uso Misto | residencial_baixa_densidade | 1 | 1 | 2 | 1 | 1 |
| ZE | Zona Especial Educacional | institucional | 0,5 | 1 | 4 | — | 2 |
| ZE-D-LV | Zona Especial Desportiva Linha Verde (ZED) | institucional | 0,5 | Parâmetros básicos (sem CEPAC): 0,5 / Com potencial adicional adquirido por CEPAC: 1 | 4 | — | 4 |
| ZFR | Zona de Fundo de Rio (Belém) | mista_media_densidade | 2 | 2 | 6 | 2 | 1 |
| ZH-1 | Zona Histórica 1 | patrimonio_cultural | 2,6 | 2,6 | 3 | 2,6 | 5 |
| ZH-1-SEPE-BR | Zona Histórica 1 – SEPE Barão-Riachuelo | patrimonio_cultural | 2,6 | 2,6 | 3 | 2,6 | 1 |
| ZH-1-SEPE-C | Zona Histórica 1 – SEPE Setor Central | patrimonio_cultural | 2,6 | 2,6 | 3 | 2,6 | 3 |
| ZH-2 | Zona Histórica 2 | patrimonio_cultural | 2 | 2 | 4 | 2 | 1 |
| ZI | Zona Industrial | industrial | sem_dado | sem_dado | sem_dado | — | 7 |
| ZI-LV | Zona Industrial Linha Verde | industrial | sem_dado | sem_dado | sem_dado | — | 1 |
| ZM | Zona Militar | institucional | 0,5 | 1 | 4 | — | 3 |
| ZPS | Zona Polo de Software | especial_economica | sem_dado | sem_dado | sem_dado | — | 1 |
| ZR-4-LV | Zona Residencial 4 Linha Verde | residencial_media_densidade | 2 | Parâmetros básicos (sem CEPAC): 2 / Com potencial adicional adquirido por CEPAC: 2,5 | 6 | — | 3 |
| ZR1 | Zona Residencial 1 | residencial_baixa_densidade | 1 | 1 | 2 | — | 10 |
| ZR2 | Zona Residencial 2 | residencial_baixa_densidade | 1 | Demais vias (zona não listada no Quadro II da Lei 16.361 – sem aquisição): 1 / Via setorial 1/2 ou coletora 1/2 (Lei 16.361 Q III): 1,5 | 2 | Demais vias: 1 / Vias classificadas (setoriais/coletoras): 1,5 | 14 |
| ZR2 - A | Zona Residencial 2 – Setor Especial de Pontos Panorâmicos | residencial_baixa_densidade | 1 | Demais vias (zona não listada no Quadro II da Lei 16.361 – sem aquisição): 1 / Via setorial 1/2 ou coletora 1/2 (Lei 16.361 Q III): 1,5 | 2 | Demais vias: 1 / Vias classificadas (setoriais/coletoras): 1,5 | 1 |
| ZR3 | Zona Residencial 3 | residencial_baixa_densidade | 1 | Vias normais: 1,5 / Via setorial 1/2 (Lei 16.361 Q III): 1,8 / Via coletora 1/2 (Lei 16.361 Q III): 1,5 | 3 | Demais vias: 1,5 / Vias setoriais: 1,8 / Vias coletoras: 1,5 | 18 |
| ZR3 - A | Zona Residencial 3 – Setor Especial de Pontos Panorâmicos | residencial_baixa_densidade | 1 | Vias normais: 1,5 / Via setorial 1/2 (Lei 16.361 Q III): 1,8 / Via coletora 1/2 (Lei 16.361 Q III): 1,5 | 3 | Demais vias: 1,5 / Vias setoriais: 1,8 / Vias coletoras: 1,5 | 2 |
| ZR3-T | Zona Residencial 3 Transição | residencial_media_densidade | 1 | Demais lotes: 2 / Testada para via externa EE/ENC até 100 m: 2 | Testada para via externa do EE/ENC até 100 m: 6 / Demais: 4 | 2 | 8 |
| ZR3-T - ALTO DA GLÓRIA | Zona Residencial 3 Transição – Alto da Glória | residencial_media_densidade | 1 | 2,5 | Testada para via externa do EE/ENC até 100 m: 6 / Demais: 4 | 2,5 | 1 |
| ZR3-T - MERÇÊS | Zona Residencial 3 Transição – Mercês | residencial_media_densidade | 1 | 2,5 | Testada para via externa do EE/ENC até 100 m: 6 / Demais: 4 | 2,5 | 1 |
| ZR4 | Zona Residencial 4 | residencial_media_densidade | 2 | 2,5 | 6 | 2,5 | 14 |
| ZR4 - ALTO DA XV | Zona Residencial 4 – Alto da XV | residencial_media_densidade | 2 | 2,5 | 6 | 2,5 | 1 |
| ZR4 - BATEL | Zona Residencial 4 – Batel | residencial_media_densidade | 2 | 2,5 | 6 | 2,5 | 1 |
| ZROC-1 | Zona Residencial de Ocupação Controlada 1 | residencial_baixa_densidade | 0,4 | Demais vias (zona não listada no Quadro II da Lei 16.361 – sem aquisição): 0,4 / Via setorial 1/2 ou coletora 1/2 (Lei 16.361 Q III): 1 | 2 | — | 3 |
| ZROC-1 CAMPO DE SANTANA | ZROC-1 Campo de Santana (art. 48) | expansao | 1 | 1 | 4 | 1 | 1 |
| ZROI | Zona Residencial de Ocupação Integrada | residencial_baixa_densidade | 1 | Demais vias (zona não listada no Quadro II da Lei 16.361 – sem aquisição): 1 / Via setorial 1/2 ou coletora 1/2 (Lei 16.361 Q III): 1,5 | 2 | Demais vias: 1 / Vias classificadas: 1,5 | 2 |
| ZS-1 | Zona de Serviço 1 | especial_economica | sem_dado | 2 | sem_dado | — | 10 |
| ZS-2 | Zona de Serviço 2 | especial_economica | sem_dado | sem_dado | sem_dado | — | 5 |
| ZS-2-LV | Zona de Serviço 2 Linha Verde | especial_economica | 1 | 1 | 2 | — | 1 |
| ZSM | Zona Setor Misto | mista_media_densidade | 2 | 3 | 6 | 3 | 1 |
| ZSM-SEPE-C | Zona Setor Misto – SEPE Setor Central | mista_media_densidade | 2 | 3 | 5 | 3 | 1 |
| ZT-LV | Zona de Transição Linha Verde | mista_media_densidade | 1 | Parâmetros básicos (sem CEPAC): 1 / Com potencial adicional adquirido por CEPAC: 2,5 | 4 | — | 12 |
| ZUM-1 | Zona de Uso Misto 1 | mista_baixa_densidade | 1 | Vias normais (Quadro II): 1,5 / Via setorial/coletora (Q III): 1,5 | 4 | 1,5 | 5 |
| ZUM-2 | Zona de Uso Misto 2 | mista_media_densidade | 2 | 2 | 6 | 2 | 3 |
| ZUM-3 | Zona de Uso Misto 3 | mista_media_densidade | 2 | 2,5 | 4 | 2,5 | 3 |
| ZUMVP | Zona de Uso Misto Vila Parolin | mista_media_densidade | 1 | 3 | CA até 1: 4 / CA 2: 8 / CA 3: 12 | 3 | 1 |

## Resumo MCMV

- Maior potencial: Eixos Estruturais (EE: CA 4 → 6 com OODC/TDC, HIS COHAB 6, densidade livre, altura livre), ZC (5 → 7, IPU 0,3 para habitacional) e ENC (2 → 3) – terra cara; via central do EE exige Plano Massa.
- Equilíbrio MCMV: ZR4, EAC, EMF, EACF, ECL-3 e ECO-1..4 (CA 1,5–2 → 2,5; 6–10 pavimentos com aquisição; HIS COHAB CA 2,5 e 625 uh/ha) – EACF/EACB/ECL-3/EMF com IPU 0,3 (OODC 70% mais barata).
- HIS com a COHAB-CT (Dec. 297/2026): isenção de OODC (Lei 16.361 art. 12), +1 pavimento, 1 vaga/4 UH (facultada perto de terminais/estações), lote 125 m², densidade +20% perto do transporte; exige UH para famílias do cadastro COHAB.
- ZR3 / ZR3-T / ZUM-1/2/3 / ZSM / ZFR: CA 1–2 → 1,5–3; bons para conjuntos de 4–6 pavimentos em terrenos ≤ 20.000 m² (art. 169). ZR3 ganha mais em vias setoriais (1,8) e coletoras (1,5).
- OUC Linha Verde: POLO-LV e SE-LV até CA 4 por CEPAC (densidade livre), ZT-LV e ZR-4-LV até 2,5 (250 uh/ha) – custo do CEPAC e contenção de cheias obrigatória.
- Centro (SERC): SBE e ST-04 dão +2 de CA não oneroso para HIS (ST-01 +1; ST-03 +0,5), limitado ao CA máximo da Lei 16.361, e incentivos de IPTU/ITBI/ISS até 2032 (LC 150/2025).
- Evitar: ZR1 (só unifamiliar), ZR2 fora do Dec. 297, ZROC-1 (CA 0,4, lote 2.000 m²), ZS-1/ZS-2/ZI/ZPS (sem habitação coletiva), APAs do Iguaçu e do Passaúna (≤ 2–10 uh/ha), UCs, SETP-Largo da Ordem e Pontos Panorâmicos (altura limitada).
- Vagas fora da HIS: 1 por apartamento (quitinete facultada) + visitantes 1/50 UH acima de 100 UH (Dec. 2.397/2023) – nas vias do Dec. 209/2024 não se admitem novos estacionamentos.

## Camadas geográficas

Servidor oficial: https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer · CRS de área: EPSG:31982

| Camada | Arquivo bruto | Oficial | Método | Feições | Download | URL |
|---|---|---|---|---|---|---|
| Zoneamento – base cadastral (zonas base) | `geo_raw/zoneamento_cadastral.geojson` | sim | vetor oficial | 341 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/35 |
| Zoneamento Lei 15.511/2019 (camada de referência, não usada como base) | `geo_raw/zoneamento_l15511.geojson` | sim | vetor oficial | 223 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/36 |
| Dec. 297/2026 – áreas HIS (Anexo II) | `geo_raw/dec297_areas.geojson` | sim | vetor oficial | 143 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/41 |
| Dec. 297/2026 – Anexo III (raios de terminais/estações) | `geo_raw/dec297_densidade_ampliada.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/42 |
| SERC – setores (Dec. 418/2026) | `geo_raw/serc_setores.geojson` | sim | vetor oficial | 9 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/43 |
| SERC – eixos prioritários | `geo_raw/serc_eixos.geojson` | sim | vetor oficial | 14 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/45 |
| SERC – perímetro | `geo_raw/serc_perimetro.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/46 |
| OUC Linha Verde | `geo_raw/ouc_linha_verde.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/29 |
| APA do Iguaçu – setores | `geo_raw/apa_iguacu.geojson` | sim | vetor oficial | 39 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/27 |
| APA do Passaúna – zonas | `geo_raw/apa_passauna.geojson` | sim | vetor oficial | 1531 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/28 |
| SMUC – ESEC | `geo_raw/uc_estacao_ecologica.geojson` | sim | vetor oficial | 2 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – PQ | `geo_raw/uc_parque_natural.geojson` | sim | vetor oficial | 32 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – PQ_LINEAR | `geo_raw/uc_parque_linear.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – BQ | `geo_raw/uc_bosque_municipal.geojson` | sim | vetor oficial | 18 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – BCBU | `geo_raw/uc_bosque_conservacao.geojson` | sim | vetor oficial | 8 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – RVS | `geo_raw/uc_refugio.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – RPPNM | `geo_raw/uc_rppnm.geojson` | sim | vetor oficial | 67 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – UC_ESPECIFICA | `geo_raw/uc_especificas.geojson` | sim | vetor oficial | 2 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – APA_MUNICIPAL | `geo_raw/uc_apa.geojson` | sim | vetor oficial | 2 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SMUC – ARIE | `geo_raw/uc_arie.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer |
| SETP Largo da Ordem | `geo_raw/setp_largo_ordem.geojson` | sim | vetor oficial | 1 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/50 |
| SETP Largo da Ordem – áreas | `geo_raw/setp_largo_ordem_areas.geojson` | sim | vetor oficial | 3 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/51 |
| Pontos panorâmicos (SEPP) | `geo_raw/pontos_panoramicos.geojson` | sim | vetor oficial | 3 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/31 |
| Setor Especial do Parque Tanguá | `geo_raw/parque_tangua.geojson` | sim | vetor oficial | 8 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/32 |
| Setor Especial de Vilas de Ofícios | `geo_raw/vila_oficios.geojson` | sim | vetor oficial | 109 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/33 |
| SEPE (linhas) | `geo_raw/sepe.geojson` | sim | vetor oficial | 88 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/30 |
| Sistema viário básico (linhas) | `geo_raw/sistema_viario.geojson` | sim | vetor oficial | 1240 | 2026-10-27 | https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/Publico_GeoCuritiba_MapaCadastral/MapServer/34 |

### Camadas complementares no JSON

- **dec297_areas_his** (papel `informativa`, 36 feições; F04 Dec. 297/2026 art. 4º §1º e Anexo II): Eixos, zonas e setores onde se admitem as condições especiais de HIS da COHAB-CT (Dec. 297/2026, mapa do Anexo II).
- **dec297_densidade_ampliada** (papel `informativa`, 1 feições; F04 Dec. 297/2026 arts. 7º §§2º–3º e 9º; Anexo III): Raios de 800 m de terminais e 400 m de estações das linhas expressa/direta (Dec. 297/2026 Anexo III): densidade HIS +20% (art. 7º §2º) e vagas facultadas (art. 9º).
- **serc_setores** (papel `informativa`, 7 feições; F11 LC 150/2025 arts. 4º e 12–14; Dec. 418/2026 arts. 4º–31): Setor Especial da Região Central (Programa Curitiba de Volta ao Centro – LC 150/2025) – CA adicional NÃO oneroso por setor (Dec. 418/2026).
- **serc_eixos** (papel `informativa`, 14 feições; F11 Dec. 418/2026 arts. 4º VIII–XI e 32–43): Eixos prioritários do SERC (EP-XV, EP-BR, EP-TG, EP-SM) – incentivos de retrofit (Dec. 418/2026 arts. 32–43).
- **serc_perimetro** (papel `informativa`, 1 feições; F10 LC 150/2025 art. 4º): Perímetro do SERC (LC 150/2025; Dec. 418/2026 Anexo I).
- **ouc_linha_verde** (papel `informativa`, 1 feições; F09 Lei 13.909/2011 arts. 1º, 5º e 13–14): Perímetro da Operação Urbana Consorciada Linha Verde (Lei 13.909/2011) – potencial adicional por CEPAC.
- **apa_iguacu** (papel `restricao`, 8 feições; F14 Dec. 1.025/2021 art. 6º e Quadros I–VII): APA municipal do Iguaçu – setores (Dec. 1.025/2021).
- **apa_passauna** (papel `restricao`, 16 feições; F15 Dec. 924/2021 art. 3º e Anexo (Quadros I–XIII)): APA estadual do Passaúna – zoneamento detalhado (recorte Curitiba).
- **unidades_conservacao** (papel `restricao`, 134 feições; F17 Lei 9.804/2000 (SMUC) e atos de criação (atributo atolegal)): Sistema Municipal de Unidades de Conservação (SMUC) – polígonos das UCs.
- **setp_largo_ordem** (papel `restricao`, 3 feições; F16 Dec. 2.070/2025 (texto não baixado – ver lacunas)): Setor Especial de Transição da Paisagem do Largo da Ordem (Dec. 2.070/2025).
- **pontos_panoramicos** (papel `restricao`, 3 feições; F01 Lei 15.511/2019 arts. 112 a 114): Setor Especial dos Pontos Panorâmicos – áreas de influência (Lei 15.511 arts. 112–114; Dec. 1.006/2020).
- **parque_tangua** (papel `restricao`, 3 feições; F16 Lei 9.800/2000; Dec. 673/2002 (não lido)): Setor Especial do Parque Tanguá (parque, transição e amortecimento – Dec. 673/2002).
- **vila_oficios** (papel `informativa`, 2 feições; F16 Dec. 2.027/2021 (não lido)): Setor Especial de Vilas de Ofícios (Dec. 2.027/2021) – inclui assentamentos irregulares mapeados.
- **sepe** (papel `informativa`, 88 feições; F01 Lei 15.511/2019 arts. 96 a 107; Dec. 209/2024): Setor Especial Preferencial de Pedestres (eixos – linhas).
- **sistema_viario_basico** (papel `informativa`, 1240 feições; F02 Lei 15.511/2019 Quadros XLIV a XLVIII; Lei 16.361/2024 Quadro III; Dec. 297/2026 art. 5º III): Sistema viário básico classificado (Lei 15.511/2019) – define os parâmetros das vias setoriais/coletoras/prioritárias (Quadros XLIV–XLVIII) e da Lei 16.361 Quadro III.

## Limitações

- Camada 35 tem atualização 2022-03; alterações posteriores de zoneamento por lei específica podem faltar.
- Simplificação ~1 m (zonas) e ~2 m (camadas dissolvidas); coordenadas com 6 casas.
- Sistema viário e SEPE são linhas de eixo de via: o lote deve ter testada para a via.
- APA do Passaúna recortada ao limite municipal aproximado.
- Camada 36 (Lei 15.511, 2019) baixada só para comparação.

## Lacunas (não encontrado em fonte oficial – ficou `null`)

- **Áreas de risco, inundação e APP (camadas públicas)**: Não há camada pública de risco/inundação/APP no Mapa Cadastral público; as camadas do GeoCuritiba "Interno" não foram usadas (acesso interno). Verificar na Guia Amarela/SMMA.
- **Patrimônio (UIP – Unidades de Interesse de Preservação)**: Sem camada pública de UIP localizada; só SETP-Largo da Ordem e zonas ZH.
- **ZI-LV (Zona Industrial da Linha Verde)**: Parâmetros não identificados com segurança no Anexo V/Quadro IX.
- **SEPPFC (Setor Especial de Preservação da Paisagem Ferroviária)**: Parâmetros no Dec. 1.033/2001 – texto não obtido.
- **Coeficiente de ajuste "a" do SEPP**: Lei 15.511 art. 113 §1º remete à localização de cada ponto (Dec. 1.006/2020) – não lido.
- **Limiares do EIV**: Decreto regulamentador dos arts. 227–228 não transcrito.
- **Trechos de Plano Massa do EE**: Plano Massa por trecho não publicado em camada.
- **Via central × vias externas × outras vias do EE**: A camada de zoneamento não distingue as faixas do EE; Quadros I–III indicados como condicionais.
- **Perímetros ZCC-Incentivo, ZR4 Batel/Alto da XV, ZR3-T Mercês/Alto da Glória**: Usados os da camada 35 (sub-áreas); o Anexo I da Lei 16.361 não foi vetorizado.
- **Divergência entre camadas 35 (2022-03) e 36 (Lei 15.511, 2019-10)**: Diferença simétrica ≈ 5,0 km² (0,4 km² na ZCSF, 1,1 km² em UC); adotada a 35 (mais recente).
- **Usos permitidos × permissíveis × tolerados e parâmetros de usos não habitacionais**: Somente a linha "Habitação Coletiva" foi transcrita (foco MCMV).
- **CA mínimo / PEUC**: Sem CA mínimo por zona na Lei 15.511; PEUC depende de lei específica.
- **Lei 14.773/2015 (alterações da OUC-LV) e regulamento de HIS da OUC-LV (art. 9º IV)**: Texto consolidado lido via Lei 13.909 (redações dadas pela 14.773); regulamento de HIS da OUC-LV não localizado.
- **Decretos de setores especiais (Dec. 2.070/2025 SETP-LO; Dec. 673/2002 Tanguá; Dec. 2.027/2021 Vilas de Ofícios)**: Não lidos; camadas incluídas apenas como alerta/informação.
- **Revisão do Plano Diretor (PL 005.00285.2026)**: Em tramitação em 27/10/2026 – não vigente, não usada.
- **Incentivos SERC para eixos EP-TG e EP-SM**: Valores dos arts. 38–43 do Dec. 418/2026 não transcritos.

## Conteúdo desta pasta

- `curitiba-pr.json` – dados no padrão da plataforma (schema 1.1).
- `fontes/` – leis, decretos e quadros oficiais (PDF/HTML + texto extraído).
- `geo_raw/` – camadas brutas GeoJSON EPSG:4326 do GeoCuritiba (serviços públicos).
- `scripts/` – `baixar_camadas.py` (ArcGIS REST), `baixa_ato.py`/`busca.py` (Legisladoc), `comum_cwb.py` (fontes), `tabelas_cwb.py` (Quadros transcritos), `build_cwb.py` (monta o JSON), `gerar_referencias.py`.

Reprodução: `cd scripts && python3 baixar_camadas.py && python3 build_cwb.py && python3 gerar_referencias.py && python3 ../../../validar_cidade.py curitiba-pr`.
