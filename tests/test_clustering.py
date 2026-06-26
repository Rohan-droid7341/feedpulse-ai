import pytest
from feedpulse.schemas.models import FeedbackItem, FeedbackSource, UrgencyLevel, SentimentType
from feedpulse.analytics.clusterer import FeedbackThemeClusterer

def test_theme_clustering():
    items = [
        FeedbackItem(
            id=f"FB-CANVAS-{i}",
            text=f"WebGL canvas rendering failure and crash on macOS tab {i}",
            source=FeedbackSource.DISCORD,
            author=f"user_{i}",
            urgency=UrgencyLevel.CRITICAL,
            sentiment=SentimentType.NEGATIVE,
            sentiment_score=-0.8,
            product_area="Canvas",
            timestamp="2026-06-01T00:00:00Z"
        )
        for i in range(4)
    ] + [
        FeedbackItem(
            id=f"FB-AUTH-{i}",
            text=f"SAML SSO infinite redirect loop on Okta login {i}",
            source=FeedbackSource.ZENDESK,
            author=f"admin_{i}",
            urgency=UrgencyLevel.CRITICAL,
            sentiment=SentimentType.NEGATIVE,
            sentiment_score=-0.9,
            product_area="Authentication",
            timestamp="2026-06-02T00:00:00Z"
        )
        for i in range(4)
    ]

    clusterer = FeedbackThemeClusterer()
    clusters = clusterer.cluster_feedback(items, n_clusters=2)

    assert len(clusters) == 2
    assert sum(c.frequency for c in clusters) == 8
