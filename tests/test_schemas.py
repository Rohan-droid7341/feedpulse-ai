import pytest
from feedpulse.schemas.models import (
    FeedbackItem,
    FeedbackSource,
    UrgencyLevel,
    SentimentType,
    SearchRequest
)

def test_feedback_item_validation():
    item = FeedbackItem(
        id="FB-TEST-1",
        text="Canvas WebGL crash on Apple M1 Max",
        source=FeedbackSource.DISCORD,
        author="tester@enterprise.com",
        urgency=UrgencyLevel.CRITICAL,
        sentiment=SentimentType.NEGATIVE,
        sentiment_score=-0.85,
        product_area="Canvas",
        timestamp="2026-06-15T10:00:00Z",
        metadata={"os": "macOS"}
    )
    assert item.id == "FB-TEST-1"
    assert item.urgency == UrgencyLevel.CRITICAL
    assert item.sentiment_score == -0.85

def test_search_request_defaults():
    req = SearchRequest(query="SAML SSO redirect loop")
    assert req.top_k == 8
    assert req.alpha == 0.55
    assert req.enable_reranking is True
