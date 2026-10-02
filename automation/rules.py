from __future__ import annotations

from typing import Any


RISK_ORDER = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def normalize_risk(value: Any) -> str:
    value = str(value or "unknown").strip().lower()
    if value in RISK_ORDER:
        return value
    if "critical" in value:
        return "critical"
    if "high" in value:
        return "high"
    if "medium" in value:
        return "medium"
    if "low" in value:
        return "low"
    return "unknown"


def infer_risk(classification: dict, *evidence_texts: str) -> str:
    """Conservative deterministic risk rule; never claims certainty."""
    explicit = normalize_risk(classification.get("risk_level"))
    if explicit != "unknown":
        return explicit

    text = " ".join(str(x or "") for x in evidence_texts).lower()
    if any(term in text for term in ("critical", "credential theft", "otp", "seed phrase", "private key")):
        return "high"
    if any(term in text for term in ("high risk", "phishing", "payment scam", "impersonation")):
        return "high"
    if any(term in text for term in ("medium risk", "suspicious", "urgent", "fraud")):
        return "medium"
    return "unknown"


def build_tasks(category: str, risk_level: str) -> list[dict[str, str]]:
    tasks = [
        {"title": "Verify the sender through an independent official channel", "priority": "high"},
        {"title": "Verify any domain or link using the organization's official website", "priority": "high"},
        {"title": "Do not share OTPs, passwords, recovery codes, or private keys", "priority": "high"},
    ]

    if category in {"payment", "investment", "crypto", "shopping", "giveaway"}:
        tasks.append({"title": "Do not send money until the payment request is independently verified", "priority": "high"})

    if category in {"identity_theft", "technical_support", "phishing"}:
        tasks.append({"title": "Review account security and change exposed credentials through the official service", "priority": "high"})

    if risk_level in {"high", "critical"}:
        tasks.append({"title": "Escalate the case for human review before taking further action", "priority": "urgent"})

    return tasks


def escalation_for(risk_level: str, category: str) -> tuple[str, str] | None:
    if risk_level == "critical":
        return "critical", f"Critical-risk rule triggered for category '{category}'. Human review is required."
    if risk_level == "high":
        return "high", f"High-risk rule triggered for category '{category}'. Human review is recommended before action."
    return None
