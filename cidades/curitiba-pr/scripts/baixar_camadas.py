#!/usr/bin/env python3
"""Baixa camadas públicas (sem login) do GeoCuritiba/IPPUC em GeoJSON WGS84.
Serviço: https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba/ (MapServer público, consulta /query padrão ArcGIS REST).
Idempotente: pula arquivos já baixados (use --force para rebaixar)."""
import json, os, sys, time, urllib.request, urllib.parse
BASE = 'https://geocuritiba.ippuc.org.br/server/rest/services/GeoCuritiba'
MC = BASE + '/Publico_GeoCuritiba_MapaCadastral/MapServer'
UC = BASE + '/Publico_Sistema_Municipal_de_Unidades_de_Conservacao/MapServer'
CAMADAS = {
    'zoneamento_l15511': (MC, 36), 'zoneamento_cadastral': (MC, 35),
    'apa_iguacu': (MC, 27), 'apa_passauna': (MC, 28), 'ouc_linha_verde': (MC, 29),
    'sepe': (MC, 30), 'pontos_panoramicos': (MC, 31), 'parque_tangua': (MC, 32), 'vila_oficios': (MC, 33),
    'sistema_viario': (MC, 34), 'dec297_areas': (MC, 41), 'dec297_densidade_ampliada': (MC, 42),
    'serc_setores': (MC, 43), 'serc_eixos': (MC, 45), 'serc_perimetro': (MC, 46),
    'setp_largo_ordem': (MC, 50), 'setp_largo_ordem_areas': (MC, 51),
    'uc_estacao_ecologica': (UC, 1), 'uc_parque_natural': (UC, 2), 'uc_parque_linear': (UC, 3),
    'uc_bosque_municipal': (UC, 4), 'uc_bosque_conservacao': (UC, 5), 'uc_refugio': (UC, 6),
    'uc_rppnm': (UC, 7), 'uc_especificas': (UC, 8), 'uc_apa': (UC, 10), 'uc_arie': (UC, 11),
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'geo_raw')

def get(url, params):
    u = url + '?' + urllib.parse.urlencode(params)
    for t in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=180) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            print('  retry', t, e); time.sleep(3 * (t + 1))
    raise RuntimeError(u)

def baixar(nome, svc, lid, force=False):
    dest = os.path.join(OUT, nome + '.geojson')
    if os.path.exists(dest) and not force:
        print('ok (cache)', nome); return
    url = f'{svc}/{lid}/query'
    ids = get(url, {'where': '1=1', 'returnIdsOnly': 'true', 'f': 'json'})
    oids = sorted(ids.get('objectIds') or [])
    feats = []
    for i in range(0, len(oids), 200):
        lote = oids[i:i + 200]
        d = get(url, {'objectIds': ','.join(map(str, lote)), 'outFields': '*', 'outSR': 4326, 'f': 'geojson', 'returnGeometry': 'true'})
        feats += d.get('features', [])
    gj = {'type': 'FeatureCollection', 'features': feats,
          'metadata': {'fonte': f'{svc}/{lid}', 'baixado_em': time.strftime('%Y-%m-%d %H:%M %z'), 'n': len(feats)}}
    json.dump(gj, open(dest, 'w'), ensure_ascii=False)
    print(nome, len(oids), 'ids ->', len(feats), 'features')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    force = '--force' in sys.argv
    sel = [a for a in sys.argv[1:] if not a.startswith('--')] or list(CAMADAS)
    for n in sel:
        baixar(n, *CAMADAS[n], force=force)
