# Referências legais – Porto Alegre/RS (`porto-alegre-rs`)

Levantamento: 2026-10-27 · IBGE 4314902 · schema 1.1 · gerado por `scripts/gerar_referencias.py`.

> Só fontes oficiais e públicas (PMPA/SMAMUS, DOPA, SAPL/legislação municipal, ArcGIS público da SMAMUS). Valores sem fonte = `null` e listados em *Lacunas*. Confirme sempre na SMAMUS – Escritório de Licenciamento (DMI – Declaração Municipal Informativa) (DMI) antes de decisão de compra.

## Marco legal vigente em 27/10/2026

Vigente em 27/10/2026: PDDUA – LC 434/1999 e alterações (compilação 16/12/2025), com regime urbanístico por subunidade (Anexos 4 densidade, 5 atividades, 6 índices, 7 volumetria, 8 parcelamento, 10 vagas – Dec. 20.385/2019, 11 Projetos Especiais); Solo Criado pela LC 946/2022; HIS: art. 22/76 do PDDUA, LC 636/2010 (PMCMV-POA), LC 547/2006 e 548/2006, LC 1.022/2024 (só protocolos até 31/12/2025) e Dec. 22.932/2024; Zona Rural LC 775/2015; Centro Histórico LC 930/2021; +4D LC 960/2022. Revisão: PDUS (LC 1.075/2026) e LUOS (LC 1.076/2026) sancionados em 14/07/2026, vigência 180 dias após a publicação (art. 125 LUOS) e aplicação das novas regras a partir de 2027 após regulamentação – NÃO usados para os índices deste arquivo.

## Como ler o regime do PDDUA

- Cada **subunidade** do PDDUA tem 4 códigos: densidade (Anexo 4), grupamento de atividades (Anexo 5), índice de aproveitamento (Anexo 6) e volumetria (Anexo 7.1). A zona base deste JSON é a combinação `D{densidade}-A{atividade}-IA{índice}-V{volumetria}`; o polígono de cada subunidade fica em `geometria.features` com MZ/UEU/subunidade.
- 230 combinações base (1546 subunidades) + 6 zonas sobrepostas de AEIS (AEIS, AEIS I, AEIS I-II, AEIS II, AEIS III, AEIS IV).
- CA básico = IA do Anexo 6; CA máximo = IA máximo (via Solo Criado, LC 946/2022), limitado a 3,0; área rarefeita: máximo = básico (art. 110).
- Lote/testada: Anexo 8.1 (loteamento); AEIS: 125 m²/5 m (nota 3). Vagas: Anexo 10.1 (Dec. 20.385/2019) – residencial dispensado em testada ≥ 12 m; MCMV 0,5 vaga/UH (LC 636/2010 art. 21).

## Fontes

| ID | Norma | Data | Título | Arquivo local (fontes/) | Link oficial |
|---|---|---|---|---|---|
| F01 | Lei Complementar nº 434/1999 e alterações | 1999-12-01 (compilação 2025-12-16) | PDDUA – Plano Diretor de Desenvolvimento Urbano Ambiental, compilação com anexos (versão 20251216) | PDDUA_compilado_20251216.pdf | [link](https://licenciamento-api.procempa.com.br/api/urbanismodrive/geopmpa/SPM/PUBLICO/PDDUA_ATUAL/ANEXOS%20ATUALIZADOS/PDDUA%2020251216%20com%20Anexos.pdf) |
| F02 | LC 434/1999, Anexo 4 | 1999-12-01 | PDDUA Anexo 4 – Densidades brutas | PDDUA_Anexo_4.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_4.pdf) |
| F03 | LC 434/1999, Anexo 5; Decreto nº 20.628/2020 | 2020-06-25 | PDDUA Anexo 5 – Regime de atividades (5.1 grupamentos; 5.3/5.4 Área Intensiva com redação do Dec. 20.628/2020; 5.5 Área Rarefeita) | PDDUA_Anexo_5.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_5.pdf) |
| F04 | LC 434/1999, Anexo 6 | 1999-12-01 | PDDUA Anexo 6 – Índices de aproveitamento e quota ideal | PDDUA_Anexo_6.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_6.pdf) |
| F05 | LC 434/1999, Anexo 7 | 1999-12-01 | PDDUA Anexo 7 – Regime volumétrico (7.1 por UEU; 7.2 malha viária) | PDDUA_Anexo_7.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_7.pdf) |
| F06 | LC 434/1999, Anexo 8 | 1999-12-01 | PDDUA Anexo 8 – Parcelamento do solo (8.1 loteamentos; 8.2 desmembramentos) | PDDUA_Anexo_8.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_8.pdf) |
| F07 | LC 434/1999, Anexo 10; Decreto nº 20.385/2019 | 2019-11-01 | PDDUA Anexo 10 – Garagens e estacionamentos (Anexo 10.1 alterado pelo Dec. 20.385/2019) | PDDUA_Anexo_10.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_10.pdf) |
| F08 | LC 434/1999, Anexo 11 | 1999-12-01 | PDDUA Anexo 11 – Projetos Especiais de Impacto Urbano (1º e 2º graus) | PDDUA_Anexo_11.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/Anexo_11.pdf) |
| F09 | Lei Complementar nº 1.075/2026 | 2026-07-14 | Plano Diretor Urbano Sustentável – PDUS (sancionado, regras a partir de 2027) | LC1075_2026_PDUS.pdf | [link](https://dopaonlineupload.procempa.com.br/dopaonlineupload/6102_ce_619410_1.pdf) |
| F10 | Lei Complementar nº 1.076/2026 | 2026-07-14 | Lei de Parcelamento, Uso e Ocupação do Solo – LUOS (sancionada, vigência 180 dias após publicação) | LC1076_2026_LUOS.pdf | [link](https://dopaonlineupload.procempa.com.br/dopaonlineupload/6102_ce_619426_1.pdf) |
| F11 | PMPA – Gabinete do Prefeito | 2026-07-14 | Notícia oficial – Prefeito sanciona novo Plano Diretor e LUOS | — | [link](https://prefeitura.poa.br/gp/noticias/prefeito-sanciona-novo-plano-diretor-e-lei-de-uso-e-ocupacao-do-solo) |
| F12 | PMPA – SMAMUS | 2026 | Notícia oficial SMAMUS – Regras do novo Plano Diretor passam a valer a partir de 2027 | — | [link](https://www.prefeitura.poa.br/smamus/noticias/regras-do-novo-plano-diretor-passam-valer-partir-de-2027) |
| F13 | Lei Complementar nº 1.022/2024 | 2024-09-12 | Fomento à produção de Habitação de Interesse Social (HIS) – isenções de Solo Criado e regime volumétrico | LC1022_2024_HIS.pdf | [link](https://dopaonlineupload.procempa.com.br/dopaonlineupload/5342_ce_491154_1.pdf) |
| F14 | Decreto nº 22.932/2024 | 2024-09-30 | Regulamenta a LC 1.022/2024 – Comissão/rito de Projeto Especial para HIS | Dec22932_2024.pdf | [link](https://dopaonlineupload.procempa.com.br/dopaonlineupload/5370_ce_503434_1.pdf) |
| F15 | Lei Complementar nº 636/2010 | 2010-01-13 | Programa Minha Casa, Minha Vida – Porto Alegre (incentivos urbanísticos e tributários) | LC636_2010.docx | [link](https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2010/36557/lei_complementar_no_636.docx) |
| F16 | Lei Complementar nº 548/2006 | 2006 | Padrões construtivos para Habitação de Interesse Social | LC548_2006.docx | [link](https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2006/34245/lei_complementar_no_548.docx) |
| F17 | Lei Complementar nº 547/2006 | 2006 | Parcelamento do solo de interesse social | LC547_2006.docx | [link](https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2006/34244/lei_complementar_no_547.docx) |
| F18 | Lei Complementar nº 946/2022 | 2022 | Outorga onerosa do direito de construir (Solo Criado) – fórmula e fator de planejamento | LC946_2022.pdf | [link](https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2022/44102/lei_complementar_no_946.pdf) |
| F19 | PGM Porto Alegre | 2011 | Parecer PGM sobre a LC 636/2010 (repositório institucional DSpace PMPA) | dspace_doc.pdf | [link](https://dspace.portoalegre.rs.gov.br/bitstreams/1de45b15-d02e-491d-80ce-cb52e7992be1/download) |
| F20 | Base cartográfica PMPA/SMAMUS | 2026-10-27 | Camada oficial do regime urbanístico por subunidade (PDDUA) – ArcGIS REST SMAMUS | — | [link](https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/PDDUA/FeatureServer/0) |
| F21 | PMPA/SMAMUS | 2026-10-27 | Mapas digitais da SMAMUS – shapefiles oficiais (AEIS 12/05/2022, PBZPA/PBZPH, APP) e metadados | mapas_digitais.html | [link](https://prefeitura.poa.br/smamus/planejamento-urbano/mapas-digitais) |
| F22 | PMPA/SMAMUS | 2026-10-27 | Serviço público POA – Consultas MIL1 (macrozonas, zona rural, bens tombados/inventariados, suscetibilidade a inundação, setores de risco CPRM, unidades de conservação) | — | [link](https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer) |
| F23 | Lei Complementar nº 960/2022 | 2022-10-05 | Perímetro do Programa +4D (4º Distrito) – ArcGIS REST | — | [link](https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/Limite_Programa_4D_130326/FeatureServer/0) |
| F24 | PMPA/SMAMUS | s/d | Guia Prático do PDDUA (leitura do regime urbanístico) | Guia_Pratico.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/Guia%20Pratico.pdf) |
| F25 | PMPA/SMAMUS | s/d | Metadados do PDDUA (dicionário de campos DENSIDADE/ATIVIDADE/INDICE/VOLUMETRIA) | ../geo_raw/PDDUA_Metadados.zip | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/PDDUA_Metadados.zip) |
| F26 | PMPA/SMAMUS | s/d | Mapa oficial das AEIS (PDF) | AEIS.pdf | [link](https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/AEIS.pdf) |

## Artigos/anexos citados por fonte (nº de parâmetros que citam)

- **F01** (Lei Complementar nº 434/1999 e alterações): art. 113 III a LC 434/99 (redação LC 646/2010) (460); art. 117 I LC 434/99 (227); arts. 27–28 LC 434/99 (227); arts. 53, 110 e 111 LC 434/99; LC 946/2022 (208); art. 96 §§ 7º a 11 LC 434/99 (redação LC 646/2010) (163); art. 76 §8º LC 434/99 (66); art. 110 LC 434/99 (19); art. 29 LC 434/99 (8); art. 76 §§3º–4º; LC 636/2010 art. 20 (6); art. 110 LC 434/99; Anexo 6 (código IA 33) (4); art. 110 LC 434/99; Anexo 6 (código IA 35) (4); art. 110 LC 434/99; Anexo 6 (código IA 31) (1); art. 110 LC 434/99; Anexo 6 (código IA 37) (1); Compilação PDDUA, nota ao art. 29 (LC 630/2009; LC 950/2022) (1); arts. 110–111 LC 434/99 (1); art. 111 LC 434/99 (1); arts. 51–53 e 110 LC 434/99; LC 1.022/2024 art. 6º (1); PDDUA arts. 22, 76; LC 636/2010; LC 1.022/2024 (1); art. 22 §3º LC 434/99; LC 1.022/2024 art. 1º §3º (1); art. 76 LC 434/99 (1) … (+2)
- **F02** (LC 434/1999, Anexo 4): Anexo 4, código 5; art. 66 LC 434/99 (29); Anexo 4, código 3; art. 66 LC 434/99 (25); Anexo 4, código 1; art. 66 LC 434/99 (19); Anexo 4, código 11; art. 66 LC 434/99 (16); Anexo 4, código 25 (13); Anexo 4, código 17; art. 66 LC 434/99 (10); Anexo 4, código 15; art. 66 LC 434/99 (9); Anexo 4, código 7; art. 66 LC 434/99 (9); Anexo 4, código 13; art. 66 LC 434/99 (8); Anexo 4, código 9; art. 66 LC 434/99 (8); Anexo 4, código 19; art. 66 LC 434/99 (6); Anexo 4, código 39 (4); Anexo 4, código 35; art. 66 LC 434/99 (3); Anexo 4, código 41 (2); Anexo 4, código 21; art. 66 LC 434/99 (1); Anexo 4, código 23 (1); Anexo 4, código 31; art. 66 LC 434/99 (1); Anexo 4, código 33; art. 66 LC 434/99 (1); Anexo 4, código 37; art. 66 LC 434/99 (1)
- **F03** (LC 434/1999, Anexo 5; Decreto nº 20.628/2020): Anexo 5.1 e Anexo 5.3 (Dec. 20.628/2020) (409); Anexo 5.1 e Anexo 5.5 (22); Anexo 5.5; Anexo 11.2 (12); Anexo 5.3; Anexo 8.1 nota (6); Anexo 11.2 (3)
- **F04** (LC 434/1999, Anexo 6): Anexo 6, código IA 25, nota (2); art. 85 LC 434/99 (38); Anexo 6, código IA 5; arts. 107–108 LC 434/99 (37); Anexo 6, código IA 5 (IA máximo); arts. 110–111 LC 434/99 (37); Anexo 6, código IA 5; art. 109 LC 434/99 (37); Anexo 6, código IA 11; arts. 107–108 LC 434/99 (19); Anexo 6, código IA 11 (IA máximo); arts. 110–111 LC 434/99 (19); Anexo 6, código IA 11; art. 109 LC 434/99 (19); Anexo 6, código IA 3; arts. 107–108 LC 434/99 (16); Anexo 6, código IA 3 (IA máximo); arts. 110–111 LC 434/99 (16); Anexo 6, código IA 3; art. 109 LC 434/99 (16); Anexo 6, código IA 15; arts. 107–108 LC 434/99 (15); Anexo 6, código IA 15 (IA máximo); arts. 110–111 LC 434/99 (15); Anexo 6, código IA 15; art. 109 LC 434/99 (15); Anexo 6, código IA 1; arts. 107–108 LC 434/99 (14); Anexo 6, código IA 1 (IA máximo); arts. 110–111 LC 434/99 (14); Anexo 6, código IA 1; art. 109 LC 434/99 (14); Anexo 6, código IA 9; arts. 107–108 LC 434/99 (13); Anexo 6, código IA 9 (IA máximo); arts. 110–111 LC 434/99 (13); Anexo 6, código IA 9; art. 109 LC 434/99 (13); Anexo 6, código IA 4; arts. 107–108 LC 434/99 (12) … (+38)
- **F05** (LC 434/1999, Anexo 7): Anexo 7.1, código volumetria 1; art. 113 LC 434/99 (156); Anexo 7.1, código 25, nota (4); LC 930/2021 (111); Anexo 7.1, código volumetria 11; art. 113 LC 434/99 (84); Anexo 7.1, código volumetria 5; art. 113 LC 434/99 (80); Anexo 7.1, código volumetria 15; art. 113 LC 434/99 (60); Anexo 7.1, código volumetria 9; art. 113 LC 434/99 (56); Anexo 7.1, código volumetria 21; art. 113 LC 434/99 (52); Anexo 7.1, código volumetria 3; art. 113 LC 434/99 (44); Anexo 7.1, código volumetria 17; art. 113 LC 434/99 (40); Anexo 7.1, código volumetria 3A; art. 113 LC 434/99 (24); Anexo 7.1, código volumetria 7; art. 113 LC 434/99 (16); Anexo 7.1, código volumetria 8; art. 113 LC 434/99 (16); Anexo 7.1, código volumetria 4; art. 113 LC 434/99 (12); Anexo 7.1, código volumetria 6; art. 113 LC 434/99 (8); Anexo 7.1, código volumetria 23; art. 113 LC 434/99 (4)
- **F06** (LC 434/1999, Anexo 8): Anexo 8.1 – Área predominantemente residencial e Mistas 1-4 (268); Anexo 8.1 (62); Anexo 8.1 – Área de proteção do ambiente natural (AOR) – 20 ha (nota 1) (22); Anexo 8.1 – Área predominantemente produtiva e Mista 5 (14); Anexo 8.1 nota (3) (13); Anexo 8.1 – Área de desenvolvimento diversificado (AOR) – 2 ha (3); Anexo 8.1 – Área de produção primária (AOR) – 2 ha (1); Anexo 8.1 (área máxima de quarteirão) e 8.2 (1)
- **F07** (LC 434/1999, Anexo 10; Decreto nº 20.385/2019): Anexo 10.1 folha 1 (Dec. 20.385/2019) (230)
- **F08** (LC 434/1999, Anexo 11): Anexo 11.2; Anexo 5.5 nota (1) (1); PDDUA arts. 55–61 e Anexo 11 (1); Anexo 11.1 (1); Anexo 11.2 (1)
- **F10** (Lei Complementar nº 1.076/2026): LC 1.076/2026 arts. 110–114 (1)
- **F13** (Lei Complementar nº 1.022/2024): LC 1.022/2024 arts. 1º §1º e 2º (1); LC 1.022/2024 art. 3º (1)
- **F14** (Decreto nº 22.932/2024): LC 1.022/2024 arts. 4º–5º; Dec. 22.932/2024 (1)
- **F15** (Lei Complementar nº 636/2010): LC 636/2010 art. 21 (7); LC 636/2010 art. 4º (1); LC 636/2010 arts. 10–28 (1)
- **F16** (Lei Complementar nº 548/2006): LC 548/2006 (1)
- **F18** (Lei Complementar nº 946/2022): PDDUA arts. 53, 110–111; LC 946/2022 (1); LC 946/2022 art. 5º (1); LC 946/2022 art. 6º e §3º (1); LC 946/2022 arts. 9–13 (1)
- **F21** (PMPA/SMAMUS): PDDUA art. 96 (notas: Portarias DECEA 957/2015, 260/2016); IN 07/2021 SMAMS (1); PDDUA art. 96 (nota RBAC 161/2011) (1); PDDUA art. 96 §3º; Lei Federal 12.651/2012 art. 4º (1); PDDUA art. 96 (notas) (1)
- **F22** (PMPA/SMAMUS): art. 29 LC 434/99 (1); LC 775/2015; Anexo 5.1 nota (**) (1); LC 601/2008; PDDUA arts. 92 e Anexo 11 (bens tombados/inventariados = Projeto Especial 1º grau) (1); Lei Federal 12.608/2012 (cartas de suscetibilidade) (1); Lei Federal 12.608/2012 (1); Lei Federal 9.985/2000; leis municipais de criação (1)
- **F23** (Lei Complementar nº 960/2022): LC 960/2022 (1)

## Zonas por categoria normalizada

| Categoria | Nº de combinações | Nº de subunidades |
|---|---|---|
| mista_media_densidade | 74 | 516 |
| especial_interesse_social | 6 | 350 |
| outra | 9 | 278 |
| patrimonio_cultural | 83 | 187 |
| residencial_media_densidade | 19 | 133 |
| ambiental | 11 | 130 |
| residencial_baixa_densidade | 7 | 94 |
| rural | 5 | 80 |
| mista_baixa_densidade | 7 | 57 |
| institucional | 7 | 42 |
| industrial | 4 | 14 |
| especial_economica | 3 | 12 |
| expansao | 1 | 3 |

## Regras de sobreposição

| Zona | Tipo | Prioridade | Efeito | Fundamento |
|---|---|---|---|---|
| 230 zonas base (subunidades) | base | 0 | — | regime por subunidade (PDDUA arts. 95–117, Anexos 4–7) |
| AEIS III – AEIS III | sobreposta | 40 | apenas_alerta | PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3) |
| AEIS – AEIS | sobreposta | 30 | apenas_alerta | PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3) |
| AEIS I – AEIS I | sobreposta | 30 | apenas_alerta | PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3) |
| AEIS I-II – AEIS I-II | sobreposta | 30 | apenas_alerta | PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3) |
| AEIS II – AEIS II | sobreposta | 30 | apenas_alerta | PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3) |
| AEIS IV – AEIS IV | sobreposta | 30 | apenas_alerta | PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3) |

## Resumo MCMV

- Maior potencial: subunidades com IA 19 (básico 2,4 → 3,0 com Solo Criado), IA 15/17 (1,9 → 3,0) e IA 11/13 (1,6 → 3,0), volumetria 09/11/13 (42–52 m) e densidade 15–19 (455–525 hab/ha) – concentradas nas MZ1–MZ3 (Cidade Radiocêntrica, Corredor de Desenvolvimento, Cidade Xadrez); terra mais cara.
- Equilíbrio MCMV: GA 05/07/09 (Mistas 02–04, habitação S/R) com IA 05–09 (1,3 → 2,0/3,0) e volumetria 05/07/09 (18–42 m), comuns na Cidade Xadrez (MZ3), Restinga (MZ7) e Eixo Lomba-Restinga (MZ6). Residencial em terreno com testada ≥ 12 m é isento de vagas (Anexo 10.1).
- Evitar: GA 13 (produtiva) – habitação proibida; GA 11 (Mista 05) – só por Projeto Especial de 2º grau; Área Rarefeita (densidade 31–37: 2–17 hab/ha, recuo de jardim 12 m) e Zona Rural; APP, setores de risco CPRM e suscetibilidade alta a inundação (camadas).
- AEIS: incentivos do PMCMV-POA (LC 636/2010) – vagas até 50% das UH, dispensa de quota ideal na Área Intensiva (art. 28), IPTU/ITBI, redução de doação em desmembramento; lote HIS 125 m²/5 m. Regime da AEIS por decreto – confirmar na DMI.
- LC 1.022/2024 (isenção de Solo Criado, de estoque e de volumetria para HIS) valeu apenas para projetos protocolados até 31/12/2025 – não conte com ela para novos projetos.
- Solo Criado: VSC = VMT × AC × FP / IA, FP = 1 (LC 946/2022); custo cresce com o valor da face de quarteirão – em áreas periféricas o Solo Criado é barato.
- Gatilhos de custo/prazo: terreno > 2,25 ha na Área Intensiva ou condomínio > 22.500 m² → Projeto Especial 1º grau; > 30.000 m² adensáveis ou > 400 vagas → 2º grau (EVU); bens inventariados/entorno de tombados; PBZPA (altura) perto do Salgado Filho.
- Transição: PDUS (LC 1.075/2026) e LUOS (LC 1.076/2026) sancionados em 14/07/2026 com regras a partir de 2027 (ZOT 1–16; ZOT 14 admite regime da ZOT 1 para HIS; OODC com isenção para HIS em faixas federais). Projetos protocolados antes podem ter direito ao regime antigo – verificar as regras de transição.

## Camadas geográficas

Servidor oficial: https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/ · CRS de área: EPSG:31982

| Camada | Arquivo bruto | Oficial | Método | Erro est. (m) | Feições | Download | URL |
|---|---|---|---|---|---|---|---|
| Regime urbanístico por subunidade (zonas base) | `geo_raw/pddua_regime.geojson` | sim | vetor oficial | None | 1547 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/PDDUA/FeatureServer/0 |
| AEIS (zonas sobrepostas) | `geo_raw/Shapefile_AEIS.zip` | sim | vetor oficial | None | 350 | 2026-10-27 | https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/Shapefile_AEIS.zip |
| Macrozonas | `geo_raw/macrozona.geojson` | sim | vetor oficial | None | 31 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer/77 |
| Zona Rural | `geo_raw/zona_rural.geojson` | sim | vetor oficial | None | 23 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer/76 |
| PBZPA/PZPANA/PBZPH (DECEA) | `geo_raw/Shapefile_PBZPA_PBZPH.zip` | sim | vetor oficial | None | 108 | 2026-10-27 | https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/Shapefile_PBZPA_PBZPH.zip |
| Zoneamento de ruído aeroportuário | `geo_raw/Shapefile_PBZPA_PBZPH.zip` | sim | vetor oficial | None | 20 | 2026-10-27 | https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/Shapefile_PBZPA_PBZPH.zip |
| APP de curso d'água (convencionada) | `geo_raw/Shapefile_APP.zip` | sim | vetor oficial | None | 139 | 2026-10-27 | https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/Shapefile_APP.zip |
| APP de topo de morro (convencionada) | `geo_raw/Shapefile_APP.zip` | sim | vetor oficial | None | 36 | 2026-10-27 | https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/Shapefile_APP.zip |
| Bens tombados e inventariados | `geo_raw/tombados_inventariados.geojson` | sim | vetor oficial | None | 1812 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer/141 |
| Suscetibilidade a inundação (CPRM) | `geo_raw/susc_inundacao.geojson` | sim | vetor oficial | None | 2216 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer/154 |
| Setores de risco (CPRM) | `geo_raw/risco_cprm.geojson` | sim | vetor oficial | None | 142 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer/152 |
| Unidades de conservação municipais | `geo_raw/unid_conservacao.geojson` | sim | vetor oficial | None | 4 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/POA___Consultas_MIL1/MapServer/114 |
| Programa +4D | `geo_raw/limite_4d.geojson` | sim | vetor oficial | None | 1 | 2026-10-27 | https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/Limite_Programa_4D_130326/FeatureServer/0 |

### Camadas complementares no JSON

- **macrozonas** (papel `macrozona`, 9 feições): Macrozonas do PDDUA (art. 29).
- **zona_rural** (papel `restricao`, 1 feições): Zona Rural (LC 775/2015) – parcelamento urbano e habitação multifamiliar não admitidos.
- **pbzpa** (papel `restricao`, 108 feições): Superfícies limitadoras de obstáculos dos aeródromos/helipontos (PBZPA, PZPANA, PBZPH) – limitam a altura das edificações.
- **ruido_aeroportuario** (papel `restricao`, 20 feições): Curvas do Plano (Específico) de Zoneamento de Ruído – PEZR/PZR dos aeródromos.
- **app** (papel `restricao`, 175 feições): Áreas de Preservação Permanente convencionadas pelo Município (Lei Federal 12.651/2012 art. 4º): cursos d'água e topos de morro.
- **patrimonio_cultural** (papel `restricao`, 1811 feições): Bens tombados, inventariados (estruturação/compatibilização) e entornos – LC 601/2008.
- **suscetibilidade_inundacao** (papel `restricao`, 3 feições): Cartas de suscetibilidade a inundação (CPRM/SGB, 2012–2014).
- **setores_risco** (papel `restricao`, 142 feições): Setores de risco alto e muito alto (CPRM/SGB) – inundação, deslizamento, enxurrada, erosão, queda, corrida.
- **unidades_conservacao** (papel `restricao`, 4 feições): Unidades de conservação municipais (Morro do Osso, Saint-Hilaire, Refúgio São Pedro, Reserva Biológica do Lami).
- **programa_4d** (papel `informativa`, 1 feições): Perímetro do Programa +4D de Regeneração Urbana do 4º Distrito (LC 960/2022) – regime próprio e incentivos; HIS isenta de Solo Criado se atendidos padrões de resiliência (LC 1.022/2024 art. 5º, p/ protocolos até 31/12/2025).

## Limitações

- Shapefiles da SMAMUS em TM-POA (SIRGAS 2000, MC -51°, k 0,999995, FE 300.000, FN 5.000.000), reprojetados com pyproj; erro < 1 m.
- Simplificação ~1 m (zonas) e ~2 m (macrozonas/manchas unidas); coordenadas com 6 casas.
- O arquivo "PDDUA_Shapefile.zip" da página Mapas Digitais contém, na verdade, o PBZPA (mesmo arquivo do Shapefile_PBZPA_PBZPH.zip); por isso o regime foi obtido do serviço ArcGIS Hosted/PDDUA.
- Base AEIS de 12/05/2022 e PBZPA/APP de 2021; servidor ArcGIS instável (erros 500 transitórios).
- Regime do Anexo 7.2 (por logradouro) não georreferenciado.

## Lacunas (não encontrado em fonte oficial – ficou `null`)

- **Códigos 99 (densidade), 99.99 (atividade), 999 (IA/volumetria), atividade 20 e 15.2**: Não constam dos Anexos 4–7 nem do dicionário PDDUA_Metadados; aparecem em AEIS e áreas de regime próprio. Parâmetros null – consultar a DMI.
- **Significado dos códigos OBS_1..OBS_5 das subunidades**: A tabela de observações não é publicada nos metadados; repassados como atributo obs_codigos.
- **CA mínimo**: O PDDUA vigente não fixa CA mínimo por zona.
- **Vagas para residencial em terreno com testada < 12 m**: O Anexo 10.1 (Dec. 20.385/2019) só trata testada ≥ 12 m (isento).
- **Regime volumétrico do Anexo 7.2 (logradouros com observações especiais)**: Depende da via de frente do lote; não vetorizado (só tabela por logradouro).
- **Regimes próprios do Centro Histórico (LC 930/2021 – gabarito) e do +4D (LC 960/2022)**: Leis específicas não transcritas; perímetro do +4D incluído como camada informativa.
- **Decretos de regime das AEIS (art. 76 §8º)**: Não há compilação pública única; AEIS tratadas como alerta com herança do regime base.
- **Prorrogação da LC 1.022/2024**: Nenhuma lei de prorrogação localizada no SAPL/DOPA até 27/10/2026.
- **LC 699/2012 e LC 722/2013 (alterações da LC 636/2010)**: Não lidas; confirmar redação vigente dos artigos citados.
- **Zoneamento da nova LUOS (Anexo 1 – ZOT)**: A camada pública Hosted/luos_anexo01_zot está vazia (0 feições) em 27/10/2026; a LUOS ainda não está vigente.
- **Áreas de Interesse Cultural (camada própria)**: Serviço Hosted/Áreas_de_Interesse_Cultural retornou erro do servidor; as áreas estão representadas nos GA 15.x/16.x das zonas base e na camada de tombados/inventariados.
- **Cota de inundação 5,35 m (2024) e mancha da cheia de 2024**: Camada Hosted/cota_535 não baixada (servidor instável); usar suscetibilidade CPRM como proxy.
- **Geometria da Macrozona 6 (Eixo Lomba-Restinga)**: Nem a camada de macrozonas (MapServer/77) nem as subunidades do regime trazem MZ 6 em 27/10/2026 (há MZ 10 – Lomba do Pinheiro); MZ6 mantida só como descrição legal do art. 29.
- **Gabarito em número de pavimentos**: O PDDUA controla altura em metros (Anexo 7.1), não em pavimentos.
- **Decreto 21.585/2022 e IN 006/2025 (procedimento do Solo Criado)**: Citados na compilação; textos não baixados.

## Conteúdo desta pasta

- `porto-alegre-rs.json` – dados no padrão da plataforma (schema 1.1).
- `fontes/` – cópias das leis, anexos e mapas oficiais (PDF/DOCX + texto extraído).
- `geo_raw/` – camadas brutas (GeoJSON EPSG:4326 do ArcGIS SMAMUS; shapefiles TM-POA da página Mapas Digitais).
- `scripts/` – `baixar_camadas.py` (download ArcGIS REST), `docx2txt.py`, `tabelas_pddua.py` (Anexos 4–8 transcritos), `build_poa.py` (monta o JSON), `gerar_referencias.py` (este arquivo).

Reprodução: `cd scripts && python3 baixar_camadas.py && python3 build_poa.py && python3 gerar_referencias.py && python3 ../../../validar_cidade.py porto-alegre-rs`.
