from __future__ import annotations

from config.models import ModelResult


class GeminiProvider:
    """
    Gemini provider with automatic model fallback.

    The configured model list is tried sequentially. This means
    quota/rate-limit/model-availability failures can move to the
    next configured Gemini model automatically.
    """

    def __init__(
        self,
        api_key: str,
        models: tuple[str, ...],
    ):
        self.api_key = api_key
        self.models = tuple(
            model.strip()
            for model in models
            if model and model.strip()
        )

        self.client = None

        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(
                    api_key=self.api_key
                )

            except Exception:
                self.client = None

    # ---------------------------------------------------------
    # TEXT COMPLETION
    # ---------------------------------------------------------

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2,
    ) -> ModelResult:

        self._require_client()

        if not prompt or not prompt.strip():
            raise ValueError(
                "Gemini prompt cannot be empty."
            )

        full_prompt = (
            f"{system.strip()}\n\n{prompt.strip()}"
            if system and system.strip()
            else prompt.strip()
        )

        errors: list[str] = []

        for index, model in enumerate(self.models):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=full_prompt,
                )

                text = self._extract_text(response)

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return ModelResult(
                    text=text,
                    provider="gemini",
                    model=model,
                    fallback_used=index > 0,
                )

            except Exception as exc:
                errors.append(
                    self._format_model_error(
                        model,
                        exc,
                    )
                )

        raise RuntimeError(
            "All Gemini models failed. "
            + " | ".join(errors)
        )

    # ---------------------------------------------------------
    # IMAGE / SCREENSHOT ANALYSIS
    # ---------------------------------------------------------

    def describe_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
    ) -> ModelResult:

        self._require_client()

        if not image_bytes:
            raise ValueError(
                "Image data is empty."
            )

        if not mime_type:
            raise ValueError(
                "Image MIME type is missing."
            )

        if not prompt or not prompt.strip():
            raise ValueError(
                "Image analysis prompt cannot be empty."
            )

        try:
            from google.genai import types
        except Exception as exc:
            raise RuntimeError(
                "The installed google-genai SDK does not provide "
                "the required multimodal types."
            ) from exc

        errors: list[str] = []

        for index, model in enumerate(self.models):
            try:
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )

                response = self.client.models.generate_content(
                    model=model,
                    contents=[
                        image_part,
                        prompt.strip(),
                    ],
                )

                text = self._extract_text(response)

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty image-analysis response."
                    )

                return ModelResult(
                    text=text,
                    provider="gemini",
                    model=model,
                    fallback_used=index > 0,
                )

            except Exception as exc:
                errors.append(
                    self._format_model_error(
                        model,
                        exc,
                    )
                )

        raise RuntimeError(
            "All Gemini image-analysis models failed. "
            + " | ".join(errors)
        )

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------

    def _require_client(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        if not self.client:
            raise RuntimeError(
                "Gemini SDK could not be initialized."
            )

        if not self.models:
            raise RuntimeError(
                "No Gemini models are configured."
            )

    @staticmethod
    def _extract_text(response) -> str:
        """
        Safely extract text from the Google GenAI response.
        """

        text = getattr(
            response,
            "text",
            None,
        )

        if isinstance(text, str) and text.strip():
            return text.strip()

        # Fallback for SDK responses where .text is unavailable.
        parts = []

        try:
            candidates = getattr(
                response,
                "candidates",
                [],
            ) or []

            for candidate in candidates:
                content = getattr(
                    candidate,
                    "content",
                    None,
                )

                if not content:
                    continue

                candidate_parts = getattr(
                    content,
                    "parts",
                    [],
                ) or []

                for part in candidate_parts:
                    part_text = getattr(
                        part,
                        "text",
                        None,
                    )

                    if isinstance(part_text, str):
                        parts.append(part_text)

        except Exception:
            pass

        return "\n".join(
            part.strip()
            for part in parts
            if isinstance(part, str) and part.strip()
        ).strip()

    @staticmethod
    def _format_model_error(
        model: str,
        exc: Exception,
    ) -> str:

        message = str(exc).lower()
        if any(marker in message for marker in ("api key", "authorization", "authentication", "401", "403")):
            safe = "provider authentication error"
        elif "429" in message or "resource_exhausted" in message or "quota" in message:
            safe = "provider rate limit or quota error"
        elif "503" in message or "unavailable" in message:
            safe = "provider temporarily unavailable"
        elif "timeout" in message or "timed out" in message:
            safe = "provider timeout"
        else:
            safe = "provider request error"
        return f"{model}: {safe}"
