"""Transparent candidate generation, evidence scoring, and reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable

from .graph import ReconstructionGraph, RelationshipEdge, graph_from_events
from .models import Event

COMPATIBLE_TYPES: dict[tuple[str, str], str] = {
    ("AUTH_FAILURE", "AUTH_SUCCESS"): "authentication_followed_by_success",
    ("AUTH_SUCCESS", "PROCESS_CREATE"): "authenticated_process_start",
    ("PROCESS_CREATE", "FILE_ACCESS"): "process_file_access",
    ("PROCESS_CREATE", "NETWORK_CONNECTION"): "process_network_connection",
    ("FILE_ACCESS", "NETWORK_CONNECTION"): "file_access_followed_by_network",
    ("NETWORK_CONNECTION", "PROCESS_CREATE"): "network_process_activity",
}


@dataclass(frozen=True, slots=True)
class ReconstructionConfig:
    max_event_gap_seconds: int = 30 * 60
    minimum_edge_score: int = 2
    include_rejected: bool = True


def _identity_match(
    left: str | None,
    right: str | None,
    label: str,
) -> tuple[int, str | None, str | None, str | None]:
    if left is None or right is None:
        return 0, None, None, f"{label} unavailable"
    if left == right:
        return 2, f"matching {label}", None, None
    return -3, None, f"conflicting {label}", None


def _score_candidate(source: Event, target: Event, relationship_type: str) -> RelationshipEdge:
    supporting: list[str] = [f"compatible event types: {source.event_type} -> {target.event_type}"]
    contradictory: list[str] = []
    missing: list[str] = []
    rules = ["event_type_compatibility", "event_time_direction"]
    score = 1

    gap = (target.event_time - source.event_time).total_seconds()
    if gap >= 0:
        supporting.append(f"event-time order is forward by {gap:g} seconds")
        score += 1
    else:
        contradictory.append("event-time order is reversed")
        score -= 2

    for left, right, label in ((source.host_id, target.host_id, "host identity"),):
        contribution, support, contradiction, unavailable = _identity_match(left, right, label)
        score += contribution
        if support:
            supporting.append(support)
            rules.append("known_identity_match")
        elif contradiction:
            contradictory.append(contradiction)
            rules.append("identity_conflict")
        elif unavailable:
            missing.append(unavailable)

    for left, right, label in (
        (source.session_id, target.session_id, "session identity"),
        (source.user_id, target.user_id, "user identity"),
    ):
        contribution, support, contradiction, unavailable = _identity_match(left, right, label)
        score += contribution
        if support:
            supporting.append(support)
            rules.append("known_identity_match")
        elif contradiction:
            contradictory.append(contradiction)
            rules.append("identity_conflict")
        elif unavailable:
            missing.append(unavailable)

    parent_id = target.attributes.get("parent_process_id")
    if source.process_id is not None and parent_id == source.process_id:
        score += 3
        supporting.append("target parent process matches source process")
        rules.append("process_ancestry_match")
    elif parent_id is None:
        missing.append("process ancestry unavailable")
    elif source.process_id is not None:
        contradictory.append("target parent process does not match source process")
        rules.append("process_ancestry_conflict")
        score -= 1

    if source.event_time == target.event_time:
        missing.append("event-time gap is zero; ordering confidence is limited")

    if score >= 6:
        strength = "Strongly supported"
    elif score >= 3:
        strength = "Plausible"
    elif score >= 1:
        strength = "Weakly supported"
    elif contradictory:
        strength = "Contradicted"
    else:
        strength = "Insufficient evidence"
    explanation = (
        f"Rule-based score {score}; this is an evidence strength label, not a calibrated probability "
        "and does not establish causation."
    )
    alternatives = (
        "Events may share context without one causing the other.",
        "Missing telemetry may explain absent supporting signals.",
    )
    return RelationshipEdge(
        source_event_id=source.event_id,
        target_event_id=target.event_id,
        relationship_type=relationship_type,
        supporting_evidence=tuple(supporting),
        contradictory_evidence=tuple(contradictory),
        missing_evidence=tuple(missing),
        applicable_rules=tuple(dict.fromkeys(rules)),
        score=score,
        evidence_strength=strength,
        explanation=explanation,
        alternative_interpretations=alternatives,
        provenance=(f"candidate generated from {source.source} and {target.source}",),
    )


def generate_candidates(events: Iterable[Event], config: ReconstructionConfig | None = None) -> list[RelationshipEdge]:
    """Generate bounded, direction-aware candidates using event time, not arrival order."""
    active = config or ReconstructionConfig()
    ordered = sorted(events, key=lambda event: (event.event_time, event.event_id))
    candidates: list[RelationshipEdge] = []
    for source_index, source in enumerate(ordered):
        for target in ordered[source_index + 1 :]:
            gap = target.event_time - source.event_time
            if gap > timedelta(seconds=active.max_event_gap_seconds):
                break
            relationship_type = COMPATIBLE_TYPES.get((source.event_type, target.event_type))
            if relationship_type is None:
                continue
            candidates.append(_score_candidate(source, target, relationship_type))
    return candidates


def reconstruct(events: Iterable[Event], config: ReconstructionConfig | None = None, version: int = 1) -> ReconstructionGraph:
    active = config or ReconstructionConfig()
    event_list = list(events)
    graph = graph_from_events(event_list, version)
    for candidate in generate_candidates(event_list, active):
        if candidate.score >= active.minimum_edge_score:
            graph.edges.append(candidate)
        elif active.include_rejected:
            graph.rejected_candidates.append(candidate)
    for event in event_list:
        if event.host_id is None or event.user_id is None or event.session_id is None:
            graph.missing_evidence.append(f"{event.event_id}: optional identity fields are incomplete")
    return graph


class IncrementalReconstructor:
    """Rebuild deterministically from all currently known events after each update."""

    def __init__(self, config: ReconstructionConfig | None = None) -> None:
        self.config = config or ReconstructionConfig()
        self._events: dict[str, Event] = {}
        self.version = 0

    def update(self, events: Iterable[Event]) -> ReconstructionGraph:
        for event in events:
            self._events[event.event_id] = event
        self.version += 1
        return reconstruct(self._events.values(), self.config, self.version)
