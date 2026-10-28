"""Tabelas do PDDUA (LC 434/99, compilação 16/12/2025) transcritas dos Anexos oficiais
(PDFs em ../fontes). Cada linha cita o anexo. Nada aqui é inferido; códigos ausentes => None."""

# Anexo 4 – Densidades brutas (hab/ha ; economias/ha): privado, solo criado, total
DENSIDADE = {
 '1': dict(hab_priv=140, econ_priv=40, hab_sc=None, econ_sc=None, hab_tot=140, econ_tot=40, area='intensiva'),
 '3': dict(hab_priv=140, econ_priv=40, hab_sc=None, econ_sc=None, hab_tot=140, econ_tot=40, area='intensiva'),
 '5': dict(hab_priv=280, econ_priv=80, hab_sc=70, econ_sc=20, hab_tot=350, econ_tot=100, area='intensiva'),
 '7': dict(hab_priv=280, econ_priv=80, hab_sc=70, econ_sc=20, hab_tot=350, econ_tot=100, area='intensiva'),
 '9': dict(hab_priv=280, econ_priv=80, hab_sc=105, econ_sc=30, hab_tot=385, econ_tot=110, area='intensiva'),
 '11': dict(hab_priv=315, econ_priv=90, hab_sc=70, econ_sc=20, hab_tot=385, econ_tot=110, area='intensiva'),
 '13': dict(hab_priv=315, econ_priv=90, hab_sc=105, econ_sc=30, hab_tot=420, econ_tot=120, area='intensiva'),
 '15': dict(hab_priv=385, econ_priv=110, hab_sc=70, econ_sc=20, hab_tot=455, econ_tot=130, area='intensiva'),
 '17': dict(hab_priv=385, econ_priv=110, hab_sc=105, econ_sc=30, hab_tot=490, econ_tot=140, area='intensiva'),
 '19': dict(hab_priv=525, econ_priv=150, hab_sc=None, econ_sc=None, hab_tot=525, econ_tot=150, area='intensiva'),
 '21': dict(hab_priv=350, econ_priv=100, hab_sc=105, econ_sc=30, hab_tot=455, econ_tot=130, area='intensiva'),
 '23': dict(conforme_projeto=True, area='intensiva'),
 '25': dict(conforme_projeto=True, area='intensiva'),
 '31': dict(hab_tot=2, econ_tot=0.5, area='rarefeita'),
 '33': dict(hab_tot=7, econ_tot=2, area='rarefeita'),
 '35': dict(hab_tot=17, econ_tot=5, area='rarefeita'),
 '37': dict(hab_tot=10, econ_tot=3, area='rarefeita'),
 '39': dict(conforme_projeto=True, area=None),
 '41': dict(conforme_projeto=True, area=None),
}

# Anexo 5.1 – Grupamentos de atividades (zonas de uso) + regra de HABITAÇÃO (Anexo 5.3/5.5, Dec. 20.628/2020)
# multifamiliar: 'permitido' | 'proibido' | 'projeto_especial' | None
GA = {
 '1': ('Área Predominantemente Residencial, Centro Histórico', 'permitido'),
 '3': ('Mista 01', 'permitido'),
 '5': ('Mista 02, Centro Histórico', 'permitido'),
 '7': ('Mista 03, Centro Histórico', 'permitido'),
 '9': ('Mista 04', 'permitido'),
 '11': ('Mista 05', 'projeto_especial'),
 '13': ('Área Predominantemente Produtiva', 'proibido'),
 '15.1': ('Área de interesse cultural – Área Predominantemente Residencial', 'permitido'),
 '15.3': ('Área de interesse cultural – Mista 01', 'permitido'),
 '15.5': ('Área de interesse cultural – Mista 02', 'permitido'),
 '15.7': ('Área de interesse cultural – Mista 03', 'permitido'),
 '15.9': ('Área de interesse cultural – Parque urbano', None),
 '16.1': ('Área de ambiência cultural – Área Predominantemente Residencial', 'permitido'),
 '16.3': ('Área de ambiência cultural – Mista 01', 'permitido'),
 '16.5': ('Área de ambiência cultural – Mista 02', 'permitido'),
 '16.7': ('Área de ambiência cultural – Mista 03', 'permitido'),
 '16.9': ('Área de ambiência cultural – Mista 04', 'permitido'),
 '17': ('Área de interesse institucional', None),
 '19.1': ('Proteção do ambiente natural', 'projeto_especial'),
 '19.2': ('Parque natural', 'proibido'),
 '19.3': ('Reserva biológica', 'proibido'),
 '21': ('Área de desenvolvimento diversificado', 'projeto_especial'),
 '23': ('Área de produção primária (Zona Rural – LC 775/2015)', 'proibido'),
 '25': ('Corredor agroindustrial', 'projeto_especial'),
 '27': ('Área com potencial de ocupação intensiva', 'projeto_especial'),
}

# Anexo 6 – Índices de aproveitamento: (IA básico, IA máximo c/ Solo Criado/TPC, quota ideal m²)
IA = {
 '1': (1.0, 1.5, 75), '2A': (1.0, 1.5, 300), '2B': (1.0, 1.5, 150),
 '3': (1.3, 2.0, 75), '4': (1.3, 2.0, 150), '4A': (1.3, 2.0, 300), '5': (1.3, 2.0, 75), '6': (1.3, 2.0, 150),
 '7': (1.3, 3.0, 75), '9': (1.3, 3.0, 75), '11': (1.6, 3.0, 75), '13': (1.6, 3.0, 75),
 '15': (1.9, 3.0, 75), '17': (1.9, 3.0, 75), '19': (2.4, 3.0, 75), '21': (0.65, 2.0, None),
 '31': (0.1, None, 20000), '33': (0.1, None, 5000), '35': (0.2, None, 2000), '37': (0.5, None, None),
}
IA_REGIME_PROPRIO = {'23': 'Regime urbanístico próprio a critério do SMGP (2) – IA não pode ser maior que 2,5 salvo exceção do art. 85', '25': 'Regime urbanístico próprio (2) – IA não pode ser maior que 2,5 salvo exceção do art. 85',
                     '39': 'regime próprio (Anexo 6)', '41': 'definido em lei específica (Anexo 6)'}

# Anexo 7.1 – Regime volumétrico: (altura máx, altura divisa, altura base, TO corpo, TO base 90% em vias do Anexo 7.2)
VOL = {
 '1': (9.0, '9,00', None, 0.666, False), '2': (9.0, '9,00', '4,00', 0.75, False),
 '3': (12.5, '12,50', None, 0.75, False), '3A': (12.5, '9,00', None, 0.75, False),
 '4': (12.5, '12,50', '9,00', 0.75, True), '5': (18.0, '12,50', '4,00', 0.75, True),
 '6': (18.0, '9,00', '4,00', 0.75, False), '7': (18.0, '18,00', None, 0.75, False),
 '8': (18.0, '18,00', '4,00 e 9,00', 0.75, True), '9': (42.0, '12,50 e 18,00', '4,00 e 9,00', 0.75, True),
 '11': (52.0, '12,50 e 18,00', '4,00 e 9,00', 0.75, True), '13': (52.0, '18,00', '6,00 e 9,00', 0.75, True),
 '15': (33.0, '12,50 e 18,00', '4,00 e 9,00', 0.75, True), '17': (27.0, '12,50 e 18,00', '4,00 e 9,00', 0.75, True),
 '19': (None, None, '9,00', 0.75, True), '21': (9.0, '9,00', None, 0.20, False), '23': (9.0, '9,00', None, 0.50, False),
}

# Art. 96 §7º – Área livre/permeável mínima em função da TO (terrenos < 1.500 m²)
PERM_POR_TO = {0.9: 0.07, 0.75: 0.17, 0.666: 0.23, 0.5: 0.35, 0.2: 0.56}

# Anexo 8.1 – Padrões para loteamento: (área mínima m², testada m)
def lote_padrao(ga):
    if ga in ('1', '3', '5', '7', '9', '16.1', '16.3', '16.5', '16.7', '16.9'):
        return (150, 5, 'Área predominantemente residencial e Mistas 1-4')
    if ga in ('11', '13'):
        return (600, 15, 'Área predominantemente produtiva e Mista 5')
    if ga.startswith('15'):
        return (None, None, 'Áreas especiais de interesse cultural – definido a critério do SMGP (nota 7)')
    if ga in ('19.1', '19.2', '19.3'):
        return (200000, 50, 'Área de proteção do ambiente natural (AOR) – 20 ha (nota 1)')
    if ga == '21':
        return (20000, None, 'Área de desenvolvimento diversificado (AOR) – 2 ha')
    if ga == '23':
        return (20000, None, 'Área de produção primária (AOR) – 2 ha')
    return (None, None, None)
