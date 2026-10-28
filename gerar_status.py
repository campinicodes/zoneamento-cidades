"""Gera a tabela de status das cidades (markdown) a partir dos JSONs – mesma função usada pela página inicial."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))
from motor import status_cidade  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cidades")


def tabela():
    lin = ["| Cidade | Zonas (base) | Geometria oficial (% área base) | Erro estimado | Levantamento | Lacunas | Fontes | JSON (MB) |",
           "|---|---|---|---|---|---|---|---|"]
    for s in sorted(os.listdir(RAIZ)):
        arq = os.path.join(RAIZ, s, f"{s}.json")
        if not os.path.isfile(arq):
            continue
        d = json.load(open(arq, encoding="utf-8")); st = status_cidade(d)
        e = st["erro_estimado_m"]
        err = "– (vetor oficial)" if not e else (f'{e["min"]:g} m' if e["min"] == e["max"] else f'{e["min"]:g}–{e["max"]:g} m')
        lin.append(f'| {d["municipio"]}/{d["uf"]} (`{s}`) | {st["n_zonas"]} ({st["n_zonas_base"]}) | {st["pct_area_base_oficial"]}% '
                   f'| {err} | {st["data_levantamento"]} | {st["n_lacunas"]} | {st["n_fontes"]} | {os.path.getsize(arq)/1e6:.1f} |')
    return "\n".join(lin)


if __name__ == "__main__":
    print(tabela())
