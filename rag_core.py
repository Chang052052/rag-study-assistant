from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Iterable
import re
import math

from pdf_parser import extract_pdf_pages_text
from retrievers import SparseKeywordRetriever, TfidfRetriever
from utils import make_citation


class RetrievalMethod(str, Enum):
    SPARSE = "Sparse (Keyword overlap)"
    TFIDF = "Semantic baseline (TF-IDF)"


@dataclass
class Chunk:
    chunk_id: str
    source: str
    page: int | None
    text: str


class RAGIndex:
    """
    A small, research-oriented index:
    - Extract per-page text from PDFs
    - Chunk with overlap
    - Provide two retrieval baselines: sparse keyword overlap + TF-IDF
    """
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        self.chunk_size = int(chunk_size)
        self.chunk_overlap = int(chunk_overlap)
        self._chunks: List[Chunk] = []
        self._docs: List[str] = []
        self._built = False
        self._sparse = None
        self._tfidf = None

    def add_pdfs(self, uploaded_files: Iterable):
        # uploaded_files are Streamlit UploadedFile objects
        self._chunks = []
        self._docs = []
        for uf in uploaded_files:
            name = uf.name
            self._docs.append(name)
            pages = extract_pdf_pages_text(uf)
            # Make chunks per page so we can cite page numbers
            for page_idx, page_text in enumerate(pages, start=1):
                for j, t in enumerate(_chunk_text(page_text, self.chunk_size, self.chunk_overlap), start=1):
                    chunk_id = f"{_safe_id(name)}-p{page_idx}-c{j:03d}"
                    self._chunks.append(Chunk(
                        chunk_id=chunk_id,
                        source=name,
                        page=page_idx,
                        text=t.strip()
                    ))

    def build(self):
        texts = [c.text for c in self._chunks]
        metas = [{"chunk_id": c.chunk_id, "source": c.source, "page": c.page} for c in self._chunks]

        self._sparse = SparseKeywordRetriever(texts=texts, metas=metas)
        self._tfidf = TfidfRetriever(texts=texts, metas=metas)
        self._built = True

    def stats(self) -> Dict[str, Any]:
        return {
            "documents": len(set(self._docs)),
            "chunks": len(self._chunks),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }

    def list_documents(self) -> List[str]:
        return sorted(list(set(self._docs)))

    def get_chunks_for_document(self, doc_name: str) -> List[Dict[str, Any]]:
        out = []
        for c in self._chunks:
            if c.source == doc_name:
                out.append({
                    "chunk_id": c.chunk_id,
                    "source": c.source,
                    "page": c.page,
                    "text": c.text,
                    "citation": make_citation(c.source, c.page, c.chunk_id),
                })
        return out

    def search(self, query: str, top_k: int = 5, method: RetrievalMethod = RetrievalMethod.SPARSE) -> List[Dict[str, Any]]:
        if not self._built:
            raise RuntimeError("Index not built. Call build() first.")

        top_k = int(top_k)
        if method == RetrievalMethod.SPARSE:
            hits = self._sparse.search(query, top_k=top_k)
        else:
            hits = self._tfidf.search(query, top_k=top_k)

        # Attach full text + citation
        results = []
        for h in hits:
            results.append({
                "chunk_id": h["chunk_id"],
                "source": h["source"],
                "page": h.get("page"),
                "text": h["text"],
                "score": float(h["score"]),
                "citation": make_citation(h["source"], h.get("page"), h["chunk_id"]),
            })
        return results


def build_answer_from_evidence(question: str, evidence: List[Dict[str, Any]], max_sentences: int = 6) -> str:
    """
    Evidence-only answer builder (extractive / citation-anchored).
    - Selects a few most informative sentences from evidence chunks
    - Appends explicit citations
    """
    # Collect candidate sentences with their citations
    sent_pool = []
    for e in evidence:
        sents = _split_sentences(e["text"])
        for s in sents:
            clean = s.strip()
            if len(clean) < 40:
                continue
            sent_pool.append((clean, e["citation"], e["score"]))

    if not sent_pool:
        return "I couldn't find sufficient evidence in the retrieved chunks to answer this question."

    # Score: combine retriever score and sentence coverage of query terms
    q_terms = set(_tokenize(question))
    scored = []
    for sent, cit, base_score in sent_pool:
        t = set(_tokenize(sent))
        overlap = len(q_terms & t)
        scored.append((base_score + 0.05 * overlap, sent, cit))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Pick diverse citations to avoid repeating same chunk too much
    chosen = []
    used_cits = set()
    for _, sent, cit in scored:
        if len(chosen) >= max_sentences:
            break
        key = cit
        if key in used_cits and len(chosen) < max_sentences // 2:
            continue
        chosen.append((sent, cit))
        used_cits.add(key)

    # Compose answer
    lines = []
    lines.append("**Answer (evidence-grounded):**")
    lines.append("")
    for sent, cit in chosen:
        lines.append(f"- {sent}  \n  `{cit}`")
    lines.append("")
    lines.append("**Notes:** This answer is compiled *only* from retrieved PDF evidence; if it feels incomplete, increase Top‑K or rebuild the index with different chunking.")
    return "\n".join(lines)


# ---------------- helpers ----------------
def _chunk_text(text: str, size: int, overlap: int):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if size <= 0:
        return [text]
    step = max(1, size - max(0, overlap))
    chunks = []
    for start in range(0, len(text), step):
        end = min(len(text), start + size)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(text):
            break
    return chunks


def _safe_id(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()


def _split_sentences(text: str):
    # Conservative splitter for lecture notes / math
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _tokenize(s: str):
    return re.findall(r"[a-zA-Z]+", s.lower())
