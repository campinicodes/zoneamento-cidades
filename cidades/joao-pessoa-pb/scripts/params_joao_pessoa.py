"""Fontes e parâmetros urbanísticos de João Pessoa-PB (schema 1.1).
Base: PD LC 164/2024 (alt. LC 171/2025), LUOS LC 166/2024 (alt. LC 169/2024 – Anexos III, IV e V substituem IV, V e VI)."""
PD = 'https://planodiretor.joaopessoa.pb.gov.br/wp-content/uploads'
SAPL = 'https://sapl.joaopessoa.pb.leg.br/media/sapl/public/normajuridica'
FONTES = [
    dict(id='F01', titulo='Plano Diretor Municipal de João Pessoa', lei='Lei Complementar nº 164/2024', data='2024-01-11',
         url=f'{SAPL}/2024/19766/lei_complementar_no_164-2024.pdf', arquivo_local='fontes/LC164_2024_PlanoDiretor_SAPL.pdf',
         observacao='Texto do SAPL da Câmara Municipal. Publicação original: DOE-JP nº 444/2024 suplemento (fontes/Diario_444_2024_SUPLEMENTO.pdf, ' + PD + '/2024/04/2024_Diario_444_SUPLEMENTO.pdf). Anexos I, II, III, VII e VIII substituídos pela LC 171/2025.'),
    dict(id='F02', titulo='Lei de Uso e Ocupação do Solo (LUOS) – republicada', lei='Lei Complementar nº 166/2024', data='2024-04-29',
         url=f'{SAPL}/2024/19967/166_-_29.04.24_-_luos_-_lei_de_uso_e_ocupacao_do_solo-republicada_em_23-08-2024.pdf', arquivo_local='fontes/LC166_2024_LUOS_republicada_SAPL.pdf',
         observacao='Publicada no DOE-JP nº 0523/supl. (06/05/2024), republicada por incorreção no DOE-JP nº 0550 (14/06/2024). Versão D.O.: ' + PD + '/2024/05/LC-166-2024-Lei-de-Uso-e-Ocupacao-do-Solo-LUOS-versao-D.O.pdf (fontes/LC166_2024_LUOS_DO.pdf). Anexos II–VI substituídos pela LC 169/2024.'),
    dict(id='F03', titulo='Altera os Anexos II, III, IV, V e VI da LUOS (zoneamento, faixas da orla, usos, parâmetros de ocupação e vagas)', lei='Lei Complementar nº 169/2024', data='2024-12-19',
         url=f'{PD}/2025/01/LC169-2024_AlteraLUOS.pdf', arquivo_local='fontes/LC169_2024_AlteraLUOS.pdf',
         observacao='Publicada no DOE-JP nº 0681, de 23/12/2024. Anexo I (novo mapa de zoneamento) e Anexo II (faixas da orla) só em raster; Anexos III (usos x hierarquia viária), IV (parâmetros de ocupação) e V (vagas) em tabela (OCR conferido visualmente).'),
    dict(id='F04', titulo='Altera arts. 50, 68, 110, 120, 123, 156 e 171 e Anexos I, II, III, VII e VIII do Plano Diretor', lei='Lei Complementar nº 171/2025', data='2025-01-09',
         url=f'{PD}/2025/01/LC171_2025_AlteraPD.pdf', arquivo_local='fontes/LC171_2025_AlteraPD.pdf',
         observacao='Publicada no DOE-JP nº 0693 (14/01/2025), republicada por incorreção. Novos mapas de macrozoneamento (Anexo I) e ZEIS (Anexo II, raster) e lista de 74 ZEIS (Anexo III).'),
    dict(id='F05', titulo='Transferência do Direito de Construir (TDC)', lei='Lei nº 15.409/2024', data='2024',
         url=f'{PD}/2025/03/Lei-15409-2024-Transferencia-do-Direito-de-Construir-TDC.pdf', arquivo_local='fontes/Lei15409_2024_TDC.pdf', observacao=None),
    dict(id='F06', titulo='Regulamenta a Lei 15.409/2024 (TDC)', lei='Decreto nº 11.266/2026', data='2026',
         url=f'{PD}/2026/07/Dec.-11266-2026-Regulamenta-a-lei-15409-2024-TDC.pdf', arquivo_local='fontes/Dec11266_2026_TDC.pdf', observacao=None),
    dict(id='F07', titulo='Parâmetros para classificação das Habitações de Interesse Social (HIS)', lei='Decreto nº 10.560/2024', data='2024-02-02',
         url=f'{PD}/2025/07/Dec-10560-2024-Parametros-para-classificacao-das-Habitacoes-de-Interesse-Social-HIS-D.O.M.pdf', arquivo_local='fontes/Dec10560_2024_HIS.pdf',
         observacao='Publicado no DOM nº 0482, de 06/03/2024 (p. 3).'),
    dict(id='F08', titulo='Plano Específico de Zoneamento de Ruído (PEZR) do Aeroporto Castro Pinto – documento e curvas', lei='PEZR 2024 (publicado no portal do Plano Diretor)', data='2024',
         url=f'{PD}/2025/05/Plano-Especifico-de-Zoneamento-de-Ruido.pdf', arquivo_local='fontes/PEZR_JoaoPessoa.pdf',
         observacao='Curvas: ' + PD + '/2025/05/Curvas_PEZR2024_JoaoPessoa.pdf (fontes/Curvas_PEZR2024.pdf). Não vetorizado.'),
    dict(id='F09', titulo='Lei do Sistema Viário Básico', lei='Lei nº 15.197/2024 (alterada pela Lei nº 15.609/2025)', data='2024',
         url=f'{PD}/2024/06/Lei-15197-2024-Lei-do-Sistema-Viario-Basico-DOM.pdf', arquivo_local='fontes/Lei15197_2024_SistemaViario.pdf',
         observacao='Alteração: ' + PD + '/2025/09/Lei-15609-2025-Altera-a-lei-15197-2024.pdf (fontes/Lei15609_2025_AlteraSV.pdf). Define a hierarquia viária usada nos Anexos III e IV da LUOS.'),
    dict(id='F10', titulo='Regularização de edificações', lei='Lei Complementar nº 182/2026', data='2026',
         url=f'{PD}/2026/07/Lei-Comp.-182-2026-Regularizacao-de-edificacoes-PDF.pdf', arquivo_local='fontes/LC182_2026_Regularizacao.pdf', observacao='Regularização de edificações existentes; não altera parâmetros para obra nova.'),
    dict(id='F11', titulo='Cria a ZEIS Democracia (Mangabeira/Costa do Sol)', lei='Lei nº 15.606/2025', data='2025-08-22',
         url=f'{SAPL}/2025/22299/15.606_-_22.08.25_-_institui_zeis_democracia_mangabeira.pdf', arquivo_local='fontes/Lei15606_2025_ZEIS_Democracia.pdf',
         observacao='DOE-JP nº 840/supl., 25/08/2025. Anexo II: quadro de coordenadas UTM (SIRGAS 2000).'),
    dict(id='F12', titulo='Cria a ZEIS Rio Sanhauá (Varadouro)', lei='Lei nº 15.607/2025', data='2025-08-22',
         url=f'{SAPL}/2025/22300/15.607_-_22.08.25_-_institui_zeis_rio_sanhaua_varadouro.pdf', arquivo_local='fontes/Lei15607_2025_ZEIS_RioSanhaua.pdf',
         observacao='DOE-JP nº 840/supl., 25/08/2025. Anexos I e III–VI: quadros de coordenadas UTM da poligonal e dos 4 setores.'),
    dict(id='F13', titulo='Instruções normativas de aprimoramento da legislação urbanística', lei='Decreto nº 9.718/2021', data='2021-05-10',
         url=f'{PD}/2025/03/DECRETO-9.718-DE-2021-2-1-1.pdf', arquivo_local='fontes/Dec9718_2021.pdf', observacao='Anterior ao novo PD/LUOS; listado no portal como legislação vigente.'),
    dict(id='F14', titulo='Malha municipal IBGE 2024 – Paraíba (limite municipal, CD_MUN 2507507)', lei='IBGE – Malhas Territoriais 2024', data='2024',
         url='https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/UFs/PB/PB_Municipios_2024.zip', arquivo_local='geo_raw/PB_Municipios_2024.zip', observacao='Usada para validar o georreferenciamento dos mapas.'),
    dict(id='F15', titulo='Portal do Plano Diretor – página "Legislação vigente"', lei='Prefeitura Municipal de João Pessoa / SEPLAN', data='2026-10-27',
         url='https://planodiretor.joaopessoa.pb.gov.br/legislacao-vigente/', arquivo_local='fontes/legislacaovigente.html', observacao='Índice oficial dos diplomas urbanísticos vigentes (consultado em 27/10/2026).'),
]

def P(valor, fid, art, obs=None, unidade=None, forma=None, **extra):
    if forma is None:
        forma = 'unico' if isinstance(valor, (int, float)) and not isinstance(valor, bool) else ('lista' if isinstance(valor, list) else 'sem_dado')
    if forma not in ('unico', 'lista'):
        valor = None if forma != 'lista' else valor
    d = dict(valor=valor, unidade=unidade, fonte_id=fid, artigo_anexo=art, observacao=obs, forma=forma)
    for k, v in extra.items():
        if v is not None: d[k] = v
    return d

def C(condicao, valor=None, forma=None, codigo=None, obs=None, texto=None, faixa=None, formula=None):
    if forma is None:
        forma = 'unico' if isinstance(valor, (int, float)) else ('formula' if formula else ('faixa' if faixa else 'sem_dado'))
    d = dict(condicao=condicao, forma=forma, valor=valor if forma in ('unico', 'lista') else None)
    if codigo: d['codigo'] = codigo
    if faixa: d['faixa'] = faixa
    if formula: d['formula'] = formula
    if texto: d['texto_original'] = texto
    if obs: d['observacao'] = obs
    return d

A4 = 'LC 169/2024, Anexo IV (substitui o Anexo V da LUOS) – Quadro de Parâmetros de Ocupação do Solo, DOE-JP nº 0681, p. 4'
A3 = 'LC 169/2024, Anexo III (substitui o Anexo IV da LUOS) – Quadro de Parâmetros de Uso do Solo vinculado à Hierarquia Viária, DOE-JP nº 0681, p. 3'
A5 = 'LC 169/2024, Anexo V (substitui o Anexo VI da LUOS) – Quadro de Número Mínimo de Vagas, DOE-JP nº 0681, p. 5'
DE = '3,00+[(N-4)x0,30]'
DE4 = '4,00+[(N-4)x0,30]'
NOTA_B = ('(B) O uso H3, quando situado nas vias locais e coletoras, poderá utilizar os seguintes parâmetros: até 3 PV: TOmax=50% | TAPmin=5% | '
          'RFTmin=5,00 | RLmin=1,50 | RFDmin=2,00; até 4 PV ou 4 PV+CT: TOmax=55% | TAPmin=5% | RFTmin=5,00 | RLmin=1,50 | RFDmin=3,00.')
NOTA_F = '(F) Observar a restrição de altura na faixa de 500 m da orla.'
NOTA_H = '(H) Os parâmetros indicados seguirão as definições de IPHAN e IPHAEP (poligonal tombada do Centro Histórico e do Sítio Paisagístico do Cabo Branco).'
NOTA_I = '(I) Para todos os usos na ZEPA-2 e ZEPA-3 é necessário licenciamento ambiental, conforme determinação do órgão competente, exceto nos casos dispensados por legislação específica.'
NOTA_J = '(J) Nos lotes regularizados (anteriormente à vigência desta Lei) com área inferior a 2.000 m² os recuos frontal, lateral e de fundo mínimos serão de 5,00 m.'
NOTA_C = '(C) Lotes com frente para rodovias deverão respeitar recuo frontal mínimo de 15,00 m.'
NOTA_A = '(A) Para o uso H1 será permitida Taxa de Ocupação de até 60%.'
NOTA_G = '(G) Para o uso H2 será permitida Taxa de Ocupação de até 60%.'

def rl(*casos):
    """casos: (condicao, valor|None, formula|None)"""
    cs = [C(c, v, formula=f) if f else C(c, v) for c, v, f in casos]
    return P(None, 'F03', A4 + ' – coluna Recuo Lateral (RL)', 'DE = distância exigida; N = número de pavimentos da edificação.', 'm', 'condicional', condicionais=cs)

def rfd(*casos):
    cs = [C(c, v, formula=f) if f else C(c, v) for c, v, f in casos]
    return P(None, 'F03', A4 + ' – coluna Recuo de Fundo (RFD)', 'DE = distância exigida; N = número de pavimentos da edificação.', 'm', 'condicional', condicionais=cs)

def um(v, col, obs=None, unidade='m'):
    return P(v, 'F03', A4 + f' – coluna {col}', obs, unidade)

# --- quadro por zona (LC 169/2024 Anexo IV) ---
ATE3_15_4_30 = rl(('até 3º pavimento', 1.5, None), ('4º pavimento', 3.0, None), ('acima do 4º pavimento', None, DE))
ATE4_30_DE = rfd(('até 4º pavimento', 3.0, None), ('acima do 4º pavimento', None, DE))
Z = {}
Z['ZH-1'] = dict(am='F', to=0.50, tap=0.10, rft=5.0, rl=ATE3_15_4_30, rfd=ATE4_30_DE, notas=[NOTA_A, NOTA_B, NOTA_F])
Z['ZH-2'] = dict(am='H', to=0.55, tap=0.05, rft=5.0, rl=ATE3_15_4_30,
                 rfd=rfd(('até 2º pavimento', 2.0, None), ('3º e 4º pavimentos', 3.0, None), ('acima do 4º pavimento', None, DE)), notas=[NOTA_A, NOTA_B, NOTA_G, NOTA_H])
Z['ZH-3'] = dict(am='F', to=0.50, tap=0.05, rft=5.0, rl=ATE3_15_4_30, rfd=ATE4_30_DE, notas=[NOTA_A, NOTA_B, NOTA_F])
Z['ZH-4'] = dict(am='F', to=0.50, tap=0.15, rft=5.0, rl=rl(('até 3º pavimento', 2.0, None), ('4º pavimento', 4.0, None), ('acima do 4º pavimento', None, DE4)),
                 rfd=rfd(('até 4º pavimento', 3.0, None), ('acima do 4º pavimento', None, DE4)), notas=[NOTA_A, NOTA_B, NOTA_F])
Z['ZH-5'] = dict(am='F', to=0.50, tap=0.15, rft=5.0, rl=rl(('até 2º pavimento', 1.5, None), ('3º e 4º pavimentos', 3.0, None), ('acima do 4º pavimento', None, DE)),
                 rfd=ATE4_30_DE, notas=[NOTA_A, NOTA_B, NOTA_F])
Z['ZCS-1'] = dict(am='H', to=(0.80, 1.00), tap=(0.0, 0.05), rft=0.0, rl=0.0, rfd=2.0, notas=[NOTA_H])
Z['ZCS-2'] = dict(am='H', to=(0.70, 1.00), tap=(0.0, 0.05), rft=(0.0, 5.0), rl=rl(('até 4º pavimento', 0.0, None), ('acima do 4º pavimento', None, DE)),
                  rfd=rfd(('até 4º pavimento', 2.0, None), ('acima do 4º pavimento', None, DE)), notas=[NOTA_H])
Z['ZCS-3'] = dict(am='FH', to=0.65, tap=0.05, rft=5.0, rl=rl(('até 2º pavimento', 0.0, None), ('3º e 4º pavimentos', 2.0, None), ('acima do 4º pavimento', None, DE)),
                  rfd=ATE4_30_DE, notas=[NOTA_B, NOTA_F, NOTA_H])
Z['ZCS-4'] = dict(am='-', to=0.65, tap=0.05, rft=5.0, rl=rl(('até 2º pavimento', 0.0, None), ('3º e 4º pavimentos', 2.0, None), ('acima do 4º pavimento', None, DE)),
                  rfd=rfd(('até 2º pavimento', 2.0, None), ('3º e 4º pavimentos', 3.0, None), ('acima do 4º pavimento', None, DE)), notas=[NOTA_B])
Z['ZCS-5'] = dict(am='F', to=0.50, tap=0.25, rft=10.0, rl=5.0, rfd=5.0, notas=[NOTA_F])
Z['ZCS-6'] = dict(am='F', to=0.30, tap=0.30, rft=10.0, rl=8.0, rfd=8.0, notas=[NOTA_F])
Z['ZCS-7'] = dict(am='-', to=0.65, tap=0.10, rft=8.0, rl=4.0, rfd=4.0, notas=[NOTA_C])
Z['ZEPA-1'] = dict(am='manejo', notas=['De acordo com os planos de manejo específicos, quando couber. (F) (H)'])
Z['ZEPA-2'] = dict(am='FH', to=0.40, tap=0.40, rft=10.0, rl=ATE3_15_4_30,
                   rfd=rfd(('até 2º pavimento', 2.0, None), ('3º e 4º pavimentos', 3.0, None), ('acima do 4º pavimento', None, DE)), notas=[NOTA_I, NOTA_F, NOTA_H])
Z['ZEPA-3'] = dict(am='FH', pav=4, to=0.40, tap=0.40, rft=10.0, rl=rl(('até 2º pavimento', 1.5, None), ('3º e 4º pavimentos', 3.0, None)),
                   rfd=rfd(('até 4º pavimento', 3.0, None)), notas=[NOTA_I, NOTA_F, NOTA_H])
Z['ZI-1'] = dict(am='-', to=0.50, tap=0.10, rft=6.0, rl=3.0, rfd=3.0, notas=[NOTA_C])
Z['ZI-2'] = dict(am='-', to=0.50, tap=0.10, rft=6.0, rl=3.0, rfd=3.0, notas=[])
Z['ZBD'] = dict(am='-', pav=2, to=0.10, tap=0.80, rft=10.0, rl=10.0, rfd=10.0, notas=[NOTA_J, NOTA_C])
Z['ZDTRL'] = dict(am='infra', notas=['Usos relacionados à implantação de estruturas para tratamento e deposição de resíduos líquidos.'])
Z['ZDTRS'] = dict(am='infra', notas=['Usos relacionados à implantação de estruturas para deposição de resíduos sólidos.'])
Z['SEAV'] = dict(am='-', to=0.40, tap=0.15, rft=5.0, rl=ATE3_15_4_30,
                 rfd=rfd(('até 2º pavimento', 2.0, None), ('3º e 4º pavimentos', 3.0, None), ('acima do 4º pavimento', None, DE)), notas=[])

NOMES = {
    'ZH-1': ('Zona Habitacional 1', 'LUOS art. 10: ocupação habitacional com maior densidade, conforme infraestrutura; usos compatíveis de comércio e serviços vicinais e de bairro.'),
    'ZH-2': ('Zona Habitacional 2', 'LUOS art. 11: ocupação habitacional de densidade média, com usos compatíveis vicinais e de bairro.'),
    'ZH-3': ('Zona Habitacional 3', 'LUOS art. 12: Zona Costeira, na faixa de 500 m de restrição da orla marítima.'),
    'ZH-4': ('Zona Habitacional 4', 'LUOS art. 13: planalto do Altiplano e Portal do Sol, com restrições ambientais, de infraestrutura e da orla.'),
    'ZH-5': ('Zona Habitacional 5', 'LUOS art. 14: Ponta do Seixas, Penha, Barra do Gramame e NO da Costa do Sol; turismo e atividades de baixo/médio impacto; restrição da orla.'),
    'ZCS-1': ('Zona de Comércio e Serviço 1', 'LUOS arts. 16–17: núcleo histórico; áreas tombadas e de restrição do Centro Histórico (análise IPHAN/IPHAEP); estímulo ao uso habitacional.'),
    'ZCS-2': ('Zona de Comércio e Serviço 2', 'LUOS arts. 18–19: faixa das áreas tombadas e de restrição do Centro Histórico (IPHAN/IPHAEP); lotes maiores; estímulo ao uso misto.'),
    'ZCS-3': ('Zona de Comércio e Serviço 3', 'LUOS art. 20: corredores de estruturação urbana, parcialmente na restrição da orla; desenvolvimento de centralidades.'),
    'ZCS-4': ('Zona de Comércio e Serviço 4', 'LUOS art. 21: corredores de transporte público; usos habitacionais, não habitacionais e mistos; centralidades.'),
    'ZCS-5': ('Zona de Comércio e Serviço 5', 'LUOS art. 22: porção norte do Polo Turístico do Cabo Branco (Lei Estadual 10.781/2016); multifamiliar, hotelaria, comércio e serviços turísticos; restrição da orla.'),
    'ZCS-6': ('Zona de Comércio e Serviço 6', 'LUOS art. 23: porção sul do Polo Turístico do Cabo Branco; grandes equipamentos turísticos; restrição da orla.'),
    'ZCS-7': ('Zona de Comércio e Serviço 7', 'LUOS art. 24: grandes equipamentos ao longo das rodovias federais e corredores; empreendimentos de grande porte não compatíveis com o uso habitacional.'),
    'ZEPA-1': ('Zona Especial de Proteção Ambiental 1', 'LUOS art. 27: falésias, Mata do Buraquinho, parques municipais, manguezais, restingas, estuários e áreas preservadas por legislação federal; usos conforme planos de manejo.'),
    'ZEPA-2': ('Zona Especial de Proteção Ambiental 2', 'LUOS art. 28: áreas ambientalmente frágeis (planícies de inundação, falésias, bordas de tabuleiro, vales, nascentes) e de transição; anuência da SEMAM; nenhuma construção na faixa de 100 m das falésias.'),
    'ZEPA-3': ('Zona Especial de Proteção Ambiental 3', 'LUOS art. 29: porção da orla do Cabo Branco e falésia do Altiplano; hotelaria e restaurantes; uso vinculado a EIV/EVA/DA analisado pela SEMAM.'),
    'ZI-1': ('Zona Industrial 1', 'LUOS arts. 30–31: Distrito Industrial, Bairro das Indústrias, Costa e Silva e Gramame (BR-101); médias e grandes indústrias; uso habitacional proibido.'),
    'ZI-2': ('Zona Industrial 2', 'LUOS arts. 30 e 32: Mangabeira, margem da Av. Hilton Souto Maior; pequenas e médias indústrias; uso habitacional proibido.'),
    'ZBD': ('Zona de Baixa Densidade', 'LUOS art. 33: Oeste e Sul do município; controle da expansão urbana, características rurais, recarga de manancial; lote mínimo 20.000 m².'),
    'ZDTRL': ('Zona de Deposição e Tratamento de Resíduos Líquidos', 'LUOS art. 34: equipamentos do sistema de esgotamento sanitário; condições especiais (SEPLAN/SEMAM/CDU).'),
    'ZDTRS': ('Zona de Deposição e Tratamento de Resíduos Sólidos', 'LUOS art. 35: aterro sanitário; condições especiais (SEPLAN/EMLUR/SEMAM/CDU).'),
    'SEAV': ('Setor Especial de Áreas Verdes', 'LUOS arts. 36–41: setor preponderante ao zoneamento, incidente em áreas da ZEPA-2; IA máximo flexibilizado até 2,0 mediante Outorga Onerosa Ambiental e preservação/recuperação (Anexo VII).'),
}

# usos (LC 169/2024 Anexo III + notas): códigos da LUOS arts. 45–48
TODOS = ['H1', 'H2', 'H3', 'CG/SG', 'CE/SE', 'HT', 'IND1']
USOS = {}
for z in ['ZH-1', 'ZH-2', 'ZH-3', 'ZH-4', 'ZH-5', 'ZCS-1', 'ZCS-2', 'ZCS-3', 'ZCS-4', 'ZCS-5', 'ZEPA-2', 'ZEPA-3', 'SEAV']:
    USOS[z] = TODOS
USOS['ZCS-6'] = ['HT', 'CG/SG', 'CE/SE']
USOS['ZCS-7'] = ['CG/SG', 'CE/SE', 'HT', 'IND1']
USOS['ZI-1'] = ['CG/SG', 'CE/SE', 'HT', 'IND1', 'IND2', 'IND3', 'EXT']
USOS['ZI-2'] = ['CG/SG', 'CE/SE', 'HT', 'IND1', 'IND2']
USOS['ZBD'] = ['H1', 'H2', 'CG/SG', 'CE/SE', 'HT', 'IND1', 'AGROSSILVIPASTORIL', 'EXT']
USOS['ZH-2'] = TODOS + ['EXT']
USOS_OBS = {
    'ZCS-6': 'Na ZCS-6 apenas usos HT e comércio/serviços relacionados ao turismo e seu apoio (classificados por ato do Executivo), independente da hierarquia viária. Habitação multifamiliar (H3) NÃO permitida.',
    'ZCS-7': 'Usos habitacionais (H1, H2, H3) proibidos na ZCS-7 em qualquer hierarquia viária.',
    'ZI-1': 'Usos habitacionais proibidos (LUOS art. 30; Anexo III). IND3 só na ZI-1.',
    'ZI-2': 'Usos habitacionais proibidos (LUOS art. 30; Anexo III). IND2 permitido na ZI-1 e ZI-2.',
    'ZBD': 'Na ZBD não são permitidos H3, IND-2 e IND-3; comércio e serviço com mais de 500 m² dependem de aprovação SEMAM e SEMOB.',
    'ZEPA-2': 'Todos os usos dependem de licenciamento ambiental; proibidos postos de combustível, oficinas, lava-jatos e cemitérios nas ZEPAs; anuência SEMAM (LUOS art. 28 §1º); vedada construção na faixa de 100 m das falésias (art. 28 §2º).',
    'ZEPA-3': 'Todos os usos dependem de licenciamento ambiental e de EIV/EVA/DA (LUOS art. 29 p.ú.); proibidos postos, oficinas, lava-jatos e cemitérios nas ZEPAs.',
    'SEAV': 'Usos e parâmetros do SEAV conforme Anexos IV e V e requisitos da Lei de Parcelamento (LUOS art. 38); respeitar APPs do Código Florestal (art. 36 p.ú.).',
    'ZCS-1': 'Proibidos postos de combustível na poligonal do Centro Histórico. Análise IPHAN/IPHAEP.',
    'ZCS-2': 'Proibidos postos de combustível na poligonal do Centro Histórico. Análise IPHAN/IPHAEP.',
}
REGRA_VIA = ('Anexo III: todos os usos permitidos, exceto IND2 (só ZI-1/ZI-2), IND3 (só ZI-1) e habitacionais em ZI-1, ZI-2 e ZCS-7. Via local: vedados empreendimentos de impacto, '
             'CE/SE >1.000 m² e HT >100 quartos; CG/SG >1.000 m² com aprovação SEMOB; CE/SE até 1.000 m² com aprovação SEMAM. Via coletora: habitacionais com mais de 100 UH '
             'com aprovação SEMOB. Via arterial: habitacionais com mais de 200 UH com aprovação SEMOB. Via expressa: não habitacionais/mistos >2.000 m² com aprovação SEMOB. '
             'UH permitidas em todos os pavimentos, inclusive térreo (LUOS art. 44 §3º).')

IA_MACRO = {'MAD-1': (1, 6), 'MAD-2': (1, 4), 'MAD-3': (1, 2), 'MBD': (1, 1), 'MPA': (1, 1)}
NOME_MACRO = {'MAD-1': 'Macrozona Adensável 1', 'MAD-2': 'Macrozona Adensável 2', 'MAD-3': 'Macrozona Adensável 3',
              'MBD': 'Macrozona de Baixa Densidade', 'MPA': 'Macrozona de Proteção Ambiental'}
