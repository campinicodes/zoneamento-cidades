"""Gera ../REFERENCIAS.md a partir de ../porto-alegre-rs.json. Uso: python3 gerar_referencias.py"""
import json, os
from collections import defaultdict, Counter

AQUI = os.path.dirname(os.path.abspath(__file__)); PASTA = os.path.dirname(AQUI)
d = json.load(open(os.path.join(PASTA, 'porto-alegre-rs.json'), encoding='utf-8'))
LOCAL = {'F01': 'PDDUA_compilado_20251216.pdf', 'F02': 'PDDUA_Anexo_4.pdf', 'F03': 'PDDUA_Anexo_5.pdf', 'F04': 'PDDUA_Anexo_6.pdf',
         'F05': 'PDDUA_Anexo_7.pdf', 'F06': 'PDDUA_Anexo_8.pdf', 'F07': 'PDDUA_Anexo_10.pdf', 'F08': 'PDDUA_Anexo_11.pdf',
         'F09': 'LC1075_2026_PDUS.pdf', 'F10': 'LC1076_2026_LUOS.pdf', 'F13': 'LC1022_2024_HIS.pdf', 'F14': 'Dec22932_2024.pdf',
         'F15': 'LC636_2010.docx', 'F16': 'LC548_2006.docx', 'F17': 'LC547_2006.docx', 'F18': 'LC946_2022.pdf', 'F19': 'dspace_doc.pdf',
         'F21': 'mapas_digitais.html', 'F24': 'Guia_Pratico.pdf', 'F25': '../geo_raw/PDDUA_Metadados.zip', 'F26': 'AEIS.pdf'}

citas = defaultdict(Counter)
def walk(o, onde):
    if isinstance(o, dict):
        if o.get('type') in ('FeatureCollection', 'Feature'): return
        if o.get('fonte_id') and o.get('artigo_anexo'): citas[o['fonte_id']][o['artigo_anexo']] += 1
        for k, v in o.items():
            if k not in ('features', 'geometria'): walk(v, onde)
    elif isinstance(o, list):
        for v in o: walk(v, onde)
for z in d['zonas']: walk(z, z['codigo'])
for n, c in d['camadas_complementares'].items(): walk(c, n)
for k in ('outorga_onerosa', 'zeis_his', 'outros_parametros'): walk(d.get(k), k)

base = [z for z in d['zonas'] if z['tipo'] == 'base']; sob = [z for z in d['zonas'] if z['tipo'] != 'base']
L = [f"# Referências legais – {d['municipio']}/{d['uf']} (`{d['slug']}`)", '',
     f"Levantamento: {d['data_levantamento']} · IBGE {d['codigo_ibge']} · schema {d['schema_versao']} · gerado por `scripts/gerar_referencias.py`.", '',
     '> Só fontes oficiais e públicas (PMPA/SMAMUS, DOPA, SAPL/legislação municipal, ArcGIS público da SMAMUS). Valores sem fonte = `null` e listados em *Lacunas*. '
     f"Confirme sempre na {d.get('orgao_confirmacao')} (DMI) antes de decisão de compra.", '',
     '## Marco legal vigente em 27/10/2026', '', d['marco_legal_vigente'], '',
     '## Como ler o regime do PDDUA', '',
     '- Cada **subunidade** do PDDUA tem 4 códigos: densidade (Anexo 4), grupamento de atividades (Anexo 5), índice de aproveitamento (Anexo 6) e volumetria (Anexo 7.1). '
     'A zona base deste JSON é a combinação `D{densidade}-A{atividade}-IA{índice}-V{volumetria}`; o polígono de cada subunidade fica em `geometria.features` com MZ/UEU/subunidade.',
     f"- {len(base)} combinações base ({sum(len(z['geometria']['features']) for z in base)} subunidades) + {len(sob)} zonas sobrepostas de AEIS ({', '.join(z['codigo'] for z in sob)}).",
     '- CA básico = IA do Anexo 6; CA máximo = IA máximo (via Solo Criado, LC 946/2022), limitado a 3,0; área rarefeita: máximo = básico (art. 110).',
     '- Lote/testada: Anexo 8.1 (loteamento); AEIS: 125 m²/5 m (nota 3). Vagas: Anexo 10.1 (Dec. 20.385/2019) – residencial dispensado em testada ≥ 12 m; MCMV 0,5 vaga/UH (LC 636/2010 art. 21).', '',
     '## Fontes', '', '| ID | Norma | Data | Título | Arquivo local (fontes/) | Link oficial |', '|---|---|---|---|---|---|']
for f in d['fontes']:
    L.append(f"| {f['id']} | {f['lei']} | {f['data']} | {f['titulo']} | {LOCAL.get(f['id'], '—')} | [link]({f['url']}) |")
L += ['', '## Artigos/anexos citados por fonte (nº de parâmetros que citam)', '']
for f in d['fontes']:
    c = citas.get(f['id'])
    if c:
        L.append(f"- **{f['id']}** ({f['lei']}): " + '; '.join(f'{a} ({n})' for a, n in c.most_common(20)) + (f' … (+{len(c)-20})' if len(c) > 20 else ''))
L += ['', '## Zonas por categoria normalizada', '', '| Categoria | Nº de combinações | Nº de subunidades |', '|---|---|---|']
cat = defaultdict(lambda: [0, 0])
for z in d['zonas']:
    cat[z['categoria_normalizada']][0] += 1; cat[z['categoria_normalizada']][1] += len(z['geometria']['features'])
for k, (a, b) in sorted(cat.items(), key=lambda x: -x[1][1]): L.append(f'| {k} | {a} | {b} |')
L += ['', '## Regras de sobreposição', '', '| Zona | Tipo | Prioridade | Efeito | Fundamento |', '|---|---|---|---|---|',
      f"| {len(base)} zonas base (subunidades) | base | {base[0]['prioridade']} | {(base[0].get('regra_sobreposicao') or {}).get('efeito') or '—'} | regime por subunidade (PDDUA arts. 95–117, Anexos 4–7) |"]
for z in sorted(sob, key=lambda z: -z['prioridade']):
    r = z.get('regra_sobreposicao') or {}
    L.append(f"| {z['codigo']} – {z['nome']} | {z['tipo']} | {z['prioridade']} | {r.get('efeito') or '—'} | {r.get('fundamento') or '—'} |")
L += ['', '## Resumo MCMV', ''] + [f'- {x}' for x in d['resumo_mcmv']]
g = d['geografico']
L += ['', '## Camadas geográficas', '', f"Servidor oficial: {g.get('servidor_oficial')} · CRS de área: {g.get('crs_area')}", '',
      '| Camada | Arquivo bruto | Oficial | Método | Erro est. (m) | Feições | Download | URL |', '|---|---|---|---|---|---|---|---|']
for c in g['camadas']:
    L.append(f"| {c['nome']} | `{c.get('arquivo') or c.get('campo')}` | {'sim' if c['oficial'] else 'não'} | {c['metodo']} | {c['erro_estimado_m']} | {c.get('n_feicoes', '—')} | {c['data_download']} | {c['fonte_url']} |")
L += ['', '### Camadas complementares no JSON', '']
for n, c in d['camadas_complementares'].items():
    L.append(f"- **{n}** (papel `{c['papel']}`, {len(c['features'])} feições): {c.get('descricao', '')}")
L += ['', '## Limitações', ''] + [f'- {x}' for x in g['limitacoes']]
L += ['', '## Lacunas (não encontrado em fonte oficial – ficou `null`)', ''] + [f"- **{x['item']}**: {x.get('motivo', '')}" for x in d['lacunas']]
L += ['', '## Conteúdo desta pasta', '', f"- `{d['slug']}.json` – dados no padrão da plataforma (schema {d['schema_versao']}).",
      '- `fontes/` – cópias das leis, anexos e mapas oficiais (PDF/DOCX + texto extraído).',
      '- `geo_raw/` – camadas brutas (GeoJSON EPSG:4326 do ArcGIS SMAMUS; shapefiles TM-POA da página Mapas Digitais).',
      '- `scripts/` – `baixar_camadas.py` (download ArcGIS REST), `docx2txt.py`, `tabelas_pddua.py` (Anexos 4–8 transcritos), `build_poa.py` (monta o JSON), `gerar_referencias.py` (este arquivo).',
      '', 'Reprodução: `cd scripts && python3 baixar_camadas.py && python3 build_poa.py && python3 gerar_referencias.py && python3 ../../../validar_cidade.py porto-alegre-rs`.']
open(os.path.join(PASTA, 'REFERENCIAS.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('REFERENCIAS.md:', len(L), 'linhas')
