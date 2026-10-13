from pathlib import Path
import os
import streamlit as st
from plant_kb.retrieval.lexical import load_jsonl, LexicalRetriever
from plant_kb.retrieval.vector_search import DatabricksVectorSearchRetriever
from plant_kb.retrieval.pipeline import HybridRetrievalPipeline
from plant_kb.retrieval.reranker import CrossEncoderReranker
from plant_kb.retrieval.hyde import hyde_search
from plant_kb.generation.llm import OpenAICompatibleLLM
from plant_kb.orchestration.answer_builder import build_response

st.set_page_config(page_title="Plant Knowledge — Local Demo", layout="wide")
st.title("UPL Unit 5 — Plant Knowledge Chatbot")
st.caption("Local mode uses BM25. Optional LLM, HYDE, Vector Search and reranking require explicitly configured approved endpoints/models.")

chunks_path = Path("data/processed/document_chunks.jsonl")
if not chunks_path.exists():
    st.warning("Run ingestion first: python -m plant_kb.cli ingest --input data/source_files --output data/processed")
    st.stop()

chunks = load_jsonl(chunks_path)
departments = sorted({c.get("department", "") for c in chunks if c.get("department")})
query = st.text_input("Question or keywords", placeholder="e.g., machine changeover or label printing")
department = st.selectbox("Department filter", ["All"] + departments)
top_k = st.slider("Retrieved passages", 1, 10, 5)

use_vector = st.checkbox("Use Databricks Vector Search (requires configured company endpoint/index)", value=False)
use_hyde = st.checkbox("Use HYDE query expansion (requires configured LLM)", value=False)
use_reranker = st.checkbox("Rerank candidates with cross-encoder (downloads/loads a model)", value=False)
use_llm = st.checkbox("Generate a grounded LLM answer (requires configured approved endpoint)", value=False)

if st.button("Search", type="primary") and query.strip():
    filtered_chunks = [c for c in chunks if department == "All" or c.get("department") == department]
    lexical = LexicalRetriever(filtered_chunks)
    semantic = None
    llm = None
    reranker = None

    if use_vector:
        semantic = DatabricksVectorSearchRetriever()

    if use_hyde or use_llm:
        try:
            llm = OpenAICompatibleLLM()
        except Exception as exc:
            st.error(f"LLM is not configured: {exc}")
            st.stop()

    if use_reranker:
        try:
            reranker = CrossEncoderReranker()
        except Exception as exc:
            st.error(f"Reranker could not be initialized: {exc}")
            st.stop()

    pipeline = HybridRetrievalPipeline(lexical, semantic_retriever=semantic, reranker=reranker)
    try:
        if use_hyde and llm:
            # HYDE is used as an alternate lexical retrieval query in local mode.
            # For full semantic HYDE, use a Vector Search index configured for text queries.
            results = hyde_search(query, llm.hypothetical_document, lexical, top_k=max(top_k, 8))
            if semantic:
                semantic_results = semantic.search(query, top_k=max(top_k, 8))
                from plant_kb.retrieval.fusion import reciprocal_rank_fusion
                results = reciprocal_rank_fusion([results, semantic_results], top_k=max(top_k, 10))
                if reranker:
                    results = reranker.rerank(query, results, top_k=top_k)
                else:
                    results = results[:top_k]
        else:
            results = pipeline.search(query, top_k=top_k, use_reranker=use_reranker)
    except Exception as exc:
        st.error(f"Retrieval failed: {exc}")
        st.stop()

    if use_llm and llm:
        try:
            st.markdown(llm.answer(query, results))
        except Exception as exc:
            st.error(f"LLM generation failed: {exc}")
            st.markdown(build_response(results))
    else:
        st.markdown(build_response(results))

    with st.expander("Source/debug metadata"):
        st.json([{k: r.get(k) for k in ("document_id", "chunk_id", "filename", "department",
            "source_location", "retrieval_method", "retrieval_score", "rrf_score", "reranker_score")} for r in results])
