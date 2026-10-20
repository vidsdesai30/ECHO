"""Deterministic synthetic event scenarios with controlled degradation."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from ..models import Event, GroundTruthRelationship


@dataclass(frozen=True, slots=True)
class DegradationConfig:
    missing_event_rate: float = 0.0
    duplicate_rate: float = 0.0
    delayed_arrival_rate: float = 0.0
    noise_count: int = 1
    missing_attribute_rate: float = 0.0
    out_of_order: bool = True

    def __post_init__(self) -> None:
        for name in ("missing_event_rate", "duplicate_rate", "delayed_arrival_rate", "missing_attribute_rate"):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.noise_count < 0:
            raise ValueError("noise_count must not be negative")


@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    seed: int
    observed_events: tuple[Event, ...]
    ground_truth: tuple[GroundTruthRelationship, ...]
    degradation: DegradationConfig

    def to_mapping(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "seed": self.seed,
            "degradation": {
                "missing_event_rate": self.degradation.missing_event_rate,
                "duplicate_rate": self.degradation.duplicate_rate,
                "delayed_arrival_rate": self.degradation.delayed_arrival_rate,
                "noise_count": self.degradation.noise_count,
                "missing_attribute_rate": self.degradation.missing_attribute_rate,
                "out_of_order": self.degradation.out_of_order,
            },
            "events": [event.to_mapping(include_original=True) for event in self.observed_events],
            "ground_truth": [relationship.to_mapping() for relationship in self.ground_truth],
        }


def _event(
    scenario_id: str,
    event_id: str,
    event_type: str,
    event_time: datetime,
    observed_time: datetime,
    **fields: Any,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "scenario_id": scenario_id,
        "event_type": event_type,
        "event_time": event_time.isoformat().replace("+00:00", "Z"),
        "observed_time": observed_time.isoformat().replace("+00:00", "Z"),
        "host_id": fields.pop("host_id", "host-alpha"),
        "user_id": fields.pop("user_id", "analyst-1"),
        "source_ip": fields.pop("source_ip", "192.0.2.10"),
        "process_id": fields.pop("process_id", None),
        "session_id": fields.pop("session_id", "session-a"),
        "source": fields.pop("source", "synthetic-sensor"),
        "attributes": fields,
    }


def generate_scenario(
    seed: int = 7,
    scenario_id: str = "scenario-demo",
    degradation: DegradationConfig | None = None,
) -> Scenario:
    """Generate a safe, local-only scenario and separate its truth from observations."""
    settings = degradation or DegradationConfig()
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    records = [
        _event(scenario_id, "evt-001", "AUTH_FAILURE", start, start + timedelta(seconds=2), user_id="analyst-1"),
        _event(scenario_id, "evt-002", "AUTH_SUCCESS", start + timedelta(seconds=40), start + timedelta(seconds=45), user_id="analyst-1"),
        _event(scenario_id, "evt-003", "PROCESS_CREATE", start + timedelta(minutes=2), start + timedelta(minutes=2, seconds=5), process_id="proc-1", executable="editor.exe"),
        _event(scenario_id, "evt-004", "FILE_ACCESS", start + timedelta(minutes=3), start + timedelta(minutes=3, seconds=20), process_id="proc-1", parent_process_id="proc-1", path="report.txt"),
        _event(scenario_id, "evt-005", "NETWORK_CONNECTION", start + timedelta(minutes=4), start + timedelta(minutes=4, seconds=8), process_id="proc-1", destination="198.51.100.20", port=443),
        _event(scenario_id, "evt-006", "BENIGN_ACTIVITY", start + timedelta(minutes=1), start + timedelta(minutes=1, seconds=2), process_id="background-1", source="background-sensor", task="scheduled-maintenance"),
    ]
    truth = (
        GroundTruthRelationship("evt-001", "evt-002", "authentication_followed_by_success"),
        GroundTruthRelationship("evt-002", "evt-003", "authenticated_process_start"),
        GroundTruthRelationship("evt-003", "evt-004", "process_file_access"),
        GroundTruthRelationship("evt-003", "evt-005", "process_network_connection"),
    )

    observed: list[dict[str, Any]] = []
    for record in records:
        if rng.random() < settings.missing_event_rate:
            continue
        copy = dict(record)
        copy["attributes"] = dict(record["attributes"])
        if rng.random() < settings.delayed_arrival_rate:
            arrival = datetime.fromisoformat(copy["observed_time"].replace("Z", "+00:00")) + timedelta(minutes=10)
            copy["observed_time"] = arrival.isoformat().replace("+00:00", "Z")
        if rng.random() < settings.missing_attribute_rate:
            for key in ("user_id", "session_id", "source_ip"):
                copy[key] = None
        observed.append(copy)
        if rng.random() < settings.duplicate_rate:
            observed.append(dict(copy))

    for index in range(settings.noise_count):
        noise_time = start + timedelta(minutes=6 + index)
        observed.append(
            _event(
                scenario_id,
                f"noise-{index + 1:03d}",
                "BENIGN_ACTIVITY",
                noise_time,
                noise_time + timedelta(seconds=1),
                host_id="host-beta",
                user_id=None,
                session_id=None,
                process_id=f"background-{index + 2}",
                source="synthetic-background",
                task="index-refresh",
            )
        )
    if settings.out_of_order:
        rng.shuffle(observed)
    events = tuple(Event.from_mapping(record) for record in observed)
    return Scenario(scenario_id, seed, events, truth, settings)
