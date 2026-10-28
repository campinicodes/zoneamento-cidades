import re,html,sys,urllib.request
for arg in sys.argv[1:]:
    i,nome=arg.split(':')
    s=urllib.request.urlopen(urllib.request.Request(f'https://legisladocexterno.curitiba.pr.gov.br/VisualizarHTML.aspx?id={i}',headers={'User-Agent':'Mozilla/5.0'}),timeout=90).read().decode('utf-8','ignore')
    open(nome+'.html','w').write(s)
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
    t=re.sub(r'<br\s*/?>|</p>|</tr>|</div>|</h\d>','\n',t,flags=re.I); t=re.sub(r'</td>',' | ',t,flags=re.I)
    t=html.unescape(re.sub('<[^>]+>','',t)); t=re.sub(r'[ \t\xa0]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
    open(nome+'.txt','w').write(t)
    an=re.findall(r'DownloadAnexo\.ashx\?id=(\d+)[^"\']*',s)
    print(i,nome,len(t),'anexos',sorted(set(an)))
