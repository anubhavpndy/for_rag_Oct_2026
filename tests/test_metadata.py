from pathlib import Path
from plant_kb.metadata import department_for, unit_mentions, stable_document_id

def test_department():
    root = Path("/tmp/source")
    assert department_for(root / "Maintenance" / "a.docx", root) == "Maintenance"

def test_unit_detection():
    assert "UNIT_03" in unit_mentions("UPL LIMITED UNIT:03")

def test_stable_id():
    assert stable_document_id("Maintenance/a.docx") == stable_document_id("Maintenance/a.docx")
