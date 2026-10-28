"""Fontes e parâmetros urbanísticos do Recife-PE (schema 1.1). Base: LPUOS Lei 19.426/2025 (texto e anexos conforme
Parecer Final de Redação nº 75/2025 da Câmara, idêntico em numeração ao publicado no DOM nº 125 de 04/10/2025)."""
EP = 'https://e-processo.recife.pe.leg.br'
FONTES = [
    dict(id='F01', titulo='Lei de Parcelamento, Uso e Ocupação do Solo do Recife (LPUOS) – publicação no Diário Oficial', lei='Lei nº 19.426/2025', data='2025-10-02',
         url=f'{EP}/sapl_documentos/norma_juridica/2159_anexo_2179', arquivo_local='fontes/Lei19426_2025_DOM_publicacao.pdf',
         observacao='Sancionada em 02/10/2025; DOM do Recife nº 125, 04/10/2025 (pp. 3–12: texto e Anexo I). Vigência 60 dias após a publicação (art. 204). Página da norma: ' + EP + '/consultas/norma_juridica/norma_juridica_mostrar_proc?cod_norma=2159 . Texto integral (PDF com OCR): ' + EP + '/pysc/download_norma_pysc?cod_norma=2159&texto_original=1 (fontes/Lei19426_2025_LPUOS.pdf).'),
    dict(id='F02', titulo='PLE nº 16/2025 – Parecer Final de Redação nº 75/2025 (texto aprovado com todos os anexos)', lei='Câmara Municipal do Recife – Comissão de Redação', data='2025-09-23',
         url=f'{EP}/sapl_documentos/parecer_comissao/4081_parecer.pdf', arquivo_local='fontes/PLE16_2025_Parecer_Redacao_Final_75_2025.pdf',
         observacao='Redação final aprovada em 23/09/2025 e enviada à sanção (Ofício 386/2025-CMR). Contém os Anexos II (mapas, versão final SETEMBRO/2025 para 3A/3B/3C) a XX como aprovados. Usado para os quadros dos Anexos IV, XV e XVIII (texto extraído em fontes/LPUOS_texto_aprovado_limpo.txt). Numeração de artigos idêntica à do DOM.'),
    dict(id='F03', titulo='PLE nº 16/2025 – proposição original do Executivo com anexos (mapas em maior resolução)', lei='Projeto de Lei do Executivo nº 16/2025', data='2025-05',
         url=f'{EP}/sapl_documentos/proposicao/61535_signed.pdf', arquivo_local='fontes/PLE16_2025_LPUOS_proposicao_com_anexos.pdf',
         observacao='Mapas do Anexo II datados MAIO/2025 (1213x1710 px). Usados para Mapas 1, 2, 4 e 6 (idênticos aos da redação final) e como referência de registro para 3A/3B/3C.'),
    dict(id='F04', titulo='Parecer da Comissão Especial (CELPUOS) nº 1/2025 ao PLE 16/2025 – emendas', lei='Câmara Municipal do Recife', data='2025-09-22',
         url=f'{EP}/sapl_documentos/parecer_comissao/3689_parecer.pdf', arquivo_local='fontes/PLE16_2025_Parecer_CELPUOS_1_2025.pdf', observacao='Aprovação com emendas, subemendas e emendas de relatoria.'),
    dict(id='F05', titulo='Tramitação do PLE 16/2025 (matéria) – sanção e publicação', lei='Câmara Municipal do Recife', data='2025-10-06',
         url=f'{EP}/consultas/materia/materia_mostrar_proc?cod_materia=MTYzNjMx', arquivo_local=None,
         observacao='Registro de 06/10/2025: "LEI Nº 19.426/2025, SANCIONADO EM 02/10/2025, PUBLICADA NO DIÁRIO OFICIAL DO MUNICÍPIO Nº 125, DE 04/10/2025" (' + EP + '/sapl_documentos/materia/tramitacao/475360_tram.pdf).'),
    dict(id='F06', titulo='Regulamenta a Outorga Onerosa do Direito de Construir (OODC) – arts. 98, VI e 115 a 123 do Plano Diretor', lei='Lei nº 18.900/2022', data='2022-03-23',
         url='https://licenciamentounificado.recife.pe.gov.br/189002022', arquivo_local=None,
         observacao='Página oficial do Licenciamento Unificado (DO Recife nº 040, 24/03/2022). NÃO acessível do ambiente de coleta (todos os hosts *.recife.pe.gov.br recusam a conexão); conteúdo não verificado – citada apenas porque a LPUOS remete a ela (arts. 116 §4º e 168).'),
]
LP = 'Lei 19.426/2025'
A4 = 'Lei 19.426/2025, Anexo IV – Parâmetros Urbanísticos de Ocupação (redação final, Parecer 75/2025 pp. 102–106)'
A18 = 'Lei 19.426/2025, Anexo XVIII – TSN e TCA (redação final, Parecer 75/2025)'

def P(valor, fid, art, obs=None, unidade=None, forma=None, **extra):
    if forma is None:
        forma = 'unico' if isinstance(valor, (int, float)) and not isinstance(valor, bool) else ('lista' if isinstance(valor, list) else 'sem_dado')
    if forma not in ('unico', 'lista'): valor = None
    d = dict(valor=valor, unidade=unidade, fonte_id=fid, artigo_anexo=art, observacao=obs, forma=forma)
    for k, v in extra.items():
        if v is not None: d[k] = v
    return d

def C(condicao, valor=None, forma=None, codigo=None, obs=None, texto=None, faixa=None, formula=None):
    if forma is None:
        forma = 'unico' if isinstance(valor, (int, float)) else ('formula' if formula else ('faixa' if faixa else 'nao_aplicavel'))
    d = dict(condicao=condicao, forma=forma, valor=valor if forma in ('unico', 'lista') else None)
    if codigo: d['codigo'] = codigo
    if faixa: d['faixa'] = faixa
    if formula: d['formula'] = formula
    if texto: d['texto_original'] = texto
    if obs: d['observacao'] = obs
    return d

NA = None
# Anexo IV (final). Campos: ca(min,bas,max) | cota-parte m2 | IAC | gab (m,pav) | af. frontal (<=26m/8pav, >26m/8pav) | lat/fundos (<=8m/2pav, <=26m/8pav, <=80m/25pav, >80m/25pav) | TO (<=8 pav, >8 pav acima do 4º) | nota gabarito
A4T = {
 'ZAN-CAPIBARIBE':   dict(ca=(NA, 1, 1), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAN-TEJIPIO':      dict(ca=(NA, 1, 1), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAN-BEBERIBE':     dict(ca=(NA, 1, 1), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAN-ORLA':         dict(ca=(NA, 1, 1), cota=NA, iac=NA, gab=NA, fr=(NA, NA), lat=(NA, NA, NA, NA), to=(NA, NA), nota=4),
 'ZDS-BEBERIBE':     dict(ca=(0.1, 1, 2), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZDS-CAPIBARIBE-A': dict(ca=(0.1, 1, 2), cota=NA, iac=0.4, gab=(26, 8), fr=(5, NA), lat=(1.5, 3, NA, NA), to=('TSN', NA), nota=3),
 'ZDS-CAPIBARIBE-B': dict(ca=(0.1, 1, 2), cota=NA, iac=0.4, gab=(51, 16), fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZDS-CAPIBARIBE-C': dict(ca=(0.1, 1, 2), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=3),
 'ZDS-TEJIPIO':      dict(ca=(0.1, 1, 2), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZDS-CENTRO':       dict(ca=(0.1, 1, 2), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=3),
 'ZONA-CENTRO':      dict(ca=(0.5, 1, 5), cota=30, iac=0.4, gab=NA, fr=(3, 3), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZRU-1-A':          dict(ca=(0.4, 1, 5), cota=30, iac=0.4, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZRU-1-B':          dict(ca=(0.4, 1, 5), cota=35, iac=0.4, gab=(65, 20), fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZRU-1-C':          dict(ca=(0.4, 1, 5), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAC-PLANICIE-1-A': dict(ca=(0.3, 1, 4), cota=NA, iac=0.4, gab=(65, 20), fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAC-PLANICIE-1-B': dict(ca=(0.3, 1, 4), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAC-PLANICIE-2':   dict(ca=(0.1, 1, 4), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
 'ZAC-MORRO':        dict(ca=(0.1, 1, 1.5), cota=NA, iac=0.5, gab=NA, fr=(3, 7), lat=(1.5, 3, NA, NA), to=('TSN', 0.40), nota=None),
 'ZAC-ORLA':         dict(ca=(0.3, 1, 3), cota=NA, iac=0.5, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=4),
 'ZEC-1':            dict(ca=(0.5, 1, 5), cota=40, iac=0.4, gab=NA, fr=(5, 7), lat=(1.5, 3, 4, 5), to=('TSN', 0.40), nota=None),
}
# Anexo XVIII final: (TCA, TSN) para T<500, 500<=T<2000, T>2000 (em %); None = N/A
A18T = {
 'ZAN': ((None, 40), (10, 50), (10, 50)), 'ZDS-BEBERIBE': ((10, 30), (15, 40), (10, 50)),
 'ZDS-CAPIBARIBE-A': ((15, 30), (5, 55), (10, 60)), 'ZDS-CAPIBARIBE-B': ((10, 30), (5, 45), (5, 50)), 'ZDS-CAPIBARIBE-C': ((10, 30), (20, 20), (25, 30)),
 'ZDS-TEJIPIO': ((10, 30), (20, 30), (30, 30)), 'ZDS-CENTRO': ((10, 30), (20, 30), (30, 30)), 'ZONA-CENTRO': ((10, 10), (10, 20), (25, 20)),
 'ZRU-1-A': ((15, 15), (15, 20), (15, 20)), 'ZRU-1-C': ((15, 15), (15, 20), (15, 20)), 'ZRU-1-B': ((15, 15), (10, 25), (10, 25)),
 'ZAC-PLANICIE-1': ((15, 20), (15, 20), (25, 25)), 'ZAC-PLANICIE-2': ((20, 20), (20, 25), (25, 25)), 'ZAC-MORRO': ((10, 15), (20, 15), (25, 20)),
 'ZAC-ORLA': ((10, 20), (25, 20), (30, 20)), 'ZEC-1': ((10, 15), (15, 15), (20, 20)), 'ZEIS': ((None, 10), (None, 20), (None, 20)),
}
def a18(cod):
    if cod.startswith('ZAN'): return A18T['ZAN']
    if cod.startswith('ZAC-PLANICIE-1'): return A18T['ZAC-PLANICIE-1']
    if cod.startswith('ZEIS'): return A18T['ZEIS']
    return A18T[cod]
NOMES = {
 'ZAN-ORLA': ('ZAN Orla', 'Zona de Ambiente Natural – Orla (faixa de praia), MANC.'),
 'ZAN-CAPIBARIBE': ('ZAN Capibaribe', 'Zona de Ambiente Natural – Capibaribe, MANC.'),
 'ZAN-TEJIPIO': ('ZAN Tejipió', 'Zona de Ambiente Natural – Tejipió, MANC.'),
 'ZAN-BEBERIBE': ('ZAN Beberibe', 'Zona de Ambiente Natural – Beberibe, MANC (inclui a porção norte de mata).'),
 'ZDS-BEBERIBE': ('ZDS Beberibe', 'Zona de Desenvolvimento Sustentável – Beberibe, MANC.'),
 'ZDS-CAPIBARIBE-A': ('ZDS Capibaribe – Setor A', 'Zona de Desenvolvimento Sustentável – Capibaribe, Setor A (gabarito 26 m/8 pav), MANC.'),
 'ZDS-CAPIBARIBE-B': ('ZDS Capibaribe – Setor B', 'Zona de Desenvolvimento Sustentável – Capibaribe, Setor B (gabarito 51 m/16 pav), MANC.'),
 'ZDS-CAPIBARIBE-C': ('ZDS Capibaribe – Setor C', 'Zona de Desenvolvimento Sustentável – Capibaribe, Setor C (sem gabarito no Anexo IV; 24 m em lotes lindeiros ao rio), MANC.'),
 'ZDS-TEJIPIO': ('ZDS Tejipió', 'Zona de Desenvolvimento Sustentável – Tejipió, MANC.'),
 'ZDS-CENTRO': ('ZDS Centro', 'Zona de Desenvolvimento Sustentável – Centro, MANC.'),
 'ZONA-CENTRO': ('Zona Centro', 'Zona Centro, MAC.'),
 'ZRU-1-A': ('ZRU 1 – Setor A', 'Zona de Reestruturação Urbana 1, Setor A (corredores de transporte), MAC.'),
 'ZRU-1-B': ('ZRU 1 – Setor B', 'Zona de Reestruturação Urbana 1, Setor B (gabarito 65 m/20 pav), MAC.'),
 'ZRU-1-C': ('ZRU 1 – Setor C', 'Zona de Reestruturação Urbana 1, Setor C – antiga ZRU 2/ZAC Orla do Plano Diretor, convertida pelo art. 10.'),
 'ZAC-PLANICIE-1-A': ('ZAC Planície 1 – Setor A', 'Zona de Ambiente Construído Planície 1, Setor A (gabarito 65 m/20 pav), MAC.'),
 'ZAC-PLANICIE-1-B': ('ZAC Planície 1 – Setor B', 'Zona de Ambiente Construído Planície 1, Setor B, MAC.'),
 'ZAC-PLANICIE-2': ('ZAC Planície 2', 'Zona de Ambiente Construído Planície 2, MAC.'),
 'ZAC-MORRO': ('ZAC Morro', 'Zona de Ambiente Construído Morro, MAC.'),
 'ZAC-ORLA': ('ZAC Orla', 'Zona de Ambiente Construído Orla, MAC (42 m em lotes lindeiros à Av. Boa Viagem).'),
}
CATEG = {'ZAN': ('ambiental', 'Zona de Ambiente Natural (MANC); CA máx 1.'),
         'ZDS': ('mista_media_densidade', 'MANC com uso misto (art. 100) e CA máx 2 (≤3).'),
         'ZONA-CENTRO': ('centralidade', 'Zona Centro (núcleo central), CA máx 5.'),
         'ZRU': ('mista_alta_densidade', 'Zona de Reestruturação Urbana (eixos de transporte), uso misto, CA máx 5 (>3).'),
         'ZAC-PLANICIE': ('mista_alta_densidade', 'MAC, uso misto, CA máx 4 (>3).'),
         'ZAC-MORRO': ('mista_baixa_densidade', 'MAC, uso misto, CA máx 1,5 (≤1,5)'),
         'ZAC-ORLA': ('mista_media_densidade', 'MAC, uso misto, CA máx 3 (≤3).')}

# Anexo V – gabarito dos SPA (Setor de Preservação da Ambiência) por ZEPH: extração parcial e não exaustiva do quadro
SPA_GAB = [('ZEPH Sítio Trindade SPA-1', 13, 4), ('ZEPH Sítio Trindade SPA-2', 26, 8), ('ZEPH Apipucos SPA-1', 7, 2), ('ZEPH Apipucos SPA-2', 10, 3),
    ('ZEPH Benfica SPA-1', 10, 3), ('ZEPH Benfica SPA-2', 26, 8), ('ZEPH Capunga SPA-1', 13, 4), ('ZEPH Capunga SPA-2', 7, 2),
    ('ZEPH Poço da Panela SPA-1', 7, 2), ('ZEPH Poço da Panela SPA-2', 13, 4), ('ZEPH Poço da Panela SPA-3', 38, 12), ('ZEPH Ponte d’Uchoa SPA', 13, 4),
    ('ZEPH Várzea SPA', 7, 2), ('ZEPH Santo Antônio e São José SPA', 13, 4), ('ZEPH Casa de Ferro SPA', 13, 4), ('ZEPH Casarão do Barbalho SPA', 13, 4),
    ('ZEPH Escola Rural Alberto Torres SPA', 13, 4), ('ZEPH Faculdade de Direito SPA', 26, 8), ('ZEPH Hospital Pedro II SPA', 26, 8),
    ('ZEPH Igreja das Fronteiras SPA', 7, 2), ('ZEPH Igreja de Santo Amaro das Salinas/Cemitério dos Ingleses SPA', 7, 2), ('ZEPH Soledade SPA', 26, 8),
    ('ZEPH Derby SPA', 26, 8), ('ZEPH Sobrado da Madalena SPA', 13, 4), ('ZEPH Fábrica da Tacaruna SPA', 7, 2), ('ZEPH Matadouro de Peixinhos SPA', 13, 4),
    ('ZEPH Arraial Novo do Bom Jesus SPA', 13, 4), ('ZEPH Dois Irmãos SPA', 13, 4), ('ZEPH Praça Ministro Salgado Filho SPA', 16, 5), ('ZEPH Cotonifício da Torre SPA', 16, 5)]
ZEIS1_NOVAS = ['Beira Rio', 'Chamego', 'Clotilde de Oliveira', 'Córrego da Fortuna', 'Curral Torrões', 'Feira Velha do Cordeiro', 'Rosarinho', 'Santa Luzia',
    'Santa Marta', 'Sete Mocambos', 'Sítio dos Pintos', 'Sítio do Forte/Coreia', 'Vacaria', 'Vila Brasil', 'Vila Sul', 'Vilas Boas e Nova Conquista']
