"""Gera REFERENCIAS.md a partir de fortaleza-ce.json (fontes, camadas, lacunas) + notas metodológicas."""
import json, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(B, 'fortaleza-ce.json')))
L = ['# Fortaleza-CE – Referências da legislação urbanística e das camadas geográficas', '',
     f"Levantamento: {d['data_levantamento']} · schema {d['schema_versao']} · gerado por `scripts/build_fortaleza.py` · validado com `validar_cidade.py fortaleza-ce` (APROVADO).", '',
     '## Marco legal vigente', '', d['marco_legal_vigente'], '',
     '## Fontes (leis, decretos, portais oficiais)', '', '| id | norma | título | data | link | arquivo local |', '|---|---|---|---|---|---|']
for f in d['fontes']:
    L.append(f"| {f['id']} | {f['lei']} | {f['titulo'].replace('|', '/')} | {f['data']} | {f['url']} | {f.get('arquivo_local') or ''} |")
L += ['', '## Dispositivos-chave por tema', '',
 '- Parâmetros por zona: LC 236/2017 Anexo 4 – Tabela 4.1 (MPA: ZIA, ZRA, ZPA), Tabela 4.2 (MOU: ZOP, ZOC, ZRU, ZOM, ZOR, Zona da Orla), Tabela 4.3 (ZEDUS, redação da LC 287/2020); ZIA Sabiaguaba: LC 436/2025.',
 '- Usos: LC 236 Anexo 5 (Tabela 5.1 – subgrupo residencial), Anexo 6 (Tabelas 6.1–6.33 por zona) e Anexo 8 (Tabela 8.1 – vias e recuos; art. 91).',
 '- Fração do Lote/densidade: PDP art. 313 (LC 101/2011; LC 243/2017 §§3º–5º); LC 236 arts. 100–102 (art. 101 p.ú.: HIS MCMV 30 m²/UH).',
 '- OODC: PDP arts. 218–223 (fórmula art. 220; isenção EHIS art. 220 §2º); FUNDURB LC 211/2015; TDC PDP arts. 224–230 + Lei 10.333/2015; OOAU Lei 10.335/2015 + LC 333/2022.',
 '- ZEIS: PDP arts. 125–138 (LC 79/2010, LC 229/2017); leis específicas de ZEIS 1: LCs 438–447/2025.',
 '- Conjuntos HIS: LC 236 arts. 204–211. EIV: PDP arts. 291–294; Projetos Especiais LC 236 arts. 170–176.',
 '- Incentivos MCMV: LC 359/2023 (ITBI, IPTU 5 anos, ISSQN 7.02, taxas) alterada pela LC 434/2025.',
 '- Vigência: LC 450/2025 (novo PDPS) aprovada, mas adiada pela LC 461/2026 (≈ maio/2027) – NÃO aplicada.', '',
 '## Camadas geográficas (todas oficiais – Fortaleza em Mapas, download público GeoJSON, sem login)', '',
 '| camada | arquivo bruto | campo | URL | baixada em | método | erro estimado (m) |', '|---|---|---|---|---|---|---|']
for c in d['geografico']['camadas']:
    L.append(f"| {c['nome']} | {c.get('arquivo') or ''} | {c.get('campo') or ''} | {c['fonte_url']} | {c['data_download']} | {c['metodo']} | {c['erro_estimado_m'] if c['erro_estimado_m'] is not None else '≈ simplificação 1,5'} |")
L += ['', 'Processamento: shapely `make_valid`, simplificação ≤ 1,5 m em EPSG:31984, coordenadas com 6 casas decimais (EPSG:4326). Nenhuma geometria digitalizada (oficial = true em todas).', '',
      '## Regras de consulta (motor genérico)', '', d['geografico']['regras_de_consulta'], '', '## Limitações', ''] + [f'- {x}' for x in d['geografico']['limitacoes']] + \
     ['', '## Lacunas', ''] + [f"- **{x['item']}** – {x['motivo']}" for x in d['lacunas']] + \
     ['', '## Resumo MCMV', ''] + [f'- {x}' for x in d['resumo_mcmv']] + \
     ['', '## Reprodutibilidade', '', '1. `python3 scripts/baixar_leis.py` (PDFs para `fontes/`; OCR com RapidOCR nos escaneados → `*.ocr.txt`).',
      '2. `python3 scripts/baixar_camadas.py` (GeoJSON para `geo_raw/`, log em `geo_raw/_log_download.json`).',
      '3. `python3 scripts/build_fortaleza.py` → `fortaleza-ce.json` (já no schema 1.1).', '4. `python3 scripts/gerar_referencias.py` → este arquivo.',
      '5. `python3 ../../validar_cidade.py fortaleza-ce`.', '']
open(os.path.join(B, 'REFERENCIAS.md'), 'w').write('\n'.join(L))
print('ok', len(L))
