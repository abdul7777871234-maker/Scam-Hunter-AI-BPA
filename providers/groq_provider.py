from __future__ import annotations
from config.models import ModelResult

class GroqProvider:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None
        if api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key)
            except Exception:
                self.client = None

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        text = str(exc).lower()
        if any(x in text for x in ("api key", "authorization", "authentication", "401", "403", "429")):
            return "provider authentication or rate-limit error"
        if "timeout" in text or "timed out" in text:
            return "provider timeout"
        return "provider request error"

    def complete(self, prompt: str, system: str = "", temperature: float = 0.2) -> ModelResult:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured.")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            r = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
            content = getattr(getattr(r.choices[0], "message", None), "content", "") or ""
            if not content:
                raise RuntimeError("Groq returned an empty response.")
            return ModelResult(content, "groq", self.model)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(self._safe_error(exc)) from exc
