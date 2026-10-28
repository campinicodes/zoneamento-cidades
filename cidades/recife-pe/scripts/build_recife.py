#!/usr/bin/env python3
"""Monta recife-pe.json (schema 1.1) a partir de geo/*.geojson (vetorização dos mapas do Anexo II da Lei 19.426/2025)
e de params_recife.py. Uso: cd scripts && python3 build_recife.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params_recife import *

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(BASE, 'geo')
HOJE = '2026-10-27'
LOG = json.load(open(os.path.join(GEO, 'vetorizacao_log.json')))
URL_RF = FONTES[1]['url']; URL_PLE = FONTES[2]['url']

def load(nome):
    return {f['properties']['codigo']: f for f in json.load(open(os.path.join(GEO, nome + '.geojson')))['features']}
ZON, ZEIS, ZEC, ZEPH = load('zoneamento'), load('zeis'), load('zec'), load('zeph')
MAC, UP, Z23 = load('macrozonas'), load('unidades_protegidas'), load('zec23_indicacao')

def fc(feats, fonte, oficial, obs):
    return {'type': 'FeatureCollection', 'crs': 'EPSG:4326 (lon, lat)', 'fonte': fonte, 'oficial': oficial, 'observacao_geometria': obs, 'features': feats}
def feat(f, codigo, **props):
    return {'type': 'Feature', 'properties': dict(codigo=codigo, area_ha=f['properties']['area_ha'], **props), 'geometry': f['geometry']}

OBS_BASE = ('Vetorização aproximada (oficial:false) dos Mapas 2 (zoneamento) e 4 (setores) do Anexo II da Lei 19.426/2025 (raster 1213x1710 px do PLE 16/2025, '
            'idênticos aos da redação final), georreferenciados pela grade UTM SIRGAS 2000/25S impressa (≈18,7 m/px; resíduo máx. %.1f m). '
            'Erro estimado ≈50 m (≈2–3 px), maior nas bordas de zonas estreitas e em feições lineares.' % max(LOG['grade']['residuo_max_x_m'], LOG['grade']['residuo_max_y_m']))
FONTE_GEO_BASE = 'Lei 19.426/2025, Anexo II – Mapas 2 e 4 (PLE 16/2025: ' + URL_PLE + '; redação final: ' + URL_RF + ')'

# ------------------------- parâmetros por zona -------------------------
def na(fid, art, un, obs='Anexo IV: N/A (não se aplica).'):
    return P(None, fid, art, obs, un, 'nao_aplicavel')

def tsn_param(cod):
    t = a18(cod)
    conds = [C(lbl, v[1] / 100.0, faixa=fx) for lbl, v, fx in zip(('terreno < 500 m²', '500 m² ≤ terreno < 2.000 m²', 'terreno > 2.000 m²'), t,
             ({'min': None, 'max': 500}, {'min': 500, 'max': 2000}, {'min': 2000, 'max': None}))]
    for c in conds: c['forma'] = 'unico'; c.pop('faixa', None)
    return P(None, 'F02', A18, 'Taxa de Solo Natural mínima (TSN, art. 130) – solo natural vegetado; varia pela área do terreno. 1 m² de jardim de chuva vale 1,30 m² de TSN (Obs. 3).', 'fracao', 'condicional', condicionais=conds)

def tca_param(cod):
    t = a18(cod)
    conds = []
    for lbl, v in zip(('terreno < 500 m²', '500 m² ≤ terreno < 2.000 m²', 'terreno > 2.000 m²'), t):
        conds.append(C(lbl, v[0] / 100.0) if v[0] is not None else C(lbl, forma='nao_aplicavel'))
    return P(None, 'F02', A18, 'Taxa de Contribuição Ambiental (TCA, arts. 131–132): % do lote em soluções ambientais (Anexo XIX). HIS pode ser dispensada (art. 164).', 'fracao', 'condicional', condicionais=conds)

def gab(cod, t):
    alt_art = A4 + '; art. 122'
    g, nota = t['gab'], t['nota']
    extra = []
    if nota == 3: extra = [C('lote lindeiro ao Rio Capibaribe (art. 122, II; Obs. 3)', 24.0)]
    if nota == 4: extra = [C('lote lindeiro à Av. Boa Viagem (art. 122, I; Obs. 4) – dispensado com fachada ativa (art. 122 p.ú.)', 42.0)]
    if g:
        alt = P(float(g[0]), 'F02', alt_art, 'Medido até o piso da laje de coberta do último pavimento (art. 121).', 'm') if not extra else \
              P(None, 'F02', alt_art, 'Medido até o piso da laje de coberta do último pavimento (art. 121).', 'm', 'condicional', condicionais=[C('demais lotes', float(g[0]))] + extra)
        if cod == 'ZRU-1-B': alt['observacao'] += ' Empreendimento com fachada ativa fica dispensado do gabarito na ZRU 1 Setor B (art. 145, V).'
        pav = P(g[1], 'F02', A4, None, 'pavimentos')
    else:
        obs = 'Anexo IV: gabarito N/A – sem limite de altura fixado pela zona (controle por CA, TO e afastamentos).'
        alt = P(None, 'F02', alt_art, obs, 'm', 'condicional', condicionais=[C('demais lotes', forma='nao_aplicavel')] + extra) if extra else na('F02', alt_art, 'm', obs)
        pav = na('F02', A4, 'pavimentos', 'Anexo IV: N/A.')
    return alt, pav

def recuos(t):
    fr, lat = t['fr'], t['lat']
    if fr[0] is None:
        return {k: na('F02', A4, 'm') for k in ('frontal', 'lateral', 'fundos')}
    cf = [C('edificação até 8 pav e 26 m', float(fr[0])), C('edificação acima de 8 pav ou 26 m', float(fr[1])) if fr[1] is not None else C('edificação acima de 8 pav ou 26 m', forma='nao_aplicavel')]
    obs_f = ('Afastamento único para todos os pavimentos, definido pelo total de pavimentos/altura (art. 125 §7º). Obs. 2 do Anexo IV: pode ser zero quando dominante na face de quadra; '
             'até 2 pav pode seguir o afastamento dominante (art. 125 §8º); esquina com 7 m pode reduzir uma frente a 5 m (§9º).')
    lbl = ('até 2 pav e 8 m', 'de 3 a 8 pav e até 26 m', 'de 9 a 25 pav e até 80 m', 'acima de 25 pav ou 80 m')
    cl = [C(l, float(v)) if v is not None else C(l, forma='nao_aplicavel') for l, v in zip(lbl, lat)]
    obs_l = ('Até 2 pav: pode colar nas divisas até 8 m de altura em 2/3 do perímetro lateral+fundos (art. 125 §4º). Acima de 2 pav: os 2 primeiros pavimentos podem colar até 10 m '
             'em 2/3 das divisas (§5º, I). Pavimento enterrado: laterais/fundos nulos (§2º).')
    return {'frontal': P(None, 'F02', A4 + '; art. 125', obs_f, 'm', 'condicional', condicionais=cf),
            'lateral': P(None, 'F02', A4 + '; art. 125', obs_l, 'm', 'condicional', condicionais=cl),
            'fundos': P(None, 'F02', A4 + '; art. 125', obs_l, 'm', 'condicional', condicionais=[dict(c) for c in cl])}

def to_param(t):
    if t['to'][0] is None: return na('F02', A4 + '; arts. 126–127', 'fracao')
    conds = [C('edificação até 8 pav e 26 m (todos os pavimentos) / pavimentos enterrados, semienterrados e 4 primeiros acima do solo nas demais', formula='1 - TSN_minima(Anexo XVIII)')]
    conds.append(C('edificação acima de 8 pav ou 26 m – pavimentos acima do 4º', t['to'][1]) if t['to'][1] is not None else C('edificação acima de 8 pav ou 26 m', forma='nao_aplicavel'))
    return P(None, 'F02', A4 + '; arts. 126–127', 'TO calculada por pavimento (art. 126 p.ú.). Com fachada ativa: 45% acima do 4º pav; HIS com fachada ativa: 50% (art. 145, II–III).', 'fracao', 'condicional', condicionais=conds)

USOS = ['habitacional unifamiliar', 'habitacional multifamiliar', 'não habitacional', 'misto']
def usos(cod):
    obs = ('Uso habitacional (inclusive multifamiliar isolado ou conjunto, art. 99) e não habitacional admitidos em qualquer imóvel, salvo atividades de instalação restrita (art. 101, '
           'com licença ambiental prévia) ou proibida (abatedouros e fábricas de fogos/explosivos, art. 102). Sem lista de usos por zona.')
    if cod.startswith('ZAN'): obs += ' Na ZAN e nas Unidades de Conservação (camada unidades_protegidas) aplicam-se os planos de manejo/licenciamento ambiental (art. 63).'
    return P(USOS, 'F01', LP + ', arts. 98–102', obs, 'codigos_de_uso', 'lista')

VAGAS = P(0, 'F01', LP + ', art. 175', 'Não há exigência mínima de vagas para nenhum uso em nenhuma zona; PGV/PGT seguem o Manual de Estudo de Tráfego (arts. 104–108, 173).', 'vagas/UH')
DENS = P(None, 'F01', LP + ', arts. 113 e 119', 'A LPUOS não fixa densidade máxima; o adensamento populacional é induzido pela Cota-parte (nº MÍNIMO de UH), onde aplicável.', 'uh/ha', 'sem_dado')
LOTE = P(125.0, 'F01', LP + ', art. 58, II', 'Esquina: 250 m² (art. 59); novos lotes em vias arteriais: 450 m² (meio de quadra) / 540 m² (esquina) (art. 60). Quadra máx. 62.500 m² e 250 m (art. 56).', 'm2')
TEST = P(5.0, 'F01', LP + ', art. 58, I', 'Esquina: 15 m em cada frente (art. 59); vias arteriais: 15 m / 18 m (art. 60); lote engastado: 12 m (art. 61).', 'm')

def parametros(cod, t):
    ca = t['ca']
    alt, pav = gab(cod, t)
    out = {'indice_areas_comuns': P(t['iac'], 'F02', A4 + '; art. 117', 'Fator × CA máximo = coeficiente máximo de áreas comuns não computáveis. HIS: 0,75 (art. 115; Obs. 1).', 'fator') if t['iac'] else na('F02', A4, 'fator'),
           'cota_parte': P(float(t['cota']), 'F02', A4 + '; art. 119', 'Nº MÍNIMO de UH = área do terreno ÷ cota-parte (multifamiliar ou misto). Dispensado em terrenos < 1.500 m² (art. 119 §2º).', 'm2/UH') if t['cota'] else na('F02', A4 + '; art. 119', 'm2/UH'),
           'taxa_contribuicao_ambiental': tca_param(cod)}
    if cod.startswith('ZAN'): out['taxa_contribuicao_ambiental'] = tca_param('ZAN-CAPIBARIBE')
    return {
        'ca_minimo': P(ca[0], 'F02', A4, 'Abaixo do CA mínimo o imóvel pode ser considerado subutilizado (PD).', 'coeficiente') if ca[0] is not None else na('F02', A4, 'coeficiente'),
        'ca_basico': P(ca[1], 'F02', A4, None, 'coeficiente'),
        'ca_maximo': P(ca[2], 'F02', A4, 'Potencial acima do básico mediante OODC (Lei 18.900/2022) ou TDC, nos termos do Plano Diretor (LC 02/2021).' if ca[2] > ca[1] else None, 'coeficiente'),
        'taxa_ocupacao': to_param(t),
        'gabarito_altura_max_m': alt, 'gabarito_pavimentos': pav,
        'taxa_permeabilidade': tsn_param(cod) if not cod.startswith('ZAN-ORLA') else tsn_param('ZAN-ORLA'),
        'recuos': recuos(t), 'lote_minimo_m2': LOTE, 'testada_minima_m': TEST,
        'usos_permitidos': usos(cod), 'vagas': VAGAS, 'densidade': DENS, 'outros': out}

def categoria(cod):
    for k in ('ZAN', 'ZDS', 'ZONA-CENTRO', 'ZRU', 'ZAC-PLANICIE', 'ZAC-MORRO', 'ZAC-ORLA'):
        if cod.startswith(k): return CATEG[k]

zonas = []
ORDEM = ['ZAN-ORLA', 'ZAN-CAPIBARIBE', 'ZAN-TEJIPIO', 'ZAN-BEBERIBE', 'ZDS-BEBERIBE', 'ZDS-CAPIBARIBE-A', 'ZDS-CAPIBARIBE-B', 'ZDS-CAPIBARIBE-C', 'ZDS-TEJIPIO', 'ZDS-CENTRO',
         'ZONA-CENTRO', 'ZRU-1-A', 'ZRU-1-B', 'ZRU-1-C', 'ZAC-PLANICIE-1-A', 'ZAC-PLANICIE-1-B', 'ZAC-PLANICIE-2', 'ZAC-MORRO', 'ZAC-ORLA']
for cod in ORDEM:
    t = A4T[cod]; nome, desc = NOMES[cod]; cat, crit = categoria(cod)
    macro = 'MANC' if cod.startswith(('ZAN', 'ZDS')) else 'MAC'
    obs = [f'Macrozona: {macro} (arts. 6º–7º).', 'Parâmetros do Anexo IV conforme redação final aprovada (Parecer 75/2025) e sancionada sem alteração de numeração (DOM 04/10/2025).']
    if cod == 'ZRU-1-C': obs.append('OODC: aquisição de potencial entre CA 1 e 3 por OODC; entre 3 e 5, OODC + retrofit de imóvel em SPS das ZEPH Boa Vista, Bairro do Recife ou Santo Antônio/São José (art. 168), com isenção da OODC desta faixa nos 5 primeiros anos.')
    if cod == 'ZAN-ORLA': obs.append('Faixa de praia: CA 1/1 e demais parâmetros N/A no Anexo IV.')
    if cod in ('ZDS-CAPIBARIBE-A', 'ZDS-CAPIBARIBE-B'): obs.append('Índice de Áreas Comuns 0,4 em célula mesclada dos Setores A e B (conferido na imagem do Anexo IV).')
    zonas.append(dict(codigo=cod, nome=nome, descricao=desc, tipo='base', prioridade=0, categoria_normalizada=cat, categoria_criterio=crit, regra_sobreposicao=None,
                      parametros=parametros(cod, t), observacoes=obs,
                      geometria=fc([feat(ZON[cod], cod, nome=nome, macrozona=macro)], FONTE_GEO_BASE, False, OBS_BASE)))

# ------------------------- zonas sobrepostas -------------------------
def sd(fid, art, un, obs):
    return P(None, fid, art, obs, un, 'sem_dado')

ZEIS_CA = {'ZEIS-1-PLANICIE': (0.5, 1, 2), 'ZEIS-1-MORRO': (0.3, 1, 2), 'ZEIS-2': (0.5, 1, 4)}
ZEIS_NOME = {'ZEIS-1-PLANICIE': ('ZEIS 1 Planície', 'Zonas Especiais de Interesse Social 1 – Planície: assentamentos de baixa renda a regularizar (PREZEIS, Lei 16.113/1995).'),
             'ZEIS-1-MORRO': ('ZEIS 1 Morro', 'Zonas Especiais de Interesse Social 1 – Morro: assentamentos de baixa renda em morros a regularizar (PREZEIS).'),
             'ZEIS-2': ('ZEIS 2', 'Zonas Especiais de Interesse Social 2: áreas/vazios destinados à produção de HIS (art. 65 do Plano Diretor).')}
for cod in ('ZEIS-1-PLANICIE', 'ZEIS-1-MORRO', 'ZEIS-2'):
    ca = ZEIS_CA[cod]; nome, desc = ZEIS_NOME[cod]
    plano = 'Conforme Plano de Regularização Urbanística da ZEIS – PREZEIS e disposições do Plano Diretor (Anexo IV).' if cod != 'ZEIS-2' else 'Conforme plano específico da ZEIS 2 e disposições do Plano Diretor (Anexo IV).'
    par = {'ca_minimo': P(ca[0], 'F02', A4, None, 'coeficiente'), 'ca_basico': P(ca[1], 'F02', A4, None, 'coeficiente'),
           'ca_maximo': P(ca[2], 'F02', A4, None, 'coeficiente'),
           'taxa_ocupacao': sd('F02', A4, 'fracao', plano), 'gabarito_altura_max_m': sd('F02', A4, 'm', plano), 'gabarito_pavimentos': sd('F02', A4, 'pavimentos', plano),
           'taxa_permeabilidade': tsn_param('ZEIS'),
           'recuos': {k: sd('F02', A4, 'm', plano) for k in ('frontal', 'lateral', 'fundos')},
           'lote_minimo_m2': sd('F01', LP + ', art. 62', 'm2', 'Dimensão dos lotes definida no plano urbanístico específico da ZEIS (art. 62).'),
           'testada_minima_m': sd('F01', LP + ', art. 62', 'm', 'Definida no plano urbanístico específico da ZEIS (art. 62).'),
           'usos_permitidos': P(USOS, 'F01', LP + ', arts. 98–102 e 111', 'Percentuais de destinação de usos em ZEIS conforme art. 74 do Plano Diretor (art. 111) – PD não acessado.', 'codigos_de_uso', 'lista'),
           'vagas': P(0, 'F01', LP + ', arts. 175 e 183', 'Sem mínimo de vagas (art. 175); requisitos de mobilidade em ZEIS com análise especial conjunta (art. 183).', 'vagas/UH'),
           'densidade': DENS,
           'outros': {'indice_areas_comuns': P(0.5, 'F02', A4 + '; art. 117', 'HIS: 0,75 (art. 115; Obs. 1).', 'fator'),
                      'taxa_contribuicao_ambiental': tca_param('ZEIS')}}
    zonas.append(dict(codigo=cod, nome=nome, descricao=desc, tipo='sobreposta', prioridade=20, categoria_normalizada='especial_interesse_social',
        categoria_criterio='Zona Especial de Interesse Social (arts. 8º e 11–17).',
        regra_sobreposicao=dict(efeito='substitui', limiar_pct=0, fundamento='Art. 8º: zonas especiais têm parâmetros próprios independentemente da zona a que se sobrepõem; Anexo IV fixa CA/IAC e remete o resto ao plano da ZEIS.',
                                alerta='ZEIS: parcelamento, ocupação e mobilidade dependem do plano urbanístico da ZEIS (PREZEIS/COMUL) – consultar a Prefeitura.'),
        parametros=par, observacoes=['Anexo III lista 117 ZEIS (contagem automática do texto: 73 ZEIS 1 Planície, 13 ZEIS 1 Morro, 31 ZEIS 2).',
            'Art. 15 cria 16 novas ZEIS 1 (' + ', '.join(ZEIS1_NOVAS) + '); art. 16 amplia Aritana e Vila Esperança/Cabocó.',
            'Geometria agrega todas as ZEIS da categoria; o mapa não traz nomes legíveis por polígono.'],
        geometria=fc([feat(ZEIS[cod], cod, nome=nome)], 'Lei 19.426/2025, Anexo II – Mapa 3A (redação final, SETEMBRO/2025): ' + URL_RF, False,
                     'Mapa 3A da redação final registrado (ORB+RANSAC, %d pontos, resíduo médio %.1f px) sobre o Mapa 3A do PLE e georreferenciado pela grade UTM. Erro estimado ≈50–60 m.' % (LOG['registro_RF_m3a_zeis']['inliers'], LOG['registro_RF_m3a_zeis']['residuo_medio_px']))))

t = A4T['ZEC-1']; pz = parametros('ZEC-1', t)
zonas.append(dict(codigo='ZEC-1', nome='ZEC 1', descricao='Zona Especial de Centralidade 1: Afogados, Água Fria, Areias, Beberibe, Casa Amarela, Encruzilhada e Praça de Boa Viagem (arts. 18–20-B).',
    tipo='sobreposta', prioridade=15, categoria_normalizada='centralidade', categoria_criterio='Zona Especial de Centralidade (art. 18), CA máx 5.',
    regra_sobreposicao=dict(efeito='substitui', limiar_pct=0, fundamento='Art. 8º e Anexo IV (linha ZEC 1). Onde houver sobreposição com ZEPH prevalecem os parâmetros da ZEPH (art. 19 §2º).'),
    parametros=pz, observacoes=['ZEC 1 Praça de Boa Viagem (art. 20-A): Setor A – potencial adicional via OODC; Setor B – CA 1→3 via OODC e 3→5 OODC + retrofit (art. 168).',
        'ZEC 1 Encruzilhada (art. 20-B): Setor A via OODC; Setor B – CA 1→4 via OODC e 4→5 com retrofit.',
        'ZEC 2 e ZEC 3: perímetros a definir por plano específico; até lá valem os parâmetros da zona de base (art. 20 §2º) – ver camada zec_2_3_indicacao.'],
    geometria=fc([feat(ZEC['ZEC-1'], 'ZEC-1', nome='ZEC 1')], 'Lei 19.426/2025, Anexo II – Mapa 3B (PLE e redação final): ' + URL_PLE + ' ; ' + URL_RF, False,
                 'Base: Mapa 3B do PLE (1213x1710 px) + ampliações do Mapa 3B da redação final (imagem de só 375x566 px; registro com resíduo médio %.1f px da imagem ampliada). '
                 'Ampliações da Praça de Boa Viagem e Encruzilhada grosseiras (erro ≈100 m); setores A/B não separados.' % LOG['registro_RF_m3b_zec']['residuo_medio_px'])))

ZEPH_NOME = {'ZEPH-SPS': ('ZEPH – Setor de Preservação da Significância (SPS)', 'SPS das 47 ZEPH (art. 25): transformações sob análise especial (art. 23; Lei 13.957/1979).'),
             'ZEPH-SPM': ('ZEPH – Setor de Preservação da Morfologia (SPM)', 'SPM das ZEPH: análise especial (art. 23).'),
             'ZEPH-SPPI': ('ZEPH – Setor de Preservação do Patrimônio Imaterial (SPPI)', 'SPPI das ZEPH: análise especial (art. 23).'),
             'ZEPH-SPA': ('ZEPH – Setor de Preservação da Ambiência (SPA)', 'SPA das ZEPH: parâmetros numéricos próprios por ZEPH/setor no Anexo V (art. 22).')}
AV = 'Lei 19.426/2025, Anexo V – Parâmetros e Requisitos Especiais para ZEPH (redação final)'
for cod in ('ZEPH-SPS', 'ZEPH-SPM', 'ZEPH-SPPI', 'ZEPH-SPA'):
    nome, desc = ZEPH_NOME[cod]
    esp = 'Análise especial pelo órgão de preservação (Anexo V; art. 23 §4º).' if cod != 'ZEPH-SPA' else 'Varia por ZEPH e por SPA-n no Anexo V; a geometria não distingue a ZEPH individual – consultar o Anexo V.'
    if cod == 'ZEPH-SPA':
        g_alt = P(None, 'F02', AV, 'Gabarito do SPA por ZEPH (lista parcial extraída do Anexo V; ZEPH ausentes aqui devem ser lidas no quadro).', 'm', 'condicional',
                  condicionais=[C(n, float(a)) for n, a, p in SPA_GAB])
        g_pav = P(None, 'F02', AV, 'Pavimentos do SPA por ZEPH (lista parcial).', 'pavimentos', 'condicional', condicionais=[C(n, p) for n, a, p in SPA_GAB])
        ca_b = P(None, 'F02', AV, 'O Anexo V remete o CA/controle de adensamento do SPA à zona de base indicada em cada linha (ex.: ZDS Capibaribe Setor A).', 'coeficiente', 'herda_da_base')
        perm = P(None, 'F02', A18, 'TSN/TCA do SPA conforme Anexo V (Obs. 1 do Anexo XVIII).', 'fracao', 'sem_dado')
    else:
        g_alt = sd('F02', AV, 'm', esp); g_pav = sd('F02', AV, 'pavimentos', esp)
        ca_b = sd('F02', AV, 'coeficiente', esp)
        perm = P(None, 'F02', A18, 'Anexo XVIII: análise especial.', 'fracao', 'sem_dado')
    par = {'ca_minimo': ca_b if cod == 'ZEPH-SPA' else sd('F02', AV, 'coeficiente', esp), 'ca_basico': ca_b, 'ca_maximo': ca_b,
           'taxa_ocupacao': sd('F02', AV, 'fracao', esp), 'gabarito_altura_max_m': g_alt, 'gabarito_pavimentos': g_pav, 'taxa_permeabilidade': perm,
           'recuos': {k: sd('F02', AV, 'm', esp) for k in ('frontal', 'lateral', 'fundos')},
           'lote_minimo_m2': sd('F02', AV + ', Requisitos Gerais III', 'm2', 'Parcelamento em ZEPH segue requisitos especiais do Anexo V.'), 'testada_minima_m': sd('F02', AV, 'm', 'Requisitos especiais do Anexo V.'),
           'usos_permitidos': P(USOS, 'F01', LP + ', arts. 98–102; Anexo V', 'Usos gerais da LPUOS, sujeitos aos requisitos especiais da ZEPH.', 'codigos_de_uso', 'lista'),
           'vagas': P(0, 'F01', LP + ', arts. 175 e 183', 'Sem mínimo (art. 175); mobilidade em ZEPH com análise especial (art. 183).', 'vagas/UH'), 'densidade': DENS, 'outros': {}}
    zonas.append(dict(codigo=cod, nome=nome, descricao=desc, tipo='sobreposta', prioridade=30, categoria_normalizada='patrimonio_cultural',
        categoria_criterio='Zona Especial de Preservação do Patrimônio Histórico-Cultural (arts. 21–25).',
        regra_sobreposicao=dict(efeito='substitui', limiar_pct=0, fundamento='Art. 8º; Anexo V; prevalência da ZEPH sobre ZEC (art. 19 §2º). Planos específicos vigentes: Leis 16.290/1997 e 18.046/2014 (art. 24 §3º).',
                                alerta='ZEPH: projeto sujeito a análise do órgão municipal de preservação (e IPHAN/FUNDARPE quando tombado).'),
        parametros=par, observacoes=['47 ZEPH listadas no art. 25.', 'Geometria agrega os setores de todas as ZEPH.'],
        geometria=fc([feat(ZEPH[cod], cod, nome=nome)], 'Lei 19.426/2025, Anexo II – Mapa 3C (redação final, SETEMBRO/2025): ' + URL_RF, False,
                     'Mapa 3C da redação final registrado (%d pontos, resíduo médio %.1f px) sobre o Mapa 3C do PLE e georreferenciado pela grade UTM. Erro estimado ≈50–60 m; ZEPH pequenas (monumentos isolados) podem ter perdido detalhe.' % (LOG['registro_RF_m3c_zeph']['inliers'], LOG['registro_RF_m3c_zeph']['residuo_medio_px']))))

# ------------------------- camadas complementares -------------------------
cam = {}
cam['macrozonas'] = dict(papel='macrozona', descricao='Macrozonas da LPUOS/PD: MANC – Macrozona de Ambiente Natural e Cultural; MAC – Macrozona de Ambiente Construído (arts. 4º–7º; Anexo II – Mapa 1).',
    fonte='Lei 19.426/2025, Anexo II – Mapa 1 (PLE 16/2025): ' + URL_PLE, oficial=False, observacao='Vetorização do raster pela grade UTM; erro ≈50 m.', fonte_id='F03', artigo_anexo='Lei 19.426/2025, arts. 4º–7º; Anexo II, Mapa 1',
    parametros_por_codigo=None, alerta_por_codigo={'MANC': 'Macrozona de Ambiente Natural e Cultural (ZAN/ZDS): CA máx 1–2; EIV para construção > 15.000 m² (Anexo XV).',
                                                   'MAC': 'Macrozona de Ambiente Construído: CA máx 1,5–5; EIV para construção > 20.000 m² (exceto HIS; HIS > 30.000 m²) (Anexo XV).'},
    features=[feat(MAC[k], k) for k in ('MANC', 'MAC')])
UPN = {'UCN': 'Unidade de Conservação da Natureza: parcelamento conforme plano de manejo e licenciamento prévio; lote mín. 10.000 m² no SCA e 500 m² no SEA (art. 63).',
       'IPAV': 'Imóvel de Proteção de Área Verde: restrição ambiental à ocupação – consultar órgão ambiental.',
       'UCP': 'Unidade de Conservação da Paisagem: restrição à ocupação.', 'PARQUE-PRACA': 'Parque/praça protegida.', 'JARDIM-HISTORICO': 'Jardim histórico protegido.'}
cam['unidades_protegidas'] = dict(papel='restricao', descricao='Unidades protegidas do Anexo II – Mapa 6 (UCN, UCP, IPAV, parques/praças, jardins históricos).',
    fonte='Lei 19.426/2025, Anexo II – Mapa 6 (PLE 16/2025): ' + URL_PLE, oficial=False, observacao='Vetorização por cor do raster; classes agregadas, sem nome por unidade; erro ≈50 m.',
    fonte_id='F03', artigo_anexo='Lei 19.426/2025, Anexo II, Mapa 6; art. 63', parametros_por_codigo=None, alerta_por_codigo={k: UPN[k] for k in UP},
    features=[feat(UP[k], k) for k in UP])
cam['zec_2_3_indicacao'] = dict(papel='informativa', descricao='Indicação de localização das ZEC 2 e ZEC 3 no Mapa 3B – perímetros ainda não definidos (art. 20 §2º).',
    fonte='Lei 19.426/2025, Anexo II – Mapa 3B (PLE): ' + URL_PLE, oficial=False, observacao='Símbolos de localização, não perímetros.', fonte_id='F02', artigo_anexo='Lei 19.426/2025, art. 20 §2º; Anexo IV (ZEC 2/3: conforme plano específico)',
    parametros_por_codigo=None, alerta_por_codigo={'ZEC-2-3': 'ZEC 2/3 sem perímetro: valem os parâmetros da zona de base até o plano específico.'}, features=[feat(Z23[k], k) for k in Z23])

macrozonas = [dict(codigo='MANC', nome='Macrozona de Ambiente Natural e Cultural', descricao='ZAN Beberibe, Capibaribe, Tejipió e Orla; ZDS Beberibe, Capibaribe, Tejipió e Centro (art. 6º).',
                   parametros={'limiar_eiv_m2': P(15000, 'F02', 'Lei 19.426/2025, Anexo XV – regra geral', 'Área total de construção acima da qual é Empreendimento de Impacto (EIV).', 'm2')}),
              dict(codigo='MAC', nome='Macrozona de Ambiente Construído', descricao='Zona Centro, ZRU 1 (Setores A/B/C), ZAC Planície 1 e 2, ZAC Morro, ZAC Orla (art. 7º).',
                   parametros={'limiar_eiv_m2': P(20000, 'F02', 'Lei 19.426/2025, Anexo XV – regra geral', 'Exceto HIS, cujo limiar na MAC é 30.000 m².', 'm2')})]

def it(chave, titulo, valor, unidade, fid, art, obs=None, forma=None, **kw):
    return dict(chave=chave, titulo=titulo, **P(valor, fid, art, obs, unidade, forma, **kw))

outorga = dict(resumo='OODC regida pelo Plano Diretor (LC 02/2021, arts. 115–123) e pela Lei 18.900/2022 (ambos em hosts da Prefeitura inacessíveis do ambiente de coleta). A LPUOS fixa, por zona, CA mínimo/básico (1 em todas)/máximo (Anexo IV), e regras especiais: ZRU 1 Setor C e ZEC 1 Praça de Boa Viagem/Encruzilhada com faixas de CA condicionadas a retrofit em ZEPH (arts. 20-A, 20-B, 168). Fórmula de contrapartida não verificada.',
    fonte_id='F01', artigo_anexo='Lei 19.426/2025, Anexo IV; arts. 20-A, 20-B, 116 §4º, 168', itens=[
    it('ca_basico', 'CA básico (todas as zonas)', 1, 'coeficiente', 'F02', A4),
    it('ca_maximo_por_zona', 'CA máximo por zona', None, 'coeficiente', 'F02', A4, 'Potencial entre o básico e o máximo adquirido por OODC/TDC.', 'condicional',
       condicionais=[C('ZAN (todas)', 1), C('ZDS (todas)', 2), C('Zona Centro', 5), C('ZRU 1 (A, B, C)', 5), C('ZAC Planície 1 e 2', 4), C('ZAC Morro', 1.5), C('ZAC Orla', 3),
                     C('ZEIS 1', 2), C('ZEIS 2', 4), C('ZEC 1', 5)]),
    it('lei_oodc', 'Lei específica da OODC', None, None, 'F06', 'Lei 18.900/2022', 'Citada pela LPUOS (arts. 116 §4º e 168); texto não acessado – ver lacunas.', 'sem_dado'),
    it('zru1c_retrofit', 'ZRU 1 Setor C – potencial condicionado a retrofit em ZEPH', None, 'coeficiente', 'F01', LP + ', art. 168', 'Fatores de Planejamento e de Interesse Social da ZRU 1; OODC da faixa 3→5 isenta nos 5 primeiros anos de vigência; habite-se do retrofit (emitido desde 01/01/2025) é condição do habite-se na ZRU 1-C.', 'condicional',
       condicionais=[C('CA 1 → 3', forma='texto', texto='mediante pagamento de contrapartida via OODC'), C('CA 3 → 5', forma='texto', texto='OODC acompanhada da comprovação de reforma ou retrofit em imóveis nos SPS das ZEPH Boa Vista, Bairro do Recife e Santo Antônio/São José')]),
    it('his_publica_centro', 'HIS pública na Zona Centro e ZDS Centro', None, None, 'F01', LP + ', art. 168 §2º', 'Áreas privativas habitacionais de empreendimentos públicos de HIS na Zona Centro e ZDS Centro recebem a mesma condição do art. 168.', 'livre'),
    it('zec1_pba', 'ZEC 1 Praça de Boa Viagem – Setor B', None, None, 'F01', LP + ', art. 20-A', 'CA 1→3 via OODC; 3→5 OODC + retrofit (art. 168). Setor A: OODC.', 'livre'),
    it('zec1_encruzilhada', 'ZEC 1 Encruzilhada – Setor B', None, None, 'F01', LP + ', art. 20-B', 'CA 1→4 via OODC; 4→5 OODC + retrofit. Setor A: OODC.', 'livre'),
    it('bonus_certificacao', 'Bônus por certificação ambiental', 0.10, 'fracao_area_privativa', 'F01', LP + ', art. 116, II e §1º; Anexo XVI', 'Até 10% de área privativa não computável conforme categoria do certificado; perda da certificação → multa equivalente ao dobro da OODC (§4º).'),
    it('nao_computaveis', 'Áreas não computáveis no CA', None, None, 'F01', LP + ', arts. 114, 116, 118, 151', 'Áreas de parâmetros qualificadores do espaço público (fachada ativa, térreo visitável, fruição pública), áreas privativas descobertas, jardineiras ≤1 m, áreas comuns até o IAC, bicicletários.', 'livre'),
    it('tdc', 'Transferência do Direito de Construir', None, None, 'F01', 'Plano Diretor (LC 02/2021) / Lei 18.901/2022', 'A LPUOS não regula a TDC; lei específica não acessada – ver lacunas.', 'sem_dado')])

zeis_his = dict(resumo='ZEIS 1 (Planície/Morro – regularização via PREZEIS, Lei 16.113/1995) e ZEIS 2 (vazios para HIS, art. 65 do PD); 117 ZEIS no Anexo III, 16 criadas e 2 ampliadas pela LPUOS. Anexo IV fixa só CA (ZEIS 1: máx 2; ZEIS 2: máx 4) e IAC; o resto segue o plano de cada ZEIS. Incentivos HIS: IAC 0,75 convertível em área privativa não computável, dispensa de TCA e de parâmetros do espaço público quando exigido por programa habitacional (ex.: MCMV), TO 50% acima do 4º pav com fachada ativa, blocos até 80 m, EIV só acima de 30.000 m² na MAC, sem mínimo de vagas.',
    fonte_id='F01', artigo_anexo='Lei 19.426/2025, arts. 11–17, 26–30, 62, 111, 115, 145, 164, 168 §2º, 175, 200; Anexos III, IV e XV', itens=[
    it('tipos_zeis', 'Tipos de ZEIS', None, None, 'F01', LP + ', arts. 11–14', 'ZEIS 1 (Planície e Morro): assentamentos de baixa renda – PREZEIS (Lei 16.113/1995). ZEIS 2: art. 65 do PDMR, parâmetros na LPUOS/PD e leis específicas (art. 14).', 'livre'),
    it('zeis_listadas', 'ZEIS listadas no Anexo III', 117, 'zonas', 'F02', 'Lei 19.426/2025, Anexo III', 'Contagem automática do texto: 73 ZEIS 1 Planície, 13 ZEIS 1 Morro, 31 ZEIS 2.'),
    it('zeis_novas', 'ZEIS 1 criadas pela LPUOS', 16, 'zonas', 'F01', LP + ', art. 15', ', '.join(ZEIS1_NOVAS) + '. Ampliadas: Aritana e Vila Esperança/Cabocó (art. 16).'),
    it('ca_zeis', 'CA nas ZEIS', None, 'coeficiente', 'F02', A4, None, 'condicional',
       condicionais=[C('ZEIS 1 Planície – mín/bás/máx 0,5/1/2', 2, codigo='ZEIS-1-PLANICIE'), C('ZEIS 1 Morro – mín/bás/máx 0,3/1/2', 2, codigo='ZEIS-1-MORRO'), C('ZEIS 2 – mín/bás/máx 0,5/1/4', 4, codigo='ZEIS-2')]),
    it('iac_his', 'Índice de Áreas Comuns para HIS', 0.75, 'fator', 'F01', LP + ', art. 115; Anexo IV Obs. 1', 'Pode ser convertido em área privativa não computável se o total ≤ CA máx + IAC e as áreas comuns ≥ 0,30 do CA máx (art. 115, I–II; art. 116, V).'),
    it('dispensa_tca_his', 'Dispensa de TCA e parâmetros do espaço público', None, None, 'F01', LP + ', art. 164', 'HIS pode ser dispensada da Taxa de Contribuição Ambiental e dos parâmetros de qualificação do espaço público quando exigido por regras de programa público de financiamento habitacional (memorial justificativo).', 'livre'),
    it('to_his_fachada_ativa', 'TO acima do 4º pav para HIS com fachada ativa', 0.5, 'fracao', 'F01', LP + ', art. 145, III', 'Edificações com mais de 8 pav; demais usos 45% (art. 145, II); padrão 40%.'),
    it('bloco_his', 'Comprimento máximo de bloco em HIS (com fachada ativa)', 80, 'm', 'F01', LP + ', art. 145, IV'),
    it('eiv_his', 'Limiar de EIV para HIS na MAC', 30000, 'm2', 'F02', 'Lei 19.426/2025, Anexo XV', 'Área total de construção; regra geral MAC 20.000 m² (exceto HIS) e MANC 15.000 m².'),
    it('vagas_his', 'Vagas mínimas', 0, 'vagas/UH', 'F01', LP + ', art. 175', 'Sem mínimo de vagas para qualquer uso.'),
    it('compartimentos_his', 'Compartimentos de HIS', None, None, 'F01', LP + ', art. 200', 'Até a revisão da Lei 16.292/1997, dimensões, iluminação e ventilação de HIS seguem normas ABNT, dispensadas as tabelas do Anexo II daquela lei.', 'livre'),
    it('ieis', 'Imóveis Especiais de Interesse Social (IEIS)', None, None, 'F01', LP + ', arts. 26–30; Anexo VI', 'Imóveis subutilizados classificados por decreto/lei (até 5 anos) para HIS; ampliação para HIS não computada no CA, análise prioritária e assistência técnica.', 'livre'),
    it('his_retrofit_centro', 'HIS pública no Centro', None, None, 'F01', LP + ', art. 168 §2º', 'Mesmas condições do art. 168 para HIS pública na Zona Centro e ZDS Centro.', 'livre'),
    it('his_equipamentos', 'HIS em áreas de equipamentos públicos', None, None, 'F01', LP + ', art. 51', 'Implantação integrada de HIS (locação social) em áreas destinadas a equipamentos públicos, sempre que tecnicamente possível.', 'livre'),
    it('usos_zeis', 'Percentuais de usos em ZEIS', None, None, 'F01', LP + ', art. 111', 'Remete ao art. 74 do Plano Diretor (não acessado).', 'sem_dado'),
    it('definicao_his_renda', 'Definição de HIS (faixa de renda)', None, None, None, None, 'Não definida na LPUOS; depende do PD/PLHIS (Lei 18.863/2021) – não acessados.', 'sem_dado')])

outros = dict(resumo='EIV para Empreendimentos de Impacto (Anexo XV: MANC >15.000 m², MAC >20.000 m², HIS na MAC >30.000 m² e atividades listadas); PGV/PGT com Estudo de Tráfego; gabaritos de 42 m na Av. Boa Viagem e 24 m às margens do Capibaribe; cota-parte; isenção de parâmetros para obras pequenas; vigência e transição.',
    fonte_id='F01', artigo_anexo='Lei 19.426/2025', itens=[
    it('eiv', 'Empreendimentos de Impacto / EIV', None, 'm2', 'F02', 'Lei 19.426/2025, arts. 109–110; Anexo XV', 'Também: aterros, autódromos, cemitérios, centrais de carga, depósitos de inflamáveis, indústrias ≥1.000 m², ETA/ETE, estádios, presídios, shoppings, terminais, OUC e obras viárias de grande porte.', 'condicional',
       condicionais=[C('MANC – área total de construção >', 15000), C('MAC – área total de construção > (exceto HIS)', 20000), C('HIS na MAC – área total de construção >', 30000)]),
    it('pgv', 'Polos Geradores de Viagens/Tráfego', None, None, 'F01', LP + ', arts. 104–108', 'Definidos no Manual de Estudo de Tráfego (Lei 18.887/2021); se também empreendimento de impacto, o Estudo de Tráfego integra o EIV.', 'livre'),
    it('gabarito_av_boa_viagem', 'Gabarito em lotes lindeiros à Av. Boa Viagem', 42, 'm', 'F01', LP + ', art. 122, I', 'Dispensado com fachada ativa (art. 122 p.ú.).'),
    it('gabarito_rio_capibaribe', 'Gabarito em lotes lindeiros ao Rio Capibaribe', 24, 'm', 'F01', LP + ', art. 122, II'),
    it('cota_parte_dispensa', 'Dispensa de cota-parte', 1500, 'm2', 'F01', LP + ', art. 119 §2º', 'Terrenos menores que 1.500 m² dispensados da cota-parte (nº mínimo de UH).'),
    it('pequenas_obras', 'Isenção de parâmetros para obras pequenas', None, None, 'F01', LP + ', art. 163', 'Até 400 m² construídos, até 2 pav, lote ≤500 m², TSN ≥20% e demais requisitos: desobrigadas dos parâmetros de ocupação.', 'livre'),
    it('fachada_ativa', 'Fachada ativa / térreo visitável / fruição pública', None, None, 'F01', LP + ', arts. 143–151', 'Áreas não computáveis; faixa de amenização 2 m; TO 45% acima do 4º pav; ZRU 1-B sem gabarito.', 'livre'),
    it('conversao_garagens', 'Conversão de garagens em UH', None, None, 'F01', LP + ', art. 167', 'Edificações regularizadas podem converter estacionamento em UH, isento de CA até o básico e de cota-parte.', 'livre'),
    it('plano_quadra', 'Plano de Quadra', None, None, 'F01', LP + ', arts. 169–170', 'Redistribuição de parâmetros entre lotes da quadra por decreto, com anuência de todos os proprietários.', 'livre'),
    it('reservatorio', 'Reservatório de retardo/acúmulo de águas pluviais', None, None, 'F01', LP + ', art. 129, III', 'Parâmetro de qualificação ambiental (ver arts. 133 e seguintes).', 'livre'),
    it('vigencia', 'Vigência da LPUOS', None, None, 'F01', LP + ', art. 204', 'Publicada no DOM de 04/10/2025; entra em vigor 60 dias após a publicação (≈03/12/2025). Vigente em 27/10/2026.', 'livre'),
    it('transicao', 'Transição', None, None, 'F01', LP + ', art. 190', 'Processos protocolados antes da vigência seguem a lei anterior; VEI deferida/tramitando dentro da validade pode usar a lei anterior.', 'livre'),
    it('revogacoes', 'Revogações', None, None, 'F01', LP + ', art. 201', 'Revoga, entre outras, as Leis 16.176/1996 (LUOS anterior), 16.286/1997, 16.719/2001 (ARU) e 18.112/2015.', 'livre'),
    it('operacoes_urbanas', 'Operações urbanas consorciadas', None, None, 'F02', 'Lei 19.426/2025, Anexo XV', 'OUC listada como empreendimento de impacto; nenhuma OUC vigente identificada nas fontes acessíveis.', 'sem_dado')])

resumo_mcmv = [
    'Multifamiliar (isolado ou conjunto) é permitido em todas as zonas – não há lista de usos por zona; só atividades restritas/proibidas são controladas (arts. 98–102).',
    'CA básico 1 em toda a cidade; máx 2 na MANC (ZDS) e 1,5–5 na MAC (ZAC Planície 4, ZRU 1/Zona Centro/ZEC 1: 5); acima do básico paga-se OODC (Lei 18.900/2022 – não acessada). ZEIS 2: CA máx 4.',
    'Sem exigência mínima de vagas para nenhum uso (art. 175) – grande vantagem para HIS/MCMV.',
    'HIS: IAC 0,75 (áreas comuns não computáveis, conversíveis em privativa – art. 115); dispensa de TCA e parâmetros do espaço público se o programa (MCMV) exigir (art. 164); TO 50% acima do 4º pav com fachada ativa; blocos até 80 m (art. 145).',
    'EIV: HIS na MAC só acima de 30.000 m² construídos (demais: 20.000 m²); na MANC, 15.000 m² (Anexo XV).',
    'Cota-parte impõe nº MÍNIMO de UH em terrenos ≥1.500 m² na Zona Centro (30 m²/UH), ZRU 1-A (30), ZRU 1-B (35) e ZEC 1 (40) – favorece unidades compactas.',
    'TO: 100% − TSN até 8 pav/26 m; acima, 40% nos pavimentos acima do 4º. TSN mínima de 10–60% conforme zona e tamanho do lote (Anexo XVIII); ZEIS 10–20%.',
    'Gabarito livre na maior parte da cidade; limites: ZDS Capibaribe A 26 m/8 pav, B 51 m/16 pav, ZRU 1-B e ZAC Planície 1-A 65 m/20 pav; 42 m na Av. Boa Viagem e 24 m às margens do Capibaribe (art. 122).',
    'Lote mínimo 125 m² e testada 5 m (art. 58); em ZEIS os lotes seguem o plano urbanístico (art. 62).',
    'Centro: HIS pública na Zona Centro/ZDS Centro com as condições do art. 168; IEIS (imóveis subutilizados para HIS) com ampliação não computável e análise prioritária (arts. 26–30).',
]

lacunas = [
    dict(item='Plano Diretor do Recife (LC 02/2021)', motivo='Só publicado em hosts *.recife.pe.gov.br, que recusam conexão a partir do ambiente de coleta (TLS encerrado); sapl.recife.pe.leg.br retornou 503. Referências ao PD vêm apenas da LPUOS.'),
    dict(item='Lei 18.900/2022 (OODC) – fórmula, fatores e isenções', motivo='Página oficial https://licenciamentounificado.recife.pe.gov.br/189002022 inacessível; não usada fonte secundária.'),
    dict(item='Lei 18.901/2022 (TDC) e demais leis de instrumentos (IPTU progressivo, OUC)', motivo='Mesmos hosts bloqueados.'),
    dict(item='Camadas vetoriais oficiais (ESIG/dados abertos da Prefeitura)', motivo='esigportal2, dados.recife e licenciamentounificado bloqueados; não se contornou bloqueio. Geometrias vetorizadas dos mapas raster da lei (oficial:false).'),
    dict(item='Anexo XX (coordenadas dos perímetros)', motivo='Na redação final o Anexo XX é um link para planilha Google Sheets (não é publicação oficial estável) – não utilizado.'),
    dict(item='Anexos no DOM', motivo='O DOM nº 125 disponível na Câmara contém só o texto e o Anexo I; os Anexos II–XX foram tomados da redação final aprovada (Parecer 75/2025), sancionada sem vetos identificados.'),
    dict(item='Setores A/B das ZEC 1 Praça de Boa Viagem e Encruzilhada', motivo='Mapa 3B da redação final tem apenas 375x566 px; ampliações vetorizadas grosseiramente e sem separação de setores.'),
    dict(item='ZEC 2 e ZEC 3', motivo='Perímetros a definir em plano específico (art. 20 §2º).'),
    dict(item='Nomes das ZEIS e das ZEPH por polígono', motivo='Mapas sem rótulos legíveis; geometria agregada por categoria/setor.'),
    dict(item='Parâmetros detalhados das ZEPH (Anexo V)', motivo='Quadro extenso e por ZEPH/SPA; só gabaritos de SPA parcialmente estruturados; SPS/SPM/SPPI são de análise especial.'),
    dict(item='Lotes lindeiros à Av. Boa Viagem e ao Rio Capibaribe (art. 122)', motivo='Faixas de lotes lindeiros não mapeadas; regra só como condicional.'),
    dict(item='Densidade máxima', motivo='LPUOS não fixa densidade; só cota-parte mínima.'),
    dict(item='Definição de HIS por renda / percentuais de uso em ZEIS', motivo='Remetidos ao PD (art. 74) e PLHIS, não acessados.'),
    dict(item='Limite municipal IBGE para validação', motivo='servicodados.ibge.gov.br bloqueado; limite derivado do Mapa 1 (área +3,6% em relação à área oficial ≈21.884 ha).'),
]

camadas_geo = [
    dict(nome='Zoneamento + setores (19 zonas base)', arquivo='geo/zoneamento.geojson', campo='codigo', fonte_url=URL_PLE, data_download=HOJE, oficial=False,
         metodo='Classificação por cor dos Mapas 2 e 4 (raster 1213x1710), restrita por macrozona; polígonos por contornos OpenCV; georreferência pela grade UTM impressa (OCR dos rótulos)', erro_estimado_m=50.0, n_feicoes=len(ZON)),
    dict(nome='Macrozonas MANC/MAC', arquivo='geo/macrozonas.geojson', campo='codigo', fonte_url=URL_PLE, data_download=HOJE, oficial=False, metodo='Classificação por cor do Mapa 1 + grade UTM', erro_estimado_m=50.0, n_feicoes=len(MAC)),
    dict(nome='ZEIS (Mapa 3A final)', arquivo='geo/zeis.geojson', campo='codigo', fonte_url=URL_RF, data_download=HOJE, oficial=False, metodo='Registro afim ORB+RANSAC do mapa da redação final sobre o do PLE + classificação por cor', erro_estimado_m=60.0, n_feicoes=len(ZEIS)),
    dict(nome='ZEC 1 (Mapa 3B)', arquivo='geo/zec.geojson', campo='codigo', fonte_url=URL_RF, data_download=HOJE, oficial=False, metodo='Mapa 3B do PLE + acréscimos do mapa final de baixa resolução', erro_estimado_m=100.0, n_feicoes=len(ZEC)),
    dict(nome='ZEPH – setores (Mapa 3C final)', arquivo='geo/zeph.geojson', campo='codigo', fonte_url=URL_RF, data_download=HOJE, oficial=False, metodo='Registro afim ORB+RANSAC + classificação por cor', erro_estimado_m=60.0, n_feicoes=len(ZEPH)),
    dict(nome='Unidades protegidas (Mapa 6)', arquivo='geo/unidades_protegidas.geojson', campo='codigo', fonte_url=URL_PLE, data_download=HOJE, oficial=False, metodo='Classificação por cor + grade UTM', erro_estimado_m=50.0, n_feicoes=len(UP)),
    dict(nome='Indicação ZEC 2/3', arquivo='geo/zec23_indicacao.geojson', campo='codigo', fonte_url=URL_PLE, data_download=HOJE, oficial=False, metodo='Símbolos do Mapa 3B', erro_estimado_m=100.0, n_feicoes=len(Z23)),
]
geografico = dict(
    descricao='Não foi possível acessar camadas vetoriais oficiais do Recife (hosts da Prefeitura bloqueados para o ambiente de coleta). As geometrias foram vetorizadas dos mapas raster do Anexo II da própria Lei 19.426/2025 (documentos oficiais da Câmara Municipal), georreferenciados pela grade UTM SIRGAS 2000/25S impressa (resíduos ≤7 m na grade; ≈18,7 m/px). Mapas 3A/3C da redação final foram registrados sobre os do PLE (resíduo ≈1 px). Todas oficial:false; erro estimado 50–100 m. Área total vetorizada ≈22.800 ha (+3,6% vs. área oficial).',
    crs='EPSG:4326', crs_area='EPSG:31985', servidor_oficial=None, camadas=camadas_geo,
    regras_de_consulta=('1) Zona base: as 19 zonas base (com setores) particionam o município; parâmetros do Anexo IV. '
        '2) ZEPH (prioridade 30, substitui) prevalece sobre ZEC (art. 19 §2º): SPS/SPM/SPPI = análise especial; SPA = Anexo V. '
        '3) ZEIS (prioridade 20, substitui): CA/IAC do Anexo IV e demais parâmetros pelo plano da ZEIS. '
        '4) ZEC 1 (prioridade 15, substitui): parâmetros da linha ZEC 1 do Anexo IV. '
        '5) Lotes lindeiros à Av. Boa Viagem (42 m) e ao Rio Capibaribe (24 m): gabarito do art. 122 (não mapeado – verificar testada). '
        '6) TSN/TCA pelo tamanho do terreno (Anexo XVIII). 7) Camadas macrozonas (limiar de EIV), unidades_protegidas e zec_2_3_indicacao: alertas. Confirmar sempre na Prefeitura (SEPUL/Licenciamento Urbanístico).'),
    regras_de_consulta_texto='Base (Anexo IV) → ZEPH > ZEIS > ZEC 1 → art. 122 → TSN/TCA por área do lote → alertas.',
    raio_divisa_m=60, pct_minimo_significativo=1.0,
    limitacoes=['Geometrias não oficiais (vetorização de mapas raster de ~1200x1700 px para todo o município), erro 50–100 m: não usar no limite entre zonas sem confirmação na Prefeitura.',
                'ZEIS e ZEPH agregadas por categoria/setor, sem nome por polígono; ZEIS/ZEPH muito pequenas podem faltar.',
                'Ampliações das ZEC 1 Praça de Boa Viagem e Encruzilhada tomadas de mapa de baixa resolução; setores A/B não separados.',
                'Faixas de lotes lindeiros (art. 122) e sistema viário (Mapa 7) não vetorizados.'],
    notas_tecnicas={'vetorizacao_log': LOG, 'scripts': ['vetorizar_lib.py', 'vet1_macrozonas.py', 'vet2_zoneamento.py', 'vet3_especiais.py', 'params_recife.py', 'build_recife.py']})

marco = ('Lei de Parcelamento, Uso e Ocupação do Solo – LPUOS: Lei nº 19.426, de 02/10/2025 (DOM nº 125, 04/10/2025; vigência 60 dias após a publicação), que revogou a Lei 16.176/1996. '
         'Plano Diretor: Lei Complementar nº 02/2021 (não acessada). Instrumentos: OODC Lei 18.900/2022; TDC Lei 18.901/2022 (não acessadas). Vigentes em 27/10/2026.')

doc = dict(schema_versao='1.1', municipio='Recife', uf='PE', slug='recife-pe', codigo_ibge='2611606', data_levantamento=HOJE,
           centro_mapa=dict(lat=-8.05, lon=-34.93, zoom=12), marco_legal_vigente=marco,
           orgao_confirmacao='Prefeitura do Recife – Secretaria de Política Urbana e Licenciamento (Licenciamento Urbanístico / consulta prévia)',
           aviso='Geometrias aproximadas (vetorização não oficial dos mapas raster da Lei 19.426/2025). Confirmar enquadramento e parâmetros na Prefeitura.',
           fontes=FONTES, macrozonas=macrozonas,
           macrozonas_observacao='As macrozonas (MANC/MAC) agrupam as zonas e definem o limiar de EIV; geometria na camada complementar "macrozonas".',
           zonas=zonas, camadas_complementares=cam, outorga_onerosa=outorga, zeis_his=zeis_his, outros_parametros=outros,
           resumo_mcmv=resumo_mcmv, geografico=geografico, lacunas=lacunas)
out = os.path.join(BASE, 'recife-pe.json')
json.dump(doc, open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', out, round(os.path.getsize(out) / 1e6, 2), 'MB', len(zonas), 'zonas', len(cam), 'camadas')
