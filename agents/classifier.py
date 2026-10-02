from __future__ import annotations


class ClassifierAgent:
    """Classifies user intent and decides which evidence sources an investigation needs."""

    def __init__(self, router):
        self.router = router

    def run(self, user_text: str) -> dict:
        text = (user_text or "").strip()

        # Keep obvious conversational turns out of the investigation pipeline.
        # This also avoids spending an LLM call on simple greetings.
        if self._obvious_normal_chat(text):
            return {
                "intent": "normal_chat",
                "category": "other",
                "requires_rag": False,
                "requires_web": False,
                "risk_level": "unknown",
                "reason": "Ordinary conversation or general chat.",
            }

        prompt = f"""
You are the intent and classification agent for ScamHunter AI.

First decide whether the user wants ordinary AI conversation or scam/phishing analysis.
Return ONLY valid JSON with these keys:

{{
  "intent": "normal_chat" or "scam_analysis",
  "category": "one of: phishing, investment, job, romance, payment, shopping, identity_theft, giveaway, technical_support, crypto, other",
  "requires_rag": true,
  "requires_web": false,
  "risk_level": "low, medium, high, or unknown",
  "reason": "short explanation"
}}

INTENT RULES:
- Use normal_chat for greetings, casual conversation, general questions, explanations,
  writing help, coding help, or other requests that are NOT asking to investigate
  suspicious content.
- Use scam_analysis when the user provides or asks about a suspicious message,
  phishing attempt, scam, fraud, suspicious link/domain, payment request, account warning,
  OTP request, impersonation, fake delivery/prize/job/investment offer, suspicious sender,
  or asks whether specific content is legitimate/safe/scam.
- A question about scams in general can remain normal_chat unless the user supplies
  specific suspicious content to investigate.
- Do not classify a message as scam_analysis merely because it contains words such as
  "bank", "account", "OTP", "payment", or "delivery". Context matters.

INVESTIGATION RULES:
- Use the internal knowledge base when the request concerns scam patterns, investigation guidance, or known scam behavior.
- Set requires_web to true when current, external, source-level, domain-level, organization-level, link-level, or sender-level information would materially help investigate the request.
- For a suspicious message, link, offer, payment request, account warning, sender claim, organization claim, or other externally verifiable scam claim, prefer web research when practical.
- Do not decide that something is a scam solely from the user's wording.
- Do not invent facts.

USER REQUEST:
{text}
"""

        try:
            result = self.router.best_available(
                prompt,
                system="You are a precise ScamHunter intent classifier. Return JSON only.",
                prefer_gemini=True,
            )
            data = self._parse(result.text)
        except Exception:
            # Conservative fallback: only analyze when deterministic signals indicate
            # suspicious content; otherwise keep ordinary conversation ordinary.
            intent = "scam_analysis" if self._web_signal(text) else "normal_chat"
            data = {
                "intent": intent,
                "category": "other",
                "requires_rag": intent == "scam_analysis",
                "requires_web": False,
                "risk_level": "unknown",
                "reason": "Intent classification could not be completed reliably.",
            }

        if self._web_signal(text):
            data["requires_web"] = True

        if data.get("intent") not in {"normal_chat", "scam_analysis"}:
            data["intent"] = "scam_analysis" if self._web_signal(text) else "normal_chat"

        if data["intent"] == "normal_chat":
            data["requires_rag"] = False
            data["requires_web"] = False

        return data

    @staticmethod
    def _obvious_normal_chat(text: str) -> bool:
        value = " ".join((text or "").lower().split()).strip("!?.,:;-")
        greetings = {
            "hi", "hello", "hey", "hiya", "howdy", "good morning",
            "good afternoon", "good evening", "good night", "salam",
            "assalam o alaikum", "assalamu alaikum", "thanks", "thank you",
            "thx", "ok", "okay", "bye", "goodbye",
        }
        if value in greetings:
            return True
        return value in {
            "how are you", "how are you doing", "what's up", "whats up",
            "who are you", "what can you do",
        }

    @staticmethod
    def _web_signal(text: str) -> bool:
        import re

        value = (text or "").lower()

        if re.search(
            r"https?://|www\.|\b[a-z0-9-]+\.(?:com|net|org|co|io|sa|pk|uk|gov|edu)\b",
            value,
        ):
            return True

        if re.search(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b", value):
            return True

        web_terms = (
            "is this a scam",
            "is this legit",
            "is this legitimate",
            "verify this",
            "check this link",
            "investigate this link",
            "check this website",
            "check this domain",
            "who sent this",
            "bank",
            "payment",
            "account",
            "otp",
            "verification",
            "refund",
            "prize",
            "investment",
            "job offer",
            "delivery",
            "package",
            "whatsapp",
            "telegram",
            "crypto",
            "wallet",
        )

        return any(term in value for term in web_terms)

    @staticmethod
    def _parse(text: str) -> dict:
        import json

        cleaned = text.strip()
        fence = chr(96) * 3

        if cleaned.startswith(fence):
            cleaned = cleaned.replace(fence + "json", "", 1)
            cleaned = cleaned.replace(fence, "")
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "intent": "scam_analysis",
                "category": "other",
                "requires_rag": True,
                "requires_web": False,
                "risk_level": "unknown",
                "reason": "The classifier returned an invalid JSON response.",
            }

        intent = str(data.get("intent", "scam_analysis")).strip().lower()
        return {
            "intent": intent if intent in {"normal_chat", "scam_analysis"} else "scam_analysis",
            "category": str(data.get("category", "other")),
            "requires_rag": bool(data.get("requires_rag", True)),
            "requires_web": bool(data.get("requires_web", False)),
            "risk_level": str(data.get("risk_level", "unknown")),
            "reason": str(data.get("reason", "")),
        }
