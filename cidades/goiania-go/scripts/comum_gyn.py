"""Fontes e construtores de parâmetro (schema 1.1) para Goiânia-GO."""
HOJE = '2026-10-27'
SL = 'https://www.goiania.go.gov.br/html/gabinete_civil/sileg/dados/legis/'
PM = 'https://portalmapa.goiania.go.gov.br/servicogyn/rest/services/MapaServer/'
ME = PM + 'Mapa_ModeloEspacial/MapServer'
SIMP = PM + 'Mapa_Simplifica_Goiania_UsoDoSolo/FeatureServer'
FONTES = [
 ('F01', 'Plano Diretor de Goiânia – texto compilado no SILEG (com as alterações das LC 363/2023, 371/2024, 373/2024 e 379/2024)', 'Lei Complementar Municipal nº 349/2022', '2022-03-04', SL + '2022/lc_20220304_000000349.html', 'lc349.html'),
 ('F02', 'Plano Diretor – Anexos XXI (Tabela de Parâmetros Urbanísticos – afastamentos × altura) e XXII (Área de Entorno do Bem Tombado)', 'LC nº 349/2022, Anexos XXI e XXII (PDF original; Anexo XXI com redação da LC 371/2024 conferida no texto compilado)', '2022-03-04', SL + '2022/lc_20220304_000000349_ane_000000021.pdf', 'anexos/lc349_ane_21.pdf'),
 ('F03', 'Ocupação dos vazios urbanos – PDU I a IV, Conjuntos Residenciais (altera a LC 349/2022)', 'Lei Complementar Municipal nº 371/2024', '2024-01-04', SL + '2024/lc_20240104_000000371.html', 'atos/lc_20240104_000000371.html'),
 ('F04', 'Outorga Onerosa do Direito de Construir – OODC (fórmula VOO = Vm × Vi × Qsc)', 'Lei Complementar Municipal nº 373/2024', '2024-01-19', SL + '2024/lc_20240119_000000373.html', 'atos/lc_20240119_000000373.html'),
 ('F05', 'Parâmetros urbanísticos e edilícios para Habitação de Interesse Social – HIS (regulamenta o art. 288 da LC 349/2022; partes vetadas promulgadas em 12/02/2025)', 'Lei Complementar Municipal nº 379/2024', '2024-06-12', SL + '2024/lc_20240612_000000379.html', 'atos/lc_20240612_000000379.html'),
 ('F06', 'Áreas de Programas Especiais de Interesse Social – AEIS I, II e III', 'Lei Municipal nº 11.083/2023', '2023-11-06', SL + '2023/lo_20231106_000011083.html', 'atos/lo_20231106_000011083.html'),
 ('F07', 'Código de Obras e Edificações (vagas: arts. 110–112)', 'Lei Complementar Municipal nº 364/2023 (com alterações da LC 379/2024)', '2023-01-13', SL + '2023/lc_20230113_000000364.html', 'atos/lc_20230113_000000364.html'),
 ('F08', 'Estudo de Impacto de Vizinhança – EIV/RIV', 'Lei Municipal nº 11.127/2024', '2024-01-04', SL + '2024/lo_20240104_000011127.html', 'atos/lo_20240104_000011127.html'),
 ('F09', 'Transferência do Direito de Construir – TDC', 'Lei Municipal nº 10.848/2022 (art. 14 com redação da LC 373/2024)', '2022-11-11', SL + '2022/lo_20221111_000010848.html', 'atos/lo_20221111_000010848.html'),
 ('F10', 'Suspensão da concessão de novas TDC por 18 meses a partir de 01/01/2025 e regras de CPC/CPC-S (até 50% da OODC; até 25% da altura no receptor)', 'Decreto Municipal nº 2.785/2025', '2025-06-11', SL + '2025/dc_20250611_000002785.html', 'atos/dc_20250611_000002785.html'),
 ('F11', 'Prorroga por mais 18 meses (efeitos a partir de 01/07/2026) a suspensão da TDC do Dec. 2.785/2025', 'Decreto Municipal nº 82/2026', '2026-07-03', SL + '2026/dc_20260703_000000082.html', 'atos/dc_20260703_000000082.html'),
 ('F12', 'Controle das atividades econômicas (graus de incomodidade × hierarquia viária)', 'Lei Municipal nº 10.845/2022', '2022-11-04', SL + '2022/lo_20221104_000010845.html', 'atos/lo_20221104_000010845.html'),
 ('F13', 'Portal Mapa Goiânia (SEPLANH) – "Simplifica Goiânia – Uso do Solo", camada 3 Unidades Territoriais (Modelo Espacial – Anexo XIV)', 'Prefeitura de Goiânia – serviço ArcGIS REST público', HOJE, SIMP + '/3', None),
 ('F14', 'Portal Mapa Goiânia – Mapa_ModeloEspacial (Plano Diretor 2022: APAC, ARAU, AEIS, programas especiais, macrozoneamento, OOAU, IVE, corredores, restrições aeroportuária e militar)', 'Prefeitura de Goiânia – serviço ArcGIS REST público', HOJE, ME, None),
 ('F15', 'Código de Parcelamento do Solo', 'Lei Complementar Municipal nº 363/2023', '2023-01-12', SL + '2023/lc_20230112_000000363.html', 'atos/lc_20230112_000000363.html'),
    ('F16', 'Regulamenta o Plano Urbanístico Básico – PUB (projeto global ≥ 50 ha)', 'Decreto Municipal nº 117/2026', '2026-08-06', SL + '2026/dc_20260806_000000117.html', 'atos/dc_20260806_000000117.html'),
]
FID = {f[0] for f in FONTES}

def P(valor, unidade, fonte, art, obs=None, forma=None, **kw):
    if forma is None:
        forma = 'unico' if isinstance(valor, (int, float)) and not isinstance(valor, bool) else ('lista' if isinstance(valor, list) else 'sem_dado')
    assert fonte is None or fonte in FID, fonte
    d = dict(valor=valor, unidade=unidade, fonte_id=fonte, artigo_anexo=art, observacao=obs, forma=forma)
    d.update(kw)
    return d

def TXT(texto, unidade, fonte, art, obs=None):
    return P(None, unidade, fonte, art, obs, forma='texto', texto_original=texto)

def SEM(unidade, obs, art=None):
    return P(None, unidade, None, art, obs, forma='sem_dado')

def NA(unidade, fonte, art, obs):
    return P(None, unidade, fonte, art, obs, forma='nao_aplicavel')

def LIVRE(unidade, fonte, art, obs):
    return P(None, unidade, fonte, art, obs, forma='livre')

def F(unidade, fonte, art, obs, formula):
    return P(None, unidade, fonte, art, obs, forma='formula', formula=formula)

def C(condicao, forma, valor=None, **kw):
    d = dict(condicao=condicao, forma=forma, valor=valor); d.update(kw); return d

def COND(unidade, fonte, art, obs, conds):
    return P(None, unidade, fonte, art, obs, forma='condicional', condicionais=conds)
