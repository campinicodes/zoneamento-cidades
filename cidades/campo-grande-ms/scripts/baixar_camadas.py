import json,urllib.request,urllib.parse,time,datetime,sys
S="https://simgeoctm.campogrande.ms.gov.br/server/rest/services"
UA={"User-Agent":"Mozilla/5.0 (Tenda-STAR levantamento urbanistico; Grok Bot)"}
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120) as r: return json.load(r)
        except Exception as e:
            print("retry",e,file=sys.stderr); time.sleep(3)
    raise
LAYERS=[("PLANO_DIRETOR_PPDUA/PLANO_DIRETOR__PDDUA",i) for i in [24,12,15,5,13,29,10,9,8,7,6,14,3,11,17,18,0,22,20,19,25,16,4,23]]+[("LIMITES_ADMINISTRATIVOS/LIMITES_ADMINISTRATIVOS",i) for i in [1,3,4,6,7]]+[("MEIO_AMBIENTE/MEIO_AMBIENTE",i) for i in [1,2]]
log=[]
for svc,lid in LAYERS:
    base=f"{S}/{svc}/MapServer/{lid}"
    meta=get(base+"?f=json")
    name=meta["name"]; mx=meta.get("maxRecordCount",1000)
    feats=[];off=0
    while True:
        q=urllib.parse.urlencode({"where":"1=1","outFields":"*","returnGeometry":"true","outSR":"4326","f":"geojson","resultOffset":off,"resultRecordCount":mx})
        d=get(base+"/query?"+q)
        fs=d.get("features",[]); feats+=fs
        if not fs or len(fs)<mx and not d.get("exceededTransferLimit"): break
        off+=len(fs)
    fn=f"raw/{svc.split('/')[0].lower()}_{lid}.geojson"
    json.dump({"type":"FeatureCollection","name":name,"features":feats},open(fn,"w"),ensure_ascii=False)
    log.append({"arquivo":fn,"camada":name,"servico":svc,"layer_id":lid,"url":base,"n_feicoes":len(feats),"baixado_em":datetime.datetime.now().isoformat(timespec="seconds")+"-03:00","geometria":meta.get("geometryType")})
    print(lid,name,len(feats))
json.dump(log,open("raw/_log_download.json","w"),ensure_ascii=False,indent=1)
