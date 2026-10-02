# 🛡️ ScamHunter AI

ScamHunter AI is an evidence-first scam investigation assistant built with
Streamlit, FAISS RAG, persistent embeddings, multi-agent orchestration,
DuckDuckGo research, memory, search caching, Groq and automatic Gemini
fallback.

## Features

- Premium light/dark/accent UI
- No manual model selector
- Groq primary reasoning path
- Gemini automatic fallback chain
- CrewAI specialist-role architecture
- Conditional multi-agent routing
- PDF/DOCX/TXT/MD knowledge base
- FAISS persistent vector index
- SHA-256 incremental document indexing
- Search cache
- Conversation/semantic/research memory
- Evidence citations
- Contradiction analysis
- Prompt-injection defense
- Upload validation
- Sample synthetic scam-reference documents
- Google Colab + Cloudflare friendly

## Secrets

Create Streamlit secrets:

```toml
GROQ_API_KEY = "..."
GEMINI_API_KEY = "..."
```

Never commit real secrets.

## Install

```bash
pip install -r requirements.txt
```

## Build the knowledge base

The sample documents are already included.

```bash
python scripts/build_knowledge_base.py
```

This creates/updates the FAISS index. Unchanged source documents should be
skipped by a production-grade manifest workflow; if you change the ingestion
implementation or embedding model, rebuild intentionally.

## Run

```bash
streamlit run app.py
```

## Colab

Install requirements, place secrets in the runtime/Streamlit secrets mechanism,
then run Streamlit. Cloudflare Tunnel can expose the local Streamlit port.

## Gemini fallback

The application tries:

1. gemini-3.8-flash
2. gemini-3.7-flash
3. gemini-3.6-flash
4. gemini-3.5-flash
5. gemini-3-flash

The user does not choose models. Provider routing is backend-only.

## Important

The included knowledge-base PDFs are synthetic demonstration material. They
are intended for RAG testing and are not official legal, financial, banking,
or law-enforcement guidance.

The system should not be treated as a guarantee that a message, website,
person, or offer is safe or fraudulent. It presents evidence and uncertainty
for human review.
