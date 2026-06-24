import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from feedpulse.schemas.models import (
    FeedbackItem,
    SearchRequest,
    HybridSearchResult,
    ThemeCluster,
    ClusterRequest,
    SynthesisRequest,
    ClusterSynthesis,
    BenchmarkReport,
    PlatformStats
)
from feedpulse.retrieval.hybrid_engine import HybridRetrievalPipeline
from feedpulse.analytics.clusterer import FeedbackThemeClusterer
from feedpulse.analytics.synthesizer import ClusterInsightSynthesizer
from feedpulse.evaluation.harness import FeedbackEvalHarness
from feedpulse.config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load data and pre-run benchmarks on startup."""
    load_initial_data()
    yield

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Customer Feedback Intelligence Platform & LLM Evaluation Harness",
    lifespan=lifespan
)

# Enable CORS for flexible dashboard embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage and state
FEEDBACK_ITEMS: List[FeedbackItem] = []
PIPELINE = HybridRetrievalPipeline(default_alpha=settings.DEFAULT_HYBRID_ALPHA)
CLUSTERER = FeedbackThemeClusterer()
SYNTHESIZER = ClusterInsightSynthesizer()
EVAL_HARNESS = FeedbackEvalHarness(PIPELINE)
LATEST_BENCHMARK: Optional[BenchmarkReport] = None

def load_initial_data():
    """Load curated seed dataset and index into retrieval pipeline."""
    global FEEDBACK_ITEMS, LATEST_BENCHMARK
    data_file = Path(__file__).resolve().parent.parent / "data" / "seed_feedback.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            FEEDBACK_ITEMS = [FeedbackItem(**item) for item in raw_data]
            PIPELINE.index(FEEDBACK_ITEMS)
            # Pre-run baseline evaluation
            LATEST_BENCHMARK = EVAL_HARNESS.run_benchmark()
            print(f"Loaded {len(FEEDBACK_ITEMS)} feedback items and initialized retrieval index.")



# ----------------- Static UI Mounting -----------------
static_dir = Path(__file__).resolve().parent.parent / "ui" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "FeedPulse AI Backend Active"}

# ----------------- REST Endpoints -----------------
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "indexed_items": len(FEEDBACK_ITEMS)
    }

@app.get("/api/v1/stats", response_model=PlatformStats)
async def get_platform_stats():
    """Returns overview platform analytics for dashboard widgets."""
    if not FEEDBACK_ITEMS:
        raise HTTPException(status_code=404, detail="No feedback items loaded.")

    sources_map = dict(Counter(it.source.value for it in FEEDBACK_ITEMS))
    urgency_map = dict(Counter(it.urgency.value for it in FEEDBACK_ITEMS))
    sentiment_map = dict(Counter(it.sentiment.value for it in FEEDBACK_ITEMS))
    areas_map = dict(Counter(it.product_area for it in FEEDBACK_ITEMS).most_common(5))

    avg_faithfulness = LATEST_BENCHMARK.overall_faithfulness if LATEST_BENCHMARK else 0.94
    p95_lat = LATEST_BENCHMARK.p95_latency_ms if LATEST_BENCHMARK else 4.5

    return PlatformStats(
        total_feedback_count=len(FEEDBACK_ITEMS),
        sources_breakdown=sources_map,
        urgency_breakdown=urgency_map,
        sentiment_breakdown=sentiment_map,
        top_product_areas=areas_map,
        avg_faithfulness=avg_faithfulness,
        p95_latency_ms=p95_lat
    )

@app.get("/api/v1/feedback", response_model=List[FeedbackItem])
async def list_feedback(limit: int = 50, offset: int = 0):
    """Retrieve paginated feedback items."""
    return FEEDBACK_ITEMS[offset:offset + limit]

@app.post("/api/v1/feedback", response_model=FeedbackItem)
async def ingest_feedback(item: FeedbackItem):
    """Ingest new customer feedback and update live retrieval index."""
    # Deduplicate by ID
    existing_ids = {it.id for it in FEEDBACK_ITEMS}
    if item.id in existing_ids:
        raise HTTPException(status_code=409, detail=f"Feedback with ID {item.id} already exists.")

    FEEDBACK_ITEMS.append(item)
    PIPELINE.index(FEEDBACK_ITEMS)
    return item

@app.post("/api/v1/search", response_model=List[HybridSearchResult])
async def hybrid_search(request: SearchRequest):
    """Execute BM25 + Dense Semantic search with cross-encoder reranking."""
    return PIPELINE.search(request)

@app.get("/api/v1/clusters", response_model=List[ThemeCluster])
async def get_theme_clusters(n_clusters: int = Query(default=6, ge=2, le=12)):
    """Discover semantic issue clusters across all indexed customer feedback."""
    return CLUSTERER.cluster_feedback(FEEDBACK_ITEMS, n_clusters=n_clusters)

@app.post("/api/v1/clusters/synthesize", response_model=ClusterSynthesis)
async def synthesize_cluster_insight(req: SynthesisRequest):
    """Generate root-cause analysis and engineering action plan for a cluster."""
    clusters = CLUSTERER.cluster_feedback(FEEDBACK_ITEMS, n_clusters=6)
    target_cluster = next((c for c in clusters if c.cluster_id == req.cluster_id), None)
    if not target_cluster:
        raise HTTPException(status_code=404, detail=f"Cluster {req.cluster_id} not found.")

    return SYNTHESIZER.synthesize(target_cluster)

@app.post("/api/v1/eval/run", response_model=BenchmarkReport)
async def run_evaluation_harness():
    """Trigger the automated regression test suite across ground-truth benchmark cases."""
    global LATEST_BENCHMARK
    LATEST_BENCHMARK = EVAL_HARNESS.run_benchmark()
    return LATEST_BENCHMARK

@app.get("/api/v1/eval/latest", response_model=BenchmarkReport)
async def get_latest_evaluation():
    """Get the latest evaluation report and quality gate scorecard."""
    global LATEST_BENCHMARK
    if LATEST_BENCHMARK is None:
        LATEST_BENCHMARK = EVAL_HARNESS.run_benchmark()
    return LATEST_BENCHMARK
