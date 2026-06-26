import pytest
from feedpulse.retrieval.bm25 import BM25Okapi, tokenize

def test_tokenizer_filters_stopwords():
    tokens = tokenize("This is a major critical crash in the WebGL canvas engine")
    assert "this" not in tokens
    assert "is" not in tokens
    assert "the" not in tokens
    assert "crash" in tokens
    assert "webgl" in tokens

def test_bm25_fit_and_query():
    doc_ids = ["DOC-1", "DOC-2", "DOC-3"]
    docs = [
        "WebGL canvas context lost and black screen on Apple M2",
        "SAML SSO infinite redirect loop between Okta and auth server",
        "Billing invoice shows wrong currency on annual Stripe renewal"
    ]
    bm25 = BM25Okapi()
    bm25.fit(doc_ids, docs)

    results = bm25.query("WebGL canvas crash", top_k=2)
    assert len(results) > 0
    top_doc_id, score, matched = results[0]
    assert top_doc_id == "DOC-1"
    assert "webgl" in matched or "canvas" in matched
    assert score > 0.0
