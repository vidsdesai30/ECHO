"""Validated event and ground-truth data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

MAX_STRING_LENGTH = 256
MAX_ATTRIBUTES = 64
MAX_ATTRIBUTE_VALUE_LENGTH = 2048


class EventValidationError(ValueError):
    """Raised when an untrusted event record is malformed."""


def _required_string(record: Mapping[str, Any], name: str) -> str:
    value = record.get(name)
    if not isinstance(value, str) or not value.strip():
        raise EventValidationError(f"{name} must be a non-empty string")
    value = value.strip()
    if len(value) > MAX_STRING_LENGTH:
        raise EventValidationError(f"{name} exceeds {MAX_STRING_LENGTH} characters")
    return value


def _optional_string(record: Mapping[str, Any], name: str) -> str | None:
    value = record.get(name)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise EventValidationError(f"{name} must be a string or null")
    value = value.strip()
    if len(value) > MAX_STRING_LENGTH:
        raise EventValidationError(f"{name} exceeds {MAX_STRING_LENGTH} characters")
    return value or None


def parse_timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise EventValidationError(f"{name} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventValidationError(f"{name} is not a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EventValidationError(f"{name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _attributes(record: Mapping[str, Any]) -> dict[str, Any]:
    value = record.get("attributes", {})
    if not isinstance(value, Mapping):
        raise EventValidationError("attributes must be an object")
    if len(value) > MAX_ATTRIBUTES:
        raise EventValidationError(f"attributes may contain at most {MAX_ATTRIBUTES} keys")
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise EventValidationError("attribute names must be non-empty strings")
        if len(key) > MAX_STRING_LENGTH:
            raise EventValidationError("attribute name is too long")
        if isinstance(item, (dict, list)):
            raise EventValidationError("nested attribute objects and arrays are not supported")
        if item is not None and not isinstance(item, (str, int, float, bool)):
            raise EventValidationError(f"attribute {key!r} has an unsupported value")
        if isinstance(item, str) and len(item) > MAX_ATTRIBUTE_VALUE_LENGTH:
            raise EventValidationError(f"attribute {key!r} is too long")
        normalized[key.strip()] = item
    return normalized


@dataclass(frozen=True, slots=True)
class Event:
    """A normalized event with its source payload preserved."""

    event_id: str
    scenario_id: str
    event_type: str
    event_time: datetime
    observed_time: datetime
    host_id: str | None = None
    user_id: str | None = None
    source_ip: str | None = None
    process_id: str | None = None
    session_id: str | None = None
    source: str = "unknown"
    attributes: dict[str, Any] = field(default_factory=dict)
    original_payload: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_mapping(cls, record: Mapping[str, Any]) -> "Event":
        if not isinstance(record, Mapping):
            raise EventValidationError("event must be an object")
        original = dict(record)
        return cls(
            event_id=_required_string(record, "event_id"),
            scenario_id=_required_string(record, "scenario_id"),
            event_type=_required_string(record, "event_type").upper(),
            event_time=parse_timestamp(record.get("event_time"), "event_time"),
            observed_time=parse_timestamp(record.get("observed_time"), "observed_time"),
            host_id=_optional_string(record, "host_id"),
            user_id=_optional_string(record, "user_id"),
            source_ip=_optional_string(record, "source_ip"),
            process_id=_optional_string(record, "process_id"),
            session_id=_optional_string(record, "session_id"),
            source=_optional_string(record, "source") or "unknown",
            attributes=_attributes(record),
            original_payload=original,
        )

    def to_mapping(self, include_original: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "event_id": self.event_id,
            "scenario_id": self.scenario_id,
            "event_type": self.event_type,
            "event_time": self.event_time.isoformat().replace("+00:00", "Z"),
            "observed_time": self.observed_time.isoformat().replace("+00:00", "Z"),
            "host_id": self.host_id,
            "user_id": self.user_id,
            "source_ip": self.source_ip,
            "process_id": self.process_id,
            "session_id": self.session_id,
            "source": self.source,
            "attributes": dict(self.attributes),
        }
        if include_original:
            result["original_payload"] = dict(self.original_payload)
        return result


@dataclass(frozen=True, slots=True)
class GroundTruthRelationship:
    """An independently generated relationship used only after reconstruction."""

    source_event_id: str
    target_event_id: str
    relationship_type: str

    def to_mapping(self) -> dict[str, str]:
        return {
            "source_event_id": self.source_event_id,
            "target_event_id": self.target_event_id,
            "relationship_type": self.relationship_type,
        }
