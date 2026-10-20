"""Reproducible evaluation metrics kept outside prediction code."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from .graph import ReconstructionGraph
from .models import GroundTruthRelationship


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    """Defines matching and zero-denominator policies for one evaluation."""

    zero_denominator_value: float = 0.0


def _relationship_key(item: GroundTruthRelationship) -> tuple[str, str, str]:
    return item.source_event_id, item.target_event_id, item.relationship_type


def evaluate_graph(
    graph: ReconstructionGraph,
    ground_truth: Iterable[GroundTruthRelationship],
    event_count: int,
    config: EvaluationConfig | None = None,
    elapsed_seconds: float | None = None,
) -> dict[str, int | float | str]:
    """Evaluate a completed graph; truth never enters graph construction."""
    settings = config or EvaluationConfig()
    expected = {_relationship_key(item) for item in ground_truth}
    predicted = {
        (edge.source_event_id, edge.target_event_id, edge.relationship_type)
        for edge in graph.edges
    }
    true_positive = len(expected & predicted)
    false_positive = len(predicted - expected)
    false_negative = len(expected - predicted)
    precision = true_positive / len(predicted) if predicted else settings.zero_denominator_value
    recall = true_positive / len(expected) if expected else settings.zero_denominator_value
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else settings.zero_denominator_value
    eligible_events = {
        event_id
        for item in expected
        for event_id in item[:2]
    }
    predicted_events = {event_id for edge in graph.edges for event_id in (edge.source_event_id, edge.target_event_id)}
    coverage = len(eligible_events & predicted_events) / len(eligible_events) if eligible_events else settings.zero_denominator_value
    false_link_rate = false_positive / len(predicted) if predicted else settings.zero_denominator_value
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "edge_precision": precision,
        "edge_recall": recall,
        "edge_f1": f1,
        "false_link_rate": false_link_rate,
        "reconstruction_coverage": coverage,
        "ordering_accuracy": settings.zero_denominator_value,
        "runtime_seconds": elapsed_seconds if elapsed_seconds is not None else 0.0,
        "event_count": event_count,
        "eligible_relationship_count": len(expected),
        "metric_policy": "Undefined zero-denominator metrics are reported as 0.0, not as perfect performance.",
    }


def timed_evaluation(
    graph: ReconstructionGraph,
    ground_truth: Iterable[GroundTruthRelationship],
    event_count: int,
    config: EvaluationConfig | None = None,
) -> dict[str, int | float | str]:
    start = perf_counter()
    metrics = evaluate_graph(graph, ground_truth, event_count, config)
    metrics["runtime_seconds"] = perf_counter() - start
    return metrics