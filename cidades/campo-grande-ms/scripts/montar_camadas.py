"""Gera camadas temáticas GeoJSON (EPSG:4326) a partir dos dados OFICIAIS baixados do
ArcGIS REST público do SIMGEO/PLANURB (raw/). Não altera geometrias, só seleciona/renomeia atributos."""
import json
R="raw/"
def L(n): return json.load(open(R+n+".geojson"))
log={x["layer_id"]:x for x in json.load(open(R+"_log_download.json")) if "PLANO" in x["servico"]}
logl={x["layer_id"]:x for x in json.load(open(R+"_log_download.json")) if "LIMITES" in x["servico"]}
logm={x["layer_id"]:x for x in json.load(open(R+"_log_download.json")) if "MEIO" in x["servico"]}
def fc(name,feats,src):
    return {"type":"FeatureCollection","name":name,"crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "metadata":{"fonte":"SIMGEO – Prefeitura de Campo Grande (ArcGIS Server público)","camadas_origem":src,"oficial":True,"epsg":4326},"features":feats}
def F(g,p): return {"type":"Feature","geometry":g,"properties":p}
def keep(p,ks): return {k:p.get(k) for k in ks if k in p}
IDX=["ocupacao","camin","cabas","camax","oo_t_dc","elevacao","area_m2","esquina_m","quadra_m","frente","lat_fundos","oo_t_dc_lf","residencia","especial","loteamento"]
# zonas
feats=[]
for f in L("plano_diretor_ppdua_12")["features"]:
    p=f["properties"]; feats.append(F(f["geometry"],{"codigo":p["sigla"],"tipo":"zona_urbana","nome":p["zona"],"bairro":p["bairro"],"regiao_urbana":p.get("reg_urb"),"legislacao":p["legislacao"],**keep(p,IDX),"camada_oficial":"Zonas urbanas (id 12)"}))
for f in L("plano_diretor_ppdua_6")["features"]:
    p=f["properties"]; feats.append(F(f["geometry"],{"codigo":"ZEIE","subcodigo":p.get("categoria"),"tipo":"zona_especial_economica","nome":p["zona"],"legislacao":p["legislacao"],**keep(p,IDX),"camada_oficial":"ZEIE (id 6)"}))
for f in L("plano_diretor_ppdua_4")["features"]:
    p=f["properties"]; feats.append(F(f["geometry"],{"codigo":"ZEU","tipo":"zona_expansao_urbana","nome":p["zona"],"legislacao":p["legislacao"],**keep(p,IDX),"camada_oficial":"Macrozona Sede e Zona de Expansão Urbana (id 4)"}))
for f in L("limites_administrativos_4")["features"]:
    p=f["properties"]; feats.append(F(f["geometry"],{"codigo":"ANHANDUI","tipo":"distrito","nome":p.get("zona"),"legislacao":p["legislacao"],**keep(p,IDX),"camada_oficial":"PERIMETRO_ANHANDUI_220221 (id 4)"}))
json.dump(fc("zonas",feats,[log[12]["url"],log[6]["url"],log[4]["url"],logl[4]["url"]]),open("zonas.geojson","w"),ensure_ascii=False)
# macrozonas
feats=[F(f["geometry"],{"codigo":f["properties"]["sigla"],"nome":f["properties"]["macrozona"],"bairro":f["properties"]["bairro"],"legislacao":f["properties"]["legislacao"]}) for f in L("plano_diretor_ppdua_24")["features"]]
feats+=[F(f["geometry"],{"codigo":f["properties"]["sigla"],"nome":f["properties"]["macrozona"],"classificacao":f["properties"].get("classifica"),"legislacao":f["properties"]["legislacao"],"escala":"municipal"}) for f in L("plano_diretor_ppdua_23")["features"]]
json.dump(fc("macrozonas",feats,[log[24]["url"],log[23]["url"]]),open("macrozonas.geojson","w"),ensure_ascii=False)
# zonas ambientais
feats=[F(f["geometry"],{"codigo":f["properties"]["sigla"],"nome":f["properties"]["zona"],"bairro":f["properties"]["bairro"],"taxa_permeabilidade":f["properties"]["tx_perm"],"tra_minima":round(float(f["properties"]["tra_min"]),2) if f["properties"]["tra_min"] is not None else None,"fator_alfa":f["properties"].get("fator_alfa"),"fator_beta":f["properties"].get("fator_beta"),"legislacao":f["properties"]["legislacao"]}) for f in L("plano_diretor_ppdua_15")["features"]]
json.dump(fc("zonas_ambientais",feats,[log[15]["url"]]),open("zonas_ambientais.geojson","w"),ensure_ascii=False)
# zeis
feats=[F(f["geometry"],{"codigo":f["properties"]["sigla"].replace(" ",""),"identificador":f["properties"].get("categoria"),"nome":f["properties"]["zona"],"bairro":f["properties"].get("bairro"),"legislacao":f["properties"]["legislacao"]}) for f in L("plano_diretor_ppdua_13")["features"]]
json.dump(fc("zeis",feats,[log[13]["url"]]),open("zeis.geojson","w"),ensure_ascii=False)
# eixos e centralidades
feats=[]
for f in L("plano_diretor_ppdua_14")["features"]:
    p=f["properties"]; feats.append(F(f["geometry"],{"codigo":"ZC","tipo":"centralidade","nome":p["zona"],"legislacao":p["legislacao"],**keep(p,IDX)}))
for f in L("plano_diretor_ppdua_3")["features"]:
    p=f["properties"]; cod=p["nome"].split("-")[-1].strip().replace(" ","")
    feats.append(F(f["geometry"],{"codigo":cod,"tipo":"eixo_adensamento","nome":p["nome"],"legislacao":p.get("legislacao"),**keep(p,IDX),"nota":"Linha (eixo viário). Aplica-se aos lotes lindeiros ao eixo – verificar testada do lote."}))
json.dump(fc("eixos_centralidades",feats,[log[14]["url"],log[3]["url"]]),open("eixos_centralidades.geojson","w"),ensure_ascii=False)
# zeia
feats=[F(f["geometry"],{"codigo":f["properties"]["sigla"],"identificador":f["properties"].get("categoria"),"nome":f["properties"]["zona"],"legislacao":f["properties"]["legislacao"]}) for f in L("plano_diretor_ppdua_11")["features"]]
json.dump(fc("zeia",feats,[log[11]["url"]]),open("zeia.geojson","w"),ensure_ascii=False)
# extras
def simple(lid,name,code=None,src=log):
    d=L(("plano_diretor_ppdua_" if src is log else "limites_administrativos_" if src is logl else "meio_ambiente_")+str(lid))
    feats=[F(f["geometry"],{**{k:v for k,v in f["properties"].items() if not k.startswith("st_") and k!="objectid"},"codigo":code or f["properties"].get("sigla")}) for f in d["features"]]
    json.dump(fc(name,feats,[src[lid]["url"]]),open(name+".geojson","w"),ensure_ascii=False)
simple(5,"zepa","ZEPA"); simple(29,"zeiu","ZEIU"); simple(22,"ooaus_areas","OOAUS"); simple(19,"peuc","PEUC"); simple(25,"iptu_progressivo","IPTU_PROG")
simple(20,"operacao_urbana_consorciada","OUC"); simple(17,"tdc_transferir","TDC_CED"); simple(18,"tdc_receber","TDC_REC")
simple(3,"perimetro_urbano","PERIM",logl); simple(7,"bairros",None,logl); simple(1,"hidrografia",None,logm)
print("ok")
# ZEIC (anexos 12.1–12.4) e APA
feats=[]; srcs=[]
for lid in (10,9,8,7):
    for f in L("plano_diretor_ppdua_%d"%lid)["features"]:
        feats.append(F(f["geometry"],{**{k:v for k,v in f["properties"].items() if not k.startswith("st_") and k!="objectid"},"codigo":"ZEIC","camada_oficial":log[lid]["camada"]}))
    srcs.append(log[lid]["url"])
json.dump(fc("zeic",feats,srcs),open("zeic.geojson","w"),ensure_ascii=False)
simple(2,"apa_lajeado","APA",logm)
print("ok2")
