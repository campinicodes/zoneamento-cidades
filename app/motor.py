"""Motor GENÉRICO de consulta de zoneamento por polígono (padrão PADRAO_JSON.md, schema 1.1).

Nada aqui é específico de uma cidade: a decisão sai só de
  zonas[].tipo / prioridade / regra_sobreposicao   e   camadas_complementares[].papel.
Uma Cidade é carregada sob demanda (lazy): na descoberta só se lê metadado + bbox;
os índices espaciais (STRtree em metros) são montados na 1ª consulta.
O resultado da descoberta (validação + metadado + bbox) fica em cache em disco (.cache_descoberta.json),
invalidado pela assinatura (mtime/tamanho) do JSON, do schema e do validador.
"""
import copy
import json
import math
import os
import sys
import threading

import numpy as np
import shapely
from pyproj import CRS, Transformer
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validar_cidade import validar  # noqa: E402

PCT_MIN_PADRAO = 0.5          # % abaixo do qual a sobreposição é resíduo de borda
RAIO_DIVISA_PADRAO = 30       # m
DIST_EIXO_PADRAO = 50         # m
LIMIAR_PADRAO = 50            # %
AREA_MAX_M2 = 50_000_000      # 50 km² – trava de segurança
DETALHE_PROPS = ("identificador", "subcodigo", "bairro", "nome")


# ---------------------------------------------------------------------------
# Projeção métrica
# ---------------------------------------------------------------------------
def epsg_utm(lon, lat):
    """EPSG da zona UTM do ponto: SIRGAS 2000 no Brasil (31972–31985), WGS 84 fora."""
    zona = int(math.floor((lon + 180) / 6)) + 1
    if -75 <= lon <= -28 and -35 <= lat <= 6:
        if lat < 0 and 18 <= zona <= 25:
            return 31960 + zona          # 31978 = 18S … 31985 = 25S
        if lat >= 0 and 18 <= zona <= 22:
            return 31954 + zona          # 31972 = 18N … 31976 = 22N
    return (32700 if lat < 0 else 32600) + zona


def crs_de(texto):
    """'EPSG:31981' / 'EPSG:31981 (SIRGAS…)' / 31981 → int EPSG, ou None."""
    if texto is None:
        return None
    if isinstance(texto, int):
        return texto
    t = str(texto).upper().replace(" ", "")
    if "EPSG:" in t:
        num = "".join(ch for ch in t.split("EPSG:")[1] if ch.isdigit())
        return int(num) if num else None
    return None


class Projetor:
    def __init__(self, epsg):
        self.epsg = epsg
        self.nome = f"EPSG:{epsg} ({CRS.from_epsg(epsg).name})"
        self._t = Transformer.from_crs(4326, epsg, always_xy=True).transform

    def __call__(self, geom):
        def f(xy):
            x, y = self._t(xy[:, 0], xy[:, 1])
            return np.column_stack([x, y])
        return shapely.transform(geom, f)


# ---------------------------------------------------------------------------
# Camada indexada
# ---------------------------------------------------------------------------
class Camada:
    def __init__(self, projetar):
        self.props, self.geoms, self.projetar = [], [], projetar
        self.arvore = None

    def adicionar(self, props, geom_json):
        g = shapely.make_valid(self.projetar(shape(geom_json)))
        if not g.is_empty:
            self.props.append(props or {})
            self.geoms.append(g)

    def indexar(self):
        self.arvore = STRtree(self.geoms) if self.geoms else None
        return self

    def perto(self, geom, raio=0):
        if self.arvore is None:
            return []
        return [int(i) for i in self.arvore.query(geom.buffer(raio) if raio else geom)]


def _rotulo(p):
    return next((str(p[k]) for k in DETALHE_PROPS if p.get(k)), "")


def sobreposicoes(camada, terreno, area, codigo_padrao=None):
    """[{codigo, area_m2, pct_terreno, detalhes:[{rotulo, area_m2, pct_terreno}]}] por área decrescente.
    Feições sobrepostas do mesmo código são unidas (a % nunca passa de 100)."""
    pedacos = {}
    for i in camada.perto(terreno):
        g = camada.geoms[i]
        if not g.intersects(terreno):
            continue
        inter = g.intersection(terreno)
        if inter.area <= 0.01:
            continue
        p = camada.props[i]
        cod = codigo_padrao or p.get("codigo")
        pedacos.setdefault(cod, {}).setdefault(_rotulo(p), []).append(inter)
    out = []
    for cod, por_rot in pedacos.items():
        tudo = shapely.union_all([g for gs in por_rot.values() for g in gs]).area
        det = sorted(((r, shapely.union_all(gs).area) for r, gs in por_rot.items() if r), key=lambda x: -x[1])
        it = {"codigo": cod, "area_m2": round(tudo, 1), "pct_terreno": round(100 * tudo / area, 2)}
        if det:
            it["detalhes"] = [{"rotulo": r, "area_m2": round(a, 1), "pct_terreno": round(100 * a / area, 2)} for r, a in det]
        out.append(it)
    return sorted(out, key=lambda x: -x["area_m2"])


# ---------------------------------------------------------------------------
# Cidade
# ---------------------------------------------------------------------------
_CACHE_ARQ = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache_descoberta.json")
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    _CACHE = json.load(open(_CACHE_ARQ, encoding="utf-8"))
except (OSError, ValueError):
    _CACHE = {}
_CACHE_LOCK = threading.Lock()


def _assinatura(caminho):
    arqs = [caminho, os.path.join(_RAIZ, "schema", "cidade.schema.json"), os.path.join(_RAIZ, "validar_cidade.py"),
            os.path.abspath(__file__)]
    return [[os.path.getmtime(a), os.path.getsize(a)] if os.path.exists(a) else None for a in arqs]


def _salvar_cache():
    with _CACHE_LOCK:
        try:
            tmp = _CACHE_ARQ + ".tmp"
            json.dump(_CACHE, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
            os.replace(tmp, _CACHE_ARQ)
        except OSError:
            pass                                       # cache é só otimização


def status_cidade(d):
    """Resumo genérico de qualidade (página inicial / README): zonas, % de área com geometria oficial, erro, lacunas."""
    area_of = area_tot = 0.0
    zonas_of = 0
    for z in d["zonas"]:
        a = sum(shape(f["geometry"]).area for f in z["geometria"]["features"]) if z["tipo"] == "base" else 0.0
        of = bool(z["geometria"].get("oficial"))
        zonas_of += of
        area_tot += a; area_of += a if of else 0.0
    g = d.get("geografico") or {}
    erros = [c.get("erro_estimado_m") for c in g.get("camadas") or [] if c.get("erro_estimado_m") is not None]
    return {"n_zonas": len(d["zonas"]),
            "n_zonas_base": sum(z["tipo"] == "base" for z in d["zonas"]),
            "zonas_geometria_oficial": zonas_of,
            "pct_area_base_oficial": round(100 * area_of / area_tot, 1) if area_tot else None,
            "erro_estimado_m": {"min": min(erros), "max": max(erros)} if erros else None,
            "metodo_geometria": "; ".join(sorted({c.get("metodo") for c in g.get("camadas") or [] if c.get("metodo")}))[:300],
            "data_levantamento": d.get("data_levantamento"),
            "n_lacunas": len(d.get("lacunas") or []),
            "n_fontes": len(d.get("fontes") or [])}


class Cidade:
    def __init__(self, caminho):
        self.caminho = caminho
        self.pasta = os.path.dirname(caminho)
        self._lock = threading.Lock()
        self._dados = None
        sig = _assinatura(caminho)
        info = _CACHE.get(caminho) if _CACHE.get(caminho, {}).get("sig") == sig else None
        if info is None:
            info = self._descobrir(caminho)
            info["sig"] = sig
            _CACHE[caminho] = info
            _salvar_cache()
        self.valida, self.erros_validacao, self.avisos_validacao = info["valida"], info["erros"], info["avisos"]
        self.meta, self.status = info["meta"], info.get("status") or {}
        self.bbox = tuple(info["bbox"]) if info["bbox"] else None
        self.tamanho_mb = round(os.path.getsize(caminho) / 1e6, 2)

    @staticmethod
    def _descobrir(caminho):
        val = validar(caminho, geometrias=False)       # estrutura; geometrias são checadas no validador CLI
        info = {"valida": val["ok"], "erros": val["erros"], "avisos": val["avisos"], "meta": {}, "bbox": None, "status": {}}
        if val["ok"]:
            d = json.load(open(caminho, encoding="utf-8"))
            meta = {k: d.get(k) for k in ("slug", "municipio", "uf", "codigo_ibge", "data_levantamento",
                                          "centro_mapa", "schema_versao", "orgao_confirmacao")}
            meta["exemplo_ficticio"] = bool(d.get("exemplo_ficticio"))
            xs, ys = [], []
            for z in d["zonas"]:
                if z["tipo"] == "base":
                    for f in z["geometria"]["features"]:
                        b = shape(f["geometry"]).bounds
                        xs += [b[0], b[2]]; ys += [b[1], b[3]]
            info["meta"], info["bbox"] = meta, ((min(xs), min(ys), max(xs), max(ys)) if xs else None)
            info["status"] = status_cidade(d)
        return info

    @property
    def slug(self):
        return self.meta.get("slug")

    @property
    def carregada(self):
        return self._dados is not None

    # ---- carga pesada, só na 1ª consulta ----
    def dados(self):
        if self._dados is None:
            with self._lock:
                if self._dados is None:
                    self._carregar()
        return self._dados

    def _carregar(self):
        d = json.load(open(self.caminho, encoding="utf-8"))
        g = d.get("geografico") or {}
        epsg = crs_de(g.get("crs_area"))
        if not epsg:
            c = d["centro_mapa"]
            epsg = epsg_utm(c["lon"], c["lat"])
        self.projetor = Projetor(epsg)
        self.zonas = {z["codigo"]: z for z in d["zonas"]}
        self.fontes = {f["id"]: f for f in d["fontes"]}
        self.cam_zona = {}
        for z in d["zonas"]:
            c = Camada(self.projetor)
            for f in z["geometria"]["features"]:
                c.adicionar(f.get("properties"), f["geometry"])
            self.cam_zona[z["codigo"]] = c.indexar()
        self.cam_base_todas = Camada(self.projetor)
        for z in d["zonas"]:
            if z["tipo"] == "base":
                for f in z["geometria"]["features"]:
                    self.cam_base_todas.adicionar({**(f.get("properties") or {}), "codigo": z["codigo"]}, f["geometry"])
        self.cam_base_todas.indexar()
        self.cam_compl = {}
        for nome, cc in (d.get("camadas_complementares") or {}).items():
            c = Camada(self.projetor)
            for f in cc.get("features") or []:
                c.adicionar(f.get("properties"), f["geometry"])
            self.cam_compl[nome] = c.indexar()
        self.pct_min = g.get("pct_minimo_significativo", PCT_MIN_PADRAO)
        self.raio_divisa = g.get("raio_divisa_m", RAIO_DIVISA_PADRAO)
        self._dados = d

    def contem(self, ponto_wgs):
        """Distância (m) do ponto às zonas base: 0 = dentro."""
        self.dados()
        p = self.projetor(ponto_wgs)
        idx = self.cam_base_todas.perto(p, 2000)
        if not idx:
            return None
        return min(self.cam_base_todas.geoms[i].distance(p) for i in idx)

    # ---- citações ----
    def com_links(self, obj):
        if isinstance(obj, dict):
            novo = {k: self.com_links(v) for k, v in obj.items()}
            f = self.fontes.get(obj.get("fonte_id"))
            if f:
                novo["fonte_lei"], novo["fonte_url"] = f.get("lei"), f.get("url")
            return novo
        if isinstance(obj, list):
            return [self.com_links(x) for x in obj]
        return obj

    def ficha(self, codigo):
        z = self.zonas.get(codigo)
        if not z:
            return None
        return {"codigo": z["codigo"], "nome": z["nome"], "tipo": z["tipo"], "descricao": z.get("descricao"),
                "parametros": self.com_links(z.get("parametros") or {}), "observacoes": z.get("observacoes")}


def _get(d, caminho):
    for k in caminho.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def _set(d, caminho, valor):
    ks = caminho.split(".")
    for k in ks[:-1]:
        d = d.setdefault(k, {})
    d[ks[-1]] = valor


def _fmt_lista(lst):
    return ", ".join(f'{x["codigo"]} {x["pct_terreno"]:.1f}%' for x in lst)


# ---------------------------------------------------------------------------
# Análise de UM polígono
# ---------------------------------------------------------------------------
def analisar(cid, geom_wgs):
    d = cid.dados()
    terreno = shapely.make_valid(cid.projetor(geom_wgs))
    area = terreno.area
    if area <= 1:
        raise ValueError("Polígono sem área.")
    if area > AREA_MAX_M2:
        raise ValueError("Polígono grande demais (> 50 km²).")
    regra = lambda z: z.get("regra_sobreposicao") or {"efeito": "apenas_alerta"}
    signif = lambda lst: [x for x in lst if x["pct_terreno"] >= cid.pct_min]
    alertas = []
    A = lambda tipo, texto, fonte=None: alertas.append({"tipo": tipo, "texto": texto, **({"fundamento": fonte} if fonte else {})})

    # ---- 1. sobreposições por tipo
    base, sobrepostas, eixos = [], {}, []
    for cod, z in cid.zonas.items():
        cam = cid.cam_zona[cod]
        if z["tipo"] == "base":
            base += sobreposicoes(cam, terreno, area, cod)
        elif z["tipo"] == "sobreposta":
            s = sobreposicoes(cam, terreno, area, cod)
            if s:
                sobrepostas[cod] = s[0]
        else:  # eixo: linha ou polígono
            r = regra(z)
            dmax = r.get("distancia_max_m") if r.get("distancia_max_m") is not None else DIST_EIXO_PADRAO
            idx = cam.perto(terreno, max(dmax, 1) * 20)
            if not idx:
                continue
            gs = [cam.geoms[i] for i in idx]
            dist = min(g.distance(terreno) for g in gs)
            pol = any("Polygon" in g.geom_type for g in gs)
            e = {"codigo": cod, "nome": z["nome"], "distancia_m": round(dist, 1), "toca": dist == 0,
                 "dentro_da_distancia": dist <= dmax, "distancia_max_m": dmax}
            if pol:
                s = sobreposicoes(cam, terreno, area, cod)
                e["pct_terreno"] = s[0]["pct_terreno"] if s else 0
            else:
                e["comprimento_dentro_m"] = round(sum(g.intersection(terreno).length for g in gs), 1)
            eixos.append(e)
    base.sort(key=lambda x: -x["area_m2"])
    eixos.sort(key=lambda x: x["distancia_m"])
    base_pred = base[0]["codigo"] if base else None

    # ---- 2. candidatas que substituem a base
    cands = []
    for cod, s in sobrepostas.items():
        z, r = cid.zonas[cod], regra(cid.zonas[cod])
        if r.get("efeito") != "substitui":
            continue
        lim = r.get("limiar_pct") if r.get("limiar_pct") is not None else LIMIAR_PADRAO
        sobre = r.get("aplica_sobre")
        if s["pct_terreno"] >= lim and (not sobre or base_pred in sobre):
            cands.append((z["prioridade"], s["pct_terreno"], cod,
                          f'{z["nome"]} cobre {s["pct_terreno"]:.1f}% do terreno (≥ {lim}%) – prioridade {z["prioridade"]}.'))
        elif s["pct_terreno"] >= lim:
            A("sobreposicao", f'{cod} cobre {s["pct_terreno"]:.1f}%, mas a regra só vale sobre {"/".join(sobre)} (base {base_pred}).', r.get("fundamento"))
        elif s["pct_terreno"] >= cid.pct_min:
            A("sobreposicao", f'{s["pct_terreno"]:.1f}% do terreno em {cod} (abaixo do limiar de {lim}%): ' +
              (r.get("alerta") or "na porção sobreposta valem os índices próprios."), r.get("fundamento"))
    for e in eixos:
        z, r = cid.zonas[e["codigo"]], regra(cid.zonas[e["codigo"]])
        if r.get("efeito") != "substitui" or not e["dentro_da_distancia"]:
            continue
        lim = r.get("limiar_pct")
        if "pct_terreno" in e and lim is not None and e["pct_terreno"] < lim:
            continue
        sobre = r.get("aplica_sobre")
        if sobre and base_pred not in sobre:
            continue
        cands.append((z["prioridade"], -e["distancia_m"], e["codigo"],
                      f'{e["codigo"]} a {e["distancia_m"]} m do terreno (≤ {e["distancia_max_m"]} m)' +
                      (" – vale SE o lote tiver testada para o eixo." if r.get("requer_testada") else ".") + f' Prioridade {z["prioridade"]}.'))
    cands.sort(key=lambda c: (c[0], c[1]), reverse=True)
    if cands and cands[0][0] > (cid.zonas[base_pred]["prioridade"] if base_pred else -1):
        aplicavel, criterio = cands[0][2], cands[0][3]
        for c in cands[1:]:
            A("precedencia", f"{c[2]} também se aplicaria, mas tem prioridade menor ou igual: {c[3]}")
    elif base_pred:
        aplicavel, criterio = base_pred, f"Zona base com maior área no terreno ({base[0]['pct_terreno']:.1f}%)."
    else:
        aplicavel, criterio = None, "Terreno fora das zonas base mapeadas no JSON da cidade – sem índices."

    # ---- 3. usa_indices_de (troca os índices da base)
    base_efetiva, troca = base_pred, None
    for cod, s in sorted(sobrepostas.items(), key=lambda kv: -cid.zonas[kv[0]]["prioridade"]):
        r = regra(cid.zonas[cod])
        if r.get("efeito") != "usa_indices_de":
            continue
        sobre = r.get("aplica_sobre")
        if sobre and base_pred not in sobre:
            if s["pct_terreno"] >= cid.pct_min:
                A("sobreposicao", f'{s["pct_terreno"]:.1f}% em {cod}: regra "usa índices de {r.get("usa_indices_de")}" vale só sobre '
                  f'{"/".join(sobre)}; aqui a base é {base_pred} – índices da base mantidos. ' + (r.get("alerta") or ""), r.get("fundamento"))
            continue
        lim = r.get("limiar_pct") if r.get("limiar_pct") is not None else LIMIAR_PADRAO
        if s["pct_terreno"] >= lim and troca is None:
            troca = {"zona": cod, "de": base_pred, "para": r.get("usa_indices_de"), "pct_terreno": s["pct_terreno"],
                     "mantem_da_base": r.get("mantem_da_base") or [], "fundamento": r.get("fundamento")}
            base_efetiva = r.get("usa_indices_de")
            A("sobreposicao", f'{cod} ({s["pct_terreno"]:.1f}% do terreno) sobre {base_pred}: índices de {base_efetiva}. ' + (r.get("alerta") or ""), r.get("fundamento"))
        elif s["pct_terreno"] >= cid.pct_min:
            A("sobreposicao", f'Só {s["pct_terreno"]:.1f}% do terreno em {cod} (limiar {lim}%): na porção em {cod} valem os índices de '
              f'{r.get("usa_indices_de")}; no restante, {base_pred}. ' + (r.get("alerta") or ""), r.get("fundamento"))
    zona_indices = base_efetiva if aplicavel == base_pred else aplicavel

    # ---- 4. apenas_alerta
    for cod, s in sobrepostas.items():
        r = regra(cid.zonas[cod])
        if r.get("efeito") == "apenas_alerta" and s["pct_terreno"] >= cid.pct_min:
            A("sobreposicao", f'{s["pct_terreno"]:.1f}% do terreno em {cod} – {cid.zonas[cod]["nome"]}. ' +
              (r.get("alerta") or "Regras específicas na porção sobreposta."), r.get("fundamento"))
    for e in eixos:
        r = regra(cid.zonas[e["codigo"]])
        if e["dentro_da_distancia"] and r.get("efeito") == "apenas_alerta":
            A("eixo", f'{e["codigo"]} a {e["distancia_m"]} m. ' + (r.get("alerta") or ""), r.get("fundamento"))

    # ---- 5. parâmetros
    ficha = cid.ficha(zona_indices)
    if ficha and troca and zona_indices == troca["para"]:
        orig = cid.ficha(troca["de"])
        for cam in troca["mantem_da_base"]:
            v = _get(orig["parametros"], cam)
            if v is not None:
                v = copy.deepcopy(v)
                v["observacao"] = (v.get("observacao") or "") + f' [Mantido da base {troca["de"]} – regra mantem_da_base de {troca["zona"]}.]'
                _set(ficha["parametros"], cam, v)
    if ficha and zona_indices != base_efetiva and base_efetiva:   # forma "herda_da_base" → valor da base efetiva
        base_f = cid.ficha(base_efetiva)
        def herdar(par, prefixo=""):
            for k, v in par.items():
                cam = prefixo + k
                if isinstance(v, dict) and v.get("forma") == "herda_da_base":
                    b = _get(base_f["parametros"], cam) if base_f else None
                    if isinstance(b, dict):
                        b = copy.deepcopy(b)
                        b["origem"] = f"herdado da base {base_efetiva} ({zona_indices}: forma herda_da_base)"
                        par[k] = b
                elif isinstance(v, dict) and "forma" not in v and k in ("recuos", "outros"):
                    herdar(v, cam + ".")
        herdar(ficha["parametros"])
    zona_ap = cid.zonas.get(aplicavel) or {}
    req_testada = regra(zona_ap).get("requer_testada") if zona_ap.get("tipo") != "base" else False
    if aplicavel and aplicavel != base_pred:
        r = regra(zona_ap)
        if r.get("alerta"):
            A("eixo" if zona_ap["tipo"] == "eixo" else "sobreposicao", f"{aplicavel}: {r['alerta']}", r.get("fundamento"))
    if req_testada:
        A("testada", f"Índices de {aplicavel} só valem com testada para o eixo/via; sem testada vale a base ({base_efetiva}) – ver 'parametros_zona_base'.")

    # ---- 6. camadas complementares
    compl, perm, macro = {}, None, None
    for nome, cc in (d.get("camadas_complementares") or {}).items():
        s = sobreposicoes(cid.cam_compl[nome], terreno, area)
        papel = cc.get("papel")
        cit = {"fonte_id": cc.get("fonte_id"), "artigo_anexo": cc.get("artigo_anexo")} if cc.get("fonte_id") else {}
        compl[nome] = {"papel": papel, "descricao": cc.get("descricao"), "sobreposicoes": s, **cid.com_links(cit)}
        ppc = cc.get("parametros_por_codigo") or {}
        if papel in ("permeabilidade", "macrozona") and s:
            pred = s[0]["codigo"]
            item = {"camada": nome, "codigo_predominante": pred, "parametros": cid.com_links(ppc.get(pred) or {})}
            if len(signif(s)) > 1:
                A(papel, f"Terreno em mais de um código da camada '{nome}': {_fmt_lista(signif(s))}.")
            if papel == "permeabilidade":
                perm = perm or item
                if ficha:
                    for k, v in (ppc.get(pred) or {}).items():
                        if k in ficha["parametros"]:
                            antigo = ficha["parametros"][k]
                            novo = cid.com_links(copy.deepcopy(v))
                            novo["origem"] = f"camada '{nome}' ({pred}) – papel permeabilidade prevalece sobre a coluna da zona"
                            if isinstance(antigo, dict) and antigo.get("observacao"):
                                novo["observacao_zona"] = antigo["observacao"]
                            ficha["parametros"][k] = novo
            else:
                macro = macro or item
        if papel == "restricao":
            apc = cc.get("alerta_por_codigo") or {}
            for x in s:
                A("restricao", f'{x["pct_terreno"]:.1f}% do terreno em {x["codigo"]} ({nome}): ' + (apc.get(x["codigo"]) or cc.get("descricao") or ""),
                  " ".join(filter(None, [cc.get("fonte_id"), cc.get("artigo_anexo")])) or None)
            dentro = {x["codigo"] for x in s}
            prox = {}
            for i in cid.cam_compl[nome].perto(terreno, cid.raio_divisa):
                g, p = cid.cam_compl[nome].geoms[i], cid.cam_compl[nome].props[i]
                if p.get("codigo") not in dentro and not g.intersects(terreno):
                    dd = g.distance(terreno)
                    if dd <= cid.raio_divisa:
                        prox[p.get("codigo")] = min(prox.get(p.get("codigo"), 1e9), dd)
            for c, dd in prox.items():
                A("restricao", f"{c} ({nome}) a {dd:.0f} m do terreno: " + (apc.get(c) or cc.get("descricao") or "") + " Verificar limites/faixas.")

    # ---- 7. alertas gerais
    if len(signif(base)) > 1:
        A("divisa", f"Terreno em mais de uma zona base: {_fmt_lista(signif(base))} – cada porção segue sua zona; confirmar critério de lote em divisa.")
    perto = {}
    for i in cid.cam_base_todas.perto(terreno, cid.raio_divisa):
        g, p = cid.cam_base_todas.geoms[i], cid.cam_base_todas.props[i]
        if p["codigo"] in {x["codigo"] for x in base} or g.intersects(terreno):
            continue
        dd = g.distance(terreno)
        if dd <= cid.raio_divisa:
            perto[p["codigo"]] = min(perto.get(p["codigo"], 1e9), dd)
    if perto:
        A("divisa", f"Divisa a menos de {cid.raio_divisa} m com: " + ", ".join(f"{c} ({v:.1f} m)" for c, v in sorted(perto.items(), key=lambda x: x[1])) + ".")
    nao_oficiais = [c for c in (d["geografico"].get("camadas") or []) if c.get("oficial") is False]
    if nao_oficiais:
        A("geometria", "Camadas NÃO oficiais/aproximadas nesta cidade: " +
          ", ".join(f'{c.get("nome")} ({c.get("metodo")}, erro ~{c.get("erro_estimado_m")} m)' for c in nao_oficiais) + ".")
    if d.get("exemplo_ficticio"):
        A("ficticio", "DADO FICTÍCIO DE EXEMPLO – esta cidade existe só para teste da plataforma.")
    A("confirmar", "Resultado indicativo – geometrias simplificadas e polígono aproximado; prevalece o texto legal. Confirmar na " +
      (d.get("orgao_confirmacao") or "prefeitura") + ".")

    c = shapely.centroid(geom_wgs)
    return {
        "cidade": {"slug": cid.slug, "municipio": d["municipio"], "uf": d["uf"]},
        "terreno": {"area_m2": round(area, 1), "area_ha": round(area / 1e4, 4), "perimetro_m": round(terreno.length, 1),
                    "centroide": {"lat": round(c.y, 6), "lon": round(c.x, 6)}, "crs_area": cid.projetor.nome},
        "resultado": {"zona_aplicavel": aplicavel, "nome_zona_aplicavel": zona_ap.get("nome"), "criterio": criterio,
                      "zona_dos_indices": zona_indices, "zona_base_predominante": base_pred, "zona_base_efetiva": base_efetiva,
                      "troca_de_indices": troca, "requer_testada": bool(req_testada),
                      "macrozona_predominante": (macro or {}).get("codigo_predominante"),
                      "permeabilidade_codigo": (perm or {}).get("codigo_predominante"),
                      "regra_de_consulta": d["geografico"].get("regras_de_consulta")},
        "parametros": ficha,
        "parametros_zona_base": cid.ficha(base_efetiva) if req_testada and base_efetiva and base_efetiva != zona_indices else None,
        "permeabilidade": perm,
        "macrozona": macro,
        "sobreposicoes": {"zonas_base": base, "sobrepostas": sorted(sobrepostas.values(), key=lambda x: -x["pct_terreno"]),
                          "eixos": eixos},
        "camadas_complementares": compl,
        "alertas": alertas,
        "referencias": f"/referencias/{cid.slug}",
    }


# ---------------------------------------------------------------------------
# Registro de cidades (descoberta + detecção)
# ---------------------------------------------------------------------------
class Registro:
    def __init__(self, pastas):
        self.cidades, self.invalidas = {}, {}
        for raiz in pastas:
            if not os.path.isdir(raiz):
                continue
            for slug in sorted(os.listdir(raiz)):
                cam = os.path.join(raiz, slug, f"{slug}.json")
                if not os.path.isfile(cam):
                    continue
                c = Cidade(cam)
                if c.valida and c.slug == slug:
                    self.cidades[slug] = c
                else:
                    self.invalidas[slug] = c.erros_validacao or [f"slug do JSON ('{c.slug}') difere da pasta"]

    def detectar(self, geom_wgs):
        """Cidade cujas zonas base contêm o centróide; senão a mais próxima (≤ 2 km) entre as que têm o ponto no bbox."""
        p = shapely.centroid(geom_wgs)
        cands = [c for c in self.cidades.values() if c.bbox and c.bbox[0] - .02 <= p.x <= c.bbox[2] + .02 and c.bbox[1] - .02 <= p.y <= c.bbox[3] + .02]
        melhor = None
        for c in cands:
            dist = c.contem(p)
            if dist is not None and (melhor is None or dist < melhor[0]):
                melhor = (dist, c)
        if melhor and melhor[0] <= 2000:
            return melhor[1], ("centróide dentro das zonas da cidade" if melhor[0] == 0 else f"zona mais próxima a {melhor[0]:.0f} m do centróide")
        return None, None
