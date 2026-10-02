from __future__ import annotations

from automation import AutomationEngine

class InvestigationOrchestrator:
    def __init__(self, router, retriever, web_search, settings):
        self.router = router
        self.retriever = retriever
        self.web = web_search
        self.settings = settings

        from agents.classifier import ClassifierAgent
        from agents.rag_agent import RAGAgent
        from agents.evidence_agent import EvidenceAgent
        from agents.pattern_agent import ScamPatternAgent
        from agents.contradiction_agent import ContradictionAgent
        from agents.critic_agent import CriticAgent
        from agents.judge_agent import JudgeAgent
        from agents.response_agent import ResponseAgent
        from agents.web_agent import WebResearchAgent

        self.classifier = ClassifierAgent(router)
        self.rag = RAGAgent(retriever, settings)
        self.web = WebResearchAgent(web_search)
        self.evidence = EvidenceAgent(router)
        self.pattern = ScamPatternAgent(router)
        self.contradiction = ContradictionAgent(router)
        self.critic = CriticAgent(router)
        self.judge = JudgeAgent(router)
        self.response = ResponseAgent(router)
        self.automation = AutomationEngine()

    def detect_intent(self, user_text: str) -> dict:
        """Route ordinary conversation away from the scam investigation pipeline."""
        return self.classifier.run(user_text)

    def run_quick(self, user_text: str, mode="Quick Check", style="Balanced", language="English", signals="") -> dict:
        events = []
        classification = self.classifier.run(user_text)
        events.append("Classifier Agent — Input classified")
        rag = self.rag.run(user_text)
        events.append("RAG Agent — Knowledge base searched")
        web = {"items": [], "cached": False}
        if classification.get("requires_web", False):
            web = self.web.run(user_text[:2500])
            events.append("Web Research Agent — Web research completed")
        evidence = self.evidence.run(user_text, rag, web)
        events.append("Evidence Agent — Evidence analyzed")
        analysis = evidence.get("analysis", "")
        evidence_items = evidence.get("evidence", rag.get("evidence", []))
        final = self.response.run(
            user_text, analysis, "", "", evidence_items,
            mode=mode, style=style, language=language, signals=signals
        )
        events.append("Response Agent — Fast response generated")
        result = {
            "answer": final,
            "events": events,
            "classification": classification,
            "rag": {"items": rag.get("items", []), "evidence": evidence_items},
            "web": web,
            "analysis": analysis,
        }
        result["automation"] = self.automation.process(result, mode=mode)
        events.append("BPA Automation Engine — Case workflow completed")
        return result

    def run(self, user_text: str, mode="Deep Investigation", style="Balanced", language="English", signals="") -> dict:
        events = []
        classification = self.classifier.run(user_text)
        events.append("Classifier Agent — Input classified")
        rag = self.rag.run(user_text) if classification.get("requires_rag", True) else {"items": [], "evidence": []}
        events.append("RAG Agent — Knowledge base searched")
        web = {"items": [], "cached": False}
        if classification.get("requires_web", False):
            web = self.web.run(user_text[:2500])
            events.append("Web Research Agent — Web research completed")
        evidence = self.evidence.run(user_text, rag, web)
        events.append("Evidence Agent — Evidence analyzed")
        pattern = self.pattern.run(user_text, evidence["analysis"])
        events.append("Scam Pattern Agent — Scam patterns analyzed")
        contradiction = self.contradiction.run(evidence["evidence"])
        events.append("Contradiction Agent — Contradictions checked")
        judge = self.judge.run(pattern, contradiction, evidence["evidence"])
        events.append("Judge Agent — Evidence reviewed")

        draft = self.response.run(
            user_text, pattern, contradiction, judge, evidence["evidence"],
            mode=mode, style=style, language=language, signals=signals
        )
        events.append("Response Agent — Draft response synthesized")

        critique = self.critic.run(draft, evidence["evidence"])
        events.append("Critic Agent — Final quality check completed")

        final = self.response.run(
            user_text,
            pattern + "\n\nQUALITY CHECK:\n" + critique,
            contradiction,
            judge,
            evidence["evidence"],
            mode=mode, style=style, language=language, signals=signals
        )
        result = {
            "answer": final,
            "events": events,
            "classification": classification,
            "rag": rag,
            "web": web,
            "analysis": evidence["analysis"],
            "pattern": pattern,
            "contradiction": contradiction,
            "judge": judge,
            "critique": critique,
        }
        result["automation"] = self.automation.process(result, mode=mode)
        events.append("BPA Automation Engine — Case workflow completed")
        return result
