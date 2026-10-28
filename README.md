# Plataforma de zoneamento multicidades – parâmetros urbanísticos para MCMV

Este pacote traz **um JSON normalizado por cidade**, todos com a mesma estrutura (JSON Schema 1.1). Os dados vêm só de fontes oficiais públicas, e cada valor tem citação (lei, artigo/anexo, URL). Junto vêm um motor genérico de consulta por polígono e uma app Flask de exemplo. O conteúdo foi levantado em 27/10/2026.
O resultado é **indicativo**. Confirme sempre na prefeitura (consulta prévia / certidão de uso do solo) antes de qualquer decisão.

## Estrutura
```
README.md                 este arquivo
RESUMO_CIDADES.md         comparativo das 9 cidades (MCMV, HIS, alertas)
PADRAO_JSON.md            padrão do JSON (NORMALIZAÇÃO OBRIGATÓRIA no topo); a fonte de verdade é o schema
schema/
  cidade.schema.json      JSON Schema draft 2020-12 (schema_versao "1.1")
  README.md               como outra aplicação consome os dados (exemplo Python sem a app)
  normalizar_cidade.py    converte um JSON legado (1.0) para 1.1 sem inventar valores
  exemplos/consumir.py    exemplo executável
validar_cidade.py         validador: schema + checagens semânticas (fonte_id, geometrias, prioridades…)
gerar_status.py           tabela de status das cidades (markdown)
comum/                    utilitários compartilhados pelos scripts de coleta (OCR)
app/                      app Flask + motor.py (genérico: nada é específico por cidade)
testes/                   testes unitários/integração (cidade fictícia + Campo Grande) e e2e das 9 cidades
cidades/<slug>/
  <slug>.json             dados da cidade (parâmetros + geometrias EPSG:4326)
  REFERENCIAS.md          fontes, citações, lacunas e método geográfico
  scripts/                scripts que geraram o JSON (reprodutibilidade)
```
Ficaram fora do pacote, por serem pesadas, as pastas `fontes/` (PDFs/HTML das leis) e `geo_raw/` (downloads brutos de geodados). Os scripts as recriam a partir das URLs oficiais listadas em `fontes[]` e em `geografico.camadas[]`.

## Como rodar
```bash
pip install -r app/requirements.txt          # flask, shapely 2, pyproj, numpy, jsonschema
python3 validar_cidade.py --todas            # valida as 9 cidades (esperado: 9 APROVADO)
python3 testes/test_plataforma.py            # 16 testes, sem pytest
cd app && python3 app.py                     # http://127.0.0.1:5000
python3 testes/e2e/teste_9_cidades.py        # com a app rodando: 1 terreno por cidade + KMZ com 3 cidades
```
Na app:
- desenhe um ou mais polígonos, ou envie KML, KMZ ou GeoJSON (todos os polígonos do arquivo são analisados);
- a cidade é detectada automaticamente pelo centróide;
- a página inicial lista as cidades com status e link para `/referencias/<slug>`.

API:
- `POST /api/consulta`: corpo GeoJSON, opcional `?cidade=<slug>`;
- `POST /api/consulta-arquivo`: campo `arquivo`;
- `GET /api/cidades`;
- `GET /api/zonas/<slug>`;
- `GET /api/validar/<slug>`.

Variáveis de ambiente: `PLATAFORMA_CIDADES` (pastas de cidades, separadas por `:`), `HOST` e `PORT`.

Desempenho (box de teste, Rio de Janeiro com 18 MB e 594 zonas):
- cada cidade é carregada sob demanda (lazy) e indexada em STRtree no CRS métrico;
- a 1ª consulta no Rio leva ≈ 1,3 s (carga + índice) e as seguintes ≈ 20 ms;
- as demais cidades levam 0,07–0,55 s na 1ª consulta e 11–23 ms nas seguintes;
- a descoberta das cidades (validação + bbox) fica em cache em `app/.cache_descoberta.json`, invalidado por mtime/tamanho: a 1ª partida leva ≈ 7,5 s e as seguintes, ≈ 0 s.

## Como adicionar uma cidade nova (sem mudar código)
1. Crie `cidades/<slug>/` (slug = `municipio-uf` minúsculo, sem acento) com `<slug>.json`, `REFERENCIAS.md`, `scripts/`, `fontes/` e `geo_raw/`.
2. Gere o JSON seguindo `PADRAO_JSON.md`, cuja seção NORMALIZAÇÃO OBRIGATÓRIA resume as regras:
   - cada parâmetro é `{valor, unidade, fonte_id, artigo_anexo, observacao, forma}` ou `null`;
   - taxas em fração 0–1;
   - faixas, condicionais e fórmulas na estrutura definida;
   - `categoria_normalizada` em cada zona;
   - regras de sobreposição só por `tipo`, `prioridade` e `regra_sobreposicao`, e camadas extras por `papel`.
3. Se partiu de um JSON no formato antigo, rode `python3 schema/normalizar_cidade.py cidades/<slug>/<slug>.json --categorias Z1=mista_media_densidade,...`.
4. Rode `python3 validar_cidade.py <slug>` até dar APROVADO (0 erros) e reinicie a app. A cidade aparece sozinha: o motor não tem nenhuma regra por cidade.
5. Regras de dados:
   - só fontes oficiais públicas;
   - valor não encontrado fica `null` / `forma:"sem_dado"`, com o motivo em `lacunas`;
   - geometria digitalizada fica `oficial:false`, com o erro estimado.

## Status das 9 cidades
| Cidade | Zonas (base) | Geometria oficial (% área base) | Erro estimado | Levantamento | Lacunas | Fontes | JSON (MB) |
|---|---|---|---|---|---|---|---|
| Campo Grande/MS (`campo-grande-ms`) | 15 (7) | 100.0% | 2 m | 2026-10-27 | 13 | 32 | 1.8 |
| Curitiba/PR (`curitiba-pr`) | 76 (76) | 100.0% | – (vetor oficial) | 2026-10-27 | 16 | 18 | 3.6 |
| Fortaleza/CE (`fortaleza-ce`) | 61 (26) | 100.0% | 2 m | 2026-10-27 | 10 | 22 | 3.9 |
| Goiânia/GO (`goiania-go`) | 23 (21) | 59.9% | – (vetor oficial) | 2026-10-27 | 17 | 16 | 6.1 |
| João Pessoa/PB (`joao-pessoa-pb`) | 23 (20) | 0.0% | 1–35 m | 2026-10-27 | 14 | 16 | 6.8 |
| Porto Alegre/RS (`porto-alegre-rs`) | 236 (230) | 100.0% | – (vetor oficial) | 2026-10-27 | 15 | 26 | 8.0 |
| Recife/PE (`recife-pe`) | 27 (19) | 0.0% | 50–100 m | 2026-10-27 | 14 | 6 | 0.9 |
| Rio de Janeiro/RJ (`rio-de-janeiro-rj`) | 594 (420) | 100.0% | 2 m | 2026-10-27 | 10 | 14 | 18.3 |
| Salvador/BA (`salvador-ba`) | 36 (34) | 0.0% | 2–15 m | 2026-10-27 | 11 | 9 | 6.4 |

"Geometria oficial" é a % da área das zonas base que vem de vetor oficial. O resto é digitalização aproximada dos mapas oficiais das leis. Em Goiânia, a AAB foi derivada por diferença de vetores oficiais.

## Comparativo para MCMV (detalhe em RESUMO_CIDADES.md)
| Cidade | Zonas (base) | Qualidade geométrica | Zonas boas para MCMV | Incentivos HIS-chave | Alerta principal |
|---|---|---|---|---|---|
| **Campo Grande/MS** | 15 (7) | Vetor oficial (100%), ~2 m | Z3, Z4 e eixos EA1/EA2. Z5 só se estiver em ZEIS 2, que passa a usar os índices da Z4 | ZEIS 2: vagas reduzidas (MZ1 dispensável, MZ2 25%, MZ3 50%), UH ≤ 70 m², mitigações reduzidas e isenção de OODC para HIS (LC 469 art. 8º II) | Até a revisão, continuam valendo os arts. 22–63-D da LOUOS antiga (PDDUA art. 97). A isenção de OODC para HIS é ambígua. Acima de 100 UH exige EIV e audiência pública |
| **Curitiba/PR** | 76 (76) | Vetor oficial (100%), sem erro declarado | ZR4, EAC, EMF, EACF, ECL-3 e ECO-1..4 (CA até 2,5, com HIS COHAB 625 uh/ha). ZR3/ZUM/ZFR para 4–6 pavimentos. EE e ZC dão mais potencial, mas a terra é cara | Dec. 297/2026 (HIS com a COHAB-CT): isenção de OODC (Lei 16.361 art. 12), +1 pavimento, 1 vaga/4 UH, lote 125 m², densidade +20% perto do transporte. No centro, SERC/LC 150/2025 dá +CA e incentivos fiscais | O incentivo HIS exige UH para famílias do cadastro COHAB. Curitiba não tem "ZEIS" (usa SEHIS). Potencial adicional pago 50% em OODC e 50% em TDC (Lei 16.361/2024) |
| **Fortaleza/CE** | 61 (26) | Vetor oficial (100%), ~2 m | ZOP1 e ZO-IV (IA 3), ZOC, ZOP2 e ZEDUS. ZRU1/ZRU2/ZOM2 nas periferias típicas de MCMV | Fração do Lote de 30 m²/UH para HIS MCMV até 6 SM, dispensada se houver esgoto CAGECE. EHIS isento de OODC. LC 359/2023: ITBI, ISS da obra, taxas e IPTU por 5 anos | **Novo PDPS (LC 450/2025) entra em vigor ≈ maio/2027** (LC 461/2026). Acima de 300 UH é Projeto Especial |
| **Goiânia/GO** | 23 (21) | Vetor oficial. A AAB (40% da área) foi derivada por diferença de vetores oficiais (~1–5 m) | AEIS III (IA 2, 1 UH/30 m², 1 vaga/3 UH). AAB (HIS: IA 2, 12 m ≈ 4 pavimentos, TO 100%). AA nos eixos (IA 6, sem altura máxima), mas a terra é cara | LC 379/2024: isenção de OODC e de ITBI (FAR/FDS/FNHIS), 1 vaga/3 UH, fração 30–45 m² | TDC suspensa para novas concessões até 2027 (sem IA 7,5 na AA). Evitar AOS/APA/APAC e Macrozonas Rurais |
| **João Pessoa/PB** | 23 (20) | **Aproximada** (vetorização de PDF; 1–35 m), exceto as ZEIS 2 de 2025 | ZH-2 (maior zona; TO 50–55%, 3–4 pavimentos), ZH-1 a ZH-5, ZCS-1 a ZCS-5. Novas ZEIS 2 Democracia e Rio Sanhauá | Dec. 10.560/2024: HIS de 25–70 m², vagas para 20% das UH. ZEIS 2 de 2025 com parâmetros próprios | **Lei de regulamentação da OODC não localizada**: o IA acima de 1 depende dela. Orla limitada a 12,90–35 m. Geometria aproximada |
| **Porto Alegre/RS** | 236 (230) | Vetor oficial (100%), sem erro declarado | GA 05/07/09 (Mistas 02–04) com IA 05–09 e volumetria 18–42 m (Cidade Xadrez, Restinga, Lomba-Restinga). Residencial com testada ≥ 12 m é isento de vagas | AEIS e PMCMV-POA (LC 636/2010): vagas até 50%, IPTU/ITBI, doação reduzida, lote 125 m². Solo Criado barato na periferia | **PDUS (LC 1.075/2026) e LUOS (LC 1.076/2026), sancionados em 14/07/2026, com regras a partir de 2027.** A isenção da LC 1.022/2024 valeu só para protocolos até 31/12/2025 |
| **Recife/PE** | 27 (19) | **Aproximada** (cor do raster + grade UTM; **50–100 m**) | Multifamiliar permitido em todas as zonas. ZAC/ZRU/ZEC com CA máximo até 5. ZEIS 2 com CA máximo 4 | **Sem mínimo de vagas** (art. 175). HIS: IAC 0,75 não computável, dispensa de TCA, TO 50% acima do 4º pavimento, blocos até 80 m, EIV só acima de 30.000 m² na MAC | **LPUOS nova (Lei 19.426/2025)**, com mapas só em raster. Plano Diretor e lei de OODC não acessados. Erro geométrico alto: confirme o lote na prefeitura |
| **Rio de Janeiro/RJ** | 594 (420) | Vetor oficial (100%), ~2 m | ZRM1/2/3, ZUM, ZCC e ZCS, sobretudo na **AP3 (Zona Norte)**: CAM +50% para HIS e nos eixos de trem/metrô/BRT. ZRU não admite multifamiliar | **OODC sem cobrança até jan/2029** (art. 110), com AP1/AP3 isentas durante a LC 270. Sem exigência de vagas fora da AP4/AP5. +20% de ATE com ≥ 20% de Locação Social na AP3 | ZEIS (zona base) limitadas a 2 pavimentos até regulamentação. EIV ainda sem lei. A partir de 2029 a OODC volta em transição de 20% ao ano |
| **Salvador/BA** | 36 (34) | **Aproximada** (digitalização do mapa oficial; 2–15 m) | ZCMe (CAM 4; quota ≤ 25 m²/UH em ZCMe-1/02, 1/03 e 2), ZCLMe, ZPR-3, ZCMu-2, ZCLMu e ZEIS-1/2/3 (CAM 3). EHIS permitido em quase todas as zonas | HIS atinge o CAM **sem OODC** (FS = 0). 1 vaga/2 UH (UH < 50 m² isentas). Lote 125 m² em qualquer zona | **Lei 9.774/2023 alterou a LOUOS**, e não foi possível confirmar se o Mapa 01A a incorpora: faça consulta prévia na SEDUR. ZEIS > 1.500 m² exigem ≥ 50% em HIS-1 |
