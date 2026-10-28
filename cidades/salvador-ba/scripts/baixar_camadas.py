#!/usr/bin/env python3
"""Baixa camadas vetoriais OFICIAIS e PÚBLICAS (sem login) do GeoSalvador (ArcGIS REST da PMS)
em GeoJSON EPSG:4326, com paginação. Saída: geo_raw/<tema>.geojson + geo_raw/_log_download.json"""
import json, os, time, urllib.request, urllib.parse, datetime
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'geo_raw')
R = 'https://geo.salvador.ba.gov.br/arcgis/rest/services/'
ML = R + 'Hosted/Mapa_LOUOS_WFL1/FeatureServer/'
PD = R + 'PDDU_2016/MapServer/'
CAMADAS = {
 'zeis': ML + '29', 'macrozona_conservacao_ambiental': ML + '2', 'macrozona_ocupacao_urbana': ML + '3',
 'macroarea_estruturacao_urbana': ML + '6', 'macroarea_urbanizacao_consolidada': ML + '7',
 'macroarea_requalificacao_borda_atlantica': ML + '8', 'macroarea_reestruturacao_borda_baia': ML + '9',
 'macroarea_integracao_metropolitana': ML + '16', 'limite_borda_maritima': ML + '73',
 'parque_bairro': ML + '74', 'apcp': ML + '75', 'ucm': ML + '76', 'parque_urbano': ML + '77',
 'parque_urbano_proposto': ML + '78', 'aprn': ML + '79', 'uc_indicadas': ML + '80', 'apa_estadual': ML + '81',
 'mata_atlantica': ML + '84', 'ouc': ML + '86', 'limite_municipal': ML + '91',
 'centralidades_metropolitanas': ML + '18', 'centralidades_municipais': ML + '25', 'zus_ilhas': ML + '26',
 'espacos_abertos_urbanizados': PD + '70',
 'bens_tombados': R + 'Hosted/bens_tombados_a/FeatureServer/0',
 'risco_idesh': R + 'Hosted/idesh_risco_a/FeatureServer/0',
 'bairros_oficiais': ML + '92',
}

def get(url, params):
    u = url + '/query?' + urllib.parse.urlencode(params)
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120) as r:
                return json.load(r)
        except Exception as e:
            err = e; time.sleep(3 * (k + 1))
    raise err

def baixar(tema, url):
    feats, off = [], 0
    while True:
        d = get(url, {'where': '1=1', 'outFields': '*', 'outSR': 4326, 'f': 'geojson',
                      'resultOffset': off, 'resultRecordCount': 1000, 'returnGeometry': 'true'})
        if 'error' in d: raise RuntimeError(f'{tema}: {d["error"]}')
        fs = d.get('features', []); feats += fs
        if len(fs) < 1000 and not d.get('exceededTransferLimit') and not (d.get('properties') or {}).get('exceededTransferLimit'): break
        if not fs: break
        off += len(fs)
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(OUT, tema + '.geojson'), 'w'))
    return len(feats)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    log = []
    for t, u in CAMADAS.items():
        try:
            n = baixar(t, u); st = 'ok'
        except Exception as e:
            n, st = 0, f'erro: {e}'
        log.append({'tema': t, 'arquivo': f'geo_raw/{t}.geojson', 'url': u, 'n_feicoes': n, 'status': st,
                    'baixado_em': datetime.date.today().isoformat()}); print(t, n, st)
    json.dump(log, open(os.path.join(OUT, '_log_download.json'), 'w'), ensure_ascii=False, indent=1)
