import re
from typing import List, Set
from feedpulse.schemas.models import UrgencyLevel

URGENCY_RANK = {
    UrgencyLevel.LOW: 0,
    UrgencyLevel.MEDIUM: 1,
    UrgencyLevel.HIGH: 2,
    UrgencyLevel.CRITICAL: 3
}

def extract_claims(text: str) -> List[str]:
    """Break synthesized prose into atomic propositional claims."""
    # Split by periods, semicolons, and commas in compound clauses
    sentences = re.split(r"[.;\n]+", text)
    claims = [s.strip() for s in sentences if len(s.strip()) > 10]
    return claims

def compute_faithfulness(claims: List[str], context_text: str) -> float:
    """
    Measures ratio of factual claims grounded in the retrieved customer feedback context.
    Matches Ragas / DeepEval faithfulness formulation: |Grounded Claims| / |Total Claims|.
    """
    if not claims:
        return 1.0

    context_lower = context_text.lower()
    context_words = set(re.findall(r"\b\w{3,}\b", context_lower))

    grounded_count = 0
    for claim in claims:
        claim_words = set(re.findall(r"\b\w{3,}\b", claim.lower()))
        if not claim_words:
            grounded_count += 1
            continue
        # Check token overlap ratio
        overlap = len(claim_words.intersection(context_words)) / len(claim_words)
        if overlap >= 0.40:
            grounded_count += 1

    return round(grounded_count / len(claims), 4)

def compute_context_precision(retrieved_ids: List[str], ground_truth_ids: List[str], k: int = 5) -> float:
    """
    Calculates precision@k: proportion of retrieved context items that are relevant ground-truth items.
    """
    if not ground_truth_ids or not retrieved_ids:
        return 0.0

    top_k_retrieved = retrieved_ids[:k]
    gt_set = set(ground_truth_ids)

    relevant_hits = sum(1 for doc_id in top_k_retrieved if doc_id in gt_set)
    return round(relevant_hits / len(top_k_retrieved), 4)

def compute_context_recall(retrieved_ids: List[str], ground_truth_ids: List[str]) -> float:
    """
    Calculates recall: fraction of ground truth feedback items captured in retrieved context.
    """
    if not ground_truth_ids:
        return 1.0
    if not retrieved_ids:
        return 0.0

    retrieved_set = set(retrieved_ids)
    hits = sum(1 for gt_id in ground_truth_ids if gt_id in retrieved_set)
    return round(hits / len(ground_truth_ids), 4)

def compute_urgency_accuracy(predicted_urgency: UrgencyLevel, ground_truth_urgency: UrgencyLevel) -> float:
    """
    Computes calibrated distance score between predicted and ground-truth urgency.
    Exact match = 1.0, 1 level off = 0.67, 2 levels off = 0.33, 3 levels off = 0.0.
    """
    pred_rank = URGENCY_RANK.get(predicted_urgency, 1)
    gt_rank = URGENCY_RANK.get(ground_truth_urgency, 1)
    diff = abs(pred_rank - gt_rank)

    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.67
    elif diff == 2:
        return 0.33
    return 0.0
