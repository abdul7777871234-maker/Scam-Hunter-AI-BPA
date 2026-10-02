from __future__ import annotations

from typing import Any

from .models import Case, new_id, utc_now


class CaseManager:
    def __init__(self) -> None:
        self.cases: dict[str, Case] = {}

    def create(self, category: str, risk_level: str, summary: str, mode: str, metadata: dict[str, Any] | None = None) -> Case:
        now = utc_now()
        case = Case(
            case_id=new_id("case"),
            status="open",
            category=category,
            risk_level=risk_level,
            created_at=now,
            updated_at=now,
            summary=summary[:1200],
            investigation_mode=mode,
            metadata=metadata or {},
        )
        self.cases[case.case_id] = case
        return case

    def update_status(self, case_id: str, status: str) -> Case | None:
        case = self.cases.get(case_id)
        if not case:
            return None
        case.status = status
        case.updated_at = utc_now()
        return case

    def get(self, case_id: str) -> Case | None:
        return self.cases.get(case_id)
