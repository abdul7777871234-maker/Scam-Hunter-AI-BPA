from __future__ import annotations

from typing import Any

from .audit import AuditLogger
from .case_manager import CaseManager
from .escalation import EscalationManager
from .rules import build_tasks, escalation_for, infer_risk
from .task_manager import TaskManager


class AutomationEngine:
    """Turns an investigation result into a structured BPA case workflow."""

    def __init__(self) -> None:
        self.cases = CaseManager()
        self.tasks = TaskManager()
        self.escalations = EscalationManager()
        self.audit = AuditLogger()

    def process(self, investigation: dict[str, Any], mode: str = "Deep Investigation") -> dict[str, Any]:
        classification = investigation.get("classification") or {}
        category = str(classification.get("category") or "other").strip().lower()
        risk = infer_risk(
            classification,
            investigation.get("pattern", ""),
            investigation.get("judge", ""),
            investigation.get("analysis", ""),
        )
        summary = str(investigation.get("answer") or investigation.get("analysis") or "").strip()

        case = self.cases.create(
            category=category,
            risk_level=risk,
            summary=summary,
            mode=mode,
            metadata={
                "intent": classification.get("intent", "scam_analysis"),
                "requires_web": bool(classification.get("requires_web", False)),
                "requires_rag": bool(classification.get("requires_rag", True)),
            },
        )
        self.audit.record("case_created", case.case_id, {"risk_level": risk, "category": category})

        task_defs = build_tasks(category, risk)
        tasks = self.tasks.create_for_case(case.case_id, task_defs)
        self.audit.record("tasks_created", case.case_id, {"count": len(tasks)})

        escalation = escalation_for(risk, category)
        escalation_item = None
        if escalation:
            level, reason = escalation
            escalation_item = self.escalations.create(case.case_id, level, reason)
            self.cases.update_status(case.case_id, "escalated")
            self.audit.record(
                "case_escalated",
                case.case_id,
                {"level": level, "reason": reason},
            )

        if not escalation_item:
            self.cases.update_status(case.case_id, "action_required")

        self.audit.record(
            "workflow_completed",
            case.case_id,
            {"status": self.cases.get(case.case_id).status if self.cases.get(case.case_id) else "unknown"},
        )

        return {
            "case": self.cases.get(case.case_id).to_dict(),
            "tasks": [task.to_dict() for task in tasks],
            "escalations": [escalation_item.to_dict()] if escalation_item else [],
            "audit": self.audit.for_case(case.case_id),
        }
