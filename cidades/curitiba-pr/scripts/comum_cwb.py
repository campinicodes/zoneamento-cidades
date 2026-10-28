"""Fontes e construtores de parâmetro (schema 1.1) para Curitiba-PR."""
HOJE = '2026-10-27'
LD = 'https://legisladocexterno.curitiba.pr.gov.br/'
VH = LD + 'VisualizarHTML.aspx?id='
AX = LD + 'DownloadAnexo.ashx?tipo=pdf&id='
GEO = 'https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/'
MC = GEO + 'Publico_GeoCuritiba_MapaCadastral/MapServer'
FONTES = [
 ('F01', 'Lei de Zoneamento, Uso e Ocupação do Solo – texto compilado (Legisladoc) e publicação original', 'Lei Municipal nº 15.511/2019', '2019-10-10', VH + '290871', 'Lei15511_2019_compilada.txt'),
 ('F02', 'Lei 15.511/2019 – Quadros de parâmetros (anexos): I–IX eixos estruturantes (anexo 19282), X–XIV eixos de adensamento/conectores (19281), XV–XXIV ZC/ZR (19286), XXV–XXX ZUM/ZSM/ZFR (19287), XXXI–XLI zonas especiais (19288), XLII–XLIII SEPE (19289), XLIV–XLVIII vias setoriais/coletoras (19285), XLIX SEHIS (19284)', 'Lei Municipal nº 15.511/2019, Quadros I a XLIX', '2019-10-10', AX + '19282', 'L15511_Q01-09_Eixos_Estruturantes.pdf'),
 ('F03', 'Aquisição de potencial construtivo adicional – OODC, TDC e CPC (Quadros I a V)', 'Lei Municipal nº 16.361/2024', '2024', VH + '416150', 'Lei16361_2024_outorga.txt'),
 ('F04', 'Condições especiais de ocupação para HIS em parceria com a COHAB-CT (regulamenta art. 224 par. único da Lei 15.511) – revoga o Dec. 1.449/2022; mapas Anexos II e III (anexo 73928)', 'Decreto Municipal nº 297/2026', '2026', VH + '465685', 'Dec297_2026_HIS.txt'),
 ('F05', 'Regulamentação das Edificações (definições, afastamentos, permeabilidade, recuo, densidade, vagas, recreação)', 'Decreto Municipal nº 2.397/2023 (em vigor desde 03/01/2024)', '2023-12-19', 'https://mid.curitiba.pr.gov.br/2024/00427509.pdf', 'Dec2397_2023_vagas.pdf'),
 ('F06', 'Regulamenta os arts. 214 e 217 a 220 da Lei 15.511 – locais onde não se admitem novos estacionamentos', 'Decreto Municipal nº 209/2024', '2024', VH + '408040', 'Dec209_2024_estacionamento.txt'),
 ('F07', 'Prêmios, incentivos construtivos e condições especiais de ocupação (revoga a Lei 15.824/2021)', 'Lei Municipal nº 16.448/2024', '2024-12-03', VH + '436120', 'Lei16448_2024_premios.txt'),
 ('F08', 'Plano Diretor de Curitiba (revisão) – macrozoneamento, instrumentos', 'Lei Municipal nº 14.771/2015', '2015-12-17', VH + '209820', 'Lei14771_2015_PD.txt'),
 ('F09', 'Operação Urbana Consorciada Linha Verde – CEPAC (com alterações da Lei 14.773/2015, ato 209830)', 'Lei Municipal nº 13.909/2011 e Lei nº 14.773/2015', '2011-12-19', VH + '143116', 'Lei13909_2011_OUCLV.txt'),
 ('F10', 'Programa Curitiba de Volta ao Centro – Setor Especial da Região Central (SERC), retrofit e incentivos fiscais', 'Lei Complementar Municipal nº 150/2025', '2025-12-18', VH + '461267', 'LC150_2025_VoltaCentro.txt'),
 ('F11', 'Regulamenta o SERC – coeficientes adicionais não onerosos por setor (novas edificações e retrofit)', 'Decreto Municipal nº 418/2026', '2026', VH + '466849', 'Dec418_2026_SERC.txt'),
 ('F12', 'Regulamenta o retrofit da LC 150/2025', 'Decreto Municipal nº 1.109/2026', '2026', VH + '476311', 'Dec1109_2026_retrofit.txt'),
 ('F13', 'Incentivos construtivos e prêmios na ZC e ZCC (arts. 35 e 78 da Lei 15.511)', 'Decreto Municipal nº 1.730/2020', '2020', VH + '320660', 'Dec1730_2020_ZC_ZCC.txt'),
 ('F14', 'APA do Iguaçu – setores e parâmetros (Quadros I a VII), com alteração do Dec. 1.004/2023 (ato 380795, ST-Bairro Novo do Caximba)', 'Decreto Municipal nº 1.025/2021 e Decreto nº 1.004/2023', '2021-06-22', VH + '332649', 'Dec1025_2021_APA_Iguacu.txt'),
 ('F15', 'APA do Passaúna – zonas e parâmetros (Quadros I a XIII, anexo 30368)', 'Decreto Municipal nº 924/2021', '2021-06-21', VH + '334390', 'Dec924_2021_anexo.pdf'),
 ('F16', 'GeoCuritiba/IPPUC – Mapa Cadastral público (camadas de zoneamento, APAs, OUC-LV, SEPE, SEPP, SETP, sistema viário, Dec. 297/2026, SERC)', 'IPPUC – serviço ArcGIS REST público', HOJE, MC, None),
 ('F17', 'GeoCuritiba/IPPUC – Sistema Municipal de Unidades de Conservação (serviço público)', 'IPPUC/SMMA', HOJE, GEO + 'Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer', None),
 ('F18', 'Legisladoc – consulta pública de atos (situação "Em Vigor" verificada em 27/10/2026)', 'Câmara/Prefeitura de Curitiba – Legisladoc externo', HOJE, LD + 'AtosConsultaExterna.aspx', None),
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

def C(condicao, forma, valor=None, **kw):
    d = dict(condicao=condicao, forma=forma, valor=valor); d.update(kw); return d

def COND(unidade, fonte, art, obs, conds):
    return P(None, unidade, fonte, art, obs, forma='condicional', condicionais=conds)
