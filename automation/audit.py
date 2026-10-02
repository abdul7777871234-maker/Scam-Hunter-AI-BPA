from __future__ import annotations

from typing import Any

from .models import AuditEvent, new_id, utc_now


class AuditLogger:
    """Process-local audit trail. Persistence can be added later without changing callers."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def record(self, event_type: str, case_id: str | None, details: dict[str, Any] | None = None, actor: str = "system") -> dict[str, Any]:
        event = AuditEvent(
            event_id=new_id("evt"),
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            timestamp=utc_now(),
            details=details or {},
        )
        self.events.append(event)
        return event.to_dict()

    def for_case(self, case_id: str) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.events if event.case_id == case_id]
