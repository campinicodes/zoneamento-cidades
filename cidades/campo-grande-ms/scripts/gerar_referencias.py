"""Gera ../REFERENCIAS.md a partir de ../campo-grande-ms.json (fontes, citações, regras, camadas, lacunas).
Uso: python3 gerar_referencias.py"""
import json, os, re
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.dirname(AQUI)
d = json.load(open(os.path.join(PASTA, "campo-grande-ms.json"), encoding="utf-8"))

citas = defaultdict(set)   # fonte_id -> artigos citados
def walk(o, onde):
    if isinstance(o, dict):
        if o.get("type") in ("FeatureCollection", "Feature"):
            return
        if o.get("fonte_id"):
            art = o.get("artigo_anexo")
            citas[o["fonte_id"]].add(f"{onde}: {art}" if art else onde)
        for k, v in o.items():
            if k not in ("features", "geometria"):
                walk(v, onde)
    elif isinstance(o, list):
        for v in o:
            walk(v, onde)
for z in d["zonas"]:
    walk(z, z["codigo"])
for n, c in d["camadas_complementares"].items():
    walk(c, n)
for k in ("outorga_onerosa", "zeis_his", "outros_parametros", "resumo_mcmv"):
    walk(d.get(k), k)

arquivos = sorted(f for f in os.listdir(os.path.join(PASTA, "fontes")) if f.lower().endswith(".pdf"))
def arquivo_local(f):
    """Casa a norma com o PDF local pelo número e ano (ex.: 'LC 516/2023' -> LC516-2023.pdf)."""
    manual = {"F04": "LC341-republicacao-mapas.pdf", "F24": "Guia-isencao-IPTU-2026.pdf"}  # nomes de arquivo sem número/ano
    if f["id"] in manual and manual[f["id"]] in arquivos:
        return manual[f["id"]]
    m = re.search(r"(?:Lei Complementar|Lei|Decreto|Resolução SEMADUR)\s*n?\.?\s*([\d.]+)/(\d{4})", f["lei"])
    if not m:
        return ""
    num, ano = m.group(1).replace(".", ""), m.group(2)
    cand = [a for a in arquivos if re.search(rf"(?<!\d){num}-{ano}", a.replace(".", "", a.count(".") - 1))]
    if "republica" in f["lei"] and "mapas" in f["lei"]:
        cand = [a for a in cand if "mapas" in a] or cand
    elif "republicada" in f["lei"]:
        cand = [a for a in cand if "consolidada" in a] or cand
    elif num == "341":
        cand = [a for a in cand if "original" in a] or cand
    return cand[0] if cand else ""

L = [f"# Referências legais – {d['municipio']}/{d['uf']} (`{d['slug']}`)", "",
     f"Levantamento: {d['data_levantamento']} · IBGE {d['codigo_ibge']} · Gerado por `scripts/gerar_referencias.py` a partir de `{d['slug']}.json`.", "",
     "> Fontes exclusivamente oficiais e públicas (Prefeitura de Campo Grande, DIOGRANDE, SIMGEO/PLANURB). "
     "Valores sem fonte estão como `null` e listados em *Lacunas*. Confirme sempre na "
     f"{d.get('orgao_confirmacao', 'prefeitura')} antes de decisão de compra.", "",
     "## Marco legal vigente", "", d["marco_legal_vigente"] if isinstance(d["marco_legal_vigente"], str) else json.dumps(d["marco_legal_vigente"], ensure_ascii=False), "",
     "## Fontes", "", "| ID | Norma | Data | Título | Arquivo local (fontes/) | Link oficial |", "|---|---|---|---|---|---|"]
for f in d["fontes"]:
    L.append(f"| {f['id']} | {f['lei']} | {f['data']} | {f['titulo']} | {arquivo_local(f) or '—'} | [link]({f['url']}) |")
L += ["", "## Onde cada fonte é citada no JSON", ""]
for f in d["fontes"]:
    c = sorted(citas.get(f["id"], []))
    if c:
        L.append(f"- **{f['id']}** ({f['lei']}): " + "; ".join(c[:25]) + (f" … (+{len(c)-25})" if len(c) > 25 else ""))
L += ["", "## Regras de sobreposição (como a plataforma decide a zona aplicável)", "",
      "| Zona | Tipo | Prioridade | Efeito | Detalhe | Fundamento |", "|---|---|---|---|---|---|"]
for z in sorted(d["zonas"], key=lambda z: -z["prioridade"]):
    r = z.get("regra_sobreposicao") or {}
    det = []
    if r.get("usa_indices_de"): det.append(f"usa índices de {r['usa_indices_de']}")
    if r.get("aplica_sobre"): det.append("sobre " + "/".join(r["aplica_sobre"]))
    if r.get("limiar_pct") is not None: det.append(f"limiar {r['limiar_pct']}%")
    if r.get("requer_testada"): det.append("requer testada")
    if r.get("distancia_max_m") is not None: det.append(f"≤ {r['distancia_max_m']} m")
    L.append(f"| {z['codigo']} – {z['nome']} | {z['tipo']} | {z['prioridade']} | {r.get('efeito') or '—'} | {', '.join(det) or '—'} | {r.get('fundamento') or '—'} |")
L += ["", "## Camadas geográficas", "", f"Servidor oficial: {d['geografico'].get('servidor_oficial')}", "",
      "| Camada | Uso no JSON | Método | Erro est. (m) | Download | URL |", "|---|---|---|---|---|---|"]
for c in d["geografico"]["camadas"]:
    L.append(f"| {c['nome']} | `{c.get('campo') or c.get('arquivo')}` | {c['metodo']} | {c['erro_estimado_m']} | {c['data_download']} | {c['fonte_url']} |")
L += ["", "### Camadas complementares", ""]
for n, c in d["camadas_complementares"].items():
    L.append(f"- **{n}** (papel `{c['papel']}`, {len(c['features'])} feições): {c.get('descricao', '')}")
L += ["", "## Limitações", ""] + [f"- {x}" for x in d["geografico"]["limitacoes"]]
L += ["", "## Lacunas (dados não encontrados em fonte oficial – ficaram `null`)", ""] + [f"- **{x['item']}**: {x.get('motivo', '')}" for x in d["lacunas"]]
L += ["", "## Conteúdo desta pasta", "", f"- `{d['slug']}.json` – dados no padrão da plataforma (schema {d['schema_versao']}).",
      "- `fontes/` – cópias das leis/decretos oficiais (PDF + texto extraído com pdftotext).",
      "- `geo_raw/` – camadas brutas baixadas do SIMGEO (GeoJSON, EPSG:4326).",
      "- `scripts/` – `baixar_camadas.py` (download SIMGEO), `montar_camadas.py`/`adicionar_geografico.py`/`build_cg.py` (montagem do JSON legado), "
      "`migrar_para_padrao.py` (conversão para o padrão 1.0), `gerar_referencias.py` (este arquivo), `consulta_zona_cg.py`/`gerar_mapa.py` (ferramentas da fase anterior)."]
open(os.path.join(PASTA, "REFERENCIAS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("REFERENCIAS.md:", len(L), "linhas")
