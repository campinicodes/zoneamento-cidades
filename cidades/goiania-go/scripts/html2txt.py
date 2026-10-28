"""Converte HTML compilado do SILEG Goiânia em texto, removendo redações superadas (classes *alterado/*alterada). Uso: python3 html2txt.py in.html out.txt"""
import re, html, sys
b = open(sys.argv[1], 'rb').read()
out = []
for ln in b.split(b'\n'):
    try: out.append(ln.decode('utf-8'))
    except UnicodeDecodeError: out.append(ln.decode('latin-1'))
s = '\n'.join(out)
s = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
s = re.sub(r'(?is)<p class="[a-z]*(alterado|alterada)"\s*>.*?</p>', '', s)
s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</tr>|</td>', '\n', s)
s = re.sub(r'<[^>]+>', ' ', s)
t = html.unescape(s)
t = re.sub(r'[ \t\xa0]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
open(sys.argv[2], 'w').write(t)
print(sys.argv[2], len(t.splitlines()))
