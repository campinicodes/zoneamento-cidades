import zipfile,re,sys
for f in sys.argv[1:]:
    x=zipfile.ZipFile(f).read('word/document.xml').decode()
    x=re.sub(r'</w:p>','\n',x); t=re.sub(r'<[^>]+>','',x)
    open(f.rsplit('.',1)[0]+'.txt','w').write(t)
