import pytest
from feedpulse.schemas.models import (
    FeedbackItem,
    FeedbackSource,
    UrgencyLevel,
    SentimentType,
    SearchRequest,
    SearchFilter
)
from feedpulse.retrieval.hybrid_engine import HybridRetrievalPipeline

@pytest.fixture
def sample_items():
    return [
        FeedbackItem(
            id="FB-1",
            text="WebGL context crash on macOS Chrome M2 graphics",
            source=FeedbackSource.DISCORD,
            author="u1",
            urgency=UrgencyLevel.CRITICAL,
            sentiment=SentimentType.NEGATIVE,
            sentiment_score=-0.9,
            product_area="Canvas",
            timestamp="2026-06-01T00:00:00Z"
        ),
        FeedbackItem(
            id="FB-2",
            text="Okta SAML 2.0 redirect loop on login timeout",
            source=FeedbackSource.ZENDESK,
            author="u2",
            urgency=UrgencyLevel.CRITICAL,
            sentiment=SentimentType.NEGATIVE,
            sentiment_score=-0.8,
            product_area="Authentication",
            timestamp="2026-06-02T00:00:00Z"
        ),
        FeedbackItem(
            id="FB-3",
            text="Markdown export erases LaTeX KaTeX equations",
            source=FeedbackSource.GITHUB,
            author="u3",
            urgency=UrgencyLevel.MEDIUM,
            sentiment=SentimentType.NEGATIVE,
            sentiment_score=-0.5,
            product_area="Export",
            timestamp="2026-06-03T00:00:00Z"
        )
    ]

def test_hybrid_pipeline_search(sample_items):
    pipeline = HybridRetrievalPipeline()
    pipeline.index(sample_items)

    req = SearchRequest(query="WebGL graphics crash on Mac", top_k=2, enable_reranking=True)
    results = pipeline.search(req)

    assert len(results) > 0
    assert results[0].item.id == "FB-1"
    assert results[0].hybrid_score > 0.0

def test_hybrid_pipeline_filtering(sample_items):
    pipeline = HybridRetrievalPipeline()
    pipeline.index(sample_items)

    req = SearchRequest(
        query="crash or error",
        top_k=5,
        filters=SearchFilter(sources=[FeedbackSource.ZENDESK])
    )
    results = pipeline.search(req)

    for r in results:
        assert r.item.source == FeedbackSource.ZENDESK
