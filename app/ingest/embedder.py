from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        embs = self.model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True)
        return np.array(embs, dtype=np.float32)
