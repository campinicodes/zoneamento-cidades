#!/usr/bin/env python3
"""Gera salvador-ba.json (schema 1.1) - Salvador/BA.
Zoneamento: Mapa 01A do Anexo 02 da LOUOS (Lei 9.148/2016, alterado ate ATA CNLU 12/2022), vetorizado do PDF oficial
(extrair_pdf_mapa01a.py) e georreferenciado contra o vetor oficial de ZEIS (georref_mapa01a.py). O vetor oficial do
zoneamento no GeoSalvador exige token - nao foi usado. Demais camadas: vetores oficiais publicos do GeoSalvador."""
import json, os, collections, re
import numpy as np, shapely
from shapely.geometry import shape, mapping, Point
from shapely import make_valid, STRtree
from shapely.ops import unary_union
from pyproj import Transformer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'geo_raw')
OUT = os.path.join(BASE, 'salvador-ba.json')
TOL = 2.0
U2G = Transformer.from_crs(31984, 4326, always_xy=True)
G2U = Transformer.from_crs(4326, 31984, always_xy=True)
A = np.array(json.load(open(os.path.join(RAW, 'georref_mapa01a.json')))['afim_pdf_para_31984'])
LOG = {e['tema']: e for e in json.load(open(os.path.join(RAW, '_log_download.json')))}

def to_utm(g): return shapely.transform(g, lambda c: np.c_[G2U.transform(c[:, 0], c[:, 1])])
def to_geo(g): return shapely.transform(g, lambda c: np.round(np.c_[U2G.transform(c[:, 0], c[:, 1])], 6))
def pdf_to_utm(g): return shapely.transform(g, lambda c: c @ A[:, :2].T + A[:, 2])
def _poly_only(g, kind=None):
    parts = list(g.geoms) if g.geom_type in ('GeometryCollection', 'MultiPolygon', 'MultiLineString') else [g]
    polys = [q for q in parts if q.geom_type in ('Polygon', 'MultiPolygon') and not q.is_empty]
    lines = [q for q in parts if q.geom_type in ('LineString', 'MultiLineString') and not q.is_empty]
    if kind is None: kind = 'poly' if polys else 'line'
    sel = polys if kind == 'poly' else lines
    if not sel: return None
    g = unary_union(sel) if len(sel) > 1 else sel[0]
    return None if g.is_empty else g
def geo_out(g_utm, tol=TOL):
    if g_utm.geom_type in ('Point', 'MultiPoint'): return mapping(to_geo(g_utm))
    kind = 'line' if g_utm.geom_type in ('LineString', 'MultiLineString') else 'poly'
    g = _poly_only(make_valid(g_utm.simplify(tol, preserve_topology=True)), kind)
    if g is None: return None
    g = shapely.set_precision(shapely.transform(g, lambda c: np.c_[U2G.transform(c[:, 0], c[:, 1])]), 1e-6)
    if not g.is_valid: g = make_valid(g)
    g = _poly_only(g, kind)
    return mapping(g) if g is not None else None
def load(t): return json.load(open(os.path.join(RAW, f'{t}.geojson')))['features']
def url(t): return LOG[t]['url']
def clean(v):
    if v is None: return None
    v = str(v).strip()
    return v or None

HOJE = '2026-10-27'
SRV = 'https://geo.salvador.ba.gov.br/arcgis/rest/services'
PDDU_URL = 'https://pddu.salvador.ba.gov.br/img/arquivos/'
MAPA01A_URL = PDDU_URL + 'louos/LOUOS_MAPA_01A_ZONAS-DE-USO_MODIFICADO_CNLU_ESALVADOR_compressed.pdf'
MAPA03_URL = PDDU_URL + 'louos/SSA_LOUOS_03_GABARITO-ABM.compressed.pdf'

# ------------------------------------------------------------------ parametros (schema 1.1)
def P(valor, unidade, fonte, art, obs=None, forma=None, **kw):
    if forma is None: forma = 'unico' if isinstance(valor, (int, float)) else ('lista' if isinstance(valor, list) else 'sem_dado')
    d = {"valor": valor, "unidade": unidade, "fonte_id": fonte, "artigo_anexo": art, "observacao": obs, "forma": forma}
    d.update({k: v for k, v in kw.items() if v is not None})
    return d
def C(condicao, forma, valor=None, **kw):
    d = {"condicao": condicao, "forma": forma, "valor": valor}
    d.update({k: v for k, v in kw.items() if v is not None})
    return d
def I(chave, titulo, valor, unidade, fonte, art, obs=None, forma=None, **kw):
    d = {"chave": chave, "titulo": titulo}; d.update(P(valor, unidade, fonte, art, obs, forma, **kw)); return d

Q6 = 'Quadro 06 do Anexo 01 da LOUOS (Lei 9.148/2016)'
Q3 = 'Quadro 03 do Anexo 01 da LOUOS'
Q10 = 'Quadro 10 do Anexo 01 da LOUOS'
Q11B = 'Quadro 11 B do Anexo 01 da LOUOS'
NOME = {  # PDDU Quadro 01 (Anexo 2 da Lei 9.069/2016)
 'ZPR-1': 'Zona Predominantemente Residencial de Baixa Densidade - 1', 'ZPR-2': 'Zona Predominantemente Residencial de Média Densidade - 2',
 'ZPR-3': 'Zona Predominantemente Residencial de Alta Densidade - 3', 'ZEIS-1': 'Zona Especial de Interesse Social - Assentamentos Precários - 1',
 'ZEIS-2': 'Zona Especial de Interesse Social - Edificação deteriorada - 2', 'ZEIS-3': 'Zona Especial de Interesse Social - Terrenos - 3',
 'ZEIS-4': 'Zona Especial de Interesse Social - APA e APRN - 4', 'ZEIS-5': 'Zona Especial de Interesse Social - Quilombos e Comunidades Tradicionais - 5',
 'ZCMe-1/01': 'Zona Centralidade Metropolitana Camaragibe - 1/01', 'ZCMe-1/02': 'Zona Centralidade Metropolitana Retiro/Acesso Norte - 1/02',
 'ZCMe-1/03': 'Zona Centralidade Metropolitana Avenida Luís Viana/Av. 29 de Março - 1/03', 'ZCMe-2': 'Zona Centralidade Metropolitana Uso Misto (Águas Claras/Valéria) - 2',
 'ZCMe-CA': 'Zona Centralidade Metropolitana - Centro Antigo', 'ZCMu-1': 'Zona Centralidade Municipal - 1 (Ipitanga/CIA Aeroporto)',
 'ZCMu-2': 'Zona Centralidade Municipal - 2', 'ZCLMe': 'Zona Centralidade Linear Metropolitana', 'ZCLMu': 'Zona Centralidade Linear Municipal',
 'ZUSI': 'Zona de Uso Sustentável nas Ilhas', 'ZIT': 'Zona de Interesse Turístico', 'ZDE-1': 'Zona de Desenvolvimento Econômico - 1',
 'ZDE-2': 'Zona de Desenvolvimento Econômico - 2', 'ZEM': 'Zona de Exploração Mineral', 'ZPAM': 'Zona de Proteção Ambiental',
 'ZUE-1': 'Zona de Uso Especial 1 - Centro Administrativo da Bahia', 'ZUE-2': 'Zona de Uso Especial 2 - Parque Tecnológico',
 'ZUE-3': 'Zona de Uso Especial 3 - Porto de Salvador', 'ZUE-4': 'Zona de Uso Especial 4 - Complexo Aeroportuário de Salvador',
 'ZUE-5': 'Zona de Uso Especial 5 - Base Naval de Aratu', 'ZUE-6': 'Zona de Uso Especial 6 - Central de Abastecimento da Bahia (CEASA)',
 'ZUE-7': 'Zona de Uso Especial 7 - Setor Militar Urbano', 'ZUE-8': 'Zona de Uso Especial 8 - Campus da UFBA',
 'ZUE-9': 'Zona de Uso Especial 9 - Campus da UNEB', 'ZUE-10': 'Zona de Uso Especial 10 - Parque de Exposições Agropecuárias',
 'ZUE-11': 'Zona de Uso Especial 11 - Aterro Sanitário Metropolitano', 'ZUE-12': 'Zona de Uso Especial 12 - Centro de Convenções da Bahia',
 'ZUE-13': 'Zona de Uso Especial 13 - Arena Fonte Nova'}
CA = {'ZPR-1': (0.10, 1.0, 1.0), 'ZPR-2': (0.20, 1.0, 2.0), 'ZPR-3': (0.30, 1.5, 3.0),
      **{f'ZEIS-{i}': (0.30, 1.5, 3.0) for i in (1, 2, 3)}, **{f'ZEIS-{i}': (0.20, 1.0, 2.0) for i in (4, 5)},
      **{k: (0.40, 2.0, 4.0) for k in ('ZCMe-1/01', 'ZCMe-1/02', 'ZCMe-1/03', 'ZCMe-2', 'ZCMe-CA', 'ZCLMe')},
      'ZCMu-1': (0.20, 1.0, 2.0), 'ZCMu-2': (0.30, 1.5, 3.0), 'ZCLMu': (0.30, 1.5, 3.0), 'ZDE-1': (0.20, 1.0, 2.0), 'ZDE-2': (0.20, 1.0, 2.0),
      'ZUSI': (0.20, 1.0, 1.0), 'ZIT': (0.20, 1.0, 2.0), 'ZEM': (0.10, 0.5, 0.5), 'ZPAM': (None, 0.2, 0.2),
      **{f'ZUE-{i}': (0.20, 1.0, 2.0) for i in (1, 3, 4, 6, 7, 8, 9, 10, 12)}, **{f'ZUE-{i}': (0.30, 1.5, 3.0) for i in (2, 13)},
      **{f'ZUE-{i}': (0.20, 1.0, 1.0) for i in (5, 11)}}
OCUP = {'ZPR-1': ('a', 0.30, '4c', 1.5, 2.5), 'ZPR-2': ('a', 0.30, '4c', 1.5, 2.5), 'ZPR-3': ('a', 0.20, '4c', 1.5, 2.5),
        **{f'ZEIS-{i}': ('a', 'b', 'g', 'g', 'g') for i in range(1, 6)},
        **{k: (0.60, 0.20, 7.5, 1.5, 2.5) for k in ('ZCMe-1/01', 'ZCMe-1/02', 'ZCMe-1/03', 'ZCMe-2')},
        'ZCMe-CA': (0.60, 0.10, '4c', 1.5, 2.5), 'ZCMu-1': (0.60, 0.20, '4c', 1.5, 2.5), 'ZCMu-2': (0.60, 0.20, '4c', 1.5, 2.5),
        'ZCLMe': (0.70, 0.20, 7.5, 1.5, 2.5), 'ZCLMu': (0.70, 0.20, '4c', 1.5, 2.5), 'ZDE-1': (0.70, 0.20, '4d', 1.5, 2.5),
        'ZDE-2': (0.60, 0.20, '4d', 1.5, 2.5), 'ZUSI': (0.30, 0.30, 5.0, 1.5, 2.5), 'ZIT': (0.50, 0.40, 5.0, 1.5, 2.5)}
LOTE = {'ZPR-1': (360, 12), 'ZPR-2': (125, 5), 'ZPR-3': (125, 5), **{f'ZEIS-{i}': (64, 4) for i in range(1, 6)},
        **{k: (1500, 30) for k in ('ZCMe-1/01', 'ZCMe-1/02', 'ZCMe-1/03', 'ZCMe-2', 'ZCLMe', 'ZDE-1', 'ZDE-2')},
        'ZCMe-CA': (250, 10), 'ZCMu-1': (500, 20), 'ZCMu-2': (360, 12), 'ZCLMu': (500, 20), 'ZUSI': (1000, 20), 'ZIT': (10000, 50)}
Q10COLS = ['ZPR-1', 'ZPR-2', 'ZPR-3', 'ZEIS-1', 'ZEIS-2', 'ZEIS-3', 'ZEIS-4', 'ZEIS-5', 'ZCMe-1/01', 'ZCMe-1/02', 'ZCMe-1/03', 'ZCMe-2', 'ZCMe-CA',
           'ZCMu-1', 'ZCMu-2', 'ZCLMe', 'ZCLMu', 'ZDE-1', 'ZDE-2', 'ZUSI', 'ZIT']
Q10T = {'R1': 'SSSSSSSSSSSSSSSSSNSSN', 'R2-01': 'SSSSSSSSSSSSSSSSSNSSN', 'R2-02': 'SSSNNNNNSSSSSSSSSNSSN', 'R3-01': 'SSSNNNNNSSSSSSSSSNSSN',
        'R3-02': 'NSSNNNNNSSSSSSSSSNSNN', 'R3-03': 'NNSNNNNNSSSSNSSSSNSNN', 'EHIS': 'NSSSSSSSSSSSSSSSSSSSN', 'EHMP': 'NSSSSSSSSSSSSSSSSSSSN'}
for _k, _v in Q10T.items(): assert len(_v) == len(Q10COLS), _k
ESP = {'art. 31': 'perímetros de ZEM com disciplina e parâmetros específicos, objeto de estudo junto ao órgão competente (art. 31 §2º).',
       'art. 32': 'perímetros de ZUE com parâmetros dos respectivos Planos Diretores aprovados pelo Executivo (art. 32 §1º).',
       'art. 33': 'ZPAM a regulamentar; até lá, alvarás analisados pela CNLU (art. 33 §4º); na ZPAM das Ilhas valem os Decretos 23.719/2012 e 23.709/2012 e o Mapa 02C (§5º).'}
def art_esp(z): return {'ZEM': 'art. 31', 'ZPAM': 'art. 33'}.get(z, 'art. 32' if z.startswith('ZUE') else None)

def esp_texto(z, unidade, extra=''):
    art = art_esp(z)
    return P(None, unidade, 'F01', f'LOUOS {art}; {Q6}', f'Não fixado. Quadro 06: "Observar as disposições contidas no {art}" – {ESP[art]} {extra}'.strip(), 'sem_dado')

def to_param(z):
    t = OCUP.get(z, (None,) * 5)[0]
    if t == 'a':
        return P(None, 'fracao', 'F03', f'{Q6}, obs. (a)', 'Índice de ocupação máximo em função da área do terreno. Av. Beira Mar (Codlog 2045): IO 0,70 em terrenos de 250 a 450 m² (nota do Quadro 06).', 'condicional',
                 condicionais=[C('terreno < 64 m²', 'unico', 0.90), C('64 m² ≤ terreno < 125 m²', 'unico', 0.70),
                               C('125 m² ≤ terreno < 250 m²', 'unico', 0.60), C('terreno ≥ 250 m²', 'unico', 0.50)])
    if isinstance(t, float): return P(t, 'fracao', 'F03', Q6)
    return esp_texto(z, 'fracao')

def perm_param(z):
    t = OCUP.get(z, (None,) * 5)[1]
    obs_ip = 'Art. 84 §3º: IP pode ser reduzido à metade com captação de 100% das águas pluviais da cobertura.'
    if t == 'b':
        return P(None, 'fracao', 'F03', f'{Q6}, obs. (b)', 'Índice de permeabilidade mínimo em função da área do terreno. ' + obs_ip, 'condicional',
                 condicionais=[C('terreno < 64 m²', 'unico', 0.05), C('64 m² ≤ terreno < 125 m²', 'unico', 0.10), C('terreno ≥ 125 m²', 'unico', 0.15)])
    if isinstance(t, float): return P(t, 'fracao', 'F03', Q6, obs_ip)
    return esp_texto(z, 'fracao')

def recuos(z):
    o = OCUP.get(z)
    if not o:
        r = P(None, 'm', 'F01', f'LOUOS {art_esp(z)}; arts. 86–90', 'Sem recuo zonal no Quadro 06 (disciplina específica); valem as regras gerais dos arts. 86–90.', 'sem_dado')
        return {"frontal": r, "lateral": dict(r), "fundos": dict(r)}
    fr, la, fu = o[2], o[3], o[4]
    prog_f = C('altura H > 12 m (recuo frontal progressivo, art. 87)', 'formula', None, formula='RFZ + 0,4 × (H − 12) ÷ 3', faixa={"min": None, "max": 15},
               observacao='RFZ = recuo frontal da zona; se o resultado ≥ 15 m, admite-se 15 m.')
    prog_l = C('altura H > 12 m (recuo lateral/fundo progressivo, art. 90 II)', 'formula', None, formula='1,5 + 0,2 × (H − 12) ÷ 3')
    if fr == 'g':
        frontal = P(None, 'm', 'F03', f'{Q6}, obs. (g) e (c); LOUOS art. 87', 'ZEIS: terrenos < 250 m² isentos de recuos.', 'condicional',
                    condicionais=[C('terreno < 250 m²', 'unico', 0), C('terreno ≥ 250 m²', 'unico', 4.0), C('terreno ≥ 250 m² e profundidade < 12 m (obs. c)', 'unico', 2.0), prog_f])
        lateral = P(None, 'm', 'F03', f'{Q6}, obs. (g); LOUOS art. 90', None, 'condicional',
                    condicionais=[C('terreno < 250 m²', 'unico', 0), C('terreno ≥ 250 m²', 'unico', 1.5), prog_l])
        fundos = P(None, 'm', 'F03', f'{Q6}, obs. (g) e (f)', None, 'condicional',
                   condicionais=[C('terreno < 250 m²', 'unico', 0), C('terreno ≥ 250 m²', 'unico', 2.5), C('profundidade < 12 m (obs. f)', 'unico', 0)])
        return {"frontal": frontal, "lateral": lateral, "fundos": fundos}
    if fr == '4c': conds = [C('regra da zona', 'unico', 4.0), C('profundidade do terreno < 12 m (obs. c)', 'unico', 2.0)]
    elif fr == '4d': conds = [C('regra da zona', 'unico', 4.0), C('lote ≥ 10.000 m² (obs. d)', 'unico', 15.0)]
    else: conds = [C('regra da zona', 'unico', fr)]
    conds += [C('lindeiro a Via Arterial II sem pista marginal (art. 89)', 'unico', 10.0), C('posto de abastecimento (nota do Quadro 06)', 'unico', 10.0), prog_f]
    obs_f = 'Recuo frontal mínimo da zona. '
    if z.startswith(('ZCMe', 'ZCMu', 'ZCL')): obs_f += 'Dispensado em vias com calçada ≥ 5 m ou com doação para alargamento da calçada (arts. 88 III e 112). '
    obs_f += 'Demais isenções no art. 88. Na ABM vale o art. 105.'
    frontal = P(None, 'm', 'F03', f'{Q6}; LOUOS arts. 87–89', obs_f, 'condicional', condicionais=conds)
    lateral = P(None, 'm', 'F03', f'{Q6}, obs. (e); LOUOS art. 90', 'Até 12 m de altura: testada ≤ 12 m dispensa; 12–15 m exige só uma lateral. §1º: alternativa soma dos laterais ≥ 30% da testada.', 'condicional',
                condicionais=[C('regra da zona (testada > 15 m)', 'unico', la), C('altura ≤ 12 m e testada ≤ 12 m', 'unico', 0), prog_l])
    fundos = P(None, 'm', 'F03', f'{Q6}, obs. (f); LOUOS art. 86 §2º', 'Terrenos de esquina não têm recuo de fundo (art. 86 §2º).', 'condicional',
               condicionais=[C('regra da zona', 'unico', fu), C('profundidade do terreno < 12 m (obs. f)', 'unico', 0), prog_l])
    if z == 'ZCMe-CA':
        for r in (lateral, fundos): r['observacao'] += ' ZCMe-CA: célula mesclada do Quadro 06 lida como comum às ZCMe (conferir).'
    return {"frontal": frontal, "lateral": lateral, "fundos": fundos}

def usos(z):
    if z in Q10COLS:
        i = Q10COLS.index(z)
        ok = [u for u, s in Q10T.items() if s[i] == 'S']; nao = [u for u, s in Q10T.items() if s[i] == 'N']
        obs = (f"Usos residenciais permitidos no {Q10}; não permitidos: {', '.join(nao) or 'nenhum'}. R1 unifamiliar; R2-01/R2-02 habitação horizontal; "
               "R3-01 edifício de apartamentos; R3-02 conjunto até 400 UH; R3-03 conjunto > 400 UH; EHIS/EHMP empreendimentos de HIS/HMP (art. 121). Usos nR/ID no mesmo quadro.")
        if z.startswith('ZEIS'): obs += ' Na ZEIS o multifamiliar de mercado (R3) não é admitido; só EHIS/EHMP.'
        return P(ok, 'codigos_de_uso', 'F03', Q10, obs, 'lista')
    txt = {'ZEM': 'Extração e beneficiamento mineral e atividades compatíveis com a lavra, conforme estudo específico (art. 31). Sem uso residencial.',
           'ZPAM': 'Conservação ambiental e uso sustentável; admite usos residenciais de baixa densidade construtiva e populacional e recreação/lazer; empreendimentos analisados pela CNLU até a regulamentação (art. 33 caput e §4º).'}.get(z, 'Nas ZUE, os usos permitidos e respectivos usos acessórios serão autorizados caso a caso, de acordo com as características específicas de cada ZUE (art. 32 §3º).')
    return P(None, 'codigos_de_uso', 'F01', f'LOUOS {art_esp(z)}', 'Zona fora do Quadro 10.', 'texto', texto_original=txt)

def vagas():
    return P(None, 'vagas/unidade', 'F03', f'{Q11B}, obs. (a) e (b)', 'Mínimo de vagas por unidade autônoma residencial (área útil). URB 2 (urbanização integrada de interesse social): mínimo 50% do Quadro 11 B (art. 75 V). PGT residencial ≥ 400 vagas exige RIT (art. 135).', 'condicional',
             condicionais=[C('R1, R2, R3 e EHMP – unidade < 50 m²', 'unico', 0), C('R1, R2, R3 e EHMP – 51 a 100 m²', 'unico', 1),
                           C('R1, R2, R3 e EHMP – 101 a 200 m²', 'unico', 2), C('R1, R2, R3 e EHMP – > 201 m²', 'unico', 3), C('EHIS – 1 vaga para cada 2 UH', 'unico', 0.5)])

def gabarito():
    return P(None, 'm', 'F01', 'LOUOS arts. 79, 85 §§6º–7º, 102–104; Mapa 03 do Anexo 02', 'Gabarito só é fixado na Área de Borda Marítima (Mapa 03 – camada gabarito_abm). Fora da ABM a LOUOS não fixa gabarito (art. 79); limitam CA, recuos progressivos, COMAER (art. 40 pú) e patrimônio (arts. 38–39).', 'condicional',
             condicionais=[C('terreno fora da ABM', 'livre', None, observacao='Sem gabarito zonal (art. 79).'),
                           C('terreno na ABM (Mapa 03)', 'texto', None, texto_original='Gabarito do Mapa 03 do Anexo 02 conforme trecho/faixa (camada gabarito_abm); máximo absoluto 75 m (art. 104).'),
                           C('EHIS de programa governamental nos trechos 1 e 2 da ABM', 'unico', 15.0, observacao='Art. 85 §7º: até 15 m sem contrapartida.')])

def params(z):
    cmin, cab, cam = CA[z]
    fq = f'{Q6}; PDDU Quadro 01 do Anexo 2'
    p = {"ca_minimo": (P(cmin, 'coeficiente', 'F03', fq, 'Divergência: o Quadro 01 do PDDU traz CA mínimo 0,20 para ZPR-1; adotado o Quadro 06 da LOUOS (lei posterior e específica).' if z == 'ZPR-1' else None)
                       if cmin is not None else P(None, 'coeficiente', 'F03', fq, 'Não se aplica (Quadro 06 e PDDU Quadro 01).', 'nao_aplicavel')),
         "ca_basico": P(cab, 'coeficiente', 'F03', fq),
         "ca_maximo": P(cam, 'coeficiente', 'F03', fq, 'Acima do CAB até o CAM mediante OODC ou TRANSCON (PDDU arts. 293–308); HIS atinge o CAM sem contrapartida (art. 293 §6º).' if cab != cam else None),
         "taxa_ocupacao": to_param(z), "gabarito_altura_max_m": gabarito(), "gabarito_pavimentos": None,
         "taxa_permeabilidade": perm_param(z), "recuos": recuos(z), "lote_minimo_m2": None, "testada_minima_m": None,
         "usos_permitidos": usos(z), "vagas": vagas(), "densidade": None, "outros": {}}
    if z == 'ZUSI':
        p['taxa_permeabilidade']['observacao'] += ' ZUSI: o Quadro 06 (obs. h) remete também aos Decretos 23.719/2012 e 23.709/2012 e ao Mapa 02C.'
    if z in LOTE:
        a, f = LOTE[z]
        conds = [C('regra da zona', 'unico', a), C('EHIS/EHMP em qualquer zona (art. 49 §3º)', 'unico', 125)]
        if z.startswith('ZEIS'):
            conds = [C('regra da zona (Quadro 03, obs. a – art. 49 §2º)', 'unico', 64), C('EHIS/EHMP (art. 49 §3º)', 'unico', 125)]
        p['lote_minimo_m2'] = P(None, 'm2', 'F03', f'{Q3}; LOUOS arts. 49–50', 'Lote máximo 20.000 m² (R2-02, R3-02, R3-03, EHIS e EHMP até 50.000 m² – art. 50 §2º).', 'condicional', condicionais=conds)
        p['testada_minima_m'] = P(f, 'm', 'F03', Q3 + (', obs. (a) – art. 49 §2º' if z.startswith('ZEIS') else ''))
    else:
        txt = 'Nas ZEM, ZUE e ZPAM, aplica-se o disposto nos artigos 31, 32 e 33, respectivamente, desta lei.'
        p['lote_minimo_m2'] = P(None, 'm2', 'F03', f'{Q3}, nota; LOUOS {art_esp(z)}', f'Não fixado. "{txt}" – {ESP[art_esp(z)]}', 'sem_dado')
        p['testada_minima_m'] = P(None, 'm', 'F03', f'{Q3}, nota; LOUOS {art_esp(z)}', f'Não fixado. "{txt}" – {ESP[art_esp(z)]}', 'sem_dado')
    if z in ('ZCMe-1/02', 'ZCMe-1/03', 'ZCMe-2'):
        art = {'ZCMe-1/02': 'art. 172 V–VIII', 'ZCMe-1/03': 'art. 173 II–V', 'ZCMe-2': 'art. 174 I–IV'}[z]
        p['densidade'] = P(None, 'uh/ha', 'F03', f'{Q6} (quota 25 m²); PDDU {art}', 'Quota máxima de terreno de 25 m² por unidade ⇒ densidade MÍNIMA de 400 UH/ha (10.000 ÷ 25). No PDDU é condição para usar CAM 4,0 no residencial, com no máximo 2 vagas/UH.', 'faixa', faixa={"min": 400, "max": None})
        p['outros']['quota_max_terreno_por_unidade_m2'] = P(25, 'm2', 'F03', Q6, 'Cota parte máxima de terreno por unidade habitacional.')
        p['outros']['vagas_max_por_uh_para_cam_4'] = P(2, 'vagas/UH', 'F02', f'PDDU {art}', 'Condição para CAM 4,0 no uso residencial; nR: cota de garagem 32 m²/vaga e no máximo 1 vaga/70 m² de área computável.')
        p['outros']['oodc_his_hmp'] = P(None, None, 'F02', f'PDDU {art}', None, 'texto', texto_original='Isenção do direito adicional de construir para HIS e redução de 50% para HMP com área computável residencial até 70 m²; redução adicional de 50% pelo FDUE.')
    elif z in OCUP:
        p['densidade'] = P(None, 'uh/ha', 'F03', Q6, 'Sem quota/densidade máxima (Quadro 06: NA); a densidade resulta do CA e do tamanho das unidades.', 'livre')
    if z.startswith('ZEIS'):
        n = int(z[-1])
        p['outros']['his1_min_pct_area_construida'] = P(0.6 if n == 3 else 0.5, 'fracao', 'F02', 'PDDU Quadro 02 do Anexo 2; PDDU art. 169; LOUOS art. 21',
              'Mínimo de HIS-1 sobre a área construída total; HIS-2 permitido. Exigido em edificação nova ou reforma com mudança de uso em terrenos > 1.500 m² nas ZEIS 1–4 (PDDU art. 169 §1º).' + (' ZEIS-5 não consta do art. 169, mas consta do Quadro 02.' if n == 5 else ''))
        p['outros']['hmp_e_nao_residencial_max_pct'] = P(0.2, 'fracao', 'F02', 'PDDU Quadro 02 do Anexo 2', 'Máximo de HMP + uso não residencial sobre a área construída total.')
        p['outros']['zeis_lindeira_zcl'] = P(None, None, 'F01', 'LOUOS art. 22', None, 'texto', texto_original='Terrenos em ZEIS lindeiros a ZCLMe/ZCLMu admitem os usos não residenciais e parâmetros de ocupação das ZCL, respeitada a incomodidade da ZEIS.')
        p['outros']['area_nao_residencial_nao_computavel'] = P(0.2, 'fracao', 'F01', 'LOUOS art. 122 §2º', 'Em EHIS/EHMP nas ZEIS, até 20% de área não residencial é não computável.')
    return p

def categoria(z):
    cam = CA[z][2]
    dens = 'baixa' if cam <= 1.5 else ('media' if cam <= 3 else 'alta')
    if z.startswith('ZEIS'): return 'especial_interesse_social', 'ZEIS (PDDU arts. 166–169).'
    if z.startswith('ZPR'): return f'residencial_{dens}_densidade', f'Zona predominantemente residencial; CAM {cam} (≤1,5 baixa; ≤3 média; >3 alta).'
    if z.startswith(('ZCMe', 'ZCMu')): return 'centralidade', 'Zona de centralidade metropolitana/municipal (LOUOS arts. 23–24).'
    if z.startswith('ZCL'): return 'eixo', 'Centralidade linear nos lotes lindeiros às vias (LOUOS arts. 25–27).'
    if z.startswith('ZDE'): return 'especial_economica', 'Zona de desenvolvimento econômico.'
    if z == 'ZIT': return 'especial_economica', 'Zona de interesse turístico.'
    if z == 'ZEM': return 'industrial', 'Exploração mineral (art. 31).'
    if z == 'ZPAM': return 'ambiental', 'Proteção ambiental (art. 33).'
    if z == 'ZUSI': return 'ambiental', 'Uso sustentável nas ilhas.'
    if z.startswith('ZUE'): return 'institucional', 'Zona de uso especial – complexos institucionais e de infraestrutura (art. 32).'
    return 'outra', None

# ------------------------------------------------------------------ zoneamento base (Mapa 01A)
ZUE_MAP = {0: 'ZUE-8', 1: 'ZUE-8', 11: 'ZUE-8', 2: 'ZUE-7', 3: 'ZUE-6', 4: 'ZUE-11', 5: 'ZUE-1', 6: 'ZUE-10', 7: 'ZUE-13',
           8: 'ZUE-5', 9: 'ZUE-12', 10: 'ZUE-2', 12: 'ZUE-4', 13: 'ZUE-3', 14: 'ZUE-9'}
ZCME_MAP = {'CMe4': 'ZCMe-1/01', 'CMe3': 'ZCMe-1/02', 'CMe5': 'ZCMe-1/03', 'CMe2': 'ZCMe-2', 'CMuT': 'ZCMe-CA'}
LEG_DIRETA = {'ZPR-1', 'ZPR-2', 'ZPR-3', 'ZDE-1', 'ZDE-2', 'ZEM', 'ZIT', 'ZUSI', 'ZPAM'}

def build_base():
    d = json.load(open(os.path.join(RAW, 'mapa01a_pdf_coords.json')))
    items = []
    for z, polys in d['polys'].items():
        for i, (g, s) in enumerate(zip(polys, d['seq'][z])):
            gu = make_valid(pdf_to_utm(shape(g)))
            if gu.area < 1: continue
            items.append({'leg': z, 'i': i, 'seq': s, 'g': gu})
    items.sort(key=lambda x: -x['seq'])  # desenhado por último = por cima
    geoms = [x['g'] for x in items]; tree = STRtree(geoms)
    for k, x in enumerate(items):
        cand = [j for j in tree.query(x['g']) if j < k]
        x['eff'] = _poly_only(make_valid(x['g'].difference(unary_union([geoms[j] for j in cand])))) if cand else x['g']
    zeis_of = [(f['properties'], make_valid(to_utm(shape(f['geometry'])))) for f in load('zeis') if f.get('geometry')]
    zt = STRtree([g for _, g in zeis_of])
    pts = [(f['properties']['cod_num'], f['properties']['desc_'], Point(*G2U.transform(*f['geometry']['coordinates'])))
           for f in load('centralidades_metropolitanas') + load('centralidades_municipais')]
    bai = [(f['properties']['nome_bairr'], make_valid(to_utm(shape(f['geometry'])))) for f in load('bairros_oficiais')]
    bt = STRtree([g for _, g in bai])
    zonas = collections.OrderedDict(); stats = collections.Counter()
    for x in items:
        g = x['eff']
        if g is None or g.is_empty or g.area < 50: continue
        g = unary_union([p for p in getattr(g, 'geoms', [g]) if p.geom_type in ('Polygon', 'MultiPolygon')]) if g.geom_type != 'Polygon' else g
        if g.is_empty: continue
        leg = x['leg']; props = {}
        bb = sorted([(bai[j][0], bai[j][1].intersection(g).area) for j in bt.query(g)], key=lambda t: -t[1])
        props['bairros'] = ', '.join(b for b, a in bb[:3] if a > 1)
        if leg in LEG_DIRETA:
            cod = leg
        elif leg == 'ZEIS':
            best = None
            for j in zt.query(g):
                a = zeis_of[j][1].intersection(g).area
                if a > 0 and (best is None or a > best[0]): best = (a, j)
            if best and clean(zeis_of[best[1]][0].get('tipozeis')) in ('1', '2', '3', '4', '5'):
                pz = zeis_of[best[1]][0]; cod = f"ZEIS-{clean(pz['tipozeis'])}"; stats['zeis_sobreposicao'] += 1
                props.update({'zeis_nome': clean(pz.get('zeisnome')), 'zeis_situacao': clean(pz.get('situacao'))})
            else:
                j = min(range(len(zeis_of)), key=lambda j: zeis_of[j][1].distance(g)); pz = zeis_of[j][0]
                cod = f"ZEIS-{clean(pz['tipozeis']) or '1'}"; stats['zeis_proximidade'] += 1
                props.update({'zeis_nome': clean(pz.get('zeisnome')), 'tipo_zeis_origem': 'inferido pela ZEIS oficial mais próxima (sem sobreposição) – conferir'})
        elif leg == 'ZCMe':
            c = min(pts[:5], key=lambda p: g.distance(p[2])); cod = ZCME_MAP[c[0]]; props['centralidade_ref'] = c[1]
        elif leg == 'ZCMu':
            c = min(pts, key=lambda p: g.distance(p[2])); cod = 'ZCMu-1' if c[0] == 'CMu07' else 'ZCMu-2'; props['centralidade_ref'] = c[1]
        elif leg == 'ZUE':
            cod = ZUE_MAP[x['i']]
        else:
            raise SystemExit(f'legenda desconhecida {leg}')
        props['legenda_mapa01a'] = leg
        zonas.setdefault(cod, []).append((g, props))
    return zonas, stats

OBS_GEOM = ('Geometria vetorizada do PDF oficial do Mapa 01A (Anexo 02 da LOUOS, com alterações da LC 074/2020, Leis 9.509/2020 e 9.510/2020 e ATAs CNLU 04/2022 e 12/2022) '
            'e georreferenciada (resíduo mediano ~0,1 m, RMS ~5 m frente ao vetor oficial de ZEIS); oficial:false.')

def build_zonas():
    zonas_g, stats = build_base()
    zonas = []; ordem = list(NOME)
    for cod in sorted(zonas_g, key=ordem.index):
        feats = []
        for g, pr in zonas_g[cod]:
            go = geo_out(g)
            if go: feats.append({"type": "Feature", "properties": {"codigo": cod, **{k: v for k, v in pr.items() if v}}, "geometry": go})
        if not feats: continue
        cat, crit = categoria(cod)
        obs = [OBS_GEOM]
        if cod.startswith('ZEIS'): obs.append('Tipo de ZEIS atribuído pelo vetor oficial de ZEIS do GeoSalvador (campo tipozeis, maior sobreposição). CA de ZEIS 1–3 (0,3/1,5/3,0) e 4–5 (0,2/1,0/2,0) conferido no Quadro 01 do PDDU.')
        if cod.startswith('ZUE'): obs.append('Número da ZUE inferido pela localização (bairros oficiais × lista do art. 32 da LOUOS / Quadro 01 do PDDU); os rótulos do mapa não são texto no PDF.')
        if cod == 'ZPR-1': obs.append('Loteamentos Itaigara e Vela Branca mantêm os parâmetros urbanísticos aprovados (nota (1) do Quadro 01 do PDDU).')
        if cod == 'ZUSI': obs.append('Quadro 06 (obs. h) remete ao zoneamento dos Decretos 23.719/2012 e 23.709/2012 e ao Mapa 02C – decretos não obtidos.')
        if cod == 'ZPAM': obs.append('Até a regulamentação, empreendimentos em ZPAM são analisados pela CNLU (art. 33).')
        if cod == 'ZCMe-1/01': obs.append('Camaragibe: Quadro 06 sem quota de terreno (NA), ao contrário de ZCMe-1/02, 1/03 e 2.')
        if cod.startswith('ZCMu'): obs.append('Subtipo ZCMu-1/ZCMu-2 atribuído pela centralidade do PDDU mais próxima (camada oficial de centralidades municipais).')
        if cod.startswith('ZCMe'): obs.append('Subzona ZCMe atribuída pela centralidade metropolitana do PDDU mais próxima (camada oficial).')
        zonas.append({"codigo": cod, "nome": NOME[cod], "descricao": f"{NOME[cod]} – LOUOS (Lei 9.148/2016) e PDDU (Lei 9.069/2016).",
                      "tipo": "base", "prioridade": 0, "categoria_normalizada": cat, "categoria_criterio": crit, "regra_sobreposicao": None,
                      "parametros": params(cod), "observacoes": obs,
                      "geometria": {"type": "FeatureCollection", "crs": "EPSG:4326", "fonte": MAPA01A_URL, "oficial": False,
                                    "observacao_geometria": "Extração vetorial do PDF oficial + georreferenciamento afim; erro estimado ~5 m.", "features": feats}})
    d = json.load(open(os.path.join(RAW, 'mapa01a_pdf_coords.json')))
    for cod in ('ZCLMe', 'ZCLMu'):
        feats = []
        for g in d['lines'][cod]:
            go = geo_out(pdf_to_utm(shape(g)), 1.0)
            if go: feats.append({"type": "Feature", "properties": {"codigo": cod}, "geometry": go})
        vias = ('BR-324 (Águas Claras/Valéria e Pirajá), Av. 29 de Março, BA-526 e BA-535 (art. 26)' if cod == 'ZCLMe' else
                'vias do art. 27 (Av. Pinto de Aguiar, Orlando Gomes, ACM, Juracy Magalhães, Bonocô, Vasco da Gama, Garibaldi, Heitor Dias, Via Portuária, entre outras)')
        zonas.append({"codigo": cod, "nome": NOME[cod], "descricao": f"{NOME[cod]}: terrenos com frente para {vias}.",
                      "tipo": "eixo", "prioridade": 10, "categoria_normalizada": "eixo", "categoria_criterio": "Centralidade linear nos lotes lindeiros às vias (LOUOS arts. 25–27).",
                      "regra_sobreposicao": {"efeito": "substitui", "usa_indices_de": None, "aplica_sobre": None, "limiar_pct": None, "requer_testada": True, "distancia_max_m": 50,
                                             "fundamento": "LOUOS arts. 25–27 (ZCL incide nos terrenos com frente para os eixos; novas vias derivadas integram a ZCL – art. 25 pú); art. 22 (ZEIS lindeira a ZCL admite usos e parâmetros da ZCL)",
                                             "alerta": f"Terreno junto a eixo {cod}: com frente para a via valem os parâmetros da {cod} (Quadro 06); confirmar testada e classificação viária (Mapa 04).",
                                             "mantem_da_base": []},
                      "parametros": params(cod), "observacoes": ["Eixo desenhado como linha no Mapa 01A (PDF oficial vetorizado); a zona vale para os lotes com testada para a via.", OBS_GEOM],
                      "geometria": {"type": "FeatureCollection", "crs": "EPSG:4326", "fonte": MAPA01A_URL, "oficial": False,
                                    "observacao_geometria": "Linhas extraídas do PDF oficial e georreferenciadas; erro ~5 m.", "features": feats}})
    return zonas, stats

# ------------------------------------------------------------------ camadas complementares
def camada(temas, papel, codfun, descricao, fonte_id, artigo, alerta_fun, keep=(), params_fun=None, dissolve=False, tol=3.0, oficial=True, fonte=None, observacao=None):
    if isinstance(temas, str): temas = [temas]
    by = collections.OrderedDict()
    for t in temas:
        for f in load(t):
            if not f.get('geometry'): continue
            c = codfun(f['properties'], t)
            if c: by.setdefault(c, []).append(f)
    out, alertas, prm = [], {}, {}
    for c, fs in by.items():
        p0 = fs[0]['properties']; alertas[c] = alerta_fun(p0, c)
        if params_fun:
            pr = params_fun(p0, c)
            if pr: prm[c] = pr
        if dissolve:
            go = geo_out(unary_union([make_valid(to_utm(shape(f['geometry']))) for f in fs]), tol)
            if go: out.append({"type": "Feature", "properties": {"codigo": c}, "geometry": go})
            continue
        for f in fs:
            if f['geometry']['type'] in ('Point', 'MultiPoint'):
                go = {"type": "Point", "coordinates": [round(v, 6) for v in f['geometry']['coordinates'][:2]]}
            else:
                go = geo_out(make_valid(to_utm(shape(f['geometry']))), tol)
            if go:
                pp = {"codigo": c}
                for k in keep:
                    v = clean(f['properties'].get(k))
                    if v: pp[k] = v[:200]
                out.append({"type": "Feature", "properties": pp, "geometry": go})
    d = {"papel": papel, "descricao": descricao, "fonte": fonte or url(temas[0]), "oficial": oficial, "fonte_id": fonte_id, "artigo_anexo": artigo,
         "parametros_por_codigo": prm or None, "alerta_por_codigo": alertas, "features": out}
    if observacao: d['observacao'] = observacao
    return d

MACRO = {'macroarea_estruturacao_urbana': 'MEU', 'macroarea_urbanizacao_consolidada': 'MUC', 'macroarea_requalificacao_borda_atlantica': 'MRBA',
         'macroarea_reestruturacao_borda_baia': 'MRBTS', 'macroarea_integracao_metropolitana': 'MIM'}
MACRO_NOME = {'MEU': 'Macroárea de Estruturação Urbana', 'MUC': 'Macroárea de Urbanização Consolidada', 'MRBA': 'Macroárea de Requalificação da Borda Atlântica',
              'MRBTS': 'Macroárea de Reestruturação da Borda da Baía de Todos os Santos', 'MIM': 'Macroárea de Integração Metropolitana'}
FDUE = {'MEU': (0.7, 0.4), 'MUC': (1.0, 1.0), 'MRBTS': (0.6, 0.4), 'MRBA': (1.0, 0.8)}
FS = {'MEU': (0.2, 0.5, 1.0), 'MIM': (0.5, 0.8, 1.0), 'MRBTS': (0.2, 0.5, 1.0), 'MUC': (0.5, 0.8, 1.0), 'MRBA': (0.5, 0.8, 1.0)}
def macro_params(c):
    q3 = 'PDDU Quadro 03 do Anexo 2 (FDUE)'; q4 = 'PDDU Quadro 04 do Anexo 2 (FS)'; p = {}
    if c in FDUE:
        r, n = FDUE[c]
        p['fdue_residencial'] = P(r, 'fator', 'F02', q3, 'Imóveis com frente para a Av. 29 de Março e a Via Pituaçu (Av. Gal Costa): FDUE 0,5 (residencial e nR).' if c == 'MEU' else None)
        p['fdue_nao_residencial'] = P(n, 'fator', 'F02', q3)
    else:
        p['fdue_residencial'] = P(None, 'fator', 'F02', q3, 'Por setor da MIM (Mapa 01B do Anexo 03 do PDDU – setores não vetorizados).', 'condicional',
            condicionais=[C('Setor 1 – BR-324 Polo Logístico', 'unico', 1.2), C('Setor 2 – BR-324 Águas Claras', 'unico', 0.5), C('Setor 3 – Retiro/Acesso Norte', 'unico', 0.5),
                          C('Setor 4 – Camaragibe', 'unico', 0.8), C('Setor 5 – Av. Luís Viana (Paralela)', 'unico', 1.0), C('Setor 6 – Uso Sustentável (Ipitanga)', 'unico', 1.0)])
        p['fdue_nao_residencial'] = P(None, 'fator', 'F02', q3, 'Por setor da MIM.', 'condicional',
            condicionais=[C('Setor 1', 'unico', 0.4), C('Setor 2', 'unico', 0.5), C('Setor 3', 'unico', 0.5), C('Setor 4', 'unico', 0.8), C('Setor 5', 'unico', 0.7), C('Setor 6', 'unico', 1.0)])
    a, b, cc = FS[c]
    p['fs_residencial'] = P(None, 'fator', 'F02', q4, 'Fator social por tamanho da unidade residencial.', 'condicional',
        condicionais=[C('HIS', 'unico', 0.0), C('residência de 50 a 70 m²', 'unico', a), C('70 m² < residência ≤ 100 m²', 'unico', b), C('residência > 100 m²', 'unico', cc)])
    return p

def build_camadas():
    Cm = {}
    Cm['macrozonas'] = camada(['macrozona_ocupacao_urbana', 'macrozona_conservacao_ambiental'], 'macrozona',
        lambda p, t: 'MZOU' if t == 'macrozona_ocupacao_urbana' else 'MZCA', 'Macrozonas do PDDU (Lei 9.069/2016, Mapa 01 do Anexo 03).', 'F02', 'PDDU art. 131 ss.; art. 293 §2º; Quadro 03, nota 2',
        lambda p, c: 'Macrozona de Ocupação Urbana: OODC/TRANSCON aplicáveis entre CAB e CAM.' if c == 'MZOU' else 'Macrozona de Conservação Ambiental: NÃO se aplica a OODC (PDDU Quadro 03, nota 2; art. 293 §2º).',
        params_fun=lambda p, c: {"oodc_aplicavel": P(1 if c == 'MZOU' else 0, 'booleano (1 = sim)', 'F02', 'PDDU art. 293 §2º; Quadro 03, nota 2')}, dissolve=True,
        observacao='MZOU/MZCA são abreviações do levantamento (o vetor oficial traz "MZA" para a de Conservação e nenhum código para a de Ocupação).')
    Cm['macroareas'] = camada(list(MACRO), 'macrozona', lambda p, t: MACRO[t], 'Macroáreas do PDDU (Mapa 01A do Anexo 03) – definem FDUE e FS da contrapartida de OODC/TRANSCON.', 'F02', 'PDDU Quadros 03 e 04 do Anexo 2; art. 295',
        lambda p, c: f'{MACRO_NOME[c]} ({c}): fatores FDUE/FS da fórmula de outorga (PDDU art. 295).', params_fun=lambda p, c: macro_params(c), dissolve=True,
        observacao='Códigos das macroáreas conforme o Quadro 04 do PDDU (a camada oficial usa MAEU para MEU e MARQ para MRBA; a da BTS não tem atributos).')
    Cm['zeis_oficial'] = camada('zeis', 'informativa', lambda p, t: f"ZEIS-{clean(p.get('tipozeis'))}" if clean(p.get('tipozeis')) else 'ZEIS',
        'Vetor oficial de ZEIS (GeoSalvador, Mapa_LOUOS) – usado para tipar as ZEIS da base.', 'F09', 'LOUOS Mapa 01B; PDDU Mapa 03 e Quadro 02',
        lambda p, c: f'{c}: percentuais mínimos de HIS-1 (PDDU Quadro 02).', ['zeisnome', 'situacao'])
    def gab_alerta(p, c):
        g = clean(p.get('gabarito_m'))
        nomes = {'ABM-FAIXA-PRAIA': 'faixa de praia (não edificável)', 'ABM-APR': 'Área de Proteção Rigorosa (Lei 3.289/1983) – parâmetros do órgão de patrimônio', 'ABM-ENCOSTA': 'encosta preservada'}
        if g: return f'Área de Borda Marítima: gabarito máximo {g} m (Mapa 03 da LOUOS, vetorização aproximada). Recuos do art. 105; na Borda Atlântica exige estudo solar (art. 102); OODC obrigatória para o potencial adicional (PDDU art. 293 §3º). Máximo absoluto 75 m (art. 104).'
        return f'Área de Borda Marítima – {nomes.get(c, c)} (Mapa 03 da LOUOS).'
    def gab_par(p, c):
        g = clean(p.get('gabarito_m'))
        if g: return {"gabarito_altura_max_m": P(float(g), 'm', 'F05', 'LOUOS art. 102 e Mapa 03 do Anexo 02', 'Valor da legenda do Mapa 03; polígono aproximado (oficial:false, erro 10–15 m).')}
        o = {'ABM-FAIXA-PRAIA': 'Faixa de praia na legenda do Mapa 03 – sem gabarito (não edificável).',
             'ABM-APR': 'Área de Proteção Rigorosa (Lei 3.289/1983): gabarito definido pela legislação de preservação/órgão de patrimônio, não levantado.',
             'ABM-ENCOSTA': 'Encosta na legenda do Mapa 03 – sem valor de gabarito indicado.'}[c]
        return {"gabarito_altura_max_m": P(None, 'm', 'F05', 'LOUOS art. 102 e Mapa 03 do Anexo 02 (legenda)', o, 'nao_aplicavel' if c == 'ABM-FAIXA-PRAIA' else 'sem_dado')}
    Cm['gabarito_abm'] = camada('mapa03_abm_gabarito', 'restricao', lambda p, t: clean(p.get('codigo')),
        'Gabarito de altura máxima na Área de Borda Marítima – Mapa 03 do Anexo 02 da LOUOS, vetorizado do raster do PDF oficial por classificação de cor (aproximado).', 'F05', 'LOUOS arts. 36, 85 §6º, 102–105, 111; Mapa 03 do Anexo 02',
        gab_alerta, ['gabarito_m'], params_fun=gab_par, tol=4.0, oficial=False, fonte=MAPA03_URL,
        observacao='Erro estimado 10–15 m (~7 m/pixel + classificação de cor). O detalhe "Centro Antigo 1:12.500" do mapa não foi vetorizado: Centro Antigo/Barra sem classe – consultar o PDF. Classes de 51 e 60 m não sobreviveram à filtragem.')
    Cm['limite_abm'] = camada('limite_borda_maritima', 'informativa', lambda p, t: clean(p.get('cod')), 'Limite da Área de Borda Marítima (BAT – Borda Atlântica; BTS – Borda da Baía de Todos os Santos).', 'F09', 'LOUOS art. 36; PDDU arts. 272–275',
        lambda p, c: f"{clean(p.get('nm_borda'))}: limite interior da ABM.", ['nm_borda'], tol=1.0)
    Cm['aprn'] = camada('aprn', 'restricao', lambda p, t: clean(p.get('denominaca')) or 'APRN', 'Áreas de Proteção de Recursos Naturais (SAVAM).', 'F09', 'PDDU arts. 264–267; LOUOS arts. 34–35',
        lambda p, c: f'{c}: área especial do SAVAM – ordenações especiais prevalecem sobre a zona (LOUOS art. 34).', ['obs'])
    Cm['apcp'] = camada('apcp', 'restricao', lambda p, t: clean(p.get('denominaca')) or 'APCP', 'Áreas de Proteção Cultural e Paisagística (SAVAM).', 'F09', 'PDDU arts. 268–271; LOUOS arts. 34–35',
        lambda p, c: f'{c}: proteção cultural/paisagística – ordenações especiais prevalecem (LOUOS art. 34).', ['obs'])
    Cm['unidades_conservacao'] = camada(['ucm', 'uc_indicadas', 'apa_estadual'], 'restricao',
        lambda p, t: (clean(p.get('denominaca')) or 'UCM') if t == 'ucm' else (f"UC indicada – {clean(p.get('descricao'))}" if t == 'uc_indicadas' else f"APA – {clean(p.get('local'))}"),
        'Unidades de Conservação municipais, UCs indicadas pelo PDDU e APAs estaduais.', 'F09', 'PDDU arts. 246–263; LOUOS art. 35 I a',
        lambda p, c: f'{c}: unidade de conservação/APA – zoneamento ambiental e plano de manejo prevalecem; licenciamento ambiental.', ['obs', 'tipo'])
    def parque_cod(p, t):
        nome = clean(p.get('local')) or clean(p.get('denominaca')) or clean(p.get('LOCAL')) or 'sem nome'
        return {'parque_urbano': 'Parque Urbano', 'parque_urbano_proposto': 'Parque Urbano Proposto', 'parque_bairro': 'Parque de Bairro', 'espacos_abertos_urbanizados': 'Espaço Aberto Urbanizado'}[t] + ' – ' + nome
    Cm['parques'] = camada(['parque_urbano', 'parque_urbano_proposto', 'parque_bairro', 'espacos_abertos_urbanizados'], 'restricao', parque_cod,
        'Parques urbanos, parques de bairro e espaços abertos urbanizados (SAVAM).', 'F09', 'PDDU arts. 276–283', lambda p, c: f'{c}: área do SAVAM – ocupação restrita.', ['obs'])
    Cm['mata_atlantica'] = camada('mata_atlantica', 'restricao', lambda p, t: f"Remanescente de Mata Atlântica – {clean(p.get('estagio')) or 'estágio não informado'}",
        'Áreas remanescentes do Bioma Mata Atlântica (RMA) – Mapa 02B da LOUOS.', 'F09', 'LOUOS art. 35 (RMA); PDDU art. 284; Lei federal 11.428/2006',
        lambda p, c: f'{c}: supressão de vegetação sujeita à Lei 11.428/2006 e a licenciamento ambiental.', [], tol=4.0)
    Cm['bens_tombados'] = camada('bens_tombados', 'restricao', lambda p, t: f"Bem tombado – {clean(p.get('trgbo')) or 'órgão n/i'}",
        'Bens tombados (IPHAN/IPAC) – polígonos.', 'F09', 'LOUOS arts. 37–39',
        lambda p, c: f'{c}: imóvel tombado – recuos, gabarito, ocupação e volumetria condicionados ao órgão de preservação (LOUOS art. 38).', ['nome', 'tombamento'], tol=1.0)
    tomb = [make_valid(to_utm(shape(f['geometry']))) for f in load('bens_tombados') if f.get('geometry')]
    Cm['entorno_tombados_200m'] = {"papel": "restricao", "descricao": "Entorno de 200 m dos bens tombados (buffer calculado sobre o vetor oficial de bens tombados).", "fonte": url('bens_tombados'), "oficial": False,
        "fonte_id": "F01", "artigo_anexo": "LOUOS art. 39", "parametros_por_codigo": None,
        "alerta_por_codigo": {"ENTORNO-TOMBADO-200M": "Até 200 m de bem tombado: gabarito, volumetria e fachadas sujeitos aos órgãos de preservação (LOUOS art. 39)."},
        "observacao": "Buffer de 200 m gerado no levantamento (não é polígono oficial); poligonais de entorno do IPHAN/IPAC podem diferir.",
        "features": [{"type": "Feature", "properties": {"codigo": "ENTORNO-TOMBADO-200M"}, "geometry": geo_out(unary_union([g.buffer(200, 8) for g in tomb]), 3.0)}]}
    Cm['risco_geologico'] = camada('risco_idesh', 'restricao', lambda p, t: f"Risco {clean(p.get('grau_risco')) or 'n/i'} – {clean(p.get('tipologia')) or 'n/i'}",
        'Setores de risco geológico/geotécnico mapeados (camada idesh_risco_a do GeoSalvador).', 'F09', 'Camada oficial de risco; PDDU (diretrizes para áreas de risco)',
        lambda p, c: f'{c}: setor de risco mapeado – consultar CODESAL/Defesa Civil; contenção e drenagem podem ser exigidas.', ['local', 'sug_obras'])
    Cm['operacoes_urbanas'] = camada('ouc', 'restricao', lambda p, t: re.sub(r'\s+', ' ', clean(p.get('nome')) or 'OUC'),
        'Perímetros de Operação Urbana Consorciada (PDDU Mapa 08).', 'F02', 'PDDU arts. 325–328; art. 296',
        lambda p, c: f'{c}: perímetro de OUC do PDDU – índices podem ser alterados por lei específica da operação (art. 326); outorga de alteração de uso só em OUC (art. 296). Não foi localizada lei específica em vigor.')
    Cm['centralidades_pddu'] = camada(['centralidades_metropolitanas', 'centralidades_municipais'], 'informativa', lambda p, t: clean(p.get('cod_num')),
        'Centralidades do PDDU (pontos) – referência para ZCMe/ZCMu.', 'F09', 'PDDU (centralidades); LOUOS arts. 23–24', lambda p, c: clean(p.get('desc_')) or c, ['desc_'])
    Cm['bairros'] = camada('bairros_oficiais', 'informativa', lambda p, t: clean(p.get('nome_bairr')), 'Bairros oficiais (Lei 9.278/2017).', 'F09', 'Lei 9.278/2017',
        lambda p, c: f'Bairro {c}.', ['pref_bairr'], tol=3.0)
    return Cm

FONTES = [
 {"id": "F01", "titulo": "LOUOS – Lei de Ordenamento do Uso e da Ocupação do Solo de Salvador (texto)", "lei": "Lei nº 9.148/2016", "data": "2016-09-08", "url": PDDU_URL + "louos/LOUOS-2016.pdf", "arquivo_local": "fontes/LOUOS-2016.pdf",
  "observacao": "Alterada pela LC 074/2020 e pelas Leis 9.509/2020, 9.510/2020 e 9.774/2023 (textos das alterações não obtidos – ver lacunas)."},
 {"id": "F02", "titulo": "PDDU – Plano Diretor de Desenvolvimento Urbano de Salvador (texto + Quadros 01–05 do Anexo 2)", "lei": "Lei nº 9.069/2016", "data": "2016-06-30", "url": PDDU_URL + "pddu/LEI-n.-9.069-PDDU-2016.pdf", "arquivo_local": "fontes/LEI-n.-9.069-PDDU-2016.pdf",
  "observacao": "Quadros: " + PDDU_URL + "pddu/quadros_PDDU_2016.pdf (fontes/quadros_PDDU_2016.pdf)."},
 {"id": "F03", "titulo": "LOUOS – Quadros do Anexo 01 (03 dimensões de lote; 06 parâmetros de ocupação; 10 usos por zona; 11 B vagas)", "lei": "Lei nº 9.148/2016, Anexo 01", "data": "2016-09-08",
  "url": PDDU_URL + "louos/Quadro-06-Par%C3%A2metros-de-Ocupa%C3%A7%C3%A3o-do-Solo.pdf", "arquivo_local": "fontes/Quadro-06-Parâmetros-de-Ocupação-do-Solo.pdf",
  "observacao": "Demais quadros no mesmo diretório (Quadro-03-Dimensões-mínimas-de-Lote.pdf, Quadro-10-Usos-Permitidos-por-zonas-de-uso.pdf, Quadro-11-B-Condições-de-instalação-por-subcategoria-de-uso.pdf), listados em https://pddu.salvador.ba.gov.br/louos-2016."},
 {"id": "F04", "titulo": "LOUOS – Mapa 01A Zonas de Uso (Anexo 02), alterado pela LC 074/2020, Leis 9.509/2020 e 9.510/2020 e ATAs CNLU 04/2022 e 12/2022", "lei": "Lei nº 9.148/2016, Anexo 02, Mapa 01A", "data": "2022", "url": MAPA01A_URL,
  "arquivo_local": "fontes/LOUOS_MAPA_01A_ZONAS-DE-USO_MODIFICADO_CNLU_ESALVADOR_compressed.pdf"},
 {"id": "F05", "titulo": "LOUOS – Mapa 03 Gabarito de Altura Máxima na Área de Borda Marítima (Anexo 02)", "lei": "Lei nº 9.148/2016, Anexo 02, Mapa 03", "data": "2016-09-08", "url": MAPA03_URL, "arquivo_local": "fontes/SSA_LOUOS_03_GABARITO-ABM.compressed.pdf"},
 {"id": "F06", "titulo": "LOUOS – Mapa 01B ZEIS (alterado pela ATA 12/2022 CNLU)", "lei": "Lei nº 9.148/2016, Anexo 02, Mapa 01B", "data": "2022", "url": PDDU_URL + "louos/SSA_LOUOS_01B_ZEIS_MODIFICADO_PROCESSO_ATA_N_12_2022_CNLU_compressed.pdf",
  "arquivo_local": "fontes/SSA_LOUOS_01B_ZEIS_MODIFICADO_PROCESSO_ATA_N_12_2022_CNLU_compressed.pdf"},
 {"id": "F07", "titulo": "PDDU – Mapas 01 (Macrozoneamento), 03 (ZEIS) e 08 (Operações Urbanas) do Anexo 03", "lei": "Lei nº 9.069/2016, Anexo 03", "data": "2016-06-30", "url": PDDU_URL + "pddu/PDDU_MAPA_01_MACROZONEAMENTO.pdf", "arquivo_local": "fontes/PDDU_MAPA_01_MACROZONEAMENTO.pdf",
  "observacao": "Também PDDU_MAPA_03_ZEIS.pdf e PDDU_MAPA_08_OPERACOES_URBANAS.pdf no mesmo diretório."},
 {"id": "F08", "titulo": "Portal oficial PDDU/LOUOS da Prefeitura de Salvador (leis, quadros e mapas)", "lei": "Prefeitura Municipal do Salvador – SEDUR", "data": HOJE, "url": "https://pddu.salvador.ba.gov.br/louos-2016",
  "observacao": "Lei 7.719/2009 (MCMV municipal) e alterações citadas apenas pelo título; texto não acessado."},
 {"id": "F09", "titulo": "GeoSalvador – serviços ArcGIS REST públicos (Mapa_LOUOS_WFL1, PDDU_2016, bens_tombados_a, idesh_risco_a, bairros)", "lei": "Prefeitura Municipal do Salvador – camadas oficiais", "data": HOJE, "url": f"{SRV}/Hosted/Mapa_LOUOS_WFL1/FeatureServer",
  "observacao": "O serviço com o zoneamento vetorial (LOUOS_2016_OK) exige token – não acessado. URLs por camada em geografico.camadas."},
]

def blocos():
    oo = {"resumo": "OODC sobre o potencial entre CAB e CAM, só na Macrozona de Ocupação Urbana e em zonas com CAM > CAB; na ABM só por OODC; nas demais áreas OODC ou TRANSCON; HIS atinge o CAM sem contrapartida.",
          "fonte_id": "F02", "artigo_anexo": "PDDU arts. 293–308; Quadros 03 e 04 do Anexo 2", "itens": [
     I('aplicacao', 'Onde se aplica', None, None, 'F02', 'PDDU art. 293 §§1º–2º', None, 'texto', texto_original='Potencial adicional = potencial utilizado (≤ CAM) − potencial básico (CAB), nas zonas com CAM > CAB contidas nas macroáreas da Macrozona de Ocupação Urbana.'),
     I('formula', 'Contrapartida financeira', None, 'R$', 'F02', 'PDDU art. 295', 'AT área do terreno; CAE CA utilizado; VUP valor unitário padrão do IPTU (SEFAZ); FDU = FDUE 0–1,2 (Quadro 03); FS 0–1 (Quadro 04) – ver camada macroareas.', 'formula', formula='CF = [AT × (CAE − CAB) ÷ CAB] × VUP × FDU × FS'),
     I('abm', 'Área de Borda Marítima', None, None, 'F02', 'PDDU art. 293 §3º', None, 'texto', texto_original='Nas ABM, o potencial adicional até o CAM só pode ser exercido mediante a Outorga Onerosa do Direito de Construir.'),
     I('transcon_alternativa', 'OODC ou TRANSCON', None, None, 'F02', 'PDDU art. 293 §4º', None, 'texto', texto_original='Nas demais áreas, OODC ou TRANSCON, de forma alternativa.'),
     I('limite_50_bairros', 'Limite de 50% por OODC em bairros listados', 0.5, 'fracao do potencial adicional', 'F02', 'PDDU art. 293 §5º', 'Vitória, Canela, Graça, Barra, Ondina, Candeal, Pituba e Caminho das Árvores (fora da ABM, Mapa 09): até 50% por OODC; o restante por TRANSCON.'),
     I('his_isencao', 'HIS sem contrapartida', 0, 'fator', 'F02', 'PDDU art. 293 §6º; Quadro 04 (FS = 0 para HIS)', 'HIS atinge o CAM da zona sem contrapartida financeira.'),
     I('rit_rivi', 'Avaliação de impacto quando a outorga > 50% do CAB', 0.5, 'fracao do CAB', 'F02', 'PDDU art. 294 §1º II', 'Acima de 50% do CAB: RIT (trânsito) e, quando couber, RIVI (meio ambiente/patrimônio).'),
     I('outorga_verde', 'Desconto por certificação IPTU Verde', None, 'fracao', 'F02', 'PDDU arts. 299–302 (Decreto 25.899/2015)', 'Bronze ≥ 50 pontos, Prata ≥ 70, Ouro ≥ 100 (art. 301).', 'condicional',
       condicionais=[C('Bronze', 'unico', 0.25), C('Prata', 'unico', 0.30), C('Ouro', 'unico', 0.40)]),
     I('alteracao_uso', 'Outorga onerosa de alteração de uso', None, None, 'F02', 'PDDU art. 296', None, 'texto', texto_original='Somente no âmbito de Operação Urbana Consorciada.'),
     I('transcon', 'Transferência do Direito de Construir (TRANSCON)', None, None, 'F02', 'PDDU arts. 297–308; LOUOS art. 110 (caso ZCMe-CA)', 'Imóveis cedentes de interesse público (patrimônio, ambiental, espaços abertos etc.); certidão de potencial construtivo; recepção até o CAM; FDUE também se aplica às cotas de TRANSCON (Quadro 03, nota 3).', 'texto',
       texto_original='Utilização do direito de construir pelos critérios dos arts. 304–307 do PDDU (proporcionalidade de VUP/CAB entre cedente e receptor, até o CAM). Caso específico da LOUOS art. 110: retrofit de imóvel tombado na ZCMe-CA que não atinja o CAM (4) pode transferir a diferença para a própria ZCMe-CA ou para ZCMe-1/02 e ZCMe-2.'),
     I('pagamento', 'Parcelamento da contrapartida', 18, 'meses (máximo)', 'F02', 'PDDU art. 295 §§2º–3º', 'Parcelas mensais em até 18 meses, juros de 1% a.m.; habite-se condicionado à quitação.'),
     I('gabarito_abm_contrapartida', 'Superação do gabarito na ABM (regeneração urbana)', 0.5, 'fracao do gabarito do Mapa 03', 'F01', 'LOUOS art. 111', 'Até +50% do gabarito na ABM para substituição de edificações, ouvida a CNLU, mediante contraprestação Cp = 0,05 × [(At × VUP × CAB) ÷ H] × (H − GAB); teto 75 m.')]}
    zh = {"resumo": "ZEIS-1 a 5 são zonas base (Mapa 01A/01B). Terrenos > 1.500 m² nas ZEIS 1–4: mínimo de 50% (ZEIS-3: 60%) da área construída em HIS-1; HMP + não residencial ≤ 20%. Na ZEIS só EHIS/EHMP (sem R3 de mercado).",
          "fonte_id": "F02", "artigo_anexo": "PDDU arts. 63, 166–169, Quadro 02; LOUOS arts. 21–22, 49–50, 75, 121–122", "itens": [
     I('his_definicao', 'HIS – renda familiar máxima', 4728, 'R$/mês (valor de 2016, corrigido anualmente pelo IPCA)', 'F02', 'PDDU art. 63 I e §2º', 'HIS-1 até R$ 2.364; HIS-2 de R$ 2.364 a R$ 4.728 (art. 63 §3º); promovida pelo Poder Público ou conveniada.'),
     I('hmp_definicao', 'HMP – faixa de renda familiar', None, 'R$/mês', 'F02', 'PDDU art. 63 II', 'Valores de 2016, corrigidos pelo IPCA.', 'faixa', faixa={"min": 4728, "max": 7880}),
     I('zeis_percentual_his1', 'Percentual mínimo de HIS-1 nas ZEIS', None, 'fracao da área construída total', 'F02', 'PDDU Quadro 02; art. 169; LOUOS art. 21', 'Terrenos > 1.500 m² (art. 169 §1º); reforma com demolição/ampliação ≥ 50% conta como edificação nova (§2º).', 'condicional',
       condicionais=[C('ZEIS-1, 2, 4 e 5', 'unico', 0.5), C('ZEIS-3', 'unico', 0.6)]),
     I('zeis_hmp_nr_max', 'HMP + não residencial nas ZEIS', 0.2, 'fracao da área construída total', 'F02', 'PDDU Quadro 02'),
     I('ehis_lote_minimo', 'Lote mínimo de EHIS/EHMP', 125, 'm2', 'F01', 'LOUOS art. 49 §3º', 'Em qualquer zona; loteamento de interesse social L2 e regularização podem ser menores (§2º; Quadro 03: ZEIS 64 m² e 4 m).'),
     I('ehis_lote_maximo', 'Lote/gleba máximo para EHIS/EHMP', 50000, 'm2', 'F01', 'LOUOS art. 50 §2º'),
     I('ehis_parametros', 'Parâmetros de EHIS/EHMP', None, None, 'F01', 'LOUOS art. 122', None, 'texto', texto_original='EHIS/EHMP respeitam o CAM e o gabarito da zona; nas ZEIS até 20% de área não residencial é não computável (§2º).'),
     I('ehis_vagas', 'Vagas de EHIS', 0.5, 'vagas/UH', 'F03', 'Quadro 11 B, obs. (b)', '1 vaga para cada 2 UH.'),
     I('urb2_vagas', 'Vagas na urbanização integrada de interesse social (URB 2)', 0.5, 'fracao do Quadro 11 B', 'F01', 'LOUOS art. 75 V–VII', 'Mínimo 50% do Quadro 11 B; EHIS/EHMP com uso misto nR1; nR ≥ 5% da área líquida.'),
     I('his_oodc', 'OODC para HIS', 0, 'fator', 'F02', 'PDDU art. 293 §6º; Quadro 04', 'HIS chega ao CAM sem contrapartida; FS reduzido para unidades de 50–100 m².'),
     I('abm_his_15m', 'HIS de programa governamental na ABM', 15, 'm', 'F01', 'LOUOS art. 85 §7º', 'Trechos 1 e 2 da ABM: até 15 m sem contrapartida.'),
     I('mcmv_lei_municipal', 'Lei municipal do MCMV', None, None, 'F08', 'Lei 7.719/2009 (alterada pela Lei 9.562/2021)', 'Texto não obtido (portal SEDUR bloqueia o acesso automatizado) – ver lacunas.', 'sem_dado')]}
    op = {"resumo": "EIV/RIV, RIT/PGT, terreno em mais de uma zona, lote máximo, ABM, aeroporto e incentivos.", "fonte_id": "F01", "artigo_anexo": "LOUOS", "itens": [
     I('eiv_egiv', 'EIV/RIV – Empreendimentos Geradores de Impacto de Vizinhança', 40000, 'm2 de área construída total', 'F01', 'LOUOS arts. 137–138', 'Residencial > 40.000 m² ou > 600 vagas; misto > 40.000 m²; urbanização integrada ≥ 1.500 UH; parcelamento > 30 ha; raio de análise ≥ 500 m.'),
     I('pgt_rit', 'Polo Gerador de Tráfego (RIT)', 400, 'vagas (residencial)', 'F01', 'LOUOS art. 135 I e §3º', 'Residencial com 400 vagas ou mais exige RIT.'),
     I('terreno_duas_zonas', 'Terreno em mais de uma zona', None, None, 'F01', 'LOUOS art. 18 §2º', None, 'texto', texto_original='Prevalece a zona que abrange a maior porção do terreno.'),
     I('lote_maximo', 'Lote máximo', 20000, 'm2', 'F01', 'LOUOS art. 50', 'Frente máxima 200 m; R2-02, R3-02, R3-03, EHIS e EHMP até 50.000 m²; quadra máxima 20.000 m² e 450 m (art. 51).'),
     I('abm_recuos', 'Recuos na ABM (trechos 4–12, H > 12 m)', None, 'm', 'F01', 'LOUOS art. 105', 'Trechos 1–3 usam recuos da zona; até 12 m: frente 5 m e laterais 2 m.', 'condicional',
       condicionais=[C('frontal', 'formula', None, formula='5 + 0,6 × (H − 6) ÷ 3'), C('lateral', 'formula', None, formula='1,5 + 0,3 × (H − 12) ÷ 3'), C('fundos', 'unico', 3.0)]),
     I('abm_estudo_solar', 'Estudo solar na Borda Atlântica', None, None, 'F01', 'LOUOS art. 102', None, 'texto', texto_original='Trechos 6–12: faixas de 0–60, 60–90, 90–120 m e de 120 m até o limite da ABM; altura limitada por estudo de sombreamento da praia; na BTS (trechos 1–5) aplica-se a Lei 3.289/1983 (APR/área contígua).'),
     I('aeroporto', 'Zona de proteção do Aeroporto', None, None, 'F01', 'LOUOS arts. 40 pú e 104', 'Restrições do COMAER prevalecem quando mais restritivas – sem vetor público (ver lacunas).', 'sem_dado'),
     I('fachada_ativa', 'Incentivos – fachada ativa e fruição pública', None, None, 'F01', 'LOUOS arts. 106–107', None, 'texto', texto_original='Fachada ativa: área do térreo das unidades com fachada ativa não computável até 70% da área do lote em ZCMe/ZCLMe/ZCMu/ZCLMu e 30% nas demais zonas (art. 106). Fruição pública: acréscimo gratuito de potencial, respeitado o CAM, de 100% (áreas livres externas contínuas) ou 70% (áreas internas) em ZCMe/ZCLMe/ZCMu/ZCLMu e 50% nas demais zonas (art. 107).'),
     I('ip_reducao', 'Redução do índice de permeabilidade', 0.5, 'fracao do IP', 'F01', 'LOUOS art. 84 §3º', 'IP mínimo do Quadro 06 reduzido à metade para empreendimento que capte 100% da água pluvial do telhado. Pelo menos 50% da área permeável exigida em solo natural/semipermeável (art. 84, I).')]}
    return oo, zh, op

def main():
    zonas, stats = build_zonas()
    camadas = build_camadas()
    oo, zh, op = blocos()
    doc = {
     "schema_versao": "1.1", "municipio": "Salvador", "uf": "BA", "slug": "salvador-ba", "codigo_ibge": "2927408", "data_levantamento": HOJE,
     "centro_mapa": {"lat": -12.9714, "lon": -38.4714, "zoom": 11},
     "orgao_confirmacao": "SEDUR – Secretaria Municipal de Desenvolvimento Urbano de Salvador (consulta prévia/alvará); CNLU – Comissão Normativa da Legislação Urbanística",
     "marco_legal_vigente": ("Plano diretor: PDDU – Lei 9.069/2016 (CA mínimo/básico/máximo no Quadro 01 do Anexo 2; HIS/HMP art. 63; ZEIS arts. 166–169 e Quadro 02; OODC arts. 293–296; TRANSCON arts. 297–308; FDUE/FS Quadros 03–04; OUC arts. 325–328). "
        "Uso e ocupação: LOUOS – Lei 9.148/2016 (Quadros 03, 06, 10 e 11 B do Anexo 01; Mapas 01A, 01B, 01C, 02B, 02C, 03 e 04 do Anexo 02), alterada pela LC 074/2020 e pelas Leis 9.509/2020, 9.510/2020 e 9.774/2023, "
        "com alterações de mapa pelas ATAs CNLU 04/2022 e 12/2022 (Mapa 01A publicado). Parâmetros de ocupação no Quadro 06 (art. 79); gabarito só na Área de Borda Marítima (art. 102, Mapa 03). "
        "EIV/RIV para EGIV (LOUOS arts. 137–138); RIT para PGT (art. 135). MCMV municipal: Lei 7.719/2009 (alterada pela Lei 9.562/2021) – texto não verificado. "
        "Revisão do PDDU/LOUOS em discussão (minuta/audiências públicas), sem vigência em 27/10/2026."),
     "fontes": FONTES,
     "macrozonas": [
        {"codigo": "MZOU", "nome": "Macrozona de Ocupação Urbana", "descricao": "PDDU art. 131; OODC/TRANSCON aplicáveis (art. 293 §2º). Geometria na camada 'macrozonas'.", "parametros": {"oodc_aplicavel": P(1, 'booleano (1 = sim)', 'F02', 'PDDU art. 293 §2º')}},
        {"codigo": "MZCA", "nome": "Macrozona de Conservação Ambiental", "descricao": "PDDU; não se aplica OODC (Quadro 03 do Anexo 2, nota 2). Geometria na camada 'macrozonas'.", "parametros": {"oodc_aplicavel": P(0, 'booleano (1 = sim)', 'F02', 'PDDU Quadro 03 do Anexo 2, nota 2')}},
     ] + [{"codigo": c, "nome": MACRO_NOME[c], "descricao": "Macroárea da Macrozona de Ocupação Urbana (PDDU Mapa 01A do Anexo 03). Geometria na camada 'macroareas'.", "parametros": macro_params(c)} for c in ('MEU', 'MIM', 'MUC', 'MRBTS', 'MRBA')],
     "macrozonas_observacao": "Macrozonas/macroáreas não alteram os índices das zonas; definem a aplicabilidade da OODC e os fatores FDUE (Quadro 03) e FS (Quadro 04) da contrapartida (PDDU art. 295). Setores da MIM (Mapa 01B do PDDU) não vetorizados.",
     "zonas": zonas, "camadas_complementares": camadas, "outorga_onerosa": oo, "zeis_his": zh, "outros_parametros": op,
     "resumo_mcmv": [
        "Zonas mais favoráveis a multifamiliar MCMV/HIS (EHIS): ZCMe (CAM 4,0; em ZCMe-1/02, 1/03 e 2 o CAM 4 exige quota ≤ 25 m² de terreno/UH, ou seja ≥ 400 UH/ha, e no máximo 2 vagas/UH), ZCLMe (CAM 4,0 em lotes com frente para BR-324, Av. 29 de Março e BA-526/535), ZPR-3, ZCMu-2, ZCLMu e ZEIS-1/2/3 (CAM 3,0). EHIS é permitido em todas as zonas do Quadro 10, exceto ZPR-1 e ZIT; R3-02 (conjunto ≤ 400 UH) não é permitido em ZPR-1, ZEIS, ZDE-1, ZUSI e ZIT.",
        "OODC: HIS atinge o CAM sem contrapartida (PDDU art. 293 §6º; FS = 0); unidades de 50–100 m² têm FS reduzido (0,2–0,8 conforme macroárea); nas ZCMe, isenção para HIS e 50% de redução para HMP ≤ 70 m². Não há OODC na Macrozona de Conservação Ambiental.",
        "Vagas: EHIS 1 vaga/2 UH (Quadro 11 B, b); unidades < 50 m² isentas; URB 2 com 50% do quadro (art. 75 V). RIT a partir de 400 vagas; EIV/RIV acima de 40.000 m² construídos ou 600 vagas, ou urbanização integrada ≥ 1.500 UH.",
        "Lote: EHIS/EHMP admitem lote de 125 m² em qualquer zona e glebas de até 50.000 m² (arts. 49 §3º e 50 §2º). TO por área do terreno em ZPR/ZEIS (≥ 250 m²: 0,50); recuos progressivos acima de 12 m de altura (arts. 87 e 90).",
        "ZEIS: terrenos > 1.500 m² nas ZEIS 1–4 exigem ≥ 50% da área construída em HIS-1 (ZEIS-3: 60%); R3 de mercado proibido; ZEIS lindeira a ZCL pode usar parâmetros da ZCL (art. 22).",
        "Gatilhos de custo/prazo: ABM (gabarito 6–75 m, estudo solar na orla atlântica, OODC obrigatória; EHIS governamental até 15 m nos trechos 1–2); entorno de 200 m de bens tombados; APRN/APCP/UC/Mata Atlântica; setores de risco; zona de proteção do aeroporto (COMAER); análise da CNLU em ZUE/ZPAM.",
        "Atenção: a Lei 9.774/2023 alterou a LOUOS e não foi possível verificar se o Mapa 01A publicado (até a ATA 12/2022) a incorpora; confirmar o zoneamento do lote na SEDUR (consulta prévia)."],
     "geografico": {
        "descricao": ("Zoneamento base VETORIZADO do PDF oficial do Mapa 01A da LOUOS (o vetor oficial do zoneamento no GeoSalvador exige token). O PDF é vetorial: os polígonos foram extraídos com PyMuPDF, "
                      "a sobreposição resolvida pela ordem de desenho (o desenhado por último prevalece) e o conjunto georreferenciado por transformação afim ajustada a pares de centroides de ZEIS (PDF × vetor oficial): "
                      "resíduo mediano 0,09 m, RMS 5,1 m, IoU mediana 0,999. Gabarito da ABM vetorizado do raster do Mapa 03 (classificação de cor; erro 10–15 m). Demais camadas: vetores oficiais públicos do GeoSalvador. Simplificação ≤ 2–4 m (UTM 24S) e 6 casas decimais."),
        "crs": "EPSG:4326", "crs_area": "EPSG:31984", "servidor_oficial": SRV,
        "camadas": [{"nome": "zoneamento_mapa01a", "arquivo": "geo_raw/mapa01a_pdf_coords.json", "fonte_url": MAPA01A_URL, "data_download": HOJE, "oficial": False, "metodo": "digitalização aproximada de mapa oficial (extração vetorial do PDF + georreferenciamento afim)", "erro_estimado_m": 5.0},
                    {"nome": "gabarito_abm_mapa03", "arquivo": "geo_raw/mapa03_abm_gabarito.geojson", "fonte_url": MAPA03_URL, "data_download": HOJE, "oficial": False, "metodo": "digitalização aproximada de mapa oficial (classificação de cor do raster + poligonização)", "erro_estimado_m": 15.0}] +
                   [{"nome": e['tema'], "arquivo": e['arquivo'], "fonte_url": e['url'], "data_download": e['baixado_em'], "oficial": True, "metodo": "vetor oficial", "erro_estimado_m": TOL, "n_feicoes": e['n_feicoes']} for e in LOG.values() if e['tema'] != 'mapa03_abm_gabarito'],
        "regras_de_consulta": "Zona base = zona do Mapa 01A com maior área no terreno (LOUOS art. 18 §2º). Eixos ZCLMe/ZCLMu valem para lotes com frente para a via (até 50 m da linha, requer testada). ZEIS lindeira a ZCL pode usar parâmetros da ZCL (art. 22). Camadas de restrição (ABM, SAVAM, tombamento, risco, OUC) geram alertas; gabarito só na ABM.",
        "raio_divisa_m": 30, "pct_minimo_significativo": 0.5,
        "limitacoes": ["Zoneamento derivado do PDF (oficial:false); prevalecem o mapa oficial e a consulta prévia da SEDUR.",
                       f"Tipos de ZEIS por sobreposição com o vetor oficial ({stats['zeis_sobreposicao']} polígonos); {stats['zeis_proximidade']} polígono(s) sem sobreposição receberam o tipo da ZEIS oficial mais próxima.",
                       "Número das ZUE e subzonas ZCMe/ZCMu atribuídos por localização (os rótulos do mapa não são texto no PDF).",
                       "Gabarito da ABM aproximado e sem o detalhe do Centro Antigo/Barra (quadro 1:12.500 do Mapa 03).",
                       "Setores da MIM (FDUE) e bairros do limite de 50% da OODC (Mapa 09) não vetorizados."],
        "notas_tecnicas": {"pipeline": "baixar_camadas.py → extrair_pdf_mapa01a.py → georref_mapa01a.py → vetorizar_mapa03_abm.py → build_salvador.py → normalizar_cidade.py --compacto → validar_cidade.py",
            "georreferenciamento": "Transformação afim PDF(pt)→EPSG:31984 ajustada por pontos de controle; parâmetros em geo_raw/georref_mapa01a.json.",
            "cobertura": "Zonas base cobrem ~99,7% da área dos bairros oficiais; ~100 ha residuais (espelhos d'água/vias não preenchidos no PDF) ficam sem zona."}},
     "lacunas": [
        {"item": "Textos da LC 074/2020 e das Leis 9.509/2020, 9.510/2020 e 9.774/2023 (alterações da LOUOS)", "motivo": "O portal sedur.salvador.ba.gov.br/leis bloqueia o acesso automatizado (WAF 'Página Bloqueada'); não foi contornado. Não foi possível verificar se algum Quadro foi alterado nem se o Mapa 01A publicado (até a ATA 12/2022) incorpora a Lei 9.774/2023."},
        {"item": "Vetor oficial do zoneamento (LOUOS_2016_OK)", "motivo": "Serviço ArcGIS protegido por token; usada vetorização do PDF oficial (oficial:false)."},
        {"item": "Zona de proteção do Aeroporto (PBZPA/COMAER)", "motivo": "Sem vetor público municipal; norma federal (DECEA)."},
        {"item": "Decretos 23.719/2012 e 23.709/2012 (ZUSI/ZPAM nas ilhas)", "motivo": "Não localizados em fonte oficial acessível."},
        {"item": "Parâmetros de ZEM, ZUE e ZPAM (TO, permeabilidade, recuos, lote)", "motivo": "A LOUOS remete a estudos/disciplina específica e à CNLU (arts. 31–33)."},
        {"item": "Lei 7.719/2009 e Lei 9.562/2021 (MCMV municipal)", "motivo": "Texto não obtido (portal SEDUR bloqueado)."},
        {"item": "Setores da MIM (Mapa 01B do PDDU) e Mapa 09 (bairros com limite de 50% da OODC)", "motivo": "Não vetorizados nesta versão; FDUE da MIM ficou condicional por setor."},
        {"item": "Gabarito da ABM no Centro Antigo/Barra", "motivo": "No Mapa 03 essa área está num quadro de detalhe 1:12.500 fora de posição; não georreferenciado."},
        {"item": "Leis específicas de OUC", "motivo": "Não foi localizada lei específica de OUC em vigor; o vetor oficial traz OUC 01–04, mas o art. 325 do PDDU lista só OUC 1–3."},
        {"item": "Divergência do CA mínimo da ZPR-1 (0,10 na LOUOS × 0,20 no PDDU)", "motivo": "Adotado o Quadro 06 da LOUOS; confirmar na SEDUR."},
        {"item": "Valores de VUP (SEFAZ) para OODC/TRANSCON", "motivo": "Planta de valores não levantada; a fórmula está registrada."}]}
    s = json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
    open(OUT, 'w').write(s)
    print('zonas', len(zonas), collections.Counter(z['tipo'] for z in zonas), dict(stats))
    print({z['codigo']: len(z['geometria']['features']) for z in zonas})
    print('camadas', {k: len(v['features']) for k, v in camadas.items()})
    print('MB', round(len(s.encode()) / 1e6, 2))

if __name__ == '__main__':
    main()
