"""Focused tests for the Master Prompt 2 reconstruction core."""

from datetime import datetime, timezone

import pytest

from echo.evaluator import evaluate_relationships
from echo.graph import graph_from_events
from echo.ingestion import ingest_records
from echo.models import Event, EventValidationError
from echo.reconstruction import IncrementalReconstructor, ReconstructionConfig, generate_candidates, reconstruct
from echo.scenarios.generator import DegradationConfig, generate_scenario


def record(**overrides):
    value = {
        "event_id": "evt-1",
        "scenario_id": "s-1",
        "event_type": "AUTH_SUCCESS",
        "event_time": "2026-01-01T12:00:00+02:00",
        "observed_time": "2026-01-01T12:01:00+02:00",
        "host_id": "host-a",
        "user_id": "user-a",
        "source_ip": "192.0.2.1",
        "process_id": "proc-a",
        "session_id": "session-a",
        "source": "test",
        "attributes": {},
    }
    value.update(overrides)
    return value


def test_event_parsing_normalizes_timezone_and_preserves_payload():
    event = Event.from_mapping(record())
    assert event.event_time == datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    assert event.original_payload["event_time"].endswith("+02:00")


def test_invalid_record_and_missing_optional_fields():
    with pytest.raises(EventValidationError):
        Event.from_mapping(record(event_time="not-a-time"))
    event = Event.from_mapping(record(host_id=None, user_id=None, session_id=None))
    assert event.host_id is None
    assert event.user_id is None


def test_ingestion_preserves_exact_and_semantic_duplicates():
    first = record()
    exact = dict(first)
    semantic = dict(first, event_id="evt-2")
    report = ingest_records([first, exact, semantic])
    assert report.accepted_count == 3
    assert report.exact_duplicate_ids == ["evt-1"]
    assert report.suspected_duplicate_ids == [("evt-1", "evt-2")]


def test_missing_identities_do_not_match():
    source = Event.from_mapping(record(event_id="a", event_type="AUTH_SUCCESS", host_id=None, user_id=None, session_id=None))
    target = Event.from_mapping(record(event_id="b", event_type="PROCESS_CREATE", host_id=None, user_id=None, session_id=None, event_time="2026-01-01T10:01:00Z"))
    candidate = generate_candidates([target, source])[0]
    assert not any("matching" in item for item in candidate.supporting_evidence if "identity" in item)
    assert not any("conflicting" in item for item in candidate.contradictory_evidence)
    assert candidate.score == 2


def test_candidate_support_and_contradiction_are_explained():
    source = Event.from_mapping(record(event_id="a", event_type="AUTH_SUCCESS", session_id="session-a"))
    target = Event.from_mapping(record(event_id="b", event_type="PROCESS_CREATE", session_id="session-b", event_time="2026-01-01T10:01:00Z"))
    candidate = generate_candidates([target, source])[0]
    assert "matching host identity" in candidate.supporting_evidence
    assert "conflicting session identity" in candidate.contradictory_evidence
    assert candidate.explanation.startswith("Rule-based score")


def test_graph_contains_disconnected_nodes_and_serializes():
    events = [Event.from_mapping(record()), Event.from_mapping(record(event_id="other", event_type="BENIGN_ACTIVITY"))]
    graph = reconstruct(events)
    serialized = graph.to_mapping()
    assert {node["event_id"] for node in serialized["nodes"]} == {"evt-1", "other"}
    assert serialized["version"] == 1


def test_scenario_generation_is_deterministic_and_truth_is_separate():
    settings = DegradationConfig(duplicate_rate=0.5, delayed_arrival_rate=1.0, noise_count=2)
    first = generate_scenario(42, degradation=settings).to_mapping()
    second = generate_scenario(42, degradation=settings).to_mapping()
    assert first == second
    assert first["ground_truth"]
    assert all("ground_truth" not in event for event in first["events"])


def test_late_event_updates_graph_using_event_time():
    scenario = generate_scenario(5, degradation=DegradationConfig(noise_count=0))
    by_id = {event.event_id: event for event in scenario.observed_events}
    engine = IncrementalReconstructor()
    early = engine.update([by_id["evt-005"], by_id["evt-003"]])
    complete = engine.update([by_id["evt-004"]])
    assert early.version == 1
    assert complete.version == 2
    assert any(edge.target_event_id == "evt-004" for edge in complete.edges)


def test_ground_truth_is_only_used_by_independent_evaluator():
    scenario = generate_scenario(3, degradation=DegradationConfig(noise_count=0))
    graph = reconstruct(scenario.observed_events)
    metrics = evaluate_relationships(graph, scenario.ground_truth)
    assert set(metrics) == {"true_positive", "false_positive", "false_negative", "precision", "recall", "f1"}
    assert all("evt-" in event_id for event_id in [edge.source_event_id for edge in graph.edges])
