#!/usr/bin/env python3
"""Monta fortaleza-ce.json (PADRAO_JSON.md v1.0) a partir das camadas oficiais do
Fortaleza em Mapas (geo_raw/) e dos parâmetros extraídos da LC 236/2017 (LPUOS) e da
LC 62/2009 (PDP) com alterações até LC 436/2025. Uso: python3 scripts/build_fortaleza.py
Parte 1: utilitários e fontes. Os parâmetros ficam em params_fortaleza.py."""
import json, glob, re, os, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, GeometryCollection
from shapely.validation import make_valid
from shapely.ops import unary_union, transform
from pyproj import Transformer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'geo_raw')
TO_UTM = Transformer.from_crs(4326, 31984, always_xy=True).transform
TO_GEO = Transformer.from_crs(31984, 4326, always_xy=True).transform
HOJE = '2026-10-27'
TOL = 1.5
MAPAS = 'https://mapas.fortaleza.ce.gov.br'
DL = {str(x['id']): x for x in json.load(open(os.path.join(RAW, '_log_download.json')))}

def raw(i):
    return json.load(open(glob.glob(os.path.join(RAW, f'{i}_*.geojson'))[0]))

def url(i):
    return f'{MAPAS}/api/download/geojson/{i}'

def round_coords(o):
    if isinstance(o, (list, tuple)):
        if o and isinstance(o[0], (int, float)):
            return [round(o[0], 6), round(o[1], 6)]
        return [round_coords(x) for x in o]
    return o

def _polys(g):
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    if isinstance(g, GeometryCollection):
        return unary_union([p for p in g.geoms if isinstance(p, (Polygon, MultiPolygon))])
    return None

def clean_geom(g, kind='poly'):
    g = make_valid(g)
    if kind == 'poly':
        g = _polys(g)
        if g is None or g.is_empty:
            return None
    u = transform(TO_UTM, g).simplify(TOL, preserve_topology=True)
    if kind == 'poly':
        u = _polys(make_valid(u))
        if u is None or u.is_empty or u.area < 1.0:
            return None
    m = mapping(transform(TO_GEO, u))
    m = {'type': m['type'], 'coordinates': round_coords(m['coordinates'])}
    if kind == 'poly':
        s = shape(m)
        if not s.is_valid:
            try:
                s = _polys(make_valid(s, method='structure'))
            except Exception:
                s = _polys(s.buffer(0))
            if s is None or s.is_empty:
                return None
            m = mapping(s)
            m = {'type': m['type'], 'coordinates': round_coords(m['coordinates'])}
            if not shape(m).is_valid:   # arredondamento recriou auto-interseção: tenta buffer(0) e, em último caso, 7 casas
                b = _polys(shape(m).buffer(0))
                mb = mapping(b); mb = {'type': mb['type'], 'coordinates': round_coords(mb['coordinates'])}
                if shape(mb).is_valid and not shape(mb).is_empty:
                    m = mb
                else:
                    m = mapping(s)
    return m

def feat(geom, props, kind='poly'):
    g = clean_geom(shape(geom) if isinstance(geom, dict) else geom, kind)
    if g is None:
        return None
    return {'type': 'Feature', 'properties': props, 'geometry': g}

def fc(features, fonte, oficial=True):
    return {'type': 'FeatureCollection', 'crs': 'EPSG:4326 (lon, lat)', 'fonte': fonte, 'oficial': oficial,
            'features': [f for f in features if f]}

def P(valor, fonte_id, art, obs=None, unidade=None, forma=None, **extra):
    """Parâmetro no formato do schema 1.1: {valor, unidade, fonte_id, artigo_anexo, observacao, forma, [...]}."""
    d = {'valor': valor, 'unidade': unidade, 'fonte_id': fonte_id, 'artigo_anexo': art, 'observacao': obs or None}
    if isinstance(valor, str):
        d['valor'] = None
        d['texto_original'] = valor
        forma = forma or 'texto'
    elif isinstance(valor, bool):
        raise ValueError(valor)
    elif isinstance(valor, (int, float)):
        forma = forma or 'unico'
    elif isinstance(valor, list):
        forma = forma or 'lista'
    else:
        forma = forma or ('condicional' if extra.get('condicionais') else 'sem_dado')
    d['forma'] = forma
    d.update(extra)
    return d

def C(condicao, valor=None, forma=None, codigo=None, obs=None):
    c = {'condicao': condicao, 'forma': forma or ('unico' if isinstance(valor, (int, float)) else 'lista' if isinstance(valor, list) else 'sem_dado'), 'valor': valor}
    if codigo:
        c['codigo'] = codigo
    if obs:
        c['observacao'] = obs
    return c

def strip_html(s):
    return ' '.join(re.sub(r'<[^>]+>', ' ', str(s or '')).split())

# ======================================================================= FONTES
SAPL = 'https://sapl.fortaleza.ce.leg.br/norma/'
SEUMA_REPO = 'https://portal.seuma.fortaleza.ce.gov.br/fortalezaonline/servletrepositoriolegislacao?pasta=legislacaoGeral&arquivo='
meta = {}
try:
    for n in json.load(open(os.path.join(BASE, 'fontes', '_normas_sapl.json'))):
        mm = re.search(r'nº\s*([\d\.]+)', n['norma'])
        if mm:
            meta.setdefault(mm.group(1).replace('.', ''), n)
except Exception:
    pass
def sapl(num):
    n = meta.get(str(num))
    return (SAPL + str(n['id'])) if n else SAPL

FONTES = [
 ('F01', 'Plano Diretor Participativo de Fortaleza (PDPFor)', 'Lei Complementar nº 62, de 02/02/2009 (DOM 13/03/2009) e alterações', '2009-02-02', SAPL + '107', 'PDF com camada de texto no repositório da SEUMA: ' + SEUMA_REPO + 'LEI_N_062.2009.pdf'),
 ('F02', 'Lei de Parcelamento, Uso e Ocupação do Solo (LPUOS)', 'Lei Complementar nº 236, de 11/08/2017 (DOM 11/08/2017, suplemento)', '2017-08-11', SAPL + '4999', 'PDF integral: https://sapl.fortaleza.ce.leg.br/media/sapl/public/normajuridica/2017/4999/4999_texto_integral.pdf'),
 ('F03', 'Altera o Anexo 4.3 (ZEDUS), o perímetro da ZEDUS Aldeota e outros dispositivos da LC 236/2017', 'Lei Complementar nº 287, de 2020', '2020', sapl(287), 'PDF escaneado lido por OCR (fontes/LC_287_2020.ocr.txt).'),
 ('F04', 'Altera o Anexo 4.1 e a Tabela 6.3 (ZIA Sabiaguaba) da LC 236/2017', 'Lei Complementar nº 436, de 2025 (DOM 23/09/2025)', '2025-09-23', SAPL + '14259', 'https://sapl.fortaleza.ce.leg.br/media/sapl/public/normajuridica/2025/14259/lc_436_plc_0036-25.pdf'),
 ('F05', 'Novo Plano Diretor Participativo e Sustentável (PDPS) – APROVADO, NÃO VIGENTE em 27/10/2026', 'Lei Complementar nº 450, de 2025 (DOM 27/11/2025)', '2025-11-27', SAPL + '14309', 'https://sapl.fortaleza.ce.leg.br/media/sapl/public/normajuridica/2025/14309/lc_450_plc_0049-25.pdf'),
 ('F06', 'Prorroga a entrada em vigor da LC 450/2025 para 18 meses após a publicação', 'Lei Complementar nº 461, de 2026', '2026', SAPL + '14434', 'https://sapl.fortaleza.ce.leg.br/media/sapl/public/normajuridica/2026/14434/461-2026_plc_0010-26.pdf'),
 ('F07', 'Incentivos fiscais aos empreendimentos do Programa Minha Casa, Minha Vida', 'Lei Complementar nº 359, de 27/06/2023 (DOM 27/06/2023)', '2023-06-27', sapl(359), 'PDF escaneado lido por OCR (fontes/LC_359_2023.ocr.txt).'),
 ('F08', 'Altera a LC 359/2023 (incentivos MCMV – Lei federal 14.620/2023)', 'Lei Complementar nº 434, de 2025 (DOM 22/08/2025)', '2025-08-22', SAPL + '14212', 'https://sapl.fortaleza.ce.leg.br/media/sapl/public/normajuridica/2025/14212/lc_434_plc_0040-25.pdf'),
 ('F09', 'Transferência do Direito de Construir (TDC)', 'Lei nº 10.333, de 2015', '2015', SEUMA_REPO + 'LEI_N_10333.2015.pdf', 'Cópia em fontes/N1_10333_2015.pdf. A LC 414/2024, que a alterava, foi revogada pela LC 424/2025.'),
 ('F10', 'Outorga Onerosa de Alteração de Uso (OOAU)', 'Lei nº 10.335, de 2015 e LC nº 333, de 2022', '2015', SEUMA_REPO + 'LEI_N_10335.2015.pdf', 'LC 333/2022: ' + sapl(333)),
 ('F11', 'Altera o art. 313 do PDP (Fração do Lote): não aplicação em ZOC/ZOP, áreas com esgoto, entorno de transporte e HIS MCMV', 'Lei Complementar nº 243, de 21/12/2017 (republicada no DOM 07/02/2018)', '2017-12-21', sapl(243), 'fontes/LC_243_2017.pdf'),
 ('F12', 'Mapa Indicador Urbano/Fração do Lote (altera o art. 313 do PDP)', 'Lei Complementar nº 101, de 30/12/2011', '2011-12-30', sapl(101), 'fontes/LC_101_2011.pdf'),
 ('F13', 'Fortaleza em Mapas – portal oficial de dados geográficos da Prefeitura de Fortaleza', 'Camadas oficiais baixadas pelo download público (GeoJSON)', HOJE, MAPAS, 'Download público sem login: ' + MAPAS + '/api/download/geojson/<id>; log em geo_raw/_log_download.json.'),
 ('F14', 'Altera a LC 62/2009 (ZEIS – arts. 132 e 138)', 'Lei Complementar nº 79, de 2010', '2010', sapl(79), 'fontes/LC_79_2010.ocr.txt'),
 ('F15', 'Altera a LC 62/2009 (art. 309 – ZEIS 3; art. 138)', 'Lei Complementar nº 229, de 2017', '2017', sapl(229), 'fontes/LC_229_2017.ocr.txt'),
 ('F16', 'Altera os arts. 244 e 247 do PDP (Operações Urbanas Consorciadas)', 'Lei Complementar nº 265, de 2019', '2019', sapl(265), 'fontes/LC_265_2019.ocr.txt'),
 ('F17', 'Ampliação da ZEDUS Aldeota e da ZEDUS Centro – Trecho 2 (Anexo 2, Mapa 5 da LC 236)', 'Lei Complementar nº 349, de 2023', '2023', sapl(349), 'fontes/LC_349_2023.ocr.txt'),
 ('F18', 'Alterações de zoneamento de 2019 (ZPA/ZRA/ZIA → zonas de ocupação; Tabelas 6.7 e 6.11; ZEDUS Centro T2)', 'LCs nº 262, 271, 277, 281, 282 e 285, de 2019', '2019', sapl(277), 'Textos em fontes/LC_262…285_2019.ocr.txt'),
 ('F19', 'Alterações de zoneamento de 2024 (Lagoa do Coité; Lagoa do Maricá; ZRU 2 Bom Jardim; ZEA Serrinha → ZRU 2; ZPA Faixa de Praia → Zona da Orla)', 'LCs nº 397, 410, 417 e 418, de 2024', '2024', SAPL + '14088', 'fontes/LC_397_2024.ocr.txt, LC_410_2024.pdf, LC_417_2024.ocr.txt, LC_418_2024.ocr.txt'),
 ('F20', 'Leis específicas de ZEIS 1 (normas especiais de parcelamento, uso e ocupação): Dionísio Torres (438), Moura Brasil (439), Pici (440), Serviluz (441), Lagamar (442), Praia do Futuro IIB (443), Mucuripe (444), Pirambu (445), Poço da Draga (446), Bom Jardim (447)', 'Leis Complementares nº 438 a 447, de 24/10/2025', '2025-10-24', SAPL + '14288', 'Ids SAPL: 438=14288, 439=14270, 440=14280, 441=14279, 442=14289, 443=14278, 444=14284, 445=14290, 446=14281, 447=14286.'),
 ('F21', 'Fundo de Desenvolvimento Urbano (FUNDURB)', 'Lei Complementar nº 211, de 2015', '2015', sapl(211), 'fontes/LC_211_2015.pdf'),
 ('F22', 'Acrescenta parágrafo ao art. 88 da LC 236/2017 (lotes de esquina)', 'Lei Complementar nº 378, de 2023', '2023', sapl(378), 'fontes/LC_378_2023.ocr.txt'),
]
fontes = []
for fid, tit, lei, data, u, obs in FONTES:
    d = {'id': fid, 'titulo': tit, 'lei': lei, 'data': data, 'url': u}
    if obs:
        d['observacao'] = obs
    fontes.append(d)

# ======================================================================= PARÂMETROS COMUNS
A42 = 'LC 236/2017, Anexo 4 – Tabela 4.2 (Macrozona de Ocupação Urbana), DOM 11/08/2017 supl., p. 57–58'
A41 = 'LC 236/2017, Anexo 4 – Tabela 4.1 (Macrozona de Proteção Ambiental), DOM 11/08/2017 supl., p. 57'
A43 = 'LC 236/2017, Anexo 4 – Tabela 4.3 (ZEDUS), com a redação da LC 287/2020 (Anexo Único)'
T51 = 'LC 236/2017, Anexo 5 – Tabela 5.1 (Subgrupo Residencial), p. 390 do PDF'
T81 = 'LC 236/2017, Anexo 8 – Tabela 8.1 (adequação ao sistema viário e recuos), p. 503 do PDF; art. 91'
FL_OBS = ('Nu = área do terreno ÷ fração (≥0,5 arredonda para cima – art. 102). Área de aplicação 1–5 conforme o Mapa Indicador Urbano/Fração do Lote (LC 101/2011; LC 236 Anexo 2, Mapas 2–2.16; ver camada fracao_do_lote). '
          'A fração NÃO se aplica: em ZOC, ZOP 1, ZOP 2 e áreas atendidas por esgotamento público; a até 300 m de metrô/VLT/terminais/corredores TRANSFOR com solução coletiva de esgoto; '
          'e a HIS multifamiliar MCMV com solução coletiva de esgoto operada pela CAGECE (PDP art. 313 §§3º–5º, LC 243/2017 – F11). HIS MCMV até 6 SM: fração 30 m²/UH em qualquer zona adequada (LC 236 art. 101 p.ú.).')

def recuos_res():
    obs = ('Residência multifamiliar (classe 2) e conjunto HIS de prédios (classes 9/10PE), até 4 pavimentos. Acima de 4 pavimentos, +0,25 m por pavimento a partir do 5º em todos os recuos (art. 91 §1º); '
           'distância entre blocos ≥ 2× recuo lateral; subsolo com recuo frontal mínimo 5 m (art. 88). Unifamiliar/conjunto de casas (classes 1, 3, 4PE): 4/2/3 m; conjunto HIS de casas (7/8PE): 3/2/3 m. Normas 1 e 14 do Anexo 8.2.')
    return {'frontal': P(5.0, 'F02', T81, obs, 'm'), 'lateral': P(3.0, 'F02', T81, None, 'm'), 'fundos': P(3.0, 'F02', T81, None, 'm')}

VAGAS_TXT = ('Residência multifamiliar (00.00.04): 1 vaga/unidade; multifamiliar de unidades compactas (00.00.10): 1 vaga/6 unidades; conjunto HIS de prédios (00.00.09): 1 vaga/unidade; '
             'conjunto HIS de casas (00.00.07): 1 vaga/6 UH (até 300 UH) ou 1/3 UH (>300 UH); HIS de reassentamento (00.00.08): opcional')
def vagas_res():
    return P(None, 'F02', T51, 'Mínimo de vagas para veículos (Anexo 5). Frações 1/6 e 1/3 expressas em vagas por UH.', 'vagas/UH', 'condicional', texto_original=VAGAS_TXT,
             condicionais=[C('residência multifamiliar (00.00.04)', 1), C('multifamiliar de unidades compactas (00.00.10)', 0.1667, obs='1 vaga a cada 6 unidades'),
                           C('conjunto HIS de prédios (00.00.09)', 1), C('conjunto HIS de casas (00.00.07) até 300 UH', 0.1667, obs='1 vaga a cada 6 UH'),
                           C('conjunto HIS de casas (00.00.07) acima de 300 UH', 0.3333, obs='1 vaga a cada 3 UH'),
                           C('HIS de reassentamento (00.00.08)', None, 'nao_aplicavel', obs='vagas opcionais')])

def fracao(fl, art=A42):
    if not fl:
        return P(None, 'F02', art, 'Sem Fração do Lote na tabela (–).', 'm2/UH', 'nao_aplicavel')
    txt = '; '.join(f'área de aplicação {k}: {v} m²/UH' for k, v in sorted(fl.items()))
    conds = [C(f'área de aplicação {k} (Mapa Indicador de Fração do Lote)', v) for k, v in sorted(fl.items())]
    conds.append(C('HIS multifamiliar MCMV/similar até 6 SM (LC 236 art. 101 p.ú.)', 30))
    conds.append(C('HIS MCMV com esgoto coletivo CAGECE; ZOC/ZOP; até 300 m de metrô/VLT/terminais (PDP art. 313 §§3º–5º)', None, 'nao_aplicavel'))
    return P(None, 'F02', art + ' (coluna Fração do Lote por área de aplicação 1–5); arts. 100–102', FL_OBS, 'm2/UH', 'condicional', texto_original=txt, condicionais=conds)

def base_params(tp, to, tosub, iab, iamin, iamax, fp, alt, test, prof, area, fl, usos, art=A42, fonte='F02', ia_obs=None):
    o = {}
    if fp is not None:
        o['fator_planejamento_oodc'] = P(fp, 'F01', 'PDP art. 220 e LC 236 Anexo 4 (coluna Fp)', 'Fp da fórmula da OODC; ajustável a cada 2 anos (art. 220 §1º).')
    o['taxa_ocupacao_subsolo'] = P(tosub, fonte, art, None, '%') if tosub is not None else P(None, fonte, art, 'Não se aplica (–) na tabela.', 'fracao', 'nao_aplicavel')
    o['profundidade_minima_lote_m'] = P(prof, fonte, art, None, 'm')
    o['fracao_do_lote'] = fracao(fl, art)
    if o['fracao_do_lote']:
        o['fracao_do_lote']['fonte_id'] = fonte
    ca_max_obs = None
    if isinstance(iamax, (int, float)) and isinstance(iab, (int, float)) and iamax > iab:
        ca_max_obs = 'Acima do IA básico até o máximo mediante OODC (PDP arts. 218–220) ou TDC (Lei 10.333/2015).'
    return {
        'ca_minimo': P(iamin, fonte, art),
        'ca_basico': P(iab, fonte, art, ia_obs),
        'ca_maximo': P(iamax, fonte, art, ca_max_obs),
        'taxa_ocupacao': P(to, fonte, art, 'TO do solo; a de subsolo está em outros.taxa_ocupacao_subsolo.', '%'),
        'gabarito_altura_max_m': P(alt, fonte, art + '; medição conforme art. 98', None, 'm'),
        'gabarito_pavimentos': None,
        'taxa_permeabilidade': P(tp, fonte, art + ('; art. 87' if art == A42 else ''), 'Pode ser reduzida até 20% com drenos/recarga (art. 87).' if art == A42 else None, '%'),
        'recuos': recuos_res(),
        'lote_minimo_m2': P(area, fonte, art, 'Lote mínimo de parcelamento; conjuntos HIS: 125 m² e testada 5 m (art. 208).', 'm²'),
        'testada_minima_m': P(test, fonte, art, None, 'm'),
        'usos_permitidos': usos,
        'vagas': vagas_res(),
        'densidade': P(None, 'F02', 'LC 236 arts. 79 VII e 100–102; PDP art. 313', 'Sem densidade em hab/ha: controlada pela Fração do Lote (m² de terreno por unidade) – ver outros.fracao_do_lote.', None, 'nao_aplicavel'),
        'outros': o,
    }

USO_VIA = P(['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10'], 'F02', T81 + '; ' + T51 + '; art. 82',
            'Classes residenciais 1–10 (R2 = residência multifamiliar; R9/R10 = conjunto HIS de prédios) adequadas em todas as classes de via (Tabela 8.1). Conjuntos >300 UH são Projeto Especial (4PE/6PE com EIV; 8PE/10PE HIS), com análise SEUMA/CPPD (art. 75 e arts. 170–176).',
            texto_original='Residencial multifamiliar (classe 2) e conjuntos HIS (classes 7, 9 e 10PE) adequados em todas as classes de via.')
_USO_VIA_OLD = P('Residencial multifamiliar (classe 2) e conjuntos HIS (classes 7, 9 e 10PE) ADEQUADOS em todas as classes de via (expressa, arterial I/II, coletora, comercial, local). '
            'Conjuntos >300 UH são Projeto Especial (4PE/6PE com EIV; 8PE/10PE HIS), com análise SEUMA/CPPD (art. 75 e arts. 170–176).', 'F02', T81 + '; ' + T51 + '; art. 82')
def uso_tab(tab, txt, fonte='F02'):
    return P(txt, fonte, f'LC 236/2017, Anexo 6 – {tab} (linha R, classes 1–10)', 'A = adequado; P(n) = adequado com restrição (nota n da tabela); I = inadequado. Classe 2 = residência multifamiliar; 9 = conjunto HIS de prédios.')

# ======================================================================= ZONAS BASE (camada 604)
U64 = lambda: uso_tab('Tabela 6.4', 'R1 A; R2 (multifamiliar) P(1); R3 A; R4 A; R5 P(1); R6 I; R7 A; R8 A; R9 (HIS prédios) P(1); R10 I')
UA = lambda t: uso_tab(t, 'Todas as classes residenciais (1–10) A')
# código, nomes na camada 604, nome, descrição, (TP, TO, TOsub, IAb, IAmin, IAmax, Fp, Alt, testada, prof, área, fração, usos)
ZBASE = [
 ('ZOP1', ['Zona de Ocupação Preferencial 1'], 'Zona de Ocupação Preferencial 1', 'PDP arts. 79–81: infraestrutura consolidada; intensificação da ocupação.', (30, 60, 60, 3.0, 0.25, 3.0, None, 72, 5, 25, 125, {1: 30, 2: 45}, USO_VIA)),
 ('ZOP2', ['Zona de Ocupação Preferencial 2'], 'Zona de Ocupação Preferencial 2', 'PDP arts. 82–84.', (30, 60, 60, 2.0, 0.20, 3.0, 0.5, 72, 5, 25, 125, {1: 30}, USO_VIA)),
 ('ZOC', ['Zona de Ocupação Consolidada'], 'Zona de Ocupação Consolidada', 'PDP arts. 85–88.', (30, 60, 60, 2.5, 0.20, 2.5, None, 72, 5, 25, 125, {1: 30}, USO_VIA)),
 ('ZRU1', ['Zona de Requalificação Urbana 1'], 'Zona de Requalificação Urbana 1', 'PDP arts. 89–92.', (30, 60, 60, 2.0, 0.20, 2.0, None, 48, 5, 25, 125, {2: 45, 3: 60, 5: 100}, USO_VIA)),
 ('ZRU2', ['Zona de Requalificação Urbana 2'], 'Zona de Requalificação Urbana 2', 'PDP arts. 93–96.', (30, 60, 60, 1.5, 0.10, 1.5, None, 48, 5, 25, 125, {2: 45, 3: 60, 4: 75, 5: 100}, USO_VIA)),
 ('ZOM1', ['Zona de Ocupação Moderada 1'], 'Zona de Ocupação Moderada 1', 'PDP arts. 97–100.', (40, 50, 50, 2.0, 0.10, 2.5, 0.75, 72, 6, 25, 150, {2: 45, 4: 75}, USO_VIA)),
 ('ZOM2', ['Zona de Ocupação Moderada 2'], 'Zona de Ocupação Moderada 2', 'PDP arts. 101–104.', (40, 50, 50, 1.0, 0.10, 1.5, 0.75, 48, 6, 25, 150, {2: 45, 4: 75, 5: 100}, USO_VIA)),
 ('ZOM2-SZ1', ['Zona de Ocupação Moderada 2 - Subzona 1'], 'Zona de Ocupação Moderada 2 – Subzona 1', 'PDP art. 105 (LC 277/2019; LC 397/2024).', (40, 50, 50, 2.0, 0.10, 2.0, None, 72, 6, 25, 150, {2: 45}, USO_VIA)),
 ('ZOR', ['Zona de Ocupação Restrita'], 'Zona de Ocupação Restrita', 'PDP arts. 106–109: baixa densidade.', (40, 45, 45, 1.0, 0.0, 1.0, None, 15, 6, 25, 150, {5: 100}, USO_VIA)),
 ('ZO-I', ['Zona de Orla - Trecho I'], 'Zona da Orla – Trecho I (Barra do Ceará/Pirambu)', 'PDP arts. 110–123; LC 236 arts. 125–134.', (30, 50, 50, 1.0, 0.25, 1.0, None, 15, 5, 25, 125, {5: 100}, U64())),
 ('ZO-II', ['Zona de Orla - Trecho II'], 'Zona da Orla – Trecho II (Jacarecanga/Moura Brasil)', 'PDP arts. 110–123.', (20, 50, 50, 1.5, 0.25, 1.5, None, 24, 5, 25, 125, None, U64())),
 ('ZO-III-SZ1', ['Zona de Orla - Trecho III'], 'Zona da Orla – Trecho III – Subzona 1 (Monsenhor Tabosa)', 'PDP arts. 110–123.', (25, 60, 60, 2.0, 0.25, 2.0, None, 48, 5, 25, 125, {1: 30}, UA('Tabela 6.5'))),
 ('ZO-III-SZ2-S1', ['Zona de Orla - Trecho III - Subzona 2 Setor 1'], 'Zona da Orla – Trecho III – Subzona 2 – Setor 1 (Praia de Iracema – interesse urbanístico)', 'PDP arts. 110–123.', (20, 60, 60, 1.0, 0.25, 2.0, None, 48, 5, 25, 125, {2: 45}, UA('Tabela 6.6'))),
 ('ZO-III-SZ2-S2', ['Zona de Orla - Trecho III - Subzona 2 Setor 2'], 'Zona da Orla – Trecho III – Subzona 2 – Setor 2 (Praia de Iracema)', 'LC 236 arts. 127–129; Tabela 6.7 alterada pela LC 271/2019.', (10, 80, None, 1.0, 0.25, 1.0, None, 10.5, 5, 25, 125, None, uso_tab('Tabela 6.7', 'R1 A; R2–R10 I (multifamiliar inadequado)'))),
 ('ZO-IV', ['Zona de Orla - Trecho IV'], 'Zona da Orla – Trecho IV (Meireles/Mucuripe)', 'PDP arts. 110–123; LC 236 art. 130.', (20, 60, 60, 3.0, 0.25, 3.0, 1.5, 72, 5, 25, 125, {1: 30}, UA('Tabela 6.8'))),
 ('ZO-V', ['Zona de Orla - Trecho V'], 'Zona da Orla – Trecho V (Iate Clube)', 'LC 236 art. 131: somente atividades listadas (pesca, alimentação, clube, gelo).', (20, 60, 60, 1.0, 0.25, 1.0, None, 15, 5, 25, 125, None, P([], 'F02', 'LC 236/2017, art. 131', 'Lista taxativa (pesca, alimentação, clube, gelo): nenhuma classe residencial é adequada.'))),
 ('ZO-VI', ['Zona de Orla - Trecho VI'], 'Zona da Orla – Trecho VI (Cais do Porto – Área Industrial)', 'LC 236 arts. 132–133.', (30, 60, 60, 1.0, 0.10, 1.0, None, 48, 12, 25, 300, None, uso_tab('Tabela 6.9', 'Todas as classes residenciais (1–10) I'))),
 ('ZO-VII', ['Zona de Orla - Trecho VII'], 'Zona da Orla – Trecho VII (Praia do Futuro)', 'LC 236 arts. 130 e 134.', (40, 50, 50, 2.0, 0.10, 2.0, 1.5, 36, 8, 25, 200, {4: 75}, UA('Tabela 6.10'))),
]
zonas = []
d604 = raw(604)
by_nome = {}
for f in d604['features']:
    by_nome.setdefault(f['properties']['nome'].strip(), []).append(f)
F604 = f'Fortaleza em Mapas (SEUMA) – camada 604 "Macrozoneamento Urbano de Fortaleza" (ano_ref 2022), {url(604)}, baixada em {HOJE}'
used = set()
for cod, nomes, nome, desc, t in ZBASE:
    tp, to, tosub, iab, iamin, iamax, fp, alt, test, prof, area, fl, usos = t
    feats = []
    for n in nomes:
        for f in by_nome.get(n, []):
            used.add(n)
            feats.append(feat(f['geometry'], {'codigo': cod, 'nome': n, 'fracao_lote_camada': f['properties'].get('fracao_lote')}))
    p = base_params(tp, to, tosub, iab, iamin, iamax, fp, alt, test, prof, area, fl, usos)
    obs = None
    if cod in ('ZO-IV', 'ZO-VII'):
        p['outros']['acrescimo_ia_hospedagem'] = P(1.0, 'F02', 'LC 236/2017, art. 130', 'IA máximo +1,0 somente para hospedagem, mediante OODC.')
    if cod == 'ZO-VII':
        obs = 'Art. 134: R-1/R-3/R-4 e uso misto podem encostar nas divisas laterais no térreo e, no pavimento superior, numa extensão de 7 m (laje até 7 m); norma 1 do Anexo 8 não se aplica.'
    if cod == 'ZOP1':
        obs = 'Fração do Lote não se aplica em ZOP1 (PDP art. 313 §3º, LC 243/2017) – atributo fracao_lote = 0 na camada oficial.'
    if cod in ('ZOP2', 'ZOC'):
        obs = 'Fração do Lote não se aplica em ZOP2/ZOC (PDP art. 313 §3º, LC 243/2017) – atributo fracao_lote = 0 na camada oficial.'
    zonas.append({'codigo': cod, 'nome': nome, 'descricao': desc + ' Macrozona de Ocupação Urbana (PDP art. 76 e ss.).', 'tipo': 'base', 'prioridade': 0,
                  'regra_sobreposicao': None, 'parametros': p, 'observacoes': obs, 'geometria': fc(feats, F604)})
assert not (set(by_nome) - used), set(by_nome) - used

# ======================================================================= ZONAS BASE ambientais (76/77/78)
ZIA = {
 'Zona de Interesse Ambiental da Sabiaguaba': ('ZIA-SABIAGUABA', 'Zona de Interesse Ambiental (ZIA) Sabiaguaba', 'PDP art. 72; parâmetros e usos redefinidos pela LC 436/2025.',
     (40, 50, None, 1.0, 0.0, 1.0, None, 15, 12, 25, 300, None,
      P('Somente nas quadras lindeiras à Av. Manoel Mavignier: R1 A, R2 (multifamiliar) P(2), R3 A; demais classes e demais áreas da ZIA Sabiaguaba: inadequado', 'F04', 'LC 436/2025 – nova Tabela 6.3 do Anexo 6 da LC 236/2017')),
     'F04', 'LC 436/2025 – nova Tabela 4.1 do Anexo 4 da LC 236/2017 (ZIA 1 Sabiaguaba)',
     'IA básico/máximo 1,50 somente nas quadras lindeiras à Av. Manoel Mavignier (a partir de UTM E 563.326,170 / N 9.578.807,140); demais áreas 1,00.',
     'Atributos de índices da camada 76 anteriores à LC 436/2025; valores seguem a lei.'),
 'Zona de Interesse Ambiental da Praia do Futuro': ('ZIA-PRAIA-DO-FUTURO', 'Zona de Interesse Ambiental (ZIA) Praia do Futuro', 'PDP art. 72; LC 236 Anexo 4.1 (ZIA 2).',
     (40, 50, 40, 2.0, 0.0, 2.0, None, 48, 12, 25, 300, {5: 100},
      uso_tab('Tabela 6.2', 'R1 A; R2 (multifamiliar) P(1); R3 A; R4 I; R5 P(1); R6–R10 I (conjuntos HIS inadequados)')),
     'F02', A41, 'IA 1,00 para unifamiliar e 2,00 para multifamiliar (Anexo 4.1).', None),
 'Zona de Interesse Ambiental do Cocó': ('ZIA-COCO', 'Zona de Interesse Ambiental (ZIA) Cocó', 'PDP art. 72; LC 236 Anexo 4.1 (ZIA 3).',
     (40, 40, 40, 1.5, 0.0, 1.5, None, 48, 12, 25, 300, {5: 100},
      P(None, 'F02', 'LC 236/2017, Anexo 6', 'Tabela própria de adequação de usos da ZIA Cocó não localizada – confirmar na SEUMA.')),
     'F02', A41, None, None),
}
for f in raw(76)['features']:
    n = f['properties']['nome_zona'].strip()
    cod, nome, desc, t, fonte, art, iaobs, obs = ZIA[n]
    tp, to, tosub, iab, iamin, iamax, fp, alt, test, prof, area, fl, usos = t
    p = base_params(tp, to, tosub, iab, iamin, iamax, fp, alt, test, prof, area, fl, usos, art=art, fonte=fonte, ia_obs=iaobs)
    zonas.append({'codigo': cod, 'nome': nome, 'descricao': desc + ' Macrozona de Proteção Ambiental.', 'tipo': 'base', 'prioridade': 0, 'regra_sobreposicao': None,
                  'parametros': p, 'observacoes': obs,
                  'geometria': fc([feat(f['geometry'], {'codigo': cod, 'nome': n})], f'Fortaleza em Mapas – camada 76 "ZIA" (ano_ref 2022), {url(76)}, baixada em {HOJE}')})

p = base_params(50, 33, 33, 0.6, 0.0, 0.6, None, 15, 12, 25, 300, None, uso_tab('Tabela 6.1', 'R1 A; R2–R10 I (multifamiliar e HIS inadequados)'), art=A41)
zonas.append({'codigo': 'ZRA', 'nome': 'Zona de Recuperação Ambiental', 'descricao': 'PDP arts. 68–71. Macrozona de Proteção Ambiental.', 'tipo': 'base', 'prioridade': 0, 'regra_sobreposicao': None,
              'parametros': p, 'observacoes': 'Camada 78 (2022) pode não refletir LCs 397/2024 (Lagoa do Coité) e 285/2019.',
              'geometria': fc([feat(f['geometry'], {'codigo': 'ZRA', 'nome': 'ZRA'}) for f in raw(78)['features']], f'Fortaleza em Mapas – camada 78 "ZRA" (ano_ref 2022), {url(78)}, baixada em {HOJE}')})

d77 = raw(77)
for sig in ['ZPA 1', 'ZPA 2', 'ZPA 3', 'ZPA 4']:
    cod = sig.replace(' ', '')
    fs = [f for f in d77['features'] if f['properties'].get('sigla_zona') == sig]
    if not fs:
        continue
    nm = fs[0]['properties'].get('nome_zona') or sig
    zero = lambda v, u=None: P(v, 'F02', A41 + '; arts. 103–104', None, u)
    p = {'ca_minimo': zero(0), 'ca_basico': zero(0), 'ca_maximo': zero(0), 'taxa_ocupacao': zero(0, '%'), 'gabarito_altura_max_m': zero(0, 'm'), 'gabarito_pavimentos': None,
         'taxa_permeabilidade': zero(100, '%'), 'recuos': None, 'lote_minimo_m2': None, 'testada_minima_m': None,
         'usos_permitidos': P([], 'F02', 'LC 236/2017, arts. 103–104; PDP arts. 63–67', 'Nenhum uso edificado – non aedificandi; não se admite parcelamento nem edificação.'),
         'vagas': None, 'densidade': zero(0, 'uh/ha'),
         'outros': {'tdc': P('Pode haver TDC de imóveis em zonas de proteção conforme PDP arts. 225–226 e Lei 10.333/2015 (verificar caso a caso)', 'F09', 'PDP arts. 224–230; Lei 10.333/2015')}}
    zonas.append({'codigo': cod, 'nome': f'{sig} – {nm}', 'descricao': 'Zona de Preservação Ambiental (PDP arts. 63–67): non aedificandi; as restrições da ZPA prevalecem sobre qualquer outra disposição (LC 236 art. 104).',
                  'tipo': 'base', 'prioridade': 0, 'regra_sobreposicao': None, 'parametros': p,
                  'observacoes': 'Camada 77 (ano_ref 2020) pode não refletir as LCs 397/2024, 410/2024 e 418/2024.',
                  'geometria': fc([feat(f['geometry'], {'codigo': cod, 'nome': nm}) for f in fs], f'Fortaleza em Mapas – camada 77 "ZPA" (ano_ref 2020), {url(77)}, baixada em {HOJE}')})

# ======================================================================= SOBREPOSTAS
import unicodedata
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Z0-9]+', '-', s.upper()).strip('-')

def nulls():
    d = {k: None for k in ['ca_minimo', 'ca_basico', 'ca_maximo', 'taxa_ocupacao', 'gabarito_altura_max_m', 'gabarito_pavimentos', 'taxa_permeabilidade',
                           'recuos', 'lote_minimo_m2', 'testada_minima_m', 'usos_permitidos', 'vagas', 'densidade']}
    d['outros'] = {}
    return d

def regra(efeito, fund, alerta, prio_lim=50, mantem=None):
    r = {'efeito': efeito, 'usa_indices_de': None, 'aplica_sobre': None, 'limiar_pct': prio_lim, 'requer_testada': False, 'distancia_max_m': None, 'fundamento': fund, 'alerta': alerta}
    if mantem:
        r['mantem_da_base'] = mantem
    return r

# ZEDUS: (TP, TOsolo, TOsub, IAmin, IAmax, Alt, testada, prof, área, fração, tabela, usos)
ZED = {
 'CENTRO - TRECHO 1': (30, 60, 60, 0.20, 4.0, 95, 5, 25, 125, None, '6.11', 'A'),
 'CENTRO - TRECHO 2': (30, 60, 60, 0.20, 4.0, 95, 5, 25, 125, None, '6.11', 'A'),
 'ALDEOTA': (30, 60, 60, 0.20, 4.0, 95, 5, 25, 125, 30, '6.12', 'A'),
 'PARANGABA': (30, 60, 60, 0.20, 2.0, 48, 5, 25, 125, 60, '6.13', 'A'),
 'PORANGABUÇU': (30, 60, 60, 0.25, 3.0, 72, 5, 25, 125, 45, '6.14', 'A'),
 'MESSEJANA': (40, 60, 60, 0.20, 3.0, 72, 5, 25, 125, 45, '6.15', 'A'),
 'MONTESE': (30, 60, 60, 0.20, 3.0, 72, 6, 25, 150, 45, '6.16', 'A'),
 'VILA UNIÃO': (30, 60, 60, 0.25, 3.0, 72, 5, 25, 125, 60, '6.17', 'R1 A; R2 (multifamiliar) A; R3 A(1); R4 A(1); R5 A; R6 A; R7–R10 (HIS) P(1)'),
 'SEIS BOCAS': (40, 60, 60, 0.20, 3.0, 48, 5, 25, 125, 30, '6.18', 'A'),
 'VARJOTA': (30, 60, 60, 0.10, 4.0, 95, 5, 25, 150, 30, '6.19', 'A'),
 'OLIVEIRA PAIVA': (40, 60, 60, 0.20, 2.0, 48, 5, 25, 125, 100, '6.20', 'A'),
 'FRANCISCO SÁ': (30, 50, 50, 0.10, 2.0, 48, 6, 25, 150, 60, None, None),
 'BR 116 - TRECHO 1': (30, 60, 60, 0.20, 2.0, 48, 5, 25, 125, 60, '6.21', 'R1–R10 P(8)'),
 'BR 116 - TRECHO 2': (30, 60, 60, 0.20, 2.0, 48, 5, 25, 125, 60, '6.22', 'R1–R10 P(3)'),
 'BR 116 - TRECHO 3': (40, 50, 50, 0.10, 1.5, 48, 6, 25, 150, 45, '6.23', 'A'),
 'BR 116 - TRECHO 4': (40, 45, 45, 0.0, 1.0, 15, 6, 25, 150, None, '6.24', 'A'),
 'ANTÔNIO BEZERRA': (30, 60, 60, 0.20, 2.0, 48, 5, 25, 125, 45, '6.25', 'A'),
 'PERIMETRAL SUL': (30, 60, 60, 0.10, 1.5, 48, 5, 25, 125, 75, '6.26', 'A'),
 'PERIMETRAL OESTE': (30, 60, 60, 0.10, 1.5, 48, 5, 25, 125, 45, '6.27', 'A'),
 'CARLITO PAMPLONA': (45, 30, 60, 0.25, 3.0, 72, 5, 25, 125, 45, '6.28', 'A'),
 'BONSUCESSO': (30, 60, 60, 0.10, 1.5, 48, 5, 25, 125, 100, '6.29', 'A'),
 'ANEL VIARIO - TRECHO 1': (40, 45, 45, 0.0, 1.0, 15, 6, 25, 150, None, '6.30', 'A'),
 'ANEL VIARIO - TRECHO 2': (40, 45, 45, 0.0, 1.0, 15, 6, 25, 150, None, '6.30', 'A'),
}
seen = set()
for f in raw(28)['features']:
    nm = re.sub(r'\s*/\s*', ' - ', f['properties']['Name'].replace('ZEDUS - ', '').strip())
    tp, to, tosub, iamin, iamax, alt, test, prof, area, fl, tab, uso = ZED[nm]
    seen.add(nm)
    cod = 'ZEDUS-' + slug(nm)
    art = A43 + (' (Varjota: IA máx 4,00 e altura 95 m pela LC 287/2020)' if nm == 'VARJOTA' else '')
    usos = (uso_tab('Tabela ' + tab, 'Todas as classes residenciais (1–10) A' if uso == 'A' else uso) if tab else
            P(None, 'F02', 'LC 236/2017, Anexo 6', 'Tabela específica não localizada; adequação a confirmar na SEUMA.'))
    p = base_params(tp, to, tosub, None, iamin, iamax, None, alt, test, prof, area, None, usos, art=art)
    p['ca_basico'] = P(None, 'F02', A43 + ', observação 1', 'IA básico = o da zona de base subjacente (Anexo 4.3, obs. 1).', 'coeficiente', 'herda_da_base')
    p['ca_maximo']['observacao'] = 'Acima do IA básico da zona subjacente até este máximo mediante OODC (PDP arts. 218–220) ou TDC.'
    p['outros']['fracao_do_lote'] = (P(fl, 'F02', A43 + ' (coluna Fração do Lote)', FL_OBS, 'm2/UH') if fl else
                                     P(None, 'F02', A43 + ' (coluna Fração do Lote)', 'Sem Fração do Lote (–).', 'm2/UH', 'nao_aplicavel'))
    p['outros']['recuos_variaveis'] = P('Nas ZEDUS admite-se avanço sobre os recuos (recuos variáveis) nos termos do art. 92', 'F02', 'LC 236/2017, art. 92')
    zonas.append({'codigo': cod, 'nome': 'ZEDUS ' + nm.title(), 'descricao': 'Zona Especial de Dinamização Urbanística e Socioeconômica (PDP arts. 145–147; LC 236 art. 220). ' + strip_html(f['properties'].get('descricao'))[:300],
                  'tipo': 'sobreposta', 'prioridade': 20,
                  'regra_sobreposicao': regra('substitui', 'LC 236/2017 Anexo 4.3 (obs. 1: IA básico da zona subjacente) e art. 135',
                                              f'Terreno na ZEDUS {nm.title()}: valem os parâmetros do Anexo 4.3 (IA máx {iamax}, altura {alt} m); o IA BÁSICO continua sendo o da zona de base.', 50, ['ca_basico']),
                  'parametros': p,
                  'observacoes': 'Perímetros: LC 236 Anexo 2 Mapa 5, alterados pelas LC 282/2019, LC 287/2020 e LC 349/2023. A camada 28 (ano_ref 2022) pode não incluir a ampliação da LC 349/2023.',
                  'geometria': fc([feat(f['geometry'], {'codigo': cod, 'nome': f['properties']['Name']})], f'Fortaleza em Mapas – camada 28 "ZEDUS" (ano_ref 2022), {url(28)}, baixada em {HOJE}')})
assert seen == set(ZED), set(ZED) - seen

ZEIS_LEIS = ('ZEIS 1 com lei específica (LCs 438–447 de 24/10/2025 – F20): Dionísio Torres, Moura Brasil, Pici, Serviluz, Lagamar, Praia do Futuro IIB, Mucuripe, Pirambu, Poço da Draga e Bom Jardim '
             '(ex.: Serviluz e Mucuripe: IA 3, TO 80%, TP 10%, 3 pavimentos, lote mínimo de regularização 30 m²; Pirambu: IA básico 2,0 e máximo 2,0; Dionísio Torres: IA 1,8 e TO 80%).')
d37 = raw(37)
ZE = [
 ('ZEIS-1', 'ZEIS 1', 'ZEIS 1 – Zona Especial de Interesse Social de Ocupação', 10,
  'PDP arts. 126–128 e 132: assentamentos irregulares de baixa renda (até 3 SM) – regularização fundiária e urbanística; vedado remembramento resultando em lote >150 m² para unifamiliar (art. 132 §2º, LC 79/2010). ' + ZEIS_LEIS,
  'Terreno em ZEIS 1: parâmetros dependem do plano de regularização/lei específica (LCs 438–447/2025 para 10 ZEIS); empreendimento de mercado sujeito a restrições – confirmar na SEUMA/HABITAFOR.', 'PDP arts. 125–132 e 138; LCs 438–447/2025'),
 ('ZEIS-2', 'ZEIS 2', 'ZEIS 2 – Zona Especial de Interesse Social de Conjuntos', 10,
  'PDP arts. 129–132: loteamentos clandestinos/irregulares e conjuntos habitacionais públicos ocupados por baixa renda – regularização.',
  'Terreno em ZEIS 2: destinada à regularização de conjuntos/loteamentos de baixa renda; parâmetros por plano específico – confirmar na SEUMA/HABITAFOR.', 'PDP arts. 125 e 129–132'),
 ('ZEIS-3', 'ZEIS 3', 'ZEIS 3 – Zona Especial de Interesse Social de Vazios', 10,
  'PDP arts. 133–137 e 309 (LC 229/2017): vazios destinados prioritariamente a HIS; Plano de Intervenção; parâmetros de EHIS por lei específica (art. 137); HIS em vazio de ZEIS 3 permite transferir todo o potencial (art. 133 §2º); cedente de TDC (art. 225).',
  'Terreno em ZEIS 3 (vazio destinado a HIS): oportunidade para MCMV/HIS – aplicam-se os parâmetros da zona de base até lei específica de EHIS (PDP art. 137); verificar Plano de Intervenção na SEUMA/HABITAFOR.', 'PDP arts. 133–137 e 309 (LC 229/2017)'),
 ('ZEA', 'ZEA', 'ZEA – Zona Especial Ambiental (Serrinha, Cambeba, Siqueira, Curió)', 15,
  'PDP arts. 148–150; LC 236 art. 220. ZEA Serrinha com limites alterados pela LC 418/2024 (áreas excluídas → ZRU 2).',
  'Terreno em Zona Especial Ambiental (ZEA): restrições ambientais/parâmetros especiais – consultar a SEUMA. Camada (2018) pode não refletir a LC 418/2024.', 'PDP arts. 148–150; LC 236 art. 220; LC 418/2024'),
 ('ZEPO', 'ZEPO', 'ZEPO – Zona Especial do Projeto Orla', 15,
  'PDP arts. 155–157: área do Plano de Gestão Integrada da Orla.',
  'Terreno na Zona Especial do Projeto Orla: verificar diretrizes do Plano de Gestão Integrada da Orla e terrenos de marinha (SPU).', 'PDP arts. 155–157'),
]
for cod, sig, nome, prio, desc, alerta, art in ZE:
    feats = [feat(f['geometry'], {'codigo': cod, 'nome': f['properties'].get('nome_geo') or sig}) for f in d37['features'] if f['properties'].get('sigla_zona') == sig]
    p = nulls()
    if cod == 'ZEIS-3':
        p['outros']['tdc_cedente'] = P('Imóvel em ZEIS 3 pode ceder potencial (TDC); HIS em vazio de ZEIS 3 → transferência de todo o potencial', 'F01', 'PDP arts. 133 §2º e 225; Lei 10.333/2015')
        p['outros']['isencao_oodc_ehis'] = P('EHIS isentos da contrapartida de OODC', 'F01', 'PDP art. 220 §2º')
    zonas.append({'codigo': cod, 'nome': nome, 'descricao': desc, 'tipo': 'sobreposta', 'prioridade': prio,
                  'regra_sobreposicao': regra('apenas_alerta', art, alerta), 'parametros': p,
                  'observacoes': 'Geometria da camada 37 "Zonas Especiais" (anoref 2018); para ZEIS há também a camada 623 (mesmos perímetros, 2018).',
                  'geometria': fc(feats, f'Fortaleza em Mapas – camada 37 "Zonas Especiais" (anoref 2018), {url(37)}, baixada em {HOJE}')})

p = nulls(); p['outros']['tdc_cedente'] = P('Imóveis em ZEPH podem transferir potencial construtivo', 'F01', 'PDP art. 225; Lei 10.333/2015')
zonas.append({'codigo': 'ZEPH', 'nome': 'ZEPH – Zona Especial de Preservação do Patrimônio Paisagístico, Histórico, Cultural e Arqueológico', 'descricao': 'PDP arts. 151–154 (Centro, Jacarecanga, Praia de Iracema, Parangaba).',
              'tipo': 'sobreposta', 'prioridade': 15,
              'regra_sobreposicao': regra('apenas_alerta', 'PDP arts. 151–154; LC 236 art. 135', 'Terreno em ZEPH: intervenções dependem de análise de patrimônio (SECULTFOR/COMPHIC); possíveis restrições de altura e volumetria.'),
              'parametros': p, 'observacoes': None,
              'geometria': fc([feat(f['geometry'], {'codigo': 'ZEPH', 'nome': f['properties']['nome']}) for f in raw(79)['features']], f'Fortaleza em Mapas – camada 79 "ZEPH" (ano_ref 2022), {url(79)}, baixada em {HOJE}')})
zonas.append({'codigo': 'ZEI', 'nome': 'ZEI – Zona Especial Institucional', 'descricao': 'PDP arts. 158–161: áreas de instituições (campi, quartéis, aeroporto etc.).', 'tipo': 'sobreposta', 'prioridade': 15,
              'regra_sobreposicao': regra('apenas_alerta', 'PDP arts. 158–161', 'Terreno em Zona Especial Institucional: uso institucional; mudança de uso depende de análise/lei específica.'),
              'parametros': nulls(), 'observacoes': None,
              'geometria': fc([feat(f['geometry'], {'codigo': 'ZEI', 'nome': f['properties']['nome']}) for f in raw(25)['features']], f'Fortaleza em Mapas – camada 25 "ZEI" (ano_ref 2022), {url(25)}, baixada em {HOJE}')})
zonas.append({'codigo': 'OUC', 'nome': 'Operações Urbanas Consorciadas', 'descricao': 'PDP arts. 242–248 (arts. 244/247 com redação da LC 265/2019): cada OUC tem lei específica.', 'tipo': 'sobreposta', 'prioridade': 25,
              'regra_sobreposicao': regra('apenas_alerta', 'PDP arts. 242–248; lei específica da OUC (propriedade "legislacao")', 'Terreno em Operação Urbana Consorciada: índices e contrapartidas da lei específica (ver nome/legislação da feição).'),
              'parametros': nulls(), 'observacoes': 'Textos das leis das OUC não baixados (lacuna).',
              'geometria': fc([feat(f['geometry'], {'codigo': 'OUC', 'nome': f['properties']['nome'], 'legislacao': f['properties'].get('legislacao'), 'publicacao': f['properties'].get('obs')}) for f in raw(29)['features']], f'Fortaleza em Mapas – camada 29 "OUC" (ano_ref 2022), {url(29)}, baixada em {HOJE}')})
AEA_USO = {'AEA 1': ('Tabela 6.31', 'Todas as classes residenciais (1–10) I'), 'AEA 2': ('Tabela 6.32', 'R1 P(1); R2–R6 P(2); R7–R10 I (HIS inadequado)'),
           'AEA 3': ('Tabela 6.33', 'R1 P(1); R2–R6 P(2); R7–R10 I (HIS inadequado)'), 'AEA 4': (None, None)}
d24 = raw(24)
for sig in ['AEA 1', 'AEA 2', 'AEA 3', 'AEA 4']:
    cod = sig.replace(' ', '')
    feats = [feat(f['geometry'], {'codigo': cod, 'nome': sig}) for f in d24['features'] if f['properties']['sigla_zona'] == sig]
    if not feats:
        continue
    tab, u = AEA_USO[sig]
    p = nulls()
    p['usos_permitidos'] = uso_tab(tab, u) if tab else P(None, 'F02', 'LC 236/2017, Anexo 6', 'Tabela da AEA 4 não localizada no texto – confirmar na SEUMA.')
    zonas.append({'codigo': cod, 'nome': f'Área Especial Aeroportuária – {sig}', 'descricao': 'Áreas Especiais Aeroportuárias (ruído do Aeroporto Pinto Martins) – adequação de usos nas Tabelas 6.31–6.33 da LC 236/2017.',
                  'tipo': 'sobreposta', 'prioridade': 30,
                  'regra_sobreposicao': regra('apenas_alerta', f'LC 236/2017, Anexo 6 – {tab or "AEA"}', f'Terreno em {sig} (ruído aeroportuário): adequação residencial: {u or "a confirmar na SEUMA"}. Onde adequado, valem os índices da zona de base.', 0),
                  'parametros': p, 'observacoes': None,
                  'geometria': fc(feats, f'Fortaleza em Mapas – camada 24 "AEA" (ano_ref 2019), {url(24)}, baixada em {HOJE}')})

# ======================================================================= CAMADAS COMPLEMENTARES
cam = {}
fl_feats = []
for f in d604['features']:
    v = int(float(f['properties'].get('fracao_lote') or 0))
    if v > 0:
        x = feat(f['geometry'], {'codigo': f'FL{v}', 'zona': f['properties']['nome']})
        if x:
            fl_feats.append(x)
cam['fracao_do_lote'] = {
    'papel': 'macrozona',
    'descricao': 'Fração do Lote (m² de terreno por unidade residencial multifamiliar) conforme o atributo "fracao_lote" da camada oficial 604. Polígonos com valor 0 (ZOP1, ZOP2, ZOC e zonas sem fração) foram omitidos.',
    'fonte': f'Fortaleza em Mapas – camada 604, atributo fracao_lote, {url(604)}', 'oficial': True, 'fonte_id': 'F13',
    'artigo_anexo': 'PDP art. 313 (LC 101/2011 e LC 243/2017); LC 236 arts. 100–102 e Anexo 4',
    'observacao': 'O Mapa Indicador de Fração (áreas de aplicação 1–5) não está publicado como camada; o atributo é uniforme por polígono.',
    'parametros_por_codigo': {c: {'fracao_lote_m2_por_uh': P(int(c[2:]), 'F02', 'LC 236/2017, Anexo 4 (coluna Fração do Lote); arts. 100–102', FL_OBS, 'm²/UH')}
                              for c in sorted({x['properties']['codigo'] for x in fl_feats}, key=lambda s: int(s[2:]))},
    'features': fl_feats}

def simple_layer(ids, codfn, papel, desc, fonte, alerta, art=None, kind='poly', namefn=None):
    feats = []
    for i in ids:
        for f in raw(i)['features']:
            c = codfn(f['properties'], i)
            if c is None or not f.get('geometry'):
                continue
            pr = {'codigo': c}
            if namefn:
                pr['nome'] = namefn(f['properties'])
            x = feat(f['geometry'], pr, kind)
            if x:
                feats.append(x)
    d = {'papel': papel, 'descricao': desc, 'fonte': fonte, 'oficial': True, 'parametros_por_codigo': None, 'fonte_id': 'F13'}
    if art:
        d['artigo_anexo'] = art
    if alerta:
        d['alerta_por_codigo'] = alerta
    d['features'] = feats
    return d

cam['bens_tombados'] = simple_layer([535, 588, 589], lambda p, i: {535: 'TOMBADO-MUNICIPAL', 588: 'TOMBADO-ESTADUAL', 589: 'TOMBADO-FEDERAL'}[i], 'restricao',
    'Bens tombados (municipais, estaduais e federais): intervenção depende de autorização do órgão de patrimônio.',
    f'Fortaleza em Mapas – camadas 535, 588 e 589 (SECULTFOR): {url(535)} | {url(588)} | {url(589)}',
    {'TOMBADO-MUNICIPAL': 'Bem tombado pelo Município (SECULTFOR/COMPHIC): intervenção depende de autorização.', 'TOMBADO-ESTADUAL': 'Bem tombado pelo Estado do Ceará (SECULT-CE): intervenção depende de autorização.', 'TOMBADO-FEDERAL': 'Bem tombado pelo IPHAN: intervenção depende de autorização federal.'},
    art='PDP arts. 151–154 (patrimônio)', namefn=lambda p: p.get('nome'))
cam['entorno_bens_tombados'] = simple_layer([536], lambda p, i: 'ENTORNO-TOMBAMENTO', 'restricao', 'Poligonais de entorno de bens tombados.',
    f'Fortaleza em Mapas – camada 536 (SECULTFOR): {url(536)}', {'ENTORNO-TOMBAMENTO': 'Terreno em poligonal de entorno de bem tombado: projeto sujeito a análise de patrimônio (altura/volumetria).'}, namefn=lambda p: p.get('nome_bem'))
def risco(p, i):
    t = str(p.get('tipo_risco') or '').strip().lower()
    return 'ASSENT-PRECARIO' if t in ('', 'none', 'sem risco') else 'ASSENT-RISCO'
cam['assentamentos_precarios_risco'] = simple_layer([124], risco, 'restricao', 'Assentamentos precários do PLHIS-For/Fortaleza 2040, com classificação de risco.',
    f'Fortaleza em Mapas – camada 124 (PLHIS-For/Fortaleza 2040): {url(124)}',
    {'ASSENT-RISCO': 'Terreno em assentamento precário com risco identificado (PLHIS-For): verificar Defesa Civil/HABITAFOR.', 'ASSENT-PRECARIO': 'Terreno em assentamento precário (PLHIS-For): provável ocupação existente/regularização fundiária.'},
    namefn=lambda p: f"{p.get('nome_assen')} ({p.get('tipo_risco')})")
cam['mangues'] = simple_layer([111], lambda p, i: 'MANGUE', 'restricao', 'Manguezais (APP – Lei federal 12.651/2012, art. 4º VII).', f'Fortaleza em Mapas – camada 111 (SEFIN 2016): {url(111)}',
    {'MANGUE': 'Manguezal: Área de Preservação Permanente (Código Florestal, art. 4º VII) – não edificável.'})
cam['alagados'] = simple_layer([669], lambda p, i: 'ALAGADO', 'restricao', 'Áreas alagadas/alagáveis (SEFIN 2016).', f'Fortaleza em Mapas – camada 669 (SEFIN 2016): {url(669)}',
    {'ALAGADO': 'Área alagada/alagável mapeada: verificar drenagem, APP e restrição ao parcelamento (Lei 6.766/1979, art. 3º p.ú.).'})
cam['unidades_conservacao'] = simple_layer([737, 85, 109], lambda p, i: {737: 'UC', 85: 'PARQUE-COCO', 109: 'ZA-PARQUE-COCO'}[i], 'restricao',
    'Unidades de Conservação, Parque Estadual do Cocó e sua Zona de Amortecimento.', f'Fortaleza em Mapas – camadas 737, 85 e 109: {url(737)} | {url(85)} | {url(109)}',
    {'UC': 'Terreno em Unidade de Conservação: ver ato de criação/plano de manejo e órgão gestor (APA admite ocupação com restrições).', 'PARQUE-COCO': 'Parque Estadual do Cocó (proteção integral): não edificável.', 'ZA-PARQUE-COCO': 'Zona de Amortecimento do Parque do Cocó: empreendimentos sujeitos a manifestação do órgão gestor (SEMA-CE).'},
    namefn=lambda p: p.get('Nome') or p.get('nome'))

aer_feats, aer_alert = [], {}
for i, aer in [(683, 'PINTO-MARTINS'), (682, 'FEIJO'), (685, 'DIAS-BRANCO')]:
    k = 0
    for f in raw(i)['features']:
        g = f['geometry']; c = g['coordinates']
        if g['type'] != 'LineString' or c[0] != c[-1] or len(c) < 4:
            continue
        txt = strip_html(f['properties'].get('Descrição') or f['properties'].get('description') or f['properties'].get('descricao'))
        if 'Horizontal Interna' in txt: t = 'HORIZONTAL-INTERNA'
        elif 'Horizontal Externa' in txt: t = 'HORIZONTAL-EXTERNA'
        elif 'Cônica' in txt: t = 'CONICA'
        elif 'Faixa de Pista' in txt: t = 'FAIXA-PISTA'
        elif 'Comprimento' in txt: t = 'PISTA'
        elif 'OFZ' in txt: t = 'OFZ'
        elif 'Horizontalda Aproxima' in txt or 'Horizontal da Aproxima' in txt: t = 'APROXIMACAO-HORIZONTAL'
        elif 'Abertura' in txt: t = 'DECOLAGEM'
        elif 'Elevação Borda' in txt: t = 'APROXIMACAO'
        else: t = 'OUTRA'
        k += 1
        cod = f'AER-{aer}-{t}-{k}'
        x = feat(Polygon(c), {'codigo': cod, 'nome': f"{(f['properties'].get('Name') or t.replace('-', ' ').title())} – {aer.replace('-', ' ').title()}"})
        if x:
            aer_feats.append(x)
            det = 'faixa de pista' if t == 'FAIXA-PISTA' else txt[:300]
            aer_alert[cod] = (f'Plano de Zona de Proteção do Aeródromo {aer.replace("-", " ").title()} – superfície {t.replace("-", " ").lower()}: {det}. '
                              'A edificação (cota do terreno + altura) não pode ultrapassar a superfície limitadora; consultar DECEA/COMAER (AGA) e SEUMA.')
cam['zona_protecao_aerodromos'] = {'papel': 'restricao',
    'descricao': 'Superfícies limitadoras de obstáculos dos Planos de Zona de Proteção dos aeródromos Pinto Martins, Feijó e Dias Branco (anéis fechados oficiais convertidos em polígonos; superfícies de transição e SPVV, publicadas como linhas abertas, não foram poligonizadas).',
    'fonte': f'Fortaleza em Mapas – camadas 683, 682 e 685: {url(683)} | {url(682)} | {url(685)}', 'oficial': True, 'fonte_id': 'F13',
    'artigo_anexo': 'Planos de Zona de Proteção de Aeródromos (COMAER/DECEA); LC 236/2017 – Áreas Especiais Aeroportuárias',
    'observacao': 'Polígono = interior do anel oficial (apenas simplificação ≤1,5 m). Altitudes copiadas da descrição oficial de cada feição.',
    'parametros_por_codigo': None, 'alerta_por_codigo': aer_alert, 'features': aer_feats}

cam['linha_preamar_1831'] = simple_layer([88], lambda p, i: 'LPM-1831', 'informativa', 'Linha de Preamar Médio de 1831 – referência para terrenos de marinha (33 m – DL 9.760/1946; SPU).',
    f'Fortaleza em Mapas – camada 88: {url(88)}', None, kind='line', namefn=lambda p: p.get('nome'))
cam['oodc_concedidas'] = simple_layer([609], lambda p, i: 'OODC', 'informativa', 'Outorgas onerosas do direito de construir concedidas (registro SEUMA).',
    f'Fortaleza em Mapas – camada 609: {url(609)}', None, kind='point', namefn=lambda p: str(p.get('Nome') or p.get('nome') or '')[:120])
k619 = 'poly' if raw(619)['features'][0]['geometry']['type'].endswith('Polygon') else 'point'
cam['cepacs'] = simple_layer([619], lambda p, i: 'CEPAC', 'informativa', 'Certificados de potencial adicional/TDC registrados (SEUMA).',
    f'Fortaleza em Mapas – camada 619: {url(619)}', None, kind=k619, namefn=lambda p: str(p.get('Nome') or '')[:120])
cam['zeis_prioritarias_plhis'] = simple_layer([102], lambda p, i: 'ZEIS-PRIORITARIA', 'informativa', 'ZEIS 1 prioritárias (PLHIS-For 2012) – 10 receberam lei específica em 2025 (LCs 438–447).',
    f'Fortaleza em Mapas – camada 102: {url(102)}', None, namefn=lambda p: p.get('nome'))

# ======================================================================= DOCUMENTO
geo_camadas = []
def gc(nome, i, metodo='download GeoJSON oficial (download público do portal)', erro=None, campo=None):
    l = DL.get(str(i), {})
    geo_camadas.append({'nome': nome, 'arquivo': f'geo_raw/{i}_{l.get("nome", "")}.geojson', 'campo': campo, 'fonte_url': url(i),
                        'data_download': l.get('baixado_em') or HOJE, 'oficial': True, 'metodo': metodo, 'erro_estimado_m': erro})
gc('Zonas base da Macrozona de Ocupação Urbana (ZOP, ZOC, ZRU, ZOM, ZOR, ZO) + fração do lote', 604, campo='nome; fracao_lote')
gc('ZIA', 76, campo='nome_zona'); gc('ZPA', 77, campo='sigla_zona'); gc('ZRA', 78)
gc('ZEDUS', 28, campo='Name'); gc('Zonas Especiais (ZEIS 1/2/3, ZEA, ZEPO)', 37, campo='sigla_zona'); gc('ZEPH', 79, campo='nome'); gc('ZEI', 25, campo='nome')
gc('OUC', 29, campo='nome; legislacao'); gc('AEA', 24, campo='sigla_zona')
for i, n in [(535, 'Bens tombados municipais'), (588, 'Bens tombados estaduais'), (589, 'Bens tombados federais'), (536, 'Entorno de bens tombados'), (124, 'Assentamentos precários/risco'),
             (111, 'Mangues'), (669, 'Alagados'), (737, 'Unidades de conservação'), (85, 'Parque Estadual do Cocó'), (109, 'Zona de amortecimento do Parque do Cocó'),
             (88, 'Linha de preamar 1831'), (609, 'OODC concedidas'), (619, 'CEPACs'), (102, 'ZEIS prioritárias')]:
    gc(n, i)
for i, n in [(683, 'Zona de proteção – Aeródromo Pinto Martins'), (682, 'Zona de proteção – Aeródromo Feijó'), (685, 'Zona de proteção – Aeródromo Dias Branco')]:
    gc(n, i, metodo='download GeoJSON oficial; anéis fechados (LineString) convertidos em polígonos', erro=2)

doc = {
 'schema_versao': '1.0', 'municipio': 'Fortaleza', 'uf': 'CE', 'slug': 'fortaleza-ce', 'codigo_ibge': '2304400', 'data_levantamento': HOJE,
 'centro_mapa': {'lat': -3.76, 'lon': -38.53, 'zoom': 12},
 'orgao_confirmacao': 'SEUMA – Secretaria Municipal do Urbanismo e Meio Ambiente de Fortaleza (Consulta de Adequabilidade Locacional – LC 236 art. 82; Fortaleza Online)',
 'marco_legal_vigente': ('Em 27/10/2026 vigoram o Plano Diretor Participativo – LC 62/2009 (F01) e a LPUOS – LC 236/2017 (F02), com alterações até a LC 436/2025 (F04). '
    'O novo Plano Diretor Participativo e Sustentável – LC 450/2025 (DOM 27/11/2025, F05) foi aprovado, mas a LC 461/2026 (F06) adiou sua vigência para 18 meses após a publicação (≈ maio/2027): NÃO está em vigor na data do levantamento. '
    'Parâmetros por zona: LC 236 Anexo 4 (Tabelas 4.1–4.3); usos: Anexos 5, 6 e 8; Fração do Lote: PDP art. 313 (LC 101/2011 e LC 243/2017). '
    'Instrumentos: OODC (PDP arts. 218–223); TDC (arts. 224–230 + Lei 10.333/2015); OOAU (Lei 10.335/2015 + LC 333/2022); OUC (arts. 242–248); EIV (arts. 291–294). Incentivos MCMV: LC 359/2023 alterada pela LC 434/2025.'),
 'fontes': fontes,
 'macrozonas': [
    {'codigo': 'MPA', 'nome': 'Macrozona de Proteção Ambiental', 'zonas': ['ZPA1', 'ZPA2', 'ZPA3', 'ZPA4', 'ZRA', 'ZIA-SABIAGUABA', 'ZIA-PRAIA-DO-FUTURO', 'ZIA-COCO'], 'fonte_id': 'F01', 'artigo_anexo': 'PDP arts. 59–75'},
    {'codigo': 'MOU', 'nome': 'Macrozona de Ocupação Urbana', 'zonas': [z[0] for z in ZBASE], 'fonte_id': 'F01', 'artigo_anexo': 'PDP arts. 76–123'}],
 'macrozonas_observacao': 'As macrozonas não têm camada própria: são a união das zonas base (camada 604 = MOU; camadas 76/77/78 = MPA). As camadas base praticamente não se sobrepõem (interseções < 0,3 km²) e cobrem ≈99,9% do município.',
 'zonas': zonas,
 'camadas_complementares': cam,
 'outorga_onerosa': {
    'base_legal': P('Outorga Onerosa do Direito de Construir (OODC) – PDP arts. 218–223', 'F01', 'PDP (LC 62/2009), arts. 218–223'),
    'aplicacao': P('Construir acima do IA básico até o IA máximo da zona (Anexo 4); nas ZEDUS, do IA básico da zona subjacente até o IA máximo da ZEDUS. Onde IA básico = máximo (ZOP1, ZOC, ZRU1, ZRU2, ZOR, zonas da Orla, ZIA, ZRA) não há OODC (salvo +1,0 para hospedagem em ZO-IV/VII – art. 130).', 'F01', 'PDP art. 218; LC 236 Anexo 4 e art. 130'),
    'formula': {'valor': 'Contrapartida = ((IApre − IAb) / IAb) × Fp × VVp × AT', 'variaveis': {'IApre': 'IA pretendido', 'IAb': 'IA básico da zona', 'Fp': 'fator de planejamento (ZOP2 0,5; ZOM1 0,75; ZOM2 0,75; ZO Trecho IV 1,5; ZO Trecho VII 1,5); varia de 0 a 1,5 e pode ser revisto a cada 2 anos (§1º)', 'VVp': 'valor venal do m² do terreno', 'AT': 'área do terreno (m²)'}, 'fonte_id': 'F01', 'artigo_anexo': 'PDP art. 220, caput e §1º'},
    'isencao_his': P('Empreendimentos Habitacionais de Interesse Social (EHIS) isentos da contrapartida', 'F01', 'PDP art. 220 §2º'),
    'pagamento_alternativo': P('Contrapartida substituível por imóveis ou obras em ZEIS', 'F01', 'PDP art. 221'),
    'destino_recursos': P('FUNDURB – Fundo de Desenvolvimento Urbano', 'F21', 'PDP art. 223; LC 211/2015'),
    'ooau': P('Outorga Onerosa de Alteração de Uso – Lei 10.335/2015 e LC 333/2022', 'F10', 'PDP art. 222; Lei 10.335/2015; LC 333/2022'),
    'tdc': P('TDC: cedentes = imóveis tombados/ZEPH, ZEIS 3, áreas ambientais (excepcional) e doação para o sistema viário; receptores = zonas com IA máximo > IA básico; regulamentação pela Lei 10.333/2015 (LC 414/2024 revogada pela LC 424/2025)', 'F09', 'PDP arts. 224–230; Lei 10.333/2015')},
 'zeis_his': {
    'categorias': P('ZEIS 1 (ocupação), ZEIS 2 (conjuntos), ZEIS 3 (vazios para HIS); novas ZEIS por lei', 'F01', 'PDP art. 125'),
    'zeis_1_leis_especificas_2025': P(ZEIS_LEIS, 'F20', 'LCs 438–447/2025'),
    'zeis_3_vazios': P('Vazios para HIS com Plano de Intervenção; parâmetros de EHIS em lei específica; HIS em ZEIS 3 permite transferir todo o potencial; ZEIS 3 é cedente de TDC', 'F01', 'PDP arts. 133–137, 225 e 309 (LC 229/2017)'),
    'fracao_lote_his_mcmv': P('HIS multifamiliar MCMV ou similar, até 6 SM: Fração do Lote = 30 m²/UH em qualquer zona adequada', 'F02', 'LC 236/2017, art. 101, parágrafo único'),
    'fracao_lote_nao_aplicavel_his': P('Em qualquer zona onde HIS multifamiliar MCMV seja adequada, a Fração do Lote não se aplica se houver solução coletiva de esgoto operada pela CAGECE', 'F11', 'PDP art. 313 §5º (LC 243/2017)'),
    'conjuntos_his': P('Conjuntos Habitacionais de Interesse Social: aprovação conjunta de parcelamento e edificação, AOP; classes 7–10 (Tabela 5.1); parâmetros da zona com lote mínimo 125 m² e testada 5 m; vagas conforme Anexo 5', 'F02', 'LC 236/2017, arts. 204–211'),
    'vagas_his': P('Conjunto HIS de casas: 1 vaga/6 UH (até 300 UH) ou 1/3 UH (>300); reassentamento: opcional; conjunto HIS de prédios: 1 vaga/UH; unidades compactas: 1 vaga/6 unidades', 'F02', T51),
    'recuos_his': P('Conjunto HIS de casas (7/8PE): 3/2/3 m; conjunto HIS de prédios (9/10PE): 5/3/3 m (+0,25 m por pavimento acima do 4º)', 'F02', T81),
    'isencao_oodc': P('EHIS isentos da contrapartida da OODC', 'F01', 'PDP art. 220 §2º'),
    'incentivos_fiscais_mcmv': P('LC 359/2023 (alterada pela LC 434/2025): isenção de ITBI (PJ na compra de terreno com recursos do Programa; PF beneficiária na aquisição de lote/unidade); IPTU isento por 5 exercícios para a PF beneficiária sem outro imóvel em Fortaleza; ISSQN isento na construção civil (subitem 7.02) de empreendimentos financiados pelo Programa; isenção total das taxas de licença de obra, habite-se, parcelamento e averbação. Fruição mediante requerimento na SEFIN e contrato com recursos do Programa (FAR, FDS, FNHIS etc.). A LC 434/2025 adequou a lei à Lei federal 14.620/2023.', 'F07', 'LC 359/2023, arts. 2º a 7º; LC 434/2025 (F08)')},
 'outros_parametros': {
    'eiv': P('EIV exigido para Projetos Especiais/PGV indicados no Anexo 5 (ex.: conjunto habitacional de casas ou de prédios >300 UH – classes 4PE-EIV e 6PE-EIV); conteúdo, TR, medidas mitigadoras e publicidade de 30 dias nos arts. 291–294 do PDP', 'F01', 'PDP arts. 291–294; LC 236 Tabela 5.1 e arts. 170–176'),
    'projetos_especiais': P('Projetos Especiais (PE) e PGV dependem de parecer da SEUMA e da CPPD; Análise de Orientação Prévia (AOP) obrigatória', 'F02', 'LC 236 arts. 75 e 170–176'),
    'calculo_ia': P('Residencial: área computável = soma das áreas privativas (NBR 12.721), excluídas sacadas até 1,05 m e estacionamentos; subsolo/garagem não computam', 'F02', 'LC 236 arts. 89–90'),
    'altura_pavimentos': P('Para os recuos de até 4 pavimentos, o 4º pavimento deve estar a até 13 m; pé-direito máximo de 3 m', 'F02', 'LC 236 art. 91 §§2º–3º'),
    'subsolo': P('Recuo frontal mínimo do subsolo 5 m; regra para lotes de esquina acrescida pela LC 378/2023', 'F22', 'LC 236 art. 88 (LC 378/2023)'),
    'condominios': P('Condomínios residenciais – LC 236 art. 193 e seguintes', 'F02', 'LC 236 art. 193'),
    'operacoes_urbanas': P('OUC por lei específica (PDP arts. 242–248; LC 265/2019) – perímetros e leis na zona sobreposta OUC', 'F16', 'PDP arts. 242–248'),
    'restricoes': P('ZPA non aedificandi (LC 236 arts. 103–104); manguezais/APP; Parque do Cocó e ZA; tombamentos e entornos; superfícies de proteção de aeródromos (DECEA); AEA (ruído); terrenos de marinha (LPM 1831); áreas alagadas – ver camadas_complementares', 'F02', 'LC 236 arts. 103–104; camadas F13')},
 'resumo_mcmv': [
    'Vigência: PDP LC 62/2009 + LPUOS LC 236/2017. O novo PDPS (LC 450/2025) só entra em vigor ≈ maio/2027 (LC 461/2026): monitorar a transição.',
    'Densidade: em qualquer zona adequada, HIS multifamiliar MCMV até 6 SM tem Fração do Lote 30 m²/UH (LC 236 art. 101 p.ú.); com solução coletiva de esgoto da CAGECE a Fração nem se aplica (PDP art. 313 §5º, LC 243/2017). Em ZOC/ZOP1/ZOP2 e a até 300 m de metrô/VLT/terminais/corredores TRANSFOR a Fração também não se aplica.',
    'Zonas de maior potencial: ZOP1 e ZO-IV (IA 3,0; 72 m); ZOC (2,5); ZOP2 (IA 2,0 → 3,0 com OODC, Fp 0,5); ZEDUS Centro/Aldeota/Varjota (IA máx 4,0; 95 m) e Porangabuçu/Messejana/Montese/Vila União/Seis Bocas/Carlito Pamplona (3,0). ZRU1/ZRU2/ZOM2 (IA 1,5–2,0; 48 m) são as áreas periféricas típicas de MCMV.',
    'Usos: multifamiliar e conjuntos HIS adequados em todas as vias na Macrozona de Ocupação Urbana; inadequados em ZPA, ZRA, ZO-III-SZ2-S2, ZO-V, ZO-VI, AEA 1 e (HIS) em ZIA Praia do Futuro e AEA 2/3; com restrição em ZO-I/II, ZIA Sabiaguaba e ZEDUS BR-116 T1/T2.',
    'Custos: EHIS isentos de OODC (PDP art. 220 §2º); LC 359/2023 (LC 434/2025): isenção de ITBI (terreno e unidades), ISSQN da obra, taxas de licença/habite-se e IPTU por 5 anos para o beneficiário.',
    'Projeto: 1 vaga/UH (multifamiliar e HIS em prédios), 1 vaga/6 UH em conjuntos HIS de casas e unidades compactas; recuos 5/3/3 m (+0,25 m/pav acima do 4º); conjuntos HIS: lote mínimo 125 m², testada 5 m.',
    'Licenciamento: conjuntos >300 UH são Projeto Especial (AOP; SEUMA/CPPD) e conjuntos de mercado >300 UH exigem EIV. ZEIS 3 são vazios destinados a HIS (Plano de Intervenção; cedentes de TDC).',
    'Restrições a checar: superfícies de proteção dos aeródromos Pinto Martins/Feijó/Dias Branco (altura), AEA (ruído), ZEPH/tombamentos, manguezais, ZA do Parque do Cocó, terrenos de marinha e áreas alagadas.'],
 'geografico': {
    'descricao': 'Todas as geometrias vêm de camadas vetoriais OFICIAIS do portal Fortaleza em Mapas (Prefeitura de Fortaleza), baixadas pelo download público em GeoJSON (sem login). Nenhuma geometria foi digitalizada. Simplificação ≤1,5 m (EPSG:31984), coordenadas com 6 casas decimais.',
    'crs': 'EPSG:4326', 'crs_area': 'EPSG:31984',
    'servidor_oficial': {'portal': MAPAS, 'download_geojson': MAPAS + '/api/download/geojson/<id>', 'observacao': 'Não foi localizado WFS/ArcGIS REST público; usado o download oferecido pelo próprio portal para cada camada.'},
    'camadas': geo_camadas,
    'regras_de_consulta': [
        '1) Zona base predominante entre as zonas base (camadas 604, 76, 77, 78), que formam uma partição do território.',
        '2) ZEDUS (prioridade 20, substitui, limiar 50%): substitui TP/TO/IA mín/IA máx/altura/lote/fração/usos; o IA básico permanece o da base (mantem_da_base).',
        '3) ZEIS 1/2/3, ZEA, ZEPO, ZEPH, ZEI, OUC e AEA: apenas alerta; AEA com limiar 0.',
        '4) Camada fracao_do_lote (macrozona): fração do código predominante; para HIS MCMV ≤6 SM usar 30 m²/UH (art. 101 p.ú.) ou não aplicar com esgoto CAGECE (art. 313 §5º).',
        '5) Camadas restricao: um alerta por código intersectado (aeródromos, tombamento/entorno, risco, mangue, alagados, UCs).',
        '6) ZPA prevalece sobre qualquer outra disposição (LC 236 art. 104).'],
    'regras_de_consulta_texto': 'Base predominante → ZEDUS (substitui, exceto IA básico) → alertas de zonas especiais e restrições. Confirmar sempre na SEUMA (Consulta de Adequabilidade).',
    'raio_divisa_m': 30, 'pct_minimo_significativo': 0.5,
    'limitacoes': [
        'Camada 604 com ano_ref 2022, ZPA 2020, Zonas Especiais/ZEIS 2018: rezoneamentos posteriores (LC 349/2023; LCs 397, 410, 417 e 418/2024) podem não estar refletidos.',
        'O Mapa Indicador de Fração do Lote (áreas de aplicação 1–5) não está publicado como vetor; usado o atributo fracao_lote da 604.',
        'Superfícies de transição e SPVV dos aeródromos (linhas abertas) não foram poligonizadas; comparar altitudes com cota do terreno + altura do edifício.',
        'Classificação viária (camada 804) não incluída (recuos residenciais independem da via na Tabela 8.1).',
        'Geometrias simplificadas (≤1,5 m): não usar para demarcação de divisas.']},
 'lacunas': [
    {'item': 'Notas de restrição P(n) do Anexo 6 (ex.: P(1) em ZO-I/II e ZIA Praia do Futuro; P(8)/P(3) em ZEDUS BR-116; P(2) em AEA 2/3 e ZIA Sabiaguaba)', 'motivo': 'Notas em imagens/rodapés do DOM; texto não extraído com segurança – registrado apenas o código.'},
    {'item': 'Áreas de aplicação 1–5 da Fração do Lote (Mapas 2–2.16 da LC 236; LC 101/2011)', 'motivo': 'Sem camada vetorial pública; digitalização não realizada. Na ZOP1 a fração (30/45) é irrelevante pois não se aplica (art. 313 §3º).'},
    {'item': 'Adequação de usos da ZIA Cocó, ZEDUS Francisco Sá e AEA 4', 'motivo': 'Tabelas específicas não localizadas no texto do Anexo 6.'},
    {'item': 'Parâmetros por setor das ZEIS 1 com lei própria (LCs 438–447/2025)', 'motivo': 'Resumidos no alerta; setores sem perímetro vetorial público. LC 442 (Lagamar) não baixada.'},
    {'item': 'Índices das Operações Urbanas Consorciadas', 'motivo': 'Leis específicas não baixadas; só a referência da camada oficial.'},
    {'item': 'Perímetros alterados após 2022 (ZEDUS Aldeota ampliada – LC 349/2023; ZRU2/ZOM2-SZ1/ZPA – LCs 397, 410, 417 e 418/2024; ZO Trecho VIII citado pela LC 418/2024)', 'motivo': 'Não constam das camadas oficiais disponíveis; confirmar na SEUMA.'},
    {'item': 'Redutor transitório da OODC (art. 220 §3º) e decretos de atualização do Fp', 'motivo': 'Decretos não localizados nas fontes consultadas.'},
    {'item': 'Texto integral das alterações da LC 434/2025 à LC 359/2023', 'motivo': 'Lido parcialmente; resumido.'},
    {'item': 'Área do art. 105 p.ú. do PDP (LC 277/2019 – IA 2,0)', 'motivo': 'Sem camada própria; não modelada.'},
    {'item': 'Gabarito em pavimentos', 'motivo': 'A LC 236 fixa altura máxima em metros; não há limite em pavimentos (exceto ZEIS com lei própria).'}],
}
# ======================================================================= NORMALIZAÇÃO schema 1.1
UNID = {'ca_minimo': 'coeficiente', 'ca_basico': 'coeficiente', 'ca_maximo': 'coeficiente', 'taxa_ocupacao': 'fracao', 'taxa_permeabilidade': 'fracao',
        'gabarito_altura_max_m': 'm', 'gabarito_pavimentos': 'pavimentos', 'frontal': 'm', 'lateral': 'm', 'fundos': 'm', 'lote_minimo_m2': 'm2',
        'testada_minima_m': 'm', 'usos_permitidos': 'codigos_de_uso'}

def norm_p(p, key):
    if p is None:
        return None
    u = p.get('unidade')
    if u == '%':
        if isinstance(p.get('valor'), (int, float)):
            p['valor'] = round(p['valor'] / 100, 6)
        u = 'fracao'
    if u in ('m²', 'm2'):
        u = 'm2'
    if u == 'm²/UH':
        u = 'm2/UH'
    if key in UNID:
        u = UNID[key]
    p['unidade'] = u
    if key == 'usos_permitidos' and p.get('forma') == 'texto':
        st = parse_usos(p['texto_original'])
        if st:
            ok = [c for c in st if not st[c].startswith('I')]
            p['valor'] = ok
            p['forma'] = 'lista'
            grupos = {}
            for c, v in st.items():
                grupos.setdefault(v, []).append(c)
            p['condicionais'] = [C({'A': 'adequado (A)', 'I': 'inadequado (I)'}.get(v, f'adequado com restrição {v} (nota da tabela)'), cs) for v, cs in grupos.items()]
            p['observacao'] = ((p.get('observacao') or '') + ' valor = classes residenciais adequadas (A) ou com restrição (P/A(n)); detalhe em condicionais/texto_original.').strip()
    if key == 'densidade' and u not in ('hab/ha', 'uh/ha', None):
        p['unidade'] = None
    return p

def norm_pars(par):
    for k, v in list(par.items()):
        if k == 'recuos':
            if v is None:
                par[k] = {'frontal': None, 'lateral': None, 'fundos': None}
            else:
                for kk in v:
                    v[kk] = norm_p(v[kk], kk)
        elif k == 'outros':
            for kk in v:
                v[kk] = norm_p(v[kk], kk)
        else:
            par[k] = norm_p(v, k)
    return par

def parse_usos(t):
    """'R1 A; R2 (multifamiliar) P(1); R7–R10 I' → {'R1':'A','R2':'P(1)',...}; None se não reconhecer."""
    st = {}
    for tok in [x.strip() for x in t.split(';') if x.strip()]:
        m = re.match(r'^Todas as classes residenciais \(1–10\) (A|I)$', tok)
        if m:
            for k in range(1, 11): st[f'R{k}'] = m.group(1)
            continue
        m = re.match(r'^R(\d+)(?:–R(\d+))?(?: \([^)]*\))? ((?:A|P|I)(?:\(\d+\))?)(?: \(.*\))?$', tok)
        if not m:
            return None
        a = int(m.group(1)); b = int(m.group(2) or a)
        for k in range(a, b + 1): st[f'R{k}'] = m.group(3)
    return st

def dens(ca):
    return 'baixa' if ca <= 1.5 else 'media' if ca <= 3 else 'alta'

def categoria(z):
    c = z['codigo']; mx = (z['parametros'].get('ca_maximo') or {}).get('valor')
    if c.startswith(('ZPA', 'ZRA', 'ZIA', 'ZEA')):
        return 'ambiental', 'Zona da Macrozona de Proteção Ambiental / especial ambiental.'
    if c.startswith('ZEDUS'):
        return 'centralidade', 'ZEDUS = zona especial de dinamização urbanística (centralidades e corredores) – PDP arts. 145–147.'
    if c.startswith('ZEIS'):
        return 'especial_interesse_social', 'Zona Especial de Interesse Social (PDP art. 125).'
    if c == 'ZEPH':
        return 'patrimonio_cultural', 'Zona especial de preservação do patrimônio.'
    if c == 'ZEI':
        return 'institucional', 'Zona especial institucional.'
    if c == 'ZO-VI':
        return 'industrial', 'Trecho VI da Orla: Cais do Porto – área industrial; residencial inadequado.'
    if c in ('ZO-V', 'ZEPO', 'OUC') or c.startswith('AEA'):
        return 'outra', 'Zona de regime específico (lista taxativa de usos, projeto orla, operação urbana ou ruído aeroportuário).'
    if isinstance(mx, (int, float)):
        return f'mista_{dens(mx)}_densidade', f'Classificação do analista: zona da Macrozona de Ocupação Urbana com uso misto; IA máximo {mx} (≤1,5 baixa; ≤3 média; >3 alta).'
    return 'outra', None

def bloco(d, resumo):
    itens = []
    for k, v in d.items():
        it = {'chave': k, 'titulo': k.replace('_', ' ')}
        if 'formula' in k and isinstance(v.get('valor'), str):
            obs = '; '.join(f'{a} = {b}' for a, b in (v.get('variaveis') or {}).items())
            q = P(None, v['fonte_id'], v['artigo_anexo'], ('variáveis: ' + obs) if obs else None, None, 'formula', formula=v['valor'], texto_original=v['valor'])
        else:
            q = dict(v)
            q.pop('variaveis', None)
        it.update(q)
        itens.append(it)
    f0 = next((i['fonte_id'] for i in itens if i.get('fonte_id')), None)
    a0 = next((i['artigo_anexo'] for i in itens if i.get('artigo_anexo')), None)
    return {'resumo': resumo, 'fonte_id': f0, 'artigo_anexo': a0, 'itens': itens}

def to_v11(doc):
    doc['schema_versao'] = '1.1'
    for f in doc['fontes']:
        o = f.pop('observacao', None)
        if o:
            m = re.match(r'^(?:Cópia em )?(fontes/[^\s,;]+)', o)
            if m:
                f['arquivo_local'] = m.group(1).replace('fontes/', '')
            if not m or len(o) > len(m.group(0)) + 2:
                f['titulo'] = f"{f['titulo']} [{o}]"
    for z in doc['zonas']:
        norm_pars(z['parametros'])
        cat, crit = categoria(z)
        z['categoria_normalizada'] = cat
        z['categoria_criterio'] = crit
        ob = z.get('observacoes')
        z['observacoes'] = [] if not ob else [ob] if isinstance(ob, str) else list(ob)
        z.setdefault('regra_sobreposicao', None)
        ordem = ['codigo', 'nome', 'descricao', 'tipo', 'prioridade', 'categoria_normalizada', 'categoria_criterio', 'regra_sobreposicao', 'parametros', 'observacoes', 'geometria']
        zz = {k: z[k] for k in ordem}; z.clear(); z.update(zz)
    for c in doc['camadas_complementares'].values():
        if c.get('parametros_por_codigo'):
            for cod, d in c['parametros_por_codigo'].items():
                for k in d:
                    d[k] = norm_p(d[k], k)
    doc['macrozonas'] = [{'codigo': m['codigo'], 'nome': m['nome'],
                          'descricao': f"{m['nome']} ({m['artigo_anexo']}, fonte {m['fonte_id']}). Zonas: {', '.join(m['zonas'])}.",
                          'parametros': {}} for m in doc['macrozonas']]
    doc['outorga_onerosa'] = bloco(doc['outorga_onerosa'], 'OODC entre o IA básico e o máximo da zona (PDP arts. 218–223); EHIS isentos; TDC e OOAU regulamentados por leis próprias.')
    doc['zeis_his'] = bloco(doc['zeis_his'], 'ZEIS 1/2/3 (PDP art. 125); fração 30 m²/UH ou dispensa com esgoto CAGECE para HIS MCMV; conjuntos HIS arts. 204–211 da LC 236; incentivos fiscais LC 359/2023.')
    doc['outros_parametros'] = bloco(doc['outros_parametros'], 'EIV, projetos especiais, cálculo do IA, altura, subsolo, condomínios, OUC e restrições.')
    g = doc['geografico']
    so = g['servidor_oficial']
    g['servidor_oficial'] = so['portal']
    g['notas_tecnicas'] = {'servidor': so}
    g['regras_de_consulta'] = ' '.join(g['regras_de_consulta'])
    return doc

to_v11(doc)
# ZIA: IA por condição (forma condicional)
for z in doc['zonas']:
    if z['codigo'] == 'ZIA-SABIAGUABA':
        for k in ('ca_basico', 'ca_maximo'):
            q = z['parametros'][k]
            q.update(valor=None, forma='condicional', condicionais=[C('quadras lindeiras à Av. Manoel Mavignier (a partir de UTM E 563.326,170 / N 9.578.807,140)', 1.5), C('demais áreas da ZIA Sabiaguaba', 1.0)])
    if z['codigo'] == 'ZIA-SABIAGUABA':
        u = z['parametros']['usos_permitidos']
        u.update(valor=['R1', 'R2', 'R3'], forma='lista', observacao='Somente nas quadras lindeiras à Av. Manoel Mavignier: R1 A, R2 (multifamiliar) P(2), R3 A; demais classes e demais áreas: inadequado.',
                 condicionais=[C('quadras lindeiras à Av. Manoel Mavignier', ['R1', 'R2', 'R3']), C('demais áreas da ZIA Sabiaguaba', None, 'nao_aplicavel', obs='inadequado')])
    if z['codigo'] == 'ZIA-PRAIA-DO-FUTURO':
        for k in ('ca_basico', 'ca_maximo'):
            q = z['parametros'][k]
            q.update(valor=None, forma='condicional', condicionais=[C('residencial unifamiliar', 1.0), C('residencial multifamiliar e demais usos', 2.0)])

out = os.path.join(BASE, 'fortaleza-ce.json')
with open(out, 'w') as fh:
    json.dump(doc, fh, ensure_ascii=False, separators=(',', ':'))
print('zonas', len(zonas), 'camadas', len(cam), 'MB', round(os.path.getsize(out) / 1e6, 2))
