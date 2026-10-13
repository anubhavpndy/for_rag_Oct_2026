from .models import ContentUnit

def make_chunks(units: list[ContentUnit], max_chars: int = 1800, overlap: int = 200) -> list[dict]:
    output = []
    for unit_no, unit in enumerate(units, 1):
        text = (unit.text or "").strip()
        if not text: continue
        pieces, start = [], 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start, end)
                if boundary > start + int(max_chars * 0.65): end = boundary
            pieces.append(text[start:end].strip())
            if end >= len(text): break
            start = max(end - overlap, start + 1)
        for piece_no, piece in enumerate(pieces, 1):
            output.append({"chunk_id": "", "chunk_text": piece,
                "content_type": unit.content_type, "section_name": unit.section_name,
                "source_location": unit.source_location})
    return output
