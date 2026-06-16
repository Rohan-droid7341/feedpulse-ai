import re
import math
from typing import List, Tuple, Dict, Optional
import numpy as np
from feedpulse.retrieval.bm25 import tokenize

class SemanticEmbeddingEngine:
    """
    High-performance semantic vector embedding engine.
    Computes sublinear TF-IDF and L2-normalized dense vector representations in pure NumPy.
    Self-contained, fast, and immune to external C-extension or PyTorch dependencies.
    """
    def __init__(self, n_components: int = 64):
        self.n_components = n_components
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_ids: List[str] = []
        self.doc_embeddings: Optional[np.ndarray] = None
        self.is_fitted: bool = False

    def fit_transform(self, doc_ids: List[str], documents: List[str]) -> np.ndarray:
        """Compute normalized vector embeddings for a corpus of documents."""
        self.doc_ids = doc_ids
        n_docs = len(documents)

        # 1. Build vocabulary and document frequencies
        doc_tokens_list = [tokenize(doc) for doc in documents]
        df_counts: Dict[str, int] = {}
        for tokens in doc_tokens_list:
            for term in set(tokens):
                df_counts[term] = df_counts.get(term, 0) + 1

        # Retain terms that appear in at least 1 document, sorted by frequency
        sorted_terms = sorted(df_counts.keys(), key=lambda t: df_counts[t], reverse=True)
        self.vocabulary = {term: idx for idx, term in enumerate(sorted_terms)}

        # 2. Compute smooth IDF: ln((N + 1) / (df + 1)) + 1
        self.idf = {
            term: math.log((n_docs + 1.0) / (df_counts[term] + 1.0)) + 1.0
            for term in self.vocabulary
        }

        # 3. Build TF-IDF matrix
        vocab_size = len(self.vocabulary)
        matrix = np.zeros((n_docs, vocab_size), dtype=np.float32)

        for doc_idx, tokens in enumerate(doc_tokens_list):
            counts: Dict[str, int] = {}
            for t in tokens:
                if t in self.vocabulary:
                    counts[t] = counts.get(t, 0) + 1
            for t, count in counts.items():
                col_idx = self.vocabulary[t]
                # Sublinear TF scaling: 1 + ln(count)
                sublinear_tf = 1.0 + math.log(count)
                matrix[doc_idx, col_idx] = sublinear_tf * self.idf[t]

        # 4. L2-Normalize each document vector
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.doc_embeddings = matrix / norms

        self.is_fitted = True
        return self.doc_embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a search query into normalized semantic vector space."""
        if not self.is_fitted or not self.vocabulary:
            raise RuntimeError("Embedding engine has not been fitted to any corpus.")

        tokens = tokenize(query)
        vec = np.zeros(len(self.vocabulary), dtype=np.float32)

        counts: Dict[str, int] = {}
        for t in tokens:
            if t in self.vocabulary:
                counts[t] = counts.get(t, 0) + 1

        for t, count in counts.items():
            col_idx = self.vocabulary[t]
            sublinear_tf = 1.0 + math.log(count)
            vec[col_idx] = sublinear_tf * self.idf[t]

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm

        return vec

    def similarity_search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Cosine similarity search over document embeddings.
        Returns list of (doc_id, scaled_score) sorted descending.
        """
        if not self.is_fitted or self.doc_embeddings is None:
            return []

        query_vec = self.embed_query(query)
        # Cosine similarity is dot product of normalized vectors
        cosine_scores = np.dot(self.doc_embeddings, query_vec)

        # Scale to 0.0 - 1.0 range
        scaled = np.clip((cosine_scores + 1.0) / 2.0, 0.0, 1.0)

        results = [(self.doc_ids[i], float(scaled[i])) for i in range(len(self.doc_ids))]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
