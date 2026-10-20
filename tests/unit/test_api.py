"""API and evaluation contract tests using the explicit local fallback."""

from fastapi.testclient import TestClient

from echo.api import create_app
from echo.evaluation import evaluate_graph
from echo.graph import ReconstructionGraph


def test_health_and_version_are_safe():
    client = TestClient(create_app())
    assert client.get("/api/health").json() == {"status": "ok", "persistence": "memory-development-fallback"}
    assert client.get("/api/version").status_code == 200


def test_investigation_event_reconstruction_and_evidence_flow():
    client = TestClient(create_app())
    created = client.post("/api/investigations", json={"name": "Local investigation"})
    investigation_id = created.json()["id"]
    scenario = client.post("/api/synthetic-scenarios", json={"seed": 9, "noise_count": 0}).json()
    imported = client.post(f"/api/investigations/{investigation_id}/events", json={"events": scenario["events"]})
    assert imported.status_code == 200
    repeated = client.post(f"/api/investigations/{investigation_id}/events", json={"events": scenario["events"]})
    assert repeated.json()["stored_count"] == 0
    assert repeated.json()["idempotent_duplicate_count"] == len(scenario["events"])
    graph = client.post(f"/api/investigations/{investigation_id}/reconstruct")
    assert graph.status_code == 200
    assert graph.json()["nodes"]
    assert client.get(f"/api/investigations/{investigation_id}/timeline").status_code == 200
    assert client.get(f"/api/investigations/{investigation_id}/relationships").status_code == 200


def test_api_rejects_malformed_events_without_stack_trace():
    client = TestClient(create_app())
    investigation_id = client.post("/api/investigations", json={"name": "Validation"}).json()["id"]
    response = client.post(f"/api/investigations/{investigation_id}/events", json={"events": [{"event_id": "bad"}]})
    assert response.status_code == 422
    assert "Traceback" not in response.text


def test_experiment_returns_measured_metrics():
    client = TestClient(create_app())
    response = client.post("/api/experiments", json={"seed": 4, "noise_count": 0})
    assert response.status_code == 200
    metrics = response.json()["metrics"]
    assert {"edge_precision", "edge_recall", "edge_f1", "false_link_rate", "reconstruction_coverage", "runtime_seconds"} <= metrics.keys()
    assert metrics["runtime_seconds"] >= 0


def test_zero_denominator_metrics_are_explicitly_zero():
    metrics = evaluate_graph(ReconstructionGraph(version=1), [], 0)
    assert metrics["edge_precision"] == 0.0
    assert metrics["metric_policy"]
