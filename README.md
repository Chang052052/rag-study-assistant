# Citation-Grounded RAG Study Assistant (Streamlit UI)

A small research-oriented demo UI for exam-style PDF study:
- Evidence-first retrieval
- Two baselines: keyword overlap (sparse) vs TF‑IDF semantic baseline
- Explicit citations at chunk + page level (when available)

## Quick start

1) Install deps:
- `pip install -r requirements.txt`

2) Run:
- `streamlit run app.py`

## Notes
- Answers are **compiled only from retrieved PDF evidence** (no LLM calls).
- For best results, index 10–20 PDFs (lecture notes + tutorials + past papers).
- If TF‑IDF is unavailable, it falls back to sparse retrieval.
