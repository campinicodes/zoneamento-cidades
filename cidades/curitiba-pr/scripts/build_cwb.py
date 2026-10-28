#!/usr/bin/env python3
"""Gera curitiba-pr.json (schema 1.1).
Entradas: geo_raw/*.geojson (baixar_camadas.py – GeoCuritiba/IPPUC, serviços públicos),
          tabelas_cwb.py (transcrição dos Quadros), comum_cwb.py (fontes e construtores).
Uso: python3 build_cwb.py"""
import warnings; warnings.filterwarnings('ignore')
import json, os, re, collections, copy, sys
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.validation import make_valid
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comum_cwb import *
from tabelas_cwb import ESP, LIVRE

CID = os.path.dirname(HERE); RAW = os.path.join(CID, 'geo_raw'); OUT = os.path.join(CID, 'curitiba-pr.json')
TOL = 0.00001  # ~1 m

def rnd(g):
    def r(c):
        if isinstance(c[0], (list, tuple)): return [r(x) for x in c]
        return [round(c[0], 6), round(c[1], 6)]
    m = mapping(g); return {'type': m['type'], 'coordinates': r(m['coordinates'])}

def _poly(g):
    if g.geom_type == 'GeometryCollection':
        ps = [x for x in g.geoms if x.geom_type in ('Polygon', 'MultiPolygon')]
        return unary_union(ps) if ps else None
    return g if g.geom_type in ('Polygon', 'MultiPolygon') else None

def limpa(g, tol=TOL):
    if g is None or g.is_empty: return None
    g = _poly(make_valid(g))
    if g is None: return None
    if tol: g = g.simplify(tol, preserve_topology=True)
    g = _poly(make_valid(g))
    if g is None or g.is_empty or g.geom_type not in ('Polygon', 'MultiPolygon'): return None
    gj = rnd(g); g2 = shape(gj)
    if not g2.is_valid:
        g2 = _poly(make_valid(g2))
        if g2 is None or g2.is_empty: return None
        gj = rnd(g2)
        if not shape(gj).is_valid: return None
    return gj

def limpa_linha(g, tol=TOL):
    if g is None or g.is_empty: return None
    g = g.simplify(tol)
    if g.is_empty: return None
    return rnd(g)

def le(nome):
    return json.load(open(os.path.join(RAW, nome + '.geojson')))

def num(v):
    s = ('%g' % v) if isinstance(v, (int, float)) else str(v)
    return s.replace('.', ',')

def pct(v): return f'{round(v * 100, 1):g}%'.replace('.', ',')

# ------------------------------------------------------------------ resolução das specs
def resolve(cod):
    s = ESP[cod]
    if 'base_de' in s:
        b = copy.deepcopy(resolve(s['base_de']))
        for k, v in s.items():
            if k in ('base_de', 'obs', 'extra_obs'): continue
            b[k] = v
        b['obs'] = list(b.get('obs', [])) + list(s.get('obs', [])) + list(s.get('extra_obs', []))
        b['herdado_de'] = s['base_de']
        return b
    return dict(s)

def art_q(s):
    if s['fq'] in ('F14', 'F15'): return s['art']
    if s['fq'] == 'F09': return f"Lei 13.909/2011 Anexo V; Lei 15.511/2019 {s['q']}"
    if s['fq'] == 'F01': return f"Lei 15.511/2019, {s['art']}"
    return f"Lei 15.511/2019, {s['q']} (linha Habitação Coletiva quando admitida); {s['art']}"

def conds_num(lst, unidade_pct=False):
    out = []
    for c, v in lst:
        if v == LIVRE: out.append(C(c, 'livre', None))
        elif isinstance(v, str): out.append(C(c, 'texto', None, texto_original=v))
        else: out.append(C(c, 'unico', v))
    return out

def par_simples(v, unidade, fonte, art, obs=None):
    """num | str | [(cond, v)] | None"""
    if v is None: return SEM(unidade, obs or 'Não fixado no quadro transcrito.', art)
    if isinstance(v, list): return COND(unidade, fonte, art, obs, conds_num(v))
    if v == LIVRE: return P(None, unidade, fonte, art, obs, forma='livre')
    if isinstance(v, str): return TXT(v, unidade, fonte, art, obs)
    return P(v, unidade, fonte, art, obs)

def afastamento(a, fonte, art):
    if a is None: return SEM('m', 'Afastamento das divisas não transcrito.', art)
    t = a[0]
    if t == 'formula':
        return P(None, 'm', fonte, art, f'Afastamento das divisas = {a[1]}, mínimo {num(a[2])} m (H = altura da edificação; Dec. 2.397/2023 define a medição).', forma='formula',
                 formula=f'max({a[1]}, {a[2]})', faixa=dict(min=a[2], max=None))
    if t == 'unico': return P(a[1], 'm', fonte, art, 'Afastamento mínimo das divisas.')
    return TXT(a[1], 'm', fonte, art)

def ca_maximo(s, art):
    fq = s['fq']; o = s.get('oodc'); cb = s.get('ca_b')
    if s.get('ca_max_fixo') is not None:
        return P(s['ca_max_fixo'], 'coeficiente', fq, art, s.get('ca_max_obs') or (o if isinstance(o, str) and o not in ('sem', 'quadro', 'lv') else None))
    if o == 'lv':
        ca_ad = s['lv'][0]
        if ca_ad is None:
            return P(cb, 'coeficiente', 'F09', 'Lei 13.909/2011 Anexo V; Lei 15.511 Quadro IX', 'Sem potencial adicional por CEPAC no Quadro IX: CA máximo = básico.')
        return COND('coeficiente', 'F09', 'Lei 13.909/2011 arts. 7º e 13 §2º, Anexo V; Lei 15.511 Quadro IX ("Parâmetros Construtivos com Potencial Adicional")',
                    'Na OUC-LV o potencial adicional é adquirido por CEPAC (não por OODC da Lei 16.361).',
                    [C('Parâmetros básicos (sem CEPAC)', 'unico', cb), C('Com potencial adicional adquirido por CEPAC', 'unico', ca_ad)])
    if isinstance(o, list):
        cs = []
        if all(t[0] and 'Q III' in t[0] for t in o):
            cs.append(C('Demais vias (zona não listada no Quadro II da Lei 16.361 – sem aquisição)', 'unico', cb))
        for t in o:
            cond, b, adq, mx = t[0], t[1], t[2], t[3]
            cs.append(C(cond or ('Vias normais (Quadro II)' if len(o) > 1 else 'Todos os lotes'), 'unico', mx,
                        observacao=f'Lei 16.361/2024 {t[7]}: básico {num(b)} + adquirível {num(adq)} (50% OODC + 50% TDC, art. 11).'))
        if len(cs) == 1:
            t = o[0]
            return P(t[3], 'coeficiente', 'F03', f'Lei 16.361/2024, {t[7]}; arts. 7º e 11',
                     f'CA básico {num(t[1])} + até {num(t[2])} adquirível (50% OODC + 50% TDC, art. 11; OODC isenta para HIS/COHAB, art. 12).')
        return COND('coeficiente', 'F03', 'Lei 16.361/2024, Quadros II e III; arts. 7º e 11', 'Aquisição: 50% OODC + 50% TDC (art. 11); OODC isenta para HIS/COHAB (art. 12).', cs)
    # sem aquisição
    txt = o if isinstance(o, str) and o not in ('sem', 'quadro') else 'Zona/setor sem aquisição de potencial nos Quadros II e III da Lei 16.361/2024: CA máximo = CA básico.'
    if s.get('ca_b_cond'):
        return COND('coeficiente', fq, art, txt, conds_num(s['ca_b_cond']))
    if cb is None: return SEM('coeficiente', txt if o not in ('sem',) else 'Parâmetros não transcritos (habitação coletiva não admitida ou zona regida por ato próprio).', art)
    return P(cb, 'coeficiente', fq, art, txt)

def pav_oodc(s):
    o = s.get('oodc')
    if not isinstance(o, list): return None
    def v(x): return ('livre', None) if x == LIVRE else ('unico', x)
    if len(o) == 1 and o[0][0] is None:
        f, val = v(o[0][6])
        return P(val, 'pavimentos', 'F03', f'Lei 16.361/2024, {o[0][7]}', f'Altura básica {num(o[0][4])} pav. + adquirível {num(o[0][5]) if o[0][5] is not None else "—"} pav. (Fc = 0,15 por pavimento, art. 9º).', forma=f)
    cs = []
    for t in o:
        f, val = v(t[6]); cs.append(C(t[0] or 'Vias normais (Quadro II)', f, val, observacao=f'Básica {num(t[4])} pav.'))
    return COND('pavimentos', 'F03', 'Lei 16.361/2024, Quadros II e III', 'Altura máxima com aquisição de pavimentos (art. 9º, Fc = 0,15).', cs)

def densidade(s, art):
    d = s.get('dens'); fq = s['fq']
    if d:
        if d[0] == 'unico': return P(d[1], d[2] if d[2] in ('hab/ha', 'uh/ha') else 'uh/ha', fq, art, 'Densidade máxima (habitações por hectare).')
        if d[0] == 'texto': return TXT(d[1], None, fq, art)
        if d[0] == 'cond':
            return COND('uh/ha', 'F09' if fq == 'F02' and s.get('oodc') == 'lv' else fq, 'Lei 13.909/2011 art. 7º §6º e art. 8º VI; Lei 15.511 Quadro IX (nota 8: habitações por hectare)',
                        'Densidade máxima para conjuntos habitacionais de habitação coletiva.', conds_num(d[1]))
    if s.get('sem_tudo') or s.get('col') in ('nao', None) and s.get('ca_b') is None:
        return SEM('uh/ha', 'Sem dado de densidade transcrito.', art)
    cb = s.get('ca_b')
    if cb is None: return SEM('uh/ha', 'Sem CA básico transcrito.', art)
    return COND('uh/ha', 'F01', 'Lei 15.511/2019 arts. 209 e 212; Dec. 2.397/2023 art. 43',
                'Densidade líquida controlada apenas para conjuntos (mais de 2 blocos) – art. 209. Na aquisição de CA, a densidade adicional é proporcional ao CA adquirido (Dec. 2.397 art. 43 par. único). CMU pode admitir mais via EIV/RAP (art. 212 §2º).',
                [C('Habitação coletiva em edifício único (art. 209 não controla)', 'livre', None),
                 C('Conjunto habitacional de habitação coletiva (> 2 blocos), zonas residenciais', 'formula', None, formula='100 * CA', observacao=f'Com CA básico {num(cb)}: {num(100 * cb)} uh/ha.')])

def usos(s, art):
    col = s.get('col'); fq = s['fq']
    if col == 'sim':
        return P(['Habitação Coletiva'], 'codigos_de_uso', fq, art, 'Lista resumida à habitação coletiva (multifamiliar), foco MCMV; os demais usos permitidos/permissíveis/tolerados estão no Quadro citado (não transcritos).')
    if col == 'nao':
        return TXT('Habitação coletiva não admitida no quadro da zona/setor.', 'codigos_de_uso', fq, art, 'Demais usos no Quadro citado (não transcritos).')
    if col is None: return SEM('codigos_de_uso', 'Usos não transcritos.', art)
    return TXT(col, 'codigos_de_uso', fq, art)

def vagas(s):
    return COND('vagas/UH', 'F05', 'Dec. 2.397/2023 arts. 74 III e 75; Dec. 297/2026 art. 9º; Dec. 209/2024 arts. 5º–7º',
                'Regra geral municipal para habitação coletiva (Dec. 2.397/2023 em vigor desde 03/01/2024).',
                [C('Habitação coletiva / conjunto de habitação coletiva (regra geral)', 'unico', 1, observacao='1 vaga por apartamento; facultado para quitinetes (art. 74 III).'),
                 C('Conjunto com mais de 100 UH – visitantes (adicional)', 'unico', 0.02, observacao='1 vaga a cada 50 UH, não computada no mínimo (art. 75).'),
                 C('HIS COHAB-CT / parceria (Dec. 297/2026)', 'unico', 0.25, observacao='Mínimo 1 vaga a cada 4 UH; facultadas até 800 m de terminais e 400 m de estações das linhas expressa/direta (Anexo III; art. 9º). Fonte: F04.'),
                 C('Logradouros do Dec. 209/2024 (SEPE Central/XV etc.)', 'texto', None, texto_original='Não se admitem novos estacionamentos (art. 5º); no SEPE Barão-Riachuelo e vias do art. 6º, vagas só vinculadas ao uso habitacional (facultadas). Fonte: F06.')])

def outros(s, art):
    o = {}
    po = pav_oodc(s)
    if po: o['pavimentos_maximo_com_aquisicao'] = po
    if s.get('oodc') == 'lv' and s['lv'][1] is not None:
        a = s['lv'][1]
        o['pavimentos_maximo_com_cepac'] = P(None if a == LIVRE else a, 'pavimentos', 'F09', 'Lei 13.909/2011 art. 7º §9º; Lei 15.511 Quadro IX',
                                              '+1 pavimento por 0,5 de CA adquirido via CEPAC, até o limite do Quadro IX.', forma='livre' if a == LIVRE else 'unico')
    h = s.get('his')
    if h:
        if h.get('ca_cond'): o['ca_maximo_his_cohab'] = COND('coeficiente', 'F04', 'Dec. 297/2026 art. 5º', 'HIS da COHAB-CT ou em parceria (unidades para famílias cadastradas na COHAB, art. 2º); vale nas áreas do mapa Anexo II.', conds_num(h['ca_cond']))
        elif h.get('ca') is not None: o['ca_maximo_his_cohab'] = P(h['ca'], 'coeficiente', 'F04', 'Dec. 297/2026 art. 5º', 'HIS da COHAB-CT ou em parceria (unidades para famílias cadastradas na COHAB, art. 2º); vale nas áreas do mapa Anexo II.' + (' ' + h['his_obs'] if h.get('his_obs') else ''))
        elif h.get('his_obs'): o['ca_maximo_his_cohab'] = TXT(h['his_obs'], 'coeficiente', 'F04', 'Dec. 297/2026 arts. 4º §2º e 5º III d')
        if h.get('dens_cond'):
            o['densidade_conjunto_his_cohab'] = COND('uh/ha', 'F04', 'Dec. 297/2026 art. 7º', 'Densidade líquida máxima por lote para conjuntos de habitação coletiva HIS (habitação coletiva isolada: livre); +20% até 800 m de terminais/400 m de estações (§2º).', [
                C(c, 'livre', None) if v == LIVRE else (C(c, 'formula', None, formula='100 * CA') if isinstance(v, str) else C(c, 'unico', v)) for c, v in h['dens_cond']])
        elif h.get('dens') == LIVRE:
            o['densidade_conjunto_his_cohab'] = P(None, 'uh/ha', 'F04', 'Dec. 297/2026 art. 7º I', 'Densidade livre para HIS.', forma='livre')
        elif h.get('dens') is not None:
            o['densidade_conjunto_his_cohab'] = P(h['dens'], 'uh/ha', 'F04', 'Dec. 297/2026 art. 7º', 'Conjuntos de habitação coletiva HIS (habitação coletiva isolada: livre); +20% até 800 m de terminais/400 m de estações (§2º).')
        if h.get('pav'):
            o['pavimentos_his_cohab'] = P(h['pav'], 'pavimentos', 'F04', 'Dec. 297/2026 art. 6º §§2º–3º', 'Altura máxima para HIS nesta zona (sem o +1 pavimento do caput).')
        else:
            o['pavimentos_his_cohab'] = TXT('Altura da legislação vigente (Lei 16.361/2024, Lei 15.511/2019) + 1 pavimento residencial se o térreo não tiver mezanino/pé-direito duplo.', 'pavimentos', 'F04', 'Dec. 297/2026 art. 6º caput e §1º')
        o['lote_minimo_his_cohab'] = P(125, 'm2', 'F04', 'Dec. 297/2026 art. 12 §1º', 'Desmembramento HIS: lote ≥ 125 m² e testada ≥ 5 m; conjuntos em série/coletiva em terrenos até 20.000 m² (art. 11).')
        o['vagas_his_cohab'] = P(0.25, 'vagas/UH', 'F04', 'Dec. 297/2026 art. 9º', '1 vaga a cada 4 UH; facultadas perto de terminais/estações (Anexo III).')
    if s.get('sepp'):
        o['altura_setor_pontos_panoramicos'] = P(None, 'm', 'F01', 'Lei 15.511/2019 arts. 112 a 114', 'RNe = referência de nível do topo da edificação; RNp = cota do ponto panorâmico (camada pontos_panoramicos: Praça das Nações 927,90; Praça Soroptimismo 922,15; Farol da Cidade 974,02); d = menor distância ao terreno; a = coeficiente de ajuste (definido por ponto, §1º – não publicado). Garantidos 2 pavimentos e 8 m (§3º).',
                                                 forma='formula', formula='RNe = RNp - (d * a)')
    col = s.get('col')
    if col in ('sim', 'nao') or col is None:
        t = {'sim': 'Admitida (permitida no quadro da zona).', 'nao': 'Não admitida.', None: 'Não transcrito.'}[col]
    else: t = col
    o['habitacao_multifamiliar'] = TXT(t, None, s['fq'], art)
    return o

def parametros(s):
    art = art_q(s); fq = s['fq']
    if s.get('sem_tudo'):
        S = lambda u: SEM(u, 'Parâmetro não obtido para este setor/zona (ver lacunas).', art)
        return dict(ca_minimo=S('coeficiente'), ca_basico=S('coeficiente'), ca_maximo=S('coeficiente'), taxa_ocupacao=S('fracao'), gabarito_altura_max_m=S('m'),
                    gabarito_pavimentos=S('pavimentos'), taxa_permeabilidade=S('fracao'), recuos=dict(frontal=S('m'), lateral=S('m'), fundos=S('m')),
                    lote_minimo_m2=S('m2'), testada_minima_m=S('m'), usos_permitidos=usos(s, art), vagas=vagas(s), densidade=S('uh/ha'),
                    outros=dict(habitacao_multifamiliar=TXT('Não transcrito – ver lacunas.', None, fq, art)))
    cam = SEM('coeficiente', 'A Lei 15.511/2019 e a Lei 16.361/2024 não fixam CA mínimo por zona (PEUC depende de lei específica).', 'Lei 15.511/2019 Quadros; Lei 14.771/2015 (PEUC)')
    if s.get('ca_b_cond'): cab = COND('coeficiente', fq, art, s.get('ca_b_obs'), conds_num(s['ca_b_cond']))
    elif s.get('ca_b') is None: cab = SEM('coeficiente', 'Habitação coletiva não admitida / parâmetro de outros usos não transcrito.', art)
    else: cab = P(s['ca_b'], 'coeficiente', fq, art, s.get('ca_b_obs'))
    # pavimentos
    if s.get('alt_cond'): pav = COND('pavimentos', fq, art, s.get('alt_obs'), conds_num(s['alt_cond']))
    else: pav = par_simples(s.get('alt'), 'pavimentos', fq, art, s.get('alt_obs'))
    if s.get('alt_m'): altm = P(s['alt_m'], 'm', fq, art, 'Altura em metros indicada no quadro.')
    elif s.get('sepp'): altm = P(None, 'm', 'F01', 'Lei 15.511/2019 art. 113', 'Setor Especial dos Pontos Panorâmicos: altura limitada pela fórmula; garantidos 2 pavimentos e 8 m.', forma='formula', formula='RNe = RNp - (d * a)')
    else: altm = SEM('m', 'Curitiba controla a altura em número de pavimentos (Quadros); altura em metros não fixada para a zona.', art)
    if s.get('perm_sem'): perm = SEM('fracao', s['perm_sem'], art)
    else: perm = par_simples(s.get('perm'), 'fracao', fq, art, 'Lei 15.511 art. 201: pode ser reduzida com mecanismo de contenção de cheias.' if fq == 'F02' else None)
    lote = s.get('lote')
    return dict(
        ca_minimo=cam, ca_basico=cab, ca_maximo=ca_maximo(s, art),
        taxa_ocupacao=par_simples(s.get('to'), 'fracao', fq, art),
        gabarito_altura_max_m=altm, gabarito_pavimentos=pav, taxa_permeabilidade=perm,
        recuos=dict(frontal=par_simples(s.get('recuo'), 'm', fq, art, 'Recuo do alinhamento predial.'),
                    lateral=afastamento(s.get('afast'), fq, art), fundos=afastamento(s.get('afast'), fq, art)),
        lote_minimo_m2=P(lote[1], 'm2', fq, art, s.get('lote_obs')) if lote else SEM('m2', 'Não fixado no quadro transcrito.', art),
        testada_minima_m=P(lote[0], 'm', fq, art) if lote else SEM('m', 'Não fixado no quadro transcrito.', art),
        usos_permitidos=usos(s, art), vagas=vagas(s), densidade=densidade(s, art), outros=outros(s, art))

CRIT = {'eixo': 'Eixo de adensamento/estrutural ao longo do transporte coletivo (Lei 14.771/2015 art. 20 I–II).',
        'centralidade': 'Zona central/cívica de alta densidade e usos diversificados.',
        'patrimonio_cultural': 'Zona/setor histórico – parâmetros condicionados à preservação (CAPC).',
        'ambiental': 'Área de proteção ambiental/UC – ocupação muito restrita.',
        'institucional': 'Zona de uso institucional/especial (educacional, militar, desportivo).',
        'especial_economica': 'Zona de serviços/atividade econômica – habitação coletiva restrita ou vedada.',
        'industrial': 'Zona industrial – habitação vedada.', 'especial_interesse_social': 'Setor destinado a HIS/regularização.',
        'expansao': 'Área de ocupação controlada condicionada a parcelamento/PDR.'}

def categoria_criterio(s):
    cat = s['cat']
    if cat in CRIT: return CRIT[cat]
    return f"Classificação do analista pela densidade (CA máximo; ≤1,5 baixa, ≤3 média) e pela restrição ao multifamiliar."

# ------------------------------------------------------------------ códigos da base
APA_I = {'SARU', 'SMRU', 'SS', 'ST', 'ST-BNC', 'STR', 'SUC', 'SUE'}
APA_P = {'ZEI', 'ZES', 'ZOO', 'ZRA', 'ZUC II'}
LVPRE = ['POLO-LV', 'SE-LV', 'ZT-LV', 'ZR-4-LV']
def codigo_de(p):
    g = (p.get('gtm_sigla_zoneamento') or '').strip(); sg = ' '.join((p.get('sg_abrangencia') or '').split())
    if g == 'SEDE':
        return 'SEDE-CFC' if 'SEDE-CFC' in sg else 'SEDE-' + sg
    if g == 'APA' and sg in APA_I: return 'APA-IGUAÇU ' + sg
    if sg in APA_P and g != 'APA': return 'APA-PASSAÚNA ' + sg
    for pre in LVPRE:
        if sg.startswith(pre + ' - '): return pre
    return sg

def main():
    z35 = le('zoneamento_cadastral')
    grupos = collections.defaultdict(list)
    for f in z35['features']:
        p = f['properties']; cod = codigo_de(p)
        g = limpa(shape(f['geometry'])) if f.get('geometry') else None
        if g is None: continue
        sg = ' '.join((p.get('sg_abrangencia') or '').split())
        grupos[cod].append(({'codigo': cod, 'subarea': sg if sg != cod else None, 'sigla_gtm': (p.get('gtm_sigla_zoneamento') or '').strip(),
                             'nome_base': p.get('nm_zona_abrangencia'), 'legislacao': p.get('legislacao'), 'data_atualizacao': p.get('data_atualizacao')}, g))
    faltam = sorted(set(grupos) - set(ESP)); sobram = sorted(set(ESP) - set(grupos))
    print('sem spec:', faltam); print('spec sem geometria:', sobram)
    assert not faltam, faltam
    zonas = []
    for cod in sorted(grupos):
        s = resolve(cod)
        obs = list(s.get('obs', []))
        if s.get('herdado_de'): obs.insert(0, f"Parâmetros do quadro de {s['herdado_de']}, com as diferenças indicadas.")
        if s.get('sepp'): obs.append('Integra o Setor Especial dos Pontos Panorâmicos (Lei 15.511 arts. 112–114; Dec. 1.006/2020): altura do topo da edificação limitada por RNe = RNp − (d × a); garantidos 2 pavimentos/8 m.')
        if cod == 'EE': obs.append('Feições com sigla_gtm EE-1 a EE-5 = trechos do Eixo Estrutural na base cadastral (o código da base não distingue via central/externa/outras vias – ver Quadros I a III).')
        if cod in LVPRE: obs.append('Sub-áreas (POLO-LV - 1, - A etc.) mantidas em properties.subarea; mesmo quadro de parâmetros.')
        obs.append('Geometria: camada 35 (Zoneamento – base cadastral, atualização 2022-03) do Mapa Cadastral GeoCuritiba; a Consulta Informativa de Lote (Guia Amarela) prevalece.')
        desc = f"{s['nome']} – {s['q']}" + ('' if s['fq'] in ('F14', 'F15') else f" da Lei 15.511/2019 ({s['art']}).")
        nome = s['nome']
        if s.get('herdado_de') and cod in ESP and 'nome' in ESP[cod]: nome = ESP[cod]['nome']
        zonas.append(dict(codigo=cod, nome=nome, descricao=desc, tipo='base', prioridade=0, categoria_normalizada=s['cat'], categoria_criterio=categoria_criterio(s),
                          regra_sobreposicao=None, parametros=parametros(s), observacoes=obs,
                          geometria=dict(type='FeatureCollection', crs='EPSG:4326 (lon, lat)', fonte='GeoCuritiba/IPPUC – Publico_GeoCuritiba_MapaCadastral/MapServer/35 (F16)', oficial=True,
                                         observacao_geometria='Vetor oficial público (outSR=4326); simplificação ~1 m; coordenadas com 6 casas.',
                                         features=[dict(type='Feature', properties=pp, geometry=g) for pp, g in grupos[cod]])))
    # ---------------------------------------------------------------- camadas
    cam = {}; geo_camadas = []
    def add_geo(nome, arquivo, layer, n, url=None):
        geo_camadas.append(dict(nome=nome, arquivo='geo_raw/' + arquivo + '.geojson', fonte_url=url or f'{MC}/{layer}', data_download=HOJE, oficial=True, metodo='vetor oficial', erro_estimado_m=None, n_feicoes=n))
    add_geo('Zoneamento – base cadastral (zonas base)', 'zoneamento_cadastral', 35, len(z35['features']))
    z36 = le('zoneamento_l15511')
    add_geo('Zoneamento Lei 15.511/2019 (camada de referência, não usada como base)', 'zoneamento_l15511', 36, len(z36['features']))
    def feats(d, fcod, props=None, tol=TOL):
        out = []
        for f in d['features']:
            if not f.get('geometry'): continue
            g = shape(f['geometry'])
            gj = limpa_linha(g, tol) if 'Line' in g.geom_type else limpa(g, tol)
            if gj is None: continue
            p = f['properties']; c = fcod(p)
            pr = {'codigo': c}; pr.update({k: p.get(k) for k in (props or [])})
            out.append(dict(type='Feature', properties=pr, geometry=gj))
        return out
    def dissolve(fe, tol=TOL * 2):
        g = collections.defaultdict(list); props = {}
        for f in fe: g[f['properties']['codigo']].append(shape(f['geometry'])); props.setdefault(f['properties']['codigo'], f['properties'])
        return [dict(type='Feature', properties=props[c], geometry=limpa(unary_union([make_valid(x) for x in g[c]]), tol)) for c in sorted(g)]
    def camada(nome, papel, desc, fonte, fid, art, fe, ppc=None, al=None, obs=None):
        fe = [f for f in fe if f['geometry']]
        cam[nome] = dict(papel=papel, descricao=desc, fonte=fonte, oficial=True, fonte_id=fid, artigo_anexo=art, observacao=obs,
                         parametros_por_codigo=ppc, alerta_por_codigo=al, features=fe)
    # Dec. 297/2026 – áreas
    d = le('dec297_areas')
    fe = dissolve(feats(d, lambda p: ' '.join((p.get('sg_zona') or '').split()), ['nm_zona', 'areas', 'legislacao']))
    ppc = {}
    for f in fe:
        c = f['properties']['codigo']
        key = {'ZED-LV': 'ZE-D-LV', 'ZROC': 'ZROC-1 CAMPO DE SANTANA'}.get(c, c)
        s = resolve(key) if key in ESP else None
        h = (s or {}).get('his')
        if c in ('ZT-LV', 'POLO-LV', 'SE-LV', 'ZR-4-LV', 'ZED-LV'):
            ppc[c] = {'ca_maximo_his_cohab': TXT('Na OUC-LV os incentivos de HIS seguem regulamentação própria (art. 9º IV da Lei 13.909/2011) – Dec. 297 art. 4º §3º.', 'coeficiente', 'F04', 'Dec. 297/2026 art. 4º §3º')}
        elif h and (h.get('ca_cond') or h.get('ca') is not None):
            o = outros(dict(s, sepp=False), '')
            ppc[c] = {k: o[k] for k in ('ca_maximo_his_cohab', 'densidade_conjunto_his_cohab', 'pavimentos_his_cohab') if k in o}
        else:
            ppc[c] = {'ca_maximo_his_cohab': TXT('Ver Dec. 297/2026 art. 5º (zona com condição própria).', 'coeficiente', 'F04', 'Dec. 297/2026 arts. 4º e 5º')}
    camada('dec297_areas_his', 'informativa', 'Eixos, zonas e setores onde se admitem as condições especiais de HIS da COHAB-CT (Dec. 297/2026, mapa do Anexo II).',
           'GeoCuritiba – MapaCadastral/41', 'F04', 'Dec. 297/2026 art. 4º §1º e Anexo II', fe, ppc, None,
           'Vale só para empreendimentos da COHAB-CT ou em parceria com ela, com UH destinadas a famílias cadastradas (art. 2º).')
    add_geo('Dec. 297/2026 – áreas HIS (Anexo II)', 'dec297_areas', 41, len(d['features']))
    d = le('dec297_densidade_ampliada')
    camada('dec297_densidade_ampliada', 'informativa', 'Raios de 800 m de terminais e 400 m de estações das linhas expressa/direta (Dec. 297/2026 Anexo III): densidade HIS +20% (art. 7º §2º) e vagas facultadas (art. 9º).',
           'GeoCuritiba – MapaCadastral/42', 'F04', 'Dec. 297/2026 arts. 7º §§2º–3º e 9º; Anexo III', dissolve(feats(d, lambda p: 'DEC297_ANEXO_III')),
           {'DEC297_ANEXO_III': {'acrescimo_densidade_his': P(0.2, 'fracao', 'F04', 'Dec. 297/2026 art. 7º §2º', 'Até +20% na densidade HIS se ≥ 50% do terreno estiver no raio (§3º).'),
                                 'vagas_his': TXT('Vagas facultadas para HIS COHAB (art. 9º).', None, 'F04', 'Dec. 297/2026 art. 9º')}}, None)
    add_geo('Dec. 297/2026 – Anexo III (raios de terminais/estações)', 'dec297_densidade_ampliada', 42, len(d['features']))
    # SERC
    SERC = {'SBE': ('Setor de Baixa Emissão', 'Novas edificações: HIS +2,0; hotelaria +2,0; habitação coletiva estratégica (exceto quitinete) +1,0; não habitacional estratégico +1,0 (art. 8º). Retrofit: HIS +2,0; hotelaria +1,5; coletiva/institucional estratégica +1,0; misto +0,5 (art. 9º).', 2.0),
            'SHBE': ('Setor Histórico de Baixa Emissão', 'Novas edificações: sem CA adicional (art. 12). Retrofit: HIS +2,0; hotelaria +1,0; coletiva/institucional estratégica +1,0; misto +1,0 (art. 13).', 0),
            'SRF': ('Setor Rodoferroviária', 'CA adicional (novas e retrofit) a definir por ato do Executivo após estudo específico (art. 16).', None),
            'ST-01': ('Setor de Transição 01', 'Novas edificações: HIS +1,0; hotelaria +0,5 (art. 19). Retrofit: HIS +1,0; hotelaria +1,0; coletiva/institucional estratégica +1,0; misto +0,5 (art. 20).', 1.0),
            'ST-02': ('Setor de Transição 02', 'Novas edificações: sem CA adicional no decreto. Retrofit: HIS +2,0; hotelaria +1,0 (art. 23).', 0),
            'ST-03': ('Setor de Transição 03', 'Novas edificações: HIS +0,5; hotelaria +0,5 (art. 26). Retrofit: HIS +0,5; hotelaria +0,5; misto +0,5 (art. 27).', 0.5),
            'ST-04': ('Setor de Transição 04', 'Novas edificações: HIS +2,0; hotelaria +2,0 (art. 30). Retrofit: HIS +2,0; hotelaria +1,0; coletiva/institucional estratégica +1,0; misto +0,5 (art. 31).', 2.0)}
    d = le('serc_setores'); fe = dissolve(feats(d, lambda p: p['subsetor_sigla'].strip(), ['subsetor', 'legislacao']))
    ppc = {}
    for c, (n, t, v) in SERC.items():
        x = {'descricao': TXT(f'{n}: {t}', None, 'F11', 'Dec. 418/2026 arts. 4º a 31')}
        x['ca_adicional_nao_oneroso_his_nova'] = (SEM('coeficiente', 'A definir por ato do Executivo (art. 16).', 'Dec. 418/2026 art. 16') if v is None else
                                                   P(v, 'coeficiente', 'F11', 'Dec. 418/2026 (artigo do setor)', 'Não oneroso; o CA total não pode exceder o CA máximo da Lei 16.361/2024 (art. 5º §1º).'))
        ppc[c] = x
    camada('serc_setores', 'informativa', 'Setor Especial da Região Central (Programa Curitiba de Volta ao Centro – LC 150/2025) – CA adicional NÃO oneroso por setor (Dec. 418/2026).',
           'GeoCuritiba – MapaCadastral/43', 'F11', 'LC 150/2025 arts. 4º e 12–14; Dec. 418/2026 arts. 4º–31', fe, ppc, None,
           'CA total ≤ CA máximo da Lei 16.361/2024 (Dec. 418 art. 5º §1º); em SEPE/ZH/SETP-LO prevalecem as restrições próprias (art. 5º §2º). Incentivos fiscais da LC 150/2025 art. 22 (IPTU/ITBI/ISS até 2032).')
    add_geo('SERC – setores (Dec. 418/2026)', 'serc_setores', 43, len(d['features']))
    d = le('serc_eixos')
    camada('serc_eixos', 'informativa', 'Eixos prioritários do SERC (EP-XV, EP-BR, EP-TG, EP-SM) – incentivos de retrofit (Dec. 418/2026 arts. 32–43).', 'GeoCuritiba – MapaCadastral/45', 'F11', 'Dec. 418/2026 arts. 4º VIII–XI e 32–43',
           feats(d, lambda p: p['sigla_trecho_eixo'].strip(), ['nome_eixo', 'trecho_eixo', 'sigla_eixo']), None, None,
           'Retrofit em EP-XV e EP-BR: HIS +2,0; hotelaria +1,0; coletiva/institucional estratégica +1,0; misto +1,0 (arts. 34 e 37). EP-TG/EP-SM: ver arts. 38–43.')
    add_geo('SERC – eixos prioritários', 'serc_eixos', 45, len(d['features']))
    d = le('serc_perimetro')
    camada('serc_perimetro', 'informativa', 'Perímetro do SERC (LC 150/2025; Dec. 418/2026 Anexo I).', 'GeoCuritiba – MapaCadastral/46', 'F10', 'LC 150/2025 art. 4º', feats(d, lambda p: 'SERC'), None, None,
           'Incentivos fiscais (LC 150/2025 art. 22–24): IPTU 100% durante as obras até 2028; ITBI isento para lista COHAB, 1% até 3 SM, 2% de 3 a 6 SM, até 2032; ISS de construção −60% para retrofit.')
    add_geo('SERC – perímetro', 'serc_perimetro', 46, len(d['features']))
    # OUC-LV
    d = le('ouc_linha_verde')
    camada('ouc_linha_verde', 'informativa', 'Perímetro da Operação Urbana Consorciada Linha Verde (Lei 13.909/2011) – potencial adicional por CEPAC.', 'GeoCuritiba – MapaCadastral/29', 'F09', 'Lei 13.909/2011 arts. 1º, 5º e 13–14',
           feats(d, lambda p: 'OUC-LV'), {'OUC-LV': {'instrumento': TXT('CEPAC (4.830.000 títulos, valor mínimo R$ 200; equivalência na Tabela II do art. 14); contenção de cheias obrigatória (art. 10); EIA/RIMA da operação (art. 27).', None, 'F09', 'Lei 13.909/2011 arts. 10, 13, 14 e 27')}}, None)
    add_geo('OUC Linha Verde', 'ouc_linha_verde', 29, len(d['features']))
    # APAs
    d = le('apa_iguacu')
    fe = dissolve(feats(d, lambda p: p['sg_setor'].strip(), ['nm_setor', 'legislacao']))
    al = {f['properties']['codigo']: f"APA do Iguaçu – {f['properties']['nm_setor']}: parâmetros do Dec. 1.025/2021 (e Dec. 1.004/2023); licenciamento ambiental (SMMA) e RAP para atividades listadas." for f in fe}
    camada('apa_iguacu', 'restricao', 'APA municipal do Iguaçu – setores (Dec. 1.025/2021).', 'GeoCuritiba – MapaCadastral/27', 'F14', 'Dec. 1.025/2021 art. 6º e Quadros I–VII', fe, None, al)
    add_geo('APA do Iguaçu – setores', 'apa_iguacu', 27, len(d['features']))
    d = le('apa_passauna')
    lim = unary_union([shape(z['geometry']) for zz in zonas for z in zz['geometria']['features']]).buffer(0.0005)
    sub = dict(type='FeatureCollection', features=[f for f in d['features'] if f.get('geometry') and shape(f['geometry']).intersects(lim)])
    fe = dissolve(feats(sub, lambda p: ' '.join((p.get('sg_zona') or '').split()), ['nm_zona', 'legislacao']), TOL * 2)
    for f in fe:
        g = shape(f['geometry']).intersection(lim); f['geometry'] = limpa(g, TOL * 2)
    fe = [f for f in fe if f['geometry']]
    al = {f['properties']['codigo']: f"APA estadual do Passaúna – {f['properties']['nm_zona']}: ocupação regida pelo zoneamento estadual (Dec. Est. 5.063/2001) e, na parte de Curitiba, pelo Dec. 924/2021 – exige anuência/licenciamento ambiental." for f in fe}
    camada('apa_passauna', 'restricao', 'APA estadual do Passaúna – zoneamento detalhado (recorte Curitiba).', 'GeoCuritiba – MapaCadastral/28', 'F15', 'Dec. 924/2021 art. 3º e Anexo (Quadros I–XIII)', fe, None, al,
           'Camada com o zoneamento estadual da APA (Dec. Est. 458/1991, Lei Est. 13.027/2000, Dec. Est. 5.063/2001); recortada ao limite municipal aproximado (união das zonas base + 50 m). As zonas base APA-PASSAÚNA trazem os parâmetros do Dec. 924/2021.')
    add_geo('APA do Passaúna – zonas', 'apa_passauna', 28, len(d['features']))
    # UCs
    UCS = [('uc_estacao_ecologica', 'ESEC'), ('uc_parque_natural', 'PQ'), ('uc_parque_linear', 'PQ_LINEAR'), ('uc_bosque_municipal', 'BQ'), ('uc_bosque_conservacao', 'BCBU'),
           ('uc_refugio', 'RVS'), ('uc_rppnm', 'RPPNM'), ('uc_especificas', 'UC_ESPECIFICA'), ('uc_apa', 'APA_MUNICIPAL'), ('uc_arie', 'ARIE')]
    fe = []; al = {}
    for arq, c in UCS:
        d = le(arq)
        for f in feats(d, lambda p, c=c: c, ['nome', 'classificacao', 'atolegal']): fe.append(f)
        al[c] = {'ESEC': 'Estação Ecológica (proteção integral) – não edificável.', 'PQ': 'Parque municipal – não edificável.', 'PQ_LINEAR': 'Parque linear – não edificável.',
                 'BQ': 'Bosque municipal – não edificável.', 'BCBU': 'Bosque de Conservação da Biodiversidade Urbana – restrições do ato de criação.', 'RVS': 'Refúgio de Vida Silvestre – uso restrito ao plano de manejo.',
                 'RPPNM': 'RPPN Municipal – área privada gravada como reserva (inedificável na porção gravada; pode gerar potencial para TDC – Lei 16.361 art. 18).',
                 'UC_ESPECIFICA': 'Unidade de conservação específica (ex.: Jardim Botânico) – não edificável.', 'APA_MUNICIPAL': 'APA – ver parâmetros da zona APA-IGUAÇU/APA-PASSAÚNA.', 'ARIE': 'ARIE/Geossítio – restrições do ato de criação.'}[c]
        add_geo(f'SMUC – {c}', arq, None, len(d['features']), url=GEO + 'Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer')
    camada('unidades_conservacao', 'restricao', 'Sistema Municipal de Unidades de Conservação (SMUC) – polígonos das UCs.', 'GeoCuritiba – Publico_Sistema_Municipal_de_Unidades_de_Conservacao', 'F17', 'Lei 9.804/2000 (SMUC) e atos de criação (atributo atolegal)', fe, None, al)
    # patrimônio / paisagem
    d1 = le('setp_largo_ordem'); d2 = le('setp_largo_ordem_areas')
    fe = feats(d1, lambda p: 'SETP-LO') + dissolve(feats(d2, lambda p: ' '.join(p['sg_abrangencia'].split()), ['nm_abrangencia']))
    camada('setp_largo_ordem', 'restricao', 'Setor Especial de Transição da Paisagem do Largo da Ordem (Dec. 2.070/2025).', 'GeoCuritiba – MapaCadastral/50 e 51', 'F16', 'Dec. 2.070/2025 (texto não baixado – ver lacunas)', fe, None,
           {f['properties']['codigo']: f"{f['properties'].get('nm_abrangencia') or 'SETP-LO'}: volumetria/paisagem controladas pelo Dec. 2.070/2025 – análise do patrimônio (CAPC)." for f in fe})
    add_geo('SETP Largo da Ordem', 'setp_largo_ordem', 50, len(d1['features'])); add_geo('SETP Largo da Ordem – áreas', 'setp_largo_ordem_areas', 51, len(d2['features']))
    d = le('pontos_panoramicos')
    fe = feats(d, lambda p: 'SE-PP ' + p['cd_abrangencia'], ['nm_abrangencia', 'pp_altitude'])
    camada('pontos_panoramicos', 'restricao', 'Setor Especial dos Pontos Panorâmicos – áreas de influência (Lei 15.511 arts. 112–114; Dec. 1.006/2020).', 'GeoCuritiba – MapaCadastral/31', 'F01', 'Lei 15.511/2019 arts. 112 a 114', fe,
           {f['properties']['codigo']: {'rnp_m': P(f['properties']['pp_altitude'], 'm', 'F16', 'atributo pp_altitude da camada 31', 'Referência de nível do ponto panorâmico (RNp).'),
                                         'altura_topo': P(None, 'm', 'F01', 'Lei 15.511/2019 art. 113', 'a = coeficiente de ajuste por ponto (Dec. 1.006/2020, não lido).', forma='formula', formula='RNe = RNp - (d * a)')} for f in fe},
           {f['properties']['codigo']: f"Ponto panorâmico {f['properties']['nm_abrangencia']} (RNp {num(f['properties']['pp_altitude'])} m): altura do topo limitada por RNe = RNp − d×a; garantidos 2 pavimentos/8 m (art. 113)." for f in fe})
    add_geo('Pontos panorâmicos (SEPP)', 'pontos_panoramicos', 31, len(d['features']))
    d = le('parque_tangua')
    fe = dissolve(feats(d, lambda p: p['sg_zona'].strip(), ['nm_abrangencia', 'legislacao']))
    camada('parque_tangua', 'restricao', 'Setor Especial do Parque Tanguá (parque, transição e amortecimento – Dec. 673/2002).', 'GeoCuritiba – MapaCadastral/32', 'F16', 'Lei 9.800/2000; Dec. 673/2002 (não lido)', fe, None,
           {f['properties']['codigo']: f"{f['properties']['nm_abrangencia']}: parâmetros especiais do Dec. 673/2002 (não transcritos)." for f in fe})
    add_geo('Setor Especial do Parque Tanguá', 'parque_tangua', 32, len(d['features']))
    d = le('vila_oficios')
    fe = dissolve(feats(d, lambda p: 'SE-VO ' + ('ASSENTAMENTO' if 'ASSENT' in (p['nm_abrangencia'] or '') else 'ZONAS'), ['nm_abrangencia', 'legislacao']))
    camada('vila_oficios', 'informativa', 'Setor Especial de Vilas de Ofícios (Dec. 2.027/2021) – inclui assentamentos irregulares mapeados.', 'GeoCuritiba – MapaCadastral/33', 'F16', 'Dec. 2.027/2021 (não lido)', fe, None, None,
           'Assentamentos irregulares indicam possível REURB/ocupação – checar situação fundiária.')
    add_geo('Setor Especial de Vilas de Ofícios', 'vila_oficios', 33, len(d['features']))
    # linhas
    d = le('sepe')
    fe = feats(d, lambda p: ' '.join((p.get('sg_abrangencia') or 'SEPE').split()), ['nm_abrangencia'])
    camada('sepe', 'informativa', 'Setor Especial Preferencial de Pedestres (eixos – linhas).', 'GeoCuritiba – MapaCadastral/30', 'F01', 'Lei 15.511/2019 arts. 96 a 107; Dec. 209/2024', fe, None,
           None, 'Lotes com testada para o SEPE: 5 pavimentos até 15 m de profundidade (art. 99), sem novos estacionamentos no SEPE Central/XV (Dec. 209 art. 5º).')
    add_geo('SEPE (linhas)', 'sepe', 30, len(d['features']))
    d = le('sistema_viario')
    fe = feats(d, lambda p: p['sist_viario_classificado'].strip(), ['codvia', 'nmvia'])
    camada('sistema_viario_basico', 'informativa', 'Sistema viário básico classificado (Lei 15.511/2019) – define os parâmetros das vias setoriais/coletoras/prioritárias (Quadros XLIV–XLVIII) e da Lei 16.361 Quadro III.',
           'GeoCuritiba – MapaCadastral/34', 'F02', 'Lei 15.511/2019 Quadros XLIV a XLVIII; Lei 16.361/2024 Quadro III; Dec. 297/2026 art. 5º III', fe,
           {c: {'efeito': TXT({'SETORIAL 1': 'Via setorial 1', 'SETORIAL 2': 'Via setorial 2', 'COLETORA 1': 'Via coletora 1', 'COLETORA 2': 'Via coletora 2'}.get(c, c.title()) +
                               ': lotes com testada para a via seguem o quadro da via (Quadros XLIV–XLVIII) e, em ZR2/ZR3/ZROI/SEHIS/ZUM-1, os CA/HIS de "vias classificadas" (Lei 16.361 Q III; Dec. 297 art. 5º III).', None, 'F02', 'Quadros XLIV–XLVIII')}
            for c in sorted({f['properties']['codigo'] for f in fe})}, None,
           'Linhas de eixo de via: para aplicar, verifique se o lote tem testada para a via classificada (status "NÃO OFICIAL" em parte das vias na base).')
    add_geo('Sistema viário básico (linhas)', 'sistema_viario', 34, len(d['features']))

    # ---------------------------------------------------------------- blocos
    def I(chave, titulo, *a, **k): return dict(chave=chave, titulo=titulo, **P(*a, **k))
    def IT(chave, titulo, texto, fonte, art, obs=None): return dict(chave=chave, titulo=titulo, **TXT(texto, None, fonte, art, obs))
    outorga = dict(resumo='Aquisição de potencial construtivo adicional pela Lei 16.361/2024: do CA básico (Lei 15.511) até o CA máximo dos Quadros II (vias normais) e III (vias classificadas), pago 50% em OODC e 50% em TDC; pavimentos adicionais também adquiríveis. HIS/COHAB isenta de OODC (art. 12). Na OUC-LV vale o CEPAC (Lei 13.909/2011).',
                   fonte_id='F03', artigo_anexo='Lei 16.361/2024 arts. 7º a 19; Quadros II a V', itens=[
        IT('aplicacao', 'Onde se aplica', 'Eixos, zonas e setores listados nos Quadros II e III da Lei 16.361/2024; zonas não listadas não admitem acréscimo (CA máximo = básico).', 'F03', 'art. 7º; Quadros II e III'),
        I('formula_oodc', 'Contrapartida da OODC', None, 'R$', 'F03', 'art. 9º', 'A = área adicional (m²); Ca = coeficiente básico do lote; Vu = valor unitário do terreno (Planta Genérica); Fc = 0,75 para CA, 0,15 para pavimentos, 1,0 para uso/porte; IPU = 0,3 nos casos do art. 10.', forma='formula', formula='Vp = (A / Ca) * Vu * Fc * IPU'),
        I('fc_coeficiente', 'Fator de correção – coeficiente', 0.75, None, 'F03', 'art. 9º'),
        I('fc_pavimento', 'Fator de correção – pavimentos adicionais', 0.15, None, 'F03', 'art. 9º'),
        I('ipu', 'Índice de Promoção Urbana (redutor)', 0.3, None, 'F03', 'art. 10 §§1º–2º', 'Habitacional na ZC e na ZR4 lindeira ao EE Boa Vista–Santa Cândida e Capão Raso–Pinheirinho; EACF, EACB, ECL-3 e EMF (Polo-LV ao sul da ZS-2) – por 2 anos, prorrogável.'),
        IT('proporcao', 'Proporção OODC × TDC', '50% do potencial adicional por OODC e 50% por TDC (art. 11); 100% OODC para SEAHM e equipamentos sociais (§1º); descontos e isenções nos §§2º–3º.', 'F03', 'arts. 11 e 19'),
        IT('isencao_his', 'Isenção para HIS', 'Isenta de OODC a HIS e a habitação coletiva produzida pela COHAB-CT ou em parceria com ela.', 'F03', 'art. 12'),
        I('tdc_potencial', 'TDC – potencial do imóvel cedente', None, 'm2', 'F03', 'art. 17', 'P = Ca × A (coeficiente da zona × área do imóvel cedente).', forma='formula', formula='P = Ca * A'),
        I('tdc_conversao', 'TDC – conversão cedente → receptor', None, 'm2', 'F03', 'art. 18', 'Fc = 0,55 patrimônio; 0,75 RPPNM e demais; 0,15 pavimentos.', forma='formula', formula='Pc = Ptr * (Vur / Vuc) * (Cc / Cr) * Fc'),
        IT('cpc', 'Certificado de Potencial Construtivo (CPC)', 'Venda de potencial pelo Município (CPC): Vp = A × Vup, com fatores de regularização 0,8–1,3; certificados válidos por 4 + 4 anos; restabelecimento do potencial a cada 15 anos.', 'F03', 'arts. 26 a 35'),
        IT('cepac', 'OUC Linha Verde – CEPAC', 'Na OUC-LV o potencial adicional (CA, pavimentos, densidade, usos/porte) é adquirido por CEPAC; 4.830.000 CEPACs; Tabela II de equivalência por setor; +10 UH por 0,1 de CA; 15 CEPACs por UH excedente; +1 pavimento por 0,5 de CA.', 'F09', 'Lei 13.909/2011 arts. 7º §§7º–9º, 13 e 14'),
        IT('serc', 'SERC – CA adicional não oneroso', 'No Setor Especial da Região Central (LC 150/2025) há CA adicional não oneroso para HIS (até +2), hotelaria e usos estratégicos, sempre limitado ao CA máximo da Lei 16.361 (Dec. 418/2026 art. 5º §1º). Ver camada serc_setores.', 'F10', 'LC 150/2025 arts. 12–14 e 18; Dec. 418/2026'),
        IT('premios', 'Prêmios e incentivos construtivos', 'Lei 16.448/2024: torre habitacional nas vias externas do EE (+1× área do terreno), fachada ativa (+1 pavimento), galerias, estacionamento não computável etc. (revogou a Lei 15.824/2021).', 'F07', 'Lei 16.448/2024 arts. 5º–23'),
    ])
    zeis = dict(resumo='Curitiba não usa "ZEIS": a HIS é tratada pelo SEHIS (Setor Especial de HIS, Quadro XLIX), pelas condições especiais do Dec. 297/2026 (COHAB-CT/parceria, em quase todas as zonas do Anexo II), pelo ST-BNC na APA do Iguaçu e pelos incentivos do SERC (LC 150/2025).',
                fonte_id='F04', artigo_anexo='Lei 15.511/2019 arts. 158–159, 221–224; Dec. 297/2026', itens=[
        IT('sehis', 'SEHIS', 'Setor Especial de HIS: CA 1, 3 pavimentos, TO 50%, lote 6 × 180 m²; habitação coletiva só em lote ≥ 360 m² com via ≥ 12 m; lotes da COHAB (art. 159).', 'F02', 'Lei 15.511 art. 158 e Quadro XLIX'),
        IT('dec297_ca', 'Dec. 297/2026 – CA máximo HIS', 'EE 6; ENC 3; EMF/EAC/EACF/ECL-3/ECO 2,5; EACB 2; ECS-1 1,5; ZC 7; ZCC Cândido de Abreu 5; ZSM/ZUMVP 3; ZH-1 2,6; ZCC demais/ZR4/ZUM-3/ZR3-T Mercês/Alto da Glória 2,5; ZH-2/ZFR/ZUM-2/ZR3-T 2; ZR3/ZUM-1 1,5 (vias setoriais 1,8); ZR2/SEHIS/ZROI/ZCSF/ZCUM 1 (vias classificadas 1,5).', 'F04', 'Dec. 297/2026 art. 5º'),
        IT('dec297_densidade', 'Dec. 297/2026 – densidade HIS', 'Habitação coletiva isolada: livre. Conjuntos: livre em ZC/ZCC-incentivo/EE/ENC; 750 uh/ha ZUMVP e ZSM em vias classificadas; 625 eixos de adensamento/ZR4/ZSM/ZUM-3; 500 EACB/ZH/ZFR/ZUM-2/ZR3-T/ZR3 em vias classificadas; 375 ECS-1/ZUM-1/ZR3; 220/200 ZR2/SEHIS/ZROI; +20% perto de terminais/estações.', 'F04', 'Dec. 297/2026 arts. 7º e 8º'),
        IT('dec297_outros', 'Dec. 297/2026 – outros incentivos', '+1 pavimento residencial (térreo sem mezanino); 1 vaga/4 UH (facultadas perto do transporte); recreação 6 m²/UH (facultável ≤ 48 UH; 3 m²/UH > 48 UH com praça); lote 125 m²/5 m; conjuntos em terreno ≤ 20.000 m²; afastamentos, recuo, TO e permeabilidade da zona (art. 4º §1º).', 'F04', 'Dec. 297/2026 arts. 4º, 6º, 9º–12'),
        IT('publico', 'Público-alvo', 'Unidades destinadas integralmente a famílias inscritas/cadastradas na COHAB-CT; empreendimentos da COHAB ou em parceria com a iniciativa privada (Certidão de Regularidade Contratual da COHAB para alvará/CVCO).', 'F04', 'Dec. 297/2026 arts. 1º, 2º e 13'),
        IT('condicoes_especiais', 'Condições especiais (Lei 15.511)', 'EI-HIS e condições especiais de ocupação para HIS a critério do CMU (arts. 221–224); parágrafo único do art. 224 regulamentado pelo Dec. 297/2026.', 'F01', 'Lei 15.511 arts. 221 a 224'),
        IT('st_bnc', 'APA do Iguaçu – ST Bairro Novo do Caximba', 'Habitação coletiva só como EIS da COHAB-CT, ≤ 100 hab/ha, em lotes municipais/COHAB na R. Delegado Bruno de Almeida.', 'F14', 'Dec. 1.025/2021 Quadro V (red. Dec. 1.004/2023)'),
        IT('zroc_campo_santana', 'ZROC-1 Campo de Santana', 'Novos loteamentos doam 15% para HIS (art. 48); condições HIS dependem de Plano de Desenvolvimento Regional (Dec. 297 art. 4º §2º).', 'F01', 'Lei 15.511 art. 48'),
        IT('serc_fiscal', 'SERC – incentivos fiscais', 'IPTU 100% durante obras (até 2028) e em imóvel de patrimônio restaurado (até 2032); retrofit habitacional IPTU 50% (100% HIS de entes públicos); ITBI isento para lista COHAB, 1% (renda ≤ 3 SM) e 2% (3–6 SM) até 2032; ISS de construção −60% em retrofit.', 'F10', 'LC 150/2025 arts. 22 a 24'),
        IT('oodc_isencao', 'Isenção de OODC', 'HIS e habitação coletiva COHAB/parceria isentas de OODC.', 'F03', 'Lei 16.361/2024 art. 12'),
    ])
    outros_b = dict(resumo='EIV, conjuntos habitacionais, plano massa, estacionamentos, retrofit e regra de aplicação dos quadros.', fonte_id='F01', artigo_anexo='Lei 15.511/2019', itens=[
        IT('eiv', 'Estudo de Impacto de Vizinhança', 'EIV Completo, EIV Simplificado ou RAP conforme regulamentação específica; necessário também para densidade acima do art. 212 (CMU) e para usos com nota no quadro (ex.: > 5.000 m²).', 'F01', 'arts. 212 §2º, 227 e 228', 'Limiares do decreto regulamentador do EIV não transcritos (lacuna).'),
        IT('conjuntos', 'Conjuntos habitacionais', 'Conjuntos de habitação coletiva ou em série apenas em lotes até 20.000 m² (flexibilizável pelo art. 169); densidade 100 × CA uh/ha nas zonas residenciais (art. 212).', 'F01', 'arts. 169, 209 a 212'),
        IT('plano_massa', 'Plano Massa (EE)', 'Lotes da via central do EE seguem Plano Massa (art. 11; Lei 16.448 arts. 5º–7º); o CMU pode dispensar (art. 12).', 'F01', 'arts. 11 e 12'),
        IT('estacionamento', 'Estacionamentos', 'Dec. 209/2024: sem novos estacionamentos no SEPE Central/XV e logradouros listados; habitacional facultado no SEPE Barão-Riachuelo; regras para lotes com canaleta.', 'F06', 'Dec. 209/2024 arts. 5º a 7º'),
        IT('vagas_regra', 'Vagas – regra geral', '1 vaga por apartamento (facultado p/ quitinete); +1 vaga/50 UH de visitantes em conjuntos > 100 UH.', 'F05', 'Dec. 2.397/2023 arts. 74 e 75'),
        IT('retrofit', 'Retrofit', 'LC 150/2025 art. 18 (+2 de CA para retrofit no SERC) e Dec. 1.109/2026 (procedimento).', 'F12', 'LC 150/2025 art. 18; Dec. 1.109/2026'),
        IT('macrozona_limites', 'Limites do Plano Diretor', 'Acréscimos máximos de CA por macrozona: eixos +2, ocupação mista +2, residencial média/alta +2, residencial baixa +1, ocupação controlada +1, destinação específica +1; densidades brutas: baixa ≤ 80, média 81–200, alta 201–400 hab/ha.', 'F08', 'Lei 14.771/2015 arts. 20 §2º e 149'),
        IT('consulta', 'Confirmação', 'Consulta Informativa de Lote ("Guia Amarela") da SMU indica zona, setores e parâmetros do lote; prevalece sobre este arquivo.', 'F01', 'Lei 15.511/2019'),
    ])
    resumo_mcmv = [
        'Maior potencial: Eixos Estruturais (EE: CA 4 → 6 com OODC/TDC, HIS COHAB 6, densidade livre, altura livre), ZC (5 → 7, IPU 0,3 para habitacional) e ENC (2 → 3) – terra cara; via central do EE exige Plano Massa.',
        'Equilíbrio MCMV: ZR4, EAC, EMF, EACF, ECL-3 e ECO-1..4 (CA 1,5–2 → 2,5; 6–10 pavimentos com aquisição; HIS COHAB CA 2,5 e 625 uh/ha) – EACF/EACB/ECL-3/EMF com IPU 0,3 (OODC 70% mais barata).',
        'HIS com a COHAB-CT (Dec. 297/2026): isenção de OODC (Lei 16.361 art. 12), +1 pavimento, 1 vaga/4 UH (facultada perto de terminais/estações), lote 125 m², densidade +20% perto do transporte; exige UH para famílias do cadastro COHAB.',
        'ZR3 / ZR3-T / ZUM-1/2/3 / ZSM / ZFR: CA 1–2 → 1,5–3; bons para conjuntos de 4–6 pavimentos em terrenos ≤ 20.000 m² (art. 169). ZR3 ganha mais em vias setoriais (1,8) e coletoras (1,5).',
        'OUC Linha Verde: POLO-LV e SE-LV até CA 4 por CEPAC (densidade livre), ZT-LV e ZR-4-LV até 2,5 (250 uh/ha) – custo do CEPAC e contenção de cheias obrigatória.',
        'Centro (SERC): SBE e ST-04 dão +2 de CA não oneroso para HIS (ST-01 +1; ST-03 +0,5), limitado ao CA máximo da Lei 16.361, e incentivos de IPTU/ITBI/ISS até 2032 (LC 150/2025).',
        'Evitar: ZR1 (só unifamiliar), ZR2 fora do Dec. 297, ZROC-1 (CA 0,4, lote 2.000 m²), ZS-1/ZS-2/ZI/ZPS (sem habitação coletiva), APAs do Iguaçu e do Passaúna (≤ 2–10 uh/ha), UCs, SETP-Largo da Ordem e Pontos Panorâmicos (altura limitada).',
        'Vagas fora da HIS: 1 por apartamento (quitinete facultada) + visitantes 1/50 UH acima de 100 UH (Dec. 2.397/2023) – nas vias do Dec. 209/2024 não se admitem novos estacionamentos.',
    ]
    lacunas = [
        dict(item='Áreas de risco, inundação e APP (camadas públicas)', motivo='Não há camada pública de risco/inundação/APP no Mapa Cadastral público; as camadas do GeoCuritiba "Interno" não foram usadas (acesso interno). Verificar na Guia Amarela/SMMA.'),
        dict(item='Patrimônio (UIP – Unidades de Interesse de Preservação)', motivo='Sem camada pública de UIP localizada; só SETP-Largo da Ordem e zonas ZH.'),
        dict(item='ZI-LV (Zona Industrial da Linha Verde)', motivo='Parâmetros não identificados com segurança no Anexo V/Quadro IX.'),
        dict(item='SEPPFC (Setor Especial de Preservação da Paisagem Ferroviária)', motivo='Parâmetros no Dec. 1.033/2001 – texto não obtido.'),
        dict(item='Coeficiente de ajuste "a" do SEPP', motivo='Lei 15.511 art. 113 §1º remete à localização de cada ponto (Dec. 1.006/2020) – não lido.'),
        dict(item='Limiares do EIV', motivo='Decreto regulamentador dos arts. 227–228 não transcrito.'),
        dict(item='Trechos de Plano Massa do EE', motivo='Plano Massa por trecho não publicado em camada.'),
        dict(item='Via central × vias externas × outras vias do EE', motivo='A camada de zoneamento não distingue as faixas do EE; Quadros I–III indicados como condicionais.'),
        dict(item='Perímetros ZCC-Incentivo, ZR4 Batel/Alto da XV, ZR3-T Mercês/Alto da Glória', motivo='Usados os da camada 35 (sub-áreas); o Anexo I da Lei 16.361 não foi vetorizado.'),
        dict(item='Divergência entre camadas 35 (2022-03) e 36 (Lei 15.511, 2019-10)', motivo='Diferença simétrica ≈ 5,0 km² (0,4 km² na ZCSF, 1,1 km² em UC); adotada a 35 (mais recente).'),
        dict(item='Usos permitidos × permissíveis × tolerados e parâmetros de usos não habitacionais', motivo='Somente a linha "Habitação Coletiva" foi transcrita (foco MCMV).'),
        dict(item='CA mínimo / PEUC', motivo='Sem CA mínimo por zona na Lei 15.511; PEUC depende de lei específica.'),
        dict(item='Lei 14.773/2015 (alterações da OUC-LV) e regulamento de HIS da OUC-LV (art. 9º IV)', motivo='Texto consolidado lido via Lei 13.909 (redações dadas pela 14.773); regulamento de HIS da OUC-LV não localizado.'),
        dict(item='Decretos de setores especiais (Dec. 2.070/2025 SETP-LO; Dec. 673/2002 Tanguá; Dec. 2.027/2021 Vilas de Ofícios)', motivo='Não lidos; camadas incluídas apenas como alerta/informação.'),
        dict(item='Revisão do Plano Diretor (PL 005.00285.2026)', motivo='Em tramitação em 27/10/2026 – não vigente, não usada.'),
        dict(item='Incentivos SERC para eixos EP-TG e EP-SM', motivo='Valores dos arts. 38–43 do Dec. 418/2026 não transcritos.'),
    ]
    geografico = dict(
        descricao='Zonas base = camada 35 (Zoneamento – base cadastral, 2022-03) do Mapa Cadastral público do GeoCuritiba, agrupada pelo código da zona/setor; APAs municipais e setores de sobreposição em camadas complementares. Todas as geometrias são vetores oficiais públicos (ArcGIS REST, sem login).',
        crs='EPSG:4326', crs_area='EPSG:31982', servidor_oficial=MC, camadas=geo_camadas,
        regras_de_consulta='1) Ache a zona base do lote; se cair em mais de uma, cada parte segue sua zona. 2) Verifique a testada: via central/externa do EE, vias setoriais/coletoras (camada sistema_viario_basico) e SEPE alteram o quadro aplicável. 3) Camadas: Dec. 297 (HIS COHAB), SERC, OUC-LV (CEPAC), APAs, UCs, SEPP, SETP-LO. 4) Confirme sempre na Consulta Informativa de Lote (Guia Amarela – SMU).',
        limitacoes=['Camada 35 tem atualização 2022-03; alterações posteriores de zoneamento por lei específica podem faltar.', 'Simplificação ~1 m (zonas) e ~2 m (camadas dissolvidas); coordenadas com 6 casas.',
                    'Sistema viário e SEPE são linhas de eixo de via: o lote deve ter testada para a via.', 'APA do Passaúna recortada ao limite municipal aproximado.', 'Camada 36 (Lei 15.511, 2019) baixada só para comparação.'],
        raio_divisa_m=30, pct_minimo_significativo=0.5,
        notas_tecnicas={'gerador': 'scripts/build_cwb.py', 'download': 'scripts/baixar_camadas.py (outSR=4326, f=geojson, paginação)', 'tabelas': 'scripts/tabelas_cwb.py'})
    MZ = [('I', 'Eixos estruturantes', 'Eixos de transporte de alta capacidade (EE, ENC, Linha Verde).'),
          ('II', 'Eixos de adensamento', 'Eixos de adensamento e conectores (EAC, EMF, EACF, EACB, ECO, ECL, ECS).'),
          ('III', 'Áreas de ocupação residencial de média densidade', 'Zonas residenciais de média densidade.'),
          ('IV', 'Áreas de ocupação residencial de baixa densidade', 'Zonas residenciais de baixa densidade.'),
          ('V', 'Áreas de ocupação mista de alta, média e baixa densidade', 'Zonas de uso misto.'),
          ('VI', 'Áreas de destinação específica', 'Zonas especiais (educacional, militar, serviços, industrial).'),
          ('VII', 'Áreas de ocupação controlada', 'Áreas com restrições ambientais/infraestrutura (ex.: ZROC).'),
          ('VIII', 'Áreas de Proteção Ambiental', 'APA estadual do Passaúna e APA municipal do Iguaçu.')]
    macrozonas = [dict(codigo='MZ-' + c, nome=n, descricao=dsc, parametros={'fundamento': TXT(f'Lei 14.771/2015 art. 20 {c}; densidades brutas (§2º): baixa ≤ 80, média 81–200, alta 201–400 habitações/ha.', None, 'F08', 'Lei 14.771/2015 art. 20 e Anexos 01–02')}) for c, n, dsc in MZ]
    doc = dict(
        schema_versao='1.1', municipio='Curitiba', uf='PR', slug='curitiba-pr', codigo_ibge='4106902', data_levantamento=HOJE,
        centro_mapa=dict(lat=-25.4284, lon=-49.2733, zoom=11),
        orgao_confirmacao='SMU – Secretaria Municipal de Urbanismo (Consulta Informativa de Lote / "Guia Amarela")',
        marco_legal_vigente=('Vigente em 27/10/2026: Plano Diretor Lei 14.771/2015; Zoneamento, Uso e Ocupação do Solo Lei 15.511/2019 (Quadros I–XLIX); potencial construtivo adicional (OODC/TDC/CPC) Lei 16.361/2024; '
                             'prêmios e incentivos Lei 16.448/2024; edificações Dec. 2.397/2023; estacionamentos Dec. 209/2024; HIS COHAB Dec. 297/2026; OUC Linha Verde Lei 13.909/2011 (Lei 14.773/2015); '
                             'Programa Curitiba de Volta ao Centro LC 150/2025 (SERC – Dec. 418/2026; retrofit Dec. 1.109/2026); APAs: Dec. 1.025/2021 e 1.004/2023 (Iguaçu), Dec. 924/2021 (Passaúna). '
                             'Revisão do Plano Diretor em tramitação (não vigente).'),
        fontes=[dict(id=a, titulo=b, lei=c, data=d, url=e, arquivo_local=(('fontes/' + f) if f else None)) for a, b, c, d, e, f in FONTES],
        macrozonas=macrozonas, macrozonas_observacao='Macrozonas do Plano Diretor (Lei 14.771/2015 art. 20) são descritivas (mapas esquemáticos – §1º); sem geometria. Os parâmetros vêm da zona base.',
        zonas=zonas, camadas_complementares=cam, outorga_onerosa=outorga, zeis_his=zeis, outros_parametros=outros_b, resumo_mcmv=resumo_mcmv, geografico=geografico, lacunas=lacunas)
    json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('zonas', len(zonas), 'camadas', len(cam), 'MB', round(os.path.getsize(OUT) / 1e6, 2))

if __name__ == '__main__':
    main()
