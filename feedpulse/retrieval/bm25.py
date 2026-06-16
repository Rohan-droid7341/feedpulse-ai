import re
import math
from typing import List, Dict, Set, Tuple

STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

def tokenize(text: str) -> List[str]:
    """Tokenize, lowercase, strip punctuation, and filter stop words."""
    tokens = re.findall(r"\b[a-zA-Z0-9_\-\$]{2,}\b", text.lower())
    return [t for t in tokens if t not in STOP_WORDS]

class BM25Okapi:
    """
    Production-grade BM25Okapi sparse search engine.
    Matches Enterpret's keyword search layer for exact match and error code queries.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size: int = 0
        self.avgdl: float = 0.0
        self.doc_lengths: List[int] = []
        self.doc_ids: List[str] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def fit(self, doc_ids: List[str], documents: List[str]) -> "BM25Okapi":
        """Index a collection of documents."""
        self.doc_ids = doc_ids
        self.corpus_size = len(documents)
        self.doc_tokens = [tokenize(doc) for doc in documents]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avgdl = (sum(self.doc_lengths) / self.corpus_size) if self.corpus_size > 0 else 0.0

        # Compute document frequencies
        self.doc_freqs.clear()
        for tokens in self.doc_tokens:
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        # Compute Robertson-Spärck Jones IDF with smoothing
        self.idf.clear()
        for term, freq in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

        return self

    def score(self, query_tokens: List[str], doc_idx: int) -> float:
        """Compute BM25 score for a specific document index against query tokens."""
        doc_len = self.doc_lengths[doc_idx]
        tokens = self.doc_tokens[doc_idx]
        if doc_len == 0 or self.avgdl == 0:
            return 0.0

        term_freqs: Dict[str, int] = {}
        for t in tokens:
            term_freqs[t] = term_freqs.get(t, 0) + 1

        score = 0.0
        for token in query_tokens:
            if token not in self.idf:
                continue
            tf = term_freqs.get(token, 0)
            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
            score += self.idf[token] * (numerator / denominator)

        return score

    def query(self, query_text: str, top_k: int = 10) -> List[Tuple[str, float, List[str]]]:
        """
        Query the index.
        Returns list of (doc_id, score, matched_tokens).
        """
        query_tokens = tokenize(query_text)
        if not query_tokens or self.corpus_size == 0:
            return []

        scores: List[Tuple[str, float, List[str]]] = []
        for idx, doc_id in enumerate(self.doc_ids):
            s = self.score(query_tokens, idx)
            matched = [t for t in set(query_tokens) if t in self.doc_tokens[idx]]
            scores.append((doc_id, s, matched))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
