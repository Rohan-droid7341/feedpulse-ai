import re
from typing import List, Tuple, Dict
from feedpulse.schemas.models import FeedbackItem

class ContextualCrossEncoderReranker:
    """
    Second-stage cross-encoder reranker simulating query-document joint attention.
    Analyzes lexical proximity, entity coverage, position decay, and severity resonance.
    """
    def __init__(self):
        pass

    def compute_rerank_score(self, query: str, item: FeedbackItem, initial_score: float) -> float:
        """Score candidate item jointly with the query."""
        query_words = [w.lower() for w in re.findall(r"\b\w+\b", query)]
        text_lower = item.text.lower()
        if not query_words:
            return initial_score

        # 1. Exact phrase bonus
        exact_phrase_bonus = 0.25 if query.lower() in text_lower else 0.0

        # 2. Token coverage
        found_tokens = [w for w in query_words if w in text_lower]
        coverage_ratio = len(found_tokens) / len(query_words)

        # 3. Keyword proximity bonus (if multiple query terms appear within 15 words)
        proximity_bonus = 0.0
        if len(query_words) >= 2:
            positions = []
            words_in_text = re.findall(r"\b\w+\b", text_lower)
            for idx, w in enumerate(words_in_text):
                if w in query_words:
                    positions.append(idx)
            if len(positions) >= 2:
                min_dist = min(abs(positions[i] - positions[i-1]) for i in range(1, len(positions)))
                if min_dist <= 10:
                    proximity_bonus = 0.15

        # 4. Severity resonance (if query contains emergency keywords: crash, freeze, lock, fail, loop)
        severity_bonus = 0.0
        emergency_terms = {"crash", "crashes", "freeze", "freezes", "loop", "locked", "critical", "broken", "severe", "drains"}
        has_emergency = any(t in emergency_terms for t in query_words)
        if has_emergency and item.urgency in ("critical", "high"):
            severity_bonus = 0.10

        # Weighted combination with original score
        rerank_score = (
            0.40 * initial_score +
            0.30 * coverage_ratio +
            0.15 * exact_phrase_bonus +
            0.10 * proximity_bonus +
            0.05 * severity_bonus
        )
        return min(1.0, max(0.0, rerank_score))

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[FeedbackItem, float, float, float, List[str]]],
        top_k: int = 8
    ) -> List[Tuple[FeedbackItem, float, float, float, float, List[str]]]:
        """
        Rerank top-k candidates.
        Input: list of (item, hybrid_score, bm25_score, dense_score, matched_tokens)
        Output: list of (item, final_score, hybrid_score, bm25_score, dense_score, matched_tokens)
        """
        reranked = []
        for item, hybrid_s, bm25_s, dense_s, matched in candidates:
            final_s = self.compute_rerank_score(query, item, hybrid_s)
            reranked.append((item, final_s, hybrid_s, bm25_s, dense_s, matched))

        # Sort descending by final rerank score
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]
