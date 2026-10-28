"""Baixa camadas vetoriais OFICIAIS e públicas (sem login) do IPP/Prefeitura do Rio (pgeo3 ArcGIS REST) em EPSG:4326."""
import json,urllib.request,urllib.parse,time,datetime,sys,os
S="https://pgeo3.rio.rj.gov.br/arcgis/rest/services"
UA={"User-Agent":"Mozilla/5.0 (Tenda-STAR levantamento urbanistico)"}
OUT=os.path.join(os.path.dirname(__file__),"..","geo_raw")
def get(u):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=180) as r: return json.load(r)
        except Exception as e:
            print("retry",e,file=sys.stderr); time.sleep(5)
    raise RuntimeError(u)
LAYERS=[
 ("zoneamento","Urbanismo/LBB_Zoneamento_urbano_vigente",0),
 ("macrozonas","Urbanismo/LBB_Zoneamento_urbano_vigente",1),
 ("smd","Urbanismo/LBB_Parametros",0),
 ("q_parametros","Urbanismo/LBB_Parametros",1),
 ("gabarito","Urbanismo/IU_Parametros_Gabarito",0),
 ("aeis","Urbanismo/LBB_AEIS",1),
 ("subsetores","Urbanismo/LBB_Setores_Subsetores",0),
 ("setores","Urbanismo/LBB_Setores_Subsetores",1),
 ("operacoes_urbanas","Urbanismo/IU_Operacoes_urbanas_temp",59),
 ("gabarito_especifico","Urbanismo/LBB_Gabarito_especifico",2),
 ("apac","Urbanismo/LBB_APAC",0),
 ("ape","Urbanismo/LBB_APE",0),
 ("aei","Urbanismo/LBB_AEI",0),
 ("app","Urbanismo/LBB_APP",0),
 ("zoneamento_ambiental","Urbanismo/LBB_Zoneamento_Ambiental",0),
 ("areas_protegidas","Urbanismo/LBB_Areas_Protegidas",0),
 ("cpa_ppa","Urbanismo/LBB_CPA_PPA",0),
 ("distritos_polos","Urbanismo/LBB_Distritos_Polos",0),
 ("corredor_cultural","Urbanismo/LBB_CorredorCultural",0),
 ("iptu_progressivo","Urbanismo/Macrozonas_IPTU_Progressivo",0),
]
if len(sys.argv)>1: LAYERS=[l for l in LAYERS if l[0] in sys.argv[1:]]
logf=os.path.join(OUT,"_log_download.json")
log=json.load(open(logf)) if os.path.exists(logf) else []
log=[l for l in log if l["tema"] not in [x[0] for x in LAYERS]]
for tema,svc,lid in LAYERS:
    base=f"{S}/{svc}/MapServer/{lid}"
    meta=get(base+"?f=json")
    mx=min(meta.get("maxRecordCount",1000),1000)
    feats=[];off=0
    while True:
        q=urllib.parse.urlencode({"where":"1=1","outFields":"*","returnGeometry":"true","outSR":"4326","f":"geojson","resultOffset":off,"resultRecordCount":mx,"orderByFields":meta.get("objectIdField") or "objectid"})
        d=get(base+"/query?"+q)
        fs=d.get("features",[]); feats+=fs
        if not fs or (len(fs)<mx and not d.get("exceededTransferLimit")): break
        off+=len(fs)
    fn=os.path.join(OUT,f"{tema}.geojson")
    json.dump({"type":"FeatureCollection","name":meta["name"],"features":feats},open(fn,"w"),ensure_ascii=False)
    log.append({"tema":tema,"arquivo":f"geo_raw/{tema}.geojson","camada":meta["name"],"url":base,"n_feicoes":len(feats),"baixado_em":datetime.datetime.now().isoformat(timespec="seconds")+"-03:00","geometria":meta.get("geometryType"),"descricao_servico":meta.get("description","")[:500]})
    print(tema,meta["name"],len(feats),flush=True)
json.dump(log,open(logf,"w"),ensure_ascii=False,indent=1)
