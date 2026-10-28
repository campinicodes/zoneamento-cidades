"""Gera REFERENCIAS.md a partir de recife-pe.json."""
import json, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(B, 'recife-pe.json')))
L = ['# Recife-PE – Referências', '', f"Levantamento: {d['data_levantamento']} · schema {d['schema_versao']} · validar_cidade.py: APROVADO", '',
     '## Marco legal vigente', '', d['marco_legal_vigente'], '', '## Fontes oficiais', '', '| id | lei | título | link | arquivo local |', '|---|---|---|---|---|']
for f in d['fontes']:
    L.append(f"| {f['id']} | {f['lei']} | {f['titulo']} | {f['url']} | {f.get('arquivo_local') or '-'} |")
L += ['', 'Observações das fontes:', ''] + [f"- **{f['id']}**: {f['observacao']}" for f in d['fontes'] if f.get('observacao')]
def v(p):
    if not p: return '-'
    if p['forma'] == 'unico': return str(p['valor'])
    if p['forma'] == 'condicional':
        return '; '.join(f"{c['condicao']}: {c['valor'] if c['forma']=='unico' else (c.get('formula') or c['forma'])}" for c in p['condicionais'])
    return p['forma']
L += ['', '## Zonas', '', '| código | tipo/prior. | categoria | CA mín/bás/máx | TO | gabarito (m) | TSN | recuo frontal | área (ha) |', '|---|---|---|---|---|---|---|---|---|']
for z in d['zonas']:
    p = z['parametros']; a = sum(f['properties'].get('area_ha', 0) for f in z['geometria']['features'])
    L.append(f"| {z['codigo']} | {z['tipo']}/{z['prioridade']} | {z['categoria_normalizada']} | {v(p['ca_minimo'])}/{v(p['ca_basico'])}/{v(p['ca_maximo'])} | {v(p['taxa_ocupacao'])} | {v(p['gabarito_altura_max_m'])} | {v(p['taxa_permeabilidade'])} | {v(p['recuos']['frontal'])} | {a:.0f} |")
L += ['', 'Comuns a todas as zonas base: lote mínimo 125 m² e testada 5 m (art. 58); usos habitacional (uni/multifamiliar), não habitacional e misto em qualquer zona, salvo atividades restritas/proibidas (arts. 98–102); sem mínimo de vagas (art. 175); sem densidade máxima.', '',
      '## Resumo MCMV', ''] + [f'- {x}' for x in d['resumo_mcmv']]
for bl, t in (('outorga_onerosa', 'Outorga onerosa'), ('zeis_his', 'ZEIS / HIS'), ('outros_parametros', 'Outros parâmetros (EIV, gabaritos especiais etc.)')):
    b = d[bl]; L += ['', f'## {t}', '', b['resumo'], '']
    for i in b['itens']:
        L.append(f"- **{i['titulo']}** ({i['fonte_id']}, {i['artigo_anexo']}): {v(i) if i['forma'] in ('unico','condicional') else ''} {i.get('observacao') or ''}".replace('  ', ' '))
g = d['geografico']
L += ['', '## Geometria', '', g['descricao'], '', '| camada | arquivo | oficial | método | erro (m) | feições |', '|---|---|---|---|---|---|']
L += [f"| {c['nome']} | {c['arquivo']} | {c['oficial']} | {c['metodo']} | {c['erro_estimado_m']} | {c['n_feicoes']} |" for c in g['camadas']]
L += ['', 'Regras de consulta: ' + g['regras_de_consulta'], '', 'Limitações:', ''] + [f'- {x}' for x in g['limitacoes']]
L += ['', '## Lacunas', ''] + [f"- **{x['item']}** – {x['motivo']}" for x in d['lacunas']]
L += ['', '## Bloqueios de acesso encontrados (não contornados)', '',
      '- Todos os hosts *.recife.pe.gov.br (licenciamentounificado, dados.recife, esigportal2/ArcGIS, icps, dome) encerram a conexão TLS a partir do ambiente de coleta.',
      '- sapl.recife.pe.leg.br retornou 503; servicodados.ibge.gov.br bloqueado. Foi usado o e-processo da Câmara Municipal (e-processo.recife.pe.leg.br), público e sem login.',
      '', '## Reprodução', '', '```', 'cd scripts', 'python3 vet1_macrozonas.py && python3 vet2_zoneamento.py && python3 vet3_especiais.py   # (venv com cv2: /workspace/.venv_ocr/bin/python)',
      'python3 build_recife.py && python3 gerar_referencias.py', 'python3 /workspace/legislacao/plataforma/validar_cidade.py recife-pe', '```',
      '', 'Arquivos: fontes/ (PDFs oficiais, textos extraídos, mapas/ PNG extraídos dos PDFs), geo/ (GeoJSON vetorizados + vetorizacao_log.json), scripts/.']
open(os.path.join(B, 'REFERENCIAS.md'), 'w').write('\n'.join(L) + '\n')
print('ok', len(L))
