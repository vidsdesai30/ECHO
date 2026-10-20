"""Independent evaluation boundary for reconstructed relationships."""

from __future__ import annotations

from typing import Iterable

from .graph import ReconstructionGraph
from .models import GroundTruthRelationship


def evaluate_relationships(
    graph: ReconstructionGraph,
    ground_truth: Iterable[GroundTruthRelationship],
) -> dict[str, int | float]:
    """Compare output edges with truth after prediction has completed."""
    predicted = {
        (edge.source_event_id, edge.target_event_id, edge.relationship_type)
        for edge in graph.edges
    }
    expected = {
        (item.source_event_id, item.target_event_id, item.relationship_type)
        for item in ground_truth
    }
    true_positive = len(predicted & expected)
    false_positive = len(predicted - expected)
    false_negative = len(expected - predicted)
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / len(expected) if expected else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
