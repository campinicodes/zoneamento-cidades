"""Etapa 2 do pipeline de Campo Grande: leva o JSON gerado por migrar_para_padrao.py (schema 1.0, textos da tabela)
ao formato normalizado do schema (schema/cidade.schema.json, versão 1.1).
1) conversões ESPECÍFICAS de CG (textos do Anexo 8.2 → condicionais/fórmulas, permeabilidade por Zona Ambiental,
   usos por grupo, vagas, índice de elevação), feitas só quando o valor ainda está no formato legado (idempotente);
2) normalizador genérico (schema/normalizar_cidade.py);
3) categoria_normalizada (classificação do analista, não da lei – ver categoria_criterio).
Nada é inventado: todo texto convertido é preservado em texto_original.
Uso: python3 scripts/migrar_para_padrao.py && python3 scripts/normalizar_schema_cg.py"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, "..", "campo-grande-ms.json")
sys.path.insert(0, os.path.join(AQUI, "..", "..", "..", "schema"))
from normalizar_cidade import normalizar, num  # noqa: E402

CATEGORIAS = {  # (categoria, critério)
 "Z1": ("mista_alta_densidade", "Zona urbana de uso misto (R1–R3 e usos especiais E*); CA máx. 5 (> 3 ⇒ alta)."),
 "Z2": ("mista_alta_densidade", "Uso misto; CA máx. 5 (> 3 ⇒ alta)."),
 "Z3": ("mista_alta_densidade", "Uso misto; CA máx. 4 (> 3 ⇒ alta)."),
 "Z4": ("mista_media_densidade", "Uso misto; CA máx. 3 (1,5 < CA ≤ 3 ⇒ média)."),
 "Z5": ("residencial_baixa_densidade", "Residencial só R1/R2 (sem multifamiliar R3/E1–E3); CA máx. 1,5 (≤ 1,5 ⇒ baixa)."),
 "ZC": ("centralidade", "Zona de Centralidade (sobreposta)."),
 "ZEIE": ("especial_economica", "Zona Especial de Interesse Econômico (polos empresariais/industriais)."),
 "EA1": ("eixo", "Eixo de adensamento (linha; vale para lotes com testada)."),
 "EA2": ("eixo", "Eixo de adensamento (linha; vale para lotes com testada)."),
 "EA3": ("eixo", "Eixo de adensamento (linha; vale para lotes com testada)."),
 "ANHANDUI": ("mista_media_densidade", "Distrito urbano de Anhanduí: uso misto, CA máx. 2 (1,5 < CA ≤ 3 ⇒ média)."),
 "ZEU": ("expansao", "Zona de Expansão Urbana."),
 "ZEIS1": ("especial_interesse_social", "ZEIS 1 – regularização fundiária."),
 "ZEIS2": ("especial_interesse_social", "ZEIS 2 – vazios para HIS."),
 "ZEIA2": ("ambiental", "Zona Especial de Interesse Ambiental 2."),
}

R_NUM = r"\d+(?:,\d+)?"


def _caso(cond, txt):
    """'livre' | '5,00 m' | 'h/6 (mín. 3,00 m)' → condicional."""
    t = txt.strip()
    c = {"condicao": cond.strip(), "forma": None, "valor": None, "texto_original": t}
    if t.lower() == "livre":
        c["forma"] = "livre"
    elif re.fullmatch(rf"{R_NUM} m", t):
        c.update(forma="unico", valor=num(t[:-2]))
    elif (m := re.fullmatch(rf"(h/\d+) \(mín\. ({R_NUM}) m\)", t)):
        c.update(forma="formula", formula=m.group(1), faixa={"min": num(m.group(2)), "max": None},
                 observacao="h = altura da edificação (m); resultado em metros, com o mínimo indicado em faixa.min")
    else:
        c["forma"] = "texto"
    return c


def recuo(texto):
    """Textos de recuo do Anexo 8.2 → lista de condicionais."""
    t = texto
    nota = None
    if (m := re.search(r"\s*\((nota \d+): ([^)]*)\)\s*$", t)):
        nota, t = m, t[:m.start()]
    conds = []
    for seg in [s for s in t.split(";") if s.strip()]:
        cond, _, val = seg.rpartition(":")
        conds.append(_caso(cond, val))
    if nota:
        conds.append({"condicao": f"edifício com fachada ativa ({nota.group(1)}) – térreo e 1º pavimento", "forma": "livre",
                      "valor": None, "texto_original": nota.group(0).strip(" ()")})
    return conds


def p(base, **k):
    q = {kk: base.get(kk) for kk in ("valor", "unidade", "fonte_id", "artigo_anexo", "observacao")}
    q.update(k)
    return q


def especificos_cg(d):
    za = d["camadas_complementares"]["zonas_ambientais"]["parametros_por_codigo"]
    def za_val(cod):
        v = za[cod]["taxa_permeabilidade"]["valor"]
        return v if isinstance(v, (int, float)) else None
    for z in d["zonas"]:
        P = z["parametros"]
        if isinstance(P.get("recuos"), dict):
            for lado, r in P["recuos"].items():
                if r and isinstance(r.get("valor"), str) and re.search(r"IE|pav", r["valor"]):
                    P["recuos"][lado] = p(r, valor=None, forma="condicional", condicionais=recuo(r["valor"]), texto_original=r["valor"])
        tp = P.get("taxa_permeabilidade")
        if tp and isinstance(tp.get("valor"), str) and "%" not in tp["valor"][:3] or (tp and tp.get("detalhe_por_zona_ambiental")):
            det = tp.get("detalhe_por_zona_ambiental") or {}
            txt = tp["valor"]
            if det and len(det) == 1 and re.fullmatch(r"\d+%", txt):
                (cod, info), = det.items()
                P["taxa_permeabilidade"] = p(tp, valor=num(txt[:-1]) / 100, forma="unico", texto_original=txt,
                    observacao=(tp.get("observacao") or "") + f" | Zona Ambiental {cod} (bairros: {', '.join(info.get('bairros', []))}).")
            else:
                cods = list(det) or sorted(za)
                conds = [{"condicao": f"lote na Zona Ambiental {c}", "codigo": c, "forma": "unico", "valor": za_val(c),
                          **({"observacao": "bairros: " + ", ".join(det[c].get("bairros", []))} if c in det else {})}
                         for c in cods if za_val(c) is not None]
                P["taxa_permeabilidade"] = p(tp, valor=None, forma="condicional", condicionais=conds, texto_original=txt)
        for k in ("ca_basico", "ca_maximo", "usos_permitidos"):
            q = P.get(k)
            if q and isinstance(q.get("valor"), str) and re.match(r"(Igual|Da zona|Usos da zona)", q["valor"]):
                P[k] = p(q, valor=None, forma="herda_da_base", texto_original=q["valor"],
                         observacao=q.get("observacao") or "Valor da zona urbana subjacente (base).")
        u = P.get("usos_permitidos")
        if u and isinstance(u.get("valor"), dict):
            g = u["valor"]
            usos = g.get("residencial", []) + g.get("especial", [])
            conds = [{"condicao": "uso residencial", "forma": "lista", "valor": g.get("residencial", [])},
                     {"condicao": "usos especiais (E)", "forma": "lista", "valor": g.get("especial", [])},
                     {"condicao": "tipos de parcelamento/loteamento admitidos", "forma": "lista", "valor": g.get("loteamento", [])},
                     {"condicao": "multifamiliar/condomínio permitido", "forma": "lista", "valor": g.get("multifamiliar_condominios_permitidos", []),
                      "observacao": g.get("multifamiliar_resumo")}]
            P["usos_permitidos"] = p(u, valor=usos, forma="lista", condicionais=conds)
        l = P.get("lote_minimo_m2")
        if l and l.get("valor") == "Conforme zona urbana; em loteamento L2: 200 m²":
            P["lote_minimo_m2"] = p(l, valor=None, forma="condicional", texto_original=l["valor"], condicionais=[
                {"condicao": "geral", "forma": "herda_da_base", "valor": None},
                {"condicao": "loteamento de interesse social L2", "codigo": "L2", "forma": "unico", "valor": 200}])
        v = P.get("vagas")
        if v and isinstance(v.get("valor"), str) and v["valor"].startswith("1 vaga por unidade habitacional"):
            P["vagas"] = p(v, valor=1, unidade="vagas/UH", forma="unico", texto_original=v["valor"],
                           observacao="Residencial: 1 vaga por UH. Demais regras: " + v["valor"].split(";", 1)[1].strip())
        elif v and isinstance(v.get("valor"), dict) and set(v["valor"]) == {"MZ1", "MZ2", "MZ3"}:
            def mz(cod, txt):
                c = {"condicao": f"macrozona {cod}", "codigo": cod, "texto_original": txt, "valor": None}
                m = re.search(r"mínimo (\d+)% do total de unidades", txt)
                if m:
                    c.update(forma="unico", valor=int(m.group(1)) / 100, observacao="vagas para pelo menos esta fração das UH (vagas/UH)")
                elif "dispensada" in txt:
                    c.update(forma="livre", observacao="exigência de vagas pode ser dispensada")
                else:
                    c["forma"] = "texto"
                return c
            P["vagas"] = p(v, valor=None, unidade="vagas/UH", forma="condicional", condicionais=[mz(c, t) for c, t in v["valor"].items()])
        ie = (P.get("outros") or {}).get("indice_elevacao")
        if ie and isinstance(ie.get("valor"), str):
            t = ie["valor"]
            if (m := re.fullmatch(rf"({R_NUM}) \(com OODC/TDC passa a (Livre|{R_NUM}) – (nota \d+)\)", t)):
                com = ({"forma": "livre", "valor": None} if m.group(2) == "Livre" else {"forma": "unico", "valor": num(m.group(2))})
                P["outros"]["indice_elevacao"] = p(ie, valor=None, unidade="coeficiente", forma="condicional", texto_original=t, condicionais=[
                    {"condicao": "sem OODC/TDC", "forma": "unico", "valor": num(m.group(1))},
                    {"condicao": f"com OODC/TDC ({m.group(3)})", **com}])
            elif re.fullmatch(R_NUM, t):
                P["outros"]["indice_elevacao"] = p(ie, valor=num(t), unidade="coeficiente", forma="unico")
            elif t == "Livre":
                P["outros"]["indice_elevacao"] = p(ie, valor=None, unidade="coeficiente", forma="livre", texto_original=t)
        for k in ("potencial_adicional_oodc_tdc", "fator_oodc_fid"):
            q = (P.get("outros") or {}).get(k)
            if q and not q.get("unidade"):
                q["unidade"] = "coeficiente"
    if isinstance(d.get("macrozonas"), list):
        for m in d["macrozonas"]:
            if "densidade_liquida_max_hab_ha" in m and not isinstance(m["densidade_liquida_max_hab_ha"], dict):
                m["densidade_liquida_max_hab_ha"] = {"valor": m["densidade_liquida_max_hab_ha"], "unidade": "hab/ha",
                                                     "fonte_id": m.get("fonte_id"), "artigo_anexo": m.get("artigo_anexo")}
    zh = d.get("zeis_his") or {}
    if isinstance(zh.get("area_max_uh_m2"), dict):
        zh["area_max_uh_m2"].setdefault("unidade", "m2")
    ff = (d.get("outorga_onerosa") or {}).get("fator_fid_por_zona")
    if isinstance(ff, dict):
        ff.setdefault("unidade", "coeficiente")
    return d


def main():
    d = json.load(open(ARQ, encoding="utf-8"))
    if d.get("schema_versao") != "1.1":
        d = especificos_cg(d)
    d = normalizar(d, {k: v[0] for k, v in CATEGORIAS.items()})
    for z in d["zonas"]:
        z["categoria_criterio"] = "Classificação do analista (não é termo legal): " + CATEGORIAS[z["codigo"]][1]
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
    print("ok →", os.path.normpath(ARQ), f"{os.path.getsize(ARQ)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
