"""Gera ../REFERENCIAS.md a partir de ../curitiba-pr.json. Uso: python3 gerar_referencias.py"""
import json, os
from collections import defaultdict, Counter

AQUI = os.path.dirname(os.path.abspath(__file__)); PASTA = os.path.dirname(AQUI)
d = json.load(open(os.path.join(PASTA, 'curitiba-pr.json'), encoding='utf-8'))
citas = defaultdict(Counter)
def walk(o):
    if isinstance(o, dict):
        if o.get('type') in ('FeatureCollection', 'Feature'): return
        if o.get('fonte_id') and o.get('artigo_anexo'): citas[o['fonte_id']][o['artigo_anexo']] += 1
        for k, v in o.items():
            if k not in ('features', 'geometria'): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
for z in d['zonas']: walk(z)
for c in d['camadas_complementares'].values(): walk(c)
for k in ('outorga_onerosa', 'zeis_his', 'outros_parametros'): walk(d.get(k))

def v(p):
    if not p: return '—'
    f = p.get('forma')
    if f in ('unico', 'lista'): return str(p['valor']).replace('.', ',') if f == 'unico' else ', '.join(p['valor'])
    if f == 'condicional':
        return ' / '.join(f"{c['condicao']}: {('%g' % c['valor']).replace('.', ',') if isinstance(c.get('valor'), (int, float)) else (c.get('formula') or c['forma'])}" for c in p['condicionais'])
    if f == 'formula': return p.get('formula')
    if f == 'texto': return (p.get('texto_original') or '')[:80]
    return f
L = [f"# Referências legais – {d['municipio']}/{d['uf']} (`{d['slug']}`)", '',
     f"Levantamento: {d['data_levantamento']} · IBGE {d['codigo_ibge']} · schema {d['schema_versao']} · gerado por `scripts/gerar_referencias.py`.", '',
     '> Só fontes oficiais e públicas (Legisladoc da Prefeitura/Câmara de Curitiba, mid.curitiba.pr.gov.br, GeoCuritiba/IPPUC – serviços públicos). Valores sem fonte = `null` e listados em *Lacunas*. '
     f"Confirme sempre na {d.get('orgao_confirmacao')} antes de decisão de compra.", '',
     '## Marco legal vigente em 27/10/2026', '', d['marco_legal_vigente'], '',
     '## Como ler os parâmetros', '',
     '- Zona base = código do zoneamento na camada 35 do Mapa Cadastral (GeoCuritiba); sub-áreas (ex.: `POLO-LV - 3`) ficam em `properties.subarea`.',
     '- CA básico, TO, altura, recuo, afastamento, permeabilidade e lote: Quadros da Lei 15.511/2019 (linha *Habitação Coletiva*). CA máximo e pavimentos máximos: Lei 16.361/2024 Quadros II/III (50% OODC + 50% TDC); na OUC-LV, CEPAC (Lei 13.909/2011).',
     '- HIS da COHAB-CT (Dec. 297/2026) em `parametros.outros.*_his_cohab`; vagas pelo Dec. 2.397/2023 arts. 74–75; densidade de conjuntos pelo art. 212 (100 × CA).', '',
     '## Fontes', '', '| ID | Norma | Data | Título | Arquivo local | Link oficial |', '|---|---|---|---|---|---|']
for f in d['fontes']:
    L.append(f"| {f['id']} | {f['lei']} | {f['data']} | {f['titulo']} | {f.get('arquivo_local') or '—'} | [link]({f['url']}) |")
L += ['', '## Artigos/anexos citados por fonte (nº de parâmetros que citam)', '']
for f in d['fontes']:
    c = citas.get(f['id'])
    if c: L.append(f"- **{f['id']}** ({f['lei']}): " + '; '.join(f'{a} ({n})' for a, n in c.most_common(15)) + (f' … (+{len(c)-15})' if len(c) > 15 else ''))
L += ['', '## Zonas (habitação coletiva)', '', '| Código | Nome | Categoria | CA básico | CA máximo | Pavimentos | HIS COHAB CA | Feições |', '|---|---|---|---|---|---|---|---|']
for z in d['zonas']:
    p = z['parametros']
    L.append(f"| {z['codigo']} | {z['nome']} | {z['categoria_normalizada']} | {v(p['ca_basico'])} | {v(p['ca_maximo'])} | {v(p['gabarito_pavimentos'])} | {v(p['outros'].get('ca_maximo_his_cohab'))} | {len(z['geometria']['features'])} |")
L += ['', '## Resumo MCMV', ''] + [f'- {x}' for x in d['resumo_mcmv']]
g = d['geografico']
L += ['', '## Camadas geográficas', '', f"Servidor oficial: {g.get('servidor_oficial')} · CRS de área: {g.get('crs_area')}", '',
      '| Camada | Arquivo bruto | Oficial | Método | Feições | Download | URL |', '|---|---|---|---|---|---|---|']
for c in g['camadas']:
    L.append(f"| {c['nome']} | `{c.get('arquivo')}` | {'sim' if c['oficial'] else 'não'} | {c['metodo']} | {c.get('n_feicoes', '—')} | {c['data_download']} | {c['fonte_url']} |")
L += ['', '### Camadas complementares no JSON', '']
for n, c in d['camadas_complementares'].items():
    L.append(f"- **{n}** (papel `{c['papel']}`, {len(c['features'])} feições; {c.get('fonte_id')} {c.get('artigo_anexo')}): {c.get('descricao', '')}")
L += ['', '## Limitações', ''] + [f'- {x}' for x in g['limitacoes']]
L += ['', '## Lacunas (não encontrado em fonte oficial – ficou `null`)', ''] + [f"- **{x['item']}**: {x.get('motivo', '')}" for x in d['lacunas']]
L += ['', '## Conteúdo desta pasta', '', f"- `{d['slug']}.json` – dados no padrão da plataforma (schema {d['schema_versao']}).",
      '- `fontes/` – leis, decretos e quadros oficiais (PDF/HTML + texto extraído).', '- `geo_raw/` – camadas brutas GeoJSON EPSG:4326 do GeoCuritiba (serviços públicos).',
      '- `scripts/` – `baixar_camadas.py` (ArcGIS REST), `baixa_ato.py`/`busca.py` (Legisladoc), `comum_cwb.py` (fontes), `tabelas_cwb.py` (Quadros transcritos), `build_cwb.py` (monta o JSON), `gerar_referencias.py`.',
      '', 'Reprodução: `cd scripts && python3 baixar_camadas.py && python3 build_cwb.py && python3 gerar_referencias.py && python3 ../../../validar_cidade.py curitiba-pr`.']
open(os.path.join(PASTA, 'REFERENCIAS.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('REFERENCIAS.md:', len(L), 'linhas')
