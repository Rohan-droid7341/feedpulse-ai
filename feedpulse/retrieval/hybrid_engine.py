from typing import List, Dict, Optional
from feedpulse.schemas.models import (
    FeedbackItem,
    SearchFilter,
    SearchRequest,
    HybridSearchResult
)
from .bm25 import BM25Okapi, tokenize
from .embeddings import SemanticEmbeddingEngine
from .reranker import ContextualCrossEncoderReranker

class HybridRetrievalPipeline:
    """
    Enterprise Hybrid Retrieval Pipeline combining:
    1. BM25Okapi Sparse Inverted Index (lexical match)
    2. Dense Latent Semantic Embeddings (semantic intent)
    3. Reciprocal Rank Fusion / Convex Alpha Weighting
    4. Cross-Encoder Second-Stage Reranking
    """
    def __init__(self, default_alpha: float = 0.55):
        self.default_alpha = default_alpha
        self.bm25 = BM25Okapi()
        self.embedding_engine = SemanticEmbeddingEngine()
        self.reranker = ContextualCrossEncoderReranker()
        self.items_by_id: Dict[str, FeedbackItem] = {}

    def index(self, items: List[FeedbackItem]):
        """Index or update customer feedback collection."""
        self.items_by_id = {item.id: item for item in items}
        doc_ids = [item.id for item in items]
        documents = [f"{item.product_area} | {item.text}" for item in items]

        self.bm25.fit(doc_ids, documents)
        self.embedding_engine.fit_transform(doc_ids, documents)

    def search(self, request: SearchRequest) -> List[HybridSearchResult]:
        """Execute two-stage hybrid search with optional metadata filtering."""
        if not self.items_by_id:
            return []

        query = request.query
        alpha = request.alpha if request.alpha is not None else self.default_alpha

        # Stage 1A: BM25 Sparse Search
        bm25_results = self.bm25.query(query, top_k=len(self.items_by_id))
        bm25_dict = {doc_id: (score, matched) for doc_id, score, matched in bm25_results}
        max_bm25 = max([s for s, _ in bm25_dict.values()], default=1.0)
        max_bm25 = max(max_bm25, 0.001)

        # Stage 1B: Dense Semantic Vector Search
        dense_results = self.embedding_engine.similarity_search(query, top_k=len(self.items_by_id))
        dense_dict = {doc_id: score for doc_id, score in dense_results}

        # Stage 1C: Convex Hybrid Fusion
        candidate_tuples = []
        for doc_id, item in self.items_by_id.items():
            # Apply metadata filters
            if not self._passes_filter(item, request.filters):
                continue

            bm25_raw, matched = bm25_dict.get(doc_id, (0.0, []))
            normalized_bm25 = bm25_raw / max_bm25
            dense_score = dense_dict.get(doc_id, 0.0)

            hybrid_score = (alpha * dense_score) + ((1.0 - alpha) * normalized_bm25)

            # Only retain candidates with non-trivial relevance
            if hybrid_score > 0.05 or normalized_bm25 > 0.1:
                candidate_tuples.append((item, hybrid_score, normalized_bm25, dense_score, matched))

        # Sort candidate pool
        candidate_tuples.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidate_tuples[:max(request.top_k * 2, 10)]

        # Stage 2: Second-stage Cross-Encoder Reranking
        if request.enable_reranking and top_candidates:
            reranked = self.reranker.rerank(query, top_candidates, top_k=request.top_k)
            results = [
                HybridSearchResult(
                    item=item,
                    hybrid_score=round(final_s, 4),
                    bm25_score=round(bm25_s, 4),
                    dense_score=round(dense_s, 4),
                    rerank_score=round(final_s, 4),
                    matched_tokens=matched
                )
                for item, final_s, hybrid_s, bm25_s, dense_s, matched in reranked
            ]
        else:
            results = [
                HybridSearchResult(
                    item=item,
                    hybrid_score=round(hybrid_s, 4),
                    bm25_score=round(bm25_s, 4),
                    dense_score=round(dense_s, 4),
                    rerank_score=round(hybrid_s, 4),
                    matched_tokens=matched
                )
                for item, hybrid_s, bm25_s, dense_s, matched in top_candidates[:request.top_k]
            ]

        return results

    def _passes_filter(self, item: FeedbackItem, filters: Optional[SearchFilter]) -> bool:
        """Evaluate item against metadata constraints."""
        if not filters:
            return True

        if filters.sources and item.source not in filters.sources:
            return False
        if filters.urgencies and item.urgency not in filters.urgencies:
            return False
        if filters.sentiments and item.sentiment not in filters.sentiments:
            return False
        if filters.product_areas and item.product_area not in filters.product_areas:
            return False

        return True
