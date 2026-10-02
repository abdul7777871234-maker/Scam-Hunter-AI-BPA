from __future__ import annotations
from config.models import ModelResult
from config.settings import Settings
from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider

class ModelRouter:
    def __init__(self,settings:Settings):
        self.settings=settings
        self.groq=GroqProvider(settings.groq_api_key,settings.groq_model)
        self.gemini=GeminiProvider(settings.gemini_api_key,settings.gemini_models)

    @property
    def has_any_provider(self)->bool:
        return bool(self.settings.groq_api_key or self.settings.gemini_api_key)

    def groq_complete(self,prompt:str,system:str="",temperature:float=0.2)->ModelResult:
        return self.groq.complete(prompt,system,temperature)

    def gemini_complete(self,prompt:str,system:str="",temperature:float=0.2)->ModelResult:
        return self.gemini.complete(prompt,system,temperature)

    def best_available(self,prompt:str,system:str="",prefer_gemini:bool=False,temperature:float=0.2)->ModelResult:
        attempts=[]
        providers=[("gemini",self.gemini_complete),("groq",self.groq_complete)] if prefer_gemini else [("groq",self.groq_complete),("gemini",self.gemini_complete)]
        for name,call in providers:
            try:
                result=call(prompt,system,temperature)
                if result and result.text and result.text.strip():
                    if attempts: result.fallback_used=True
                    return result
                attempts.append(f"{name}: empty response")
            except Exception as exc:
                attempts.append(f"{name}: {self._safe_error(exc)}")
        raise RuntimeError("All AI providers failed. Attempts: "+" | ".join(attempts))

    def describe_image(self,image_bytes:bytes,mime_type:str,prompt:str)->ModelResult:
        if not image_bytes: raise ValueError("The uploaded image is empty.")
        return self.gemini.describe_image(image_bytes=image_bytes,mime_type=mime_type,prompt=prompt)

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        msg = str(exc).lower()
        if any(x in msg for x in ("api key", "authorization", "authentication", "401", "403")):
            return "provider authentication error"
        if "429" in msg or "quota" in msg or "resource_exhausted" in msg:
            return "provider rate limit or quota error"
        if "timeout" in msg or "timed out" in msg:
            return "provider timeout"
        return "provider request error"
