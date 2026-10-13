# UPL Unit 5 Plant Knowledge Chatbot — Modular Starter

Mixed SharePoint documents do not need department-specific folders. Put files in one folder or nested folders; department metadata comes from `config/metadata_overrides.csv`. Unknown department is `UNCLASSIFIED`, never guessed from a folder.

## Setup (Python 3.10/3.11)
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```
Put approved test files under `data/source_files/`, then run:
```bash
python -m plant_kb.cli ingest --input data/source_files --output data/processed --manifest config/metadata_overrides.csv
python -m plant_kb.cli search --input data/processed/document_chunks.jsonl --query "machine changeover"
streamlit run app.py
pytest
```

## Metadata and naming
Manifest columns: `source_key,department,plant_id,unit_id,document_type,document_number,version,approval_status`. In local tests source_key can be filename or relative path; in SharePoint integration prefer the stable SharePoint item ID. Filename is a clue, not authoritative metadata. Proposed name: `UPL_PL01_U05_MAINT_SOP_0001_v01.docx`; confirm actual codes with document control and preserve original SharePoint filename/ID.

## Retrieval modules
- `retrieval/lexical.py`: local BM25
- `retrieval/fusion.py`: Reciprocal Rank Fusion (RRF)
- `retrieval/hyde.py`: HYDE workflow boundary; requires an LLM callback
- `retrieval/reranker.py`: optional cross-encoder; `pip install sentence-transformers`
- `retrieval/pipeline.py`: lexical + semantic fusion, optional reranking
- `generation/llm.py`: OpenAI-compatible LLM adapter; `pip install openai`

These are modular components, not all activated in the local UI. HYDE/semantic search require configured approved endpoints; the LLM adapter needs `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`. Do not send confidential plant data to a personal endpoint.

## Databricks
Replace example catalog/schema names in `databricks/create_tables.sql` and `databricks/load_jsonl_to_delta.py`. Volume and Delta tables are separate Unity Catalog objects. The loader overwrites tables and is development-only; production needs idempotent, version-aware upserts.

## Validation and security
Some source files mention `UNIT:03`, while target context is Unit 5. Warnings preserve the original content. Confirm before live use. Do not push company documents, extracted text, secrets, internal endpoints or company IP to personal GitHub unless explicitly authorized.


## Optional UI integrations
The Streamlit UI has opt-in checkboxes for Vector Search, HYDE, cross-encoder reranking, and LLM answer generation. They remain off by default. Configure approved environment variables in a local `.env` only when policy allows; never commit the real `.env`.
- LLM: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
- Vector Search: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_VECTOR_ENDPOINT`, `DATABRICKS_VECTOR_INDEX`
- Vector Search requires an existing compatible Delta Sync index with text-query embedding configured and searchable columns matching the code.
- Reranker requires `pip install sentence-transformers` and model download/access. Verify company model policy.
- HYDE generates hypothetical text for retrieval only. The final answer must be grounded in retrieved source passages.
