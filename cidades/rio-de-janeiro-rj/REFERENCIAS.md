# Rio de Janeiro-RJ – Referências do levantamento (27/10/2026)

## Leis e normas (fontes do JSON)
| id | norma | link |
|---|---|---|
| F01 | LC 270/2024 – Plano Diretor (PDDUS) com zoneamento/LUOS (Título V; Anexos XV, XVII, XVIII, XX, XXI, XXII, XXV) | https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/a99e317a9cfec383032568620071f5d2/0274835ddbc09b5303258aa700487674?OpenDocument |
| F03 | LC 274/2024 (altera LC 270) | https://aplicnt.camara.rj.gov.br/apl/Legislativos/contlei.nsf/66ff1c35b8d68ddd032578690069dda8/d57750a2ebbaaae003258b5d007275f3?OpenDocument |
| F04 | LC 281/2025 (altera LC 270/274) | https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C2812025.html (padrão do acervo; não aberto) |
| F05 | LC 291/2025 (Anexo XVII – FIS) | https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C2912025.html (padrão do acervo; não aberto) |
| F06 | LC 301/2026 – AEIU Praça Onze Maravilha; altera Anexo XXI AP2.2, LC 229 | https://desenvolvimentourbano.prefeitura.rio/praca-onze-maravilha/ |
| F07 | LC 229/2021 – Reviver Centro | https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C2292021.html |
| F08 | LC 101/2009 – OUC Porto Maravilha (CEPAC) | https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C1012009.html (padrão do acervo; não aberto) |
| F09 | Decreto 56.561/2025 – atividades (CNAE) × categorias de uso | https://desenvolvimentourbano.prefeitura.rio/wp-content/uploads/sites/52/2025/08/Decreto-Municipal-No.-56561-de-05-08-2025.pdf |

## Geografia (todas vetor oficial, sem login)
- F02 Zoneamento e macrozonas: https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Urbanismo/LBB_Zoneamento_urbano_vigente/MapServer (camadas 0 e 1)
- F10 Operações urbanas: …/IU_Operacoes_urbanas_temp (camada 59); F11 AEIS: …/LBB_AEIS (camada 1)
- F12 demais LBB (SMD, Q, gabaritos, APAC, APE, AEI, APP, áreas protegidas, zoneamento ambiental, CPA/PPA, Corredor Cultural, distritos/polos, setores/subsetores, IPTU progressivo) – URLs exatas em geo_raw/_log_download.json
- F13 item ArcGIS Online 23de66d35c394fc89a5c5bca844373b4 (caráter informativo; crédito SMDU)
- F14 Suscetibilidade a deslizamentos (raster, não usado)

## Como os dados foram obtidos
- `scripts/baixar_camadas.py` → `geo_raw/*.geojson` (paginação ArcGIS REST, outSR 4326) + `_log_download.json`.
- `scripts/build_rio.py` → `rio-de-janeiro-rj.json` (simplificação 2 m em EPSG:31983, 6 casas decimais).
- Zonas base = sigla da zona/subzona + AP (a tabela do Anexo XXI muda por AP); quando a mesma subzona tem parâmetros diferentes na mesma AP (trechos de logradouro, cotas), cria-se variante `v1, v2…`.
- Parâmetros por zona vêm dos atributos da camada oficial (transcrição SMDU do Anexo XXI); regras gerais (OODC, vagas, SMD, ZEIS, HIS, EIV) dos artigos da LC 270.

## AVISO sobre o texto legal
Os sites oficiais (Câmara, DOM/doweb, prefeitura.rio) bloqueiam o ambiente de levantamento. O WebFetch da Câmara retorna o LC 270 só até o art. 80; LC 274 foi lida integralmente no site da Câmara.
Os demais artigos da LC 270 (consolidada até a LC 301/2026) foram LIDOS numa compilação NÃO oficial (LegisWeb, `fontes/LC270_2024_TRANSCRICAO_NAO_OFICIAL_legisweb.txt`) e são citados pelo número do artigo da lei oficial (F01). A Fórmula 1 do Anexo XXV veio de um trecho de busca. **Confirmar no texto oficial antes de uso decisório.** Notas de pesquisa: `fontes/NOTAS_PESQUISA.md`.

## Reprodução (schema 1.1)
`python3 scripts/build_rio.py && python3 ../../schema/normalizar_cidade.py rio-de-janeiro-rj.json --compacto && python3 ../../validar_cidade.py rio-de-janeiro-rj` → APROVADO (0 erros, 0 avisos) em 27/10/2026. `categoria_normalizada` é atribuída no build (função `categoria`, critério em `categoria_criterio`).
