#!/usr/bin/env python3
"""Gera goiania-go.json (schema 1.1).
Entradas: geo_raw/*.geojson (baixar_camadas.py – Portal Mapa Goiânia/SEPLANH, ArcGIS REST público),
          tabelas_gyn.py (parâmetros por unidade territorial), comum_gyn.py (fontes e construtores).
Partição das zonas base (ordem de precedência; cada unidade perde a área já atribuída às anteriores):
  ARAU-APP > ARAU-JB > APAC-ABT > APAC-AEBT-* > ARAU-UUS > AOS > ADD > AA > AAB (resíduo da Macrozona Construída) > Macrozonas Rurais.
Uso: python3 build_gyn.py"""
import warnings; warnings.filterwarnings('ignore')
import json, os, sys, collections
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from shapely.validation import make_valid
import pyproj, shapely
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comum_gyn import *
import tabelas_gyn as T

CID = os.path.dirname(HERE); RAW = os.path.join(CID, 'geo_raw'); OUT = os.path.join(CID, 'goiania-go.json')
TOL = 0.00001  # ~1 m
FWD = pyproj.Transformer.from_crs(4326, 31982, always_xy=True).transform
INV = pyproj.Transformer.from_crs(31982, 4326, always_xy=True).transform

def rnd(g):
    def r(c):
        if isinstance(c[0], (list, tuple)): return [r(x) for x in c]
        return [round(c[0], 6), round(c[1], 6)]
    m = mapping(g); return {'type': m['type'], 'coordinates': r(m['coordinates'])}

def _poly(g):
    if g is None: return None
    if g.geom_type == 'GeometryCollection':
        ps = [x for x in g.geoms if x.geom_type in ('Polygon', 'MultiPolygon')]
        return unary_union(ps) if ps else None
    return g if g.geom_type in ('Polygon', 'MultiPolygon') else None

def limpa(g, tol=TOL):
    """Polígono válido, simplificado (~1 m) e ajustado à grade de 1e-6 grau (set_precision garante validade após o arredondamento)."""
    if g is None or g.is_empty: return None
    g = _poly(make_valid(g))
    if g is None: return None
    if tol: g = g.simplify(tol, preserve_topology=True)
    for _ in range(3):
        g = _poly(shapely.set_precision(make_valid(g), 1e-6))
        if g is None or g.is_empty: return None
        gj = rnd(g); g2 = shape(gj)
        if g2.is_valid and not g2.is_empty: return gj
        g = g2.buffer(0)
    return None

def limpa_linha(g, tol=TOL):
    """Linha simplificada e arredondada; descarta trechos que ficam com < 2 pontos distintos."""
    if g is None or g.is_empty: return None
    g = g.simplify(tol)
    from shapely.geometry import LineString, MultiLineString
    partes = []
    for ln in (g.geoms if hasattr(g, 'geoms') else [g]):
        pts = []
        for x, y in ln.coords:
            p = (round(x, 6), round(y, 6))
            if not pts or pts[-1] != p: pts.append(p)
        if len(set(pts)) >= 2: partes.append(LineString(pts))
    if not partes: return None
    out = partes[0] if len(partes) == 1 else MultiLineString(partes)
    return out.is_valid and rnd(out) or None

def le(nome): return json.load(open(os.path.join(RAW, nome + '.geojson')))
def M(f): return _poly(make_valid(transform(FWD, shape(f['geometry'])))) if f.get('geometry') else None
def para_wgs(gm, min_m2=1.0):
    """Polígono métrico -> GeoJSON 4326 limpo; descarta partes < min_m2 (lascas da diferença)."""
    gm = _poly(gm)
    if gm is None or gm.is_empty: return None
    if gm.geom_type == 'MultiPolygon':
        ps = [p for p in gm.geoms if p.area >= min_m2]
        if not ps: return None
        gm = unary_union(ps)
    elif gm.area < min_m2: return None
    return limpa(transform(INV, gm))

def main():
    S = le('ut_simplifica'); MZ = le('me_macrozoneamento'); BT = le('me_bem_tombado_apac'); JB = le('me_arau_jardim_botanico')
    by = collections.defaultdict(list)
    for f in S['features']:
        g = M(f)
        if g is not None and not g.is_empty: by[f['properties']['sigla']].append((f['properties'], g))
    mc = unary_union([M(f) for f in MZ['features'] if f['properties']['sigla'] == 'MC'])
    rurais = collections.defaultdict(list)
    for f in MZ['features']:
        if f['properties']['sigla'] in T.RURAIS: rurais[f['properties']['sigla']].append(M(f))
    # --- unidades candidatas (métricas)
    cand = collections.OrderedDict()
    cand['ARAU-APP'] = [({'nome_base': 'ÁREA DE PRESERVAÇÃO PERMANENTE', 'fonte_camada': 'Simplifica/3 sigla APP'}, g) for p, g in by['APP']]
    cand['ARAU-JB'] = [({'nome_base': f['properties'].get('nm'), 'fonte_camada': 'ModeloEspacial/27'}, M(f)) for f in JB['features']]
    abt, aebt = [], collections.defaultdict(list)
    for f in BT['features']:
        p = f['properties']; g = M(f)
        if g is None: continue
        nome = (p.get('bemtombado') or '').strip() or None
        if p.get('sigla') == 'ABT': abt.append(({'bem_tombado': nome, 'tipo_bem': (p.get('TIPO') or '').strip() or None, 'fonte_camada': 'ModeloEspacial/28 sigla ABT'}, g))
        else: aebt[T.grupo_aebt(nome)].append(({'bem_tombado': nome, 'fonte_camada': 'ModeloEspacial/28 sigla AEBT'}, g))
    cand['APAC-ABT'] = abt
    for c in ['APAC-AEBT-C', 'APAC-AEBT-A', 'APAC-AEBT-B', 'APAC-AEBT-SUB', 'APAC-AEBT-BB', 'APAC-AEBT-ND']:
        cand[c] = aebt.get(c, [])
    cand['ARAU-UUS'] = [({'nome_base': p.get('nm'), 'fonte_camada': 'Simplifica/3 sigla UUS'}, g) for p, g in by['UUS']]
    cand['AOS'] = [({'fonte_camada': 'Simplifica/3 sigla AOS'}, g) for p, g in by['AOS']]
    cand['ADD'] = [({'fonte_camada': 'Simplifica/3 sigla ADD'}, g) for p, g in by['ADD']]
    cand['AA'] = [({'tipo_aa': {1: 'Eixo de Desenvolvimento', 0: 'vazio/PDU ou outra'}.get(p.get('tp_des'), p.get('tp_des')), 'fonte_camada': 'Simplifica/3 sigla AA'}, g) for p, g in by['AA']]
    usado = None; zonas_geo = collections.OrderedDict(); areas = {}
    def corta(lst):
        nonlocal usado
        out = []
        dis = collections.defaultdict(list)
        for pr, g in lst:
            key = json.dumps(pr, sort_keys=True, ensure_ascii=False); dis[key].append(g)
        for key, gs in dis.items():
            u = unary_union([make_valid(x) for x in gs])
            if usado is not None: u = u.difference(usado)
            gj = para_wgs(u, 5.0)
            if gj: out.append((json.loads(key), gj, u.area))
        tot = unary_union([make_valid(g) for pr, g in lst]) if lst else None
        if tot is not None: usado = tot if usado is None else unary_union([usado, tot])
        return out
    for c, lst in cand.items():
        r = corta(lst)
        if r: zonas_geo[c] = r; areas[c] = sum(a for _, _, a in r) / 1e6
    # AAB = resíduo da Macrozona Construída
    aab = mc.difference(usado)
    zonas_geo['AAB'] = [({'fonte_camada': 'resíduo: Macrozona Construída (ModeloEspacial/33) menos as demais unidades'}, para_wgs(aab, 50.0), aab.area)]; areas['AAB'] = aab.area / 1e6
    usado = unary_union([usado, mc])
    for sig in T.RURAIS:
        u = unary_union(rurais[sig]).difference(usado)
        gj = para_wgs(u, 50.0)
        if gj: zonas_geo['MR-' + sig] = [({'nome_base': T.RURAIS[sig][0], 'fonte_camada': 'ModeloEspacial/33 sigla ' + sig}, gj, u.area)]; areas['MR-' + sig] = u.area / 1e6
    for c, a in areas.items(): print(f'{c:16s} {a:9.2f} km2 {len(zonas_geo[c])} feições')

    # --- zonas
    def colecao(c, oficial=True, obs=None, fonte=None):
        feats = []
        for pr, gj, a in zonas_geo[c]:
            p = {'codigo': c}; p.update({k: v for k, v in pr.items() if v is not None}); p['area_m2'] = round(a)
            feats.append(dict(type='Feature', properties=p, geometry=gj))
        return dict(type='FeatureCollection', crs='EPSG:4326 (lon, lat)', fonte=fonte or 'Portal Mapa Goiânia – Simplifica Goiânia Uso do Solo/FeatureServer/3 (F13) e Mapa_ModeloEspacial (F14)',
                    oficial=oficial, observacao_geometria=obs or 'Vetor oficial público (outSR=4326), recortado pela ordem de precedência das unidades; simplificação ~1 m; 6 casas decimais.', features=feats)
    Z = []
    def zona(cod, nome, desc, cat, crit, par, obs, tipo='base', prio=0, regra=None, geo=None):
        Z.append(dict(codigo=cod, nome=nome, descricao=desc, tipo=tipo, prioridade=prio, categoria_normalizada=cat, categoria_criterio=crit, regra_sobreposicao=regra,
                      parametros=par, observacoes=obs, geometria=geo or colecao(cod)))
    CONF = 'Confirmar no Uso do Solo/Consulta Prévia da SEPLANH: a unidade do lote no Modelo Espacial (Anexo XIV) prevalece sobre este arquivo.'
    zona('AA', 'Área Adensável (AA)', 'Eixos de Desenvolvimento (~350 m dos corredores exclusivos/preferenciais) e vazios ocupados por PDU/Conjunto (LC 349/2022 art. 159; LC 371/2024 art. 63 – o Anexo XIV prevalece).',
         'mista_alta_densidade', 'IA 6 (7,5 com TDC) > 3, sem altura máxima nem controle de densidade → alta densidade (critério CA máx.: ≤1,5 baixa; ≤3 média; >3 alta).', T.aa(),
         ['Geometria: Simplifica/3 sigla AA (tp_des 1 = Eixo de Desenvolvimento; 0 = demais).', 'Lotes lindeiros a corredor exclusivo: vagas facultadas (LC 364 art. 110 §8º) e recuo de 18 m do eixo da via (art. 183 §10).', CONF])
    zona('ADD', 'Área de Desaceleração de Densidade (ADD)', 'Áreas consolidadas de alta densidade onde se desacelera o adensamento (LC 349/2022 art. 158).', 'mista_alta_densidade',
         'IA 5 > 3 → alta densidade.', T.add(), ['Geometria: Simplifica/3 sigla ADD (7 polígonos – Setores Oeste, Bueno, Marista e vizinhos).', CONF])
    zona('AAB', 'Área de Adensamento Básico (AAB)', 'Demais áreas da Macrozona Construída não enquadradas nas outras unidades (LC 349/2022 art. 157).', 'residencial_media_densidade',
         'Sem IA fixado; altura 12 m com TO 100% e 1 UH/90 m² (111 uh/ha); HIS IA 2 → média densidade.', T.aab(),
         ['Geometria DERIVADA: Macrozona Construída (ModeloEspacial/33) menos AA, ADD, AOS, UUS, APAC, APP e Jardim Botânico – é a definição legal (art. 157), mas não é uma camada publicada (oficial:false).',
          'Lacunas na base (áreas verdes, UPI e ARCT urbanas não publicadas no serviço) caem aqui – confirmar.', CONF])
    Z[-1]['geometria'] = colecao('AAB', False, 'Derivada por diferença de vetores oficiais (EPSG:31982); erro estimado ≈ erro das camadas de origem (~1–5 m), mais áreas verdes/UPI não publicadas que caem na AAB.')
    zona('AOS', 'Área de Ocupação Sustentável (AOS)', 'Faixas de transição (≥ 100 m) junto às APPs e antigas UUS da LC 171/2007 (LC 349/2022 art. 150).', 'residencial_baixa_densidade',
         'Sem IA; TO 40%, 12 m e 1 UH/180 m² (55,6 uh/ha) → baixa densidade.', T.aos(), ['Geometria: Simplifica/3 sigla AOS (2.038 polígonos, sobreposições internas dissolvidas).', CONF])
    zona('ARAU-UUS', 'ARAU – Unidade de Uso Sustentável (UUS)', 'Polígonos "Unidade de Uso Sustentável" da base (ARAU – unidades de conservação de uso sustentável, art. 145).', 'ambiental',
         'Área ambiental com ocupação restrita (TO 40%, 12 m, permeabilidade 25%).', T.arau_ocupavel('ARAU-UUS'),
         ['Na base Simplifica a sigla UUS tem cd_sis igual ao da AOS; pode tratar-se de UUS da LC 171/2007 que o art. 150 II/III converte em AOS – parâmetros idênticos aos da AOS nos pontos tratados aqui.', CONF])
    zona('ARAU-APP', 'ARAU – Área de Preservação Permanente (APP)', 'APPs de cursos d\'água, nascentes e demais (LC 349/2022 art. 143; Código Florestal), urbanas e rurais (ARAR – art. 202 I).', 'ambiental',
         'Não edificável.', T.nao_edificavel('APP', 'LC 349/2022 arts. 142, 143 e 202'),
         ['Geometria: Simplifica/3 sigla APP (inclui APPs da zona rural).', 'A faixa real depende da largura do curso d\'água e do levantamento no local (Código Florestal).'])
    zona('ARAU-JB', 'ARAU – Jardim Botânico', 'Jardim Botânico Amália Hermano Teixeira (LC 349/2022 art. 149).', 'ambiental', 'Não edificável.', T.nao_edificavel('Jardim Botânico', 'LC 349/2022 arts. 149 e 163'),
         ['Geometria: Mapa_ModeloEspacial/27.'])
    zona('APAC-ABT', 'APAC – Área do Bem Tombado (ABT)', 'Bens tombados (União, Estado, Município) e seus terrenos (LC 349/2022 art. 153 I; Anexo XX).', 'patrimonio_cultural',
         'Bem tombado – parâmetros do órgão de tombamento.', T.abt(), ['Geometria: Mapa_ModeloEspacial/28 sigla ABT (82 feições, com o nome do bem em properties.bem_tombado).'])
    for c, g in T.AEBT_GRUPOS.items():
        if c not in zonas_geo: continue
        zona(c, g['nome'], f"Área de Entorno do Bem Tombado – {g['bens']} (LC 349/2022 arts. 153 II, 181, 188 e Anexo XXII).", 'patrimonio_cultural',
             'Entorno de bem tombado – altura e recuos do Anexo XXII.', T.aebt(c),
             ['Geometria: Mapa_ModeloEspacial/28 sigla AEBT; o grupo foi atribuído pelo nome do bem (properties.bem_tombado) × linha do Anexo XXII (leitura do analista).',
              'Obras e demolições dependem de anuência do ente cultural (IPHAN/IPHAN-GO/Município – art. 154).', CONF] + (['"Centro Cultural CELG – Eng. Oton" associado à linha "Subestação Goiânia" do Anexo XXII (mesmo imóvel – confirmar).'] if c == 'APAC-AEBT-SUB' else []))
    for sig, (nome, fr) in T.RURAIS.items():
        c = 'MR-' + sig
        if c not in zonas_geo: continue
        zona(c, nome, f'{nome} – solo rural (LC 349/2022 arts. 197 a 208); chácaras a partir de {fr:,} m² (art. 197 par. único).'.replace(',', '.'), 'rural', 'Macrozona rural – habitação coletiva não se aplica.', T.rural(sig),
             ['Geometria: Mapa_ModeloEspacial/33 (macrozoneamento) menos APPs.', 'Partes podem ser convertidas a urbano por OOAU (camada ooau – art. 249; Anexo XI).'])
    # --- sobrepostas
    bases = [z['codigo'] for z in Z]
    A = le('me_aeis'); fe = []
    dis = collections.defaultdict(list)
    for f in A['features']:
        p = f['properties']; g = M(f)
        if g is None: continue
        per = 'anterior à LC 171/2007' if 'ANTERIOR' in p['NM'] else ('pós LC 171/2007' if '171' in p['NM'] else 'pós LC 349/2022')
        dis[(per, (p.get('NM2') or '').strip() or None)].append(g)
    zonas_geo['AEIS-III'] = []
    for (per, dec), gs in dis.items():
        u = unary_union(gs); gj = para_wgs(u, 5.0)
        if gj: zonas_geo['AEIS-III'].append(({'periodo': per, 'ato': dec, 'fonte_camada': 'ModeloEspacial/7'}, gj, u.area))
    zona('AEIS-III', 'Área Especial de Interesse Social III (AEIS III)', 'Imóveis destinados a empreendimentos habitacionais de interesse social (Lei 11.083/2023; LC 349/2022 art. 212 III red. LC 379/2024 art. 24); novas AEIS III por decreto.',
         'especial_interesse_social', 'Gravame de HIS (≥ 80% HIS): IA 2, 1 UH/30 m², altura pela tabela da AA.', T.aeis3(),
         ['Geometria: Mapa_ModeloEspacial/7 (115 polígonos, inclui decretos de 2025/2026); a camada Simplifica/3 tem 109 AEIS III (versão anterior).',
          'Os parâmetros valem para empreendimentos de HIS (LC 379/2024); usos não HIS seguem a unidade de base.', CONF],
         tipo='sobreposta', prio=30,
         regra=dict(efeito='substitui', usa_indices_de=None, aplica_sobre=['AA', 'ADD', 'AAB', 'AOS'], limiar_pct=None, requer_testada=False, distancia_max_m=None,
                    fundamento='Lei 11.083/2023 arts. 22–34; LC 379/2024 art. 14 §1º IV (fração 30 m², tabela de alturas da AA, IA 2); em AOS/APA vale 180 m² (art. 14).',
                    alerta='Imóvel gravado como AEIS III: ≥ 80% da área em HIS (Lei 11.083 art. 31); OODC e ITBI isentos para HIS (LC 379 arts. 10–11). Em APP/APAC/ARAU prevalece a unidade de base.',
                    mantem_da_base=['taxa_permeabilidade', 'recuos.frontal', 'recuos.lateral', 'recuos.fundos', 'usos_permitidos']),
         geo=colecao('AEIS-III', True, None, 'Portal Mapa Goiânia – Mapa_ModeloEspacial/MapServer/7 (F14)'))
    apa = [(p, g) for p, g in by['APA']]
    zonas_geo['ARAU-APA'] = []
    for p, g in apa:
        gj = para_wgs(g, 5.0)
        if gj: zonas_geo['ARAU-APA'].append(({'nome_base': p.get('nm'), 'fonte_camada': 'Simplifica/3 sigla APA'}, gj, g.area))
    zona('ARAU-APA', 'ARAU – Área de Proteção Ambiental (APA)', 'APAs municipais/estaduais (Alto Anicuns, Morro do Mendanha, João Leite, Ribeirão São Domingos) – integram a ARAU na Macrozona Construída (art. 179 II).',
         'ambiental', 'Ocupação só após Plano de Manejo; 1 UH/180 m² → baixa densidade/ambiental.', T.apa(),
         ['Geometria: Simplifica/3 sigla APA (4 polígonos; grande parte na zona rural).', 'Em APP prevalece a APP.', CONF], tipo='sobreposta', prio=40,
         regra=dict(efeito='substitui', usa_indices_de=None, aplica_sobre=[c for c in bases if c not in ('ARAU-APP', 'ARAU-JB', 'APAC-ABT')] + ['AEIS-III'], limiar_pct=None, requer_testada=False, distancia_max_m=None,
                    fundamento='LC 349/2022 arts. 121, 179 II e §3º, 190 §3º, 194 e 200; LC 379/2024 art. 14 (HIS em APA: 180 m²).',
                    alerta='Imóvel em APA: ocupação/parcelamento só após o Plano de Manejo (art. 179 §3º); na zona rural é proibido sítio de recreio em APA (art. 200). Exige licenciamento ambiental.', mantem_da_base=[]),
         geo=colecao('ARAU-APA', True, None, 'Portal Mapa Goiânia – Simplifica Goiânia Uso do Solo/FeatureServer/3 (F13)'))
    print('zonas', len(Z))

    # ---------------------------------------------------------------- camadas
    cam = {}; geo_camadas = []
    def add_geo(nome, arquivo, url, n, oficial=True, metodo='vetor oficial'):
        geo_camadas.append(dict(nome=nome, arquivo='geo_raw/' + arquivo + '.geojson', fonte_url=url, data_download=HOJE, oficial=oficial, metodo=metodo, erro_estimado_m=None, n_feicoes=n))
    def feats(d, fcod, props=None, tol=TOL):
        out = []
        for f in d['features']:
            if not f.get('geometry'): continue
            g = shape(f['geometry'])
            gj = limpa_linha(g, tol) if 'Line' in g.geom_type else limpa(g, tol)
            if gj is None: continue
            p = f['properties']; pr = {'codigo': fcod(p)}
            pr.update({k: (p.get(k).strip() if isinstance(p.get(k), str) else p.get(k)) for k in (props or []) if p.get(k) not in (None, ' ', '')})
            out.append(dict(type='Feature', properties=pr, geometry=gj))
        return out
    def camada(nome, papel, desc, fonte, fid, art, fe, ppc=None, al=None, obs=None):
        cam[nome] = dict(papel=papel, descricao=desc, fonte=fonte, oficial=True, fonte_id=fid, artigo_anexo=art, observacao=obs, parametros_por_codigo=ppc, alerta_por_codigo=al, features=[f for f in fe if f['geometry']])
    add_geo('Unidades territoriais – Simplifica Goiânia Uso do Solo (zonas base)', 'ut_simplifica', SIMP + '/3', len(S['features']))
    add_geo('Macrozoneamento (Macrozona Construída, 7 rurais e OOAU)', 'me_macrozoneamento', ME + '/33', len(MZ['features']))
    add_geo('Áreas de Patrimônio Cultural – APAC (ABT e AEBT)', 'me_bem_tombado_apac', ME + '/28', len(BT['features']))
    add_geo('Jardim Botânico', 'me_arau_jardim_botanico', ME + '/27', len(JB['features']))
    add_geo('AEIS III (Programas Especiais de Interesse Social)', 'me_aeis', ME + '/7', len(A['features']))
    # macrozoneamento
    MZN = {'MC': 'Macrozona Construída', **{k: v[0] for k, v in T.RURAIS.items()}}
    fe = feats(dict(features=[f for f in MZ['features'] if f['properties']['sigla'] != 'OOAU']), lambda p: p['sigla'], ['nm'])
    camada('macrozoneamento', 'macrozona', 'Macrozona Construída (urbana) e as sete Macrozonas Rurais (LC 349/2022 arts. 130–131 e Anexo XIV).', 'Mapa_ModeloEspacial/33', 'F14', 'LC 349/2022 art. 131 e Anexo XIV', fe,
           {c: {'macrozona': TXT(n, None, 'F01', 'LC 349/2022 art. 131')} for c, n in MZN.items() if any(f['properties']['codigo'] == c for f in fe)})
    d = le('me_ooau')
    camada('ooau', 'informativa', 'Áreas rurais passíveis de Outorga Onerosa de Alteração de Uso (rural → urbano) – Anexo XI.', 'Mapa_ModeloEspacial/32', 'F01', 'LC 349/2022 arts. 249 e 250; Anexo XI',
           feats(d, lambda p: 'OOAU'), {'OOAU': {'ooau_contrapartida': TXT('Alteração de uso rural→urbano mediante contrapartida (art. 249); TDC pode substituir a OOAU à razão de 1,62% da área (§§8º–11, red. LC 373/2024 art. 10) – suspensa para novas TDC (Dec. 82/2026 art. 1º §1º).', None, 'F01', 'LC 349/2022 art. 249; LC 373/2024 art. 10; Dec. 82/2026')}},
           None, 'Parcelamento urbano nessas áreas só após OOAU aprovada; até lá valem os parâmetros rurais.')
    add_geo('OOAU (Anexo XI)', 'me_ooau', ME + '/32', len(d['features']))
    d = le('me_ive')
    fe = feats(d, lambda p: 'IVE', ['nm_ive', 'tp_ive'])
    camada('ive', 'informativa', 'Áreas de Influência das Vias Expressas (IVE) – Anexo XVI.', 'Mapa_ModeloEspacial/5', 'F01', 'LC 349/2022 art. 189; Anexo XVI; Lei 10.845/2022', fe,
           {'IVE': {'efeito': TXT('A IVE regula apenas usos e grau de incomodidade das atividades econômicas (art. 189); os índices de ocupação são os da unidade territorial de base.', None, 'F01', 'LC 349/2022 art. 189')}}, None)
    add_geo('IVE (Anexo XVI)', 'me_ive', ME + '/5', len(d['features']))
    d = le('me_corredores')
    fe = feats(d, lambda p: (p.get('tp_cor') or 'Corredor').strip().upper().replace(' ', '_'), ['nm_cor', 'tp_cor', 'Eixo_Desen'])
    cods = sorted({f['properties']['codigo'] for f in fe})
    REC = {'CORREDOR_PREFERENCIAL': 15, 'CORREDOR_EXCLUSIVO': 18, 'CORREDOR_ESTRATÉGICO': 18, 'CORREDOR_ESTRATEGICO': 18}
    camada('corredores', 'restricao', 'Corredores estruturadores da macro rede viária (exclusivos, preferenciais, estratégicos) – linhas de eixo.', 'Mapa_ModeloEspacial/1', 'F01', 'LC 349/2022 art. 183 §§6º–10; LC 364/2023 art. 110 §8º', fe,
           {c: {'distancia_eixo_m': (P(REC[c], 'm', 'F01', 'LC 349/2022 art. 183 §10', 'Distância mínima bilateral entre o início da edificação (inclusive subsolo) e o eixo da via.') if c in REC else
                                     SEM('m', 'Tipo de corredor sem regra própria identificada.', 'LC 349/2022 art. 183 §10'))} for c in cods},
           {c: (f"Lote lindeiro a {c.replace('_', ' ').lower()}: manter {REC[c]} m do eixo da via (art. 183 §10)" + ('; em AA, vagas facultadas (LC 364 art. 110 §8º).' if REC.get(c) == 18 else '.')) if c in REC else 'Corredor da macro rede viária – verificar recuo especial (art. 183 §10).' for c in cods},
           'Linhas de eixo: aplicar só a lotes com testada para o corredor; área de reserva para alargamento pode ser exigida (art. 183 §§6º–8º).')
    add_geo('Corredores (linhas)', 'me_corredores', ME + '/1', len(d['features']))
    d = le('me_eixo_desenvolvimento')
    camada('eixos_desenvolvimento', 'informativa', 'Eixos de Desenvolvimento (corredores que geram a AA com faixa de ~350 m) – linhas.', 'Mapa_ModeloEspacial/4', 'F01', 'LC 349/2022 arts. 159 I, 244 §2º e 252 §1º',
           feats(d, lambda p: 'EIXO_DESENVOLVIMENTO', ['nm_cor']), {'EIXO_DESENVOLVIMENTO': {'tdc': TXT('Nos imóveis de AA dos Eixos de Desenvolvimento o potencial de TDC é isento de OODC (art. 244 §2º) e pode acrescer até 25% da altura (art. 252 §1º) – novas TDC suspensas (Dec. 2.785/2025; Dec. 82/2026).', None, 'F01', 'LC 349/2022 arts. 244 §2º e 252')}}, None)
    add_geo('Eixos de Desenvolvimento (linhas)', 'me_eixo_desenvolvimento', ME + '/4', len(d['features']))
    d = le('me_declividade30')
    camada('declividade_30', 'restricao', 'Áreas com declividade acima de 30% (contornos – linhas).', 'Mapa_ModeloEspacial/2', 'F01', 'LC 349/2022 art. 121 II; Lei federal 6.766/1979 art. 3º par. único III', feats(d, lambda p: 'DECLIVIDADE_30'),
           None, {'DECLIVIDADE_30': 'Declividade > 30%: parcelamento só com exigências específicas (Lei 6.766/1979); em APA lote mínimo 1.250 m² e 1 economia (art. 121 II).'}, 'A camada pública traz só os contornos (linhas) – verificar se o lote está dentro do contorno.')
    add_geo('Declividade > 30% (linhas)', 'me_declividade30', ME + '/2', len(d['features']))
    fe = []
    for arq, cod in [('me_aero_aproximacao', 'AERO_APROXIMACAO'), ('me_aero_ruido', 'AERO_RUIDO'), ('me_aero_seguranca', 'AERO_SEGURANCA')]:
        d = le(arq); fe += feats(d, lambda p, cod=cod: cod, ['tp_ara', 'nm_ara']); add_geo(f'Restrição aeroportuária – {cod}', arq, ME + '/' + {'me_aero_aproximacao': '38', 'me_aero_ruido': '39', 'me_aero_seguranca': '40'}[arq], len(d['features']))
    camada('restricao_aeroportuaria', 'restricao', 'Restrições aeroportuárias (áreas de aproximação, cone de ruído e área de segurança) – grupo "Plano Diretor 2007" do Portal Mapa.', 'Mapa_ModeloEspacial/38–40', 'F14', 'Planos de zona de proteção de aeródromo (COMAER/DECEA – Portaria 957/GC3); camada municipal de referência', fe, None,
           {'AERO_APROXIMACAO': 'Superfície de aproximação de aeródromo: altura da edificação limitada pelo Plano Básico de Zona de Proteção – consulta ao COMAER/DECEA (AGA).', 'AERO_RUIDO': 'Cone de ruído: restrições de uso (habitação pode ser incompatível conforme o Plano de Zoneamento de Ruído).', 'AERO_SEGURANCA': 'Área de segurança aeroportuária: atividades atrativas de fauna e edificações sujeitas a análise.'},
           'Camadas publicadas no grupo do Plano Diretor de 2007 (referência); a regra vigente é federal (DECEA) – não se usou a portaria para índices.')
    d = le('me_restricao_militar')
    camada('restricao_militar', 'restricao', 'Áreas de restrição militar (Decreto-Lei 3.437/1941 – 1ª zona 15 braças/33 m, 2ª zona 600 braças/1.320 m).', 'Mapa_ModeloEspacial/44', 'F14', 'Decreto-Lei federal 3.437/1941 arts. 1º e 2º',
           feats(d, lambda p: 'MILITAR_' + ({'1ª Zona': 'I', '2ª Zona': 'II'}.get((p.get('in_zona') or '').strip(), 'PERIMETRO')), ['nm_arm', 'in_zona', 'in_metros', 'obs']), None,
           {'MILITAR_I': 'Restrição militar 1ª zona (33 m): construções dependem de autorização do Exército.', 'MILITAR_II': 'Restrição militar 2ª zona (1.320 m): edificações sujeitas a anuência do Ministério da Defesa/Exército.', 'MILITAR_PERIMETRO': 'Perímetro da Vila Militar (referência).'},
           'Camada do grupo "Plano Diretor 2007" do Portal Mapa (referência).')
    add_geo('Restrição militar', 'me_restricao_militar', ME + '/44', len(d['features']))
    fe = []; nomes = {}
    for arq, cod, lid in [('me_pe_urbanistico', 'PE_URBANISTICO', 8), ('me_pe_ambiental', 'PE_AMBIENTAL', 9), ('me_pe_economico', 'PE_ECONOMICO', 10)]:
        d = le(arq); fe += feats(d, lambda p, cod=cod: cod, ['NM2']); add_geo(f'Programas Especiais – {cod}', arq, ME + f'/{lid}', len(d['features']))
    camada('programas_especiais', 'informativa', 'Áreas de Programas Especiais de interesse urbanístico (Setores Central, Campinas e Sul), ambiental e econômico (Aerotrópole, polos, AUE).', 'Mapa_ModeloEspacial/8–10', 'F01', 'LC 349/2022 arts. 209 a 214; art. 120 V',
           fe, None, {'PE_URBANISTICO': 'Área de Programa Especial de Interesse Urbanístico: parâmetros diferenciados por lei específica (art. 120 V; art. 196 §4º) – não identificada lei em vigor para índices.',
                      'PE_AMBIENTAL': 'Área de Programa Especial de Interesse Ambiental (parques, Meia Ponte, aterro): restrições ambientais – consultar AMMA.',
                      'PE_ECONOMICO': 'Área de Programa Especial de Interesse Econômico: uso econômico prioritário; habitação pode ser restrita (lei específica).'})
    d = le('me_aede')
    camada('aede', 'informativa', 'Área Especial de Desenvolvimento Econômico (faixas ao longo de rodovias na zona rural).', 'Mapa_ModeloEspacial/12', 'F01', 'LC 349/2022 arts. 201 III e 208', feats(d, lambda p: 'AEDE', ['NM']), None,
           {'AEDE': 'AEDE: atividades econômicas impactantes/macroprojetos por ato da SEPLANH (art. 197 par. único III); faixa definida caso a caso (art. 208 §2º).'})
    add_geo('AEDE', 'me_aede', ME + '/12', len(d['features']))
    d = le('me_arar_app')
    camada('arar_app', 'restricao', 'APPs da zona rural (ARAR) publicadas no Modelo Espacial.', 'Mapa_ModeloEspacial/14', 'F01', 'LC 349/2022 arts. 202 e 203', feats(d, lambda p: 'ARAR_APP'), None,
           {'ARAR_APP': 'APP rural (ARAR – preponderante, art. 201 §1º): não edificável.'}, 'Complementa a APP da zona base (Simplifica).')
    add_geo('ARAR – APP rural', 'me_arar_app', ME + '/14', len(d['features']))
    for arq, lid in [('me_limite_municipio', 34), ('me_arau_app', 21), ('me_arar_uus', 18), ('med_bem_tombado', None), ('med_entorno_bem_tombado', None)]:
        d = le(arq); add_geo(f'{arq} (baixada para conferência, não usada)', arq, d.get('meta', {}).get('fonte_url') or ME + f'/{lid}', len(d['features']))

    # ---------------------------------------------------------------- blocos
    def I(chave, titulo, *a, **k): return dict(chave=chave, titulo=titulo, **P(*a, **k))
    def IT(chave, titulo, texto, fonte, art, obs=None): return dict(chave=chave, titulo=titulo, **TXT(texto, None, fonte, art, obs))
    outorga = dict(resumo='OODC incide sobre a área privativa que excede 1× a área do terreno (CA básico não oneroso, arts. 242–244) até o IA da unidade (AA 6; ADD 5). Contrapartida VOO = Vm × Vi × Qsc (LC 373/2024). HIS isenta (LC 379 art. 10); AEBT isento (art. 244 §1º II).',
                   fonte_id='F04', artigo_anexo='LC 349/2022 arts. 241 a 250; LC 373/2024', itens=[
        I('formula_oodc', 'Contrapartida da OODC', None, 'R$', 'F04', 'LC 373/2024 art. 4º', 'Vm = razão do CUB R16 (SINDUSCON-GO): 50% Grupo I, 40% Grupo II, 30% Grupo III; Vi por unidade; Qsc = m² de solo criado.', forma='formula', formula='VOO = Vm * Vi * Qsc'),
        I('vi_aa', 'Vi – AA e PDU I', 0.10, None, 'F04', 'LC 373/2024 art. 4º §2º I'), I('vi_aab', 'Vi – AAB, PDU II/III e Conjuntos', 0.15, None, 'F04', 'art. 4º §2º II'),
        I('vi_add', 'Vi – ADD', 0.20, None, 'F04', 'art. 4º §2º III'), I('vi_aos', 'Vi – AOS, APAC e PDU IV', 0.30, None, 'F04', 'art. 4º §2º IV'),
        I('vm_grupo1', 'Vm – Grupo I (razão do CUB R16)', 0.5, 'fracao', 'F04', 'art. 4º §3º I'), I('vm_grupo2', 'Vm – Grupo II', 0.4, 'fracao', 'F04', 'art. 4º §3º II'), I('vm_grupo3', 'Vm – Grupo III', 0.3, 'fracao', 'F04', 'art. 4º §3º III'),
        IT('grupo1_setores', 'Grupo I – setores', 'Serrinha, Jardim Goiás, Alto da Glória, Oeste, Marista, Bueno, Nova Suíça, Bela Vista, Central, Campinas, Coimbra, Aeroporto, Sul, Sudoeste, Jardim América, Leste Universitário, Pedro Ludovico, Parque Amazônia, Jaó, Jardim Atlântico, Norte Ferroviário e Norte Ferroviário II.', 'F04', 'LC 373/2024 Anexo – Grupo I'),
        IT('grupo2_3', 'Grupos II e III', 'Grupo II: lista do Anexo (Jardim Guanabara, Jardim Europa, Cidade Jardim, Vila Negrão de Lima, Leste Vila Nova, Funcionários, Fama, Centro-Oeste, Marechal Rondon etc.). Grupo III: lista do Anexo + conjuntos habitacionais não citados + demais setores (art. 4º §5º).', 'F04', 'LC 373/2024 art. 4º §§4º–5º e Anexo'),
        IT('pagamento', 'Pagamento', 'Até 5 parcelas trimestrais; até 60% em bens/obras/serviços; validade de 2 anos (renovável); CCO só após quitação; templos isentos (art. 1º §2º).', 'F04', 'LC 373/2024 arts. 1º, 5º, 6º e 8º'),
        IT('cpc_s', 'TDC/CPC-S em substituição à OODC', 'CPC-S pode substituir até 50% da contrapartida da OODC (após os 120 dias iniciais) e até 25% da altura no receptor; novas concessões de TDC suspensas desde 01/01/2025 por 18 meses e prorrogadas por mais 18 meses a partir de 01/07/2026 (inclusive para OOAU).', 'F10', 'Dec. 2.785/2025 arts. 2º e 4º; Dec. 82/2026 art. 1º'),
        IT('isencoes', 'Isenções', 'Habitação coletiva com fachada ativa no Setor Central; edificações no AEBT; potencial de TDC em AA dos Eixos e PDU; área de fachada ativa; HIS (LC 379 art. 10).', 'F01', 'LC 349/2022 art. 244 §§1º–2º; LC 379/2024 art. 10'),
        IT('ooau', 'Outorga Onerosa de Alteração de Uso (OOAU)', 'Conversão de áreas rurais do Anexo XI em urbanas mediante contrapartida (art. 249); ver camada ooau.', 'F01', 'LC 349/2022 arts. 249 e 250'),
        IT('tdc', 'TDC', 'Lei 10.848/2022 (art. 14 red. LC 373/2024): TDC substitui contrapartida da OODC nos casos da Lei 9.123/2011 e de desapropriação/doação de interesse público; potencial de parques do PUAMA escriturados até 2013 pode ser usado em ADD.', 'F09', 'Lei 10.848/2022 art. 14'),
    ])
    zeis = dict(resumo='HIS em Goiânia: LC 379/2024 (parâmetros especiais para HIS de programas como o MCMV – Lei 14.620/2023), AEIS I/II (Reurb-S) e AEIS III (empreendimentos HIS) da Lei 11.083/2023; isenção de OODC e ITBI.',
                fonte_id='F05', artigo_anexo='LC 379/2024; Lei 11.083/2023; LC 349/2022 arts. 211–212', itens=[
        IT('his_fracao', 'Fração ideal HIS', '30 m² em vazios do Grupo I (Anexo XXIII) e do Grupo III (Lei 9.123), quitinete em AAB e em AEIS; 180 m² em AOS e APA; 45 m² nos demais casos; sem controle em AA/ADD.', 'F05', 'LC 379/2024 art. 14'),
        IT('his_ia', 'Índice de aproveitamento HIS', 'IA 2 em AAB ou AEIS (exceto zoneamento ambiental), ampliável com TDC (§2º); em AEIS aplica-se a tabela de alturas da AA (art. 14 IV); AAB mantém 12 m.', 'F05', 'LC 379/2024 art. 14 §§1º–2º'),
        I('his_vagas', 'Vagas HIS', 0.3333, 'vagas/UH', 'F05', 'LC 379/2024 art. 16', '1 vaga a cada 3 UH; até 30% motos; facultadas em corredor exclusivo na AA (§4º); fachada ativa ≤ 180 m² dispensada.'),
        I('his_uh_max', 'Área privativa máxima da UH', 70, 'm2', 'F05', 'LC 379/2024 art. 16'),
        IT('his_isencoes', 'Isenções', 'Isenção de OODC (art. 10) e de ITBI para FAR/FDS/FNHIS (art. 11).', 'F05', 'LC 379/2024 arts. 10 e 11'),
        IT('his_vias', 'Vias internas', 'Vias internas de pedestre 6 m e de pista 5 m (art. 20).', 'F05', 'LC 379/2024 art. 20'),
        IT('aeis_12', 'AEIS I e II (Reurb-S)', 'Lote 90 m²/5 m (AOS 180 m²/6 m); 1 UH/90 m² (AOS 180 m²; quitinete 30 m²).', 'F06', 'Lei 11.083/2023 arts. 8º e 10'),
        IT('aeis_3', 'AEIS III', 'Parcelamento 150 m²/6 m (AOS 180 m²); ≥ 80% da área em HIS e até 20% para atividades/fachada ativa; prioridade a famílias de até 5 SM em PPP; modalidade fechada com faixa permeável de 2 m; novas AEIS III por decreto (art. 212 III red. LC 379).', 'F06', 'Lei 11.083/2023 arts. 24, 31 e 34; LC 379/2024 art. 24'),
        IT('eiv_eit', 'EIV/EIT', 'Empreendimento residencial de interesse social isento de EIT (art. 267 §2º); EIV só nos casos do art. 5º da Lei 11.127/2024.', 'F01', 'LC 349/2022 art. 267 §2º'),
    ])
    outros_b = dict(resumo='EIV/RIV, EIT, PDU (vazios urbanos), vagas, distâncias entre blocos e regras de aplicação.', fonte_id='F01', artigo_anexo='LC 349/2022', itens=[
        IT('eiv', 'EIV/RIV', 'Obrigatório para macroprojetos; atividades com reunião > 600 pessoas; mercados > 2.000 m²; ensino > 360 m² ou > 100 alunos/turno; terminais; estações; aeródromos; OUC; torres; atividades do Anexo I. Simplificado < 540 m²/< 600 pessoas; edifícios multiatividade em AA/ADD fora do inciso II; dispensas no art. 6º.', 'F08', 'Lei 11.127/2024 arts. 5º a 7º; LC 349/2022 art. 262'),
        IT('eit', 'EIT/RIT (polo gerador de tráfego)', 'Habitação seriada/coletiva, conjunto ou PDU com mais de 500 vagas; habitação coletiva em ADD com mais de 300 vagas; loteamento/condomínio > 700 lotes; HIS isenta.', 'F01', 'LC 349/2022 art. 267 (red. LC 363/2023 e LC 379/2024)'),
        IT('pdu', 'Vazios urbanos – PDU e Conjuntos', 'PDU I: IA 6 (7,5 com TDC), fração livre; PDU II e PDU III Grupo III: 30 m²; PDU III Grupo II e outros vazios: 60 m²; PDU IV: 180 m² (LC 371/2024). Vazios no AEBT não podem ser PDU (art. 159 §2º).', 'F03', 'LC 371/2024 art. 17 e demais; LC 349/2022 arts. 159 e 174'),
        IT('vagas', 'Vagas (Código de Obras)', 'Coletiva/quitinete: 1 vaga/100 m² de área privativa total; demais: 1/UH; visitantes: 0 (≤ 9 UH), 1 (10–25), 2 (26–100), +1/100 UH; 2% acessíveis; corredor exclusivo em AA: facultadas.', 'F07', 'LC 364/2023 arts. 110 e 111'),
        IT('afastamento_blocos', 'Distância entre blocos', 'Acima de 7,5 m de altura, a distância entre edificações no mesmo lote é o dobro do recuo lateral do Anexo XXI.', 'F01', 'LC 349/2022 art. 182'),
        IT('pub', 'Plano Urbanístico Básico (PUB)', 'Projeto urbanístico global em área mínima de 50 ha, por etapas (prazo 20 + 10 anos); na Macrozona Rural não converte o solo em urbano – exige OOAU a cada etapa; modalidades de ocupação seguem o Plano Diretor.', 'F16', 'Dec. 117/2026 arts. 1º a 5º; LC 363/2023 arts. 135–146'),
        IT('ouc', 'Operação Urbana Consorciada', 'Prevista no Plano Diretor como instrumento; nenhuma OUC em vigor identificada.', 'F01', 'LC 349/2022 (instrumentos)'),
        IT('consulta', 'Confirmação', 'O Uso do Solo / Consulta Prévia emitido pela SEPLANH prevalece sobre este arquivo.', 'F01', 'LC 349/2022'),
    ])
    resumo_mcmv = [
        'Maior potencial: AEIS III (gravame HIS) – IA 2, 1 UH/30 m² (≈ 333 uh/ha), altura pela tabela da AA, 1 vaga/3 UH, isenções de OODC e ITBI; 115 polígonos no Modelo Espacial (decretos até 2026).',
        'AA (Eixos de Desenvolvimento ~350 m dos corredores): IA 6, sem altura máxima e sem controle de densidade; HIS com vaga facultada em corredor exclusivo; OODC mais barata (Vi 0,10) e HIS isenta – mas terra cara e TDC suspensa até 2027 (sem IA 7,5).',
        'AAB (maior parte da cidade): para HIS IA 2, altura 12 m (≈ 4 pavimentos), TO 100%, 1 UH/45 m² (30 m² em vazios do Grupo I/III) – bom para condomínios de 4 pavimentos sem elevador.',
        'Vazios urbanos via PDU (LC 371/2024): PDU I IA 6 (7,5 c/ TDC) e frações de 30–60 m² nos PDU II/III – exige projeto diferenciado.',
        'Evitar: AOS e APA (1 UH/180 m², TO 40%, 12 m; APA só com Plano de Manejo), APAC (AEBT 7,5–11 m; ABT pelo órgão de tombamento), APP/Jardim Botânico, Setores Sul e Jaó (7,5 m) e as Macrozonas Rurais (só chácaras; conversão por OOAU).',
        'Vagas: fora da HIS, 1 vaga/100 m² de área privativa (coletiva) – em HIS 1 vaga/3 UH (LC 379/2024 art. 16).',
    ]
    lacunas = [
        dict(item='Áreas verdes, UPI e ARCT urbanas', motivo='Camadas ModeloEspacial/22, 24 e 26 retornam 0 feições no serviço público em 27/10/2026; essas áreas caem na AAB (residual) – confirmar.'),
        dict(item='Camadas ARAU/ARAR do Modelo Espacial com conteúdo trocado', motivo='Camadas 18 (UUS rural) e 25 (UUS urbana) retornam polígonos de APP/APA; não foram usadas (usou-se a base Simplifica).'),
        dict(item='AAB sem camada própria', motivo='Derivada por diferença (Macrozona Construída − demais unidades), conforme art. 157; marcada oficial:false.'),
        dict(item='Índice de aproveitamento da AAB e da AOS', motivo='LC 349/2022 art. 196 só fixa IA para ADD e AA; nas demais o potencial resulta de altura/TO/recuos (sem número de CA).'),
        dict(item='Taxa de ocupação na APAC', motivo='Anexo XXII e art. 190 não fixam TO para APAC.'),
        dict(item='Área do Bem Tombado (ABT)', motivo='Parâmetros pelas diretrizes do órgão de tombamento (art. 154 §2º) – não publicados por imóvel.'),
        dict(item='Bosque dos Buritis, Hipódromo da Lagoinha e um entorno sem nome', motivo='Entornos (AEBT) presentes na base sem linha correspondente no Anexo XXII.'),
        dict(item='Plano de Manejo das APAs', motivo='Ocupação em APA depende do Plano de Manejo (art. 179 §3º) – não lido.'),
        dict(item='Grupos I/II/III (OODC) e Grupos do Anexo XXIII (vazios)', motivo='Listas de setores não espacializadas (sem camada de bairros vinculada).'),
        dict(item='Vazios urbanos/PDU', motivo='Não há camada pública de vazios elegíveis a PDU I–IV; regra da LC 371/2024 descrita só em texto.'),
        dict(item='Setores Jaó e Sul (altura 7,5 m)', motivo='Sem polígono de bairro no JSON; condição registrada nos parâmetros de altura.'),
        dict(item='Restrições aeroportuárias e militares', motivo='Camadas do grupo "Plano Diretor 2007"; regra federal (DECEA/Exército) não transcrita.'),
        dict(item='Declividade > 30%', motivo='Camada publicada só como contornos (linhas).'),
        dict(item='Lei 10.845/2022 (atividades × vias)', motivo='Quadros de incomodidade por via não transcritos (foco habitação).'),
        dict(item='Lei 9.123/2011 (PUAMA) e lista Grupo III de vazios', motivo='Não lidas em detalhe.'),
        dict(item='Alterações após 27/10/2026 / revisão do PD', motivo='Texto compilado do SILEG consultado em 27/10/2026; decretos de novas AEIS III posteriores à camada podem faltar.'),
        dict(item='Operação Urbana Consorciada', motivo='Nenhuma OUC vigente identificada.'),
    ]
    geografico = dict(
        descricao='Zonas base = partição das unidades territoriais do Modelo Espacial (Anexo XIV) a partir da camada pública "Simplifica Goiânia – Uso do Solo" (FeatureServer/3) e do Mapa_ModeloEspacial (APAC/28, Jardim Botânico/27, Macrozoneamento/33); AAB derivada como resíduo; AEIS III e APA como zonas sobrepostas.',
        crs='EPSG:4326', crs_area='EPSG:31982', servidor_oficial=PM, camadas=geo_camadas,
        regras_de_consulta='1) Ache a zona base do lote (AA, ADD, AAB, AOS, APAC, ARAU ou rural). 2) Verifique as sobrepostas: AEIS III (HIS) e APA. 3) Camadas: corredores (recuo de 15/18 m do eixo), IVE (usos), OOAU, programas especiais, restrições aeroportuária/militar, declividade. 4) Altura/recuos pelo Anexo XXI (ou XXII no AEBT). 5) Confirme no Uso do Solo da SEPLANH.',
        limitacoes=['AAB derivada por diferença (oficial:false).', 'Simplificação ~1 m; 6 casas decimais; lascas < 5 m² descartadas.', 'Corredores, eixos e declividade são linhas.',
                    'Serviços ArcGIS 10.4 sem data de atualização por feição em parte das camadas.', 'Precedência entre unidades sobrepostas na base definida pelo analista (ARAU > APAC > AOS > ADD > AA > AAB).'],
        raio_divisa_m=30, pct_minimo_significativo=0.5,
        notas_tecnicas={'gerador': 'scripts/build_gyn.py', 'download': 'scripts/baixar_camadas.py (query por objectIds, outSR=4326, f=json, conversão esri→GeoJSON)', 'tabelas': 'scripts/tabelas_gyn.py'})
    macrozonas = [dict(codigo='MC', nome='Macrozona Construída', descricao='Área urbana (art. 131 I); dividida nas unidades territoriais AA, ADD, AAB, AOS, APAC e ARAU.', parametros={'fundamento': TXT('LC 349/2022 arts. 131 e 139.', None, 'F01', 'LC 349/2022 arts. 131 e 139')})] + \
                 [dict(codigo='MR-' + s, nome=n, descricao=f'Macrozona rural; chácaras a partir de {fr} m².', parametros={'fracao_chacara': P(fr, 'm2', 'F01', 'LC 349/2022 art. 197 par. único')}) for s, (n, fr) in T.RURAIS.items()]
    doc = dict(
        schema_versao='1.1', municipio='Goiânia', uf='GO', slug='goiania-go', codigo_ibge='5208707', data_levantamento=HOJE,
        centro_mapa=dict(lat=-16.6869, lon=-49.2648, zoom=11),
        orgao_confirmacao='SEPLANH – Secretaria Municipal de Planejamento Urbano e Habitação (Uso do Solo / Consulta Prévia)',
        marco_legal_vigente=('Vigente em 27/10/2026: Plano Diretor LC 349/2022 (texto compilado SILEG, com LC 363/2023, 371/2024, 373/2024 e 379/2024); Código de Obras LC 364/2023; Parcelamento LC 363/2023; '
                             'OODC LC 373/2024; HIS LC 379/2024; AEIS Lei 11.083/2023; EIV Lei 11.127/2024; TDC Lei 10.848/2022 (suspensa para novas concessões pelos Dec. 2.785/2025 e 82/2026); atividades Lei 10.845/2022; PUB Dec. 117/2026.'),
        fontes=[dict(id=a, titulo=b, lei=c, data=d, url=e, arquivo_local=(('fontes/' + f) if f else None)) for a, b, c, d, e, f in FONTES],
        macrozonas=macrozonas, macrozonas_observacao='Geometria das macrozonas na camada "macrozoneamento"; as rurais também são zonas base (MR-*).',
        zonas=Z, camadas_complementares=cam, outorga_onerosa=outorga, zeis_his=zeis, outros_parametros=outros_b, resumo_mcmv=resumo_mcmv, geografico=geografico, lacunas=lacunas)
    json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('zonas', len(Z), 'camadas', len(cam), 'MB', round(os.path.getsize(OUT) / 1e6, 2))

if __name__ == '__main__':
    main()
