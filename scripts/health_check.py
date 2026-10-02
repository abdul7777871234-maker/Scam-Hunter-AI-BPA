from config.settings import Settings
from rag.ingestion import KnowledgeBase

s = Settings.from_runtime()
kb = KnowledgeBase(s)
print("FAISS vectors:", kb.store.count)
print("Groq configured:", bool(s.groq_api_key))
print("Gemini configured:", bool(s.gemini_api_key))
