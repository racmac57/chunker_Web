from typing import List, Optional, Dict, Any
from functools import lru_cache

from rag_integration import ChromaRAG
from ollama_client import ollama_chat

SYSTEM_PROMPT = (
    "Answer with short, precise steps. "
    "Use only the supplied context for facts. "
    "If context lacks an answer, say so and request a follow-up query. "
    "Cite sources like [1], [2] matching snippet order."
)


def _build_context(snippets: List[Dict[str, Any]]) -> str:
    lines = []
    for i, snippet in enumerate(snippets, 1):
        metadata = snippet.get("metadata", {}) or {}
        source = f"{metadata.get('file_name', 'unknown')}#chunk{metadata.get('chunk_index', '0')}"
        text = snippet.get("document", "")
        lines.append(f"[{i}] {source}\n{text}")
    return "\n\n".join(lines)


@lru_cache(maxsize=256)
def _cached_answer(model: str, user_msg: str, ctx_hash: str, temperature: float) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    return ollama_chat(model=model, messages=messages, options={"temperature": temperature})


def ask_kb(
    query: str,
    n_results: int = 6,
    file_type: Optional[str] = None,
    department: Optional[str] = None,
    tags: Optional[List[str]] = None,
    model: str = "llama3.1:8b",
    temperature: float = 0.2,
) -> Dict[str, Any]:
    rag = ChromaRAG(persist_dir="./chroma_db", collection_name="chunker_knowledge_base")
    hits = rag.search_similar(
        query=query,
        n_results=n_results,
        file_type=file_type,
        department=department,
        tags=tags,
    )

    context_text = _build_context(hits)
    user_msg = (
        f"Query:\n{query}\n\n"
        f"Context snippets:\n{context_text}\n\n"
        "Reply with a direct answer. Then provide 3 bullet action steps. "
        "Cite sources as [n]."
    )

    answer = _cached_answer(model, user_msg, str(hash(context_text)), temperature)
    return {"answer": answer, "hits": hits}

