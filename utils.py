from __future__ import annotations
import re
from html import escape

def make_citation(source: str, page: int | None, chunk_id: str) -> str:
    # Citation format designed for demos / reports
    if page is None:
        return f"[{source} • {chunk_id}]"
    return f"[{source} • p.{page} • {chunk_id}]"

def pretty_source(item: dict) -> str:
    src = item.get("source", "Unknown")
    page = item.get("page", None)
    if page is None:
        return src
    return f"{src} (p.{page})"

def highlight_terms(text: str, query: str, max_terms: int = 10) -> str:
    """
    Simple HTML highlighting for the Evidence Viewer.
    """
    if not text:
        return ""
    terms = _top_terms(query, max_terms=max_terms)
    safe = escape(text)
    # Apply longest-first to reduce partial overlaps
    for t in sorted(set(terms), key=len, reverse=True):
        if len(t) < 3:
            continue
        pattern = re.compile(rf"\\b({re.escape(t)})\\b", re.IGNORECASE)
        safe = pattern.sub(r"<mark style='padding:0 3px; border-radius:4px;'>\\1</mark>", safe)
    # Keep it readable
    return safe.replace("\\n", "<br/>")

def _top_terms(query: str, max_terms: int = 10):
    words = re.findall(r"[a-zA-Z]+", query.lower())
    stop = {
        "the","a","an","and","or","to","of","in","on","for","is","are","be","that","this",
        "do","does","mean","explain","how","what","which","where","used","use","typically",
        "function","functions"
    }
    words = [w for w in words if w not in stop]
    # Keep order but unique
    out = []
    for w in words:
        if w not in out:
            out.append(w)
        if len(out) >= max_terms:
            break
    return out
