"""Parâmetros por unidade territorial – Goiânia-GO (LC 349/2022 compilada + LC 371, 373, 379/2024, Lei 11.083/2023, LC 364/2023).
Cada função devolve o dicionário 'parametros' (schema 1.1)."""
from comum_gyn import *

# ---------------------------------------------------------------- Anexo XXI (afastamentos × altura)
ANEXO_XXI = [(4.0, 0, 0, 5), (7.5, 0, 0, 5), (11.0, 2, 2, 5), (14.5, 3, 3, 5)] + \
    [(round(18 + 3.5 * i, 2), round(3.2 + 0.2 * i, 2), round(3.2 + 0.2 * i, 2), 5) for i in range(14)] + \
    [(round(67 + 3.5 * i, 2), round(6.0 + 0.2 * i, 2), round(6.0 + 0.2 * i, 2), 6) for i in range(8)] + \
    [(round(95 + 3.5 * i, 2), round(7.6 + 0.2 * i, 2), round(7.6 + 0.2 * i, 2), 8) for i in range(4)] + [(109.0, 8.4, 8.4, 10)]
assert ANEXO_XXI[-2] == (105.5, 8.2, 8.2, 8) and ANEXO_XXI[17] == (63.5, 5.8, 5.8, 5) and ANEXO_XXI[25] == (91.5, 7.4, 7.4, 6)
A21 = 'LC 349/2022 art. 180 e Anexo XXI (red. LC 371/2024)'
OBS_A21 = ('Tabela por faixa de altura da edificação (4; 7,5; 11; 14,5; 18 … 109 m, passos de 3,5 m). Altura intermediária: aplicar a linha da '
           'altura imediatamente superior (leitura do analista – confirmar na SEPLANH). Acima de 109 m: +0,20 m a cada 3,5 m (art. 180 §2º).')
F_LAT = '0 if H <= 7.5 else (2 if H <= 11 else round(3 + 0.2 * ceil(max(H - 14.5, 0) / 3.5), 2))'

def lateral_a21(aa_add=False, hmax=None):
    obs = OBS_A21 + ' H = altura da edificação (m).'
    if aa_add: obs += ' Em AA/ADD os pavimentos de estacionamento/instalações até 11 m (laje de cobertura) ficam liberados dos recuos laterais e de fundo (art. 183 §1º; nota ¹ do Anexo XXI); subsolo aflorado: 12,5 m (§2º).'
    if hmax: obs += f' Altura máxima da unidade: {num(hmax)} m.'
    obs += ' Distância entre blocos no mesmo lote acima de 7,5 m = 2 × recuo lateral (art. 182). Subsolos sem recuo (art. 183 §3º).'
    return F('m', 'F01', A21 + '; arts. 182 e 183', obs, F_LAT)

def frontal_a21(corredor=True):
    conds = [C('altura até 63,5 m', 'unico', 5), C('altura de 67 a 91,5 m', 'unico', 6), C('altura de 95 a 105,5 m', 'unico', 8), C('altura de 109 m', 'unico', 10),
             C('altura acima de 109 m', 'formula', None, formula='10 + 0.2 * ceil((H - 109) / 3.5)')]
    if corredor:
        conds += [C('lote em corredor preferencial (macro rede viária)', 'unico', 15, observacao='Distância mínima entre o início da edificação e o EIXO da via, inclusive subsolo (art. 183 §10 I).'),
                  C('lote em corredor exclusivo ou estratégico', 'unico', 18, observacao='Distância mínima ao EIXO da via, inclusive subsolo (art. 183 §10 II).'),
                  C('lotes do art. 180 §3º (Av. 24 de Outubro em Campinas; Rua 4, Av. Goiás e quadras entre Tocantins/Araguaia/Rua 4 no Centro)', 'unico', 0, observacao='Ocupação obrigatória no alinhamento.')]
    return COND('m', 'F02', A21 + '; arts. 180 §3º e 183 §§9º–11', 'Recuo frontal medido do alinhamento. Edificações de atividades econômicas até 7,5 m em vias arteriais dos Setores Central e Campinas: isentas, garantido passeio de 5 m (art. 183 §9º).', conds)

def num(v):
    return ('%g' % v).replace('.', ',')

# ---------------------------------------------------------------- comuns
def ca_minimo():
    return SEM('coeficiente', 'LC 349/2022 não fixa CA mínimo por unidade territorial; PEUC/IPTU progressivo dependem de notificação (arts. 230 e ss.).', 'LC 349/2022')

def ca_basico_mc():
    return P(1, 'coeficiente', 'F01', 'LC 349/2022 arts. 242 a 244',
             'Coeficiente Básico NÃO oneroso = área privativa até 1× a área do terreno, sem contar subsolo, estacionamento, áreas comuns/circulações, instalações e fachada ativa (art. 242 I–VII). Opcional: edificação de até 7,5 m tem toda a área não onerosa (art. 242 VIII). O excedente é oneroso (OODC – LC 373/2024).')

def vagas_mc(aa=False):
    conds = [C('Habitação coletiva / quitinete (regra geral)', 'unico', 1, observacao='1 vaga por 100 m² da área privativa total (LC 364/2023 art. 110 I); 2% das vagas acessíveis.'),
             C('Demais tipologias habitacionais (unifamiliar, geminada, seriada)', 'unico', 1, observacao='1 vaga por unidade habitacional (art. 110).'),
             C('Visitantes em habitação coletiva', 'texto', None, texto_original='Até 9 UH: dispensado; 10 a 25 UH: 1; 26 a 100 UH: 2; acima de 100 UH: +1 a cada 100 UH (LC 364/2023 art. 111).'),
             C('HIS (LC 379/2024)', 'unico', 0.3333, observacao='Mínimo 1 vaga a cada 3 UH; até 30% podem ser de motocicleta; fachada ativa até 180 m² dispensada (LC 379/2024 art. 16). Fonte: F05.')]
    if aa:
        conds.append(C('Lote lindeiro a Corredor Exclusivo em AA', 'unico', 0, observacao='Vagas facultadas (LC 364/2023 art. 110 §8º, incl. pela LC 379/2024 art. 29; LC 379 art. 16 §4º para HIS).'))
    return COND('vagas (ver condição)', 'F07', 'LC 364/2023 arts. 110 a 112; LC 379/2024 arts. 16 e 29', 'A unidade varia: vagas/100 m² de área privativa (coletiva) ou vagas/UH.', conds)

def usos_hab(fonte='F01', art='LC 349/2022 arts. 162 e 163; Lei 10.845/2022', obs=None):
    return P(['habitacional unifamiliar', 'habitacional geminada', 'habitacional seriada', 'habitacional coletiva', 'atividade econômica (GI-1 a GI-5 conforme Lei 10.845/2022 e hierarquia viária)', 'institucional'],
             'codigos_de_uso', fonte, art, obs or 'Tipologias habitacionais admitidas em todas as unidades da Macrozona Construída, exceto APP, Jardim Botânico, áreas verdes, Zona de Segurança e UCs que não admitam habitação (art. 163). Atividades econômicas por grau de incomodidade × via (Lei 10.845/2022 – não transcrita).', forma='lista')

def perm_mc():
    return P(0.10, 'fracao', 'F01', 'LC 349/2022 art. 192', 'Índice paisagístico mínimo de 15% do terreno, com no mínimo 10% em cobertura vegetal PERMEÁVEL (o restante pode ser vegetação sobre laje).')

def perm_ambiental():
    return P(0.25, 'fracao', 'F01', 'LC 349/2022 art. 194', '25% do terreno com cobertura vegetal permeável (AOS e áreas ocupáveis da ARAU).')

def lote_geral(aos=False):
    if aos: return P(360, 'm2', 'F01', 'LC 349/2022 art. 120 II', 'Lote máximo 5.000 m²; acima disso, "área" com testada ≥ 12 m (art. 120 III). AEIS: lotes menores (Lei 11.083/2023).'), P(12, 'm', 'F01', 'LC 349/2022 art. 120 II')
    return (COND('m2', 'F01', 'LC 349/2022 art. 120; Lei 11.083/2023 arts. 8º e 24', 'Parcela máxima 5.000 m² (art. 120 I).',
                 [C('Parcelamento regular (geral)', 'unico', 270), C('AEIS I/II (Reurb-S)', 'unico', 90, observacao='Testada 5 m (Lei 11.083 art. 8º). Fonte: F06.'),
                  C('AEIS III – parcelamento de interesse social', 'unico', 150, observacao='Testada 6 m (Lei 11.083 art. 24). Fonte: F06.')]),
            COND('m', 'F01', 'LC 349/2022 art. 120; Lei 11.083/2023', None, [C('Parcelamento regular (geral)', 'unico', 10), C('AEIS I/II', 'unico', 5), C('AEIS III', 'unico', 6)]))

def outros_comuns(vi, extra=None):
    o = {'oodc_vi': P(vi, None, 'F04', 'LC 373/2024 art. 4º §2º', 'Valor do índice (Vi) da fórmula VOO = Vm × Vi × Qsc; Vm = % do CUB R16 SINDUSCON-GO por grupo de setores (50%/40%/30%).'),
         'indice_paisagistico': P(0.15, 'fracao', 'F01', 'LC 349/2022 art. 192', 'Mínimo 15% do terreno com cobertura vegetal (≥ 10% permeável).')}
    o.update(extra or {})
    return o

def dens_uh(fracao, fonte, art, obs):
    return round(10000 / fracao, 2)

# ---------------------------------------------------------------- unidades
def aa():
    lote, test = lote_geral()
    return dict(
        ca_minimo=ca_minimo(), ca_basico=ca_basico_mc(),
        ca_maximo=COND('coeficiente', 'F01', 'LC 349/2022 arts. 196 II e 252 §6º; Dec. 2.785/2025 e Dec. 82/2026', 'IA computa só áreas privativas (exclui estacionamento, carga/descarga, escaninhos, fachada ativa – art. 196 §1º); fruição pública acresce 100% da área (§3º).',
                       [C('Geral (qualquer uso)', 'unico', 6), C('Com recepção de TDC (até +25% da altura – art. 252)', 'unico', 7.5, observacao='Novas concessões de TDC suspensas desde 01/01/2025 (Dec. 2.785/2025), prorrogado por 18 meses a partir de 01/07/2026 (Dec. 82/2026); CPC/CPC-S já emitidas podem ser usadas. Fonte: F10/F11.'),
                        C('Faixa de 350 m da Av. Fued José Sebba (LC 379/2024 art. 34)', 'unico', 6, observacao='Fonte: F05.')]),
        taxa_ocupacao=COND('fracao', 'F01', 'LC 349/2022 art. 190 I, II, §§1º, 2º e 5º (red. LC 371/2024)', None,
                           [C('Até 11 m de altura', 'unico', 1.0, observacao='Sobre o terreno excluídas as APPs (§1º).'),
                            C('Pavimento de estacionamento/instalações entre 11 e 14,5 m', 'unico', 1.0, observacao='Respeitados os recuos do Anexo XXI (§5º).'),
                            C('Acima de 11 m de altura', 'unico', 0.5, observacao='Sobre o terreno excluídos os recuos obrigatórios e as APPs (§2º).')]),
        gabarito_altura_max_m=LIVRE('m', 'F01', 'LC 349/2022 art. 187', 'AA não tem altura máxima; limitada por IA, recuos do Anexo XXI, restrições aeroportuárias (COMAER) e AEBT.'),
        gabarito_pavimentos=LIVRE('pavimentos', 'F01', 'LC 349/2022 art. 187', 'Sem limite de pavimentos.'),
        taxa_permeabilidade=perm_mc(),
        recuos=dict(frontal=frontal_a21(), lateral=lateral_a21(True), fundos=lateral_a21(True)),
        lote_minimo_m2=lote, testada_minima_m=test, usos_permitidos=usos_hab(), vagas=vagas_mc(True),
        densidade=LIVRE('uh/ha', 'F05', 'LC 349/2022 art. 179 (AA não listada); LC 379/2024 art. 14', 'Sem controle de densidade (fração ideal) em AA – o art. 179 só fixa fração para AOS, APA, AAB e APAC; LC 379/2024 art. 14 confirma para HIS.'),
        outros=outros_comuns(0.10, {
            'altura_tdc': P(0.25, 'fracao', 'F01', 'LC 349/2022 art. 252', 'TDC recebida até +25% da altura máxima atingida (só AA nos Eixos de Desenvolvimento e PDU I–III), últimos pavimentos com os recuos do pavimento anterior. Concessões suspensas (Dec. 2.785/2025; Dec. 82/2026).'),
            'eixo_setor_sul': TXT('No Setor Sul, só integram a AA os lotes com testada para o eixo (art. 159).', None, 'F01', 'LC 349/2022 art. 159'),
            'baia_desaceleracao': TXT('Habitação geminada, seriada e coletiva com acesso por via expressa, arterial ou coletora em AA/ADD e altura > 11 m exige baia de desaceleração (art. 163 §1º).', None, 'F01', 'LC 349/2022 art. 163 §1º')}))

def add():
    p = aa()
    p['ca_maximo'] = P(5, 'coeficiente', 'F01', 'LC 349/2022 art. 196 I', 'IA máximo 5 para qualquer uso; só áreas privativas (art. 196 §1º). Recepção de TDC (art. 252) só se aplica à AA dos Eixos e PDU I–III.')
    p['densidade'] = LIVRE('uh/ha', 'F05', 'LC 349/2022 art. 179 (ADD não listada); LC 379/2024 art. 14', 'Sem controle de fração ideal em ADD. EIT obrigatório para habitação coletiva com mais de 300 vagas (art. 267 IX).')
    p['outros'] = outros_comuns(0.20, {'eit_add': P(300, None, 'F01', 'LC 349/2022 art. 267 IX (red. LC 363/2023)', 'Habitação coletiva em ADD com mais de 300 vagas é polo gerador de tráfego (EIT/RIT).'),
                                       'baia_desaceleracao': p['outros']['baia_desaceleracao']})
    p['vagas'] = vagas_mc(False)
    p['gabarito_altura_max_m'] = LIVRE('m', 'F01', 'LC 349/2022 art. 187', 'ADD não tem altura máxima; limitada por IA 5 e recuos do Anexo XXI.')
    return p

ALT12 = lambda: COND('m', 'F01', 'LC 349/2022 art. 186', None, [C('Geral', 'unico', 12), C('Setores Jaó e Sul', 'unico', 7.5)])

def aab():
    lote, test = lote_geral()
    return dict(
        ca_minimo=ca_minimo(), ca_basico=ca_basico_mc(),
        ca_maximo=COND('coeficiente', 'F01', 'LC 349/2022 arts. 186, 190 III e 196; LC 379/2024 art. 14 §1º', 'A LC 349 não fixa IA para a AAB (art. 196 só trata de ADD e AA): o potencial resulta de altura 12 m × TO 100% × recuos.',
                       [C('Geral (sem IA fixado)', 'nao_aplicavel', None), C('HIS (LC 379/2024)', 'unico', 2, observacao='IA 2 para HIS em AAB, ampliável com TDC (art. 14 §2º). Fonte: F05.')]),
        taxa_ocupacao=P(1.0, 'fracao', 'F01', 'LC 349/2022 art. 190 III e §1º', '100% até 12 m, sobre o terreno excluídas as APPs; respeitar recuos do Anexo XXI.'),
        gabarito_altura_max_m=ALT12(), gabarito_pavimentos=SEM('pavimentos', 'Controle por altura em metros (12 m), não por pavimentos.', 'LC 349/2022 art. 186'),
        taxa_permeabilidade=perm_mc(), recuos=dict(frontal=frontal_a21(), lateral=lateral_a21(hmax=12), fundos=lateral_a21(hmax=12)),
        lote_minimo_m2=lote, testada_minima_m=test, usos_permitidos=usos_hab(), vagas=vagas_mc(),
        densidade=COND('uh/ha', 'F01', 'LC 349/2022 art. 179 III, §§5º e 6º; LC 379/2024 art. 14', 'Densidade líquida = 10.000 / fração ideal (1 UH por fração de terreno).',
                       [C('Geral – 1 UH / 90 m² de terreno', 'unico', 111.11), C('Quitinete – 1 UH / 30 m²', 'unico', 333.33),
                        C('HIS em vazio Grupo I (Anexo XXIII) ou Grupo III (Lei 9.123) – 1 UH / 30 m²', 'unico', 333.33, observacao='LC 379/2024 art. 14. Fonte: F05.'),
                        C('HIS nos demais casos – 1 UH / 45 m²', 'unico', 222.22, observacao='LC 379/2024 art. 14. Fonte: F05.'),
                        C('Chácara/sítio de recreio em via < 13 m', 'texto', None, texto_original='4 economias por unidade imobiliária (art. 179 §5º I).')]),
        outros=outros_comuns(0.15))

def aos():
    lote, test = lote_geral(True)
    return dict(
        ca_minimo=ca_minimo(), ca_basico=ca_basico_mc(),
        ca_maximo=NA('coeficiente', 'F01', 'LC 349/2022 arts. 186, 190 §3º e 196', 'Sem IA fixado para AOS: potencial resulta de altura 12 m, TO 40% (inclusive subsolo) e fração 180 m²/UH.'),
        taxa_ocupacao=P(0.4, 'fracao', 'F01', 'LC 349/2022 art. 190 §§3º e 4º', '40% do terreno, inclusive subsolo; sobre a área total excluída só a APP.'),
        gabarito_altura_max_m=ALT12(), gabarito_pavimentos=SEM('pavimentos', 'Controle por altura em metros.', 'LC 349/2022 art. 186'),
        taxa_permeabilidade=perm_ambiental(), recuos=dict(frontal=frontal_a21(), lateral=lateral_a21(hmax=12), fundos=lateral_a21(hmax=12)),
        lote_minimo_m2=lote, testada_minima_m=test, usos_permitidos=usos_hab(), vagas=vagas_mc(),
        densidade=P(55.56, 'uh/ha', 'F01', 'LC 349/2022 art. 179 I e §4º; LC 379/2024 art. 14', '1 UH por 180 m² de terreno (inclusive HIS – LC 379 art. 14); APP entra no cálculo (§4º).'),
        outros=outros_comuns(0.30, {'transicao_app': TXT('Faixa de transição ≥ 100 m junto às APPs de cursos d\'água e nascentes (art. 150); um imóvel não pode ter mais de uma unidade territorial, exceto ARAU (§4º).', None, 'F01', 'LC 349/2022 art. 150')}))

def arau_ocupavel(nome):
    p = aos()
    p['ca_maximo'] = NA('coeficiente', 'F01', 'LC 349/2022 arts. 186, 190 §3º', f'{nome}: sem IA; altura 12 m, TO 40% e permeabilidade 25% nas áreas passíveis de ocupação da ARAU.')
    p['outros'] = outros_comuns(0.30)
    return p

def apa():
    p = arau_ocupavel('APA')
    p['lote_minimo_m2'] = COND('m2', 'F01', 'LC 349/2022 arts. 120 IV e 121', 'Parcelamento só se autorizado pelo Plano de Manejo.', [C('Declividade ≤ 30% (até 2 economias/lote)', 'unico', 450), C('Declividade > 30% (1 economia/lote)', 'unico', 1250)])
    p['testada_minima_m'] = COND('m', 'F01', 'LC 349/2022 art. 121', None, [C('Declividade ≤ 30%', 'unico', 15), C('Declividade > 30%', 'unico', 20)])
    p['densidade'] = P(55.56, 'uh/ha', 'F01', 'LC 349/2022 art. 179 II e §3º', '1 UH por no mínimo 180 m²; ocupação só após o Plano de Manejo da APA (§3º).')
    p['usos_permitidos'] = usos_hab(obs='Ocupação condicionada ao Plano de Manejo (art. 179 §3º; art. 121). Parcelamento rural em APA segue o Plano de Manejo e não admite sítio de recreio (art. 200).')
    return p

def nao_edificavel(oque, art, fonte='F01'):
    n = lambda u: NA(u, fonte, art, f'{oque}: área não edificável / sem ocupação urbana.')
    return dict(ca_minimo=n('coeficiente'), ca_basico=n('coeficiente'), ca_maximo=n('coeficiente'), taxa_ocupacao=n('fracao'), gabarito_altura_max_m=n('m'), gabarito_pavimentos=n('pavimentos'),
                taxa_permeabilidade=n('fracao'), recuos=dict(frontal=n('m'), lateral=n('m'), fundos=n('m')), lote_minimo_m2=n('m2'), testada_minima_m=n('m'),
                usos_permitidos=NA('codigos_de_uso', fonte, art + '; LC 349/2022 art. 163', f'{oque}: habitação não admitida (art. 163).'), vagas=None,
                densidade=n('uh/ha'), outros={})

def abt():
    s = lambda u: SEM(u, 'Área do Bem Tombado: parâmetros definidos pelas diretrizes do órgão responsável pelo tombamento (IPHAN, Estado ou Município) – art. 154 §2º.', 'LC 349/2022 art. 154 §2º')
    return dict(ca_minimo=s('coeficiente'), ca_basico=s('coeficiente'), ca_maximo=s('coeficiente'), taxa_ocupacao=s('fracao'), gabarito_altura_max_m=s('m'), gabarito_pavimentos=s('pavimentos'),
                taxa_permeabilidade=perm_mc(), recuos=dict(frontal=s('m'), lateral=s('m'), fundos=s('m')), lote_minimo_m2=s('m2'), testada_minima_m=s('m'),
                usos_permitidos=s('codigos_de_uso') | {'unidade': 'codigos_de_uso'}, vagas=vagas_mc(),
                densidade=P(111.11, 'uh/ha', 'F01', 'LC 349/2022 art. 179 III', '1 UH por 90 m² na APAC, se o uso habitacional for admitido pelo órgão de tombamento.'),
                outros=outros_comuns(0.30, {'anuencia': TXT('Qualquer obra exige prévia anuência dos entes culturais competentes; bens não podem ser demolidos/mutilados (art. 154 caput e §1º).', None, 'F01', 'LC 349/2022 art. 154')}))

# AEBT: grupos do Anexo XXII
AEBT_GRUPOS = {
 'APAC-AEBT-A': dict(nome='APAC – Entorno de Bem Tombado (7,5 m; recuo frontal 5 m)', alt=7.5, fr=5, lat=None,
                     bens='Praça Cívica, Coreto, Obeliscos, Monumento às Três Raças, Relógio e Fontes Luminosas da Av. Goiás, Palácio do Governo, Secretaria Geral, Fórum e TJ, Delegacia Fiscal, TRE, Dpto. Estadual de Informação, Chefatura de Polícia, Tribunal de Contas, Liceu, Faculdade de Direito/Casa tipo Rua 20, Casa de Pedro Ludovico, Painéis D.J. Oliveira, Grupo Escolar Modelo, Igreja do Sagrado Coração de Maria, Igreja e Casa dos Padres Redentoristas, Antiga Escola Técnica Federal, Casa do Prof. Colemar Natal e Silva, Martim Cererê, Cruzeiro, Estação Meteorológica, Terminal do Aeródromo, Sobrado do IBGE'),
 'APAC-AEBT-B': dict(nome='APAC – Entorno de Bem Tombado (11 m; frontal 5 m; lateral/fundo 2 m acima de 7,5 m)', alt=11, fr=5, lat=2,
                     bens='Lago das Rosas, Casa do 1º Prefeito, Sobrado Casa da Cultura, Ateneu Dom Bosco, Estação Ferroviária/Praça do Trabalhador (quadra 141: alinhamento), Antiga Capela da Santa Casa, Fachada da Catedral, Mercado Popular, Centro de Treinamento do Parque Anhanguera, Teatro Inacabado, Cemitério Santana, Parque Botafogo'),
 'APAC-AEBT-C': dict(nome='APAC – Entorno de Bem Tombado (7,5 m; ocupação no alinhamento frontal e laterais)', alt=7.5, fr=0, lat=0,
                     bens='Sede do Fórum e da Prefeitura de Campinas; Antigo Palace Hotel'),
 'APAC-AEBT-SUB': dict(nome='APAC – Entorno da Subestação Goiânia (11 m; frontal 5 m)', alt=11, fr=5, lat=None, bens='Subestação Goiânia (Centro Cultural CELG Eng. Oton)'),
 'APAC-AEBT-BB': dict(nome='APAC – Entorno da Estátua de Bartolomeu Bueno (altura do Anexo XXI; alinhamento)', alt=None, fr=0, lat=0, bens='Estátua de Bartolomeu Bueno da Silva'),
 'APAC-AEBT-ND': dict(nome='APAC – Entorno de Bem Tombado sem linha no Anexo XXII', alt='nd', fr=None, lat=None, bens='Bosque dos Buritis; Hipódromo da Lagoinha; entorno sem nome na base'),
}
# nome do bem na camada Mapa_ModeloEspacial/28 -> grupo
def grupo_aebt(nome):
    n = (nome or '').upper()
    for chave, g in [('PALACE HOTEL', 'C'), ('CAMPINAS', 'C'), ('CELG', 'SUB'), ('SUBESTA', 'SUB'), ('BARTOLOMEU', 'BB'), ('BURITIS', 'ND'), ('HIPÓDROMO', 'ND'),
                     ('CEMITÉRIO', 'B'), ('MERCADO', 'B'), ('BOTAFOGO', 'B'), ('LAGO DAS ROSAS', 'B'), ('ESTAÇÃO FERROVI', 'B'), ('TRABALHADOR', 'B'), ('CASA DA CULTURA', 'B'),
                     ('CATEDRAL', 'B'), ('PARQUE ANHAGUERA', 'B'), ('PARQUE ANHANGUERA', 'B'), ('ATENEU', 'B'), ('INACABADO', 'B'), ('PRIMEIRO PREFEITO', 'B'), ('SANTA CASA', 'B'),
                     ('CRUZEIRO', 'A'), ('MARTIM', 'A'), ('D.J. OLIVEIRA', 'A'), ('CORAÇÃO DE MARIA', 'A'), ('ESCOLA TÉCNICA', 'A'), ('PRAÇA CÍVICA', 'A')]:
        if chave in n: return 'APAC-AEBT-' + g
    return 'APAC-AEBT-ND'

def aebt(cod):
    g = AEBT_GRUPOS[cod]; art = 'LC 349/2022 arts. 181, 188 e Anexo XXII'
    lote, test = lote_geral()
    if g['alt'] == 'nd':
        s = lambda u: SEM(u, 'O Anexo XXII não traz linha para este bem; parâmetros a definir por ato da SEPLANH com o ente do tombamento (art. 155 par. único).', 'LC 349/2022 arts. 155 e 188')
        alt, fr, lat = s('m'), s('m'), s('m')
    else:
        alt = (P(g['alt'], 'm', 'F02', art) if g['alt'] else F('m', 'F02', art + ' (nota 26)', 'Estátua de Bartolomeu Bueno: altura segue o Anexo XXI da unidade subjacente.', 'altura do Anexo XXI'))
        fr = P(g['fr'], 'm', 'F02', art, 'Ocupação obrigatória no alinhamento.' if g['fr'] == 0 else None)
        if g['lat'] is None: lat = P(0, 'm', 'F02', art, 'Anexo XXII sem recuo lateral/fundo ("–").')
        elif g['lat'] == 0: lat = P(0, 'm', 'F02', art, 'Ocupação obrigatória nos alinhamentos laterais.')
        else: lat = COND('m', 'F02', art + ' (notas 3–34)', None, [C('Altura até 7,5 m', 'unico', 0), C('Altura acima de 7,5 m (até 11 m)', 'unico', 2)])
    obs_alt = None
    if cod == 'APAC-AEBT-A':
        alt = COND('m', 'F02', art, 'Linhas especiais do Anexo XXII que podem cair neste grupo.', [C('Geral', 'unico', 7.5), C('Entorno do Grande Hotel', 'unico', 11, observacao='Ocupação no alinhamento (nota 1).'),
                                                                                                  C('Entorno do Cine Teatro Goiânia', 'unico', 21.5), C('Lotes 3/30/28, 26, 17/24, 19, 21, 23/25/5 e 57 da quadra 67 do Setor Central', 'unico', 4)])
    return dict(
        ca_minimo=ca_minimo(), ca_basico=ca_basico_mc(),
        ca_maximo=NA('coeficiente', 'F01', 'LC 349/2022 arts. 188, 196 e 244 §1º II', 'Sem IA: potencial resulta da altura/recuos do Anexo XXII. Toda a área é isenta de OODC no AEBT (art. 244 §1º II).'),
        taxa_ocupacao=SEM('fracao', 'O Anexo XXII fixa só altura e recuos; o art. 190 não trata da APAC – confirmar na SEPLANH.', 'LC 349/2022 arts. 188 e 190'),
        gabarito_altura_max_m=alt, gabarito_pavimentos=SEM('pavimentos', 'Controle por altura.', art),
        taxa_permeabilidade=perm_mc(), recuos=dict(frontal=fr, lateral=lat, fundos=lat), lote_minimo_m2=lote, testada_minima_m=test,
        usos_permitidos=usos_hab(obs='Vazio urbano no AEBT não pode ser ocupado como PDU nem como conjunto de habitação coletiva de alta densidade (art. 159 §2º). Demolições e obras dependem do ente cultural (art. 154 §§3º–4º).'),
        vagas=vagas_mc(), densidade=P(111.11, 'uh/ha', 'F01', 'LC 349/2022 art. 179 III', '1 UH por 90 m² (APAC).'),
        outros=outros_comuns(0.30, {'isencao_oodc': TXT('Novas edificações e modificações no AEBT são isentas de OODC (art. 244 §1º II).', None, 'F01', 'LC 349/2022 art. 244 §1º II'),
                                    'bens_do_grupo': TXT(g['bens'], None, 'F02', 'LC 349/2022 Anexo XXII')}))

def aeis3():
    p = aab()
    art = 'LC 379/2024 art. 14 §1º IV e §2º; Lei 11.083/2023 arts. 22 a 34'
    p['ca_maximo'] = COND('coeficiente', 'F05', art, 'Parâmetros para HIS (≥ 80% da área em HIS – Lei 11.083 art. 31).', [C('HIS em AEIS', 'unico', 2, observacao='IA 2 (exceto zoneamento ambiental), ampliável com TDC (art. 14 §2º).'), C('Sobre AA/ADD', 'herda_da_base', None)])
    p['gabarito_altura_max_m'] = COND('m', 'F05', art, None, [C('HIS em AEIS – tabela de alturas da AA (Anexo XXI)', 'livre', None, observacao='LC 379 art. 14 IV: aplica a tabela de altura da AA.'), C('Sobre AOS/APA', 'unico', 12)])
    p['densidade'] = COND('uh/ha', 'F05', art + '; Lei 11.083/2023 art. 10', None, [C('HIS em AEIS – 1 UH / 30 m²', 'unico', 333.33), C('Sobre AOS ou APA – 1 UH / 180 m²', 'unico', 55.56),
                                                                                    C('AEIS I/II (Reurb-S) – 1 UH / 90 m² (30 m² quitinete)', 'unico', 111.11, observacao='Lei 11.083/2023 art. 10. Fonte: F06.')])
    p['lote_minimo_m2'] = COND('m2', 'F06', 'Lei 11.083/2023 arts. 8º §3º e 24', None, [C('AEIS III – parcelamento', 'unico', 150), C('AEIS III em AOS', 'unico', 180), C('AEIS I/II (Reurb-S)', 'unico', 90)])
    p['testada_minima_m'] = P(6, 'm', 'F06', 'Lei 11.083/2023 art. 24', 'AEIS I/II: 5 m (art. 8º).')
    p['vagas'] = P(0.3333, 'vagas/UH', 'F05', 'LC 379/2024 art. 16', '1 vaga a cada 3 UH (até 30% motos); facultadas em corredor exclusivo na AA (§4º).')
    p['outros'] = outros_comuns(0.15, {
        'percentual_his': P(0.8, 'fracao', 'F06', 'Lei 11.083/2023 art. 31', 'Mínimo 80% da área para HIS e até 20% para atividades/fachada ativa.'),
        'uh_area_max_m2': P(70, 'm2', 'F05', 'LC 379/2024 art. 16', 'Área privativa máxima da UH de HIS.'),
        'isencao_oodc': TXT('HIS isenta de OODC (LC 379/2024 art. 10) e de ITBI quando FAR/FDS/FNHIS (art. 11).', None, 'F05', 'LC 379/2024 arts. 10 e 11'),
        'vias_internas': TXT('Vias internas de conjuntos HIS: 6 m (pedestre) / 5 m (pista) – art. 20.', None, 'F05', 'LC 379/2024 art. 20'),
        'recuo_permeavel_fechado': P(2, 'm', 'F06', 'Lei 11.083/2023 art. 34', 'Modalidade fechada: faixa permeável de 2 m junto ao alinhamento.')})
    return p

RURAIS = {'MRA': ('Macrozona Rural do Alto Anicuns', 1000), 'MRB': ('Macrozona Rural do Barreiro', 1000), 'MRD': ('Macrozona Rural do Dourados', 1000), 'MRL': ('Macrozona Rural do Lajeado', 1000),
          'MRC': ('Macrozona Rural do Capivara', 2000), 'MRJ': ('Macrozona Rural do João Leite', 2000), 'MRS': ('Macrozona Rural do São Domingos', 2000)}

def rural(sig):
    nome, fr = RURAIS[sig]; art = 'LC 349/2022 arts. 197 a 208 (art. 197 par. único incl. LC 371/2024)'
    n = lambda u, o='Solo rural: índices urbanos não se aplicam; condicionantes por lei específica (art. 199).': NA(u, 'F01', art, o)
    return dict(ca_minimo=n('coeficiente'), ca_basico=n('coeficiente'), ca_maximo=n('coeficiente'), taxa_ocupacao=n('fracao'), gabarito_altura_max_m=n('m'), gabarito_pavimentos=n('pavimentos'),
                taxa_permeabilidade=n('fracao'), recuos=dict(frontal=n('m'), lateral=n('m'), fundos=n('m')),
                lote_minimo_m2=P(fr, 'm2', 'F01', 'LC 349/2022 art. 197 par. único ' + ('I' if fr == 1000 else 'II') + ' (incl. LC 371/2024)', 'Fração mínima de parcelamento para sítio de recreio/chácara (fora de APA – art. 200 proíbe sítio de recreio em APA); demais casos: módulo rural (legislação federal).'),
                testada_minima_m=SEM('m', 'Não fixada para o solo rural.', art),
                usos_permitidos=NA('codigos_de_uso', 'F01', art, 'Habitação multifamiliar urbana não se aplica; atividades agropecuárias, agro/ecoturismo, silvicultura e as do Dec. federal 62.504/1968 (art. 198); ABADEE/AEDE por ato da SEPLANH (art. 197 par. único III). Conversão para uso urbano só via OOAU (art. 249).'),
                vagas=None, densidade=n('uh/ha'), outros={'unidades_rurais': TXT('ARAR (APP, reserva legal, UC, áreas de recuperação – preponderante), ABADEE (remanescente) e AEDE (faixas ao longo de BR-060, BR-153, GO-010/020/040/060/070/080/462 e Anel Rodoviário).', None, 'F01', 'LC 349/2022 arts. 201 a 208')})
