# Recife-PE – Referências

Levantamento: 2026-10-27 · schema 1.1 · validar_cidade.py: APROVADO

## Marco legal vigente

Lei de Parcelamento, Uso e Ocupação do Solo – LPUOS: Lei nº 19.426, de 02/10/2025 (DOM nº 125, 04/10/2025; vigência 60 dias após a publicação), que revogou a Lei 16.176/1996. Plano Diretor: Lei Complementar nº 02/2021 (não acessada). Instrumentos: OODC Lei 18.900/2022; TDC Lei 18.901/2022 (não acessadas). Vigentes em 27/10/2026.

## Fontes oficiais

| id | lei | título | link | arquivo local |
|---|---|---|---|---|
| F01 | Lei nº 19.426/2025 | Lei de Parcelamento, Uso e Ocupação do Solo do Recife (LPUOS) – publicação no Diário Oficial | https://e-processo.recife.pe.leg.br/sapl_documentos/norma_juridica/2159_anexo_2179 | fontes/Lei19426_2025_DOM_publicacao.pdf |
| F02 | Câmara Municipal do Recife – Comissão de Redação | PLE nº 16/2025 – Parecer Final de Redação nº 75/2025 (texto aprovado com todos os anexos) | https://e-processo.recife.pe.leg.br/sapl_documentos/parecer_comissao/4081_parecer.pdf | fontes/PLE16_2025_Parecer_Redacao_Final_75_2025.pdf |
| F03 | Projeto de Lei do Executivo nº 16/2025 | PLE nº 16/2025 – proposição original do Executivo com anexos (mapas em maior resolução) | https://e-processo.recife.pe.leg.br/sapl_documentos/proposicao/61535_signed.pdf | fontes/PLE16_2025_LPUOS_proposicao_com_anexos.pdf |
| F04 | Câmara Municipal do Recife | Parecer da Comissão Especial (CELPUOS) nº 1/2025 ao PLE 16/2025 – emendas | https://e-processo.recife.pe.leg.br/sapl_documentos/parecer_comissao/3689_parecer.pdf | fontes/PLE16_2025_Parecer_CELPUOS_1_2025.pdf |
| F05 | Câmara Municipal do Recife | Tramitação do PLE 16/2025 (matéria) – sanção e publicação | https://e-processo.recife.pe.leg.br/consultas/materia/materia_mostrar_proc?cod_materia=MTYzNjMx | - |
| F06 | Lei nº 18.900/2022 | Regulamenta a Outorga Onerosa do Direito de Construir (OODC) – arts. 98, VI e 115 a 123 do Plano Diretor | https://licenciamentounificado.recife.pe.gov.br/189002022 | - |

Observações das fontes:

- **F01**: Sancionada em 02/10/2025; DOM do Recife nº 125, 04/10/2025 (pp. 3–12: texto e Anexo I). Vigência 60 dias após a publicação (art. 204). Página da norma: https://e-processo.recife.pe.leg.br/consultas/norma_juridica/norma_juridica_mostrar_proc?cod_norma=2159 . Texto integral (PDF com OCR): https://e-processo.recife.pe.leg.br/pysc/download_norma_pysc?cod_norma=2159&texto_original=1 (fontes/Lei19426_2025_LPUOS.pdf).
- **F02**: Redação final aprovada em 23/09/2025 e enviada à sanção (Ofício 386/2025-CMR). Contém os Anexos II (mapas, versão final SETEMBRO/2025 para 3A/3B/3C) a XX como aprovados. Usado para os quadros dos Anexos IV, XV e XVIII (texto extraído em fontes/LPUOS_texto_aprovado_limpo.txt). Numeração de artigos idêntica à do DOM.
- **F03**: Mapas do Anexo II datados MAIO/2025 (1213x1710 px). Usados para Mapas 1, 2, 4 e 6 (idênticos aos da redação final) e como referência de registro para 3A/3B/3C.
- **F04**: Aprovação com emendas, subemendas e emendas de relatoria.
- **F05**: Registro de 06/10/2025: "LEI Nº 19.426/2025, SANCIONADO EM 02/10/2025, PUBLICADA NO DIÁRIO OFICIAL DO MUNICÍPIO Nº 125, DE 04/10/2025" (https://e-processo.recife.pe.leg.br/sapl_documentos/materia/tramitacao/475360_tram.pdf).
- **F06**: Página oficial do Licenciamento Unificado (DO Recife nº 040, 24/03/2022). NÃO acessível do ambiente de coleta (todos os hosts *.recife.pe.gov.br recusam a conexão); conteúdo não verificado – citada apenas porque a LPUOS remete a ela (arts. 116 §4º e 168).

## Zonas

| código | tipo/prior. | categoria | CA mín/bás/máx | TO | gabarito (m) | TSN | recuo frontal | área (ha) |
|---|---|---|---|---|---|---|---|---|
| ZAN-ORLA | base/0 | ambiental | nao_aplicavel/1/1 | nao_aplicavel | demais lotes: nao_aplicavel; lote lindeiro à Av. Boa Viagem (art. 122, I; Obs. 4) – dispensado com fachada ativa (art. 122 p.ú.): 42.0 | terreno < 500 m²: 0.4; 500 m² ≤ terreno < 2.000 m²: 0.5; terreno > 2.000 m²: 0.5 | nao_aplicavel | 140 |
| ZAN-CAPIBARIBE | base/0 | ambiental | nao_aplicavel/1/1 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.4; 500 m² ≤ terreno < 2.000 m²: 0.5; terreno > 2.000 m²: 0.5 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 2248 |
| ZAN-TEJIPIO | base/0 | ambiental | nao_aplicavel/1/1 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.4; 500 m² ≤ terreno < 2.000 m²: 0.5; terreno > 2.000 m²: 0.5 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 1629 |
| ZAN-BEBERIBE | base/0 | ambiental | nao_aplicavel/1/1 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.4; 500 m² ≤ terreno < 2.000 m²: 0.5; terreno > 2.000 m²: 0.5 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 5111 |
| ZDS-BEBERIBE | base/0 | mista_media_densidade | 0.1/1/2 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.3; 500 m² ≤ terreno < 2.000 m²: 0.4; terreno > 2.000 m²: 0.5 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 883 |
| ZDS-CAPIBARIBE-A | base/0 | mista_media_densidade | 0.1/1/2 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m: nao_aplicavel | demais lotes: 26.0; lote lindeiro ao Rio Capibaribe (art. 122, II; Obs. 3): 24.0 | terreno < 500 m²: 0.3; 500 m² ≤ terreno < 2.000 m²: 0.55; terreno > 2.000 m²: 0.6 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: nao_aplicavel | 484 |
| ZDS-CAPIBARIBE-B | base/0 | mista_media_densidade | 0.1/1/2 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | 51.0 | terreno < 500 m²: 0.3; 500 m² ≤ terreno < 2.000 m²: 0.45; terreno > 2.000 m²: 0.5 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 284 |
| ZDS-CAPIBARIBE-C | base/0 | mista_media_densidade | 0.1/1/2 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | demais lotes: nao_aplicavel; lote lindeiro ao Rio Capibaribe (art. 122, II; Obs. 3): 24.0 | terreno < 500 m²: 0.3; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.3 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 1227 |
| ZDS-TEJIPIO | base/0 | mista_media_densidade | 0.1/1/2 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.3; 500 m² ≤ terreno < 2.000 m²: 0.3; terreno > 2.000 m²: 0.3 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 2769 |
| ZDS-CENTRO | base/0 | mista_media_densidade | 0.1/1/2 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | demais lotes: nao_aplicavel; lote lindeiro ao Rio Capibaribe (art. 122, II; Obs. 3): 24.0 | terreno < 500 m²: 0.3; 500 m² ≤ terreno < 2.000 m²: 0.3; terreno > 2.000 m²: 0.3 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 977 |
| ZONA-CENTRO | base/0 | centralidade | 0.5/1/5 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.1; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | edificação até 8 pav e 26 m: 3.0; edificação acima de 8 pav ou 26 m: 3.0 | 480 |
| ZRU-1-A | base/0 | mista_alta_densidade | 0.4/1/5 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.15; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 1683 |
| ZRU-1-B | base/0 | mista_alta_densidade | 0.4/1/5 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | 65.0 | terreno < 500 m²: 0.15; 500 m² ≤ terreno < 2.000 m²: 0.25; terreno > 2.000 m²: 0.25 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 54 |
| ZRU-1-C | base/0 | mista_alta_densidade | 0.4/1/5 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.15; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 147 |
| ZAC-PLANICIE-1-A | base/0 | mista_alta_densidade | 0.3/1/4 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | 65.0 | terreno < 500 m²: 0.2; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.25 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 99 |
| ZAC-PLANICIE-1-B | base/0 | mista_alta_densidade | 0.3/1/4 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.2; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.25 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 497 |
| ZAC-PLANICIE-2 | base/0 | mista_alta_densidade | 0.1/1/4 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.2; 500 m² ≤ terreno < 2.000 m²: 0.25; terreno > 2.000 m²: 0.25 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 1872 |
| ZAC-MORRO | base/0 | mista_baixa_densidade | 0.1/1/1.5 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.15; 500 m² ≤ terreno < 2.000 m²: 0.15; terreno > 2.000 m²: 0.2 | edificação até 8 pav e 26 m: 3.0; edificação acima de 8 pav ou 26 m: 7.0 | 1902 |
| ZAC-ORLA | base/0 | mista_media_densidade | 0.3/1/3 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | demais lotes: nao_aplicavel; lote lindeiro à Av. Boa Viagem (art. 122, I; Obs. 4) – dispensado com fachada ativa (art. 122 p.ú.): 42.0 | terreno < 500 m²: 0.2; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 343 |
| ZEIS-1-PLANICIE | sobreposta/20 | especial_interesse_social | 0.5/1/2 | sem_dado | sem_dado | terreno < 500 m²: 0.1; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | sem_dado | 1548 |
| ZEIS-1-MORRO | sobreposta/20 | especial_interesse_social | 0.3/1/2 | sem_dado | sem_dado | terreno < 500 m²: 0.1; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | sem_dado | 1609 |
| ZEIS-2 | sobreposta/20 | especial_interesse_social | 0.5/1/4 | sem_dado | sem_dado | terreno < 500 m²: 0.1; 500 m² ≤ terreno < 2.000 m²: 0.2; terreno > 2.000 m²: 0.2 | sem_dado | 77 |
| ZEC-1 | sobreposta/15 | centralidade | 0.5/1/5 | edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais: 1 - TSN_minima(Anexo XVIII); edificação acima de 8 pav ou 26 m – pavimentos acima do 4º: 0.4 | nao_aplicavel | terreno < 500 m²: 0.15; 500 m² ≤ terreno < 2.000 m²: 0.15; terreno > 2.000 m²: 0.2 | edificação até 8 pav e 26 m: 5.0; edificação acima de 8 pav ou 26 m: 7.0 | 149 |
| ZEPH-SPS | sobreposta/30 | patrimonio_cultural | sem_dado/sem_dado/sem_dado | sem_dado | sem_dado | sem_dado | sem_dado | 1106 |
| ZEPH-SPM | sobreposta/30 | patrimonio_cultural | sem_dado/sem_dado/sem_dado | sem_dado | sem_dado | sem_dado | sem_dado | 6 |
| ZEPH-SPPI | sobreposta/30 | patrimonio_cultural | sem_dado/sem_dado/sem_dado | sem_dado | sem_dado | sem_dado | sem_dado | 18 |
| ZEPH-SPA | sobreposta/30 | patrimonio_cultural | herda_da_base/herda_da_base/herda_da_base | sem_dado | ZEPH Sítio Trindade SPA-1: 13.0; ZEPH Sítio Trindade SPA-2: 26.0; ZEPH Apipucos SPA-1: 7.0; ZEPH Apipucos SPA-2: 10.0; ZEPH Benfica SPA-1: 10.0; ZEPH Benfica SPA-2: 26.0; ZEPH Capunga SPA-1: 13.0; ZEPH Capunga SPA-2: 7.0; ZEPH Poço da Panela SPA-1: 7.0; ZEPH Poço da Panela SPA-2: 13.0; ZEPH Poço da Panela SPA-3: 38.0; ZEPH Ponte d’Uchoa SPA: 13.0; ZEPH Várzea SPA: 7.0; ZEPH Santo Antônio e São José SPA: 13.0; ZEPH Casa de Ferro SPA: 13.0; ZEPH Casarão do Barbalho SPA: 13.0; ZEPH Escola Rural Alberto Torres SPA: 13.0; ZEPH Faculdade de Direito SPA: 26.0; ZEPH Hospital Pedro II SPA: 26.0; ZEPH Igreja das Fronteiras SPA: 7.0; ZEPH Igreja de Santo Amaro das Salinas/Cemitério dos Ingleses SPA: 7.0; ZEPH Soledade SPA: 26.0; ZEPH Derby SPA: 26.0; ZEPH Sobrado da Madalena SPA: 13.0; ZEPH Fábrica da Tacaruna SPA: 7.0; ZEPH Matadouro de Peixinhos SPA: 13.0; ZEPH Arraial Novo do Bom Jesus SPA: 13.0; ZEPH Dois Irmãos SPA: 13.0; ZEPH Praça Ministro Salgado Filho SPA: 16.0; ZEPH Cotonifício da Torre SPA: 16.0 | sem_dado | sem_dado | 255 |

Comuns a todas as zonas base: lote mínimo 125 m² e testada 5 m (art. 58); usos habitacional (uni/multifamiliar), não habitacional e misto em qualquer zona, salvo atividades restritas/proibidas (arts. 98–102); sem mínimo de vagas (art. 175); sem densidade máxima.

## Resumo MCMV

- Multifamiliar (isolado ou conjunto) é permitido em todas as zonas – não há lista de usos por zona; só atividades restritas/proibidas são controladas (arts. 98–102).
- CA básico 1 em toda a cidade; máx 2 na MANC (ZDS) e 1,5–5 na MAC (ZAC Planície 4, ZRU 1/Zona Centro/ZEC 1: 5); acima do básico paga-se OODC (Lei 18.900/2022 – não acessada). ZEIS 2: CA máx 4.
- Sem exigência mínima de vagas para nenhum uso (art. 175) – grande vantagem para HIS/MCMV.
- HIS: IAC 0,75 (áreas comuns não computáveis, conversíveis em privativa – art. 115); dispensa de TCA e parâmetros do espaço público se o programa (MCMV) exigir (art. 164); TO 50% acima do 4º pav com fachada ativa; blocos até 80 m (art. 145).
- EIV: HIS na MAC só acima de 30.000 m² construídos (demais: 20.000 m²); na MANC, 15.000 m² (Anexo XV).
- Cota-parte impõe nº MÍNIMO de UH em terrenos ≥1.500 m² na Zona Centro (30 m²/UH), ZRU 1-A (30), ZRU 1-B (35) e ZEC 1 (40) – favorece unidades compactas.
- TO: 100% − TSN até 8 pav/26 m; acima, 40% nos pavimentos acima do 4º. TSN mínima de 10–60% conforme zona e tamanho do lote (Anexo XVIII); ZEIS 10–20%.
- Gabarito livre na maior parte da cidade; limites: ZDS Capibaribe A 26 m/8 pav, B 51 m/16 pav, ZRU 1-B e ZAC Planície 1-A 65 m/20 pav; 42 m na Av. Boa Viagem e 24 m às margens do Capibaribe (art. 122).
- Lote mínimo 125 m² e testada 5 m (art. 58); em ZEIS os lotes seguem o plano urbanístico (art. 62).
- Centro: HIS pública na Zona Centro/ZDS Centro com as condições do art. 168; IEIS (imóveis subutilizados para HIS) com ampliação não computável e análise prioritária (arts. 26–30).

## Outorga onerosa

OODC regida pelo Plano Diretor (LC 02/2021, arts. 115–123) e pela Lei 18.900/2022 (ambos em hosts da Prefeitura inacessíveis do ambiente de coleta). A LPUOS fixa, por zona, CA mínimo/básico (1 em todas)/máximo (Anexo IV), e regras especiais: ZRU 1 Setor C e ZEC 1 Praça de Boa Viagem/Encruzilhada com faixas de CA condicionadas a retrofit em ZEPH (arts. 20-A, 20-B, 168). Fórmula de contrapartida não verificada.

- **CA básico (todas as zonas)** (F02, Lei 19.426/2025, Anexo IV – Parâmetros Urbanísticos de Ocupação (redação final, Parecer 75/2025 pp. 102–106)): 1 
- **CA máximo por zona** (F02, Lei 19.426/2025, Anexo IV – Parâmetros Urbanísticos de Ocupação (redação final, Parecer 75/2025 pp. 102–106)): ZAN (todas): 1; ZDS (todas): 2; Zona Centro: 5; ZRU 1 (A, B, C): 5; ZAC Planície 1 e 2: 4; ZAC Morro: 1.5; ZAC Orla: 3; ZEIS 1: 2; ZEIS 2: 4; ZEC 1: 5 Potencial entre o básico e o máximo adquirido por OODC/TDC.
- **Lei específica da OODC** (F06, Lei 18.900/2022): Citada pela LPUOS (arts. 116 §4º e 168); texto não acessado – ver lacunas.
- **ZRU 1 Setor C – potencial condicionado a retrofit em ZEPH** (F01, Lei 19.426/2025, art. 168): CA 1 → 3: texto; CA 3 → 5: texto Fatores de Planejamento e de Interesse Social da ZRU 1; OODC da faixa 3→5 isenta nos 5 primeiros anos de vigência; habite-se do retrofit (emitido desde 01/01/2025) é condição do habite-se na ZRU 1-C.
- **HIS pública na Zona Centro e ZDS Centro** (F01, Lei 19.426/2025, art. 168 §2º): Áreas privativas habitacionais de empreendimentos públicos de HIS na Zona Centro e ZDS Centro recebem a mesma condição do art. 168.
- **ZEC 1 Praça de Boa Viagem – Setor B** (F01, Lei 19.426/2025, art. 20-A): CA 1→3 via OODC; 3→5 OODC + retrofit (art. 168). Setor A: OODC.
- **ZEC 1 Encruzilhada – Setor B** (F01, Lei 19.426/2025, art. 20-B): CA 1→4 via OODC; 4→5 OODC + retrofit. Setor A: OODC.
- **Bônus por certificação ambiental** (F01, Lei 19.426/2025, art. 116, II e §1º; Anexo XVI): 0.1 Até 10% de área privativa não computável conforme categoria do certificado; perda da certificação → multa equivalente ao dobro da OODC (§4º).
- **Áreas não computáveis no CA** (F01, Lei 19.426/2025, arts. 114, 116, 118, 151): Áreas de parâmetros qualificadores do espaço público (fachada ativa, térreo visitável, fruição pública), áreas privativas descobertas, jardineiras ≤1 m, áreas comuns até o IAC, bicicletários.
- **Transferência do Direito de Construir** (F01, Plano Diretor (LC 02/2021) / Lei 18.901/2022): A LPUOS não regula a TDC; lei específica não acessada – ver lacunas.

## ZEIS / HIS

ZEIS 1 (Planície/Morro – regularização via PREZEIS, Lei 16.113/1995) e ZEIS 2 (vazios para HIS, art. 65 do PD); 117 ZEIS no Anexo III, 16 criadas e 2 ampliadas pela LPUOS. Anexo IV fixa só CA (ZEIS 1: máx 2; ZEIS 2: máx 4) e IAC; o resto segue o plano de cada ZEIS. Incentivos HIS: IAC 0,75 convertível em área privativa não computável, dispensa de TCA e de parâmetros do espaço público quando exigido por programa habitacional (ex.: MCMV), TO 50% acima do 4º pav com fachada ativa, blocos até 80 m, EIV só acima de 30.000 m² na MAC, sem mínimo de vagas.

- **Tipos de ZEIS** (F01, Lei 19.426/2025, arts. 11–14): ZEIS 1 (Planície e Morro): assentamentos de baixa renda – PREZEIS (Lei 16.113/1995). ZEIS 2: art. 65 do PDMR, parâmetros na LPUOS/PD e leis específicas (art. 14).
- **ZEIS listadas no Anexo III** (F02, Lei 19.426/2025, Anexo III): 117 Contagem automática do texto: 73 ZEIS 1 Planície, 13 ZEIS 1 Morro, 31 ZEIS 2.
- **ZEIS 1 criadas pela LPUOS** (F01, Lei 19.426/2025, art. 15): 16 Beira Rio, Chamego, Clotilde de Oliveira, Córrego da Fortuna, Curral Torrões, Feira Velha do Cordeiro, Rosarinho, Santa Luzia, Santa Marta, Sete Mocambos, Sítio dos Pintos, Sítio do Forte/Coreia, Vacaria, Vila Brasil, Vila Sul, Vilas Boas e Nova Conquista. Ampliadas: Aritana e Vila Esperança/Cabocó (art. 16).
- **CA nas ZEIS** (F02, Lei 19.426/2025, Anexo IV – Parâmetros Urbanísticos de Ocupação (redação final, Parecer 75/2025 pp. 102–106)): ZEIS 1 Planície – mín/bás/máx 0,5/1/2: 2; ZEIS 1 Morro – mín/bás/máx 0,3/1/2: 2; ZEIS 2 – mín/bás/máx 0,5/1/4: 4 
- **Índice de Áreas Comuns para HIS** (F01, Lei 19.426/2025, art. 115; Anexo IV Obs. 1): 0.75 Pode ser convertido em área privativa não computável se o total ≤ CA máx + IAC e as áreas comuns ≥ 0,30 do CA máx (art. 115, I–II; art. 116, V).
- **Dispensa de TCA e parâmetros do espaço público** (F01, Lei 19.426/2025, art. 164): HIS pode ser dispensada da Taxa de Contribuição Ambiental e dos parâmetros de qualificação do espaço público quando exigido por regras de programa público de financiamento habitacional (memorial justificativo).
- **TO acima do 4º pav para HIS com fachada ativa** (F01, Lei 19.426/2025, art. 145, III): 0.5 Edificações com mais de 8 pav; demais usos 45% (art. 145, II); padrão 40%.
- **Comprimento máximo de bloco em HIS (com fachada ativa)** (F01, Lei 19.426/2025, art. 145, IV): 80 
- **Limiar de EIV para HIS na MAC** (F02, Lei 19.426/2025, Anexo XV): 30000 Área total de construção; regra geral MAC 20.000 m² (exceto HIS) e MANC 15.000 m².
- **Vagas mínimas** (F01, Lei 19.426/2025, art. 175): 0 Sem mínimo de vagas para qualquer uso.
- **Compartimentos de HIS** (F01, Lei 19.426/2025, art. 200): Até a revisão da Lei 16.292/1997, dimensões, iluminação e ventilação de HIS seguem normas ABNT, dispensadas as tabelas do Anexo II daquela lei.
- **Imóveis Especiais de Interesse Social (IEIS)** (F01, Lei 19.426/2025, arts. 26–30; Anexo VI): Imóveis subutilizados classificados por decreto/lei (até 5 anos) para HIS; ampliação para HIS não computada no CA, análise prioritária e assistência técnica.
- **HIS pública no Centro** (F01, Lei 19.426/2025, art. 168 §2º): Mesmas condições do art. 168 para HIS pública na Zona Centro e ZDS Centro.
- **HIS em áreas de equipamentos públicos** (F01, Lei 19.426/2025, art. 51): Implantação integrada de HIS (locação social) em áreas destinadas a equipamentos públicos, sempre que tecnicamente possível.
- **Percentuais de usos em ZEIS** (F01, Lei 19.426/2025, art. 111): Remete ao art. 74 do Plano Diretor (não acessado).
- **Definição de HIS (faixa de renda)** (None, None): Não definida na LPUOS; depende do PD/PLHIS (Lei 18.863/2021) – não acessados.

## Outros parâmetros (EIV, gabaritos especiais etc.)

EIV para Empreendimentos de Impacto (Anexo XV: MANC >15.000 m², MAC >20.000 m², HIS na MAC >30.000 m² e atividades listadas); PGV/PGT com Estudo de Tráfego; gabaritos de 42 m na Av. Boa Viagem e 24 m às margens do Capibaribe; cota-parte; isenção de parâmetros para obras pequenas; vigência e transição.

- **Empreendimentos de Impacto / EIV** (F02, Lei 19.426/2025, arts. 109–110; Anexo XV): MANC – área total de construção >: 15000; MAC – área total de construção > (exceto HIS): 20000; HIS na MAC – área total de construção >: 30000 Também: aterros, autódromos, cemitérios, centrais de carga, depósitos de inflamáveis, indústrias ≥1.000 m², ETA/ETE, estádios, presídios, shoppings, terminais, OUC e obras viárias de grande porte.
- **Polos Geradores de Viagens/Tráfego** (F01, Lei 19.426/2025, arts. 104–108): Definidos no Manual de Estudo de Tráfego (Lei 18.887/2021); se também empreendimento de impacto, o Estudo de Tráfego integra o EIV.
- **Gabarito em lotes lindeiros à Av. Boa Viagem** (F01, Lei 19.426/2025, art. 122, I): 42 Dispensado com fachada ativa (art. 122 p.ú.).
- **Gabarito em lotes lindeiros ao Rio Capibaribe** (F01, Lei 19.426/2025, art. 122, II): 24 
- **Dispensa de cota-parte** (F01, Lei 19.426/2025, art. 119 §2º): 1500 Terrenos menores que 1.500 m² dispensados da cota-parte (nº mínimo de UH).
- **Isenção de parâmetros para obras pequenas** (F01, Lei 19.426/2025, art. 163): Até 400 m² construídos, até 2 pav, lote ≤500 m², TSN ≥20% e demais requisitos: desobrigadas dos parâmetros de ocupação.
- **Fachada ativa / térreo visitável / fruição pública** (F01, Lei 19.426/2025, arts. 143–151): Áreas não computáveis; faixa de amenização 2 m; TO 45% acima do 4º pav; ZRU 1-B sem gabarito.
- **Conversão de garagens em UH** (F01, Lei 19.426/2025, art. 167): Edificações regularizadas podem converter estacionamento em UH, isento de CA até o básico e de cota-parte.
- **Plano de Quadra** (F01, Lei 19.426/2025, arts. 169–170): Redistribuição de parâmetros entre lotes da quadra por decreto, com anuência de todos os proprietários.
- **Reservatório de retardo/acúmulo de águas pluviais** (F01, Lei 19.426/2025, art. 129, III): Parâmetro de qualificação ambiental (ver arts. 133 e seguintes).
- **Vigência da LPUOS** (F01, Lei 19.426/2025, art. 204): Publicada no DOM de 04/10/2025; entra em vigor 60 dias após a publicação (≈03/12/2025). Vigente em 27/10/2026.
- **Transição** (F01, Lei 19.426/2025, art. 190): Processos protocolados antes da vigência seguem a lei anterior; VEI deferida/tramitando dentro da validade pode usar a lei anterior.
- **Revogações** (F01, Lei 19.426/2025, art. 201): Revoga, entre outras, as Leis 16.176/1996 (LUOS anterior), 16.286/1997, 16.719/2001 (ARU) e 18.112/2015.
- **Operações urbanas consorciadas** (F02, Lei 19.426/2025, Anexo XV): OUC listada como empreendimento de impacto; nenhuma OUC vigente identificada nas fontes acessíveis.

## Geometria

Não foi possível acessar camadas vetoriais oficiais do Recife (hosts da Prefeitura bloqueados para o ambiente de coleta). As geometrias foram vetorizadas dos mapas raster do Anexo II da própria Lei 19.426/2025 (documentos oficiais da Câmara Municipal), georreferenciados pela grade UTM SIRGAS 2000/25S impressa (resíduos ≤7 m na grade; ≈18,7 m/px). Mapas 3A/3C da redação final foram registrados sobre os do PLE (resíduo ≈1 px). Todas oficial:false; erro estimado 50–100 m. Área total vetorizada ≈22.800 ha (+3,6% vs. área oficial).

| camada | arquivo | oficial | método | erro (m) | feições |
|---|---|---|---|---|---|
| Zoneamento + setores (19 zonas base) | geo/zoneamento.geojson | False | Classificação por cor dos Mapas 2 e 4 (raster 1213x1710), restrita por macrozona; polígonos por contornos OpenCV; georreferência pela grade UTM impressa (OCR dos rótulos) | 50.0 | 19 |
| Macrozonas MANC/MAC | geo/macrozonas.geojson | False | Classificação por cor do Mapa 1 + grade UTM | 50.0 | 2 |
| ZEIS (Mapa 3A final) | geo/zeis.geojson | False | Registro afim ORB+RANSAC do mapa da redação final sobre o do PLE + classificação por cor | 60.0 | 3 |
| ZEC 1 (Mapa 3B) | geo/zec.geojson | False | Mapa 3B do PLE + acréscimos do mapa final de baixa resolução | 100.0 | 1 |
| ZEPH – setores (Mapa 3C final) | geo/zeph.geojson | False | Registro afim ORB+RANSAC + classificação por cor | 60.0 | 4 |
| Unidades protegidas (Mapa 6) | geo/unidades_protegidas.geojson | False | Classificação por cor + grade UTM | 50.0 | 5 |
| Indicação ZEC 2/3 | geo/zec23_indicacao.geojson | False | Símbolos do Mapa 3B | 100.0 | 1 |

Regras de consulta: 1) Zona base: as 19 zonas base (com setores) particionam o município; parâmetros do Anexo IV. 2) ZEPH (prioridade 30, substitui) prevalece sobre ZEC (art. 19 §2º): SPS/SPM/SPPI = análise especial; SPA = Anexo V. 3) ZEIS (prioridade 20, substitui): CA/IAC do Anexo IV e demais parâmetros pelo plano da ZEIS. 4) ZEC 1 (prioridade 15, substitui): parâmetros da linha ZEC 1 do Anexo IV. 5) Lotes lindeiros à Av. Boa Viagem (42 m) e ao Rio Capibaribe (24 m): gabarito do art. 122 (não mapeado – verificar testada). 6) TSN/TCA pelo tamanho do terreno (Anexo XVIII). 7) Camadas macrozonas (limiar de EIV), unidades_protegidas e zec_2_3_indicacao: alertas. Confirmar sempre na Prefeitura (SEPUL/Licenciamento Urbanístico).

Limitações:

- Geometrias não oficiais (vetorização de mapas raster de ~1200x1700 px para todo o município), erro 50–100 m: não usar no limite entre zonas sem confirmação na Prefeitura.
- ZEIS e ZEPH agregadas por categoria/setor, sem nome por polígono; ZEIS/ZEPH muito pequenas podem faltar.
- Ampliações das ZEC 1 Praça de Boa Viagem e Encruzilhada tomadas de mapa de baixa resolução; setores A/B não separados.
- Faixas de lotes lindeiros (art. 122) e sistema viário (Mapa 7) não vetorizados.

## Lacunas

- **Plano Diretor do Recife (LC 02/2021)** – Só publicado em hosts *.recife.pe.gov.br, que recusam conexão a partir do ambiente de coleta (TLS encerrado); sapl.recife.pe.leg.br retornou 503. Referências ao PD vêm apenas da LPUOS.
- **Lei 18.900/2022 (OODC) – fórmula, fatores e isenções** – Página oficial https://licenciamentounificado.recife.pe.gov.br/189002022 inacessível; não usada fonte secundária.
- **Lei 18.901/2022 (TDC) e demais leis de instrumentos (IPTU progressivo, OUC)** – Mesmos hosts bloqueados.
- **Camadas vetoriais oficiais (ESIG/dados abertos da Prefeitura)** – esigportal2, dados.recife e licenciamentounificado bloqueados; não se contornou bloqueio. Geometrias vetorizadas dos mapas raster da lei (oficial:false).
- **Anexo XX (coordenadas dos perímetros)** – Na redação final o Anexo XX é um link para planilha Google Sheets (não é publicação oficial estável) – não utilizado.
- **Anexos no DOM** – O DOM nº 125 disponível na Câmara contém só o texto e o Anexo I; os Anexos II–XX foram tomados da redação final aprovada (Parecer 75/2025), sancionada sem vetos identificados.
- **Setores A/B das ZEC 1 Praça de Boa Viagem e Encruzilhada** – Mapa 3B da redação final tem apenas 375x566 px; ampliações vetorizadas grosseiramente e sem separação de setores.
- **ZEC 2 e ZEC 3** – Perímetros a definir em plano específico (art. 20 §2º).
- **Nomes das ZEIS e das ZEPH por polígono** – Mapas sem rótulos legíveis; geometria agregada por categoria/setor.
- **Parâmetros detalhados das ZEPH (Anexo V)** – Quadro extenso e por ZEPH/SPA; só gabaritos de SPA parcialmente estruturados; SPS/SPM/SPPI são de análise especial.
- **Lotes lindeiros à Av. Boa Viagem e ao Rio Capibaribe (art. 122)** – Faixas de lotes lindeiros não mapeadas; regra só como condicional.
- **Densidade máxima** – LPUOS não fixa densidade; só cota-parte mínima.
- **Definição de HIS por renda / percentuais de uso em ZEIS** – Remetidos ao PD (art. 74) e PLHIS, não acessados.
- **Limite municipal IBGE para validação** – servicodados.ibge.gov.br bloqueado; limite derivado do Mapa 1 (área +3,6% em relação à área oficial ≈21.884 ha).

## Bloqueios de acesso encontrados (não contornados)

- Todos os hosts *.recife.pe.gov.br (licenciamentounificado, dados.recife, esigportal2/ArcGIS, icps, dome) encerram a conexão TLS a partir do ambiente de coleta.
- sapl.recife.pe.leg.br retornou 503; servicodados.ibge.gov.br bloqueado. Foi usado o e-processo da Câmara Municipal (e-processo.recife.pe.leg.br), público e sem login.

## Reprodução

```
cd scripts
python3 vet1_macrozonas.py && python3 vet2_zoneamento.py && python3 vet3_especiais.py   # (venv com cv2: /workspace/.venv_ocr/bin/python)
python3 build_recife.py && python3 gerar_referencias.py
python3 /workspace/legislacao/plataforma/validar_cidade.py recife-pe
```

Arquivos: fontes/ (PDFs oficiais, textos extraídos, mapas/ PNG extraídos dos PDFs), geo/ (GeoJSON vetorizados + vetorizacao_log.json), scripts/.
