from plant_kb.models import ContentUnit
from plant_kb.chunking import make_chunks

def test_chunk_source_location():
    unit = ContentUnit("pump " * 500, "spreadsheet_row", {"sheet_name": "S1", "row_number": 7})
    chunks = make_chunks([unit], max_chars=150, overlap=20)
    assert len(chunks) > 1
    assert all(c["source_location"]["sheet_name"] == "S1" for c in chunks)
