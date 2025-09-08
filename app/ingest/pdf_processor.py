from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF
import re

def extract_text_blocks(pdf_path: Path) -> List[Dict]:
    doc = fitz.open(pdf_path)
    blocks = []
    for page_no, page in enumerate(doc, start=1):
        for b in page.get_text("blocks", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE):
            x0, y0, x1, y1 = b[0], b[1], b[2], b[3]
            text = b[4] if len(b) > 4 else ''
            txt = (text or '').strip()
            if not txt:
                continue
            blocks.append({
                "page": page_no,
                "bbox": [x0, y0, x1, y1],
                "text": re.sub(r"\s+", " ", txt)
            })
    doc.close()

    # heuristic: join very small blocks that are consecutive on same page
    merged: List[Dict] = []
    for b in blocks:
        if merged and b["page"] == merged[-1]["page"] and (b["bbox"][1] - merged[-1]["bbox"][3]) < 8:
            merged[-1]["text"] += " " + b["text"]
        else:
            merged.append(b)
    return merged
