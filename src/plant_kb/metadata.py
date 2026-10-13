from pathlib import Path
import hashlib, re, csv
from .settings import settings
UNIT_RE = re.compile(r"\bUNIT\s*[:\-]?\s*([0-9]{1,3})\b", re.I)

def stable_document_id(relative_path):
    digest = hashlib.sha256(relative_path.replace("\\", "/").lower().encode()).hexdigest()[:16]
    return "DOC-" + digest.upper()

def unit_mentions(text):
    return sorted({"UNIT_" + m.group(1).zfill(2) for m in UNIT_RE.finditer(text or "")})

def load_metadata_manifest(path):
    path = Path(path); result = {}
    if not path.exists(): return result
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(line for line in f if not line.lstrip().startswith("#")):
            key = (row.get("source_key") or "").strip()
            if key: result[key] = {k: (v or "").strip() for k, v in row.items() if k != "source_key"}
    return result

def document_record(path, root, all_text, digest, manifest=None):
    rel = path.relative_to(root).as_posix()
    override = (manifest or {}).get(rel) or (manifest or {}).get(path.name) or {}
    mentions = unit_mentions(all_text)
    plant_id = override.get("plant_id") or settings.plant_id
    unit_id = override.get("unit_id") or settings.unit_id
    department = override.get("department") or "UNCLASSIFIED"
    warnings = []
    if department == "UNCLASSIFIED":
        warnings.append("Department not supplied by approved metadata; review before production use.")
    for found in mentions:
        if found != unit_id:
            warnings.append(f"Source text mentions {found}; metadata unit is {unit_id}. Review before production.")
    return {
        "document_id": override.get("document_number") or stable_document_id(rel),
        "source_key": rel, "filename": path.name, "relative_path": rel,
        "file_type": path.suffix.lower().lstrip("."), "department": department,
        "plant_id": plant_id, "unit_id": unit_id,
        "document_type": override.get("document_type") or "UNKNOWN",
        "version": override.get("version") or digest[:12],
        "approval_status": override.get("approval_status") or "PENDING_REVIEW",
        "source_uri": rel, "status": "PROCESSED", "content_sha256": digest,
        "detected_unit_mentions": mentions, "metadata_warnings": warnings,
    }
