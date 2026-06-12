from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FeedbackSource(str, Enum):
    ZENDESK = "zendesk"
    DISCORD = "discord"
    APP_STORE = "app_store"
    GITHUB = "github"
    G2_REVIEWS = "g2_reviews"
    CUSTOMER_SURVEY = "customer_survey"

class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SentimentType(str, Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"

class FeedbackItem(BaseModel):
    """Core customer feedback unit matching Enterpret's multi-source ingestion layer."""
    id: str = Field(..., description="Unique deterministic identifier (e.g. FB-1001)")
    text: str = Field(..., description="Raw text of the customer feedback, review, or ticket")
    source: FeedbackSource = Field(..., description="Originating ingestion channel")
    author: str = Field(..., description="Customer, reviewer, or enterprise user identifier")
    urgency: UrgencyLevel = Field(..., description="Assessed issue urgency")
    sentiment: SentimentType = Field(..., description="Sentiment classification")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Continuous sentiment polarity (-1.0 to 1.0)")
    product_area: str = Field(..., description="Feature area (e.g. Canvas, Auth, Billing, Mobile)")
    timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom channel metadata (e.g. app version, plan tier)")

class SearchFilter(BaseModel):
    sources: Optional[List[FeedbackSource]] = None
    urgencies: Optional[List[UrgencyLevel]] = None
    sentiments: Optional[List[SentimentType]] = None
    product_areas: Optional[List[str]] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search or semantic inquiry")
    top_k: int = Field(default=8, ge=1, le=50)
    alpha: float = Field(default=0.55, ge=0.0, le=1.0, description="Dense vs sparse weight (1=Dense, 0=BM25)")
    filters: Optional[SearchFilter] = None
    enable_reranking: bool = Field(default=True, description="Apply second-stage cross-encoder reranking")

class HybridSearchResult(BaseModel):
    item: FeedbackItem
    hybrid_score: float = Field(..., description="Final fused ranking score")
    bm25_score: float = Field(..., description="Normalized sparse keyword score")
    dense_score: float = Field(..., description="Dense semantic cosine similarity")
    rerank_score: float = Field(..., description="Cross-encoder relevance score")
    matched_tokens: List[str] = Field(default_factory=list, description="Extracted keywords found in text")

class ThemeCluster(BaseModel):
    cluster_id: int
    theme_name: str
    frequency: int
    avg_sentiment: float
    primary_urgency: UrgencyLevel
    top_keywords: List[str]
    sample_items: List[FeedbackItem]
    root_cause_analysis: Optional[str] = None
    suggested_action: Optional[str] = None

class ClusterRequest(BaseModel):
    n_clusters: Optional[int] = Field(default=6, ge=2, le=12, description="Target number of themes to discover")

class SynthesisRequest(BaseModel):
    cluster_id: int
    focus_prompt: Optional[str] = None

class ClusterSynthesis(BaseModel):
    cluster_id: int
    theme_name: str
    ticket_count: int
    root_cause: str
    customer_impact: str
    engineering_action_plan: str
    affected_components: List[str]
    generated_at: str

class EvalCase(BaseModel):
    case_id: str
    query: str
    expected_theme: str
    expected_item_ids: List[str]
    ground_truth_summary: str
    ground_truth_urgency: UrgencyLevel

class EvalMetricScores(BaseModel):
    case_id: str
    query: str
    faithfulness: float = Field(..., ge=0.0, le=1.0, description="Ratio of claims grounded in retrieved context")
    context_precision: float = Field(..., ge=0.0, le=1.0, description="Relevance quality of retrieved top-K context")
    context_recall: float = Field(..., ge=0.0, le=1.0, description="Coverage of ground-truth reference items")
    urgency_accuracy: float = Field(..., ge=0.0, le=1.0, description="Classification accuracy on urgency severity")
    hallucination_rate: float = Field(..., ge=0.0, le=1.0, description="Estimated ungrounded assertion rate")
    latency_ms: float = Field(..., description="End-to-end evaluation duration")
    passed_gate: bool

class BenchmarkReport(BaseModel):
    total_cases: int
    overall_faithfulness: float
    overall_context_precision: float
    overall_context_recall: float
    overall_urgency_accuracy: float
    overall_hallucination_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    quality_gate_passed: bool
    quality_gate_details: Dict[str, Any]
    individual_results: List[EvalMetricScores]

class PlatformStats(BaseModel):
    total_feedback_count: int
    sources_breakdown: Dict[str, int]
    urgency_breakdown: Dict[str, int]
    sentiment_breakdown: Dict[str, int]
    top_product_areas: Dict[str, int]
    avg_faithfulness: float
    p95_latency_ms: float
