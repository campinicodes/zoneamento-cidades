"""Transcrição dos parâmetros oficiais de Curitiba (linha HABITAÇÃO COLETIVA salvo indicação).

Fontes: Lei 15.511/2019 Quadros (F02), Lei 16.361/2024 Quadros II/III (F03), Dec. 297/2026 arts. 5–9 (F04),
Dec. 2.397/2023 (F05), Lei 13.909/2011 Anexo V (F09), Dec. 1.025/2021 (F14), Dec. 924/2021 (F15).
Campos do spec:
  nome, cat, q (quadro), art (artigos da Lei 15.511), col ('sim'|'nao'|texto de restrição)
  ca_b, ca_b_cond [(cond, valor)], alt ('livre'|int|None), alt_cond [(cond, valor|'livre')], alt_m
  to (num | [(cond, num)]), recuo (num | str | [(cond, num|str)]), perm (num | str | [(cond,num|str)])
  afast (('formula', 'H/6', min) | ('unico', m) | ('texto', str)), lote (testada, area)
  oodc: [(cond, ca_b, adq, ca_max, alt_b, alt_adq, alt_max, quadro)] | 'sem' | texto
  his: dict(ca, ca_cond, dens, dens_cond, pav) – Dec. 297/2026
  dens: (forma, valor|texto, unidade) densidade específica; obs: [str]
"""
LIVRE = 'livre'
H6 = ('formula', 'H/6', 2.5)

def L(t, a):
    return (t, a)

# ---------- Lei 16.361/2024 Quadro II (vias normais) e III (vias classificadas) -------------
Q3_ZR3 = [('Via setorial 1/2 (Lei 16.361 Q III)', 1, 0.8, 1.8, 3, 3, 6, 'Quadro III'),
          ('Via coletora 1/2 (Lei 16.361 Q III)', 1, 0.5, 1.5, 3, 1, 4, 'Quadro III')]
def q3(ca_b, adq, mx, ab, aa, am):
    return [('Via setorial 1/2 ou coletora 1/2 (Lei 16.361 Q III)', ca_b, adq, mx, ab, aa, am, 'Quadro III')]

ESP = {}
def Z(codigo, **kw):
    kw.setdefault('fq', 'F02'); kw.setdefault('obs', [])
    ESP[codigo] = kw
    return kw

# ================= EIXOS =================
Z('EE', nome='Eixo Estrutural', cat='eixo', q='Quadros I (via central), II (vias externas) e III (outras vias)', art='arts. 9º a 14',
  col='sim', ca_b=4, ca_b_cond=[('Trechos EE Norte (Funcionários–Mascarenhas de Moraes–João Gbur–Mariano Gardolinski) e EE Sul (Pres. Kennedy–Orlando Padilha–W. Churchill/André Ferreira Barbosa) – nota 4 do Quadro I / nota (2) Lei 16.361 Q II', 3),
                                    ('Demais trechos', 4)],
  alt=LIVRE, to=[('Via central: térreo e 2º pavimento', 1.0), ('Via central: demais pavimentos', 0.5),
                 ('Vias externas: subsolo, térreo e 2º pavimento', 1.0), ('Vias externas: demais pavimentos', 0.5),
                 ('Outras vias: embasamento', 0.75), ('Outras vias: torre', 0.5)],
  recuo=[('Via central', 'Plano Massa (Lei 16.448/2024 arts. 5º a 7º) – sem recuo fixado no Quadro I'), ('Vias externas', 10), ('Outras vias', 5)],
  perm='Conforme regulamentação específica (Quadros I a III, nota) – Dec. 2.397/2023 arts. 34 a 36',
  afast=('texto', 'Via central: H/6 a partir do embasamento, mín. 2,50 m; vias externas: facultado até o 2º pavimento, acima H/6 mín. 2,50 m; outras vias: H/6 mín. 2,50 m.'),
  lote=L(15, 450),
  oodc=[('Demais trechos (nota 1)', 4, 2, 6, LIVRE, None, LIVRE, 'Quadro II'),
        ('Trechos nota (2): EE Norte e EE Sul indicados', 3, 0, 3, LIVRE, None, LIVRE, 'Quadro II')],
  his=dict(ca=6), dens=None,
  obs=['Lei 16.448/2024 art. 11: nas vias externas do EE, torre exclusivamente habitacional recebe +1 vez a área do terreno de potencial não oneroso.',
       'Lei 16.448/2024 art. 8º: torre comercial +1,5 vez a área do terreno; art. 10: comércio no térreo/2º das outras vias não computável (até 1×).',
       'IPU 0,3 para uso habitacional na ZR4 lindeira aos segmentos do EE Boa Vista–Santa Cândida e Capão Raso–Pinheirinho (Lei 16.361 art. 10 §1º) – aplica-se à ZR4, não ao EE.'])
Z('ENC', nome='Eixo Nova Curitiba', cat='eixo', q='Quadros IV e V', art='arts. 15 a 17', col='sim',
  ca_b=2, alt=LIVRE, to=[('Subsolo', 0.6), ('Demais pavimentos', 0.5)], recuo=[('Via central', 5), ('Vias externas', 10)], perm=0.25,
  afast=('formula', 'H/5', 2.5), lote=L(15, 450),
  oodc=[(None, 2, 1, 3, LIVRE, None, LIVRE, 'Quadro II')], his=dict(ca=3),
  obs=['Art. 15 §2º da Lei 15.511: acréscimo de 1 no CA para densidade ≥ 200 hab/ha (até 300 hab/ha); nota 7 Lei 16.361 Q II: pode adquirir 1 de CA se não atingir 200 hab/ha.'])
Z('EAC', nome='Eixo Presidente Affonso Camargo', cat='eixo', q='Quadros VII (via central) e VIII (outras vias)', art='art. 19', col='sim',
  ca_b=1.5, alt=4, to=[('Via central: embasamento', 0.75), ('Via central: torre', 0.5), ('Outras vias', 0.5)], recuo=5,
  perm=[('Outras vias', 0.25), ('Via central', 'Conforme regulamentação (Quadro VII)')], afast=H6, lote=L(15, 450),
  oodc=[(None, 1.5, 1, 2.5, 4, 6, 10, 'Quadro II')], his=dict(ca=2.5, dens=625))
Z('EMF', nome='Eixo Marechal Floriano', cat='eixo', q='Quadro VI', art='art. 18', col='sim',
  ca_b=1, alt=4, to=[('Embasamento', 0.75), ('Torre', 0.5)], recuo=5, perm='Conforme regulamentação (Quadro VI)', afast=H6, lote=L(15, 450),
  oodc=[(None, 1, 1.5, 2.5, 4, 6, 10, 'Quadro II')], his=dict(ca=2.5, dens=625),
  obs=['IPU 0,3 (Lei 16.361 art. 10 §2º) no EMF entre o Polo-Linha Verde e o limite sul da ZS-2.', 'Lei 16.448 arts. 18–19: fachada ativa +1 pavimento não oneroso.'])
Z('EACF', nome='Eixo de Adensamento Comendador Franco', cat='eixo', q='Quadro X', art='arts. 23 a 25', col='sim',
  ca_b=1, alt=4, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450),
  oodc=[(None, 1, 1.5, 2.5, 4, 6, 10, 'Quadro II')], his=dict(ca=2.5, dens=625), obs=['IPU 0,3 (Lei 16.361 art. 10 §2º).'])
Z('EACB', nome='Eixo de Adensamento Eng. Costa Barros', cat='eixo', q='Quadro XI', art='arts. 23 e 26', col='sim',
  ca_b=1, alt=4, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450),
  oodc=[(None, 1, 1, 2, 4, 4, 8, 'Quadro II')], his=dict(ca=2, dens=500), obs=['IPU 0,3 (Lei 16.361 art. 10 §2º).'])
for k in ['ECO-1', 'ECO-2', 'ECO-3', 'ECO-4']:
    x = (1.5, 1, 2.5, 4, 6, 10) if k == 'ECO-3' else (1.5, 1, 2.5, 4, 4, 8)
    y = (1.5, 1, 2.5, 6, 4, 10) if k == 'ECO-3' else (1.5, 1, 2.5, 6, 2, 8)
    Z(k, nome=f'Eixo Conector Oeste {k[-1]}', cat='eixo', q='Quadro XII', art='arts. 27 a 33', col='sim',
      ca_b=1.5, alt=4, alt_cond=[('Lote lindeiro à ZR4', 6), ('Demais', 4)], to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450),
      oodc=[('Demais lotes',) + x + ('Quadro II',), ('Lote lindeiro à ZR4',) + y + ('Quadro II',)], his=dict(ca=2.5, dens=625))
Z('ECL-3', nome='Eixo Conector Leste 3', cat='eixo', q='Quadro XIII', art='arts. 27 a 33', col='sim',
  ca_b=1.5, alt=4, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450),
  oodc=[(None, 1.5, 1, 2.5, 4, 6, 10, 'Quadro II')], his=dict(ca=2.5, dens=625), obs=['IPU 0,3 (Lei 16.361 art. 10 §2º).',
  'ECL-1/2 e ECS-2 só vigoram após implantação do sistema de transporte (art. 29) – não aparecem na base cartográfica.'])
Z('ECS-1', nome='Eixo Conector Sul 1', cat='eixo', q='Quadro XIV', art='arts. 27 a 33', col='sim',
  ca_b=1, alt=4, to=0.5, recuo=3, perm=0.25, afast=('unico', 2), lote=L(12, 360),
  oodc=[(None, 1, 0.5, 1.5, 4, 2, 6, 'Quadro II')], his=dict(ca=1.5, dens=375))

# ================= ZONA CENTRAL / SEPE =================
Z('ZC', nome='Zona Central', cat='centralidade', q='Quadro XV', art='arts. 35 e 36', col='sim',
  ca_b=5, alt=LIVRE, to=[('Embasamento', 1.0), ('Torre', 0.66)], recuo='Alinhamento predial obrigatório (Quadro XV)',
  perm='Atendida no subsolo / mecanismo de contenção de cheias (Quadro XV, nota)', afast=('unico', 2), lote=L(11, 330),
  oodc=[(None, 5, 2, 7, LIVRE, None, LIVRE, 'Quadro II')], his=dict(ca=7, dens=LIVRE),
  obs=['IPU 0,3 para uso habitacional na ZC (Lei 16.361 art. 10 §1º).', 'Lei 16.448 arts. 21–23: galeria não computável (×2 se torre habitacional); estacionamento acima do solo não computável.',
       'Dec. 209/2024 arts. 5º–7º: logradouros onde não se admitem novos estacionamentos (habitacional facultado nos do art. 6º).',
       'Parte da ZC integra o SERC (LC 150/2025; Dec. 418/2026) – ver camada serc_setores.'])
Z('ZC-SEPE-C', nome='Zona Central – Setor Especial Preferencial de Pedestres (Setor Central)', cat='centralidade', q='Quadro XLII (nota 3)', art='arts. 96 a 99', col='sim',
  ca_b=5, ca_b_obs='Nota (3) do Quadro XLII/art. 99: o coeficiente é o da zona atravessada (ZC = 5).', alt=5,
  alt_obs='5 pavimentos até a profundidade de 15 m a partir do alinhamento; além dela, altura da zona atravessada (ZC: livre).',
  to=[('Embasamento', 1.0), ('Torre', 0.66)], recuo='Alinhamento predial (Quadro XLII)', perm='Conforme regulamentação (Quadro XLII, nota 3)',
  afast=('texto', 'Conforme Quadro XLII.'), lote=L(11, 330), oodc='Lei 16.361 Q II não lista o SEPE; CA da zona atravessada (ZC). Aquisição até o máximo da ZC (7) não confirmada no texto – confirmar com a SMU.',
  his=dict(ca=7, dens=LIVRE), obs=['Dec. 209/2024 art. 5º I: não se admitem novos estacionamentos no Setor Preferencial de Pedestres Central/XV.'])
Z('ZC-SEPE-XV', nome='Zona Central – SEPE Rua XV de Novembro', cat='patrimonio_cultural', q='Quadro XLII', art='art. 101', col='sim',
  ca_b=3.6, ca_b_obs='Art. 101: o coeficiente não poderá ser superior a 3,6.', alt=5, to=[('Embasamento', 1.0), ('Torre', 0.66)],
  recuo='Alinhamento predial (Quadro XLII)', perm='Conforme regulamentação', afast=('texto', 'Conforme Quadro XLII.'), lote=L(11, 330),
  oodc='CA limitado a 3,6 pelo art. 101 da Lei 15.511.', ca_max_fixo=3.6, his=None,
  obs=['Análise do CAPC/patrimônio.', 'Dec. 209/2024 art. 5º I: sem novos estacionamentos.'])
Z('ZC-SEPE-BR', nome='Zona Central – SEPE Barão-Riachuelo', cat='patrimonio_cultural', q='Quadro XLIII', art='arts. 105 a 107', col='sim',
  ca_b=3.6, ca_b_cond=[('Lotes com testada para a Rua Riachuelo, uso habitacional (nota 4)', 5), ('Cruzamento Riachuelo × XV de Novembro (nota 4)', 3.6), ('Demais', 3.6)],
  alt=None, alt_obs='Embasamento de 3 pavimentos (até 13 m, nota 5; limitado à altura de imóvel histórico no lote/confrontante) + bloco vertical (altura conforme Quadro XLIII).',
  to=[('Embasamento', 1.0), ('Torre', 0.66)], recuo=[('Embasamento', 'Alinhamento predial obrigatório'), ('Bloco vertical', 15)],
  perm='Conforme regulamentação (nota 3)', afast=('texto', 'Embasamento: facultado (nota 6 – testada até 15 m); bloco vertical conforme Quadro XLIII.'), lote=L(11, 330),
  oodc='SEPE não consta da Lei 16.361 Q II.', his=dict(ca=7, dens=LIVRE),
  obs=['Dec. 209/2024 art. 6º I: estacionamentos só vinculados a uso habitacional.', 'Art. 107 par. único: dentro de ZH prevalecem os quadros da ZH.'])
Z('ZSM-SEPE-C', nome='Zona Setor Misto – SEPE Setor Central', cat='mista_media_densidade', q='Quadro XXIX + Quadro XLII (nota 3)', art='arts. 64 e 99', col='sim',
  base_de='ZSM', alt=5, alt_obs='5 pavimentos até 15 m de profundidade; além, altura da ZSM (art. 99).')

# ================= ZCC =================
Z('ZCC', nome='Zona de Centro Cívico', cat='centralidade', q='Quadros XXXVI (Av. Cândido de Abreu) e XXXVII (demais)', art='arts. 78 a 83', col='sim',
  ca_b=2, ca_b_cond=[('Lotes com testada para a Av. Cândido de Abreu (Quadro XXXVI)', 4), ('Demais (Quadro XXXVII)', 2)],
  alt=6, alt_cond=[('Av. Cândido de Abreu', LIVRE), ('Demais', 6)], to=0.5, recuo=[('Av. Cândido de Abreu', 10), ('Demais', 5)], perm=0.25,
  afast=('texto', 'Cândido de Abreu: 2,50 m até 4 pavimentos, acima H/6 mín. 3,00 m; demais: H/6 mín. 2,50 m.'), lote=L(20, 600),
  oodc=[('ZCC-Incentivo – Av. Cândido de Abreu', 4, 1, 5, LIVRE, None, LIVRE, 'Quadro II'), ('ZCC-Incentivo – demais (perímetro Anexo I-e)', 2, 0.5, 2.5, 6, 4, 10, 'Quadro II')],
  his=dict(ca=2.5, ca_cond=[('Av. Cândido de Abreu', 5), ('Demais', 2.5)], dens=625, dens_cond=[('Cândido de Abreu (ZCC-incentivo)', LIVRE), ('Demais', 625)]),
  obs=['Nota 4 Lei 16.361 Q II: restrições junto à ciclovia na ZCC.', 'Dec. 1.730/2020: incentivos dos arts. 35 e 78 da Lei 15.511.'])

# ================= ZONAS RESIDENCIAIS =================
Z('ZR1', nome='Zona Residencial 1', cat='residencial_baixa_densidade', q='Quadro XVI', art='arts. 37 e 38', col='nao',
  ca_b=1, alt=2, to=0.5, recuo=5, perm=0.25, afast=('texto', 'Conforme Quadro XVI.'), lote=L(15, 600), oodc='sem',
  dens=('texto', 'Habitação unifamiliar: 1 habitação para cada 300 m² de terreno (Quadro XVI).', None), his=None,
  obs=['Somente habitação unifamiliar – sem habitação coletiva.'])
Z('ZR2', nome='Zona Residencial 2', cat='residencial_baixa_densidade', q='Quadro XVII', art='art. 39', col='nao',
  ca_b=1, alt=2, to=0.5, recuo=5, perm=0.25, afast=('texto', 'Facultado (Quadro XVII).'), lote=L(12, 360),
  oodc=q3(1, 0.5, 1.5, 2, 2, 4), dens=('texto', 'Habitações unifamiliares em série: 1 UH/120 m² de terreno (Quadro XVII).', None),
  his=dict(ca=1, ca_cond=[('Demais vias', 1), ('Vias classificadas (setoriais/coletoras)', 1.5)], dens=200, dens_cond=[('Demais vias', 200), ('Vias classificadas', 220)], pav=4),
  obs=['Habitação coletiva não admitida no Quadro XVII; nas vias setoriais/coletoras valem os Quadros XLIV–XLVII e a Lei 16.361 Q III.',
       'Dec. 297/2026 admite conjuntos HIS COHAB com CA 1 (1,5 em vias classificadas), até 4 pavimentos.'])
Z('ZR2 - A', nome='Zona Residencial 2 – Setor Especial de Pontos Panorâmicos', cat='residencial_baixa_densidade', base_de='ZR2', sepp=True)
Z('ZR3', nome='Zona Residencial 3', cat='residencial_baixa_densidade', q='Quadro XVIII', art='art. 40', col='sim',
  ca_b=1, alt=3, alt_m=10, to=0.5, recuo=5, perm=0.25, afast=('texto', 'Facultado até 3 pavimentos (10 m); acima H/6 mín. 2,50 m.'), lote=L(12, 360),
  oodc=[('Vias normais', 1, 0.5, 1.5, 3, 1, 4, 'Quadro II')] + Q3_ZR3,
  his=dict(ca=1.5, ca_cond=[('Demais vias', 1.5), ('Vias setoriais', 1.8), ('Vias coletoras', 1.5)], dens=375, dens_cond=[('Demais vias', 375), ('Vias classificadas', 500)]),
  obs=['Conjuntos habitacionais apenas em lotes < 20.000 m² (art. 169).'])
Z('ZR3 - A', nome='Zona Residencial 3 – Setor Especial de Pontos Panorâmicos', cat='residencial_baixa_densidade', base_de='ZR3', sepp=True)
Z('ZR3-T', nome='Zona Residencial 3 Transição', cat='residencial_media_densidade', q='Quadro XIX', art='arts. 41 e 42', col='sim',
  ca_b=1, alt=4, alt_cond=[('Testada para via externa do EE/ENC até 100 m', 6), ('Demais', 4)], to=0.5, recuo=5, perm=0.25,
  afast=('texto', 'Facultado até 2 pavimentos; acima H/6 mín. 2,50 m.'), lote=L(15, 450),
  oodc=[('Demais lotes', 1, 1, 2, 4, 2, 6, 'Quadro II'), ('Testada para via externa EE/ENC até 100 m', 1, 1, 2, 6, 2, 8, 'Quadro II')],
  his=dict(ca=2, dens=500))
for k, n in [('ZR3-T - MERÇÊS', 'Mercês'), ('ZR3-T - ALTO DA GLÓRIA', 'Alto da Glória')]:
    Z(k, nome=f'Zona Residencial 3 Transição – {n}', cat='residencial_media_densidade', base_de='ZR3-T',
      oodc=[(f'ZR3-T {n} (perímetro Anexo I da Lei 16.361)', 1, 1.5, 2.5, 4, 4, 8, 'Quadro II')], his=dict(ca=2.5, dens=625))
Z('ZR4', nome='Zona Residencial 4', cat='residencial_media_densidade', q='Quadro XX', art='arts. 43 e 44', col='sim',
  ca_b=2, alt=6, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450),
  oodc=[(None, 2, 0.5, 2.5, 6, 2, 8, 'Quadro II')], his=dict(ca=2.5, dens=625),
  obs=['IPU 0,3 para uso habitacional na ZR4 lindeira aos EE Boa Vista–Santa Cândida e Capão Raso–Pinheirinho (Lei 16.361 art. 10 §1º).'])
for k, n in [('ZR4 - BATEL', 'Batel'), ('ZR4 - ALTO DA XV', 'Alto da XV')]:
    Z(k, nome=f'Zona Residencial 4 – {n}', cat='residencial_media_densidade', base_de='ZR4',
      oodc=[(f'ZR4 {n} (perímetro Anexo I da Lei 16.361)', 2, 0.5, 2.5, 6, 4, 10, 'Quadro II')])
Z('ZROC-1', nome='Zona Residencial de Ocupação Controlada 1', cat='residencial_baixa_densidade', q='Quadros XXII e XXIII', art='arts. 45 a 49', col='Habitação coletiva só nos lotes com testada para a Via Metropolitana (Quadro XXIII); demais: não admitida (Quadro XXII).',
  ca_b=0.4, alt=2, to=[('Demais lotes (Quadro XXII)', 0.3), ('Via Metropolitana (Quadro XXIII)', 0.5)], recuo=5,
  perm=[('Demais lotes (Quadro XXII)', 0.5), ('Via Metropolitana (Quadro XXIII)', 0.25)], afast=('texto', 'Conforme Quadros XXII/XXIII.'),
  lote=L(20, 2000), lote_obs='Quadro XXII: 20 × 2.000 m²; Via Metropolitana (Quadro XXIII): 15 × 450 m².',
  oodc=q3(0.4, 0.6, 1, 2, 2, 4), his=dict(ca=None), dens=('texto', 'Habitação unifamiliar: 1 habitação/2.000 m² de terreno (≈ 5 hab/ha, Quadro XXII).', None))
Z('ZROC-1 CAMPO DE SANTANA', nome='ZROC-1 Campo de Santana (art. 48)', cat='expansao', q='Quadro XXI', art='art. 48', col='Admitida nos imóveis objeto de parcelamento (art. 48), Quadro XXI; demais imóveis seguem o Quadro XXII.',
  ca_b=1, alt=4, to=0.5, recuo=5, perm=0.25, afast=('unico', 2.5), lote=L(15, 450),
  oodc='Lei 16.361: não consta no Quadro II para esta subárea.', his=dict(ca=1, his_obs='CMU, com Plano de Desenvolvimento Regional obrigatório (Dec. 297 art. 4º §2º).'),
  obs=['Novos loteamentos: doação de 10% para equipamentos, 10% para lazer e 15% para HIS (art. 48).'])
Z('ZROI', nome='Zona Residencial de Ocupação Integrada', cat='residencial_baixa_densidade', q='Quadro XXIV', art='arts. 50 a 52', col='sim',
  ca_b=1, alt=2, to=0.5, recuo=5, perm=0.25, afast=('texto', 'Conforme Quadro XXIV.'), lote=L(15, 450),
  oodc=q3(1, 0.5, 1.5, 2, 2, 4), his=dict(ca=1, ca_cond=[('Demais vias', 1), ('Vias classificadas', 1.5)], dens=200, dens_cond=[('Demais vias', 200), ('Vias classificadas', 220)], pav=4),
  obs=['Novos loteamentos na ZROI: destinação mínima de 40% da área ao Município para sistema viário e equipamentos (art. 51).'])

# ================= ZONAS DE USO MISTO =================
Z('ZUM-1', nome='Zona de Uso Misto 1', cat='mista_baixa_densidade', q='Quadro XXV', art='arts. 53 a 58', col='sim',
  ca_b=1, alt=4, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450),
  oodc=[(None, 1, 0.5, 1.5, 4, 2, 6, 'Quadro II')] + [('Via setorial/coletora (Q III)', 1, 0.5, 1.5, 4, 2, 6, 'Quadro III')], his=dict(ca=1.5, dens=375))
Z('ZUM-2', nome='Zona de Uso Misto 2', cat='mista_media_densidade', q='Quadro XXVI', art='arts. 53 a 58', col='sim',
  ca_b=2, alt=6, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450), oodc='sem', his=dict(ca=2, dens=500))
Z('ZUM-3', nome='Zona de Uso Misto 3', cat='mista_media_densidade', q='Quadro XXVII', art='arts. 53 a 58', col='sim',
  ca_b=2, alt=4, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(12, 360),
  oodc=[('Habitação coletiva / transitória 1', 2, 0.5, 2.5, 4, 2, 6, 'Quadro II')], his=dict(ca=2.5, dens=625))
Z('ZUMVP', nome='Zona de Uso Misto Vila Parolin', cat='mista_media_densidade', q='Quadro XXVIII', art='arts. 59 a 63', col='sim',
  ca_b=1, ca_b_obs='CA 1 por uso, cumulativo até 3 (Quadro XXVIII).', ca_max_fixo=3, ca_max_obs='Coeficiente cumulativo por uso até 3 (Quadro XXVIII); não consta OODC na Lei 16.361 Q II.',
  alt=4, alt_cond=[('CA até 1', 4), ('CA 2', 8), ('CA 3', 12)], to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(12, 360), oodc='quadro',
  his=dict(ca=3, dens=None, dens_cond=[('Vias classificadas', 750), ('Demais vias', 'art. 212 (100 × CA hab./ha)')]),
  obs=['Lei 16.448 arts. 18–19: fachada ativa +1 pavimento não oneroso.'])
Z('ZSM', nome='Zona Setor Misto', cat='mista_media_densidade', q='Quadro XXIX', art='art. 64', col='sim',
  ca_b=2, alt=6, to=[('Subsolo, térreo e 2º pavimento', 1.0), ('Demais pavimentos', 0.5)], recuo=[('Até o 2º pavimento', 'Facultado'), ('Acima do 2º pavimento', 5)],
  perm='Conforme regulamentação (Quadro XXIX)', afast=('texto', 'H/6 a partir do embasamento, mín. 2,50 m.'), lote=L(15, 450),
  oodc=[(None, 2, 1, 3, 6, 4, 10, 'Quadro II')], his=dict(ca=3, dens=625, dens_cond=[('Demais vias', 625), ('Vias classificadas', 750)]))
Z('ZFR', nome='Zona de Fundo de Rio (Belém)', cat='mista_media_densidade', q='Quadro XXX', art='arts. 65 e 66', col='sim',
  ca_b=2, alt=6, to=0.5, recuo=5, perm=0.25, afast=H6, lote=L(15, 450), oodc='sem', his=dict(ca=2, dens=500),
  obs=['Rua Treze de Maio: uso misto com estacionamento – CA 3 e 6 pavimentos (Quadro XXX, nota).'])

# ================= ZONAS ESPECIAIS =================
for k, n in [('ZE', 'Zona Especial Educacional'), ('ZM', 'Zona Militar')]:
    Z(k, nome=n, cat='institucional', q='Quadro XXXI' if k == 'ZE' else 'Quadro XXXII', art='arts. 67 e 68' if k == 'ZE' else 'arts. 67 e 69', col='sim',
      ca_b=0.5, alt=4, to=0.3, recuo=10, perm=0.25, afast=('unico', 5), lote=L(20, 600),
      oodc=[(None, 0.5, 0.5, 1, 4, 0, 4, 'Quadro II')], his=None)
Z('ZPS', nome='Zona Polo de Software', cat='especial_economica', q='Quadro XXXIII', art='art. 70', col='nao', ca_b=None, alt=None, oodc='sem', his=None,
  obs=['Habitação coletiva não admitida (Quadro XXXIII); parâmetros de outros usos não transcritos.'])
Z('ZH-1', nome='Zona Histórica 1', cat='patrimonio_cultural', q='Quadro XXXIV', art='arts. 71 a 77', col='sim',
  ca_b=2.6, ca_b_obs='Art. 73; parágrafo único: a Câmara Técnica do Patrimônio Cultural Edificado pode admitir CA até 4 para imóveis tombados, com transferência total do potencial construtivo.', alt=3, to=[('Térreo', 1.0), ('Demais pavimentos', 0.8)],
  recuo='Alinhamento predial obrigatório', perm='Conforme regulamentação', afast=('texto', 'Conforme Quadro XXXIV.'), lote=L(11, 330),
  oodc='sem', his=dict(ca=2.6, dens=500), obs=['Projetos analisados pela CAPC (Comissão de Avaliação do Patrimônio Cultural).'])
Z('ZH-1-SEPE-C', nome='Zona Histórica 1 – SEPE Setor Central', cat='patrimonio_cultural', base_de='ZH-1', extra_obs=['Art. 107 par. único: na ZH prevalecem os quadros da ZH; SEPE impõe restrições a estacionamento (Dec. 209/2024).'])
Z('ZH-1-SEPE-BR', nome='Zona Histórica 1 – SEPE Barão-Riachuelo', cat='patrimonio_cultural', base_de='ZH-1', extra_obs=['Art. 107 par. único: na ZH prevalecem os quadros da ZH.'])
Z('ZH-2', nome='Zona Histórica 2', cat='patrimonio_cultural', q='Quadro XXXV', art='arts. 71 a 77', col='sim',
  ca_b=2, alt=4, to=0.5, recuo=5, perm=0.25, afast=('texto', 'Facultado (Quadro XXXV).'), lote=L(15, 450), oodc='sem', his=dict(ca=2, dens=500))
for k, n in [('ZCSF', 'Zona de Contenção São Francisco'), ('ZCUM', 'Zona de Contenção de Uso Misto')]:
    Z(k, nome=n, cat='residencial_baixa_densidade', q='Quadro XXXVIII', art='arts. 84 e 85', col='sim',
      ca_b=1, alt=2, to=0.5, recuo=5, perm=0.25, afast=('texto', 'Conforme Quadro XXXVIII.'), lote=L(15, 450), oodc='sem', his=dict(ca=1, pav=2))
for k, n, q in [('ZS-1', 'Zona de Serviço 1', 'Quadro XXXIX'), ('ZS-2', 'Zona de Serviço 2', 'Quadro XL'), ('ZI', 'Zona Industrial', 'Quadro XLI')]:
    Z(k, nome=n, cat='industrial' if k == 'ZI' else 'especial_economica', q=q, art='arts. 86 a 91', col='nao', ca_b=None, alt=None,
      oodc=([('BR-277 – apenas habitação transitória 1', 1, 1, 2, 2, 4, 6, 'Quadro II')] if k == 'ZS-1' else 'sem'), his=None,
      obs=['Habitação coletiva não admitida; parâmetros dos demais usos não transcritos (não relevantes para MCMV).'])
Z('SEHIS', nome='Setor Especial de Habitação de Interesse Social', cat='especial_interesse_social', q='Quadro XLIX', art='art. 158', col='Habitação coletiva só em lotes ≥ 360 m² com via de caixa ≥ 12 m (Quadro XLIX).',
  ca_b=1, alt=3, to=0.5, recuo=3, perm=0.25, afast=('unico', 2), lote=L(6, 180),
  oodc=q3(1, 0.5, 1.5, 3, 1, 4), his=dict(ca=1, ca_cond=[('Demais vias', 1), ('Vias classificadas', 1.5)], dens=200, dens_cond=[('Demais vias', 200), ('Vias classificadas', 220)], pav=4),
  obs=['Lei 16.448 arts. 18–19: fachada ativa +1 pavimento em SEHIS nas vias classificadas.'])
for k in ['SEDE-ECS-1', 'SEDE-ZR4', 'SEDE-CFC']:
    Z(k, nome='Setor Especial Desportivo' + (' – Centro de Formação/Coritiba (Alto da XV)' if k == 'SEDE-CFC' else f' (sobre {k[5:]})'), cat='institucional',
      q='art. 122', art='arts. 121 a 124', fq='F01', col='Não definido para habitação coletiva no art. 122 (Plano Diretor de Ocupação Específico – arts. 123 e 124).',
      ca_b=1, alt=4, to=0.5, recuo='Admitido o recuo existente (art. 122)', perm=0.25, afast=('texto', 'Conforme Plano Diretor de Ocupação Específico (art. 123).'), lote=None, oodc='sem', his=None)
Z('UC', nome='Unidade de Conservação / Parque (zoneamento)', cat='ambiental', q='Mapa de zoneamento e legislação das UCs', art='art. 34 (mapa de zoneamento)', fq='F01', col='nao',
  ca_b=None, alt=None, oodc='sem', his=None, obs=['Ocupação regida pelo plano de manejo/ato de criação de cada UC (camadas uc_*).'])
Z('SEPPFC', nome='Setor Especial de Preservação da Paisagem Ferroviária', cat='patrimonio_cultural', q='Dec. 1.033/2001', art='arts. 92 a 95 (setores especiais)', fq='F01', col=None,
  ca_b=None, alt=None, oodc='sem', his=None, sem_tudo=True, obs=['Parâmetros do Dec. 1.033/2001 não obtidos – ver lacunas.'])

# ================= OUC LINHA VERDE (Lei 13.909/2011, Anexo V; Lei 15.511 Quadro IX) =================
def LV(cod, nome, cat, ca_b, alt, ca_ad, alt_ad, to, recuo, lote, dens=None, col='sim', afast=None, extra=None):
    Z(cod, nome=nome, cat=cat, q='Quadro IX (Lei 15.511, transcrito das Leis 13.909/2011 e 14.773/2015) / Anexo V (Lei 13.909)', art='arts. 20 a 22 (Lei 15.511); arts. 7º, 8º e 14 (Lei 13.909)', col=col,
      ca_b=ca_b, alt=alt, to=to, recuo=recuo, perm_sem='Quadro IX não fixa taxa de permeabilidade; Lei 13.909 art. 10: contenção de cheias obrigatória em todo novo empreendimento na OUC-LV.',
      afast=afast or ('texto', 'Até 2 pavimentos: facultado; acima de 2 pavimentos: H/6, mínimo 2,50 m (Quadro IX).'), lote=lote, lv=(ca_ad, alt_ad), dens=dens,
      oodc='lv', his=None, obs=['Na OUC-LV o potencial adicional é adquirido por CEPAC (Lei 13.909 art. 13 §2º; Tabela II do art. 14); Dec. 297/2026 art. 4º §3º: na OUC-LV os incentivos de HIS seguem regulamentação própria (art. 9º IV da Lei 13.909).',
                               'Lei 13.909 art. 7º §7º–§9º: densidade adicional por CEPAC (15 CEPACs por UH excedente) e +1 pavimento por 0,5 de CA adquirido; art. 8º: com aquisição ≥ 80% da ACA, estacionamento sobre o solo não computável, TO do subsolo 75%, +10% da área do lote (lotes ≥ 2.000 m², até 1.000 m²); art. 10: contenção de cheias obrigatória.'] + (extra or []))
EMB = ('texto', 'Embasamento ou até o 2º pavimento: facultado; acima de 2 pavimentos: H/6, mínimo 2,50 m (Quadro IX).')
LV('POLO-LV', 'Polo Linha Verde', 'eixo', 1, LIVRE, 4, LIVRE, [('Embasamento (nota 4: até 10 m)', 0.76), ('Torre', 0.5)], 5, L(20, 1000),
   dens=('cond', [('Parâmetros básicos', 100), ('Com potencial adicional (CEPAC)', LIVRE)], 'uh/ha'), afast=EMB)
LV('SE-LV', 'Setor Especial Linha Verde', 'eixo', 1, 6, 4, LIVRE, 0.5, 5, L(20, 1000), dens=('cond', [('Parâmetros básicos', 100), ('Com potencial adicional (CEPAC)', LIVRE)], 'uh/ha'),
   extra=['Lei 13.909 art. 8º V: no SE-LV, ocupação exclusivamente residencial ou mista recebe incentivo de 50% da área do lote (condicionado à aquisição de ≥ 80% da ACA).'])
LV('ZT-LV', 'Zona de Transição Linha Verde', 'mista_media_densidade', 1, 4, 2.5, 8, 0.5, 5, L(15, 450), dens=('cond', [('Parâmetros básicos', 100), ('Com potencial adicional (CEPAC)', 250)], 'uh/ha'))
LV('ZR-4-LV', 'Zona Residencial 4 Linha Verde', 'residencial_media_densidade', 2, 6, 2.5, 8, 0.5, 5, L(15, 450), dens=('cond', [('Parâmetros básicos', 200), ('Com potencial adicional (CEPAC)', 250)], 'uh/ha'))
LV('ZE-D-LV', 'Zona Especial Desportiva Linha Verde (ZED)', 'institucional', 0.5, 4, 1, 8, 0.3, 10, L(20, 1000), col='nao', afast=EMB,
   extra=['Habitação coletiva não listada no Quadro IX para a ZED; nota (6): altura livre na R. Dino Bertoldi e perímetro Victor Ferreira do Amaral/Farid Surugi/Suécia/Victório Vizinoni/Armando Prince.'])
LV('ZS-2-LV', 'Zona de Serviço 2 Linha Verde', 'especial_economica', 1, 2, None, None, 0.5, 10, L(15, 450), col='nao', afast=('texto', 'Conforme Quadro IX.'),
   extra=['Habitação coletiva não listada no Quadro IX para a ZS-2.'])
Z('ZI-LV', nome='Zona Industrial Linha Verde', cat='industrial', q='Lei 13.909 Anexo V', art='—', fq='F09', col=None, ca_b=None, alt=None, oodc='sem', his=None, sem_tudo=True,
  obs=['Parâmetros não transcritos com segurança – ver lacunas.'])

# ================= APA DO IGUAÇU (Dec. 1.025/2021; Dec. 1.004/2023) =================
def AI(cod, nome, cat, quadro, col, ca, pav, to, recuo, perm, afast, lote, dens=None, obs=None):
    Z('APA-IGUAÇU ' + cod, nome=f'APA do Iguaçu – {nome}', cat=cat, q=quadro, art='Dec. 1.025/2021 art. 6º e ' + quadro, fq='F14', col=col,
      ca_b=ca, alt=pav, to=to, recuo=recuo, perm=perm, afast=afast, lote=lote, oodc='sem', his=None, dens=dens, obs=obs or [])
AI('SARU', 'Setor de Alta Restrição de Uso', 'ambiental', 'Quadro I', 'nao', 0.2, 2, 0.1, 15, 0.8, ('unico', 5), L(20, 5000), ('unico', 2, 'hab/ha'), ['Habitação: unifamiliar; atividades sujeitas a RAP.'])
AI('SMRU', 'Setor de Média Restrição de Uso', 'ambiental', 'Quadro II', 'nao', 0.4, 2, 0.2, 15, 0.5, ('unico', 5), L(20, 5000), ('unico', 2, 'hab/ha'), ['4 hab/ha em lotes ≥ 10.000 m² oriundos de loteamento.'])
AI('ST', 'Setor de Transição', 'residencial_baixa_densidade', 'Quadro III', 'nao', 1, 2, 0.5, 5, 0.25, ('texto', 'Conforme Quadro III.'), L(12, 360), None,
   ['Até 3 habitações unifamiliares por lote; série 1 UH/120 m²; sem habitação coletiva. Regularização fundiária (REURB) pela COHAB.'])
AI('STR', 'Setor de Transição Restrito', 'residencial_baixa_densidade', 'Quadro IV', 'nao', 1, 2, 0.5, 5, 0.25, ('texto', 'Conforme Quadro IV.'), L(12, 360), None, ['Até 3 habitações unifamiliares por lote.'])
AI('ST-BNC', 'Setor de Transição – Bairro Novo do Caximba', 'especial_interesse_social', 'Quadro V (red. Dec. 752/2023 e Dec. 1.004/2023)',
   'Habitação coletiva só como EIS da COHAB-CT, ≤ 100 hab/ha, em lotes municipais/COHAB com testada para a R. Delegado Bruno de Almeida até 150 m de profundidade, lote ≥ 360 m² e via ≥ 12 m.',
   1, 4, 0.5, 3, 0.25, ('unico', 2), L(6, 180), ('unico', 100, 'hab/ha'),
   ['Unifamiliar (até 4 por lote) / série: CA 1,2, 2 pavimentos, TO 60%, recuo 3 m, lote 6 × 180 m² (Quadro V).'])
AI('SUE', 'Setor de Uso Especial', 'ambiental', 'Quadro VI', 'nao', 0.2, 2, 0.1, 15, 0.8, ('unico', 5), L(20, 5000), None, ['1 habitação unifamiliar por lote.'])
AI('SS', 'Setor de Serviço', 'especial_economica', 'Quadro VII', 'nao', 0.4, 4, 0.2, 15, 0.5, ('unico', 5), L(20, 2000), None, ['1 habitação unifamiliar por lote.'])
Z('APA-IGUAÇU SUC', nome='APA do Iguaçu – Setor de Unidades de Conservação', cat='ambiental', q='art. 6º VIII', art='Dec. 1.025/2021 art. 6º VIII', fq='F14', col='nao', ca_b=None, alt=None, oodc='sem', his=None,
   obs=['Regido pelos atos das UCs.'])

# ================= APA DO PASSAÚNA (Dec. 924/2021, Anexo) =================
def AP(cod, nome, cat, quadro, col, ca, pav, to, recuo, perm, afast, lote, dens=None, obs=None, sem=False):
    Z('APA-PASSAÚNA ' + cod, nome=f'APA do Passaúna – {nome}', cat=cat, q=quadro, art='Dec. 924/2021 art. 3º e Anexo ' + quadro, fq='F15', col=col,
      ca_b=ca, alt=pav, to=to, recuo=recuo, perm=perm, afast=afast, lote=lote, oodc='sem', his=None, dens=dens, obs=obs or [], sem_tudo=sem)
AP('ZUC II', 'Zona de Urbanização Consolidada II', 'residencial_baixa_densidade', 'Quadro I', 'nao', 1, 2, 0.5, 5, 0.25, ('texto', 'Facultado (2,50 m para permissíveis).'), L(15, 600),
   ('texto', '1 habitação unifamiliar/600 m²; densidade bruta 10 hab/ha (Quadro I).', None))
AP('ZOO', 'Zona de Ocupação Orientada', 'ambiental', 'Quadro II', 'nao', 0.4, 2, 0.2, 10, 0.6, ('unico', 2.5), L(20, 5000), ('unico', 2, 'hab/ha'), ['Série: 4 hab/ha.'])
AP('ZEI', 'Zona Especial de Indústria', 'industrial', 'Quadro III', 'nao', 1, None, 0.5, None, 0.25, ('texto', 'Conforme Quadro III.'), L(20, 600), None, ['CA 0,6 para unifamiliar/comércio geral.'])
AP('ZES', 'Zona Especial de Serviços', 'especial_economica', 'Quadro IV', 'nao', 1, 2, 0.5, None, 0.25, ('unico', 2.5), L(20, 600))
AP('ZRA', 'Zona de Recuperação Ambiental', 'ambiental', 'Quadro XII', 'nao', None, None, None, None, None, None, None, None, ['Somente recuperação ambiental/lazer; sem parâmetros numéricos.'], sem=True)
