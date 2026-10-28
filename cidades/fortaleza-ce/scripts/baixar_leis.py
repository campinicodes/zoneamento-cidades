"""Baixa textos integrais das normas no SAPL da Câmara Municipal de Fortaleza (API pública /api/norma/normajuridica)."""
import json, subprocess, os, sys
OUT = os.path.join(os.path.dirname(__file__), "..", "fontes")
API = "https://sapl.fortaleza.ce.leg.br/api/norma/normajuridica/"
def get(u):
    return json.loads(subprocess.run(["curl","-s","-m","60",u],capture_output=True,text=True).stdout)
ids = [int(x) for x in sys.argv[1:]]
meta = []
for i in ids:
    n = get(f"{API}{i}/")
    url = n["texto_integral"]
    if url: url = url.replace("http://","https://")
    fn = f"LC_{n['numero']}_{n['ano']}.pdf" if n["tipo"]==2 else f"N{n['tipo']}_{n['numero']}_{n['ano']}.pdf"
    if url:
        subprocess.run(["curl","-s","-m","300","-o",os.path.join(OUT,fn),url])
        subprocess.run(["pdftotext","-layout",os.path.join(OUT,fn),os.path.join(OUT,fn[:-4]+".txt")])
    meta.append({"id":i,"norma":n["__str__"],"ementa":n["ementa"],"data_publicacao":n["data_publicacao"],"veiculo":n["veiculo_publicacao"],"texto_integral":url,"arquivo":fn,"pagina":f"https://sapl.fortaleza.ce.leg.br/norma/{i}"})
    print(i, n["__str__"], "|", n["ementa"][:150])
old = []
p = os.path.join(OUT,"_normas_sapl.json")
if os.path.exists(p): old = json.load(open(p))
d = {m["id"]:m for m in old+meta}
json.dump(list(d.values()), open(p,"w"), ensure_ascii=False, indent=1)
