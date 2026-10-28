#!/usr/bin/env python3
"""Baixa camadas públicas do ArcGIS REST da SMAMUS/PMPA (sem login) em GeoJSON EPSG:4326.
Uso: python3 baixar_camadas.py [nome ...]   (sem args = todas)
Gentil com o servidor: 1 requisição por vez, pausa e retries."""
import json, sys, time, urllib.request, urllib.parse, os
BASE = "https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/"
OUT = os.path.join(os.path.dirname(__file__), "..", "geo_raw")
CAMADAS = {
  "pddua_regime": "Hosted/PDDUA/FeatureServer/0",
  "luos_zot": "Hosted/luos_anexo01_zot/FeatureServer/0",
  "aeis": "POA___Consultas_MIL1/MapServer/75",
  "zona_rural": "POA___Consultas_MIL1/MapServer/76",
  "macrozona": "POA___Consultas_MIL1/MapServer/77",
  "pbzpa_altura": "POA___Consultas_MIL1/MapServer/37",
  "ruido_pezr": "POA___Consultas_MIL1/MapServer/36",
  "app_topo_morro": "POA___Consultas_MIL1/MapServer/106",
  "app_curso_dagua": "POA___Consultas_MIL1/MapServer/107",
  "unid_conservacao": "POA___Consultas_MIL1/MapServer/114",
  "tombados_inventariados": "POA___Consultas_MIL1/MapServer/141",
  "risco_cprm": "POA___Consultas_MIL1/MapServer/152",
  "susc_mov_massa": "POA___Consultas_MIL1/MapServer/153",
  "susc_inundacao": "POA___Consultas_MIL1/MapServer/154",
  "cota_535_2024": "Hosted/cota_535/FeatureServer/0",
  "limite_4d": "Hosted/Limite_Programa_4D_130326/FeatureServer/0",
  "interesse_cultural": "Hosted/Áreas_de_Interesse_Cultural/FeatureServer/0",
}
def get(url, params, tries=6):
    q = url + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "Mozilla/5.0"}), timeout=120) as r:
                d = json.loads(r.read().decode("utf-8"))
            if "error" in d: raise RuntimeError(d["error"])
            return d
        except Exception as e:
            print("  retry", i + 1, str(e)[:120], flush=True); time.sleep(5 * (i + 1))
    raise RuntimeError("falhou " + q)
def baixar(nome, path):
    path = urllib.parse.quote(path)
    url = BASE + path + "/query"
    meta = get(BASE + path, {"f": "json"})
    mx = min(meta.get("maxRecordCount", 1000) or 1000, 1000)
    ids = get(url, {"where": "1=1", "returnIdsOnly": "true", "f": "json"})
    oids = sorted(ids.get("objectIds") or []); oidf = ids.get("objectIdFieldName", "OBJECTID")
    feats = []
    for i in range(0, len(oids), mx):
        chunk = oids[i:i + mx]
        d = get(url, {"where": f"{oidf}>={chunk[0]} AND {oidf}<={chunk[-1]}", "outFields": "*",
                      "outSR": 4326, "f": "geojson", "returnGeometry": "true"})
        feats += d.get("features", []); time.sleep(1)
    fc = {"type": "FeatureCollection", "fonte": BASE + path, "data_download": time.strftime("%Y-%m-%d"),
          "nome_camada": meta.get("name"), "features": feats}
    json.dump(fc, open(os.path.join(OUT, nome + ".geojson"), "w"))
    print(nome, len(oids), "ids ->", len(feats), "feições", flush=True)
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or CAMADAS):
        try: baixar(n, CAMADAS[n])
        except Exception as e: print("ERRO", n, e)
        time.sleep(2)
