import pytest
from fastapi.testclient import TestClient
from feedpulse.api.routes import app, load_initial_data

@pytest.fixture(scope="module")
def client():
    load_initial_data()
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["indexed_items"] >= 30

def test_stats_endpoint(client):
    res = client.get("/api/v1/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_feedback_count"] >= 30
    assert "critical" in data["urgency_breakdown"]
    assert data["avg_faithfulness"] >= 0.85

def test_hybrid_search_endpoint(client):
    payload = {
        "query": "WebGL canvas crash on Mac M2",
        "top_k": 5,
        "alpha": 0.55,
        "enable_reranking": True
    }
    res = client.post("/api/v1/search", json=payload)
    assert res.status_code == 200
    results = res.json()
    assert len(results) > 0
    assert "FB-1001" in [r["item"]["id"] for r in results] or "FB-1002" in [r["item"]["id"] for r in results]

def test_clusters_endpoint(client):
    res = client.get("/api/v1/clusters?n_clusters=4")
    assert res.status_code == 200
    clusters = res.json()
    assert len(clusters) == 4

def test_eval_benchmark_endpoint(client):
    res = client.post("/api/v1/eval/run")
    assert res.status_code == 200
    report = res.json()
    assert report["total_cases"] == 6
    assert report["quality_gate_passed"] is True
    assert report["overall_faithfulness"] >= 0.85
