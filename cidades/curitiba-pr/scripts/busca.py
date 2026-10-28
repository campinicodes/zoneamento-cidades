import re,sys,html,requests
U='https://legisladocexterno.curitiba.pr.gov.br/AtosConsultaExterna.aspx'
def busca(tipo,num,ano):
    s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
    p=s.get(U,timeout=60).text
    data={}
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*>',p):
        n=re.search(r'name="([^"]+)"',m.group(0)); v=re.search(r'value="([^"]*)"',m.group(0))
        if n: data[n.group(1)]=html.unescape(v.group(1)) if v else ''
    for m in re.finditer(r'<select[^>]*name="([^"]+)"[^>]*>(.*?)</select>',p,re.S):
        opts=re.findall(r'<option([^>]*)value="([^"]*)"',m.group(2))
        sel=[v for a,v in opts if 'selected' in a]
        data[m.group(1)]=sel[0] if sel else (opts[0][1] if opts else '')
    for m in re.finditer(r'<input[^>]*type="text"[^>]*>',p):
        n=re.search(r'name="([^"]+)"',m.group(0)); v=re.search(r'value="([^"]*)"',m.group(0))
        if n: data[n.group(1)]=v.group(1) if v else ''
    pre='ctl00$cphMasterPrincipal$'
    data.update({'__EVENTTARGET':pre+'lnbPesquisar','__EVENTARGUMENT':'',pre+'ddlTipoAto':tipo,pre+'txtNrAto':num,pre+'txtAno':ano,pre+'txtTextoBuscado':''})
    r=s.post(U,data=data,timeout=90).text
    ids=sorted(set(re.findall(r'VisualizarHTML\.aspx\?id=(\d+)|[?&]id=(\d+)',r)))
    print(tipo,num,ano,len(r),ids[:20])
    open(f'/tmp/busca_{tipo}_{num}_{ano}.html','w').write(r)
for a in sys.argv[1:]:
    busca(*a.split(':'))

def visualizar(tipo,num,ano):
    s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
    def form(p):
        data={}
        for m in re.finditer(r'<input[^>]*type="hidden"[^>]*>',p):
            n=re.search(r'name="([^"]+)"',m.group(0)); v=re.search(r'value="([^"]*)"',m.group(0))
            if n: data[n.group(1)]=html.unescape(v.group(1)) if v else ''
        for m in re.finditer(r'<select[^>]*name="([^"]+)"[^>]*>(.*?)</select>',p,re.S):
            opts=re.findall(r'<option([^>]*)value="([^"]*)"',m.group(2)); sel=[v for a,v in opts if 'selected' in a]
            data[m.group(1)]=sel[0] if sel else (opts[0][1] if opts else '')
        for m in re.finditer(r'<input[^>]*type="text"[^>]*>',p):
            n=re.search(r'name="([^"]+)"',m.group(0)); v=re.search(r'value="([^"]*)"',m.group(0))
            if n: data[n.group(1)]=html.unescape(v.group(1)) if v else ''
        return data
    pre='ctl00$cphMasterPrincipal$'
    p=s.get(U,timeout=60).text; d=form(p)
    d.update({'__EVENTTARGET':pre+'lnbPesquisar','__EVENTARGUMENT':'',pre+'ddlTipoAto':tipo,pre+'txtNrAto':num,pre+'txtAno':ano})
    r=s.post(U,data=d,timeout=90)
    links=re.findall(r'(ctl00\$cphMasterPrincipal\$gdvGrid2\$ctl\d+\$lnkVisualizar)',r.text)
    out=[]
    for l in dict.fromkeys(links):
        d2=form(r.text); d2.update({'__EVENTTARGET':l,'__EVENTARGUMENT':''})
        r2=s.post(U,data=d2,timeout=90,allow_redirects=True)
        ids=re.findall(r'VisualizarHTML\.aspx\?id=(\d+)',r2.url+r2.text)
        out.append((l,r2.url,ids[:3]))
    return out

def ids_de(tipo,num,ano):
    s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
    p=s.get(U,timeout=60).text
    data={}
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*>',p):
        n=re.search(r'name="([^"]+)"',m.group(0)); v=re.search(r'value="([^"]*)"',m.group(0))
        if n: data[n.group(1)]=html.unescape(v.group(1)) if v else ''
    for m in re.finditer(r'<select[^>]*name="([^"]+)"[^>]*>(.*?)</select>',p,re.S):
        opts=re.findall(r'<option([^>]*)value="([^"]*)"',m.group(2)); sel=[v for a,v in opts if 'selected' in a]
        data[m.group(1)]=sel[0] if sel else (opts[0][1] if opts else '')
    pre='ctl00$cphMasterPrincipal$'
    data.update({'__EVENTTARGET':pre+'lnbPesquisar','__EVENTARGUMENT':'',pre+'ddlTipoAto':tipo,pre+'txtNrAto':num,pre+'txtAno':ano,pre+'txtTextoBuscado':'',pre+'txtNrAtoFinal':''})
    r=s.post(U,data=data,timeout=90).text
    t=re.sub(r'\s+',' ',html.unescape(re.sub(r'<script.*?</script>|<[^>]+>',' ',r,flags=re.S)))
    i=t.find('Encontrado'); 
    return re.findall(r'linkToView\(&quot;(\d+)&quot;\)',r), t[i:i+500]
