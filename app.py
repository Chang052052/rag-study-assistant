import streamlit as st
from rag_core import RAGIndex, RetrievalMethod, build_answer_from_evidence
from utils import highlight_terms, pretty_source
from pathlib import Path

st.set_page_config(
    page_title="Citation-Grounded RAG Study Assistant",
    page_icon="📘",
    layout="wide",
)

# ---------- Header ----------
st.markdown(
    """
    <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
      <div>
        <h2 style="margin:0;">📘 Citation-Grounded RAG Study Assistant</h2>
        <div style="opacity:0.8;">Exam-oriented PDF study • evidence-first retrieval • explicit citations</div>
      </div>
      <div style="text-align:right; opacity:0.85;">
        <div><b>Demo focus:</b> retrieval + evidence recall</div>
        <div style="font-size:12px;">No hallucinations: answers are built only from retrieved chunks</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ---------- Session state ----------
if "index" not in st.session_state:
    st.session_state.index = None
if "corpus_name" not in st.session_state:
    st.session_state.corpus_name = "Unnamed corpus"
if "last_results" not in st.session_state:
    st.session_state.last_results = {}

# ---------- Sidebar (Control Panel) ----------
with st.sidebar:
    st.header("⚙️ Control Panel")

    st.subheader("Corpus")
    st.session_state.corpus_name = st.text_input("Corpus name", st.session_state.corpus_name)

    uploaded = st.file_uploader(
        "Upload PDFs (10–20 recommended)",
        type=["pdf"],
        accept_multiple_files=True
    )

    colA, colB = st.columns(2)
    with colA:
        chunk_size = st.number_input("Chunk size (chars)", min_value=400, max_value=2400, value=1200, step=100)
    with colB:
        chunk_overlap = st.number_input("Overlap (chars)", min_value=0, max_value=800, value=200, step=50)

    st.subheader("Retrieval")
    k_top = st.slider("Top-K", min_value=1, max_value=10, value=5, step=1)

    method = st.radio(
        "Method",
        options=[
            "Sparse (Keyword overlap)",
            "Semantic baseline (TF-IDF)"
        ],
        index=0
    )

    st.subheader("Actions")
    build_clicked = st.button("🔧 Build / Rebuild Index", type="primary", use_container_width=True)
    clear_clicked = st.button("🧹 Clear Index", use_container_width=True)

    st.caption("Tip: After indexing, use the tabs to ask questions, run mini experiments, and explore the corpus.")

if clear_clicked:
    st.session_state.index = None
    st.session_state.last_results = {}
    st.toast("Index cleared.", icon="🧹")

# ---------- Index build ----------
if build_clicked:
    if not uploaded:
        st.error("Please upload at least one PDF before building the index.")
    else:
        with st.spinner("Indexing PDFs… (extracting text, chunking, building TF-IDF)"):
            idx = RAGIndex(
                chunk_size=int(chunk_size),
                chunk_overlap=int(chunk_overlap),
            )
            idx.add_pdfs(uploaded)
            idx.build()
            st.session_state.index = idx
        st.success(f"Indexed {idx.stats()['documents']} PDFs • {idx.stats()['chunks']} chunks")

index: RAGIndex | None = st.session_state.index

# ---------- Main tabs ----------
tab1, tab2, tab3 = st.tabs(["🧠 Study / Ask", "🧪 Retrieval Experiment", "📚 Corpus Explorer"])

# ==========================================================
# TAB 1: Study / Ask
# ==========================================================
with tab1:
    if not index:
        st.info("Upload PDFs and click **Build / Rebuild Index** to start.")
    else:
        left, right = st.columns([0.42, 0.58], gap="large")

        with left:
            st.subheader("✍️ Exam-oriented Question")
            q = st.text_area(
                "Enter a question (definition / proof / method / application / location-based)",
                value="What does it mean for a function to be holomorphic on a domain?",
                height=120
            )

            qtype = st.selectbox(
                "Question type (used for UI clarity)",
                ["Definition", "Proof / Method", "Application", "Location-based"],
                index=0
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                run_clicked = st.button("🔎 Retrieve Evidence", use_container_width=True, type="primary")
            with col2:
                gen_clicked = st.button("🧾 Build Answer", use_container_width=True)
            with col3:
                st.metric("Corpus", st.session_state.corpus_name)

            st.caption("Evidence-first: you can retrieve without generating. Answer is compiled only from retrieved chunks.")

        with right:
            st.subheader("🔍 Retrieval Results & Evidence")

            # Determine retrieval method
            rmethod = RetrievalMethod.SPARSE if method.startswith("Sparse") else RetrievalMethod.TFIDF

            if run_clicked:
                results = index.search(q, top_k=int(k_top), method=rmethod)
                st.session_state.last_results = {"q": q, "method": rmethod.value, "results": results}

            if not st.session_state.last_results:
                st.info("Click **Retrieve Evidence** to see Top-K chunks.")
            else:
                results = st.session_state.last_results["results"]
                # Layout: two panels (ranking + evidence)
                rcol, ecol = st.columns([0.46, 0.54], gap="large")

                with rcol:
                    st.markdown("**Ranking panel**")
                    for i, item in enumerate(results, start=1):
                        src = pretty_source(item)
                        score_label = "overlap" if rmethod == RetrievalMethod.SPARSE else "cosine"
                        st.markdown(
                            f"""
                            <div style="border:1px solid rgba(0,0,0,0.08); border-radius:12px; padding:10px 12px; margin-bottom:10px;">
                              <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div><b>Rank {i}</b> • <span style="opacity:0.8;">{src}</span></div>
                                <div style="font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; opacity:0.85;">
                                  {score_label}={item['score']:.3f}
                                </div>
                              </div>
                              <div style="margin-top:6px; font-size:12px; opacity:0.85;">
                                Chunk ID: <span style="font-family:ui-monospace, monospace;">{item['chunk_id']}</span>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    selected = st.selectbox(
                        "Select a chunk to view as evidence",
                        options=list(range(1, len(results) + 1)),
                        index=0
                    ) - 1

                with ecol:
                    item = results[selected]
                    st.markdown("**Evidence viewer**")
                    st.markdown(
                        f"<div style='opacity:0.85; margin-bottom:6px;'>{pretty_source(item)} • Chunk <span style='font-family:ui-monospace,monospace;'>{item['chunk_id']}</span></div>",
                        unsafe_allow_html=True
                    )
                    highlighted = highlight_terms(item["text"], q, max_terms=10)
                    st.markdown(
                        f"<div style='border-left:4px solid rgba(30,90,200,0.4); padding:10px 12px; background:rgba(0,0,0,0.02); border-radius:8px;'>{highlighted}</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown("**Citations**")
                    st.code(item["citation"], language="text")

            # Answer panel
            st.divider()
            st.subheader("🧾 Citation-grounded Answer")
            if gen_clicked:
                if not st.session_state.last_results:
                    st.warning("Retrieve evidence first.")
                else:
                    results = st.session_state.last_results["results"]
                    answer = build_answer_from_evidence(
                        question=st.session_state.last_results["q"],
                        evidence=results[: min(5, len(results))],
                        max_sentences=6,
                    )
                    st.markdown(answer)

            else:
                st.caption("Click **Build Answer** to compile an answer strictly from the retrieved evidence.")

# ==========================================================
# TAB 2: Retrieval Experiment
# ==========================================================
with tab2:
    if not index:
        st.info("Build an index first.")
    else:
        st.subheader("🧪 Mini Retrieval Experiment (Evidence Recall)")
        st.caption("Compare Sparse keyword overlap vs TF-IDF semantic baseline on Q3, Q7, Q18. Success = at least one relevant chunk in Top-3.")

        default_queries = {
            "Q3": "What does it mean for a function to be holomorphic on a domain?",
            "Q7": "State the Cauchy–Riemann equations and explain their role in complex differentiability.",
            "Q18": "How are power series used to represent holomorphic functions locally?",
        }

        with st.expander("Edit the experiment queries", expanded=False):
            for key in list(default_queries.keys()):
                default_queries[key] = st.text_input(key, default_queries[key])

        k_eval = st.select_slider("Evaluate at K", options=[3, 5], value=3)

        run_eval = st.button("▶ Run Experiment", type="primary")
        if run_eval:
            rows = []
            for qid, qtext in default_queries.items():
                for m in [RetrievalMethod.SPARSE, RetrievalMethod.TFIDF]:
                    res = index.search(qtext, top_k=int(k_eval), method=m)
                    # Heuristic relevance judgement: if query's key terms appear, or contains hallmark phrase
                    # This is for demo — in a real study you'd label manually.
                    joined = " ".join([r["text"].lower() for r in res])
                    if qid == "Q7":
                        relevant = ("cauchy" in joined and "riemann" in joined) or ("u_x" in joined and "v_y" in joined)
                    elif qid == "Q18":
                        relevant = ("power series" in joined) or ("radius of convergence" in joined) or ("expansion" in joined)
                    else:
                        relevant = ("holomorphic" in joined and "differentiable" in joined)

                    rows.append({
                        "Question": qid,
                        "Method": m.value,
                        f"Recall@{k_eval}": "✅ Yes" if relevant else "❌ No",
                        "Top chunk": pretty_source(res[0]) if res else "—",
                    })

            # Display as a compact table
            st.dataframe(rows, use_container_width=True, hide_index=True)

            st.markdown("### Inspect retrieved chunks")
            pick_q = st.selectbox("Question", list(default_queries.keys()), index=0)
            pick_m = st.selectbox("Method", [RetrievalMethod.SPARSE.value, RetrievalMethod.TFIDF.value], index=0)
            method_map = {RetrievalMethod.SPARSE.value: RetrievalMethod.SPARSE, RetrievalMethod.TFIDF.value: RetrievalMethod.TFIDF}

            res = index.search(default_queries[pick_q], top_k=int(k_eval), method=method_map[pick_m])
            for i, item in enumerate(res, start=1):
                st.markdown(f"**Rank {i}** • {pretty_source(item)} • score={item['score']:.3f}")
                st.markdown(
                    f"<div style='border-left:4px solid rgba(0,0,0,0.15); padding:8px 10px; background:rgba(0,0,0,0.02); border-radius:8px;'>{highlight_terms(item['text'], default_queries[pick_q])}</div>",
                    unsafe_allow_html=True
                )
                st.code(item["citation"], language="text")
                st.divider()

# ==========================================================
# TAB 3: Corpus Explorer
# ==========================================================
with tab3:
    if not index:
        st.info("Build an index first.")
    else:
        st.subheader("📚 Corpus Explorer")
        stats = index.stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("PDFs", stats["documents"])
        c2.metric("Chunks", stats["chunks"])
        c3.metric("Chunk size", stats["chunk_size"])

        docs = index.list_documents()
        pick_doc = st.selectbox("Select a document", docs, index=0)
        doc_chunks = index.get_chunks_for_document(pick_doc)

        st.caption("Showing chunk boundaries and citations (page-level if available).")
        for ch in doc_chunks[:200]:  # guard for huge corpora
            st.markdown(f"**{ch['chunk_id']}** • p.{ch.get('page', '—')} • {Path(ch['source']).name}")
            st.markdown(
                f"<div style='border:1px solid rgba(0,0,0,0.08); padding:10px 12px; border-radius:10px; background:rgba(0,0,0,0.015);'>{ch['text']}</div>",
                unsafe_allow_html=True
            )
            st.code(ch["citation"], language="text")
            st.divider()
