from __future__ import annotations
from typing import List, Dict, Any
import re

class SparseKeywordRetriever:
    """
    Very simple baseline: keyword overlap count (no BM25).
    """
    def __init__(self, texts: List[str], metas: List[Dict[str, Any]]):
        self.texts = texts
        self.metas = metas
        self._tokens = [set(_tok(t)) for t in texts]

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        q = set(_tok(query))
        scored = []
        for i, toks in enumerate(self._tokens):
            overlap = len(q & toks)
            if overlap == 0:
                continue
            scored.append((float(overlap), i))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, i in scored[:top_k]:
            meta = self.metas[i]
            out.append({
                "chunk_id": meta["chunk_id"],
                "source": meta["source"],
                "page": meta.get("page"),
                "score": score,
                "text": self.texts[i],
            })
        return out


class TfidfRetriever:
    """
    Lightweight semantic baseline using TF-IDF cosine similarity.
    """
    def __init__(self, texts: List[str], metas: List[Dict[str, Any]]):
        self.texts = texts
        self.metas = metas
        self._vectorizer = None
        self._X = None

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                max_features=150000,
            )
            self._X = self._vectorizer.fit_transform(texts)
        except Exception as e:
            # If sklearn isn't available, degrade gracefully
            self._vectorizer = None
            self._X = None

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self._vectorizer is None or self._X is None:
            # Fallback to sparse overlap if TF-IDF unavailable
            return SparseKeywordRetriever(self.texts, self.metas).search(query, top_k=top_k)

        from sklearn.metrics.pairwise import cosine_similarity
        qv = self._vectorizer.transform([query])
        sims = cosine_similarity(qv, self._X).ravel()
        idxs = sims.argsort()[::-1][:top_k]
        out = []
        for i in idxs:
            score = float(sims[i])
            if score <= 0:
                continue
            meta = self.metas[i]
            out.append({
                "chunk_id": meta["chunk_id"],
                "source": meta["source"],
                "page": meta.get("page"),
                "score": score,
                "text": self.texts[i],
            })
        return out


def _tok(s: str):
    return re.findall(r"[a-zA-Z]+", s.lower())
