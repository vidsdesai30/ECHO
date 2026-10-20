"""Safe JSON event ingestion and provenance reporting."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from .models import Event, EventValidationError

MAX_FILE_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class IngestionIssue:
    index: int
    message: str
    event_id: str | None = None


@dataclass(slots=True)
class IngestionReport:
    events: list[Event] = field(default_factory=list)
    invalid_records: list[IngestionIssue] = field(default_factory=list)
    exact_duplicate_ids: list[str] = field(default_factory=list)
    suspected_duplicate_ids: list[tuple[str, str]] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        return len(self.events)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "accepted_count": self.accepted_count,
            "invalid_count": len(self.invalid_records),
            "exact_duplicate_ids": list(self.exact_duplicate_ids),
            "suspected_duplicate_ids": [list(pair) for pair in self.suspected_duplicate_ids],
            "invalid_records": [
                {"index": issue.index, "event_id": issue.event_id, "message": issue.message}
                for issue in self.invalid_records
            ],
        }


def _semantic_key(event: Event) -> tuple[Any, ...]:
    return (
        event.scenario_id,
        event.event_type,
        event.event_time,
        event.host_id,
        event.user_id,
        event.process_id,
        event.session_id,
    )


def ingest_records(records: Iterable[Mapping[str, Any]]) -> IngestionReport:
    report = IngestionReport()
    exact_payloads: dict[str, str] = {}
    semantic_events: dict[tuple[Any, ...], str] = {}
    for index, record in enumerate(records):
        try:
            event = Event.from_mapping(record)
        except (EventValidationError, TypeError, AttributeError) as exc:
            event_id = record.get("event_id") if isinstance(record, Mapping) else None
            report.invalid_records.append(IngestionIssue(index, str(exc), event_id if isinstance(event_id, str) else None))
            continue
        canonical = json.dumps(event.original_payload, sort_keys=True, separators=(",", ":"), default=str)
        if event.event_id in exact_payloads:
            if exact_payloads[event.event_id] == canonical:
                report.exact_duplicate_ids.append(event.event_id)
            else:
                report.invalid_records.append(
                    IngestionIssue(index, "event_id is reused with a different payload", event.event_id)
                )
                continue
        else:
            exact_payloads[event.event_id] = canonical
        key = _semantic_key(event)
        previous_id = semantic_events.get(key)
        if previous_id is not None and previous_id != event.event_id:
            report.suspected_duplicate_ids.append((previous_id, event.event_id))
        else:
            semantic_events[key] = event.event_id
        report.events.append(event)
    return report


def load_json_records(path: str | Path) -> tuple[list[Mapping[str, Any]], dict[str, Any]]:
    file_path = Path(path)
    if file_path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"input file exceeds {MAX_FILE_BYTES} bytes")
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to read JSON input: {exc}") from exc
    if isinstance(payload, list):
        return payload, {}
    if not isinstance(payload, Mapping):
        raise ValueError("JSON input must be an event array or an object containing events")
    records = payload.get("events")
    if not isinstance(records, list):
        raise ValueError("JSON object must contain an events array")
    metadata = {key: value for key, value in payload.items() if key != "events"}
    return records, metadata
