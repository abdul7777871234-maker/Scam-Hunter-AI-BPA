from __future__ import annotations

from .models import Escalation, new_id


class EscalationManager:
    def __init__(self) -> None:
        self.items: dict[str, Escalation] = {}

    def create(self, case_id: str, level: str, reason: str) -> Escalation:
        item = Escalation(
            escalation_id=new_id("esc"),
            case_id=case_id,
            level=level,
            reason=reason,
        )
        self.items[item.escalation_id] = item
        return item

    def for_case(self, case_id: str) -> list[dict]:
        return [item.to_dict() for item in self.items.values() if item.case_id == case_id]
