#!/usr/bin/env python3
"""Gera rio-de-janeiro-rj.json (padrão plataforma 1.0) a partir das camadas oficiais IPP/SMDU
baixadas em geo_raw/ (scripts/baixar_camadas.py) + transcrição dos artigos da LC 270/2024 e alterações.
Uso: python3 scripts/build_rio.py"""
import json, re, os, collections, datetime
import shapely
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from pyproj import Transformer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'geo_raw')
OUT = os.path.join(BASE, 'rio-de-janeiro-rj.json')
LOG = json.load(open(os.path.join(RAW, '_log_download.json')))
LOGD = {e['tema']: e for e in LOG}
TOL = float(os.environ.get('TOL_M', '2'))          # simplificação (m) – zonas
TOL_C = float(os.environ.get('TOL_C_M', '2'))      # simplificação (m) – camadas complementares

to_utm = Transformer.from_crs(4326, 31983, always_xy=True)
to_geo = Transformer.from_crs(31983, 4326, always_xy=True)
def _fwd(c):
    x, y = to_utm.transform(c[:, 0], c[:, 1]); c[:, 0], c[:, 1] = x, y; return c
def _inv(c):
    x, y = to_geo.transform(c[:, 0], c[:, 1]); c[:, 0], c[:, 1] = x, y; return c

def geom_simpl(g, tol):
    if g is None: return None
    try:
        s = shape(g)
    except Exception:
        return None
    if s.is_empty: return None
    if not s.is_valid: s = shapely.make_valid(s)
    u = shapely.transform(s, _fwd)
    u = u.simplify(tol, preserve_topology=True)
    if u.is_empty: return None
    gg = shapely.transform(u, _inv)
    gg = shapely.set_precision(gg, 1e-6)
    if gg.is_empty: return None
    m = mapping(gg)
    return json.loads(json.dumps(m), parse_float=lambda v: round(float(v), 6))

def load(t): return json.load(open(os.path.join(RAW, f'{t}.geojson')))['features']
def url(t): return LOGD[t]['url'] if t in LOGD else None
def clean(v):
    if v is None: return None
    v = str(v).strip()
    return None if v in ('', ' ', 'None', '`nome`') else v

NUM = re.compile(r'^\s*(\d+(?:[.,]\d+)?)')
def num(v):
    v = clean(v)
    if not v: return None
    m = NUM.match(v)
    return float(m.group(1).replace(',', '.')) if m else None

HOJE = '2026-10-27'
LC270 = 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/a99e317a9cfec383032568620071f5d2/0274835ddbc09b5303258aa700487674?OpenDocument'
SRV = 'https://pgeo3.rio.rj.gov.br/arcgis/rest/services'
FONTES = [
 {"id": "F01", "titulo": "Lei Complementar nº 270, de 16/01/2024 – Plano Diretor de Desenvolvimento Urbano Sustentável (inclui zoneamento/LUOS: Título V, Anexos XV, XVII, XVIII, XX, XXI, XXII, XXV), republicada após derrubada de vetos (14/03/2024)", "lei": "LC 270/2024", "data": "2024-01-16", "url": LC270},
 {"id": "F02", "titulo": "IPP/SMDU – Zoneamento urbano vigente (Legislação Bairro a Bairro): camada 0 Zoneamento (zona/subzona por AP, com CAB, CAM, TO, lote, testada, gabarito, afastamento, ICS) e camada 1 Macrozonas", "lei": "LC 270/2024 e alterações (transcrição oficial do Anexo XXI em vetor)", "data": HOJE, "url": f"{SRV}/Urbanismo/LBB_Zoneamento_urbano_vigente/MapServer"},
 {"id": "F03", "titulo": "Lei Complementar nº 274, de 17/07/2024 – altera a LC 270/2024 (arts. 5–14, 17–23, 26 e 38 revogados pela LC 281/2025)", "lei": "LC 274/2024", "data": "2024-07-17", "url": "https://aplicnt.camara.rj.gov.br/apl/Legislativos/contlei.nsf/66ff1c35b8d68ddd032578690069dda8/d57750a2ebbaaae003258b5d007275f3?OpenDocument"},
 {"id": "F04", "titulo": "Lei Complementar nº 281, de 30/05/2025 – altera a LC 270/2024 e LC 274/2024", "lei": "LC 281/2025", "data": "2025-05-30", "url": "https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C2812025.html"},
 {"id": "F05", "titulo": "Lei Complementar nº 291, de 01/12/2025 – altera a LC 270/2024 (inclui Anexo XVII – Fator de Interesse Social/Incentivo)", "lei": "LC 291/2025", "data": "2025-12-01", "url": "https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C2912025.html"},
 {"id": "F06", "titulo": "Lei Complementar nº 301, de 09/07/2026 – institui a AEIU Praça Onze Maravilha; altera LC 97/2009, LC 229/2021, LC 232/2021, LC 270/2024 (Anexo XXI – AP 2.2) e LC 281/2025", "lei": "LC 301/2026", "data": "2026-07-09", "url": "https://desenvolvimentourbano.prefeitura.rio/praca-onze-maravilha/"},
 {"id": "F07", "titulo": "Lei Complementar nº 229, de 14/07/2021 – Programa Reviver Centro (Operação Interligada)", "lei": "LC 229/2021", "data": "2021-07-14", "url": "https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C2292021.html"},
 {"id": "F08", "titulo": "Lei Complementar nº 101, de 23/11/2009 – Operação Urbana Consorciada da Região do Porto do Rio (Porto Maravilha, CEPAC)", "lei": "LC 101/2009", "data": "2009-11-23", "url": "https://e.camara.rj.gov.br/Arquivo/Documents/legislacao/html/C1012009.html"},
 {"id": "F09", "titulo": "Decreto nº 56.561, de 05/08/2025 – enquadramento das atividades econômicas (CNAE) nas categorias de uso da LC 270/2024 por AP", "lei": "Decreto 56.561/2025", "data": "2025-08-05", "url": "https://desenvolvimentourbano.prefeitura.rio/wp-content/uploads/sites/52/2025/08/Decreto-Municipal-No.-56561-de-05-08-2025.pdf"},
 {"id": "F10", "titulo": "IPP/SMDU – Operações urbanas e Operações Interligadas (Porto Maravilha, Reviver Centro, Praça Onze, OUCs Autódromo/Guaratiba, São Januário, Legado Olímpico, Inhoaíba, PNM Barra)", "lei": "LC 101/2009, LC 229/2021, LC 301/2026, LC 133/2013, LC 258/2022, LC 272/2024, LC 273/2024, LC 284/2025", "data": HOJE, "url": url('operacoes_urbanas')},
 {"id": "F11", "titulo": "IPP/SMDU – Áreas de Especial Interesse Social (AEIS)", "lei": "leis/decretos de cada AEIS (campo legislacao)", "data": HOJE, "url": url('aeis')},
 {"id": "F12", "titulo": "IPP/SMDU – camadas Legislação Bairro a Bairro: SMD, Coeficiente de Adensamento Q, Gabarito (Anexo XXI), Gabarito específico, APAC, APE/AEBT, AEI, APP, Áreas protegidas, Zoneamento ambiental, CPA/PPA, Corredor Cultural, Distritos/Polos, Setores/Subsetores, Macrozonas IPTU progressivo", "lei": "LC 270/2024 e normas de proteção (campo legislacao de cada feição)", "data": HOJE, "url": SRV},
 {"id": "F13", "titulo": "ArcGIS Online – item 'Zoneamento urbano vigente' (owner PrefeituraRio): camadas da LC 270/2024 de caráter informativo; uso com crédito à SMDU", "lei": "-", "data": HOJE, "url": "https://www.arcgis.com/home/item.html?id=23de66d35c394fc89a5c5bca844373b4"},
 {"id": "F14", "titulo": "Fundação GEO-RIO/IPP – Suscetibilidade a deslizamentos (MapServer raster, não vetorizado)", "lei": "-", "data": HOJE, "url": f"{SRV}/Geotecnia/Suscetibilidade_a_deslizamentos/MapServer"},
]

def P(valor, fonte='F02', art='LC 270/2024, Anexo XXI (tabela da AP) – vetor IPP/SMDU', obs=None, unidade=None):
    d = {"valor": valor, "fonte_id": fonte, "artigo_anexo": art}
    if unidade: d["unidade"] = unidade
    if obs: d["observacao"] = obs
    return d

# ---------------------------------------------------------------- usos por família (art. 334 + 338)
def usos_familia(sig):
    f = sig.split()[0] if sig else ''
    A = 'LC 270/2024 art. 334 (conceito da zona) e art. 338; distribuição detalhada no Anexo XVIII; atividades por CNAE no Dec. 56.561/2025'
    if f.startswith('ZRU'):
        return P('Residencial I e II (uni/bifamiliar e grupamentos/vila); multifamiliar (Residencial III) NÃO permitido. ' + ('ZRU1: serviços compatíveis.' if f == 'ZRU1' else 'ZRU2: atividades não residenciais compatíveis.'), 'F01', A, 'Multifamiliar: NÃO. LC 274/2024 art. 5º previa reconversão p/ multifamiliar mediante contrapartida, mas foi revogado pela LC 281/2025.')
    if f.startswith('ZRM'):
        extra = {'ZRM1': 'serviços compatíveis', 'ZRM2': 'comércio e serviços de apoio ao uso residencial', 'ZRM3': 'usos não residenciais diversificados'}.get(f, '')
        return P(f'Residencial multifamiliar predominante (Residencial III permitido, edificação única ou grupamento); {extra}. ICS máx {"0,4" if f=="ZRM3" else "0,3"} do CAM para não residencial (art. 367).', 'F01', A, 'Multifamiliar: SIM.')
    if f == 'ZCC': return P('Comércio e serviços metropolitanos; incentivada maior incidência do uso residencial e misto.', 'F01', A, 'Multifamiliar: SIM (incentivado).')
    if f == 'ZUM': return P('Residencial, comercial, de serviços e industrial sem predominância.', 'F01', A, 'Multifamiliar: SIM.')
    if f == 'ZCS': return P('Predominância de comércio e serviços de alcance regional/municipal, junto a eixos de transporte; uso misto admitido em todas as zonas (art. 338 §3º).', 'F01', A, 'Multifamiliar: conferir Anexo XVIII (o conceito do art. 334 não o veda; art. 392 prevê edificações residenciais multifamiliares em ZCS na AP3).')
    if f == 'ZUPI': return P('Indústrias sem incômodo, com convivência com os demais usos, inclusive o residencial.', 'F01', A, 'Residencial admitido pelo conceito; categoria multifamiliar: conferir Anexo XVIII.')
    if f == 'ZEI': return P('Indústrias de impacto significativo; comércio/serviços complementares; uso residencial NÃO permitido.', 'F01', A, 'Multifamiliar: NÃO.')
    if f == 'ZDM': return P('Setor industrial e logístico de alcance metropolitano, podendo conviver com os demais usos urbanos.', 'F01', A, 'Multifamiliar: conferir Anexo XVIII.')
    if f.startswith('ZEIS'): return P('Predominantemente moradia (comunidades consolidadas/favelas); usos complementares não poluentes (art. 383).', 'F01', 'LC 270/2024 arts. 334 X, 380–385', 'Parâmetros específicos por norma do Executivo; até lá, máx. 2 pavimentos (art. 384).')
    if f == 'ZPP': return P('Plano Piloto da Baixada de Jacarepaguá (Dec. 3.046/1981 por subzona); sem restrição ao uso residencial nas categorias construtivas permitidas no local (art. 338 §10).', 'F01', 'LC 270/2024 arts. 334 XI e 338 §10; Dec. 3.046/1981', 'Multifamiliar: depende da subzona do Dec. 3.046/1981.')
    if f.startswith('ZCA1'): return P('Proteção integral: só atividades de apoio, proteção, controle e gestão ambiental.', 'F01', 'LC 270/2024 arts. 334 I a, 387', 'Multifamiliar: NÃO.')
    if f.startswith('ZCA2'): return P('Ocupação de baixa densidade compatível com a preservação ambiental; sem loteamento particular (art. 389).', 'F01', 'LC 270/2024 arts. 334 I b, 388–390', 'Multifamiliar: improvável/conferir Anexo XVIII.')
    if f == 'ZA': return P('Atividades agropecuárias e extrativistas e de apoio.', 'F01', 'LC 270/2024 art. 334 II', 'Multifamiliar: conferir Anexo XVIII.')
    if f == 'ZOE': return P('Áreas sob jurisdição pública/concessão com regime específico.', 'F01', 'LC 270/2024 art. 334 XII', None)
    if f == 'ZFU': return P('Zona Franca Urbanística (Av. Brasil, Dutra, Missões): requalificação urbana e ocupação vertical; térreo integrado ao espaço público.', 'F01', 'LC 270/2024 arts. 334 XIII e 391', 'Multifamiliar: conferir Anexo XVIII.')
    if f == 'ZEITE': return P('Extração mineral existente e atividades de baixo impacto associadas; parâmetros após encerramento.', 'F01', 'LC 270/2024 art. 334 XIV', 'Multifamiliar: NÃO (até regime específico).')
    return None

NOME_FAM = {'ZCA1': 'Zona de Conservação Ambiental 1', 'ZCA2': 'Zona de Conservação Ambiental 2', 'ZA': 'Zona Agrícola', 'ZRU1': 'Zona Residencial Unifamiliar 1', 'ZRU2': 'Zona Residencial Unifamiliar 2', 'ZRM1': 'Zona Residencial Multifamiliar 1', 'ZRM2': 'Zona Residencial Multifamiliar 2', 'ZRM3': 'Zona Residencial Multifamiliar 3', 'ZCS': 'Zona Comercial e de Serviços', 'ZCC': 'Zona Central da Cidade', 'ZUM': 'Zona de Uso Misto', 'ZUPI': 'Zona de Uso Predominantemente Industrial', 'ZEI': 'Zona de Uso Estritamente Industrial', 'ZDM': 'Zona de Desenvolvimento Econômico Metropolitano', 'ZEIS1': 'Zona de Especial Interesse Social 1', 'ZEIS2': 'Zona de Especial Interesse Social 2', 'ZPP': 'Zona do Plano Piloto da Baixada de Jacarepaguá', 'ZOE': 'Zona de Operações Especiais', 'ZFU': 'Zona Franca Urbanística', 'ZEITE': 'Zona de Especial Interesse Territorial Estratégico'}

OODC_AP = {
 '1': 'AP1: isenta de contrapartida da OODC durante a vigência da LC 270 (art. 110 §3º I); Porto Maravilha/Reviver Centro/Praça Onze seguem leis próprias (§4º).',
 '3': 'AP3: isenta de contrapartida da OODC durante a vigência da LC 270 (art. 110 §3º II).',
}
OODC_GERAL = ('OODC acima do CAB até o CAM (arts. 106–111). Sem cobrança para licenciamentos nos 5 primeiros anos de vigência (até jan/2029, art. 110 caput); '
              'depois, redução progressiva do potencial não oneroso: 20% (6º ano), 40% (7º), 60% (8º), 80% (9º) da diferença CAM–CAB (art. 110 §1º).')

ZFIELDS = ['legislacao', 'zona', 'subzona', 'sigla', 'ap', 'cab', 'obs_cab', 'cam', 'obs_cam', 'to_', 'obs_to', 'lote_min', 'obs_lote_min', 'testada_min', 'obs_testada_min', 'gab_afast', 'obs_gab_afast', 'gab_n_afast', 'obs_gab_n_afast', 'afast_fron', 'obs_afast_fron', 'ics', 'obs_ics', 'obs_riu', 'obs']

def txt(p, k, ok):
    a, b = clean(p.get(k)), clean(p.get(ok)) if ok else None
    return '; '.join(x for x in (a, b) if x) or None

def gab(v):
    v = clean(v)
    if not v: return None, None
    mp = re.search(r'(\d+)\s*pav', v); mm = re.search(r'(\d+(?:[.,]\d+)?)\s*m\b', v)
    return (int(mp.group(1)) if mp else None), (float(mm.group(1).replace(',', '.')) if mm else None)

def zona_params(p):
    ap = clean(p['ap']); sig = clean(p['sigla']) or ''
    art = f'LC 270/2024, Anexo XXI – tabela da AP {ap} (vetor IPP/SMDU)'
    def par(k, ok, conv=num, unidade=None, extra=None):
        t = txt(p, k, ok)
        if not t: return None
        v = conv(t) if conv else None
        o = t if (v is None or (str(t).strip() not in (str(clean(p.get(k))),))) else None
        if extra: o = (o + ' | ' if o else '') + extra
        return P(v, 'F02', art, o, unidade)
    cab = par('cab', 'obs_cab', extra='CAB = 1 salvo exceções (LC 270 arts. 103 pú e 345 §4º).')
    cam_extra = OODC_GERAL + (' ' + OODC_AP[ap] if ap in OODC_AP else '')
    cam = par('cam', 'obs_cam', extra=cam_extra)
    to = txt(p, 'to_', 'obs_to'); tov = num(to)
    to_p = P(round(tov / 100, 4) if tov is not None else None, 'F02', art, to if (tov is None or to != clean(p['to_'])) else None, 'fração da área do terreno') if to else None
    perm = None
    if tov is not None and tov <= 100:
        perm = P(round(0.2 * (1 - tov / 100), 4), 'F01', 'LC 270/2024 arts. 351–352 (SMD = 20% da área livre resultante da TO máxima)',
                 'Valor calculado = 0,20 × (1 − TO). Exceções: AP3 (15 bairros ilhas de calor) 70% da área livre mínima; isenções ZCA, ZA, ZDM/ZEI na AP3, áreas sem TO (art. 352 §§5º–6º) – ver camada smd.', 'fração da área do terreno')
    gpa, gma = gab(clean(p['gab_afast']))
    gtxt = txt(p, 'gab_afast', 'obs_gab_afast'); gntxt = txt(p, 'gab_n_afast', 'obs_gab_n_afast')
    gpav = P(gpa, 'F02', art, 'Edificações afastadas das divisas: ' + gtxt, 'pavimentos') if gtxt else None
    galt = P(gma, 'F02', art, 'Edificações afastadas das divisas: ' + gtxt, 'm') if gtxt else None
    fr = txt(p, 'afast_fron', 'obs_afast_fron')
    recuos = {"frontal": P(num(fr), 'F02', art, (fr if fr != clean(p['afast_fron']) else None) or 'Mínimo geral 3 m salvo zona/PAA/Dec. 3.046/1981 (art. 363 §1º); dispensado em vias ≤ 8 m e APAC (art. 406, red. LC 274/2024).', 'm') if fr else None,
              "lateral": P(None, 'F01', 'LC 270/2024 Título V Cap. III Seção VII; LC 198/2019 (COES)', 'Afastamentos laterais/fundos não constam da camada; seguem LC 270/COES conforme altura e tipologia (afastada x não afastada).'),
              "fundos": P(None, 'F01', 'LC 270/2024 Título V Cap. III Seção VII; LC 198/2019 (COES)', 'Idem lateral.')}
    lote = par('lote_min', 'obs_lote_min', unidade='m²'); test = par('testada_min', 'obs_testada_min', unidade='m')
    ap4_5 = ap in ('4', '5')
    vagas = P(0.25 if ap4_5 else None, 'F01',
              'LC 270/2024 art. 368 caput e §1º I',
              ('AP4 (inclusive ZPP) e AP5: 1 vaga para cada 4 unidades, EXCETO empreendimentos HIS vinculados a políticas habitacionais governamentais (seguem legislação específica). ' if ap4_5 else 'Vagas dispensadas em todo o Município exceto AP4/AP5, polos geradores de viagens (órgão de trânsito) e Paquetá (proibidas). ')
              + 'PCD, carga/descarga e recarga elétrica (LC 262/2023) conforme norma; reconversão residencial dispensa novas vagas (§3º, red. LC 274/2024).', 'vagas por unidade (1 vaga / 4 unidades)' if ap4_5 else 'vagas por unidade')
    vagas['forma'] = 'unico' if ap4_5 else 'livre'
    outros = {}
    if gntxt: outros['gabarito_nao_afastadas'] = P(gab(clean(p['gab_n_afast']))[0], 'F02', art, 'Edificações não afastadas das divisas: ' + gntxt, 'pavimentos')
    ics = txt(p, 'ics', 'obs_ics')
    if ics: outros['ics'] = P(num(ics), 'F02', art + '; art. 367', ics, 'fração do CAM (não residencial)')
    for k in ('obs_riu', 'obs'):
        if clean(p.get(k)): outros[k] = P(None, 'F02', art, clean(p[k]))
    if clean(p.get('legislacao')): outros['legislacao_camada'] = P(clean(p['legislacao']), 'F02', 'campo legislacao (6.270/2024 = LC 270/2024)')
    outros['ap'] = P(ap, 'F02', 'campo ap')
    if ap in OODC_AP: outros['oodc_isencao_ap'] = P(True, 'F01', 'LC 270/2024 art. 110 §3º', OODC_AP[ap])
    if ap == '3':
        outros['bonus_ap3_locacao_social'] = P(0.2, 'F01', 'LC 270/2024 art. 392', 'ZCS/ZUM/ZRM3 na AP3: +20% ATE se ≥20% das unidades destinadas ao Programa de Locação Social.', 'fração da ATE') if sig.split()[0] in ('ZCS', 'ZUM', 'ZRM3') else None
        if outros.get('bonus_ap3_locacao_social') is None: outros.pop('bonus_ap3_locacao_social')
    outros['ca_minimo_regra'] = P(None, 'F01', 'LC 270/2024 art. 105', 'CAMin = 50% do CAB nas Macrozonas de Estruturação Urbana, Desenvolvimento Estratégico e Controle da Ocupação (ver camada macrozonas); uni/bifamiliar isento.')
    return {
        "ca_minimo": None, "ca_basico": cab, "ca_maximo": cam, "taxa_ocupacao": to_p,
        "gabarito_altura_max_m": galt, "gabarito_pavimentos": gpav, "taxa_permeabilidade": perm,
        "recuos": recuos, "lote_minimo_m2": lote, "testada_minima_m": test,
        "usos_permitidos": usos_familia(sig), "vagas": vagas,
        "densidade": P(None, 'F01', 'LC 270/2024 art. 348 (Coeficiente de Adensamento Q)', 'Q só onde exigido (Anexo XXI/arts. 417–430); nº máx. de unidades = área do terreno / Q – ver camada q_adensamento.'),
        "outros": outros}

def categoria(fam, ca):
    def dens(c):
        if c is None: return None
        return 'baixa' if c <= 1.5 else ('media' if c <= 3 else 'alta')
    d = dens(ca); cs = f"CA máx {ca}" if ca is not None else "CA máx não numérico na camada"
    if fam.startswith('ZCA'): return 'ambiental', f'{fam}: Zona de Conservação Ambiental (art. 334 I).'
    if fam == 'ZA': return 'rural', 'ZA: Zona Agrícola (art. 334 II).'
    if fam.startswith('ZEIS'): return 'especial_interesse_social', f'{fam}: ZEIS (art. 334 X).'
    if fam in ('ZUPI', 'ZEI'): return 'industrial', f'{fam}: zona industrial (art. 334).'
    if fam == 'ZDM': return 'especial_economica', 'ZDM: desenvolvimento econômico metropolitano/logístico (art. 334).'
    if fam == 'ZOE': return 'institucional', 'ZOE: áreas sob jurisdição pública/concessões com regime específico (art. 334 XII).'
    if fam == 'ZEITE': return 'outra', 'ZEITE: extração mineral (art. 334 XIV).'
    if fam == 'ZCC': return 'centralidade', 'ZCC: Zona Central da Cidade (art. 334).'
    if fam.startswith('ZRU'): return 'residencial_baixa_densidade', f'{fam}: só uni/bifamiliar (art. 334); {cs}.'
    if d is None: d = 'media'; cs += ' – densidade assumida média (sem CA numérico)'
    if fam.startswith('ZRM'): return f'residencial_{d}_densidade', f'{fam}: multifamiliar predominante, não residencial limitado pelo ICS (art. 367); {cs}.'
    return f'mista_{d}_densidade', f'{fam}: usos diversificados (art. 334); {cs} (≤1,5 baixa, ≤3 média, >3 alta).'

def build_base():
    feats = load('zoneamento')
    grupos = collections.OrderedDict()
    sem = 0
    for f in feats:
        p = f['properties']
        if not f.get('geometry') or not clean(p.get('sigla')):
            sem += 1; continue
        key = (clean(p['sigla']), clean(p['ap']))
        sig_par = tuple(clean(p.get(k)) for k in ZFIELDS if k not in ('legislacao',))
        grupos.setdefault(key, collections.OrderedDict()).setdefault(sig_par, []).append(f)
    zonas = []
    for (sig, ap), variantes in grupos.items():
        vs = sorted(variantes.items(), key=lambda kv: -len(kv[1]))
        for i, (sp, fs) in enumerate(vs):
            codigo = f'{sig} | AP{ap}' + (f' v{i+1}' if len(vs) > 1 else '')
            p0 = fs[0]['properties']
            fam = sig.split()[0]
            nome = f"{NOME_FAM.get(fam, clean(p0['zona']) or fam)} – {sig} – AP {ap}" + (f' (variante {i+1})' if len(vs) > 1 else '')
            gfeats = []
            for f in fs:
                g = geom_simpl(f['geometry'], TOL)
                if g is None: continue
                gfeats.append({"type": "Feature", "properties": {"codigo": codigo, "nome": nome, "sigla": sig, "zona": clean(f['properties']['zona']), "subzona": clean(f['properties']['subzona']), "ap": ap, "objectid": f['properties'].get('objectid')}, "geometry": g})
            if not gfeats: continue
            obs = [f"Zona/subzona {sig} na AP {ap}: parâmetros transcritos pela SMDU/IPP (camada oficial) do Anexo XXI da LC 270/2024 e alterações."]
            if len(vs) > 1: obs.append(f'A mesma subzona tem {len(vs)} conjuntos de parâmetros na AP {ap} (variações por logradouro/trecho, cota ou norma específica); esta é a variante {i+1} ({len(fs)} polígonos).')
            if any('acrescido em 50%' in (x or '') for x in sp): obs.append('AP3: CAM pode ser acrescido em 50% ao longo dos eixos ferroviários, metroviários e de BRT e em empreendimentos de HIS (nota da tabela da AP3, Anexo XXI).')
            if fam.startswith('ZEIS'): obs.append('ZEIS: parâmetros por norma específica do Executivo (art. 381); até lá máx. 2 pavimentos (art. 384); áreas de risco não mitigável são non aedificandi (art. 381 §4º).')
            if fam == 'ZPP': obs.append('ZPP: CAM = IAA da subzona do Dec. 3.046/1981 (art. 345 §5º).')
            cat, crit = categoria(fam, num(p0.get('cam')) if num(p0.get('cam')) is not None else num(p0.get('cab')))
            zonas.append({"codigo": codigo, "nome": nome, "categoria_normalizada": cat, "categoria_criterio": crit,
                          "descricao": f"{clean(p0['zona']) or ''} {('– ' + clean(p0['subzona'])) if clean(p0['subzona']) else ''}".strip(),
                          "tipo": "base", "prioridade": 0, "regra_sobreposicao": None,
                          "parametros": zona_params(p0), "observacoes": obs,
                          "geometria": {"type": "FeatureCollection", "crs": "EPSG:4326 (lon, lat)", "fonte": url('zoneamento'), "oficial": True, "features": gfeats}})
    return zonas, sem

# ---------------------------------------------------------------- operações urbanas / AEIU
OU_LEI = {'da Região do Porto do Rio': ('F08', 'LC 101/2009 (OUC Porto Maravilha – CEPAC)'), 'Praça Onze': ('F06', 'LC 301/2026 art. 8º e Anexo III (AEIU Praça Onze Maravilha)'), 'Reviver Centro': ('F07', 'LC 229/2021 Cap. IX (Operação Interligada) c/c LC 270 art. 395 e LC 301/2026')}
def build_ou():
    feats = load('operacoes_urbanas')
    grp = collections.OrderedDict(); skip = 0
    for f in feats:
        p = f['properties']; nome = clean(p.get('nome'))
        if not nome or not f.get('geometry'): skip += 1; continue
        k = (nome, clean(p.get('tipo_op')), clean(p.get('tipo_area')), clean(p.get('setor')))
        grp.setdefault(k, []).append(f)
    zonas = []
    for (nome, top, tarea, setor), fs in grp.items():
        p = fs[0]['properties']
        fonte, art = OU_LEI.get(nome, ('F10', f"{(top or '').strip()} {nome} – legislação {clean(p.get('legislacao'))} (6.xxx = Lei Complementar; 1.xxx = Decreto)"))
        cam = num(p.get('cam')); cab = num(p.get('cab')); to = num(p.get('to_'))
        gp = num(p.get('gab_afast_pav')) or num(p.get('gab_pav')); gm = num(p.get('gab_afast_m')) or num(p.get('gab_m'))
        substitui = cam is not None and nome in ('Praça Onze', 'da Região do Porto do Rio') and tarea != 'Área Receptora'
        nm = 'Porto Maravilha' if nome == 'da Região do Porto do Rio' else re.sub(r'^(da|do|de)\s+', '', nome).strip()
        cod = f"OU {nm} | {tarea or top.strip()} | {setor or '-'}"
        curto = cod
        desc = clean(p.get('descricao')) or ''
        partes = [f"{(top or '').strip()} {nome} – {tarea or ''} {setor or ''}".strip()]
        for lab, k in (('CAB', 'cab'), ('CAB adicional', 'cab_ad'), ('CAM', 'cam'), ('CAM adicional', 'cam_ad'), ('TO %', 'to_'), ('gabarito afastadas (pav)', 'gab_afast_pav'), ('gabarito afastadas (m)', 'gab_afast_m'), ('gabarito não afastadas (pav)', 'gab_n_afast_pav'), ('gabarito (pav)', 'gab_pav'), ('gabarito (m)', 'gab_m'), ('uso adicional', 'uso_ad'), ('lote mín.', 'lote_min'), ('obs. CAM', 'obs_cam'), ('obs', 'observacao')):
            if clean(p.get(k)): partes.append(f"{lab}: {clean(p[k])}")
        alerta = ' | '.join(partes)
        if tarea == 'Área Receptora': alerta += ' | Área receptora de potencial construtivo da operação (aquisição de potencial/CEPAC/contrapartida conforme a lei da operação); fora disso valem os índices da zona base.'
        if tarea == 'Área Doadora': alerta += ' | Área doadora: potencial construtivo vinculado à operação.'
        par = {"ca_minimo": None,
               "ca_basico": P(cab, 'F10', art) if cab is not None else None,
               "ca_maximo": P(cam, 'F10', art, clean(p.get('obs_cam'))) if cam is not None else None,
               "taxa_ocupacao": P(round(to / 100, 4), 'F10', art, None, 'fração da área do terreno') if to is not None else None,
               "gabarito_altura_max_m": P(gm, 'F10', art, None, 'm') if gm else None,
               "gabarito_pavimentos": P(int(gp), 'F10', art, None, 'pavimentos') if gp else None,
               "taxa_permeabilidade": None, "recuos": None,
               "lote_minimo_m2": P(num(p.get('lote_min')), 'F10', art, clean(p.get('lote_min')), 'm²') if clean(p.get('lote_min')) else None,
               "testada_minima_m": None,
               "usos_permitidos": P('Conforme zoneamento da LC 270/2024 e suas regulamentações (LC 301/2026 art. 8º §2º)' if nome == 'Praça Onze' else (clean(p.get('uso_ad')) or 'Conforme lei da operação / zona base'), fonte, art),
               "vagas": None, "densidade": None,
               "outros": {"legislacao_camada": P(clean(p.get('legislacao')), 'F10', 'campo legislacao'), "descricao_camada": P(desc or None, 'F10', 'campo descricao') if desc else None}}
        if par['outros']['descricao_camada'] is None: par['outros'].pop('descricao_camada')
        gfeats = []
        for f in fs:
            g = geom_simpl(f['geometry'], TOL)
            if g: gfeats.append({"type": "Feature", "properties": {"codigo": cod, "nome": nome, "tipo_op": clean(f['properties'].get('tipo_op')), "tipo_area": tarea, "setor": setor, "legislacao": clean(f['properties'].get('legislacao'))}, "geometry": g})
        if not gfeats: continue
        zonas.append({"codigo": cod, "categoria_normalizada": "outra", "categoria_criterio": "Perímetro de operação urbana/AEIU (regime específico sobreposto ao zoneamento).", "nome": f"{(top or '').strip()} {nome} – {tarea or ''} {setor or ''}".replace('  ', ' ').strip(),
                      "descricao": desc[:600] if desc else f"Perímetro/setor de {(top or '').strip()} {nome}.",
                      "tipo": "sobreposta", "prioridade": 40 if substitui else 25,
                      "regra_sobreposicao": {"efeito": "substitui" if substitui else "apenas_alerta", "usa_indices_de": None, "aplica_sobre": None,
                                             "limiar_pct": 50, "requer_testada": False, "distancia_max_m": None,
                                             "fundamento": f"{art}; LC 270/2024 arts. 110 §4º, 113 e 138 (regimes específicos prevalecem sobre zonas)",
                                             "alerta": alerta,
                                             "mantem_da_base": ["usos_permitidos", "vagas", "recuos", "testada_minima_m", "taxa_permeabilidade", "densidade"] if substitui else None},
                      "parametros": par, "observacoes": [alerta],
                      "geometria": {"type": "FeatureCollection", "crs": "EPSG:4326 (lon, lat)", "fonte": url('operacoes_urbanas'), "oficial": True, "features": gfeats}})
    return zonas, skip

# ---------------------------------------------------------------- camadas complementares
def camada(tema, papel, codfun, descricao, fonte_id, artigo, alerta_fun, props_keep, params_fun=None, tol=None, dissolve=False):
    feats = load(tema); out = []; alertas = {}; params = {}
    by = collections.OrderedDict()
    for f in feats:
        if not f.get('geometry'): continue
        p = f['properties']; c = codfun(p)
        if not c: continue
        by.setdefault(c, []).append(f)
    for c, fs in by.items():
        p0 = fs[0]['properties']
        alertas[c] = alerta_fun(p0, c)
        if params_fun:
            pr = params_fun(p0, c)
            if pr: params[c] = pr
        if dissolve:
            try:
                u = unary_union([shapely.make_valid(shape(f['geometry'])) for f in fs])
                g = geom_simpl(mapping(u), tol or TOL_C)
                if g: out.append({"type": "Feature", "properties": {"codigo": c, "nome": c}, "geometry": g})
            except Exception:
                dissolve = False
            continue
        for f in fs:
            g = geom_simpl(f['geometry'], tol or TOL_C)
            if g:
                pp = {"codigo": c}
                for k in props_keep:
                    v = clean(f['properties'].get(k))
                    if v: pp[k] = v[:300]
                out.append({"type": "Feature", "properties": pp, "geometry": g})
    d = {"papel": papel, "descricao": descricao, "fonte": url(tema), "oficial": True, "fonte_id": fonte_id, "artigo_anexo": artigo,
         "parametros_por_codigo": params or None, "alerta_por_codigo": alertas, "features": out}
    return d

def j(*xs): return ' – '.join(clean(x) for x in xs if clean(x))

def build_camadas():
    C = {}
    MZ = {'Estruturação Urbana', 'Desenvolvimento Estratégico', 'Controle da Ocupação'}
    def mz_par(p, c):
        if c in MZ:
            return {"ca_minimo": {"valor": 0.5, "unidade": "× CAB (= 0,5 quando CAB = 1)", "fonte_id": "F01", "artigo_anexo": "LC 270/2024 art. 105 §1º", "observacao": "CAMin = 50% do CAB; uni/bifamiliar e imóveis de interesse ambiental isentos (§2º). Usado para parcelamento/edificação compulsórios e IPTU progressivo."}}
        return {"ca_minimo": {"valor": None, "fonte_id": "F01", "artigo_anexo": "LC 270/2024 art. 105 §1º", "observacao": "CAMin não fixado para esta macrozona."}}
    C['macrozonas'] = camada('macrozonas', 'macrozona', lambda p: clean(p.get('macrozona')),
        'Macrozonas da LC 270/2024 (art. 82; Anexo XIII). Direcionam instrumentos, CAM por AP (Anexo XV) e CAMin.', 'F02', 'LC 270/2024 arts. 82 e 105; Anexos XIII–XV',
        lambda p, c: f'Macrozona de {c} (LC 270/2024 art. 82).', [], mz_par, dissolve=True)
    C['smd_excecoes'] = camada('smd', 'restricao', lambda p: j(p.get('smd'))[:120],
        'Superfície Mínima Drenante – áreas com regra diferente da geral (20% da área livre).', 'F12', 'LC 270/2024 arts. 351–353',
        lambda p, c: f"SMD: {clean(p.get('smd'))}. {clean(p.get('obs')) or ''} {clean(p.get('obs_riu')) or ''}".strip(), ['smd', 'obs', 'legislacao'])
    C['q_adensamento'] = camada('q_parametros', 'restricao', lambda p: f"Q={clean(p.get('q'))} ({clean(p.get('obs')) or ''})",
        'Coeficiente de Adensamento Q (nº máx. de unidades = área do terreno / Q).', 'F12', 'LC 270/2024 art. 348 e artigos citados',
        lambda p, c: f"Coeficiente de Adensamento Q = {clean(p.get('q'))} m²/unidade ({clean(p.get('obs')) or ''}): nº máx. de unidades = área do terreno ÷ {clean(p.get('q'))}.", ['q', 'obs', 'legislacao'],
        lambda p, c: {"densidade": {"valor": num(p.get('q')), "unidade": "m² de terreno por unidade (Q)", "fonte_id": "F12", "artigo_anexo": f"LC 270/2024 art. 348; {clean(p.get('obs')) or ''}"}})
    C['gabarito_anexo_xxi'] = camada('gabarito', 'restricao', lambda p: f"{clean(p.get('origem')) or '-'} | af {clean(p.get('gab_af_pav')) or clean(p.get('gab_pav')) or '-'} pav",
        'Mapa de gabaritos por área (IU_Parametros_Gabarito) – gabaritos diferenciados dentro das subzonas.', 'F12', 'LC 270/2024 Anexo XXI/XXII',
        lambda p, c: 'Gabarito diferenciado (mapa de gabarito): ' + '; '.join(f"{k}={clean(p.get(k))}" for k in ('origem', 'gab_af_pav', 'gab_af_m', 'gab_naf_pav', 'gab_naf_m', 'gab_pav', 'gab_m') if clean(p.get(k))), ['origem', 'gab_af_pav', 'gab_af_m', 'gab_naf_pav', 'gab_naf_m', 'gab_pav', 'gab_m', 'ap'])
    C['gabarito_especifico'] = camada('gabarito_especifico', 'restricao', lambda p: j(p.get('tipo') or 'Gabarito específico', p.get('nome'))[:150] or 'Gabarito específico',
        'Gabaritos específicos (decretos, APAC, AEIU, PEUs, orla) que prevalecem quando mais restritivos.', 'F12', 'LC 270/2024 art. 333 §4º e normas citadas',
        lambda p, c: f"Gabarito específico: afastadas {clean(p.get('gab_af')) or '-'} ({clean(p.get('leg_af')) or ''}); não afastadas {clean(p.get('gab_naf')) or '-'} ({clean(p.get('leg_naf')) or ''}).", ['nome', 'tipo', 'gab_af', 'gab_naf', 'leg_af', 'leg_naf'])
    C['aeis'] = camada('aeis', 'restricao', lambda p: f"AEIS {clean(p.get('tipologia')) or 'SEM INFORMAÇÃO'}",
        'Áreas de Especial Interesse Social (AEIS 1/2/3 – favelas, loteamentos, vazios para HIS). Padrões especiais por norma específica de cada AEIS.', 'F11', 'LC 270/2024 arts. 138 §1º II, 139–141',
        lambda p, c: f"Terreno em {c}: Área de Especial Interesse Social – padrões urbanísticos especiais definidos na norma de cada AEIS (campo legislacao da feição); prevalecem sobre a zona (art. 138). Conferir pavimentos/TO/IAT da feição.", ['cod', 'nome', 'legislacao', 'sigla', 'pavimentos', 'tx_ocupacao', 'iat', 'coef_adensamento', 'afastamentos', 'ra'])
    C['apac'] = camada('apac', 'restricao', lambda p: j(p.get('tipo'), p.get('nome'))[:150],
        'Áreas de Proteção do Ambiente Cultural (APAC), sítios e AIC – patrimônio cultural.', 'F12', 'LC 270/2024 Título III Cap. VIII; art. 333 §4º',
        lambda p, c: f"{c}: imóvel em área de proteção cultural ({clean(p.get('orgao')) or 'órgão de patrimônio'}) – projeto sujeito a análise do órgão de tutela; gabarito/afastamento podem ser mais restritivos ({clean(p.get('legislacao')) or ''}).", ['codigo', 'nome', 'tipo', 'legislacao', 'orgao'])
    C['ape_aebt'] = camada('ape', 'restricao', lambda p: j(p.get('tipo'), p.get('nome'))[:150],
        'Áreas de Proteção do Entorno de bens tombados (APE/AEBT).', 'F12', 'LC 270/2024 Título III Cap. VIII',
        lambda p, c: f"{c}: entorno de bem tombado ({clean(p.get('orgao')) or ''}) – aprovação do órgão de patrimônio ({clean(p.get('legislacao')) or ''}).", ['codigo', 'nome', 'tipo', 'legislacao', 'orgao'])
    C['corredor_cultural'] = camada('corredor_cultural', 'restricao', lambda p: j(p.get('nome')) or 'Corredor Cultural',
        'Zona Especial do Corredor Cultural (Centro).', 'F12', 'normas do Corredor Cultural (campo legislacao)',
        lambda p, c: f"{c}: preservação/renovação controlada; estacionamento comercial proibido nas ruas do Corredor Cultural (LC 270 art. 369 §1º IV).", ['codigo', 'nome', 'legislacao'])
    C['cpa_ppa'] = camada('cpa_ppa', 'restricao', lambda p: j(p.get('tipo'), p.get('nome'))[:150],
        'CPA/PPA/ZPPA – áreas de proteção paisagística/ambiental.', 'F12', 'campo legislacao',
        lambda p, c: f"{c}: proteção paisagística/ambiental ({clean(p.get('legislacao')) or ''}).", ['codigo', 'nome', 'tipo', 'legislacao', 'orgao'])
    C['app'] = camada('app', 'restricao', lambda p: j('APP', p.get('nome')),
        'Área de Preservação Permanente demarcada pelo Município (a camada municipal tem só 1 polígono; APPs de rios, encostas >45°, topos e restingas do Código Florestal NÃO estão mapeadas aqui).', 'F12', 'LC 270/2024 arts. 7º XXI, 78, 214–215 (Seção II – APP); Lei 12.651/2012',
        lambda p, c: f"{c}: APP – non aedificandi (LC 270 art. 7º XXI e art. 78).", ['codigo', 'nome', 'legislacao'])
    C['areas_protegidas'] = camada('areas_protegidas', 'restricao', lambda p: j(p.get('tipo'), p.get('nome'))[:150],
        'Unidades de conservação, zonas de amortecimento, tombamentos ambientais, sítio Patrimônio Mundial (Paisagem Carioca).', 'F12', 'LC 270/2024 Título III Cap. VII Seção I; art. 78',
        lambda p, c: f"{c}: área protegida ({clean(p.get('orgao')) or ''}) – plano de manejo/norma de criação prevalece ({clean(p.get('legislacao')) or ''}).", ['codigo', 'nome', 'tipo', 'legislacao', 'orgao'], tol=TOL_C)
    C['zoneamento_ambiental'] = camada('zoneamento_ambiental', 'restricao', lambda p: j(p.get('sigla'), p.get('nome'))[:150],
        'Zoneamento ambiental de APAs/UCs (ZOC, ZCVS, ZPVS, ZVS...).', 'F12', 'decretos de zoneamento das UCs (campo legislacao)',
        lambda p, c: f"{c}: zoneamento de unidade de conservação – parâmetros do decreto da UC prevalecem ({clean(p.get('legislacao')) or ''}).", ['nome', 'sigla', 'tipo', 'legislacao'])
    C['aei'] = camada('aei', 'restricao', lambda p: j(p.get('tipo'), p.get('nome'))[:150],
        'Áreas de Especial Interesse (AEIU, AEIF, AEIC, AEIA, AEIT...) – regime urbanístico específico.', 'F12', 'LC 270/2024 art. 138',
        lambda p, c: f"{c}: Área de Especial Interesse – regime específico pode prevalecer sobre a zona ({clean(p.get('legislacao')) or ''}).", ['codigo', 'nome', 'tipo', 'legislacao', 'ap'])
    C['setores_subsetores'] = camada('subsetores', 'informativa', lambda p: j(p.get('legislacao'), p.get('sigla') or p.get('nome'))[:150],
        'Setores/subsetores de leis específicas (Porto Maravilha LC 101/2009, Reviver Centro LC 229/2021, LC 258/2022, Praça Onze LC 301/2026).', 'F12', 'campo legislacao',
        lambda p, c: f"Subsetor {c}.", ['sigla', 'nome', 'legislacao', 'legislacao_extenso'])
    C['distritos_polos'] = camada('distritos_polos', 'informativa', lambda p: j(p.get('tipo'), p.get('nome'))[:150],
        'Distritos, polos e quarteirões (benefícios/políticas setoriais).', 'F12', 'LC 270/2024 art. 138 §9º',
        lambda p, c: c, ['nome', 'tipo', 'legislacao'])
    C['iptu_progressivo'] = camada('iptu_progressivo', 'informativa', lambda p: f"PEUC/IPTU progressivo – {clean(p.get('macrozona'))}",
        'Áreas de aplicação de parcelamento/edificação compulsórios e IPTU progressivo.', 'F12', 'LC 270/2024 arts. 150 e seguintes (Título III Cap. IV – PEUC e IPTU progressivo)',
        lambda p, c: c, ['macrozona'], dissolve=True)
    return C

def main():
    zb, sem = build_base(); zo, skipou = build_ou()
    camadas = build_camadas()
    zonas = zb + zo
    fam = collections.Counter(z['codigo'].split('|')[0].split()[0] for z in zb)
    doc = {
     "schema_versao": "1.0", "municipio": "Rio de Janeiro", "uf": "RJ", "slug": "rio-de-janeiro-rj", "codigo_ibge": "3304557",
     "data_levantamento": HOJE, "centro_mapa": {"lat": -22.9068, "lon": -43.1729, "zoom": 11},
     "orgao_confirmacao": "SMDU – Secretaria Municipal de Desenvolvimento Urbano e Licenciamento (Consulta urbanística / Legislação Bairro a Bairro; mapas.rio.rj.gov.br)",
     "marco_legal_vigente": {
        "plano_diretor": "LC 270/2024 (PDDUS) – vigente desde 17/01/2024; o zoneamento/uso e ocupação do solo está incorporado (Título V e Anexos XVIII, XX, XXI, XXII). Alterações: LC 274/2024, LC 281/2025, LC 291/2025, LC 292/2025, LC 299/2026, LC 301/2026.",
        "zoneamento": "Zonas e subzonas por Área de Planejamento (AP1, AP2.1, AP2.2, AP3, AP4, AP5) – Anexo XXI (parâmetros) e Anexo XXII (mapas). Normas locais mantidas: Dec. 3.046/1981 (Plano Piloto Jacarepaguá/ZPP), PEUs/decretos de gabarito, APACs, LC 98/2009, LC 232/2021 (reconversão).",
        "outorga": "OODC e OO de alteração de uso: LC 270 arts. 106–116, Fórmulas 1–3 do Anexo XXV, FIS no Anexo XVII (alterado pela LC 291/2025).",
        "operacoes_urbanas": "OUC Porto Maravilha (LC 101/2009, CEPAC); Reviver Centro (LC 229/2021, Operação Interligada, reformulado pela LC 301/2026); AEIU Praça Onze Maravilha (LC 301/2026); OUCs Autódromo/Guaratiba (LC 273/2024), São Januário (LC 272/2024), Legado Olímpico (LC 284/2025), Parque Inhoaíba (LC 258/2022), PNM Barra (LC 133/2013).",
        "uso_atividades": "Dec. 56.561/2025 (CNAE por categoria de uso e AP).",
        "codigo_obras": "LC 198/2019 – Código de Obras e Edificações Simplificado (COES).",
        "zeis_his": "ZEIS 1/2 (LC 270 arts. 334 X, 380–385); AEIS 1/2/3 (arts. 138–141); HIS em grupamentos segue legislação específica (art. 371 §5º).",
        "eiv": "EIV/RIV previsto (art. 343) mas dependente de lei específica; até lá impactos avaliados pelos órgãos no licenciamento (art. 343 §2º).",
        "nota_texto": "O texto oficial da Câmara (F01) é bloqueado geograficamente para o ambiente de levantamento; os artigos foram lidos numa compilação consolidada não oficial (LegisWeb) e citados pelo número do artigo da LC 270/2024 – confirmar no texto oficial F01/DOM antes de uso decisório."},
     "fontes": FONTES,
     "macrozonas": [{"codigo": m, "nome": f"Macrozona de {m}", "descricao": "Macrozona da LC 270/2024 (art. 82; Anexo XIII); geometria na camada complementar 'macrozonas'.", "parametros": ({"ca_minimo": {"valor": 0.5, "unidade": "coeficiente", "fonte_id": "F01", "artigo_anexo": "LC 270/2024 art. 105 §1º", "observacao": "CAMin = 50% do CAB (0,5 quando CAB = 1); uni/bifamiliar isento.", "forma": "unico"}} if m in ('Estruturação Urbana', 'Desenvolvimento Estratégico', 'Controle da Ocupação') else {})} for m in ['Proteção Integral', 'Uso Sustentável', 'Controle da Ocupação', 'Requalificação Urbana', 'Estruturação Urbana', 'Desenvolvimento Estratégico', 'Redução da Vulnerabilidade']],
     "macrozonas_observacao": "Camada 'macrozonas' (papel macrozona) dissolvida por macrozona; CAM por macrozona/AP no Anexo XV, mas os coeficientes do zoneamento (Anexo XXI) prevalecem quando mais restritivos (art. 82 §4º).",
     "zonas": zonas,
     "camadas_complementares": camadas,
     "outorga_onerosa": {
        "base_legal": P('LC 270/2024 arts. 102–116; Anexo XXV (Fórmulas 1, 2, 3); Anexo XVII (FIS)', 'F01', 'arts. 106–116'),
        "cab_padrao": P(1.0, 'F01', 'art. 103 pú; art. 345 §1º I e §4º', 'CAB sempre ≤ 1; CAB < 1 em ZCA2 (0,1), ZOE A Galeão (0,6) e subzonas listadas no art. 345 §4º (AP3/AP4/AP5).'),
        "aplicacao": P('Área edificável acima de S × CAB até o CAM da zona (Anexo XXI); devida em todo o Município, inclusive onde não há CAM (limite = ATE do local). Não incide onde CAB = CAM, em reconversão/retrofit sem acréscimo acima do CAB, nem sobre áreas não computáveis (art. 347).', 'F01', 'arts. 106, 108, 109, 110 §2º, 111 §3º, 345 §3º, 347 §1º'),
        "formula": P('Fórmula 1 do Anexo XXV: CF = 0,80 × [ATE − (S × CAB)] × VUP × FIS', 'F01', 'art. 111; Anexo XXV – Fórmula 1', 'Transcrição obtida de cópia do Anexo XXV republicado (não aberto no site oficial): VUP = valor unitário do m² do IPTU × 0,3; FIS (0 a 1) do Anexo XVII (alterado pela LC 291/2025). CONFIRMAR no Anexo XXV oficial.'),
        "transicao": P('Licenciados nos 5 primeiros anos (17/01/2024–jan/2029): sem cobrança. 6º ano: potencial não oneroso reduzido em 20% da diferença CAM−CAB; 7º: 40%; 8º: 60%; 9º: 80%; depois cobrança integral.', 'F01', 'art. 110 caput e §1º'),
        "isencoes_territoriais": P('AP1 e AP3 isentas de contrapartida durante a vigência da LC 270; Porto Maravilha e Reviver Centro (e Praça Onze, LC 301/2026) seguem suas leis; áreas onde já havia cobrança de instrumento oneroso na publicação ficam fora da carência.', 'F01', 'art. 110 §§3º, 4º e 8º; art. 113 §§1º–2º'),
        "pagamento": P('Até 36 parcelas corrigidas pelo IPCA-E; licença condicionada à 1ª parcela e habite-se à quitação; pode ser convertida em obras (praças, ciclovias, HIS, drenagem...).', 'F01', 'art. 110 §§5º–6º; art. 112'),
        "destinacao": P('≥ 5% FMDU e ≥ 5% FMHIS (produção de HIS).', 'F01', 'art. 114 pú'),
        "alteracao_de_uso": P('OO de alteração de uso: uso não conforme mediante contrapartida; terrenos em mais de uma zona podem estender os usos da zona de maior hierarquia (Fórmula 2 comercial; Fórmula 3 multifamiliar em zona residencial); não se aplica em ZCA1.', 'F01', 'arts. 115–116, 336 §2º; LC 274/2024 art. 3º'),
        "tdc": P('Transferência do Direito de Construir (arts. 117–120) e Readequação do Potencial Construtivo no Lote (arts. 121–126) para imóveis tombados/preservados, interesse ambiental, PAA e direito de superfície.', 'F01', 'arts. 117–126'),
        "cepac_operacoes": P('Porto Maravilha: potencial adicional via CEPAC (LC 101/2009); Reviver Centro/Praça Onze: Operação Interligada (LC 229/2021, LC 301/2026); OUCs com áreas doadoras/receptoras (ver zonas OU …).', 'F10', 'LC 270 art. 113; leis das operações')},
     "zeis_his": {
        "zeis": P('ZEIS 1 (favelas e áreas contíguas) e ZEIS 2 (favelas acima da cota 100, em UC de uso sustentável ou em suscetibilidade média/alta a deslizamento) são zonas BASE do mapa. Parâmetros por norma específica do Executivo com participação popular, PAL/PAA (art. 381); até lá máx. 2 pavimentos (art. 384), na AP4 algumas ZEIS com 4 pav. (Anexo XXI); risco não mitigável = non aedificandi.', 'F01', 'arts. 334 X, 380–385'),
        "aeis": P('AEIS 1 (favelas, loteamentos precários, conjuntos), AEIS 2 (vazios/subutilizados com infraestrutura, para HIS), AEIS 3 (demais assentamentos de baixa renda do SABREN). AEIS existentes continuam válidas; padrões especiais por norma específica; prevalecem sobre zonas (art. 138).', 'F01', 'arts. 138 §1º II, 139–141'),
        "his_mcmv_grupamentos": P('Grupamentos de interesse social vinculados à política habitacional municipal, estadual ou federal seguem a legislação específica, salvo normas menos restritivas da LC 270.', 'F01', 'art. 371 §5º (red. LC 299/2026)'),
        "his_vagas": P('Na AP4/AP5 a exigência de 1 vaga/4 unidades não se aplica a HIS de políticas habitacionais governamentais (legislação específica); no resto do Município vagas são dispensadas.', 'F01', 'art. 368 §1º I'),
        "his_cam_ap3": P('AP3: CAM pode ser acrescido em 50% em empreendimentos de HIS e ao longo de eixos ferroviários/metroviários/BRT.', 'F02', 'Anexo XXI – tabela AP3 (nota nos campos CAM)'),
        "his_oodc": P('FIS (Fator de Interesse Social) reduz/isenta a contrapartida da OODC – valores no Anexo XVII (LC 291/2025); descumprimento da destinação = cassação + cobrança com multa de 10%.', 'F01', 'art. 111 §§1º–2º; Anexo XVII', 'Valores do FIS não lidos (anexo em imagem/PDF não acessível).'),
        "locacao_social_ap3": P('AP3 (ZCS, ZUM, ZRM3): +20% de ATE se ≥ 20% das unidades forem para Locação Social.', 'F01', 'art. 392'),
        "reviver_his": P('Edificações não afastadas destinadas a HIS não se sujeitam à LC 229/2021 (prevalece a LC 270).', 'F01', 'art. 395 §1º'),
        "areas_estrategicas_his": P('Áreas estratégicas para HIS incluem terrenos contíguos a AEIS e até 400 m de favelas.', 'F01', 'art. 18 VII'),
        "grandes_empreendimentos": P('LC 274/2024 art. 27: grupamentos com ≥ 500 unidades doam lote e equipamento (escola), +1 a cada 1.000 UH adicionais – conferir vigência (LC 281/2025 revogou outros artigos da LC 274, não este).', 'F03', 'LC 274/2024 art. 27')},
     "outros_parametros": {
        "eiv": P('EIV/RIV depende de lei específica; até lá impactos avaliados pelos órgãos no licenciamento ordinário; Anexo XIX classifica impactos por uso; polos geradores de viagens têm vagas definidas pelo órgão de trânsito.', 'F01', 'arts. 343, 339 §4º, 368 §1º II'),
        "terreno_mais_de_uma_zona": P('Índices calculados por área de cada zona e somados, aplicáveis livremente no terreno, respeitados usos e gabarito de cada zona; acesso pela testada onde o uso é permitido.', 'F01', 'art. 336; art. 115 §§1º–3º'),
        "limite_zona_logradouro": P('Zonas definidas por logradouro valem numa faixa de 40 m do alinhamento (ou meia quadra se < 80 m); 100 m em vias listadas da AP3/AP4; 200 m Av. Brasil (AP5, trecho Vila Militar–Santíssimo), 300 m Av. Dom João VI, 60 m em estradas de Guaratiba.', 'F01', 'art. 335 (red. LC 274/2024)'),
        "normas_prevalentes": P('Normas de proteção ambiental, cultural, paisagística e AEROVIÁRIA mais restritivas prevalecem; áreas non aedificandi por razões ambientais/geológicas/serviços públicos.', 'F01', 'art. 333 §4º; art. 524 pú (non altius tollendi, non aedificandi, micro-ondas, Fortes)'),
        "cotas_encostas": P('Acima da cota 100 m (60 m Pão de Açúcar/Urca/Telégrafos/Engenho Novo; 80 m São Conrado) = ZCA2; loteamento particular vedado acima da cota 60 m.', 'F01', 'art. 388; art. 327 §1º (LC 274/2024 art. 43)'),
        "cone_aeroportos": P(None, 'F01', 'art. 333 §4º; art. 391 §1º', 'Restrições aeroviárias (Galeão, Santos Dumont, Jacarepaguá, Afonsos, Santa Cruz) prevalecem, mas não há camada vetorial municipal pública dos cones/PBZPA – consultar DECEA/COMAER (AGA).'),
        "grupamentos": P('Grupamento: área máx. 40.000 m² e testada máx. 200 m; tipos permitidos por zona no Anexo XX; vilas conforme Anexo XX.', 'F01', 'arts. 371–376'),
        "pavimento_cobertura": P('Pavimento de uso comum sobre o último pavimento em edificações com ≥ 7 pavimentos, até 50% do pavimento inferior e afastado 3 m da fachada – não conta como pavimento.', 'F01', 'art. 354 II d'),
        "ics": P('Índice de Comércio e Serviços em zonas residenciais: ZRU/ZRM1/ZRM2 0,3 do CAM; ZRM3 0,4 do CAM.', 'F01', 'art. 367'),
        "remembramento_ap3": P('ZCS/ZUM na AP3: remembramento ≥ 1.000 m² ganha +1 pavimento.', 'F01', 'art. 393'),
        "brt_ap4_ap5": P('Usos C3/S3 permitidos em edificações não residenciais/mistas nas vias de BRT das AP4/AP5.', 'F03', 'LC 270 art. 394-A (acrescido pela LC 274/2024)')},
     "resumo_mcmv": [
        "Melhores zonas para MCMV/HIS multifamiliar: ZRM1/2/3, ZUM, ZCC e ZCS (conferir Anexo XVIII), em especial AP3 (Zona Norte): CAM das tabelas + 50% para HIS e em eixos de trem/metrô/BRT (nota Anexo XXI AP3), OODC isenta na AP3 durante a vigência da LC 270, sem exigência de vagas e +20% ATE com ≥ 20% de Locação Social (art. 392).",
        "AP4/AP5 (Zona Oeste): vagas 1/4 unidades exigidas em geral, mas HIS de política habitacional governamental segue legislação específica (art. 368 §1º I); Zonas ZRU não admitem multifamiliar.",
        "OODC: sem cobrança até jan/2029 em todo o Município (art. 110); a partir daí transição de 20% ao ano; AP1 e AP3 isentas durante a vigência; FIS (Anexo XVII) reduz contrapartida de interesse social.",
        "Grupamentos HIS vinculados a programas governamentais (ex.: MCMV) seguem legislação específica, salvo regra mais branda da LC 270 (art. 371 §5º); grupamento máx. 40.000 m²/testada 200 m; ≥ 500 UH exige doação de lote+escola (LC 274 art. 27).",
        "ZEIS (base) limitam a 2 pavimentos até regulamentação – pouco aptas a empreendimento vertical; AEIS (camada) indicam regimes especiais e áreas estratégicas para HIS (até 400 m de favelas – art. 18 VII).",
        "Gatilhos de custo/prazo: EIV ainda sem lei (avaliação no licenciamento); polos geradores de viagem; APAC/APE/tombamento (análise do patrimônio); UCs/zona de amortecimento; cota > 60/100 m; cones de aeroporto (consulta COMAER); suscetibilidade a deslizamento (GEO-RIO).",
        "Centro: Porto Maravilha exige CEPAC para potencial adicional; Reviver Centro/Praça Onze (Operação Interligada) favorecem retrofit residencial; HIS não afastada não se sujeita à LC 229 (art. 395 §1º)."],
     "geografico": {
        "descricao": "Todas as geometrias são vetores OFICIAIS do servidor público ArcGIS do IPP/Prefeitura do Rio (pgeo3.rio.rj.gov.br, sem login), camadas 'Legislação Bairro a Bairro' (LBB) mantidas pela SMDU. Nenhum polígono foi digitalizado. Geometrias simplificadas (≤ %.0f m em UTM 23S) e coordenadas com 6 casas." % TOL,
        "crs": "EPSG:4326", "crs_area": "EPSG:31983",
        "servidor_oficial": {"diretorio": SRV, "zoneamento": f"{SRV}/Urbanismo/LBB_Zoneamento_urbano_vigente/MapServer", "item_agol": "https://www.arcgis.com/home/item.html?id=23de66d35c394fc89a5c5bca844373b4", "visualizador": "https://mapas.rio.rj.gov.br/"},
        "camadas": [{"nome": e['tema'], "arquivo": f"geo_raw/{e['arquivo']}" if 'arquivo' in e else None, "fonte_url": e['url'], "data_download": e['baixado_em'], "n_feicoes": e['n_feicoes'], "oficial": True, "metodo": "vetor oficial", "erro_estimado_m": TOL} for e in LOG],
        "regras_de_consulta": {"zona_base": "Zona base = polígono do zoneamento (sigla + AP) com maior área no terreno; a AP define a tabela do Anexo XXI.", "terreno_em_mais_de_uma_zona": "LC 270 art. 336: índices ponderados por área e somáveis; usos e gabarito de cada zona.", "faixas_por_logradouro": "Zonas lineares já vêm desenhadas pela SMDU como faixas (40/60/100/200/300 m – art. 335).", "sobrepostas": "Operações urbanas/AEIU: Praça Onze e Porto Maravilha com CAM próprio substituem a base (mantendo usos da base); demais OUC/receptoras/doadoras = alerta.", "restricoes": "APAC, APE, AEIS, UCs, zoneamento ambiental, gabaritos específicos, SMD, Q = alertas."},
        "raio_divisa_m": 30, "pct_minimo_significativo": 0.5,
        "limitacoes": ["A camada do IPP tem caráter informativo (F13); prevalece o texto legal e a certidão/consulta da SMDU.",
                       "Parâmetros com texto (ex.: 'CEA', 'Artigos 380 a 385', 'Dec. 11.990/1993') ficam com valor null e o texto na observação.",
                       "Afastamentos laterais/fundos, usos detalhados (Anexo XVIII), FIS (Anexo XVII) e Fórmulas (Anexo XXV) não constam da camada e não foram lidos no original.",
                       "Cones de aproximação de aeroportos e APPs hídricas não têm vetor municipal público; suscetibilidade a deslizamentos é raster (não vetorizado).",
                       f"{sem} feição(ões) do zoneamento sem sigla/geometria e {skipou} feição(ões) de operações urbanas sem nome/geometria foram descartadas."]},
     "lacunas": [
        {"item": "Texto oficial da LC 270/2024 e alterações (Câmara/DOM)", "motivo": "Sites oficiais (camara.rio, aplicnt/e.camara, doweb, prefeitura.rio) bloqueiam o acesso a partir do ambiente de levantamento (geobloqueio/WAF); WebFetch da Câmara devolve só até o art. 80. Artigos lidos em compilação não oficial (LegisWeb) – conferir no F01."},
        {"item": "Anexo XXV (Fórmulas 1–3) e Anexo XVII (FIS) da LC 270/2024 / LC 291/2025", "motivo": "Anexos em imagem/PDF não acessíveis no site oficial; Fórmula 1 registrada a partir de transcrição de busca – confirmar; valores do FIS por faixa não obtidos."},
        {"item": "Anexo XVIII – usos permitidos por zona (tabela)", "motivo": "Tabela não disponível em vetor/texto acessível; usos descritos pelo conceito da zona (art. 334) e pelo Dec. 56.561/2025 (PDF bloqueado)."},
        {"item": "Afastamentos laterais e de fundos por zona", "motivo": "Não constam da camada oficial; regras na LC 270 (Seção VII) e COES (LC 198/2019) dependem da altura/tipologia."},
        {"item": "Cone de aproximação/PBZPA dos aeroportos", "motivo": "Sem camada pública municipal; norma federal (COMAER/DECEA)."},
        {"item": "Suscetibilidade a deslizamentos / áreas de risco", "motivo": "Serviço GEO-RIO (F14) é raster (MapServer sem feições); não vetorizado."},
        {"item": "APP hídricas e de encosta (Código Florestal)", "motivo": "Camada municipal LBB_APP tem 1 polígono; demais APPs não mapeadas em vetor público municipal."},
        {"item": "URLs F04, F05 e F08 (padrão e.camara.rj.gov.br)", "motivo": "Seguem o padrão do acervo oficial da Câmara (confirmado para a LC 229/2021), mas não puderam ser abertas a partir do ambiente."},
        {"item": "Tabela AP 2.2 alterada pela LC 301/2026", "motivo": "Assume-se que a camada IPP (contém Praça Onze/LC 301) já reflete a nova tabela; não conferido contra o anexo da lei."},
        {"item": "Lei específica de EIV/RIV", "motivo": "Ainda não editada (art. 343 §1º)."}]}
    s = json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
    open(OUT, 'w').write(s)
    print('zonas base', len(zb), 'sobrepostas', len(zo), 'familias', dict(fam))
    print('camadas', {k: len(v['features']) for k, v in camadas.items()})
    print('MB', round(len(s.encode()) / 1e6, 2))

if __name__ == '__main__':
    main()
