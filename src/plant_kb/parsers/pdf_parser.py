from pathlib import Path
from pypdf import PdfReader
from ..models import ContentUnit, ParsedDocument

class PdfParser:
    def parse(self, path: Path) -> ParsedDocument:
        reader = PdfReader(str(path))
        units, warnings = [], []
        for pno, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                units.append(ContentUnit(text, "pdf_page", {"page_number": pno}))
        if not units:
            warnings.append("No selectable PDF text found; scanned PDFs need an approved OCR step.")
        return ParsedDocument(units, warnings)
