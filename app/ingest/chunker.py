from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_blocks(blocks: List[Dict], max_chars: int = 1200, overlap: int = 200) -> List[Dict]:
    texts = [b["text"] for b in blocks]
    joined = "\n".join(texts)
    splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=overlap)
    chunks = splitter.split_text(joined)
    return [{"text": c, "meta": {"len": len(c)}} for c in chunks]
