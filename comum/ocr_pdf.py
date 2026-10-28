"""OCR de PDFs escaneados (RapidOCR/onnxruntime). Uso: python ocr_pdf.py arquivo.pdf [pag_ini pag_fim] -> arquivo.ocr.txt
Agrupa caixas por linha (y) para manter a ordem de leitura; tabelas saem com colunas separadas por ' | '."""
import sys, fitz
from rapidocr_onnxruntime import RapidOCR
eng = RapidOCR()
pdf = sys.argv[1]; doc = fitz.open(pdf)
a = int(sys.argv[2]) if len(sys.argv) > 2 else 1; b = int(sys.argv[3]) if len(sys.argv) > 3 else doc.page_count
out = open(pdf[:-4] + (f".p{a}-{b}" if len(sys.argv) > 2 else "") + ".ocr.txt", "w")
for pn in range(a - 1, b):
    pix = doc[pn].get_pixmap(dpi=200)
    res, _ = eng(pix.tobytes("png"))
    out.write(f"\n===== página {pn+1} =====\n")
    if not res: continue
    items = sorted([(min(p[1] for p in bx), min(p[0] for p in bx), max(p[1] for p in bx), t) for bx, t, s in res])
    lines = []
    for y0, x0, y1, t in items:
        if lines and abs(lines[-1][0] - y0) < (y1 - y0) * 0.6: lines[-1][1].append((x0, t))
        else: lines.append([y0, [(x0, t)]])
    for y, ws in lines: out.write(" | ".join(t for x, t in sorted(ws)) + "\n")
    out.flush()
print("ok", pdf)
