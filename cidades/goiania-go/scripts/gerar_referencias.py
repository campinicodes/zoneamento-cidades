"""Gera ../REFERENCIAS.md a partir de ../goiania-go.json. Uso: python3 gerar_referencias.py"""
import json, os
from collections import defaultdict, Counter

AQUI = os.path.dirname(os.path.abspath(__file__)); PASTA = os.path.dirname(AQUI)
d = json.load(open(os.path.join(PASTA, 'goiania-go.json'), encoding='utf-8'))
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
     '> Só fontes oficiais e públicas (SILEG – legislação compilada da Prefeitura de Goiânia, goiania.go.gov.br; Portal Mapa Goiânia/SEPLANH – ArcGIS REST público). Valores sem fonte = `null` e listados em *Lacunas*. '
     f"Confirme sempre na {d.get('orgao_confirmacao')} antes de decisão de compra.", '',
     '## Marco legal vigente em 27/10/2026', '', d['marco_legal_vigente'], '',
     '## Como ler os parâmetros', '',
     '- Zonas base = unidades territoriais do Modelo Espacial (LC 349/2022 Anexo XIV): AA, ADD, AAB (resíduo da Macrozona Construída), AOS, APAC (ABT e entornos AEBT agrupados pelas linhas do Anexo XXII), ARAU (APP, Jardim Botânico, UUS) e as 7 Macrozonas Rurais; sobrepostas: AEIS III (HIS) e APA.',
     '- IA (CA máximo): art. 196 (AA 6, ADD 5); CA básico = 1 (área não onerosa, arts. 242–244). TO, altura e densidade: arts. 190–196; recuos: Anexo XXI (altura × afastamento) e Anexo XXII (APAC); vagas: LC 364/2023 arts. 110–111; HIS: LC 379/2024 arts. 14–16 (em `parametros.condicionais` com código HIS).',
     '- TDC suspensa para novas concessões (Dec. 2.785/2025 + Dec. 82/2026): o IA 7,5 da AA com TDC aparece como condicional, não como valor corrente.', '',
     '## Fontes', '', '| ID | Norma | Data | Título | Arquivo local | Link oficial |', '|---|---|---|---|---|---|']
for f in d['fontes']:
    L.append(f"| {f['id']} | {f['lei']} | {f['data']} | {f['titulo']} | {f.get('arquivo_local') or '—'} | [link]({f['url']}) |")
L += ['', '## Artigos/anexos citados por fonte (nº de parâmetros que citam)', '']
for f in d['fontes']:
    c = citas.get(f['id'])
    if c: L.append(f"- **{f['id']}** ({f['lei']}): " + '; '.join(f'{a} ({n})' for a, n in c.most_common(15)) + (f' … (+{len(c)-15})' if len(c) > 15 else ''))
L += ['', '## Zonas (habitação coletiva)', '', '| Código | Nome | Categoria | CA básico | CA máximo | TO | Altura (m) | Densidade | Feições |', '|---|---|---|---|---|---|---|---|---|']
for z in d['zonas']:
    p = z['parametros']
    L.append(f"| {z['codigo']} | {z['nome']} | {z['categoria_normalizada']} | {v(p['ca_basico'])} | {v(p['ca_maximo'])} | {v(p['taxa_ocupacao'])} | {v(p['gabarito_altura_max_m'])} | {v(p['densidade'])} | {len(z['geometria']['features'])} |")
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
      '- `fontes/` – leis, decretos e quadros oficiais (PDF/HTML + texto extraído).', '- `geo_raw/` – camadas brutas GeoJSON EPSG:4326 do Portal Mapa Goiânia (Simplifica FeatureServer/3 e Mapa_ModeloEspacial).',
      '- `scripts/` – `baixar_camadas.py` (ArcGIS REST), `html2txt.py` (SILEG→texto), `comum_gyn.py` (fontes e construtores), `tabelas_gyn.py` (parâmetros transcritos), `build_gyn.py` (monta o JSON), `gerar_referencias.py`.',
      '', 'Reprodução: `cd scripts && python3 baixar_camadas.py && python3 build_gyn.py && python3 gerar_referencias.py && python3 ../../../validar_cidade.py goiania-go`.']
open(os.path.join(PASTA, 'REFERENCIAS.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('REFERENCIAS.md:', len(L), 'linhas')
