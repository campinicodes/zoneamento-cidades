"""Baixa camadas públicas do Fortaleza em Mapas (IPPLAN) – botão 'Download GeoJSON' (api/download/geojson/<id>)."""
import json, os, subprocess, datetime
OUT = os.path.join(os.path.dirname(__file__), "..", "geo_raw")
CAMADAS = {
 604: "macrozoneamento-urbano-de-fortaleza", 623: "zonas-especiais-de-interesse-social",
 28: "zedus", 29: "ouc-operacao-urbana-consorciada", 609: "oodc-outorga-onerosa",
 79: "zeph", 80: "zepo-projeto-orla", 25: "zei-institucionais", 24: "aea-areas-especiais-aeroportuarias",
 76: "zia", 77: "zpa", 78: "zra", 37: "zonas-especiais-pddufor", 682: "zpa-aerodromo-feijo",
 683: "zpa-aerodromo-pinto-martins", 685: "zpa-aerodromo-dias-branco", 535: "bens-tombados-municipais",
 536: "bens-tombados-poligonais-entorno", 588: "bens-tombados-estaduais", 589: "bens-tombados-federais",
 124: "assentamentos-areas-de-risco", 88: "linha-de-preamar", 111: "mangues", 619: "cepacs",
 740: "funcionamento-comercial-zedus-zo", 21: "bairros", 12: "limite-municipal", 737: "unidades-de-conservacao",
 109: "zona-amortecimento-parque-coco", 85: "parque-estadual-coco", 804: "classificacao-de-logradouro",
 102: "zeis-prioritarias", 669: "alagados", 657: "rios", 93: "lagoas",
}
log = []
for i, nome in CAMADAS.items():
    f = os.path.join(OUT, f"{i}_{nome}.geojson")
    url = f"https://mapas.fortaleza.ce.gov.br/api/download/geojson/{i}"
    r = subprocess.run(["curl", "-s", "-m", "300", "-o", f, "-w", "%{http_code}", url], capture_output=True, text=True)
    n = None
    try: n = len(json.load(open(f))["features"])
    except Exception as e: n = f"ERRO {e}"
    log.append({"id": i, "nome": nome, "url": url, "http": r.stdout, "n_feicoes": n, "baixado_em": datetime.datetime.now().isoformat(timespec="seconds")})
    print(i, nome, r.stdout, n, flush=True)
json.dump(log, open(os.path.join(OUT, "_log_download.json"), "w"), ensure_ascii=False, indent=1)
