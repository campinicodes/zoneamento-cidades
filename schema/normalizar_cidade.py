"""Normalizador GENÉRICO e conservador: converte um <slug>.json no formato legado (schema_versao 1.0, valores soltos)
para o formato do schema (schema_versao 1.1). Não inventa dado: só muda a FORMA (texto → número quando o texto é só
número, "30%" → 0.3 em taxas, dict → condicionais, etc.) e guarda o texto original em texto_original.
O que não for convertível com segurança vira forma "texto" (valor null) e aparece como aviso no validador.
categoria_normalizada NÃO é deduzida (é decisão do analista): passe --categorias Z1=mista_alta_densidade,...
Idempotente: rodar de novo sobre um arquivo já normalizado não muda nada.

Uso: python3 normalizar_cidade.py <entrada.json> [--saida out.json] [--categorias COD=cat,COD=cat] [--compacto]"""
import argparse, json, re, sys

PADRAO = ("ca_minimo", "ca_basico", "ca_maximo", "taxa_ocupacao", "gabarito_altura_max_m", "gabarito_pavimentos",
          "taxa_permeabilidade", "recuos", "lote_minimo_m2", "testada_minima_m", "usos_permitidos", "vagas", "densidade", "outros")
UNIDADE = {"ca_minimo": "coeficiente", "ca_basico": "coeficiente", "ca_maximo": "coeficiente",
           "taxa_ocupacao": "fracao", "taxa_permeabilidade": "fracao", "gabarito_altura_max_m": "m",
           "gabarito_pavimentos": "pavimentos", "frontal": "m", "lateral": "m", "fundos": "m",
           "lote_minimo_m2": "m2", "testada_minima_m": "m", "usos_permitidos": "codigos_de_uso"}
CHAVES_PARAM = ("valor", "unidade", "fonte_id", "artigo_anexo", "observacao", "forma", "faixa", "condicionais", "formula", "texto_original")
RE_COD = re.compile(r"^[A-Z0-9][A-Z0-9_.\-]*$")
NUM = r"-?\d+(?:[.,]\d+)?"


def num(s):
    return float(s.replace(",", ".")) if ("," in s or "." in s) else int(s)


def tipo_de(chave):
    u = UNIDADE.get(chave)
    return "fracao" if u == "fracao" else "lista" if chave == "usos_permitidos" else "num" if u else "livre"


def _anexa(obs, txt):
    return txt if not obs else (obs if txt in obs else f"{obs} | {txt}")


def converter_texto(s, tipo):
    """Texto legal → (forma, valor, faixa, observacao). Só padrões inequívocos; o resto vira 'texto'."""
    t = s.strip()
    low = t.lower()
    if low in ("livre", "isento", "isenta"):
        return "livre", None, None, None
    if low in ("-", "—", "n/a", "na", "não se aplica", "nao se aplica", "não aplicável"):
        return "nao_aplicavel", None, None, None
    if re.match(r"^(conforme|igual|da zona|o da zona|a da zona|mesmos?|mesmas?)\b", low):
        return "herda_da_base", None, None, t
    m = re.fullmatch(rf"({NUM})\s*(%)?", t)
    if m:
        v = num(m.group(1))
        if m.group(2) or (tipo == "fracao" and v > 1):
            if tipo != "fracao":
                return "texto", None, None, None
            v = round(v / 100, 6)
        return "unico", v, None, None
    m = re.fullmatch(rf"({NUM})\s*(m²|m2|m)", t)
    if m and tipo == "num":
        return "unico", num(m.group(1)), None, None
    m = re.fullmatch(rf"({NUM})\s*(%)?\s*(?:a|até|-|–)\s*({NUM})\s*(%)?", t)
    if m and tipo in ("num", "fracao"):
        a, b = num(m.group(1)), num(m.group(3))
        if tipo == "fracao" and (m.group(2) or m.group(4) or a > 1 or b > 1):
            a, b = round(a / 100, 6), round(b / 100, 6)
        return "faixa", None, {"min": a, "max": b}, None
    m = re.fullmatch(rf"({NUM})\s*(%|m²|m2|m)?\s*[\(–\-;:]\s*(.+)", t)
    if m and tipo in ("num", "fracao"):
        v = num(m.group(1))
        if tipo == "fracao" and (m.group(2) == "%" or v > 1):
            v = round(v / 100, 6)
        return "unico", v, None, m.group(3).strip(" )")
    return "texto", None, None, None


def _humano(k):
    return str(k).replace("_", " ")


def condicional(cond, v, tipo):
    c = {"condicao": _humano(cond), "forma": "sem_dado", "valor": None}
    if RE_COD.match(str(cond)):
        c["codigo"] = str(cond)
    if v is None:
        return c
    if isinstance(v, bool):
        v = str(v)
    if isinstance(v, (int, float)):
        if tipo == "fracao" and v > 1:
            c["observacao"] = f"convertido de {v}%"
            v = round(v / 100, 6)
        c.update(forma="unico", valor=v)
    elif isinstance(v, list) and all(isinstance(x, str) for x in v):
        c.update(forma="lista", valor=v)
    elif isinstance(v, str):
        forma, val, faixa, obs = converter_texto(v, tipo)
        c.update(forma=forma, valor=val)
        if faixa:
            c["faixa"] = faixa
        c["texto_original"] = v
        if obs:
            c["observacao"] = obs
    else:
        c.update(forma="texto", texto_original=json.dumps(v, ensure_ascii=False))
    return c


def normalizar_param(p, chave):
    """Qualquer coisa → PARAM {valor, unidade, fonte_id, artigo_anexo, observacao, forma, ...} (ou None)."""
    if p is None:
        return None
    if not isinstance(p, dict) or "valor" not in p and not ({"fonte_id", "forma"} & set(p)):
        p = {"valor": p}
    tipo = tipo_de(chave)
    out = {k: p.get(k) for k in ("valor", "unidade", "fonte_id", "artigo_anexo", "observacao")}
    for k in ("faixa", "condicionais", "formula", "texto_original"):
        if p.get(k) is not None:
            out[k] = p[k]
    extras = {k: v for k, v in p.items() if k not in CHAVES_PARAM and k not in ("variaveis", "chave", "titulo")}
    for k, v in extras.items():
        out["observacao"] = _anexa(out["observacao"], f"{_humano(k)}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}")
    if isinstance(p.get("variaveis"), dict):
        out["observacao"] = _anexa(out["observacao"], "variáveis: " + "; ".join(f"{a} = {b}" for a, b in p["variaveis"].items()))
    unid_orig = (p.get("unidade") or "").strip().lower()
    if chave in UNIDADE:
        out["unidade"] = UNIDADE[chave]
    elif chave == "densidade":
        out["unidade"] = {"hab/ha": "hab/ha", "uh/ha": "uh/ha"}.get(unid_orig.replace(" ", ""), "hab/ha" if out["valor"] is not None or unid_orig else None)
    if p.get("forma"):                      # já normalizado: só completa chaves
        out["forma"] = p["forma"]
        return out
    v = out["valor"]
    if v is None:
        out["forma"] = "sem_dado" if not out.get("faixa") and not out.get("condicionais") else ("faixa" if out.get("faixa") else "condicional")
    elif isinstance(v, bool):
        out.update(valor=None, forma="texto", texto_original=str(v))
    elif isinstance(v, (int, float)):
        if tipo == "fracao" and (unid_orig in ("%", "percentual", "porcentagem") or v > 1):
            out["texto_original"] = f"{v}%"
            v = round(v / 100, 6)
        if chave == "gabarito_pavimentos" and float(v).is_integer():
            v = int(v)
        out.update(valor=v, forma="unico")
    elif isinstance(v, str):
        forma, val, faixa, obs = converter_texto(v, tipo)
        out.update(valor=val, forma=forma, texto_original=v)
        if faixa:
            out["faixa"] = faixa
        if forma == "herda_da_base" and obs:
            out["observacao"] = _anexa(out["observacao"], obs)
        elif obs:
            out["observacao"] = _anexa(out["observacao"], obs)
        if chave == "formula" or (forma == "texto" and re.search(r"[A-Za-z]\w*\s*=\s*", v) and len(v) < 160 and chave.startswith("formula")):
            out.update(forma="formula", formula=v)
    elif isinstance(v, list):
        if all(isinstance(x, str) for x in v):
            out.update(forma="lista")
        else:
            out.update(valor=None, forma="texto", texto_original=json.dumps(v, ensure_ascii=False))
    elif isinstance(v, dict):
        conds = [condicional(k, x, tipo) for k, x in v.items()]
        out["valor"] = None
        if tipo == "lista":
            todos = []
            for c in conds:
                if c["forma"] == "lista":
                    todos += [x for x in c["valor"] if x not in todos]
            out.update(valor=todos, forma="lista")
        else:
            out["forma"] = "condicional" if any(c["forma"] != "sem_dado" for c in conds) else "sem_dado"
        out["condicionais"] = conds
    if out["forma"] in ("unico", "lista") and out.get("texto_original") is None:
        out.pop("texto_original", None)
    return out


def normalizar_parametros(par):
    par = dict(par or {})
    novo = {}
    for k in PADRAO:
        v = par.pop(k, None)
        if k == "recuos":
            v = v if isinstance(v, dict) and not ({"valor"} & set(v)) else ({"frontal": v, "lateral": None, "fundos": None} if v else {})
            novo[k] = {lado: normalizar_param(v.get(lado), lado) for lado in ("frontal", "lateral", "fundos")}
        elif k == "outros":
            novo[k] = {re.sub(r"[^a-z0-9_]", "_", kk.lower()): normalizar_param(vv, kk) for kk, vv in (v or {}).items()}
        else:
            novo[k] = normalizar_param(v, k)
    for k, v in par.items():                # chave fora do padrão → vai para outros (nunca se perde)
        novo["outros"][re.sub(r"[^a-z0-9_]", "_", k.lower())] = normalizar_param(v, k)
    novo["outros"] = {k: v for k, v in novo["outros"].items() if v is not None}
    return novo


def normalizar_bloco(b):
    if isinstance(b, dict) and set(b) >= {"itens"} and isinstance(b["itens"], list):
        b.setdefault("resumo", None); b.setdefault("fonte_id", None); b.setdefault("artigo_anexo", None)
        b["itens"] = [dict(normalizar_param(i, i.get("chave", "")), chave=i["chave"], titulo=i.get("titulo") or _humano(i["chave"])) for i in b["itens"]]
        return b
    out = {"resumo": None, "fonte_id": None, "artigo_anexo": None, "itens": []}
    if isinstance(b, str):
        out["resumo"] = b
        return out
    for k, v in (b or {}).items():
        if k in ("base_legal", "fundamento") and isinstance(v, dict) and "valor" not in v:
            out["fonte_id"], out["artigo_anexo"] = v.get("fonte_id"), v.get("artigo_anexo")
            continue
        if k in ("resumo", "descricao") and isinstance(v, str):
            out["resumo"] = v
            continue
        chave = re.sub(r"[^a-z0-9_]", "_", k.lower()).strip("_") or "item"
        if not re.match(r"^[a-z]", chave):
            chave = "item_" + chave
        item = normalizar_param(v, chave)
        if item is None:
            item = normalizar_param({"valor": None}, chave)
        out["itens"].append({"chave": chave, "titulo": _humano(k), **item})
    return out


def normalizar_macrozonas(mzs):
    out = []
    for m in mzs or []:
        if isinstance(m, str):
            out.append({"codigo": None, "nome": None, "descricao": m, "parametros": {}})
            continue
        if set(m) <= {"codigo", "nome", "descricao", "parametros"} and isinstance(m.get("parametros"), dict):
            out.append({"codigo": m.get("codigo"), "nome": m.get("nome"), "descricao": m.get("descricao"),
                        "parametros": {k: normalizar_param(v, k) for k, v in m["parametros"].items()}})
            continue
        cit = {"fonte_id": m.get("fonte_id"), "artigo_anexo": m.get("artigo_anexo")}
        params = {}
        for k, v in m.items():
            if k in ("codigo", "nome", "descricao", "fonte_id", "artigo_anexo", "diretriz"):
                continue
            params[re.sub(r"[^a-z0-9_]", "_", k.lower())] = normalizar_param(v if isinstance(v, dict) else {"valor": v, **cit}, k)
        out.append({"codigo": m.get("codigo"), "nome": m.get("nome"),
                    "descricao": m.get("descricao") or m.get("diretriz"), "parametros": params})
    return out


GEO_OK = {"descricao", "crs", "crs_area", "servidor_oficial", "camadas", "regras_de_consulta", "limitacoes",
          "raio_divisa_m", "pct_minimo_significativo", "camadas_detalhe", "regras_de_consulta_texto", "notas_tecnicas"}


def normalizar_geografico(g):
    g = dict(g or {})
    notas = dict(g.get("notas_tecnicas") or {})
    for k in list(g):
        if k not in GEO_OK:
            notas[k] = g.pop(k)
    so = g.get("servidor_oficial")
    if isinstance(so, (dict, list)):
        notas["servidor_oficial_detalhe"] = so
        urls = [v for v in (so.values() if isinstance(so, dict) else so) if isinstance(v, str) and v.startswith("http")]
        g["servidor_oficial"] = urls[0] if urls else None
    if isinstance(g.get("limitacoes"), str):
        g["limitacoes"] = [g["limitacoes"]]
    if isinstance(g.get("regras_de_consulta"), (dict, list)):
        g.setdefault("regras_de_consulta_texto", g["regras_de_consulta"])
        g["regras_de_consulta"] = json.dumps(g["regras_de_consulta"], ensure_ascii=False)
    for c in g.get("camadas") or []:
        if "arquivo/campo" in c:
            c["arquivo"] = c.pop("arquivo/campo")
    g.setdefault("servidor_oficial", None)
    if notas:
        g["notas_tecnicas"] = notas
    return g


def normalizar_camada(c):
    c = dict(c)
    for k in ("observacao", "fonte_id", "artigo_anexo"):
        if k in c and c[k] is None:
            c.pop(k)
    ppc = c.get("parametros_por_codigo")
    if isinstance(ppc, dict):
        c["parametros_por_codigo"] = {cod: {re.sub(r"[^a-z0-9_]", "_", k.lower()): normalizar_param(v, k) for k, v in ps.items()}
                                      for cod, ps in ppc.items()}
    c.setdefault("parametros_por_codigo", None)
    return c


def normalizar(d, categorias=None):
    d = dict(d)
    d["schema_versao"] = "1.1"
    d["codigo_ibge"] = str(d.get("codigo_ibge", "")) if d.get("codigo_ibge") is not None else d.get("codigo_ibge")
    cm = d.get("centro_mapa")
    if isinstance(cm, dict) and isinstance(cm.get("zoom"), float):
        cm["zoom"] = int(round(cm["zoom"]))
    if isinstance(d.get("marco_legal_vigente"), (dict, list)):
        d["marco_legal_vigente"] = json.dumps(d["marco_legal_vigente"], ensure_ascii=False)
    d["macrozonas"] = normalizar_macrozonas(d.get("macrozonas"))
    for z in d.get("zonas", []):
        z["parametros"] = normalizar_parametros(z.get("parametros"))
        z.setdefault("descricao", None); z.setdefault("regra_sobreposicao", None)
        rg = z.get("regra_sobreposicao")
        if isinstance(rg, dict) and rg.get("mantem_da_base") is None and "mantem_da_base" in rg:
            rg["mantem_da_base"] = []          # null ≡ lista vazia (mesma semântica no motor)
        ob = z.get("observacoes")
        z["observacoes"] = [ob] if isinstance(ob, str) else [] if ob is None else [x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in ob]
        if categorias and z.get("codigo") in categorias:
            z["categoria_normalizada"] = categorias[z["codigo"]]
        extras = [k for k in z if k not in ("codigo", "nome", "descricao", "tipo", "prioridade", "categoria_normalizada",
                                            "categoria_criterio", "regra_sobreposicao", "parametros", "observacoes", "geometria")]
        for k in extras:
            v = z.pop(k)
            z["observacoes"].append(f"{_humano(k)}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}")
    d["camadas_complementares"] = {k: normalizar_camada(v) for k, v in (d.get("camadas_complementares") or {}).items()}
    for b in ("outorga_onerosa", "zeis_his", "outros_parametros"):
        d[b] = normalizar_bloco(d.get(b))
    r = d.get("resumo_mcmv")
    d["resumo_mcmv"] = (r if isinstance(r, list) and all(isinstance(x, str) for x in r) else
                        [r] if isinstance(r, str) else
                        [f"{_humano(k)}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}" for k, v in r.items()] if isinstance(r, dict) else
                        [x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in (r or [])])
    d["geografico"] = normalizar_geografico(d.get("geografico"))
    d["lacunas"] = [l if isinstance(l, dict) else {"item": str(l), "motivo": ""} for l in d.get("lacunas") or []]
    for l in d["lacunas"]:
        l.setdefault("motivo", "")
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada"); ap.add_argument("--saida"); ap.add_argument("--categorias", default="")
    ap.add_argument("--compacto", action="store_true")
    a = ap.parse_args()
    cats = dict(x.split("=", 1) for x in a.categorias.split(",") if "=" in x)
    d = normalizar(json.load(open(a.entrada, encoding="utf-8")), cats)
    with open(a.saida or a.entrada, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, **({"separators": (",", ":")} if a.compacto else {"indent": 1}))
    print("normalizado →", a.saida or a.entrada, "| rode: python3 ../validar_cidade.py --arquivo", a.saida or a.entrada)
