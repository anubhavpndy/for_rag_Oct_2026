import argparse, json
from .ingestion import ingest_directory
from .retrieval.lexical import load_jsonl, LexicalRetriever
from .orchestration.answer_builder import build_response

def main():
    parser = argparse.ArgumentParser("plant-kb")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--input", default="data/source_files")
    ingest.add_argument("--output", default="data/processed")
    ingest.add_argument("--manifest", default="config/metadata_overrides.csv")
    search = sub.add_parser("search")
    search.add_argument("--input", default="data/processed/document_chunks.jsonl")
    search.add_argument("--query", required=True)
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--department")
    search.add_argument("--unit-id")
    args = parser.parse_args()
    if args.command == "ingest":
        report = ingest_directory(args.input, args.output, args.manifest)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if report["files_failed"]: raise SystemExit(1)
    else:
        chunks = load_jsonl(args.input)
        results = LexicalRetriever(chunks).search(args.query, args.top_k, args.department, args.unit_id)
        print(build_response(results))

if __name__ == "__main__":
    main()
