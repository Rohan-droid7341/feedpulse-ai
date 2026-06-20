from collections import Counter
from typing import List, Dict
import numpy as np
from feedpulse.schemas.models import FeedbackItem, ThemeCluster, UrgencyLevel
from feedpulse.retrieval.bm25 import tokenize
from feedpulse.retrieval.embeddings import SemanticEmbeddingEngine

THEME_NAME_MAPPINGS = {
    "canvas": "WebGL Canvas Metal Backend Crashes",
    "webgl": "WebGL Context Loss & GPU Freezes",
    "saml": "SAML 2.0 / Okta SSO Infinite Redirect Loops",
    "auth": "Enterprise SSO & Authentication Timeouts",
    "katex": "Markdown Exporter Stripping Math Equations",
    "math": "LaTeX & KaTeX Formula Disappearance",
    "billing": "Multi-Currency Stripe Billing & Duplicate Invoices",
    "invoice": "Currency Conversion & Renewal Invoicing Failures",
    "battery": "Mobile Background Sync CPU & Battery Drain",
    "mobile": "iOS/Android WorkManager Thread Lock Contention",
    "cursor": "Multiplayer Canvas Cursor Jitter & Latency",
    "collaboration": "WebSocket Realtime Collaboration Dropped Frames",
    "search": "Elasticsearch Document Indexing Queue Stalls",
    "contrast": "Dark Theme WCAG AA Contrast Ratio Deficiencies"
}

class FeedbackThemeClusterer:
    """
    Unsupervised semantic theme clustering engine.
    Partitions raw customer feedback into cohesive product issue clusters using pure NumPy K-Means.
    """
    def __init__(self, default_n_clusters: int = 6):
        self.default_n_clusters = default_n_clusters

    def cluster_feedback(self, items: List[FeedbackItem], n_clusters: int = 6) -> List[ThemeCluster]:
        """Cluster items and compute theme summaries."""
        if not items:
            return []

        actual_k = min(n_clusters, len(items))
        if actual_k < 2:
            return [self._create_single_cluster(0, items)]

        # Prepare text features
        corpus = [f"{item.product_area} {item.text}" for item in items]
        embedder = SemanticEmbeddingEngine()
        vectors = embedder.fit_transform([item.id for item in items], corpus)

        # Run pure NumPy K-Means with deterministic seed
        labels = self._run_kmeans(vectors, k=actual_k, max_iters=25, seed=42)

        cluster_groups: Dict[int, List[FeedbackItem]] = {}
        for idx, label in enumerate(labels):
            cluster_groups.setdefault(int(label), []).append(items[idx])

        theme_clusters: List[ThemeCluster] = []
        for cluster_id, group_items in sorted(cluster_groups.items(), key=lambda x: len(x[1]), reverse=True):
            # Compute top keywords
            all_tokens = []
            for item in group_items:
                all_tokens.extend(tokenize(item.text))
            top_kw_counts = Counter(all_tokens).most_common(5)
            top_keywords = [kw for kw, _ in top_kw_counts]

            # Determine human-readable theme name
            theme_name = self._infer_theme_name(group_items, top_keywords)

            # Metrics
            avg_sentiment = sum(it.sentiment_score for it in group_items) / len(group_items)
            urgency_counts = Counter(it.urgency for it in group_items)
            primary_urgency = urgency_counts.most_common(1)[0][0]

            theme_clusters.append(ThemeCluster(
                cluster_id=cluster_id,
                theme_name=theme_name,
                frequency=len(group_items),
                avg_sentiment=round(avg_sentiment, 2),
                primary_urgency=primary_urgency,
                top_keywords=top_keywords,
                sample_items=group_items[:4]
            ))

        return theme_clusters

    def _run_kmeans(self, vectors: np.ndarray, k: int, max_iters: int = 25, seed: int = 42) -> np.ndarray:
        """Deterministic K-Means on cosine-normalized vectors."""
        np.random.seed(seed)
        n_samples = vectors.shape[0]

        # Initialize centroids by picking evenly spaced samples
        step = max(1, n_samples // k)
        init_indices = [(i * step) % n_samples for i in range(k)]
        centroids = vectors[init_indices].copy()

        labels = np.zeros(n_samples, dtype=int)
        for _ in range(max_iters):
            # Cosine distance = 1 - dot product (vectors are normalized)
            similarities = np.dot(vectors, centroids.T)
            new_labels = np.argmax(similarities, axis=1)

            if np.array_equal(new_labels, labels):
                break
            labels = new_labels

            # Update centroids
            for cluster_idx in range(k):
                members = vectors[labels == cluster_idx]
                if len(members) > 0:
                    mean_vec = np.mean(members, axis=0)
                    norm = np.linalg.norm(mean_vec)
                    centroids[cluster_idx] = mean_vec / (norm if norm > 0 else 1.0)

        return labels

    def _infer_theme_name(self, items: List[FeedbackItem], top_keywords: List[str]) -> str:
        """Infer high-signal title based on product area and top keywords."""
        combined_text = " ".join([it.product_area.lower() for it in items] + top_keywords).lower()
        for key, title in THEME_NAME_MAPPINGS.items():
            if key in combined_text:
                return title

        areas = Counter(it.product_area for it in items)
        dom_area = areas.most_common(1)[0][0]
        kw_phrase = " / ".join(top_keywords[:2]).title()
        return f"{dom_area}: {kw_phrase}"

    def _create_single_cluster(self, cluster_id: int, items: List[FeedbackItem]) -> ThemeCluster:
        all_tokens = []
        for it in items:
            all_tokens.extend(tokenize(it.text))
        top_keywords = [k for k, _ in Counter(all_tokens).most_common(5)]
        avg_sentiment = sum(it.sentiment_score for it in items) / len(items) if items else 0.0

        return ThemeCluster(
            cluster_id=cluster_id,
            theme_name="General Feedback Cluster",
            frequency=len(items),
            avg_sentiment=round(avg_sentiment, 2),
            primary_urgency=UrgencyLevel.MEDIUM,
            top_keywords=top_keywords,
            sample_items=items
        )
