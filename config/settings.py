from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class Settings:
    # ---------------------------------------------------------
    # API KEYS
    # ---------------------------------------------------------

    groq_api_key: str = ""
    gemini_api_key: str = ""

    # ---------------------------------------------------------
    # PRIMARY GROQ MODEL
    # ---------------------------------------------------------

    groq_model: str = "openai/gpt-oss-120b"

    # ---------------------------------------------------------
    # GEMINI FALLBACK CHAIN
    #
    # Ordered from preferred/newest to fallback.
    # ---------------------------------------------------------

    gemini_models: tuple[str, ...] = (
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    )

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    chunk_size: int = 850
    chunk_overlap: int = 120

    rag_top_k: int = 15
    rerank_top_k: int = 5

    # ---------------------------------------------------------
    # WEB SEARCH
    # ---------------------------------------------------------

    max_web_results: int = 6
    search_ttl_hours: int = 24

    # ---------------------------------------------------------
    # MEMORY
    # ---------------------------------------------------------

    max_memory_items: int = 5

    # ---------------------------------------------------------
    # UPLOADS
    # ---------------------------------------------------------

    max_upload_mb: int = 10

    # Persist uploaded text documents into the local knowledge base.
    # Disabled by default so temporary user uploads are not retained.
    persist_uploads: bool = False

    # ---------------------------------------------------------
    # DIRECTORIES
    # ---------------------------------------------------------

    data_dir: Path = field(
        default=ROOT / "knowledge_base"
    )

    cache_dir: Path = field(
        default=ROOT / "cache"
    )

    memory_dir: Path = field(
        default=ROOT / "memory_data"
    )

    # ---------------------------------------------------------
    # RUNTIME SECRETS
    # ---------------------------------------------------------

    @classmethod
    def from_runtime(cls) -> "Settings":

        def secret(name: str) -> str:
            # Streamlit Secrets
            try:
                import streamlit as st

                value = st.secrets.get(name)

                if value:
                    return str(value).strip()

            except Exception:
                pass

            # Environment variables
            return os.getenv(name, "").strip()

        groq_model = (
            os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            ).strip()
            or "openai/gpt-oss-120b"
        )

        settings = cls(
            groq_api_key=secret("GROQ_API_KEY"),
            gemini_api_key=secret("GEMINI_API_KEY"),
            groq_model=groq_model,

            max_upload_mb=max(
                1,
                _env_int("MAX_UPLOAD_MB", 10),
            ),

            persist_uploads=_env_bool(
                "PERSIST_UPLOADS",
                False,
            ),
        )

        settings.data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        settings.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        settings.memory_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        return settings
