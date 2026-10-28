"""Vetoriza mapas do Plano Diretor LC 164/2024 (PDF SAPL, vetorial A0): Anexo I macrozoneamento (p.74),
Anexo II ZEIS (p.76), Anexo VII restrições ambientais (p.88) e Anexo VIII restrições adicionais (p.90).
ATENÇÃO: os Anexos I, II, VII e VIII foram substituídos pela LC 171/2025 (publicados só como imagem);
ver comparar_lc171.py. Saída: geo_raw/pd_<camada>_utm.geojson (EPSG:31985)."""
from vetorizar_pd_lib import *
import os, sys
# Anexo I macrozoneamento: cores pela ordem da legenda (y 362..455)
dr = load(74); f, m = grid(74)
MZ = {(0.804, 0.537, 0.4): 'MAD-1', (1.0, 0.498, 0.498): 'MAD-2', (1.0, 0.659, 0.0): 'MAD-3',
      (0.447, 0.537, 0.267): 'MPA', (1.0, 1.0, 0.576): 'MBD'}
save('macrozonas', painter(fills(dr, MZ)), f, m)
# Anexo II ZEIS
dr = load(76); f, m = grid(76)
save('zeis', {'ZEIS': [g for _, g in fills(dr, {(0.859, 0.29, 0.29): 'ZEIS'})]}, f, m, explode=True)
# Anexo VII restrições ambientais
dr = load(88); f, m = grid(88)
s = fills(dr, {(0.447, 0.537, 0.267): 'UNIDADE_CONSERVACAO', (0.671, 0.804, 0.4): 'PARQUE_MUNICIPAL'})
gr = {c: [g for cc, g in s if cc == c] for c in ('UNIDADE_CONSERVACAO', 'PARQUE_MUNICIPAL')}
gr['MANANCIAL_PRELIMINAR'] = clips(dr, [32988, 61189])
gr['PARQUE_ESTADUAL_TRILHAS'] = clips(dr, [108788])
save('restricoes_ambientais', gr, f, m)
# Anexo VIII: ver vetorizar_pd_p90.py
