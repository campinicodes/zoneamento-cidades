#!/usr/bin/env python3
"""Gera porto-alegre-rs.json (schema 1.1) a partir de:
 - geo_raw/pddua_regime.geojson (ArcGIS Hosted/PDDUA – subunidades com regime D/A/IA/V)
 - geo_raw/*.geojson baixados por baixar_camadas.py (Consultas_MIL1)
 - shapefiles oficiais da página Mapas Digitais (AEIS, PBZPA, APP) em geo_raw/*.zip
 - tabelas transcritas em tabelas_pddua.py
Uso: python3 build_poa.py"""
import warnings; warnings.filterwarnings('ignore', category=DeprecationWarning)
import json, os, re, zipfile, tempfile, glob, collections, datetime
import shapefile
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from shapely.validation import make_valid
from pyproj import CRS, Transformer
from tabelas_pddua import DENSIDADE, GA, IA, IA_REGIME_PROPRIO, VOL, PERM_POR_TO, lote_padrao

HERE = os.path.dirname(os.path.abspath(__file__))
CID = os.path.dirname(HERE)
RAW = os.path.join(CID, 'geo_raw')
OUT = os.path.join(CID, 'porto-alegre-rs.json')
HOJE = '2026-10-27'
TOL = 0.00001  # ~1,1 m em graus (lat -30)

# ----------------------------------------------------------------- fontes
PU = 'https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Anexos%20PDDUA/'
MD = 'https://prefeitura.poa.br/sites/default/files/usu_img/planejamento_urbano/Mapas%20Digitais/'
GIS = 'https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/'
FONTES = [
 ('F01', 'PDDUA – Plano Diretor de Desenvolvimento Urbano Ambiental, compilação com anexos (versão 20251216)', 'Lei Complementar nº 434/1999 e alterações', '1999-12-01 (compilação 2025-12-16)',
  'https://licenciamento-api.procempa.com.br/api/urbanismodrive/geopmpa/SPM/PUBLICO/PDDUA_ATUAL/ANEXOS%20ATUALIZADOS/PDDUA%2020251216%20com%20Anexos.pdf', 'PDDUA_compilado_20251216.pdf'),
 ('F02', 'PDDUA Anexo 4 – Densidades brutas', 'LC 434/1999, Anexo 4', '1999-12-01', PU + 'Anexo_4.pdf', 'PDDUA_Anexo_4.pdf'),
 ('F03', 'PDDUA Anexo 5 – Regime de atividades (5.1 grupamentos; 5.3/5.4 Área Intensiva com redação do Dec. 20.628/2020; 5.5 Área Rarefeita)', 'LC 434/1999, Anexo 5; Decreto nº 20.628/2020', '2020-06-25', PU + 'Anexo_5.pdf', 'PDDUA_Anexo_5.pdf'),
 ('F04', 'PDDUA Anexo 6 – Índices de aproveitamento e quota ideal', 'LC 434/1999, Anexo 6', '1999-12-01', PU + 'Anexo_6.pdf', 'PDDUA_Anexo_6.pdf'),
 ('F05', 'PDDUA Anexo 7 – Regime volumétrico (7.1 por UEU; 7.2 malha viária)', 'LC 434/1999, Anexo 7', '1999-12-01', PU + 'Anexo_7.pdf', 'PDDUA_Anexo_7.pdf'),
 ('F06', 'PDDUA Anexo 8 – Parcelamento do solo (8.1 loteamentos; 8.2 desmembramentos)', 'LC 434/1999, Anexo 8', '1999-12-01', PU + 'Anexo_8.pdf', 'PDDUA_Anexo_8.pdf'),
 ('F07', 'PDDUA Anexo 10 – Garagens e estacionamentos (Anexo 10.1 alterado pelo Dec. 20.385/2019)', 'LC 434/1999, Anexo 10; Decreto nº 20.385/2019', '2019-11-01', PU + 'Anexo_10.pdf', 'PDDUA_Anexo_10.pdf'),
 ('F08', 'PDDUA Anexo 11 – Projetos Especiais de Impacto Urbano (1º e 2º graus)', 'LC 434/1999, Anexo 11', '1999-12-01', PU + 'Anexo_11.pdf', 'PDDUA_Anexo_11.pdf'),
 ('F09', 'Plano Diretor Urbano Sustentável – PDUS (sancionado, regras a partir de 2027)', 'Lei Complementar nº 1.075/2026', '2026-07-14', 'https://dopaonlineupload.procempa.com.br/dopaonlineupload/6102_ce_619410_1.pdf', 'LC1075_2026_PDUS.pdf'),
 ('F10', 'Lei de Parcelamento, Uso e Ocupação do Solo – LUOS (sancionada, vigência 180 dias após publicação)', 'Lei Complementar nº 1.076/2026', '2026-07-14', 'https://dopaonlineupload.procempa.com.br/dopaonlineupload/6102_ce_619426_1.pdf', 'LC1076_2026_LUOS.pdf'),
 ('F11', 'Notícia oficial – Prefeito sanciona novo Plano Diretor e LUOS', 'PMPA – Gabinete do Prefeito', '2026-07-14', 'https://prefeitura.poa.br/gp/noticias/prefeito-sanciona-novo-plano-diretor-e-lei-de-uso-e-ocupacao-do-solo', None),
 ('F12', 'Notícia oficial SMAMUS – Regras do novo Plano Diretor passam a valer a partir de 2027', 'PMPA – SMAMUS', '2026', 'https://www.prefeitura.poa.br/smamus/noticias/regras-do-novo-plano-diretor-passam-valer-partir-de-2027', None),
 ('F13', 'Fomento à produção de Habitação de Interesse Social (HIS) – isenções de Solo Criado e regime volumétrico', 'Lei Complementar nº 1.022/2024', '2024-09-12', 'https://dopaonlineupload.procempa.com.br/dopaonlineupload/5342_ce_491154_1.pdf', 'LC1022_2024_HIS.pdf'),
 ('F14', 'Regulamenta a LC 1.022/2024 – Comissão/rito de Projeto Especial para HIS', 'Decreto nº 22.932/2024', '2024-09-30', 'https://dopaonlineupload.procempa.com.br/dopaonlineupload/5370_ce_503434_1.pdf', 'Dec22932_2024.pdf'),
 ('F15', 'Programa Minha Casa, Minha Vida – Porto Alegre (incentivos urbanísticos e tributários)', 'Lei Complementar nº 636/2010', '2010-01-13', 'https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2010/36557/lei_complementar_no_636.docx', 'LC636_2010.docx'),
 ('F16', 'Padrões construtivos para Habitação de Interesse Social', 'Lei Complementar nº 548/2006', '2006', 'https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2006/34245/lei_complementar_no_548.docx', 'LC548_2006.docx'),
 ('F17', 'Parcelamento do solo de interesse social', 'Lei Complementar nº 547/2006', '2006', 'https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2006/34244/lei_complementar_no_547.docx', 'LC547_2006.docx'),
 ('F18', 'Outorga onerosa do direito de construir (Solo Criado) – fórmula e fator de planejamento', 'Lei Complementar nº 946/2022', '2022', 'https://legislacao.portoalegre.rs.gov.br/media/sapl/public/normajuridica/2022/44102/lei_complementar_no_946.pdf', 'LC946_2022.pdf'),
 ('F19', 'Parecer PGM sobre a LC 636/2010 (repositório institucional DSpace PMPA)', 'PGM Porto Alegre', '2011', 'https://dspace.portoalegre.rs.gov.br/bitstreams/1de45b15-d02e-491d-80ce-cb52e7992be1/download', 'dspace_doc.pdf'),
 ('F20', 'Camada oficial do regime urbanístico por subunidade (PDDUA) – ArcGIS REST SMAMUS', 'Base cartográfica PMPA/SMAMUS', HOJE, GIS + 'Hosted/PDDUA/FeatureServer/0', None),
 ('F21', 'Mapas digitais da SMAMUS – shapefiles oficiais (AEIS 12/05/2022, PBZPA/PBZPH, APP) e metadados', 'PMPA/SMAMUS', HOJE, 'https://prefeitura.poa.br/smamus/planejamento-urbano/mapas-digitais', 'mapas_digitais.html'),
 ('F22', 'Serviço público POA – Consultas MIL1 (macrozonas, zona rural, bens tombados/inventariados, suscetibilidade a inundação, setores de risco CPRM, unidades de conservação)', 'PMPA/SMAMUS', HOJE, GIS + 'POA___Consultas_MIL1/MapServer', None),
 ('F23', 'Perímetro do Programa +4D (4º Distrito) – ArcGIS REST', 'Lei Complementar nº 960/2022', '2022-10-05', GIS + 'Hosted/Limite_Programa_4D_130326/FeatureServer/0', None),
 ('F24', 'Guia Prático do PDDUA (leitura do regime urbanístico)', 'PMPA/SMAMUS', 's/d', MD + 'Guia%20Pratico.pdf', 'Guia_Pratico.pdf'),
 ('F25', 'Metadados do PDDUA (dicionário de campos DENSIDADE/ATIVIDADE/INDICE/VOLUMETRIA)', 'PMPA/SMAMUS', 's/d', MD + 'PDDUA_Metadados.zip', None),
 ('F26', 'Mapa oficial das AEIS (PDF)', 'PMPA/SMAMUS', 's/d', MD + 'AEIS.pdf', 'AEIS.pdf'),
]
FID = {f[0] for f in FONTES}

def P(valor, unidade, fonte, art, obs=None, forma=None, **kw):
    if forma is None:
        forma = 'unico' if isinstance(valor, (int, float)) else ('lista' if isinstance(valor, list) else 'sem_dado')
    assert fonte is None or fonte in FID, fonte
    d = dict(valor=valor, unidade=unidade, fonte_id=fonte, artigo_anexo=art, observacao=obs, forma=forma)
    d.update(kw)
    return d

def TXT(texto, unidade, fonte, art, obs=None):
    return P(None, unidade, fonte, art, obs, forma='texto', texto_original=texto)

def SEM(unidade, obs, art=None):
    return P(None, unidade, None, art, obs, forma='sem_dado')

def C(condicao, forma, valor=None, **kw):
    d = dict(condicao=condicao, forma=forma, valor=valor); d.update(kw); return d

# ----------------------------------------------------------------- geometria
def rnd(g):
    def r(c):
        if isinstance(c[0], (list, tuple)): return [r(x) for x in c]
        return [round(c[0], 6), round(c[1], 6)]
    m = mapping(g); return {'type': m['type'], 'coordinates': r(m['coordinates'])}

def limpa(g, tol=TOL):
    if g is None or g.is_empty: return None
    g = make_valid(g)
    if g.geom_type == 'GeometryCollection':
        polys = [x for x in g.geoms if x.geom_type in ('Polygon', 'MultiPolygon')]
        if not polys: return None
        g = unary_union(polys)
    if tol: g = g.simplify(tol, preserve_topology=True)
    g = make_valid(g)
    if g.geom_type == 'GeometryCollection':
        g = unary_union([x for x in g.geoms if x.geom_type in ('Polygon', 'MultiPolygon')])
    if g.is_empty or g.geom_type not in ('Polygon', 'MultiPolygon'): return None
    # garante validade após arredondamento
    gj = rnd(g); g2 = shape(gj)
    if not g2.is_valid:
        g2 = make_valid(g2)
        if g2.geom_type == 'GeometryCollection':
            g2 = unary_union([x for x in g2.geoms if x.geom_type in ('Polygon', 'MultiPolygon')])
        if g2.is_empty: return None
        gj = rnd(g2)
        if not shape(gj).is_valid: return None
    return gj

def le_geojson(nome):
    p = os.path.join(RAW, nome + '.geojson')
    return json.load(open(p)) if os.path.exists(p) else None

def le_shp(zipname, base):
    d = tempfile.mkdtemp()
    zipfile.ZipFile(os.path.join(RAW, zipname)).extractall(d)
    shp = glob.glob(os.path.join(d, '**', base + '.shp'), recursive=True)[0]
    prj = open(shp[:-4] + '.prj').read()
    tr = Transformer.from_crs(CRS.from_wkt(prj), CRS.from_epsg(4326), always_xy=True)
    r = shapefile.Reader(shp, encoding='utf-8')
    out = []
    for k in range(len(r)):
        try:
            g = shape(r.shape(k).__geo_interface__)
        except Exception:
            continue  # feição sem geometria no shapefile oficial
        if g.is_empty: continue
        g = transform(tr.transform, g)
        out.append((r.record(k).as_dict(), g))
    return out

def norm(c):
    c = str(c).strip().upper()
    m = re.match(r'^0*(\d+)(.*)$', c)
    if not m: return c
    return m.group(1) + m.group(2)

# ----------------------------------------------------------------- parâmetros de zona base
RAREF_D = {'31', '33', '35', '37'}
GA_RAREF = {'19.1', '19.2', '19.3', '21', '23', '25', '27'}

def area_ocupacao(d, a, i):
    if d in RAREF_D or i in RAREF_D or a in GA_RAREF: return 'rarefeita'
    if d in ('99',) and i == '999': return None
    return 'intensiva'

def categoria(a, i, area):
    ga = GA.get(a)
    iam = IA.get(i)
    camax = (iam[1] if iam[1] is not None else iam[0]) if iam else None
    def dens(x):
        if x is None: return None
        return 'baixa' if x <= 1.5 else ('media' if x <= 3 else 'alta')
    if a.startswith('15') or a.startswith('16'): return 'patrimonio_cultural', f'GA {a} (Área de interesse/ambiência cultural – Anexo 5.1)'
    if a == '17': return 'institucional', 'GA 17 – Área de interesse institucional'
    if a.startswith('19'): return 'ambiental', f'GA {a} – Área de proteção do ambiente natural (AOR)'
    if a == '23': return 'rural', 'GA 23 – produção primária / Zona Rural (LC 775/2015)'
    if a in ('21', '25'): return 'rural', f'GA {a} – Área de Ocupação Rarefeita (densidade bruta ≤ 17 hab/ha)'
    if a == '27': return 'expansao', 'GA 27 – Área com potencial de ocupação intensiva (AOR)'
    if a == '13': return 'industrial', 'GA 13 – Área predominantemente produtiva (habitação proibida)'
    if a == '11': return 'especial_economica', 'GA 11 – Mista 05 (habitação proibida no Anexo 5.3; residencial só por Projeto Especial)'
    if ga is None or dens(camax) is None: return 'outra', f'códigos A{a}/IA{i} sem correspondência documentada nas tabelas do PDDUA'
    pre = 'residencial' if a == '1' else 'mista'
    return f'{pre}_{dens(camax)}_densidade', f'GA {a} ({ga[0]}); CA máx {camax} (≤1,5 baixa; ≤3 média; >3 alta)'

def params_base(d, a, i, v):
    area = area_ocupacao(d, a, i)
    pr = {}
    pr['ca_minimo'] = SEM('coeficiente', 'O PDDUA não fixa CA mínimo por zona (parcelamento/edificação compulsórios dependem de lei específica).')
    # IA
    if i in IA:
        b, mx, q = IA[i]
        pr['ca_basico'] = P(b, 'coeficiente', 'F04', f'Anexo 6, código IA {i}; arts. 107–108 LC 434/99', 'Índice de aproveitamento (IA) básico sobre a área do terreno.')
        if mx is not None:
            pr['ca_maximo'] = P(mx, 'coeficiente', 'F04', f'Anexo 6, código IA {i} (IA máximo); arts. 110–111 LC 434/99',
                                'IA máximo atingível com Solo Criado (outorga onerosa) e/ou Transferência de Potencial Construtivo, condicionado ao estoque da UEU/quarteirão (art. 53) e às modalidades do art. 111 (pequeno ≤300 m², médio 300–1.000 m², grande >1.000 m²).')
        else:
            pr['ca_maximo'] = P(b, 'coeficiente', 'F01', 'art. 110 LC 434/99; Anexo 6 (código IA ' + i + ')',
                                'Área de Ocupação Rarefeita: Solo Criado e TPC aplicam-se só na Área de Ocupação Intensiva (art. 110) – IA máximo = IA básico.')
    elif i in IA_REGIME_PROPRIO:
        t = IA_REGIME_PROPRIO[i]
        if i in ('23', '25'):  # nota (2) do Anexo 6: teto numérico explícito
            for k in ('ca_basico', 'ca_maximo'):
                pr[k] = P(None, 'coeficiente', 'F04', f'Anexo 6, código IA {i}, nota (2); art. 85 LC 434/99',
                          'Regime urbanístico próprio: só o teto é fixado em lei (IA ≤ 2,5, salvo a exceção do art. 85); valor exato na DMI do imóvel.',
                          forma='faixa', faixa=dict(min=None, max=2.5), texto_original=t)
        else:
            pr['ca_basico'] = TXT(t, 'coeficiente', 'F04', f'Anexo 6, código IA {i}', 'Consultar a DMI do imóvel.')
            pr['ca_maximo'] = TXT(t, 'coeficiente', 'F04', f'Anexo 6, código IA {i}', 'Consultar a DMI do imóvel.')
    else:
        pr['ca_basico'] = SEM('coeficiente', f'Código IA "{i}" sem correspondência no Anexo 6 (código não documentado nos metadados; possivelmente regime próprio/AEIS – confirmar na DMI).')
        pr['ca_maximo'] = SEM('coeficiente', pr['ca_basico']['observacao'])
    # volumetria
    if v in VOL:
        alt, div, base, to, b90 = VOL[v]
        art = f'Anexo 7.1, código volumetria {v}; art. 113 LC 434/99'
        if b90:
            pr['taxa_ocupacao'] = P(None, 'fracao', 'F05', art, 'Nota (1)/(2)/(3) do Anexo 7.1: TO de 90% na base e 75% no corpo para terrenos com frente para as vias do Anexo 7.2 (e área central, códigos 08–19).', forma='condicional',
                                    condicionais=[C('corpo do edifício / caso geral', 'unico', to), C('base (até a altura da base) – terreno com frente para via do Anexo 7.2 ou na área central', 'unico', 0.9)])
        else:
            pr['taxa_ocupacao'] = P(to, 'fracao', 'F05', art)
        if alt is not None:
            pr['gabarito_altura_max_m'] = P(alt, 'm', 'F05', art, 'Altura máxima da edificação; sujeita também às restrições aeronáuticas (PBZPA/COMAER – ver camada pbzpa).')
        else:
            pr['gabarito_altura_max_m'] = TXT('Nota (3) do Anexo 7.1: no alinhamento, 1 pavimento para cada 2 m de largura do logradouro, até 10 pavimentos; acima disso, recuo de frente de 2 m por pavimento adicional a partir do último pavimento não recuado. TO base 90% e corpo 75%.', 'm', 'F05', art)
        # permeabilidade (art. 96)
        conds = []
        conds.append(C(f'terreno < 1.500 m² com TO de {int(round(to*100,0)) if to!=0.666 else 66.6}%', 'unico', PERM_POR_TO[to]))
        if b90: conds.append(C('terreno < 1.500 m² usando TO de 90% (base)', 'unico', 0.07))
        conds.append(C('terreno > 1.500 m² (TO até 75%)', 'unico', 0.2, observacao='Com TO de 90% aplicam-se medidas alternativas (§§ 9º e 11) até completar os 20%.'))
        pr['taxa_permeabilidade'] = P(None, 'fracao', 'F01', 'art. 96 §§ 7º a 11 LC 434/99 (redação LC 646/2010)',
                                       'Área Livre permeável (AL) mínima. Compensação por medidas alternativas (terraço verde, piso semipermeável, plantio) até 50% da AL (≤1.500 m²), 40% (1.500–3.000 m²) ou 30% (>3.000 m²) – art. 96 §10.', forma='condicional', condicionais=conds)
        outros_vol = dict(
            altura_divisa_m=TXT(div, 'm', 'F05', art, 'Altura máxima permitida na divisa (lateral/fundos sem afastamento).') if div else P(None, 'm', 'F05', art, 'Sem construção na divisa definida no Anexo 7.1 para este código.', forma='nao_aplicavel'),
            altura_base_m=TXT(base, 'm', 'F05', art, 'Altura máxima da base (pode ocupar a TO de base).') if base else P(None, 'm', 'F05', art, 'Código sem base.', forma='nao_aplicavel'))
    elif v == '25':
        art = 'Anexo 7.1, código 25, nota (4); LC 930/2021'
        for k, u in (('taxa_ocupacao', 'fracao'), ('gabarito_altura_max_m', 'm'), ('taxa_permeabilidade', 'fracao')):
            pr[k] = TXT('Regime urbanístico próprio: na UEU 026 da MZ1 e subunidade 05 da UEU 002 da MZ1 (Programa de Reabilitação do Centro Histórico, LC 930/2021) a volumetria é estabelecida pelo GABARITO.', u, 'F05', art)
        outros_vol = {}
    else:
        for k, u in (('taxa_ocupacao', 'fracao'), ('gabarito_altura_max_m', 'm'), ('taxa_permeabilidade', 'fracao')):
            pr[k] = SEM(u, f'Código de volumetria "{v}" sem correspondência no Anexo 7.1 (não documentado; confirmar na DMI).')
        outros_vol = {}
    pr['gabarito_pavimentos'] = None
    # recuos
    if area:
        fr = 4 if area == 'intensiva' else 12
        frontal = P(fr, 'm', 'F01', 'art. 117 I LC 434/99', f'Recuo para ajardinamento na Área de Ocupação {area.capitalize()}, medido do alinhamento (exceções do art. 122; vias do Anexo 7.2 podem ter regra própria).')
    else:
        frontal = SEM('m', 'Área de ocupação (intensiva/rarefeita) não determinável pelos códigos da subunidade.')
    lat_conds = [C('edificação até a altura máxima na divisa (Anexo 7.1)', 'unico', 0, observacao='Pode encostar nas divisas laterais/fundos até a altura na divisa.'),
                 C('acima da altura na divisa, H ≤ 27 m', 'formula', None, formula='0.18*H', faixa=dict(min=3, max=None)),
                 C('acima da altura na divisa, 27 m < H ≤ 42 m', 'formula', None, formula='0.20*H', faixa=dict(min=3, max=None)),
                 C('acima da altura na divisa, H > 42 m', 'formula', None, formula='0.25*H', faixa=dict(min=3, max=None))]
    lat = P(None, 'm', 'F01', 'art. 113 III a LC 434/99 (redação LC 646/2010)', 'Recuos de altura aplicados a partir da base; H = altura da edificação; mínimo 3 m.', forma='condicional', condicionais=lat_conds)
    pr['recuos'] = dict(frontal=frontal, lateral=lat, fundos=json.loads(json.dumps(lat)))
    # lote
    lm, tm, desc = lote_padrao(a)
    if lm is not None:
        pr['lote_minimo_m2'] = P(lm, 'm2', 'F06', f'Anexo 8.1 – {desc}', 'Padrão para lotes de loteamento; em loteamento de interesse social admite-se lote de 125 m² com testada 5 m (nota 3). Eixos do Anexo 7.2: 450 m²/15 m.')
    elif desc:
        pr['lote_minimo_m2'] = TXT(desc, 'm2', 'F06', 'Anexo 8.1')
    else:
        pr['lote_minimo_m2'] = SEM('m2', 'GA sem coluna correspondente no Anexo 8.1.')
    if tm is not None:
        pr['testada_minima_m'] = P(tm, 'm', 'F06', f'Anexo 8.1 – {desc}')
    else:
        pr['testada_minima_m'] = SEM('m', 'Anexo 8.1 não fixa testada para esta área (ou definida a critério do SMGP).')
    # usos
    if a in GA:
        nome, mf = GA[a]
        rotulo = {'permitido': 'habitação (inclusive multifamiliar) permitida sem restrição (S/R)', 'proibido': 'habitação PROIBIDA',
                  'projeto_especial': 'habitação admitida só mediante Projeto Especial / regras da Área Rarefeita', None: 'regime de uso específico'}[mf]
        art_u = 'Anexo 5.1 e Anexo 5.3 (Dec. 20.628/2020)' if a not in GA_RAREF else 'Anexo 5.1 e Anexo 5.5'
        pr['usos_permitidos'] = P([f'GA {a} – {nome}'], 'codigos_de_uso', 'F03', art_u, 'Grupamento de atividades da subunidade; ' + rotulo + '. Demais atividades conforme as tabelas do Anexo 5.')
        txt = {'permitido': 'Habitação (1.1 a 1.4 do Anexo 5.2, inclusive multifamiliar) permitida sem restrição de porte (S/R) no GA ' + a + ' – Anexo 5.3.',
               'proibido': 'Habitação PROIBIDA no GA ' + a + ' (Anexo 5.3/5.5).',
               None: 'GA ' + a + ' com regime de uso específico (parque/institucional) – consultar legislação específica.'}
        if mf == 'projeto_especial':
            if a == '11':
                t = 'Anexo 5.3: habitação PROIBIDA (²) na Mista 05; Anexo 8.1 nota (6): mediante Projeto Especial será analisado o uso residencial; Anexo 11.2: condomínio/loteamento residencial na Mista 05 = Projeto Especial de 2º grau.'
                fo, ar = 'F03', 'Anexo 5.3; Anexo 8.1 nota (6); Anexo 11.2'
            else:
                t = 'Anexo 5.5 (Área Rarefeita) lista "Habitação" entre as atividades do GA ' + a + '; empreendimento habitacional de interesse social na Área Rarefeita é Projeto Especial de 2º grau (Anexo 11.2)' + ('; nota (1) do Anexo 5.5: para HIS adota-se o GA da Área Intensiva via Projeto Especial.' if a == '27' else '.')
                fo, ar = 'F03', 'Anexo 5.5; Anexo 11.2'
            hab = TXT(t, None, fo, ar)
        else:
            hab = TXT(txt[mf], None, 'F03', art_u)
    else:
        pr['usos_permitidos'] = SEM('codigos_de_uso', f'Código de atividade "{a}" sem correspondência no Anexo 5.1 (não documentado; possivelmente regime próprio – confirmar na DMI).')
        hab = SEM(None, 'Sem GA documentado.')
    pr['vagas'] = P(None, 'vagas/UH', 'F07', 'Anexo 10.1 folha 1 (Dec. 20.385/2019)', 'Cota por vaga 25–30 m². Condomínios por unidades autônomas: ver Res. 02/2000. Empreendimentos PMCMV em AEIS podem reduzir para 50% do nº de UH (LC 636/2010 art. 21).', forma='condicional',
                    condicionais=[C('residencial em terreno com testada ≥ 12 m', 'unico', 0, observacao='Isento de vagas obrigatórias.'),
                                  C('residencial em terreno com testada < 12 m', 'sem_dado', None, observacao='Anexo 10.1 (Dec. 20.385/2019) não lista o caso; confirmar no Escritório de Licenciamento.')])
    # densidade
    if d in DENSIDADE:
        dd = DENSIDADE[d]
        if dd.get('conforme_projeto'):
            pr['densidade'] = TXT('Densidade conforme projeto (Anexo 4, código ' + d + ').', 'hab/ha', 'F02', f'Anexo 4, código {d}')
        else:
            ob = f"Densidade bruta total {dd['hab_tot']} hab/ha e {dd['econ_tot']} economias/ha"
            if dd.get('hab_priv') is not None and dd.get('hab_sc'):
                ob += f" (privado {dd['hab_priv']} hab/ha e {dd['econ_priv']} econ/ha + Solo Criado {dd['hab_sc']} hab/ha e {dd['econ_sc']} econ/ha)"
            pr['densidade'] = P(dd['hab_tot'], 'hab/ha', 'F02', f'Anexo 4, código {d}; art. 66 LC 434/99', ob + '. Controle por UEU/quarteirão (estoque).')
    else:
        pr['densidade'] = SEM('hab/ha', f'Código de densidade "{d}" sem correspondência no Anexo 4 (não documentado).')
    # outros
    out = {}
    out['habitacao_multifamiliar'] = hab
    if i in IA and IA[i][2]:
        out['quota_ideal_m2_por_economia'] = P(IA[i][2], 'm2/economia', 'F04', f'Anexo 6, código IA {i}; art. 109 LC 434/99',
                                              'Fração mínima de terreno por economia. Aplica-se a edificações residenciais com volumetria 01, condomínios de casas na Área Intensiva e a toda a Área Rarefeita (art. 109); empreendimentos DHP/MCMV na Área Intensiva são dispensados (LC 636/2010 art. 28).')
    out['area_de_ocupacao'] = TXT('Área de Ocupação ' + (area.capitalize() if area else 'não determinada'), None, 'F01', 'arts. 27–28 LC 434/99') if area else SEM(None, 'Não determinada.')
    out['solo_criado'] = (TXT('Solo Criado e TPC aplicáveis (Área de Ocupação Intensiva), até o IA máximo e limitados ao estoque da UEU/quarteirão.', None, 'F01', 'arts. 53, 110 e 111 LC 434/99; LC 946/2022')
                          if area == 'intensiva' else P(None, None, 'F01', 'art. 110 LC 434/99', 'Solo Criado/TPC não se aplicam na Área Rarefeita.', forma='nao_aplicavel') if area == 'rarefeita' else SEM(None, 'Indeterminado.'))
    out.update(outros_vol)
    pr['outros'] = out
    return pr, area

# ----------------------------------------------------------------- montagem
def main():
    reg = le_geojson('pddua_regime')
    combos = collections.defaultdict(list)
    for f in reg['features']:
        p = f['properties']
        if not f.get('geometry'): continue
        d, a, i, v = (norm(p['densidade']), norm(p['atividade']), norm(p['indice']), norm(p['volumetria']))
        cod = f'D{d}-A{a}-IA{i}-V{v}'
        g = limpa(shape(f['geometry']))
        if g is None: continue
        obs = [str(p[k]) for k in ('obs_1', 'obs_2', 'obs_3', 'obs_4', 'obs_5') if p.get(k) not in (None, 0, '0')]
        combos[cod].append(({'codigo': cod, 'mz': p.get('mz'), 'ueu': p.get('ueu'), 'subunidade': p.get('subunidade'), 'cod_subun': p.get('cod_subun'),
                             'obs_codigos': ','.join(obs) or None}, g, (d, a, i, v)))
    zonas = []
    for cod in sorted(combos):
        feats = combos[cod]
        d, a, i, v = feats[0][2]
        pr, area = params_base(d, a, i, v)
        cat, crit = categoria(a, i, area)
        ga = GA.get(a, (None,))[0]
        nome = f'Regime D{d}/A{a}/IA{i}/V{v}' + (f' – {ga}' if ga else '')
        desc = (f'Subunidades do PDDUA com densidade código {d} (Anexo 4), grupamento de atividades {a} (Anexo 5.1), índice de aproveitamento {i} (Anexo 6) e volumetria {v} (Anexo 7.1). '
                f'{len(feats)} subunidade(s); Área de Ocupação {area or "indeterminada"}.')
        obsz = ['Código sintético da plataforma = combinação dos 4 códigos do regime urbanístico do PDDUA (campos DENSIDADE/ATIVIDADE/INDICE/VOLUMETRIA da camada oficial); a DMI do imóvel prevalece.',
                'Cada feição traz MZ/UEU/subunidade (cod_subun) e os códigos de observação (OBS_1..5) da base oficial – o significado dessas observações não está publicado nos metadados.']
        if '99' in (d,) or a == '99.99' or i == '999' or v == '999':
            obsz.append('Códigos 99/99.99/999 não constam dos Anexos nem dos metadados; ocorrem, p.ex., em subunidades de AEIS e de regime próprio – parâmetros null (ver lacunas).')
        zonas.append(dict(codigo=cod, nome=nome, descricao=desc, tipo='base', prioridade=0, categoria_normalizada=cat, categoria_criterio=crit,
                          regra_sobreposicao=None, parametros=pr, observacoes=obsz,
                          geometria=dict(type='FeatureCollection', crs='EPSG:4326 (lon, lat)', fonte='ArcGIS REST SMAMUS Hosted/PDDUA/FeatureServer/0 (F20)', oficial=True,
                                         observacao_geometria='Subunidades oficiais, simplificadas ~1 m (preserve_topology), coordenadas com 6 casas.',
                                         features=[dict(type='Feature', properties=pp, geometry=g) for pp, g, _ in feats])))
    # ---- AEIS (sobrepostas)
    aeis = le_shp('Shapefile_AEIS.zip', 'AEIS_12_05_2022')
    grp = collections.defaultdict(list)
    mapa_tipo = {'AEIS I': 'AEIS I', 'AEIS II': 'AEIS II', 'AEIS III': 'AEIS III', 'AEIS IV': 'AEIS IV', 'AEIS I - AEIS II': 'AEIS I-II', 'AEIS': 'AEIS'}
    for rec, g in aeis:
        t = mapa_tipo.get((rec.get('TIPO') or '').strip(), 'AEIS')
        gj = limpa(g)
        if gj is None: continue
        grp[t].append(({'codigo': t, 'nome': (rec.get('NOME') or '').strip() or None, 'lei': (rec.get('LEI') or '').strip() or None, 'decreto': (rec.get('DECRETO') or '').strip() or None,
                        'cod_subun': rec.get('COD_SUBUN'), 'observacao': (rec.get('OBSERVACAO') or '').strip() or None}, gj))
    desc_aeis = {
        'AEIS I': 'AEIS I – assentamentos autoproduzidos por população de baixa renda (regularização fundiária e urbanística) – art. 76 I.',
        'AEIS II': 'AEIS II – loteamentos públicos ou privados irregulares/clandestinos ocupados por população de baixa renda – art. 76 II.',
        'AEIS III': 'AEIS III – imóveis não edificados/subutilizados na Área de Ocupação Intensiva destinados à produção de HIS com interveniência do Poder Público – art. 76 III.',
        'AEIS IV': 'AEIS IV – áreas ocupadas em situação precária/risco destinadas a reassentamento – art. 76 IV.',
        'AEIS I-II': 'Polígono classificado na base oficial como "AEIS I - AEIS II".',
        'AEIS': 'Polígono AEIS sem tipo especificado na base oficial.'}
    prio = {'AEIS III': 40, 'AEIS I': 30, 'AEIS II': 30, 'AEIS I-II': 30, 'AEIS IV': 30, 'AEIS': 30}
    for t in sorted(grp):
        H = lambda unid, k: P(None, unid, 'F01', 'art. 76 §8º LC 434/99', 'Regime urbanístico da AEIS definido por decreto específico; enquanto isso vale o regime da subunidade (base).', forma='herda_da_base')
        pr = dict(ca_minimo=H('coeficiente', 0), ca_basico=H('coeficiente', 0), ca_maximo=H('coeficiente', 0), taxa_ocupacao=H('fracao', 0),
                  gabarito_altura_max_m=H('m', 0), gabarito_pavimentos=None, taxa_permeabilidade=H('fracao', 0),
                  recuos=dict(frontal=H('m', 0), lateral=H('m', 0), fundos=H('m', 0)),
                  lote_minimo_m2=P(125, 'm2', 'F06', 'Anexo 8.1 nota (3)', 'Loteamento de interesse social: lote 125 m², testada 5 m; nas AEIS I, II e III dispensa-se a malha viária mínima e o percentual de equipamentos é definido por projeto (art. 139-B).'),
                  testada_minima_m=P(5, 'm', 'F06', 'Anexo 8.1 nota (3)'),
                  usos_permitidos=H('codigos_de_uso', 0),
                  vagas=P(0.5, 'vagas/UH', 'F15', 'LC 636/2010 art. 21', 'Empreendimentos identificados como AEIS podem reduzir o padrão de vagas em até 50% do nº de UH (mínimo resultante).'),
                  densidade=H('hab/ha', 0),
                  outros=dict(instrumentos_his=TXT('Urbanizador Social (LO 9.162/2003); Fundo Municipal de HIS (LC 612/2009); empreendimentos incentivados do PMCMV-POA passam a ser AEIS (LC 636/2010 art. 20).', None, 'F01', 'art. 76 §§3º–4º; LC 636/2010 art. 20')))
        zonas.append(dict(codigo=t, nome=t, descricao=desc_aeis[t], tipo='sobreposta', prioridade=prio[t], categoria_normalizada='especial_interesse_social',
                          categoria_criterio='Área Especial de Interesse Social (PDDUA art. 76)',
                          regra_sobreposicao=dict(efeito='apenas_alerta', usa_indices_de=None, aplica_sobre=None, limiar_pct=None, requer_testada=False, distancia_max_m=None,
                                                  fundamento='PDDUA art. 76 e §8º (regime por decreto); LC 636/2010 arts. 20–21; Anexo 8.1 nota (3)', mantem_da_base=[],
                                                  alerta=f'Terreno em {t}: área destinada a HIS/regularização. Regime urbanístico próprio por decreto (art. 76 §8º) – confirmar na DMI; vagas MCMV podem cair a 50% das UH (LC 636/2010 art. 21).'),
                          parametros=pr, observacoes=['Geometria do shapefile oficial AEIS_12_05_2022 (Mapas Digitais SMAMUS); data da base 12/05/2022 – AEIS instituídas depois disso podem faltar.'],
                          geometria=dict(type='FeatureCollection', crs='EPSG:4326 (lon, lat)', fonte='Shapefile_AEIS.zip – AEIS_12_05_2022 (F21), reprojetado de TM-POA (SIRGAS 2000, MC -51°)', oficial=True,
                                         observacao_geometria='Reprojeção TM-POA → EPSG:4326 com pyproj; simplificação ~1 m.',
                                         features=[dict(type='Feature', properties=pp, geometry=g) for pp, g in grp[t]])))
    # ---- camadas
    cam = {}
    geo_camadas = []
    def add_geo(nome, arquivo, url, n, metodo='vetor oficial', erro=None, oficial=True):
        geo_camadas.append(dict(nome=nome, arquivo=arquivo, fonte_url=url, data_download=HOJE, oficial=oficial, metodo=metodo, erro_estimado_m=erro, n_feicoes=n))
    add_geo('Regime urbanístico por subunidade (zonas base)', 'geo_raw/pddua_regime.geojson', GIS + 'Hosted/PDDUA/FeatureServer/0', len(reg['features']))
    add_geo('AEIS (zonas sobrepostas)', 'geo_raw/Shapefile_AEIS.zip', MD + 'Shapefile_AEIS.zip', len(aeis))
    # macrozonas
    mzn = {1: 'Cidade Radiocêntrica', 2: 'Corredor de Desenvolvimento', 3: 'Cidade Xadrez', 4: 'Cidade da Transição', 5: 'Cidade Jardim', 6: 'Eixo Lomba-Restinga',
           7: 'Restinga', 8: 'Cidade Rururbana', 9: 'Unidades de conservação estaduais – Parque Estadual e APA Delta do Jacuí', 10: 'Lomba do Pinheiro (criada pela LC 630/2009 – Operação Urbana Consorciada revogada pela LC 950/2022)'}
    mz = le_geojson('macrozona'); fe = []
    gm = collections.defaultdict(list)
    for f in mz['features']:
        c = f['properties'].get('MZ')
        if c is None or not f.get('geometry'): continue
        gm[int(c)].append(shape(f['geometry']))
    for c in sorted(gm):
        gj = limpa(unary_union([make_valid(x) for x in gm[c]]), TOL * 2)
        if gj: fe.append(dict(type='Feature', properties=dict(codigo=f'MZ{c}', nome=mzn.get(c)), geometry=gj))
    ppc = {f'MZ{c}': {'descricao': TXT(mzn[c], None, 'F01', 'art. 29 LC 434/99' if c < 10 else 'Compilação PDDUA, nota ao art. 29 (LC 630/2009; LC 950/2022)')} for c in gm if c in mzn}
    cam['macrozonas'] = dict(papel='macrozona', descricao='Macrozonas do PDDUA (art. 29).', fonte='ArcGIS REST SMAMUS – POA___Consultas_MIL1/MapServer/77', oficial=True,
                             fonte_id='F22', artigo_anexo='art. 29 LC 434/99', observacao='Informativo: os índices vêm da subunidade, não da macrozona.', parametros_por_codigo=ppc, alerta_por_codigo=None, features=fe)
    add_geo('Macrozonas', 'geo_raw/macrozona.geojson', GIS + 'POA___Consultas_MIL1/MapServer/77', len(mz['features']))
    # zona rural
    zr = le_geojson('zona_rural')
    g = limpa(unary_union([make_valid(shape(f['geometry'])) for f in zr['features'] if f.get('geometry')]), TOL * 2)
    cam['zona_rural'] = dict(papel='restricao', descricao='Zona Rural (LC 775/2015) – parcelamento urbano e habitação multifamiliar não admitidos.', fonte='ArcGIS REST SMAMUS – Consultas_MIL1/MapServer/76', oficial=True,
                             fonte_id='F22', artigo_anexo='LC 775/2015; Anexo 5.1 nota (**)', observacao=None, parametros_por_codigo=None,
                             alerta_por_codigo={'ZONA_RURAL': 'Terreno na Zona Rural (LC 775/2015): inviável para MCMV/loteamento urbano.'},
                             features=[dict(type='Feature', properties=dict(codigo='ZONA_RURAL'), geometry=g)])
    add_geo('Zona Rural', 'geo_raw/zona_rural.geojson', GIS + 'POA___Consultas_MIL1/MapServer/76', len(zr['features']))
    # PBZPA
    pb = le_shp('Shapefile_PBZPA_PBZPH.zip', 'LIMITES_DECEA'); fe = []; al = {}
    for rec, g in pb:
        c = f"{rec['LOCAL'].strip()} – {rec['DESCRICAO'].strip()}"
        c = re.sub(r'\s+', ' ', c)
        gj = limpa(g)
        if gj is None: continue
        fe.append(dict(type='Feature', properties=dict(codigo=c, cota=rec.get('COTA'), mensagem=rec.get('MENSAGEM')), geometry=gj))
        al.setdefault(c, f'{c}: restrição aeronáutica (PBZPA/PZPANA – Portaria DECEA/COMAER). Ver cota e mensagem da feição; análise do DECEA pode ser exigida. ' + (rec.get('MENSAGEM') or '')[:300])
    cam['pbzpa'] = dict(papel='restricao', descricao='Superfícies limitadoras de obstáculos dos aeródromos/helipontos (PBZPA, PZPANA, PBZPH) – limitam a altura das edificações.', fonte='Shapefile_PBZPA_PBZPH.zip – LIMITES_DECEA (Mapas Digitais SMAMUS)', oficial=True,
                        fonte_id='F21', artigo_anexo='PDDUA art. 96 (notas: Portarias DECEA 957/2015, 260/2016); IN 07/2021 SMAMS', observacao='Base de 2021 (data dos arquivos). Altitude/altura máxima do objeto aparece na DMI.',
                        parametros_por_codigo=None, alerta_por_codigo=al, features=fe)
    add_geo('PBZPA/PZPANA/PBZPH (DECEA)', 'geo_raw/Shapefile_PBZPA_PBZPH.zip', MD + 'Shapefile_PBZPA_PBZPH.zip', len(pb))
    ru = le_shp('Shapefile_PBZPA_PBZPH.zip', 'PBZPA_RUIDO'); fe = []; al = {}
    for rec, g in ru:
        c = re.sub(r'\s+', ' ', f"{rec['LOCAL'].strip()} – {rec['ZONA'].strip()} – {(rec.get('OBS') or '').strip()[:60]}")
        gj = limpa(g)
        if gj is None: continue
        fe.append(dict(type='Feature', properties=dict(codigo=c, obs=rec.get('OBS')), geometry=gj))
        al.setdefault(c, f"Plano Específico de Zoneamento de Ruído: {(rec.get('OBS') or '').strip()} – usos compatíveis pela Tabela E-2 do RBAC 161/ANAC (residencial pode ser incompatível).")
    cam['ruido_aeroportuario'] = dict(papel='restricao', descricao='Curvas do Plano (Específico) de Zoneamento de Ruído – PEZR/PZR dos aeródromos.', fonte='Shapefile_PBZPA_PBZPH.zip – PBZPA_RUIDO', oficial=True,
                                      fonte_id='F21', artigo_anexo='PDDUA art. 96 (nota RBAC 161/2011)', observacao=None, parametros_por_codigo=None, alerta_por_codigo=al, features=fe)
    add_geo('Zoneamento de ruído aeroportuário', 'geo_raw/Shapefile_PBZPA_PBZPH.zip', MD + 'Shapefile_PBZPA_PBZPH.zip', len(ru))
    # APP
    fe = []
    for base, c, n in (('CONV_APP_CDAGUA', 'APP_CURSO_DAGUA', 'APP de curso d\'água'), ('CONV_APP_TMORRO', 'APP_TOPO_MORRO', 'APP de topo de morro')):
        rs = le_shp('Shapefile_APP.zip', base)
        for rec, g in rs:
            gj = limpa(g)
            if gj is None: continue
            pp = dict(codigo=c, nome=n)
            if rec.get('MORRO'): pp['morro'] = rec.get('MORRO')
            fe.append(dict(type='Feature', properties=pp, geometry=gj))
        add_geo(n + ' (convencionada)', 'geo_raw/Shapefile_APP.zip', MD + 'Shapefile_APP.zip', len(rs))
    cam['app'] = dict(papel='restricao', descricao='Áreas de Preservação Permanente convencionadas pelo Município (Lei Federal 12.651/2012 art. 4º): cursos d\'água e topos de morro.', fonte='Shapefile_APP.zip (Mapas Digitais SMAMUS)', oficial=True,
                      fonte_id='F21', artigo_anexo='PDDUA art. 96 §3º; Lei Federal 12.651/2012 art. 4º', observacao='Faixas convencionadas; a delimitação definitiva é feita no licenciamento ambiental.', parametros_por_codigo=None,
                      alerta_por_codigo={'APP_CURSO_DAGUA': 'APP de curso d\'água – área não edificável (Código Florestal art. 4º).', 'APP_TOPO_MORRO': 'APP de topo de morro – área não edificável.'}, features=fe)
    # tombados
    tb = le_geojson('tombados_inventariados')
    if tb:
        fe = []
        for f in tb['features']:
            if not f.get('geometry'): continue
            c = (f['properties'].get('PROTECAO') or 'Sem classificação').strip()
            gj = limpa(shape(f['geometry']), 0)
            if gj is None: continue
            fe.append(dict(type='Feature', properties=dict(codigo=c, nome=f['properties'].get('NOME'), endereco=f['properties'].get('ENDERECO'), instancia=(f['properties'].get('INSTANCIA') or '').strip() or None), geometry=gj))
        codes = sorted({x['properties']['codigo'] for x in fe})
        cam['patrimonio_cultural'] = dict(papel='restricao', descricao='Bens tombados, inventariados (estruturação/compatibilização) e entornos – LC 601/2008.', fonte='ArcGIS REST SMAMUS – Consultas_MIL1/MapServer/141', oficial=True,
                                          fonte_id='F22', artigo_anexo='LC 601/2008; PDDUA arts. 92 e Anexo 11 (bens tombados/inventariados = Projeto Especial 1º grau)', observacao=None, parametros_por_codigo=None,
                                          alerta_por_codigo={c: f'Imóvel/entorno com proteção cultural "{c}": análise da EPAHC/COMPAHC; demolição e volumetria restritas; Projeto Especial de 1º grau (Anexo 11).' for c in codes}, features=fe)
        add_geo('Bens tombados e inventariados', 'geo_raw/tombados_inventariados.geojson', GIS + 'POA___Consultas_MIL1/MapServer/141', len(tb['features']))
    # suscetibilidade e risco
    si = le_geojson('susc_inundacao')
    if si:
        gg = collections.defaultdict(list)
        for f in si['features']:
            if f.get('geometry'): gg[f['properties']['CLASSE']].append(make_valid(shape(f['geometry'])))
        fe = []
        for c in sorted(gg):
            gj = limpa(unary_union(gg[c]), TOL * 2)
            if gj: fe.append(dict(type='Feature', properties=dict(codigo=f'INUNDACAO_{c.upper()}'.replace('É', 'E'), classe=c), geometry=gj))
        cam['suscetibilidade_inundacao'] = dict(papel='restricao', descricao='Cartas de suscetibilidade a inundação (CPRM/SGB, 2012–2014).', fonte='ArcGIS REST SMAMUS – Consultas_MIL1/MapServer/154', oficial=True,
                                                fonte_id='F22', artigo_anexo='Lei Federal 12.608/2012 (cartas de suscetibilidade)', observacao='Não reflete a cheia de maio/2024; ver também LC 1.022/2024 art. 6º.', parametros_por_codigo=None,
                                                alerta_por_codigo={x['properties']['codigo']: f"Suscetibilidade {x['properties']['classe']} a inundação (CPRM) – exige estudo de drenagem/cota de soleira." for x in fe}, features=fe)
        add_geo('Suscetibilidade a inundação (CPRM)', 'geo_raw/susc_inundacao.geojson', GIS + 'POA___Consultas_MIL1/MapServer/154', len(si['features']))
    rc = le_geojson('risco_cprm')
    if rc:
        fe = []
        for f in rc['features']:
            if not f.get('geometry'): continue
            p = f['properties']; c = f"RISCO_{p['GRAU_RISCO'].upper().replace(' ', '_')}"
            gj = limpa(shape(f['geometry']))
            if gj: fe.append(dict(type='Feature', properties=dict(codigo=c, tipologia=p.get('TIPOLOGIA'), setor=p.get('SETOR'), local=p.get('LOCAL')), geometry=gj))
        cam['setores_risco'] = dict(papel='restricao', descricao='Setores de risco alto e muito alto (CPRM/SGB) – inundação, deslizamento, enxurrada, erosão, queda, corrida.', fonte='ArcGIS REST SMAMUS – Consultas_MIL1/MapServer/152', oficial=True,
                                    fonte_id='F22', artigo_anexo='Lei Federal 12.608/2012', observacao=None, parametros_por_codigo=None,
                                    alerta_por_codigo={'RISCO_ALTO': 'Setor de risco ALTO (CPRM) – inviável sem obras de mitigação.', 'RISCO_MUITO_ALTO': 'Setor de risco MUITO ALTO (CPRM) – evitar.'}, features=fe)
        add_geo('Setores de risco (CPRM)', 'geo_raw/risco_cprm.geojson', GIS + 'POA___Consultas_MIL1/MapServer/152', len(rc['features']))
    uc = le_geojson('unid_conservacao')
    if uc:
        fe = []
        for f in uc['features']:
            gj = limpa(shape(f['geometry'])) if f.get('geometry') else None
            if gj: fe.append(dict(type='Feature', properties=dict(codigo='UNIDADE_CONSERVACAO', nome=f['properties'].get('UC') or f['properties'].get('NOME'), lei=f['properties'].get('LEI')), geometry=gj))
        cam['unidades_conservacao'] = dict(papel='restricao', descricao='Unidades de conservação municipais (Morro do Osso, Saint-Hilaire, Refúgio São Pedro, Reserva Biológica do Lami).', fonte='ArcGIS REST SMAMUS – Consultas_MIL1/MapServer/114', oficial=True,
                                           fonte_id='F22', artigo_anexo='Lei Federal 9.985/2000; leis municipais de criação', observacao=None, parametros_por_codigo=None,
                                           alerta_por_codigo={'UNIDADE_CONSERVACAO': 'Unidade de conservação – ocupação vedada/restrita ao plano de manejo.'}, features=fe)
        add_geo('Unidades de conservação municipais', 'geo_raw/unid_conservacao.geojson', GIS + 'POA___Consultas_MIL1/MapServer/114', len(uc['features']))
    l4 = le_geojson('limite_4d')
    if l4:
        fe = [dict(type='Feature', properties=dict(codigo='PROGRAMA_4D', nome=f['properties'].get('nome'), lei=f['properties'].get('legislacao')), geometry=limpa(shape(f['geometry']))) for f in l4['features'] if f.get('geometry')]
        cam['programa_4d'] = dict(papel='informativa', descricao='Perímetro do Programa +4D de Regeneração Urbana do 4º Distrito (LC 960/2022) – regime próprio e incentivos; HIS isenta de Solo Criado se atendidos padrões de resiliência (LC 1.022/2024 art. 5º, p/ protocolos até 31/12/2025).', fonte='ArcGIS REST SMAMUS – Hosted/Limite_Programa_4D_130326', oficial=True,
                                  fonte_id='F23', artigo_anexo='LC 960/2022', observacao='O regime específico do +4D não foi transcrito para esta plataforma (ver lacunas).', parametros_por_codigo=None, alerta_por_codigo=None, features=fe)
        add_geo('Programa +4D', 'geo_raw/limite_4d.geojson', GIS + 'Hosted/Limite_Programa_4D_130326/FeatureServer/0', len(l4['features']))

    # ----------------------------------------------------------------- blocos
    def I(chave, titulo, *a, **k):
        d = P(*a, **k); d = dict(chave=chave, titulo=titulo, **d); return d
    def IT(chave, titulo, texto, fonte, art, obs=None):
        return dict(chave=chave, titulo=titulo, **TXT(texto, None, fonte, art, obs))
    outorga = dict(resumo='Solo Criado (outorga onerosa do direito de construir) aplicável em toda a Área de Ocupação Intensiva, do IA básico até o IA máximo do Anexo 6, limitado ao estoque de cada UEU/quarteirão; valor pela LC 946/2022 com FP = 1,0 até lei ordinária específica.', fonte_id='F18', artigo_anexo='PDDUA arts. 53, 110–111; LC 946/2022', itens=[
        IT('aplicacao', 'Onde se aplica', 'Toda a Área de Ocupação Intensiva (art. 110), acima do IA básico até o IA máximo (Anexo 6). Na Área Rarefeita não se aplica.', 'F01', 'arts. 110–111 LC 434/99'),
        dict(chave='formula', titulo='Fórmula do valor do Solo Criado', **P(None, 'R$', 'F18', 'LC 946/2022 art. 5º', 'VMT = valor do m² de terreno da face de quarteirão (planta de valores); AC = área adensável adicional (m²); FP = fator de planejamento; IA = índice de aproveitamento da face.', forma='formula', formula='VSC = VMT * AC * FP / IA')),
        dict(chave='fator_planejamento', titulo='Fator de planejamento (FP)', **P(1.0, None, 'F18', 'LC 946/2022 art. 6º e §3º', 'FP pode variar de 0 a 1,3 por lei ordinária; enquanto não houver, FP = 1. O valor deve constar da DMI.', faixa=dict(min=0, max=1.3))),
        IT('modalidades', 'Modalidades de Solo Criado', 'Pequeno adensável ≤ 300 m²; médio adensável 300–1.000 m² (até 30% da área adensável, apenas em UEUs/quarteirões liberados); grande adensável > 1.000 m² até os limites do Anexo 6 (EVU – Dec. 19.741/2017); não adensável sem limite.', 'F01', 'art. 111 LC 434/99'),
        IT('procedimento', 'Procedimento', 'Decreto 21.585/2022 (procedimento); IN 006/2025 (preço em terreno com mais de uma subunidade). Exceções da LC 946 art. 13 para GA 01, 03 e 19.', 'F18', 'LC 946/2022 arts. 9–13', 'Decreto 21.585/2022 e IN 006/2025 citados na compilação do PDDUA; textos não baixados.'),
        IT('isencao_his_lc1022', 'Isenção de Solo Criado para HIS (LC 1.022/2024)', 'HIS (art. 22 PDDUA, Demhab e MCMV todas as faixas) na Área Intensiva: isenção de Solo Criado, dos limites de estoque da UEU/quarteirão e do regime volumétrico do Anexo 7 (observado o COMAER); áreas de garagem não computadas. VALE SÓ para projetos protocolados até 31/12/2025.', 'F13', 'LC 1.022/2024 arts. 1º §1º e 2º', 'Sem prorrogação localizada em 27/10/2026 → não se aplica a novos protocolos.'),
        IT('tpc', 'Transferência de Potencial Construtivo', 'TPC aplicável na Área Intensiva (art. 110); fator 3 para TPC originado em bairros atingidos pela enchente de 2024 (LC 1.022/2024 art. 6º).', 'F01', 'arts. 51–53 e 110 LC 434/99; LC 1.022/2024 art. 6º'),
        IT('futuro_luos', 'OODC na nova LUOS (a partir de 2027)', 'VC = (VMT × AC × FP) ÷ CA; FP de 0 a 1,5 (padrão 1,0); HIS nas faixas dos programas federais isenta de OODC; recursos 50% FMGT / 50% FMHIS.', 'F10', 'LC 1.076/2026 arts. 110–114', 'Ainda NÃO vigente em 27/10/2026 (art. 125: 180 dias após publicação; regras aplicadas após regulamentação em 2027).'),
    ])
    zeis = dict(resumo='AEIS I–IV (PDDUA art. 76) com regime por decreto; incentivos PMCMV-POA (LC 636/2010) vigentes; incentivos da LC 1.022/2024 restritos a protocolos até 31/12/2025.', fonte_id='F01', artigo_anexo='PDDUA arts. 22, 76; LC 636/2010; LC 1.022/2024', itens=[
        IT('definicao_his', 'Definição de HIS/DHP', 'Demanda Habitacional Prioritária (DHP) = famílias com renda até 6 salários mínimos (art. 22 §3º). LC 1.022/2024 considera HIS: art. 22 PDDUA + Demhab + MCMV em todas as faixas.', 'F01', 'art. 22 §3º LC 434/99; LC 1.022/2024 art. 1º §3º'),
        IT('tipos_aeis', 'Tipos de AEIS', 'AEIS I (assentamentos autoproduzidos), AEIS II (loteamentos irregulares), AEIS III (vazios urbanos na Área Intensiva para produção de HIS com interveniência do Poder Público), AEIS IV (áreas precárias). Regime urbanístico por decreto (§8º).', 'F01', 'art. 76 LC 434/99'),
        IT('pmcmv_faixas', 'Faixas do PMCMV-POA', 'Faixa I até 3 SM; Faixa II 3–6 SM; Faixa III 6–10 SM.', 'F15', 'LC 636/2010 art. 4º'),
        IT('pmcmv_incentivos', 'Incentivos PMCMV-POA', 'Isenções/reduções de IPTU e ITBI (art. 10); desmembramento > 5.000 m² com 18% de doação, dispensável/reduzível para faixas I e II em glebas ≤ 22.500 m² (arts. 11–12); loteamento pela LC 547/2006 (art. 14); compensação vegetal da faixa I assumida pelo Município (art. 17); padrões construtivos LC 547/548 (art. 19); empreendimentos incentivados tornam-se AEIS (art. 20); vagas reduzíveis a 50% das UH (art. 21); DHP na Área Intensiva dispensada da quota ideal (art. 28).', 'F15', 'LC 636/2010 arts. 10–28', 'Alterada pelas LC 699/2012 e 722/2013 (não lidas – ver lacunas).'),
        dict(chave='vagas_aeis', titulo='Vagas mínimas em AEIS (MCMV)', **P(0.5, 'vagas/UH', 'F15', 'LC 636/2010 art. 21')),
        IT('padroes_construtivos', 'Padrões construtivos HIS', 'Pé-direito mínimo 2,40 m (2,20 m em áreas de serviço/banheiro), dispensa de zeladoria e outras flexibilizações.', 'F16', 'LC 548/2006'),
        dict(chave='lote_minimo_his', titulo='Lote mínimo em loteamento de interesse social', **P(125, 'm2', 'F06', 'Anexo 8.1 nota (3)', 'Testada mínima 5 m; dispensa dos 2% para parque.')),
        IT('lc1022_loteamento', 'Doação em loteamentos HIS (LC 1.022/2024)', 'Faixa I/Demhab: isenção da doação do Anexo 8; Faixa II: 5%; Faixa III: 10% (protocolos até 31/12/2025).', 'F13', 'LC 1.022/2024 art. 3º'),
        IT('lc1022_rito', 'Rito HIS (LC 1.022/2024 + Dec. 22.932/2024)', 'Projeto Especial de 1º grau com comissão CEFH; Centro Histórico (LC 930/2021) e +4D (LC 960/2022) com isenção de Solo Criado se atendidos padrões de resiliência (art. 5º).', 'F14', 'LC 1.022/2024 arts. 4º–5º; Dec. 22.932/2024'),
        IT('rarefeita_his', 'HIS na Área Rarefeita', 'Empreendimento HIS na Área Rarefeita é Projeto Especial de 2º grau; no GA 27 adota-se o GA da Área Intensiva via Projeto Especial.', 'F08', 'Anexo 11.2; Anexo 5.5 nota (1)'),
    ])
    outros = dict(resumo='Projetos Especiais de Impacto Urbano (Anexo 11) funcionam como EIV; licenciamento ambiental municipal; restrições aeronáuticas, APP, patrimônio e risco nas camadas.', fonte_id='F08', artigo_anexo='PDDUA arts. 55–61 e Anexo 11', itens=[
        IT('projeto_especial_1g', 'Projeto Especial de 1º grau', 'Condomínio acima dos limites do Anexo 8.4 até 30 ha; edificação não residencial 10.000–30.000 m² ou 200–400 vagas; terreno > 2,25 ha na Área Intensiva; bens tombados/inventariados; loteamentos 2,25–30 ha.', 'F08', 'Anexo 11.1'),
        IT('projeto_especial_2g_eiv', 'Projeto Especial de 2º grau (EVU/EIV)', 'Grande porte (> 30.000 m² de área adensável ou > 400 vagas); condomínio/loteamento residencial na Mista 05; HIS na Área Rarefeita/potencial intensiva; loteamento > 30 ha; Urbanizador Social (Lei 9.162/2003). Exige Estudo de Viabilidade Urbanística e contrapartidas.', 'F08', 'Anexo 11.2'),
        dict(chave='condominio_area_maxima', titulo='Área máxima de condomínio/quarteirão (Área Intensiva residencial/mista)', **P(22500, 'm2', 'F06', 'Anexo 8.1 (área máxima de quarteirão) e 8.2', 'Acima exige Projeto Especial (Anexo 11).')),
        dict(chave='doacao_loteamento', titulo='Destinação pública em loteamento (Área Intensiva residencial/mista)', **P(0.2, 'fracao', 'F06', 'Anexo 8.1', '18% equipamentos comunitários/escola + 2% praça/parque, além da malha viária.')),
        IT('eia', 'EIA/RIMA e licenciamento ambiental', 'Licenciamento ambiental municipal (SMAMUS); EIA conforme Resolução CONAMA 01/1986 e legislação estadual para empreendimentos de grande impacto.', 'F01', 'PDDUA arts. 59–61 (referência)', 'Enquadramento detalhado não transcrito.'),
        IT('operacoes_urbanas', 'Operações urbanas / programas especiais', 'OUC Lomba do Pinheiro (LC 630/2009) revogada pela LC 950/2022; Programa +4D (LC 960/2022) e Reabilitação do Centro Histórico (LC 930/2021) com regime próprio.', 'F01', 'Compilação PDDUA, notas ao art. 29; LC 930/2021; LC 960/2022'),
        IT('aeroporto', 'Restrições aeronáuticas', 'PBZPA/PZPANA (Portarias DECEA 957/2015 e 260/2016) e PEZR (RBAC 161) – altura máxima do objeto na DMI.', 'F21', 'PDDUA art. 96 (notas)'),
    ])
    resumo_mcmv = [
        'Maior potencial: subunidades com IA 19 (básico 2,4 → 3,0 com Solo Criado), IA 15/17 (1,9 → 3,0) e IA 11/13 (1,6 → 3,0), volumetria 09/11/13 (42–52 m) e densidade 15–19 (455–525 hab/ha) – concentradas nas MZ1–MZ3 (Cidade Radiocêntrica, Corredor de Desenvolvimento, Cidade Xadrez); terra mais cara.',
        'Equilíbrio MCMV: GA 05/07/09 (Mistas 02–04, habitação S/R) com IA 05–09 (1,3 → 2,0/3,0) e volumetria 05/07/09 (18–42 m), comuns na Cidade Xadrez (MZ3), Restinga (MZ7) e Eixo Lomba-Restinga (MZ6). Residencial em terreno com testada ≥ 12 m é isento de vagas (Anexo 10.1).',
        'Evitar: GA 13 (produtiva) – habitação proibida; GA 11 (Mista 05) – só por Projeto Especial de 2º grau; Área Rarefeita (densidade 31–37: 2–17 hab/ha, recuo de jardim 12 m) e Zona Rural; APP, setores de risco CPRM e suscetibilidade alta a inundação (camadas).',
        'AEIS: incentivos do PMCMV-POA (LC 636/2010) – vagas até 50% das UH, dispensa de quota ideal na Área Intensiva (art. 28), IPTU/ITBI, redução de doação em desmembramento; lote HIS 125 m²/5 m. Regime da AEIS por decreto – confirmar na DMI.',
        'LC 1.022/2024 (isenção de Solo Criado, de estoque e de volumetria para HIS) valeu apenas para projetos protocolados até 31/12/2025 – não conte com ela para novos projetos.',
        'Solo Criado: VSC = VMT × AC × FP / IA, FP = 1 (LC 946/2022); custo cresce com o valor da face de quarteirão – em áreas periféricas o Solo Criado é barato.',
        'Gatilhos de custo/prazo: terreno > 2,25 ha na Área Intensiva ou condomínio > 22.500 m² → Projeto Especial 1º grau; > 30.000 m² adensáveis ou > 400 vagas → 2º grau (EVU); bens inventariados/entorno de tombados; PBZPA (altura) perto do Salgado Filho.',
        'Transição: PDUS (LC 1.075/2026) e LUOS (LC 1.076/2026) sancionados em 14/07/2026 com regras a partir de 2027 (ZOT 1–16; ZOT 14 admite regime da ZOT 1 para HIS; OODC com isenção para HIS em faixas federais). Projetos protocolados antes podem ter direito ao regime antigo – verificar as regras de transição.',
    ]
    lacunas = [
        dict(item='Códigos 99 (densidade), 99.99 (atividade), 999 (IA/volumetria), atividade 20 e 15.2', motivo='Não constam dos Anexos 4–7 nem do dicionário PDDUA_Metadados; aparecem em AEIS e áreas de regime próprio. Parâmetros null – consultar a DMI.'),
        dict(item='Significado dos códigos OBS_1..OBS_5 das subunidades', motivo='A tabela de observações não é publicada nos metadados; repassados como atributo obs_codigos.'),
        dict(item='CA mínimo', motivo='O PDDUA vigente não fixa CA mínimo por zona.'),
        dict(item='Vagas para residencial em terreno com testada < 12 m', motivo='O Anexo 10.1 (Dec. 20.385/2019) só trata testada ≥ 12 m (isento).'),
        dict(item='Regime volumétrico do Anexo 7.2 (logradouros com observações especiais)', motivo='Depende da via de frente do lote; não vetorizado (só tabela por logradouro).'),
        dict(item='Regimes próprios do Centro Histórico (LC 930/2021 – gabarito) e do +4D (LC 960/2022)', motivo='Leis específicas não transcritas; perímetro do +4D incluído como camada informativa.'),
        dict(item='Decretos de regime das AEIS (art. 76 §8º)', motivo='Não há compilação pública única; AEIS tratadas como alerta com herança do regime base.'),
        dict(item='Prorrogação da LC 1.022/2024', motivo='Nenhuma lei de prorrogação localizada no SAPL/DOPA até 27/10/2026.'),
        dict(item='LC 699/2012 e LC 722/2013 (alterações da LC 636/2010)', motivo='Não lidas; confirmar redação vigente dos artigos citados.'),
        dict(item='Zoneamento da nova LUOS (Anexo 1 – ZOT)', motivo='A camada pública Hosted/luos_anexo01_zot está vazia (0 feições) em 27/10/2026; a LUOS ainda não está vigente.'),
        dict(item='Áreas de Interesse Cultural (camada própria)', motivo='Serviço Hosted/Áreas_de_Interesse_Cultural retornou erro do servidor; as áreas estão representadas nos GA 15.x/16.x das zonas base e na camada de tombados/inventariados.'),
        dict(item='Cota de inundação 5,35 m (2024) e mancha da cheia de 2024', motivo='Camada Hosted/cota_535 não baixada (servidor instável); usar suscetibilidade CPRM como proxy.'),
        dict(item='Geometria da Macrozona 6 (Eixo Lomba-Restinga)', motivo='Nem a camada de macrozonas (MapServer/77) nem as subunidades do regime trazem MZ 6 em 27/10/2026 (há MZ 10 – Lomba do Pinheiro); MZ6 mantida só como descrição legal do art. 29.'),
        dict(item='Gabarito em número de pavimentos', motivo='O PDDUA controla altura em metros (Anexo 7.1), não em pavimentos.'),
        dict(item='Decreto 21.585/2022 e IN 006/2025 (procedimento do Solo Criado)', motivo='Citados na compilação; textos não baixados.'),
    ]
    geografico = dict(
        descricao='Zonas base = subunidades do PDDUA agrupadas pela combinação dos 4 códigos do regime urbanístico (densidade/atividade/IA/volumetria); AEIS como sobrepostas de alerta; restrições em camadas complementares. Todas as geometrias são vetores oficiais públicos (ArcGIS REST da SMAMUS e shapefiles da página Mapas Digitais).',
        crs='EPSG:4326', crs_area='EPSG:31982', servidor_oficial=GIS, camadas=geo_camadas,
        regras_de_consulta='1) Ache a subunidade (zona base) do terreno – se o lote cair em mais de uma, cada parte segue seu regime (a DMI informa por subunidade). 2) AEIS: alerta e incentivos MCMV, regime por decreto. 3) Restrições: PBZPA (altura), ruído, APP, patrimônio, risco/inundação, UC, Zona Rural. 4) Confirmar sempre na DMI (Declaração Municipal Informativa, Dec. 18.624/2014) – válida por 1 ano.',
        limitacoes=['Shapefiles da SMAMUS em TM-POA (SIRGAS 2000, MC -51°, k 0,999995, FE 300.000, FN 5.000.000), reprojetados com pyproj; erro < 1 m.',
                    'Simplificação ~1 m (zonas) e ~2 m (macrozonas/manchas unidas); coordenadas com 6 casas.',
                    'O arquivo "PDDUA_Shapefile.zip" da página Mapas Digitais contém, na verdade, o PBZPA (mesmo arquivo do Shapefile_PBZPA_PBZPH.zip); por isso o regime foi obtido do serviço ArcGIS Hosted/PDDUA.',
                    'Base AEIS de 12/05/2022 e PBZPA/APP de 2021; servidor ArcGIS instável (erros 500 transitórios).',
                    'Regime do Anexo 7.2 (por logradouro) não georreferenciado.'],
        raio_divisa_m=30, pct_minimo_significativo=0.5,
        notas_tecnicas={'gerador': 'scripts/build_poa.py', 'download': 'scripts/baixar_camadas.py (paginação por OBJECTID, outSR=4326, f=geojson)', 'shapefiles': 'Mapas Digitais SMAMUS, TM-POA reprojetado com pyproj'})
    macrozonas = [dict(codigo=f'MZ{c}', nome=mzn[c], descricao=None, parametros={}) for c in sorted(mzn)]
    for m in macrozonas:
        m['descricao'] = {1: 'Centro Histórico e extensão até a III Perimetral; miscigenação e proteção ao patrimônio.', 2: 'Entre BR-290, Av. Sertório e Av. Assis Brasil; empreendimentos de polarização metropolitana (Aeroporto, CEASA).',
                          3: 'Entre a Av. Sertório e a Cidade da Transição; preenchimento de vazios e corredores de centralidade.', 4: 'Entre a Cidade Radiocêntrica e a Cidade Jardim; densificação controlada.',
                          5: 'Baixa densidade, residencial predominantemente unifamiliar, orla do Guaíba.', 6: 'Ao longo das Estradas João de Oliveira Remião e João Antônio da Silveira; potencial para HIS.',
                          7: 'Bairro Restinga e Parque Industrial.', 8: 'Patrimônio natural, lazer/turismo, residencial e setor primário; núcleos intensivos de Belém Velho, Belém Novo, Lami etc.',
                          9: 'Ilhas do Delta do Jacuí (Decreto Estadual 28.436/79), exceto UEU 9032 (Ilha da Pintada).', 10: 'Lomba do Pinheiro.'}[int(m['codigo'][2:])]
        m['parametros'] = {'fundamento': TXT('PDDUA art. 29' if m['codigo'] != 'MZ10' else 'LC 630/2009 (criou a MZ10); OUC revogada pela LC 950/2022', None, 'F01', 'art. 29 LC 434/99')}
    doc = dict(
        schema_versao='1.1', municipio='Porto Alegre', uf='RS', slug='porto-alegre-rs', codigo_ibge='4314902', data_levantamento=HOJE,
        centro_mapa=dict(lat=-30.0346, lon=-51.2177, zoom=11),
        orgao_confirmacao='SMAMUS – Escritório de Licenciamento (DMI – Declaração Municipal Informativa)',
        marco_legal_vigente=('Vigente em 27/10/2026: PDDUA – LC 434/1999 e alterações (compilação 16/12/2025), com regime urbanístico por subunidade (Anexos 4 densidade, 5 atividades, 6 índices, 7 volumetria, 8 parcelamento, 10 vagas – Dec. 20.385/2019, 11 Projetos Especiais); '
                             'Solo Criado pela LC 946/2022; HIS: art. 22/76 do PDDUA, LC 636/2010 (PMCMV-POA), LC 547/2006 e 548/2006, LC 1.022/2024 (só protocolos até 31/12/2025) e Dec. 22.932/2024; Zona Rural LC 775/2015; Centro Histórico LC 930/2021; +4D LC 960/2022. '
                             'Revisão: PDUS (LC 1.075/2026) e LUOS (LC 1.076/2026) sancionados em 14/07/2026, vigência 180 dias após a publicação (art. 125 LUOS) e aplicação das novas regras a partir de 2027 após regulamentação – NÃO usados para os índices deste arquivo.'),
        fontes=[dict(id=a, titulo=b, lei=c, data=d, url=e, arquivo_local=(('fontes/' + f) if f else None)) for a, b, c, d, e, f in FONTES],
        macrozonas=macrozonas, macrozonas_observacao='Macrozonas são estruturais/descritivas; os índices vêm da subunidade (zona base).',
        zonas=zonas, camadas_complementares=cam, outorga_onerosa=outorga, zeis_his=zeis, outros_parametros=outros, resumo_mcmv=resumo_mcmv,
        geografico=geografico, lacunas=lacunas)
    json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('zonas', len(zonas), 'base', sum(1 for z in zonas if z['tipo'] == 'base'), 'MB', round(os.path.getsize(OUT) / 1e6, 2))

if __name__ == '__main__':
    main()
