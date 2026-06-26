import pytest
from feedpulse.schemas.models import UrgencyLevel
from feedpulse.evaluation.metrics import (
    extract_claims,
    compute_faithfulness,
    compute_context_precision,
    compute_context_recall,
    compute_urgency_accuracy
)

def test_extract_claims():
    text = "The WebGL canvas crashes on Apple Silicon M2. Chrome allocates 4GB memory then freezes; users are blocked."
    claims = extract_claims(text)
    assert len(claims) >= 2

def test_compute_faithfulness():
    context = "WebGL canvas context lost and black screen crash on Apple Silicon M2 MacBook Pro during zoom."
    grounded_claims = [
        "WebGL canvas context lost on Apple Silicon M2.",
        "Black screen crash occurred during zoom on MacBook Pro."
    ]
    score = compute_faithfulness(grounded_claims, context)
    assert score >= 0.85

def test_context_precision_and_recall():
    retrieved = ["FB-1", "FB-2", "FB-3", "FB-4", "FB-5"]
    ground_truth = ["FB-1", "FB-2", "FB-3"]

    precision = compute_context_precision(retrieved, ground_truth, k=5)
    recall = compute_context_recall(retrieved, ground_truth)

    assert precision == 0.60
    assert recall == 1.00

def test_urgency_accuracy():
    assert compute_urgency_accuracy(UrgencyLevel.CRITICAL, UrgencyLevel.CRITICAL) == 1.0
    assert compute_urgency_accuracy(UrgencyLevel.CRITICAL, UrgencyLevel.HIGH) == 0.67
    assert compute_urgency_accuracy(UrgencyLevel.CRITICAL, UrgencyLevel.LOW) == 0.0
