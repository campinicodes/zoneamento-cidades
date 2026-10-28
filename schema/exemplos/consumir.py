"""Exemplo mínimo de consumo de um <slug>.json SEM a app (só json + jsonschema; shapely opcional)."""
import json, sys
from jsonschema import Draft202012Validator

import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
schema = json.load(open(f"{BASE}/schema/cidade.schema.json", encoding="utf-8"))
cidade = json.load(open(f"{BASE}/cidades/campo-grande-ms/campo-grande-ms.json", encoding="utf-8"))

erros = list(Draft202012Validator(schema).iter_errors(cidade))
if erros:
    sys.exit(f"JSON fora do schema: {erros[0].message}")


def ler(p):
    """Parâmetro normalizado → número, lista ou descrição curta. A 'forma' diz como ler."""
    if p is None:
        return None                                   # não levantado
    f = p["forma"]
    if f in ("unico", "lista"):
        return p["valor"]
    if f == "faixa":
        return (p["faixa"]["min"], p["faixa"]["max"])
    if f == "condicional":
        return {c["condicao"]: ler({**c, "faixa": c.get("faixa")}) for c in p["condicionais"]}
    if f == "formula":
        return p["formula"]
    return f                                          # livre | herda_da_base | nao_aplicavel | sem_dado | texto


fontes = {f["id"]: f for f in cidade["fontes"]}
for z in cidade["zonas"]:
    P = z["parametros"]
    ca = P["ca_maximo"]
    cit = f'{fontes[ca["fonte_id"]]["lei"]}, {ca["artigo_anexo"]}' if ca and ca["fonte_id"] else "-"
    print(f'{z["codigo"]:9} {z["categoria_normalizada"]:28} CAmáx={ler(ca)!s:14} TO={ler(P["taxa_ocupacao"])!s:45.45} | {cit[:60]}')

# Em qual zona base cai um ponto? (opcional: shapely)
try:
    from shapely.geometry import Point, shape
    pt = Point(-54.6201, -20.4697)                    # lon, lat (EPSG:4326)
    for z in cidade["zonas"]:
        if z["tipo"] == "base" and any(shape(f["geometry"]).contains(pt) for f in z["geometria"]["features"]):
            print("ponto está na zona base", z["codigo"])
except ImportError:
    pass
