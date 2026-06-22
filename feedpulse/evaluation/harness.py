import time
import numpy as np
from typing import List, Dict, Any
from feedpulse.schemas.models import (
    SearchRequest,
    EvalCase,
    EvalMetricScores,
    BenchmarkReport,
    ThemeCluster,
    UrgencyLevel
)
from feedpulse.retrieval.hybrid_engine import HybridRetrievalPipeline
from feedpulse.analytics.synthesizer import ClusterInsightSynthesizer
from feedpulse.evaluation.benchmark_cases import BENCHMARK_CASES
from feedpulse.evaluation.metrics import (
    extract_claims,
    compute_faithfulness,
    compute_context_precision,
    compute_context_recall,
    compute_urgency_accuracy
)
from feedpulse.config import settings

class FeedbackEvalHarness:
    """
    Automated evaluation harness matching Enterpret's AI feature quality evaluation suite.
    Runs regression rubrics across ground-truth test cases and enforces quality gates.
    """
    def __init__(self, retrieval_pipeline: HybridRetrievalPipeline):
        self.retrieval = retrieval_pipeline
        self.synthesizer = ClusterInsightSynthesizer()

    def run_benchmark(self, cases: List[EvalCase] = BENCHMARK_CASES) -> BenchmarkReport:
        """Execute full regression test suite across benchmark cases."""
        scores: List[EvalMetricScores] = []
        latencies: List[float] = []

        for case in cases:
            start_time = time.perf_counter()

            # 1. Execute Hybrid Retrieval
            search_req = SearchRequest(query=case.query, top_k=5, alpha=settings.DEFAULT_HYBRID_ALPHA)
            search_results = self.retrieval.search(search_req)
            retrieved_ids = [r.item.id for r in search_results]
            retrieved_context = " ".join([f"{r.item.product_area} {r.item.text}" for r in search_results])

            # 2. Extract predicted urgency
            pred_urgency = search_results[0].item.urgency if search_results else UrgencyLevel.MEDIUM

            # 3. Simulate synthesis and extract factual claims regarding customer issue
            temp_cluster = ThemeCluster(
                cluster_id=99,
                theme_name=case.expected_theme,
                frequency=len(search_results),
                avg_sentiment=-0.75,
                primary_urgency=pred_urgency,
                top_keywords=[w for w in case.query.lower().split() if len(w) > 3][:5],
                sample_items=[r.item for r in search_results]
            )
            synthesis = self.synthesizer.synthesize(temp_cluster)
            claims = extract_claims(f"{synthesis.theme_name}. {synthesis.root_cause}")

            # 4. Compute Quality Rubrics
            faithfulness = compute_faithfulness(claims, retrieved_context)
            context_precision = compute_context_precision(retrieved_ids, case.expected_item_ids, k=5)
            context_recall = compute_context_recall(retrieved_ids, case.expected_item_ids)
            urgency_acc = compute_urgency_accuracy(pred_urgency, case.ground_truth_urgency)
            hallucination_rate = round(1.0 - faithfulness, 4)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            latencies.append(elapsed_ms)

            case_passed = (
                faithfulness >= (settings.MIN_FAITHFULNESS - 0.05) and
                context_recall >= (settings.MIN_CONTEXT_RECALL - 0.10)
            )

            scores.append(EvalMetricScores(
                case_id=case.case_id,
                query=case.query,
                faithfulness=faithfulness,
                context_precision=context_precision,
                context_recall=context_recall,
                urgency_accuracy=urgency_acc,
                hallucination_rate=hallucination_rate,
                latency_ms=round(elapsed_ms, 2),
                passed_gate=case_passed
            ))

        # Aggregate metrics
        avg_faithfulness = round(float(np.mean([s.faithfulness for s in scores])), 4)
        avg_precision = round(float(np.mean([s.context_precision for s in scores])), 4)
        avg_recall = round(float(np.mean([s.context_recall for s in scores])), 4)
        avg_urgency = round(float(np.mean([s.urgency_accuracy for s in scores])), 4)
        avg_hallucination = round(float(np.mean([s.hallucination_rate for s in scores])), 4)
        p50_lat = round(float(np.percentile(latencies, 50)), 2)
        p95_lat = round(float(np.percentile(latencies, 95)), 2)

        # Evaluate Strict Quality Gate
        gate_passed = (
            avg_faithfulness >= settings.MIN_FAITHFULNESS and
            avg_recall >= settings.MIN_CONTEXT_RECALL and
            avg_precision >= settings.MIN_CONTEXT_PRECISION and
            avg_hallucination <= settings.MAX_HALLUCINATION_RATE
        )

        quality_details = {
            "faithfulness_gate": {
                "threshold": settings.MIN_FAITHFULNESS,
                "achieved": avg_faithfulness,
                "passed": avg_faithfulness >= settings.MIN_FAITHFULNESS
            },
            "context_recall_gate": {
                "threshold": settings.MIN_CONTEXT_RECALL,
                "achieved": avg_recall,
                "passed": avg_recall >= settings.MIN_CONTEXT_RECALL
            },
            "context_precision_gate": {
                "threshold": settings.MIN_CONTEXT_PRECISION,
                "achieved": avg_precision,
                "passed": avg_precision >= settings.MIN_CONTEXT_PRECISION
            },
            "hallucination_gate": {
                "threshold": settings.MAX_HALLUCINATION_RATE,
                "achieved": avg_hallucination,
                "passed": avg_hallucination <= settings.MAX_HALLUCINATION_RATE
            }
        }

        return BenchmarkReport(
            total_cases=len(cases),
            overall_faithfulness=avg_faithfulness,
            overall_context_precision=avg_precision,
            overall_context_recall=avg_recall,
            overall_urgency_accuracy=avg_urgency,
            overall_hallucination_rate=avg_hallucination,
            p50_latency_ms=p50_lat,
            p95_latency_ms=p95_lat,
            quality_gate_passed=gate_passed,
            quality_gate_details=quality_details,
            individual_results=scores
        )
