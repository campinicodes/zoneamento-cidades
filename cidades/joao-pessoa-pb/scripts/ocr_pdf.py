"""OCR simples (RapidOCR/onnx) de PDFs escaneados: uso /workspace/.venv_ocr/bin/python ocr_pdf.py arq.pdf [dpi]"""
import sys, pymupdf as fitz, numpy as np
from rapidocr_onnxruntime import RapidOCR
eng = RapidOCR(); pdf = sys.argv[1]; dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 200
out = []
for i, p in enumerate(fitz.open(pdf)):
    pix = p.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
    res, _ = eng(img)
    out.append(f'===== página {i+1} =====')
    lines = []
    for box, txt, sc in (res or []):
        y = (box[0][1] + box[2][1]) / 2; x = box[0][0]; lines.append((y, x, txt))
    lines.sort(); cur = []; ly = None
    for y, x, t in lines:
        if ly is not None and abs(y - ly) > 12: out.append(' | '.join(c for _, c in sorted(cur))); cur = []
        cur.append((x, t)); ly = y
    if cur: out.append(' | '.join(c for _, c in sorted(cur)))
open(pdf[:-4] + '.ocr.txt', 'w').write('\n'.join(out))
print('ok', pdf)
