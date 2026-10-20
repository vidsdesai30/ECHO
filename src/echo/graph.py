"""Deterministic graph structures for observed events and hypotheses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import Event


@dataclass(frozen=True, slots=True)
class RelationshipEdge:
    source_event_id: str
    target_event_id: str
    relationship_type: str
    supporting_evidence: tuple[str, ...]
    contradictory_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    applicable_rules: tuple[str, ...]
    score: int
    evidence_strength: str
    explanation: str
    alternative_interpretations: tuple[str, ...]
    provenance: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        return {
            "source_event_id": self.source_event_id,
            "target_event_id": self.target_event_id,
            "relationship_type": self.relationship_type,
            "supporting_evidence": list(self.supporting_evidence),
            "contradictory_evidence": list(self.contradictory_evidence),
            "missing_evidence": list(self.missing_evidence),
            "applicable_rules": list(self.applicable_rules),
            "score": self.score,
            "evidence_strength": self.evidence_strength,
            "explanation": self.explanation,
            "alternative_interpretations": list(self.alternative_interpretations),
            "provenance": list(self.provenance),
        }


@dataclass(slots=True)
class ReconstructionGraph:
    version: int
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[RelationshipEdge] = field(default_factory=list)
    rejected_candidates: list[RelationshipEdge] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "nodes": [self.nodes[event_id] for event_id in sorted(self.nodes)],
            "edges": [edge.to_mapping() for edge in sorted(self.edges, key=_edge_key)],
            "rejected_candidates": [
                edge.to_mapping() for edge in sorted(self.rejected_candidates, key=_edge_key)
            ],
            "missing_evidence": sorted(self.missing_evidence),
        }


def _edge_key(edge: RelationshipEdge) -> tuple[str, str, str]:
    return edge.source_event_id, edge.target_event_id, edge.relationship_type


def graph_from_events(events: list[Event], version: int) -> ReconstructionGraph:
    graph = ReconstructionGraph(version=version)
    for event in sorted(events, key=lambda item: item.event_id):
        graph.nodes[event.event_id] = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "event_time": event.event_time.isoformat().replace("+00:00", "Z"),
            "observed_time": event.observed_time.isoformat().replace("+00:00", "Z"),
            "scenario_id": event.scenario_id,
            "uncertainty": "observed_event",
        }
    return graph
