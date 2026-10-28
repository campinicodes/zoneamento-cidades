#!/usr/bin/env python3
"""Monta joao-pessoa-pb.json (schema 1.1) a partir das camadas vetorizadas em geo_raw/ e dos parâmetros
de params_joao_pessoa.py. Uso: cd scripts && python3 build_joao_pessoa.py"""
import json, os, sys, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, GeometryCollection
from shapely.validation import make_valid
from shapely.ops import unary_union, transform
from pyproj import Transformer
from params_joao_pessoa import *

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'geo_raw')
TO_GEO = Transformer.from_crs(31985, 4326, always_xy=True).transform
HOJE = '2026-10-27'
URL_LUOS_MAPA = FONTES[1]['url']

def rd(o):
    if isinstance(o, (list, tuple)):
        if o and isinstance(o[0], (int, float)):
            return [round(o[0], 6), round(o[1], 6)]
        return [rd(x) for x in o]
    return o

def polys(g):
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    if isinstance(g, GeometryCollection):
        return unary_union([p for p in g.geoms if isinstance(p, (Polygon, MultiPolygon))])
    return None

def geo(g_utm, simp=2.0, min_area=50.0):
    g = polys(make_valid(g_utm))
    if g is None or g.is_empty: return None
    g = polys(make_valid(g.simplify(simp, preserve_topology=True)))
    if g is None or g.is_empty: return None
    parts = [p for p in (g.geoms if isinstance(g, MultiPolygon) else [g]) if p.area >= min_area]
    if not parts: return None
    g = MultiPolygon(parts) if len(parts) > 1 else parts[0]
    m = mapping(transform(TO_GEO, g)); m = {'type': m['type'], 'coordinates': rd(m['coordinates'])}
    s = shape(m)
    if not s.is_valid:
        s = polys(make_valid(s))
        m = mapping(s); m = {'type': m['type'], 'coordinates': rd(m['coordinates'])}
        if not shape(m).is_valid:
            b = polys(shape(m).buffer(0)); m = mapping(b); m = {'type': m['type'], 'coordinates': rd(m['coordinates'])}
    return m

def load(nome):
    d = json.load(open(os.path.join(RAW, nome)))
    return d, {f['properties']['codigo']: shape(f['geometry']) for f in d['features']}

def fc(feats, fonte, oficial, obs=None):
    d = {'type': 'FeatureCollection', 'crs': 'EPSG:4326 (lon, lat)', 'fonte': fonte, 'oficial': oficial, 'features': [f for f in feats if f]}
    if obs: d['observacao_geometria'] = obs
    return d

def feat(g, props, simp=2.0, min_area=50.0):
    m = geo(g, simp, min_area)
    return {'type': 'Feature', 'properties': props, 'geometry': m} if m else None

# ---------------- geometrias ----------------
zd, ZG = load('zonas_lc169_corrigido_utm.geojson')
md, MG = load('macrozonas_lc171_corrigido_utm.geojson')
_, OV = load('luos_overlays_utm.geojson')
od, ORLA = load('orla_faixas_utm.geojson')
_, RA = load('pd_restricoes_ambientais_utm.geojson')
_, RX = load('pd_restricoes_adicionais_utm.geojson')
_, ZL = load('zeis_leis_2025_utm.geojson')
zeis171 = json.load(open(os.path.join(RAW, 'lc171_zeis_utm.geojson')))
LOG169 = zd.get('log_lc169')

def macro_pct(g):
    r = {}
    for k, m in MG.items():
        a = g.intersection(m).area / g.area * 100
        if a >= 0.5: r[k] = round(a, 1)
    return dict(sorted(r.items(), key=lambda x: -x[1]))

GEO_FONTE_Z = ('Vetorização do Mapa de Zoneamento da LUOS (LC 166/2024, Anexo II, p. 46 do PDF republicado – desenho vetorial do PDF, '
               'georreferenciado pela grade UTM SIRGAS 2000/25S impressa) com correções da LC 169/2024 Anexo I (raster) – ' + URL_LUOS_MAPA)
GEO_OBS_Z = ('NÃO OFICIAL (oficial:false): não há camada vetorial pública do zoneamento. Erro estimado ~15 m (IoU 0,987 contra o limite IBGE, deslocamento ~5 m) '
             'nos trechos do vetor da LUOS; ~35 m nos trechos alterados pela LC 169/2024 (registro raster): ZDTRS ao norte → ZBD (162,8 ha), '
             'porção SW de ZDTRL → ZI-1 com recorte de ZDTRS (24,0 ha), recorte de ZCS-7 → ZCS-4 (15,6 ha). Simplificação 2 m.')

# ---------------- parâmetros por zona ----------------
def am_param(cod, t):
    am = t['am']
    orla = C('lote na faixa de 500 m de restrição da orla (camada orla_faixas)', forma='faixa', faixa={'min': 12.9, 'max': 35.0},
             obs='Altura máxima pela faixa (LUOS art. 61): 1ª 12,90; 2ª 16,50; 3ª 19,50; 4ª 22,50; 5ª 25,50; 6ª 28,50; 7ª 31,50; 8ª 34,00; 9ª 35,00 m. Lote em mais de uma faixa respeita o limite de cada uma (§1º). Medida do meio-fio na metade da testada mais próxima da orla até o piso do último pavimento; nos primeiros 30 m, até a laje de cobertura (§§2º–3º).')
    fora = C('fora da faixa de 500 m', forma='livre', obs='Anexo IV não fixa AM: altura resultante da aplicação dos demais parâmetros (LUOS art. 58 §1º), observadas as restrições COMAER/ANAC e ANATEL (art. 59).')
    iph = C('poligonal tombada do Centro Histórico / Sítio Paisagístico do Cabo Branco', forma='texto', texto=NOTA_H, obs='Altura definida por IPHAN/IPHAEP (LUOS art. 60).')
    art = A4 + ' – coluna AM; LUOS arts. 58–62'
    if am == 'F': return P(None, 'F03', art, NOTA_F, 'm', 'condicional', condicionais=[orla, fora])
    if am == 'FH': return P(None, 'F03', art, NOTA_F + ' ' + NOTA_H, 'm', 'condicional', condicionais=[orla, iph, fora])
    if am == 'H': return P(None, 'F03', art, 'Altura definida por IPHAN/IPHAEP nas poligonais tombadas; fora delas, altura resultante dos demais parâmetros (art. 58 §1º) e COMAER (art. 59).', 'm', 'texto', texto_original=NOTA_H)
    if am == 'manejo': return P(None, 'F03', art, None, 'm', 'texto', texto_original=t['notas'][0])
    if am == 'infra': return P(None, 'F03', art, None, 'm', 'texto', texto_original=t['notas'][0])
    return P(None, 'F03', art, 'Anexo IV sem AM para a zona: altura resultante dos demais parâmetros (LUOS art. 58 §1º), observadas COMAER/ANAC e ANATEL (art. 59).', 'm', 'livre')

def num_or_range(v, col, unidade, obs=None):
    if v is None: return None
    if isinstance(v, tuple):
        return P(None, 'F03', A4 + f' – coluna {col}', obs, unidade, 'faixa', faixa={'min': v[0], 'max': v[1]})
    if isinstance(v, dict): return v
    return um(v, col, obs, unidade)

def ia_params(cod, mp):
    base = P(1, 'F01', 'LC 164/2024 (PD), art. 50 §1º; LUOS (LC 166/2024) art. 53', 'IA básico igual a 1 em todas as macrozonas (MAD-1, MAD-2, MAD-3, MBD e MPA).', 'coeficiente')
    cs = [C(f'lote na {NOME_MACRO[m]} ({m}) – {p}% da zona', IA_MACRO[m][1], codigo=m) for m, p in mp.items()]
    mx = P(None, 'F01', 'LC 164/2024 (PD), art. 50 §1º (redação mantida pela LC 171/2025); LUOS art. 53 §§2º–3º',
           'IA máximo definido pela macrozona do lote (camada macrozonas): MAD-1 6; MAD-2 4; MAD-3 2; MBD 1; MPA 1. O excedente ao básico só é obtido onerosamente por OODC e/ou TDC (cumulativos). '
           'Se a existência de infraestrutura não for comprovada, aplica-se o IA básico (PD art. 50 §2º). Percentuais = fração da área da zona em cada macrozona (vetorização).',
           'coeficiente', 'condicional', condicionais=cs)
    return base, mx

CA_MIN = P(None, 'F01', 'LC 164/2024 (PD), art. 87 p.ú., I', 'Não há IA mínimo no quadro da LUOS. Para fins de PEUC o PD considera subutilizado o imóvel com área construída inferior a 5% do potencial construtivo permitido (texto em texto_original).', 'coeficiente', 'sem_dado',
           texto_original='imóvel não edificado ou subutilizado: aquele cuja área construída seja inferior a 5% (cinco por cento) do potencial construtivo permitido para edificação no lote')
LOTE = P(125, 'F16', 'Lei Federal 6.766/1979, art. 4º, II', 'Mínimo federal (125 m² e frente 5 m) – a Lei municipal de Parcelamento do Solo referida na LUOS (arts. 38 e 50) não consta da página de legislação vigente do município (ver lacunas). Na ZBD o lote mínimo é 20.000 m² (LUOS art. 33).', 'm2')
TESTADA = P(5, 'F16', 'Lei Federal 6.766/1979, art. 4º, II', 'Mínimo federal; sem testada mínima municipal localizada.', 'm')
DENS = P(None, None, None, 'PD e LUOS não fixam densidade máxima (controle por IA, TO, AM e recuos).', None, 'sem_dado')

def vagas(cod):
    if cod in ('ZCS-6', 'ZCS-7', 'ZI-1', 'ZI-2', 'ZEPA-1', 'ZDTRL', 'ZDTRS'):
        return P(None, 'F03', A5, 'Habitação multifamiliar não permitida na zona; vagas de outros usos no Anexo V.', 'vagas/UH', 'nao_aplicavel')
    if cod == 'ZBD':
        return P(1, 'F03', A5 + ' – linhas H1/H2', 'H3 não permitido na ZBD; H1/H2: 1 vaga por UH.', 'vagas/UH')
    return P(None, 'F03', A5, 'Vagas de bicicletas e motos facultativas para H3; HIS: Decreto 10.560/2024 art. 3º (20% das UH para automóveis, 30% bicicletas, 15% motos).', 'vagas/UH', 'condicional',
             condicionais=[C('H1/H2', 1), C('H3 com UH de área útil até 30 m²', 0.25, obs='1 vaga a cada 4 UH'), C('H3 com UH de área útil acima de 30 m²', 0.5, obs='1 vaga a cada 2 UH'),
                           C('H3 (HIS) – conforme regulamentação específica (Dec. 10.560/2024)', 0.2, obs='Dec. 10.560/2024 art. 3º, I, d: vagas para automóveis em quantidade mínima equivalente a 20% das UH.')],
             texto_original='H1, H2: 1 vaga por UH; H3 (UH área útil até 30 m²): 1 vaga a cada 4 UH; H3 (UH área útil acima de 30 m²): 1 vaga a cada 2 UH; H3 (HIS): conforme regulamentação específica.')

def usos(cod):
    if cod == 'ZEPA-1':
        return P(None, 'F03', A3 + ' – notas', None, 'codigos_de_uso', 'texto', texto_original='Na ZEPA-1 o uso do solo será disciplinado mediante elaboração de planos de manejo específicos, quando couber, conforme determinação do órgão competente.')
    if cod in ('ZDTRL', 'ZDTRS'):
        return P(None, 'F03', A3 + ' – notas', None, 'codigos_de_uso', 'texto', texto_original='Os usos permitidos na ZDTRL e na ZDTRS são, apenas, aqueles vinculados aos sistemas de esgotamento sanitário e tratamento de água ou ao aterro sanitário, a serem aprovados pelo CDU.')
    obs = (USOS_OBS.get(cod, '') + ' ' + REGRA_VIA).strip()
    if 'H3' in USOS[cod]: obs = 'H3 (habitação multifamiliar, ≥3 UH – LUOS art. 45, III) PERMITIDA. ' + obs
    return P(USOS[cod], 'F03', A3 + '; LUOS arts. 44–48', obs, 'codigos_de_uso', 'lista')

def parametros(cod, mp):
    t = Z[cod]
    b, mx = ia_params(cod, mp)
    special = t['am'] in ('manejo', 'infra')
    def sd(nome, un):
        return P(None, 'F03', A4, t['notas'][0], un, 'texto', texto_original=t['notas'][0])
    to_obs = ' '.join(n for n in t['notas'] if n[:3] in ('(A)', '(B)', '(G)', '(H)')) or None
    par = {
        'ca_minimo': CA_MIN, 'ca_basico': b, 'ca_maximo': mx,
        'taxa_ocupacao': sd('TO', 'fracao') if special else num_or_range(t['to'], 'TO máxima', 'fracao', to_obs),
        'gabarito_altura_max_m': am_param(cod, t),
        'gabarito_pavimentos': P(t['pav'], 'F03', A4 + ' – coluna AM', 'Número máximo de pavimentos fixado no Anexo IV.', 'pavimentos') if t.get('pav') else None,
        'taxa_permeabilidade': sd('TAP', 'fracao') if special else num_or_range(t['tap'], 'TAP mínima', 'fracao', 'Pode ser reduzida em algumas zonas com mecanismos de contenção de cheias (LUOS art. 67); materiais do Anexo VIII (art. 65 §3º).'),
        'recuos': {
            'frontal': sd('RFT', 'm') if special else num_or_range(t['rft'], 'Recuo Frontal (RFT)', 'm', 'Recuo para todas as frentes (LUOS art. 68 §1º); medido do alinhamento existente ou projetado (§4º). ' + (NOTA_C if NOTA_C in t['notas'] else '') + (NOTA_J if NOTA_J in t['notas'] else '')),
            'lateral': sd('RL', 'm') if special else num_or_range(t['rl'], 'Recuo Lateral (RL)', 'm', '(D) Colagem lateral de até 50% no térreo permitida para todos os usos, exceto ZCS-1 a ZCS-4.'),
            'fundos': sd('RFD', 'm') if special else num_or_range(t['rfd'], 'Recuo de Fundo (RFD)', 'm', '(E) Colagem de fundos de até 60% no térreo para H1.'),
        },
        'lote_minimo_m2': P(20000, 'F02', 'LUOS (LC 166/2024), art. 33', None, 'm2') if cod == 'ZBD' else LOTE,
        'testada_minima_m': TESTADA,
        'usos_permitidos': usos(cod),
        'vagas': vagas(cod),
        'densidade': DENS,
        'outros': {},
    }
    if not special and NOTA_B in t['notas']:
        par['outros']['h3_vias_locais_coletoras'] = P(None, 'F03', A4 + ' – nota (B)', 'Alternativa para H3 em vias locais e coletoras.', None, 'texto', texto_original=NOTA_B)
    if NOTA_I in t['notas']:
        par['outros']['licenciamento_ambiental'] = P(None, 'F03', A4 + ' – nota (I)', None, None, 'texto', texto_original=NOTA_I)
    par['outros']['subsolo'] = P(None, 'F02', 'LUOS (LC 166/2024), art. 50, VI e Seção própria', 'Subsolo e semissubsolo disciplinados na LUOS (afloramento máx. 1,60 m – art. 72).', None, 'livre')
    return par

def categoria(cod, mp):
    dom = next(iter(mp)) if mp else None
    camax = IA_MACRO[dom][1] if dom else 1
    dens = 'baixa' if camax <= 1.5 else ('media' if camax <= 3 else 'alta')
    crit = f'Classificação do analista: macrozona predominante {dom} (IA máx {camax}; ≤1,5 baixa; ≤3 média; >3 alta). '
    if cod.startswith('ZH'): return f'residencial_{dens}_densidade', crit + 'Zona Habitacional (uso habitacional predominante, LUOS art. 8º).'
    if cod in ('ZCS-1', 'ZCS-2'): return 'patrimonio_cultural', crit + 'Centro Histórico/áreas tombadas (IPHAN/IPHAEP).'
    if cod in ('ZCS-3', 'ZCS-4'): return 'eixo', crit + 'Corredores de estruturação urbana / transporte público (LUOS arts. 20–21).'
    if cod == 'ZCS-5': return f'mista_{dens}_densidade', crit + 'Polo Turístico com multifamiliar, hotelaria e comércio.'
    if cod in ('ZCS-6', 'ZCS-7'): return 'especial_economica', crit + 'Uso turístico/grandes equipamentos; H3 não permitido.'
    if cod.startswith('ZEPA') or cod == 'SEAV': return 'ambiental', crit + 'Proteção ambiental.'
    if cod.startswith('ZI'): return 'industrial', crit + 'Zona Industrial.'
    if cod == 'ZBD': return 'rural', crit + 'Características rurais e controle da expansão (LUOS art. 33).'
    return 'institucional', crit + 'Infraestrutura de saneamento/resíduos.'

ORDEM = ['ZH-1', 'ZH-2', 'ZH-3', 'ZH-4', 'ZH-5', 'ZCS-1', 'ZCS-2', 'ZCS-3', 'ZCS-4', 'ZCS-5', 'ZCS-6', 'ZCS-7',
         'ZEPA-1', 'ZEPA-2', 'ZEPA-3', 'ZI-1', 'ZI-2', 'ZBD', 'ZDTRL', 'ZDTRS']
zonas = []
for cod in ORDEM:
    g = ZG[cod]; mp = macro_pct(g)
    cat, crit = categoria(cod, mp)
    nome, desc = NOMES[cod]
    obs = list(Z[cod]['notas'])
    obs.append(f'Área vetorizada: {g.area/1e4:.1f} ha. Macrozonas (% da área): ' + ', '.join(f'{k} {v}%' for k, v in mp.items()) + '.')
    if cod in ('ZBD', 'ZEPA-1', 'ZEPA-2', 'ZEPA-3', 'ZDTRL', 'ZDTRS'):
        obs.append('Parâmetros aplicam-se exatamente nas delimitações do mapa; não se aplicam as regras de prolongamento (art. 5º) nem de predominância no lote (art. 6º) – LUOS arts. 5º p.ú. e 6º p.ú.')
    zonas.append(dict(codigo=cod, nome=nome, descricao=desc, tipo='base', prioridade=0, categoria_normalizada=cat, categoria_criterio=crit,
                      regra_sobreposicao=None, parametros=parametros(cod, mp), observacoes=obs,
                      geometria=fc([feat(g, {'codigo': cod, 'nome': nome, 'area_ha': round(g.area / 1e4, 1)})], GEO_FONTE_Z, False, GEO_OBS_Z)))

# SEAV (sobreposta)
gS = OV['SEAV']; mpS = macro_pct(gS)
parS = parametros('SEAV', mpS)
parS['ca_maximo'] = P(None, 'F02', 'LUOS (LC 166/2024) arts. 37, 39 e 54; Anexo VII', 'IA máximo outorgado onerosamente (Outorga Onerosa Ambiental, valores em lei específica – art. 39 §1º) e proporcional à área preservada com cobertura vegetal ou recuperada (APPs não contam – art. 54 p.ú.). Flexibilização só na parte do lote dentro do SEAV.',
                      'coeficiente', 'condicional', condicionais=[C('30% a 40% de área preservada', 1.4), C('40% a 50% de área preservada', 1.6), C('50% a 60% de área preservada', 1.8), C('acima de 60% de área preservada', 2.0)])
zonas.append(dict(codigo='SEAV', nome=NOMES['SEAV'][0], descricao=NOMES['SEAV'][1], tipo='sobreposta', prioridade=10, categoria_normalizada='ambiental',
                  categoria_criterio='Setor de áreas verdes sobre ZEPA-2 (LUOS art. 36).',
                  regra_sobreposicao=dict(efeito='substitui', usa_indices_de=None, aplica_sobre=['ZEPA-2'], limiar_pct=0, requer_testada=False, distancia_max_m=None,
                                          fundamento='LUOS art. 36 (SEAV é preponderante ao zoneamento) e art. 6º p.ú. (parâmetros aplicados exatamente na delimitação).',
                                          alerta='Lote no SEAV: parâmetros do SEAV (LC 169 Anexo IV) e IA máx 1,4–2,0 conforme área preservada (Anexo VII), mediante Outorga Onerosa Ambiental; respeitar APPs.',
                                          mantem_da_base=['ca_basico']),
                  parametros=parS, observacoes=[f'Área vetorizada: {gS.area/1e4:.1f} ha (hachura do Anexo II da LUOS).', 'Parâmetros do SEAV conforme Anexos IV e V e Lei de Parcelamento (art. 38).'],
                  geometria=fc([feat(gS, {'codigo': 'SEAV', 'nome': 'Setor Especial de Áreas Verdes', 'area_ha': round(gS.area / 1e4, 1)})], GEO_FONTE_Z, False,
                               'NÃO OFICIAL: hachura do Anexo II da LUOS vetorizada; erro estimado ~15 m. A LC 169/2024 não alterou o SEAV visivelmente.')))

# ZEIS criadas por lei com poligonal em coordenadas (oficial)
def zeis_lei(cod, fid, lei, nome, desc, pav, am, usos_l, usos_txt, obs_extra):
    g = ZL[cod]; mp = macro_pct(g)
    base_cod = max(ZG, key=lambda k: ZG[k].intersection(g).area)
    art = f'{lei}, art. ' + ('4º' if fid == 'F11' else '5º')
    par = {
        'ca_minimo': CA_MIN, 'ca_basico': P(None, fid, art, 'A lei da ZEIS não fixa IA: mantém-se o da zona/macrozona de base.', 'coeficiente', 'herda_da_base'),
        'ca_maximo': P(None, fid, art, 'A lei da ZEIS não fixa IA máximo: mantém-se o da macrozona (PD art. 50). HIS pode ser isenta de OODC (PD art. 101 p.ú.).', 'coeficiente', 'herda_da_base'),
        'taxa_ocupacao': P(0.40, fid, art + ', I', None, 'fracao'),
        'gabarito_altura_max_m': am,
        'gabarito_pavimentos': pav,
        'taxa_permeabilidade': P(0.40, fid, art + ', II', 'TAP mínima de 40%, dos quais no mínimo 20% de área verde (área permeável com cobertura vegetal – Portaria MCID 725/2023).', 'fracao'),
        'recuos': {'frontal': P(5.0, fid, art + ', III/IV, a', None, 'm'), 'lateral': P(1.5, fid, art + ', III/IV, b', None, 'm'), 'fundos': P(2.0, fid, art + ', III/IV, c', None, 'm')},
        'lote_minimo_m2': P(None, fid, lei, 'Lei da ZEIS não fixa lote mínimo; projeto conforme plano urbanístico/programa HIS.', 'm2', 'sem_dado'),
        'testada_minima_m': P(None, fid, lei, None, 'm', 'sem_dado'),
        'usos_permitidos': P(usos_l, fid, lei + ', art. 2º/3º', usos_txt, 'codigos_de_uso', 'lista'),
        'vagas': P(0.2, 'F07', 'Decreto 10.560/2024, art. 3º, I, d', 'HIS: vagas para automóveis ≥20% das UH; bicicletas 30%; motos 15% (exigências podem ser dispensadas em ZEIS – §1º).', 'vagas/UH'),
        'densidade': DENS, 'outros': {},
    }
    return dict(codigo=cod, nome=nome, descricao=desc, tipo='sobreposta', prioridade=20, categoria_normalizada='especial_interesse_social',
                categoria_criterio='ZEIS 2 criada por lei específica (PD arts. 54–58).',
                regra_sobreposicao=dict(efeito='substitui', usa_indices_de=None, aplica_sobre=None, limiar_pct=0, requer_testada=False, distancia_max_m=None,
                                        fundamento=f'{lei} (parâmetros próprios da ZEIS – LUOS art. 51; PD art. 54 p.ú.). Poligonal fechada por coordenadas.',
                                        alerta=f'Lote na {nome}: aplicar os parâmetros da lei da ZEIS (destinada a HIS/MCMV); IA da macrozona.', mantem_da_base=['ca_basico', 'ca_maximo']),
                parametros=par, observacoes=[f'Zona de base predominante sob a ZEIS: {base_cod}; macrozona: ' + ', '.join(f'{k} {v}%' for k, v in mp.items()) + '.', f'Área da poligonal: {g.area:.2f} m².'] + obs_extra,
                geometria=fc([feat(g, {'codigo': cod, 'nome': nome, 'lei': lei, 'area_m2': round(g.area, 2)}, 0.0, 0.0)],
                             f'Quadro de coordenadas UTM SIRGAS 2000 (fuso 25S) publicado na {lei} – {[f for f in FONTES if f["id"]==fid][0]["url"]}', True,
                             'Poligonal construída diretamente das coordenadas oficiais da lei (conferida pelas distâncias do quadro e pela área declarada; diferença <0,01%).'))
zonas.append(zeis_lei('ZEIS-DEMOCRACIA', 'F11', 'Lei 15.606/2025', 'ZEIS Democracia', 'ZEIS 2 nos bairros Mangabeira e Costa do Sol (lotes 52.397.0320 e 52.397.0287; 29.920,83 m²) para redução do déficit habitacional de baixa renda.',
                      P(4, 'F11', 'Lei 15.606/2025, art. 4º, IV', None, 'pavimentos'),
                      P(None, 'F11', 'Lei 15.606/2025, art. 4º', 'Lei fixa 4 pavimentos; sem altura em metros.', 'm', 'livre'),
                      ['H3', 'CG/SG', 'CE/SE'], 'No mínimo 60% da área destinada a uso Habitacional Multifamiliar (H3) e no máximo 40% a Comércio e Serviços (art. 2º §1º). Projetos devem atender à Portaria MCID 725/2023 (MCMV) e ao Dec. 10.560/2024 (art. 3º).',
                      ['Classificada como ZEIS 2 (art. 2º §2º). Criação aprovada pelo CDU (Resolução 03/CDU-GP/2025).']))
zonas.append(zeis_lei('ZEIS-RIO-SANHAUA', 'F12', 'Lei 15.607/2025', 'ZEIS Rio Sanhauá', 'ZEIS 2 no Varadouro (lote 23.066.0067; 10.967,04 m²) para realocação de famílias em área de risco do Porto do Capim; salvaguarda do patrimônio histórico.',
                      P(None, 'F12', 'Lei 15.607/2025, art. 5º, V', 'Por setor (Anexos III–VI).', 'pavimentos', 'condicional', condicionais=[C('Setor 04 (Anexo VI)', 1), C('Setor 03 (Anexo V)', 3), C('Setor 02 (Anexo IV)', 6), C('Setor 01 (Anexo III) – área verde em sua totalidade', forma='nao_aplicavel')]),
                      P(None, 'F12', 'Lei 15.607/2025, art. 5º, VI', 'Por setor; setores não vetorizados (só a poligonal geral).', 'm', 'condicional', condicionais=[C('Setor 04', 7.5), C('Setor 03', 13.5), C('Setor 02', 18.0), C('Setor 01 – área verde', forma='nao_aplicavel')]),
                      ['H1', 'H2', 'H3', 'CG/SG', 'CE/SE'], 'Destinada ao uso habitacional; comércio e serviço até 20% da área do lote (art. 3º §§1º–2º). UH para famílias com renda bruta até R$ 2.640,00 (Lei federal 14.620/2023 – MCMV Faixa 1), prioridade Porto do Capim (§4º).',
                      ['Classificada como ZEIS 2 (art. 3º §3º). Setor 01 integralmente área verde. Atender Decreto-Lei 25/1937 (patrimônio).', 'Os quadros de coordenadas dos 4 setores (Anexos III–VI) não foram vetorizados; os parâmetros por setor estão como condicionais.']))
FONTES.append(dict(id='F16', titulo='Lei do Parcelamento do Solo Urbano', lei='Lei Federal nº 6.766/1979', data='1979-12-19', url='https://www.planalto.gov.br/ccivil_03/leis/l6766.htm', arquivo_local=None,
                   observacao='Usada só para lote mínimo/frente mínima gerais (art. 4º, II), na falta de lei municipal de parcelamento localizada.'))

# ---------------- camadas complementares ----------------
GRADE_OBS = 'Vetorização do desenho vetorial do PDF georreferenciado pela grade UTM impressa (EPSG:31985); erro estimado ~15–20 m.'
cam = {}
cam['macrozonas'] = dict(papel='macrozona', descricao='Macrozonas do Plano Diretor (LC 164/2024 art. 47, mapa do Anexo I substituído pela LC 171/2025). Definem o IA básico (1) e o IA máximo de cada lote.',
    fonte='Vetorização do Anexo I do PD (LC 164/2024, p. 74 do PDF SAPL – vetorial) com a alteração da LC 171/2025 Anexo I (raster, registrado por ECC 0,97): 145,6 ha de MAD-2 → MBD (Mussuré). ' + FONTES[0]['url'],
    oficial=False, observacao='NÃO OFICIAL; erro ~15 m no traçado do PD e ~35 m no trecho alterado pela LC 171. Divergência total LC171×PD 3,7% (maior parte ruído de registro).',
    fonte_id='F01', artigo_anexo='LC 164/2024 arts. 44–50 e Anexo I; LC 171/2025 Anexo I',
    parametros_por_codigo={m: {'ca_basico': P(IA_MACRO[m][0], 'F01', 'LC 164/2024, art. 50 §1º', None, 'coeficiente'), 'ca_maximo': P(IA_MACRO[m][1], 'F01', 'LC 164/2024, art. 50 §1º', 'Acima do básico, onerosamente (OODC/TDC – LUOS art. 53 §2º).', 'coeficiente')} for m in IA_MACRO},
    alerta_por_codigo=None,
    features=[feat(MG[m], {'codigo': m, 'nome': NOME_MACRO[m], 'area_ha': round(MG[m].area / 1e4, 1)}) for m in ['MAD-1', 'MAD-2', 'MAD-3', 'MBD', 'MPA']])
ALT = {f'FAIXA_{k}': v for k, v in {1: 12.90, 2: 16.50, 3: 19.50, 4: 22.50, 5: 25.50, 6: 28.50, 7: 31.50, 8: 34.00, 9: 35.00}.items()}
reg = od.get('registro', {})
cam['orla_faixas'] = dict(papel='restricao', descricao='Faixas de restrição de altura da orla marítima (500 m a partir da testada da primeira quadra; 9 faixas) – LUOS arts. 61–62; PD art. 64; Constituição Estadual art. 229.',
    fonte='Vetorização dos caminhos de recorte vetoriais do mapa do Anexo III da LUOS (p. 48 do PDF SAPL), registrado à faixa de 500 m do Anexo II. ' + URL_LUOS_MAPA,
    oficial=False, observacao=f'NÃO OFICIAL; erro estimado ~20 m (borda da faixa de 500 m coincide com mediana {reg.get("dist_borda_mediana_m", 0):.1f} m). O Anexo III foi substituído pelo Anexo II da LC 169/2024 (raster de baixa resolução): sem mudança perceptível do traçado, mas não verificável faixa a faixa.',
    fonte_id='F02', artigo_anexo='LUOS arts. 61–62 e Anexo III; LC 169/2024 Anexo II',
    parametros_por_codigo={k: {'gabarito_altura_max_m': P(v, 'F02', 'LUOS art. 61, ' + ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'][int(k[-1]) - 1], 'Lote em várias faixas: respeitar o limite de cada uma (§1º).', 'm')} for k, v in ALT.items()},
    alerta_por_codigo={k: f'Orla – {k[-1]}ª faixa: altura máxima {str(v).replace(".", ",")} m (LUOS art. 61).' for k, v in ALT.items()},
    features=[feat(ORLA[k], {'codigo': k, 'faixa': int(k[-1]), 'altura_max_m': ALT[k], 'area_ha': round(ORLA[k].area / 1e4, 1)}) for k in sorted(ORLA)])
cam['bordas_tabuleiro'] = dict(papel='restricao', descricao='Bordas de tabuleiro e faixa de praia indicadas no mapa de zoneamento da LUOS (hachuras do Anexo II).',
    fonte='Vetorização das hachuras do Anexo II da LUOS (p. 46). ' + URL_LUOS_MAPA, oficial=False, observacao=GRADE_OBS, fonte_id='F02', artigo_anexo='LUOS art. 28, I (bordas de tabuleiro na ZEPA-2); Anexo II',
    parametros_por_codigo=None,
    alerta_por_codigo={'BORDAS_TABULEIRO': 'Borda de tabuleiro: área ambientalmente frágil (ZEPA-2) – anuência SEMAM; vedada construção na faixa de 100 m das falésias (LUOS art. 28).',
                       'FAIXA_PRAIA_500M': 'Faixa de 500 m da orla: altura máxima por faixa (ver orla_faixas; LUOS arts. 61–62).'},
    features=[feat(OV['BORDAS_TABULEIRO'], {'codigo': 'BORDAS_TABULEIRO', 'area_ha': round(OV['BORDAS_TABULEIRO'].area / 1e4, 1)}),
              feat(OV['FAIXA_PRAIA_500M'], {'codigo': 'FAIXA_PRAIA_500M', 'area_ha': round(OV['FAIXA_PRAIA_500M'].area / 1e4, 1)})])
cam['zeis_pd'] = dict(papel='informativa', descricao='Zonas Especiais de Interesse Social do Plano Diretor (Anexo II substituído pela LC 171/2025; 74 ZEIS listadas no Anexo III, ≈482,7 ha). Sem parâmetros próprios: flexibilização só por programa de regularização + projeto específico + CDU + lei (LUOS art. 51).',
    fonte='Vetorização do mapa raster do Anexo II da LC 171/2025 (máscara de cor), registrado por SIFT+RANSAC ao mapa vetorial do PD (p. 76). ' + FONTES[3]['url'],
    oficial=False, observacao=f'NÃO OFICIAL; resíduo de registro mediana 11,9 m / p90 26,9 m; pixel ≈17 m; erro estimado ~35 m. Área vetorizada {sum(shape(f["geometry"]).area for f in zeis171["features"])/1e4:.1f} ha (≈79% da área listada) – ZEIS pequenas podem faltar.',
    fonte_id='F04', artigo_anexo='LC 164/2024 arts. 54–59; LC 171/2025 Anexos II e III',
    parametros_por_codigo=None, alerta_por_codigo={'ZEIS': 'Lote em ZEIS (PD arts. 55–59): prioridade para HIS e regularização; parâmetros da zona de base, salvo lei específica da ZEIS (LUOS art. 51). Confirmar na SEPLAN o nome/lei da ZEIS (Anexo III da LC 171/2025).'},
    features=[feat(shape(f['geometry']), {'codigo': 'ZEIS', 'parte': f['properties'].get('parte'), 'area_ha': f['properties'].get('area_ha')}, 3.0, 500) for f in zeis171['features']])
RA_AL = {'UNIDADE_CONSERVACAO': 'Unidade de conservação (PD Anexo VII): uso conforme plano de manejo/órgão gestor.',
         'PARQUE_MUNICIPAL': 'Parque municipal (ZEPA-1; PD Anexo VII): ocupação restrita.',
         'MANANCIAL_PRELIMINAR': 'Área de manancial (proposta preliminar – PD Anexo VII): proteção e recarga de mananciais; consultar SEMAM.',
         'PARQUE_ESTADUAL_TRILHAS': 'Parque Estadual das Trilhas: unidade de conservação estadual.'}
cam['protecao_ambiental'] = dict(papel='restricao', descricao='Zonas Especiais de Preservação Ambiental do PD (Anexo VII, substituído pela LC 171/2025): unidades de conservação, parques municipais, Parque Estadual das Trilhas e área de manancial (proposta preliminar).',
    fonte='Vetorização do Anexo VII do PD (LC 164/2024, p. 88 do PDF SAPL – vetorial). ' + FONTES[0]['url'], oficial=False,
    observacao=GRADE_OBS + ' O Anexo VII da LC 171/2025 (raster) não foi comparado faixa a faixa.', fonte_id='F01', artigo_anexo='LC 164/2024 arts. 54, II e 60–61; Anexo VII',
    parametros_por_codigo=None, alerta_por_codigo=RA_AL,
    features=[feat(RA[k], {'codigo': k, 'area_ha': round(RA[k].area / 1e4, 1)}, 3.0, 300) for k in RA_AL if k in RA])
RX_AL = {'SUSC_MOV_MASSA_ALTA': 'Alta suscetibilidade a movimento de massa (PD Anexo VIII): restrição adicional – exigir estudos geotécnicos.',
         'SUSC_MOV_MASSA_MODERADA': 'Moderada suscetibilidade a movimento de massa (PD Anexo VIII).',
         'SUSC_INUNDACAO_ALTA': 'Alta suscetibilidade a inundação (PD Anexo VIII): restrição adicional.',
         'SUSC_INUNDACAO_MODERADA': 'Moderada suscetibilidade a inundação (PD Anexo VIII).',
         'ALTIPLANO_CABO_BRANCO': 'Platô do Altiplano do Cabo Branco: restrição adicional de altura e paisagem (PD art. 65).',
         'CENTRO_HISTORICO': 'Centro Principal/Centro Histórico (PD art. 63): índices por quadra e análise IPHAN/IPHAEP.',
         'TOMBAMENTO_IPHAN': 'Poligonal de tombamento IPHAN: análise prévia do IPHAN.',
         'TOMBAMENTO_IPHAEP': 'Poligonal de tombamento IPHAEP: análise prévia do IPHAEP.',
         'MATA_BURAQUINHO': 'Mata do Buraquinho (ZEPA-1): ocupação vedada/restrita.'}
cam['restricoes_adicionais'] = dict(papel='restricao', descricao='Zonas Especiais de Restrições Adicionais do PD (Anexo VIII, substituído pela LC 171/2025): suscetibilidade a movimento de massa e inundação, Altiplano do Cabo Branco, tombamentos IPHAN/IPHAEP, Centro Histórico e Mata do Buraquinho (PD arts. 62–65).',
    fonte='Vetorização do Anexo VIII do PD (LC 164/2024, p. 90 do PDF SAPL – vetorial). ' + FONTES[0]['url'], oficial=False,
    observacao=GRADE_OBS + ' Classes de suscetibilidade simplificadas (5 m) e sem fragmentos < 2.000 m². Falésias (linhas) não poligonizadas.', fonte_id='F01', artigo_anexo='LC 164/2024 arts. 54, III e 62–65; Anexo VIII',
    parametros_por_codigo=None, alerta_por_codigo=RX_AL,
    features=[feat(RX[k], {'codigo': k, 'area_ha': round(RX[k].area / 1e4, 1)}, 5.0 if k.startswith('SUSC') else 3.0, 2000 if k.startswith('SUSC') else 300) for k in RX_AL if k in RX])
for k, c in cam.items():
    c['features'] = [f for f in c['features'] if f]

# ---------------- blocos ----------------
def it(chave, titulo, valor, unidade, fid, art, obs=None, forma=None, **kw):
    d = P(valor, fid, art, obs, unidade, forma, **kw); d = dict(chave=chave, titulo=titulo, **d); return d

outorga = dict(resumo='OODC prevista no PD (arts. 100–101) para construir acima do IA básico (1) até o IA máximo da macrozona (6/4/2/1/1), cumulativa com a TDC (LUOS art. 53 §2º). A lei específica de regulamentação (fórmula, contrapartida) NÃO foi localizada entre a legislação vigente publicada; isenção só para HIS e equipamentos públicos (art. 101 p.ú.). No SEAV há Outorga Onerosa Ambiental (LUOS arts. 37–39).',
    fonte_id='F01', artigo_anexo='LC 164/2024 arts. 50, 100–101; LUOS art. 53', itens=[
    it('base_legal', 'Base legal', None, None, 'F01', 'LC 164/2024, arts. 100–101', None, 'texto', texto_original='O município poderá outorgar, onerosamente, o direito de construir acima do índice de aproveitamento básico até o limite do índice de aproveitamento máximo do lote (...) de acordo com a lei específica.'),
    it('ia_basico', 'IA básico (todas as macrozonas)', 1, 'coeficiente', 'F01', 'LC 164/2024, art. 50 §1º'),
    it('ia_maximo', 'IA máximo por macrozona', None, 'coeficiente', 'F01', 'LC 164/2024, art. 50 §1º', None, 'condicional', condicionais=[C(m, IA_MACRO[m][1], codigo=m) for m in IA_MACRO]),
    it('cumulatividade_tdc', 'OODC e TDC cumulativas até o IA máximo', None, None, 'F02', 'LUOS art. 53 §2º', None, 'texto', texto_original='podendo esses instrumentos serem aplicados de forma cumulativa até o limite do IA Máximo'),
    it('formula_contrapartida', 'Fórmula / contrapartida', None, None, 'F01', 'LC 164/2024, art. 101, I–VI', 'Depende de lei municipal específica não localizada (ver lacunas).', 'sem_dado'),
    it('isencao_his', 'Isenção para HIS', None, None, 'F01', 'LC 164/2024, art. 101 p.ú.', 'Única exceção admitida à proibição de isenção: HIS e equipamentos públicos (depende da lei específica).', 'texto', texto_original='Não poderá ser concedido benefício de isenção para outorga onerosa do direito de construir para novas edificações, exceto habitações de interesse social e para equipamentos públicos.'),
    it('fruicao_publica', 'Potencial adicional por fruição pública', None, None, 'F01', 'LC 164/2024, arts. 119–123 (alt. LC 171/2025 arts. 120 e 123)', 'A área de fruição pública vira potencial adicional no próprio lote, somável a OODC/TDC até o IA máximo; recuo frontal flexível (calçada mín. 2/3/4 m em via local/coletora/arterial); uso não residencial do térreo não computável.', 'livre'),
    it('outorga_ambiental_seav', 'Outorga Onerosa Ambiental (SEAV)', None, 'coeficiente', 'F02', 'LUOS arts. 37–39 e 54; Anexo VII', 'IA máx 1,4/1,6/1,8/2,0 conforme 30–40/40–50/50–60/>60% de área preservada; valores em lei específica (não localizada).', 'condicional',
       condicionais=[C('30–40% preservado', 1.4), C('40–50%', 1.6), C('50–60%', 1.8), C('>60%', 2.0)]),
    it('infraestrutura', 'Sem infraestrutura comprovada', None, None, 'F01', 'LC 164/2024, art. 50 §2º', 'Usa-se o IA básico.', 'texto', texto_original='Caso a existência das infraestruturas não seja comprovada, deverá ser utilizado o índice de aproveitamento básico.')])

zeis_his = dict(resumo='ZEIS 1 (assentamentos a regularizar) e ZEIS 2 (vazios para HIS) – PD arts. 54–59; 74 ZEIS listadas na LC 171/2025 (Anexo III) sem parâmetros próprios; flexibilização só por lei específica (LUOS art. 51). Em 2025 foram criadas por lei duas ZEIS 2 com parâmetros e coordenadas: Democracia (Lei 15.606) e Rio Sanhauá (Lei 15.607). HIS definida pelo Dec. 10.560/2024: 25–70 m² privativos, pé-direito ≥2,40 m, renda até R$ 8.000 (ou teto MCMV), vagas 20% UH.',
    fonte_id='F07', artigo_anexo='LC 164/2024 arts. 54–59; LUOS art. 51; Dec. 10.560/2024; Leis 15.606 e 15.607/2025', itens=[
    it('tipos_zeis', 'Tipos de ZEIS', None, None, 'F01', 'LC 164/2024, art. 55, I e II', None, 'texto', texto_original='ZEIS 1: assentamentos habitacionais de baixa renda, consolidados, carentes de infraestrutura, passíveis de regularização e de HIS; ZEIS 2: lotes ou glebas não edificadas ou subutilizadas, dotadas de infraestrutura, destinadas prioritariamente a famílias de projetos de urbanização ou a conjuntos de HIS promovidos pelo poder público.'),
    it('zeis_listadas', 'ZEIS listadas (LC 171/2025, Anexo III)', 74, 'zonas', 'F04', 'LC 171/2025, Anexo III', 'Área total listada ≈482,7 ha; geometria aproximada na camada zeis_pd.'),
    it('flexibilizacao', 'Flexibilização de parâmetros em ZEIS', None, None, 'F02', 'LUOS art. 51', None, 'texto', texto_original='Nas ZEIS (...) será permitida a flexibilização dos parâmetros urbanísticos de ocupação do solo, desde que previstas em programa voltado à regularização fundiária e em projeto urbanístico específico, mediante eventual exigência de contrapartidas urbanísticas, mediante parecer técnico do órgão licenciador, aprovação pelo CDU e publicação de Lei específica.'),
    it('criacao_zeis', 'Criação/alteração de ZEIS', None, None, 'F01', 'LC 164/2024, art. 54 p.ú.; art. 58', 'Por lei, ouvido o CDU; plano urbanístico participativo próprio para cada ZEIS.', 'livre'),
    it('his_area_privativa', 'HIS – área privativa', None, 'm2', 'F07', 'Dec. 10.560/2024, art. 3º, I, a', None, 'faixa', faixa={'min': 25, 'max': 70}),
    it('his_pe_direito', 'HIS – pé-direito mínimo', 2.40, 'm', 'F07', 'Dec. 10.560/2024, art. 3º, I, c'),
    it('his_vagas', 'HIS – vagas mínimas (proporção das UH)', None, None, 'F07', 'Dec. 10.560/2024, art. 3º, I, d', 'Automóveis 20%, bicicletas 30%, motocicletas 15% das UH (dimensões do COE). Dispensáveis em parte em ZEIS (art. 3º §1º).', 'texto',
       texto_original='oferecer vagas em quantidade mínima equivalente à proporção de unidades habitacionais: 30% para bicicletas, 20% para automóveis e 15% para motocicletas'),
    it('his_renda', 'HIS – renda familiar', 8000, 'R$/mês', 'F07', 'Dec. 10.560/2024, arts. 2º §2º, 3º, II, a e 4º', 'Renda bruta familiar até R$ 8.000 ou, no MCMV, o teto do programa; classes HIS-1/2/3 no art. 4º (HIS-1 até R$ 2.640; HIS-2 até R$ 4.400; HIS-3 até R$ 8.000 – leitura do OCR do art. 4º, conferir no original). Comprovação de vínculo ao MCMV dispensa demais requisitos de renda.'),
    it('zeis_democracia', 'ZEIS Democracia (Lei 15.606/2025)', None, None, 'F11', 'Lei 15.606/2025, arts. 1º–4º', 'ZEIS 2, 29.920,83 m²; ≥60% H3 e ≤40% comércio/serviço; TO 40%, TAP 40% (20% verde), recuos 5/1,5/2 m, 4 pavimentos; Portaria MCID 725/2023 (MCMV) e Dec. 10.560/2024. Zona sobreposta ZEIS-DEMOCRACIA.', 'livre'),
    it('zeis_rio_sanhaua', 'ZEIS Rio Sanhauá (Lei 15.607/2025)', None, None, 'F12', 'Lei 15.607/2025, arts. 1º–5º', 'ZEIS 2, 10.967,04 m², realocação Porto do Capim; habitação + até 20% comércio; renda até R$ 2.640 (MCMV Faixa 1); TO 40%, TAP 40%, recuos 5/1,5/2 m; pavimentos 1/3/6 e AM 7,5/13,5/18 m por setor. Zona sobreposta ZEIS-RIO-SANHAUA.', 'livre'),
    it('fundo_urbanizacao', 'Fundo de Urbanização', None, None, 'F04', 'LC 164/2024 art. 171 §2º (redação LC 171/2025)', 'Recursos (inclusive OODC) destinados à urbanização de ZEIS, produção de HIS e infraestrutura.', 'livre'),
    it('isencao_oodc_his', 'HIS e OODC', None, None, 'F01', 'LC 164/2024, art. 101 p.ú.', 'HIS é a exceção que admite isenção de OODC (depende da lei específica).', 'livre')])

outros = dict(resumo='TDC regulamentada (Lei 15.409/2024 + Dec. 11.266/2026); OUC (PD arts. 105–111) e TER na Ilha do Bispo (arts. 124–126) sem projeto aprovado localizado; EIV exigido em casos citados (ZEPA-3; empreendimentos de impacto em via local vedados), sem lei geral de EIV localizada; restrição da orla (9 faixas), Altiplano, Centro Histórico, COMAER/PEZR.',
    fonte_id='F01', artigo_anexo='LC 164/2024; LUOS; Lei 15.409/2024', itens=[
    it('tdc', 'Transferência do Direito de Construir', None, None, 'F05', 'Lei 15.409/2024; PD arts. 102–104; Dec. 11.266/2026', 'Imóveis cedentes: MPA, Centro Histórico e RPPNM. Potencial: PCC = (C × A × i) − Ac, com i = 1,5/1,2/1,0/0,8 por porte do lote; transferido: PT = PCC × Vc/Vr. Certidão válida por 1 ano. Receptor limitado ao IA máximo da macrozona.', 'formula', formula='PCC = (C × A × i) − Ac; PT = PCC × Vc / Vr'),
    it('ouc', 'Operações Urbanas Consorciadas', None, None, 'F01', 'LC 164/2024, arts. 105–111 (art. 110 alt. LC 171/2025)', 'Por lei específica; recursos aplicados exclusivamente na própria OUC; CEPAC (art. 111). Nenhuma OUC vigente localizada.', 'livre'),
    it('ter_ilha_do_bispo', 'Território de Estruturação e Requalificação (TER)', None, None, 'F01', 'LC 164/2024, arts. 124–126; LUOS art. 52', 'Aplicado na Ilha do Bispo: índices diferentes dos da LUOS mediante projeto de urbanização aprovado (CDU/DCU) e contrapartidas. Perímetro não vetorizado.', 'livre'),
    it('eiv', 'Estudo de Impacto de Vizinhança', None, None, 'F02', 'LUOS art. 29 p.ú.; LC 169 Anexo III; PD art. 109', 'Exigido expressamente na ZEPA-3 e no âmbito das OUC; empreendimentos de impacto vedados em via local. Lei municipal geral de EIV (lista de empreendimentos) não localizada.', 'livre'),
    it('aprovacao_semob_uh', 'Aprovação SEMOB por porte habitacional', None, 'UH', 'F03', A3, None, 'condicional', condicionais=[C('via coletora – habitacionais com mais de 100 UH', 100), C('via arterial – habitacionais com mais de 200 UH', 200)]),
    it('orla_alturas', 'Alturas na faixa de 500 m da orla', None, 'm', 'F02', 'LUOS arts. 61–62', 'Ver camada orla_faixas.', 'condicional', condicionais=[C(f'{k}ª faixa', v) for k, v in enumerate([12.9, 16.5, 19.5, 22.5, 25.5, 28.5, 31.5, 34.0, 35.0], 1)]),
    it('comaer', 'Restrições aeronáuticas', None, None, 'F02', 'LUOS art. 59', 'Plano Básico de Zona de Proteção de Aeródromos (COMAER/ANAC) e Plano de Proteção de Canais de Micro-ondas (ANATEL). PEZR do aeroporto (Aena) publicado no portal, não vetorizado.', 'livre'),
    it('centro_historico', 'Centro Histórico', None, None, 'F02', 'LUOS art. 60; PD art. 63', 'Alturas do Centro Histórico pela análise IPHAN/IPHAEP; regulamentação complementar com índices por quadra.', 'livre'),
    it('altiplano', 'Altiplano do Cabo Branco', None, None, 'F01', 'LC 164/2024, art. 65', 'Restrição adicional: limitar alturas para preservar a paisagem da falésia e a Ponta do Cabo Branco (camada restricoes_adicionais).', 'livre'),
    it('falesias', 'Faixa de proteção das falésias', 100, 'm', 'F02', 'LUOS art. 28 §2º', 'Em nenhuma hipótese serão permitidas construções na faixa dos 100 m de proteção das falésias.'),
    it('peuc', 'Parcelamento/Edificação Compulsórios', None, None, 'F01', 'LC 164/2024, art. 87', 'Por lei específica; subutilizado = construído < 5% do potencial.', 'livre'),
    it('limites_zona_prolongamento', 'Prolongamento de parâmetros nas vias limítrofes', None, None, 'F02', 'LUOS art. 5º', 'Parâmetros de ZH/ZCS que tenham vias como limite aplicam-se aos lotes com frente para ambos os lados da via (não vale para ZBD, ZEPA, ZI, ZDTRL, ZDTRS, SEAV).', 'livre')])

macrozonas = [dict(codigo=m, nome=NOME_MACRO[m], descricao={'MAD-1': 'Áreas de maiores densidade e dinâmica, com infraestrutura que permite intensificação; alto potencial construtivo (PD art. 47, I).',
    'MAD-2': 'Grande potencial ou tendência de ocupação na próxima década; intensificação moderada (PD art. 47, II). Portal do Sol: infraestrutura dimensionada como MAD-1 (§2º).',
    'MAD-3': 'Infraestrutura e suporte ambiental restringem a intensificação (PD art. 47, III).',
    'MBD': 'Características predominantemente rurais; controle da expansão e proteção de mananciais (PD art. 47, IV).',
    'MPA': 'Proteção e conservação ambiental e paisagística primordiais (PD art. 47, V).'}[m] + f' Área vetorizada (LC 171): {MG[m].area/1e4:.0f} ha.',
    parametros={'ca_basico': P(IA_MACRO[m][0], 'F01', 'LC 164/2024, art. 50 §1º', None, 'coeficiente'), 'ca_maximo': P(IA_MACRO[m][1], 'F01', 'LC 164/2024, art. 50 §1º', None, 'coeficiente')}) for m in IA_MACRO]

resumo_mcmv = [
    'H3 (multifamiliar) permitido em ZH-1 a ZH-5, ZCS-1 a ZCS-5, ZEPA-2, ZEPA-3 e SEAV; PROIBIDO em ZCS-6, ZCS-7, ZI-1, ZI-2 e ZBD (LC 169/2024 Anexo III).',
    'IA básico 1 em toda a cidade; IA máximo pela macrozona: MAD-1 6, MAD-2 4, MAD-3 2, MBD/MPA 1 (PD art. 50) – o excedente só por OODC/TDC; HIS é a única exceção admitida à proibição de isenção de OODC (PD art. 101 p.ú.), mas a lei da OODC não foi localizada.',
    'Parâmetros típicos para MCMV em ZH-2 (maior zona, 5.428 ha): TO 55% (H3 em via local/coletora: 50% até 3 PV / 55% até 4 PV), TAP 5%, RFT 5 m, RL 1,5 m até 3º PV, RFD 2–3 m; AM sem limite fora da orla (LC 169 Anexo IV).',
    'Vagas: H3 com UH ≤30 m² 1 vaga/4 UH; >30 m² 1 vaga/2 UH; HIS conforme Dec. 10.560/2024: automóveis 20% das UH, bicicletas 30%, motos 15%.',
    'HIS (Dec. 10.560/2024): área privativa 25–70 m², pé-direito ≥2,40 m, renda até R$ 8.000 ou teto MCMV; empreendimento vinculado ao MCMV comprova o enquadramento; em ZEIS alguns requisitos dispensados.',
    'Via coletora: habitacional >100 UH precisa de aprovação SEMOB; via arterial: >200 UH (LC 169 Anexo III). Via local veda empreendimentos de impacto.',
    'ZEIS 2 criadas em 2025 para HIS/MCMV com parâmetros próprios: Democracia (Mangabeira, 2,99 ha; ≥60% H3; TO 40%, TAP 40%, 4 PV) e Rio Sanhauá (Varadouro, 1,10 ha; Faixa 1 até R$ 2.640; 1–6 PV por setor).',
    'Orla (500 m): altura de 12,90 m a 35,00 m por faixa – limita fortemente o multifamiliar em ZH-3/ZH-4/ZH-5/ZCS-3/ZCS-5.',
    'Áreas de suscetibilidade alta a inundação/movimento de massa e tombamentos (PD Anexo VIII) exigem atenção na viabilidade.',
]

lacunas = [
    dict(item='Lei específica da OODC (fórmula, contrapartida, isenção HIS)', motivo='Prevista no PD art. 101; não consta na página de legislação vigente nem foi localizada no SAPL.'),
    dict(item='Lei de Parcelamento do Solo municipal (lote mínimo/testada por zona)', motivo='Referida na LUOS (arts. 38 e 51) mas não publicada na página de legislação vigente; usado o mínimo federal (Lei 6.766/1979) exceto ZBD (20.000 m²).'),
    dict(item='Lei geral de EIV', motivo='Não localizada; EIV citado apenas em casos específicos (ZEPA-3, OUC).'),
    dict(item='Geometria oficial vetorial do zoneamento, macrozonas, ZEIS e restrições', motivo='Prefeitura não publica camadas vetoriais públicas (www.joaopessoa.pb.gov.br e filipeia retornam 403; dados.joaopessoa inacessível). Geometrias vetorizadas dos PDFs das leis (oficial:false).'),
    dict(item='Mapa de zoneamento da LC 169/2024 (Anexo I) só em raster', motivo='Alterações aplicadas por registro raster (erro ~35 m); pequenas mudanças <5 ha podem não estar refletidas.'),
    dict(item='Faixas da orla conforme LC 169/2024 (Anexo II)', motivo='Raster de baixa resolução; usado o traçado vetorial do Anexo III original da LUOS.'),
    dict(item='ZEIS do PD (LC 171/2025 Anexo II) sem nomes por polígono', motivo='Mapa raster sem rótulos legíveis; 381,6 ha vetorizados de ≈482,7 ha listados; ZEIS pequenas podem faltar.'),
    dict(item='Setores da ZEIS Rio Sanhauá', motivo='Quadros de coordenadas dos Setores 01–04 (Anexos III–VI) não vetorizados; parâmetros por setor só como condicionais.'),
    dict(item='Falésias (faixa de 100 m) e PEZR do aeroporto', motivo='Falésias são linhas no PD Anexo VIII e o PEZR é PDF da Aena; não poligonizados.'),
    dict(item='Área de manancial', motivo='Mapa do PD indica "proposta preliminar".'),
    dict(item='TER Ilha do Bispo e OUC', motivo='Sem perímetro/projeto aprovado localizado.'),
    dict(item='LC 171/2025 – art. 50', motivo='A LC 171 lista o art. 50 entre os alterados mas publica só "Art. 50 … §1º … §2º …" (sem texto novo visível); mantidos os IA da redação original da LC 164/2024.'),
    dict(item='Classes de renda HIS-1/2/3 (Dec. 10.560/2024 art. 4º)', motivo='Texto lido por OCR de DOM em duas colunas; conferir valores no original.'),
    dict(item='Densidade máxima', motivo='PD e LUOS não fixam densidade.'),
]

camadas_geo = [
    dict(nome='Zoneamento LUOS + LC 169 (20 zonas base)', arquivo='geo_raw/zonas_lc169_corrigido_utm.geojson', campo='codigo', fonte_url=URL_LUOS_MAPA, data_download=HOJE, oficial=False,
         metodo='Vetorização do PDF vetorial (Anexo II LUOS, p. 46; fills por cor, ordem de pintura) + grade UTM; correções LC 169 Anexo I por registro ECC do raster', erro_estimado_m=15.0, n_feicoes=20),
    dict(nome='SEAV, faixa de 500 m e bordas de tabuleiro', arquivo='geo_raw/luos_overlays_utm.geojson', campo='codigo', fonte_url=URL_LUOS_MAPA, data_download=HOJE, oficial=False, metodo='Caminhos de recorte (hachuras) do PDF vetorial', erro_estimado_m=15.0, n_feicoes=3),
    dict(nome='Faixas da orla (9)', arquivo='geo_raw/orla_faixas_utm.geojson', campo='codigo', fonte_url=URL_LUOS_MAPA, data_download=HOJE, oficial=False, metodo='Caminhos de recorte do Anexo III da LUOS (p. 48) com registro afim à faixa de 500 m', erro_estimado_m=20.0, n_feicoes=9),
    dict(nome='Macrozonas PD + LC 171', arquivo='geo_raw/macrozonas_lc171_corrigido_utm.geojson', campo='codigo', fonte_url=FONTES[0]['url'], data_download=HOJE, oficial=False, metodo='PDF vetorial PD p. 74 + correção raster LC 171 Anexo I (ECC)', erro_estimado_m=15.0, n_feicoes=5),
    dict(nome='ZEIS LC 171 (Anexo II)', arquivo='geo_raw/lc171_zeis_utm.geojson', campo='codigo', fonte_url=FONTES[3]['url'], data_download=HOJE, oficial=False, metodo='Máscara de cor no raster + registro SIFT/RANSAC ao PD p. 76', erro_estimado_m=35.0, n_feicoes=len(cam['zeis_pd']['features'])),
    dict(nome='ZEIS Democracia e Rio Sanhauá', arquivo='geo_raw/zeis_leis_2025_utm.geojson', campo='codigo', fonte_url=FONTES[10]['url'], data_download=HOJE, oficial=True, metodo='Coordenadas UTM SIRGAS 2000 dos quadros oficiais das Leis 15.606 e 15.607/2025', erro_estimado_m=1.0, n_feicoes=2),
    dict(nome='Proteção ambiental (PD Anexo VII)', arquivo='geo_raw/pd_restricoes_ambientais_utm.geojson', campo='codigo', fonte_url=FONTES[0]['url'], data_download=HOJE, oficial=False, metodo='PDF vetorial PD p. 88', erro_estimado_m=15.0, n_feicoes=len(cam['protecao_ambiental']['features'])),
    dict(nome='Restrições adicionais (PD Anexo VIII)', arquivo='geo_raw/pd_restricoes_adicionais_utm.geojson', campo='codigo', fonte_url=FONTES[0]['url'], data_download=HOJE, oficial=False, metodo='PDF vetorial PD p. 90 (fills e clips)', erro_estimado_m=20.0, n_feicoes=len(cam['restricoes_adicionais']['features'])),
    dict(nome='Limite municipal IBGE 2024 (validação)', arquivo='geo_raw/ibge_pb/', campo='CD_MUN=2507507', fonte_url=FONTES[13]['url'], data_download=HOJE, oficial=True, metodo='Download público IBGE (geoftp)', erro_estimado_m=None, n_feicoes=1),
]
geografico = dict(
    descricao='Não existe camada vetorial pública oficial do zoneamento de João Pessoa; as geometrias foram vetorizadas dos mapas das próprias leis (PDFs vetoriais da LUOS e do PD, georreferenciados pela grade UTM SIRGAS 2000/25S impressa; alterações das LC 169/2024 e LC 171/2025 aplicadas por registro dos rasters). Exceção: as ZEIS Democracia e Rio Sanhauá, construídas das coordenadas oficiais publicadas nas leis (oficial:true). Coordenadas WGS84 com 6 casas; simplificação 2–5 m.',
    crs='EPSG:4326', crs_area='EPSG:31985', servidor_oficial=None, camadas=camadas_geo,
    regras_de_consulta=('1) Zona base: as 20 zonas base formam partição do município. Lote em duas zonas (LUOS art. 6º): se >70% numa zona, aplicam-se os parâmetros dela a todo o lote; entre 45% e 55%, pode-se adotar qualquer das duas; nos demais casos cada zona vale na sua porção. '
        'Exceção: ZEPA, ZBD, ZDTRL, ZDTRS e SEAV valem exatamente nos seus limites (art. 6º p.ú.). Parâmetros de ZH/ZCS limitadas por via valem para lotes nos dois lados da via (art. 5º). '
        '2) IA: básico 1; máximo pela macrozona do lote (camada macrozonas: MAD-1 6, MAD-2 4, MAD-3 2, MBD 1, MPA 1), só onerosamente (OODC/TDC). '
        '3) SEAV (prioridade 10, substitui, limiar 0): parâmetros próprios e IA máx 1,4–2,0 por área preservada. '
        '4) ZEIS-DEMOCRACIA e ZEIS-RIO-SANHAUA (prioridade 20, substitui; IA mantém a base/macrozona). '
        '5) orla_faixas: altura máxima da faixa (a menor de cada faixa atingida). '
        '6) zeis_pd, protecao_ambiental, restricoes_adicionais e bordas_tabuleiro: alertas por código. Confirmar sempre na SEPLAN/SEDURB.'),
    regras_de_consulta_texto='Base (regra 70%/45–55% do art. 6º) → IA pela macrozona → SEAV/ZEIS por lei → altura da orla → alertas.',
    raio_divisa_m=30, pct_minimo_significativo=0.5,
    limitacoes=['Geometrias não oficiais (vetorização dos mapas das leis), erro 15–35 m; não usar para decisões no limite entre zonas sem consulta à Prefeitura.',
                'Alterações da LC 169/2024 (zoneamento) e LC 171/2025 (macrozonas, ZEIS) aplicadas por comparação de rasters de baixa resolução.',
                'Faixas da orla do Anexo III original (LC 169 Anexo II raster não verificável faixa a faixa).',
                'Restrições adicionais simplificadas (5 m) e sem fragmentos < 2.000 m².',
                'Setores da ZEIS Rio Sanhauá, perímetro do TER e PEZR não vetorizados.'],
    notas_tecnicas={'log_lc169': LOG169, 'registro_orla': reg, 'scripts': ['vetorizar_luos.py', 'comparar_lc169.py', 'aplicar_lc169.py', 'vetorizar_pd.py', 'vetorizar_pd_p90.py', 'comparar_lc171.py', 'vetorizar_lc171_zeis.py', 'vetorizar_orla_faixas.py', 'zeis_leis_coordenadas.py', 'build_joao_pessoa.py']})

marco = ('Plano Diretor: LC 164/2024 (11/01/2024), alterada pela LC 171/2025 (09/01/2025). Uso e ocupação: LUOS LC 166/2024 (29/04/2024, republicada), com Anexos II–VI substituídos pela LC 169/2024 (19/12/2024). '
         'Instrumentos: TDC Lei 15.409/2024 + Dec. 11.266/2026; HIS Dec. 10.560/2024; ZEIS Leis 15.606 e 15.607/2025; Sistema Viário Lei 15.197/2024 (alt. Lei 15.609/2025). Vigentes em 27/10/2026.')

doc = dict(schema_versao='1.1', municipio='João Pessoa', uf='PB', slug='joao-pessoa-pb', codigo_ibge='2507507', data_levantamento=HOJE,
           centro_mapa=dict(lat=-7.1195, lon=-34.8450, zoom=12), marco_legal_vigente=marco, orgao_confirmacao='SEPLAN / SEDURB – Prefeitura Municipal de João Pessoa (consulta prévia / Diretoria de Controle Urbano)',
           aviso='Geometrias aproximadas (vetorização não oficial dos mapas das leis), exceto as ZEIS das Leis 15.606/15.607. Confirmar parâmetros e enquadramento na Prefeitura.',
           fontes=FONTES, macrozonas=macrozonas,
           macrozonas_observacao='As macrozonas definem o IA máximo do lote; geometria na camada complementar "macrozonas" (papel macrozona).',
           zonas=zonas, camadas_complementares=cam, outorga_onerosa=outorga, zeis_his=zeis_his, outros_parametros=outros,
           resumo_mcmv=resumo_mcmv, geografico=geografico, lacunas=lacunas)
out = os.path.join(BASE, 'joao-pessoa-pb.json')
json.dump(doc, open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', out, round(os.path.getsize(out) / 1e6, 2), 'MB', len(zonas), 'zonas', len(cam), 'camadas')
