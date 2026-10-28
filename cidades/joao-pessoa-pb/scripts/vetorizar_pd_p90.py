"""Anexo VIII (restrições adicionais) do PD LC 164/2024, p.90 — parte separada de vetorizar_pd.py
porque as manchas de suscetibilidade têm até 24 mil anéis (usa path_to_geom_fast)."""
import json, pickle, os, sys, time
import pymupdf as fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vetor_pdf import path_to_geom, path_to_geom_fast
import vetorizar_pd_lib as L
dr = L.load(90); f, m = L.grid(90)
CORES = {(0.902, 0.271, 0.271): 'SUSC_MOV_MASSA_ALTA', (1.0, 0.767, 0.3): 'SUSC_MOV_MASSA_MODERADA',
         (0.0, 0.518, 0.659): 'SUSC_INUNDACAO_ALTA', (0.537, 0.804, 0.4): 'SUSC_INUNDACAO_MODERADA'}
gr = {}
for i in (18, 19, 20, 21):
    t = time.time(); c = CORES[tuple(round(v, 3) for v in dr[i]['fill'])]
    gr[c] = path_to_geom_fast(dr[i]['items']); print(c, round(time.time() - t), 's', flush=True)
it = dr[64890]['items']; gr['ALTIPLANO_CABO_BRANCO'] = path_to_geom(it + [('l', it[-1][-1], it[0][1])], True)
gr['TOMBAMENTO_IPHAEP'] = L.clips(dr, [66830]); gr['TOMBAMENTO_IPHAN'] = L.clips(dr, [64901, 64989, 65028])
gr['CENTRO_HISTORICO'] = L.clips(dr, [68101]); gr['MATA_BURAQUINHO'] = L.clips(dr, [22])
L.save('restricoes_adicionais', gr, f, m)
