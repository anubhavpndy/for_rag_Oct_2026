from pathlib import Path
import hashlib, json
from .settings import settings
from .metadata import document_record, load_metadata_manifest
from .chunking import make_chunks
from .parsers.factory import SUPPORTED, parser_for

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()

def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

def ingest_directory(input_dir, output_dir, manifest_path="config/metadata_overrides.csv"):
    root, out = Path(input_dir).resolve(), Path(output_dir).resolve()
    if not root.exists(): raise FileNotFoundError(f"Input directory not found: {root}")
    paths = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    manifest = load_metadata_manifest(manifest_path)
    docs, chunks = [], []
    report = {"configured_plant_id": settings.plant_id, "configured_unit_id": settings.unit_id,
              "files_discovered": len(paths), "files_processed": 0, "chunks_created": 0,
              "files_failed": [], "warnings": [],
              "metadata_note": "Department is never inferred from folder names; missing department is UNCLASSIFIED."}
    for path in paths:
        try:
            parsed = parser_for(path).parse(path)
            text = "\n".join(u.text for u in parsed.content_units)
            digest = sha256(path)
            doc = document_record(path, root, text, digest, manifest)
            doc_chunks = make_chunks(parsed.content_units, settings.chunk_chars, settings.overlap)
            for i, chunk in enumerate(doc_chunks, 1):
                chunk.update({"chunk_id": f"{doc['document_id']}-CH{i:06d}",
                    "document_id": doc["document_id"], "filename": doc["filename"],
                    "department": doc["department"], "plant_id": doc["plant_id"],
                    "unit_id": doc["unit_id"], "file_type": doc["file_type"],
                    "document_version": doc["version"], "source_uri": doc["source_uri"],
                    "approval_status": doc["approval_status"],
                    "metadata_warnings": doc["metadata_warnings"]})
            doc["chunk_count"] = len(doc_chunks); doc["parser_warnings"] = parsed.warnings
            docs.append(doc); chunks.extend(doc_chunks); report["files_processed"] += 1
            report["warnings"] += [{"filename": path.name, "warning": w}
                                   for w in parsed.warnings + doc["metadata_warnings"]]
        except Exception as exc:
            report["files_failed"].append({"filename": str(path.relative_to(root)), "error": str(exc)})
    report["chunks_created"] = len(chunks)
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "documents.jsonl", docs)
    write_jsonl(out / "document_chunks.jsonl", chunks)
    (out / "ingestion_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
