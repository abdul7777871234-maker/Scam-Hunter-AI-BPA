from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class Case:
    case_id: str
    status: str
    category: str
    risk_level: str
    created_at: str
    updated_at: str
    source: str = "ai_investigation"
    summary: str = ""
    investigation_mode: str = "Deep Investigation"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    task_id: str
    case_id: str
    title: str
    priority: str
    status: str = "open"
    owner: str = "system"
    created_at: str = field(default_factory=utc_now)
    due_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Escalation:
    escalation_id: str
    case_id: str
    level: str
    reason: str
    status: str = "open"
    created_at: str = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditEvent:
    event_id: str
    case_id: str | None
    event_type: str
    actor: str
    timestamp: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
