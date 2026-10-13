from pathlib import Path
from .docx_parser import DocxParser
from .pdf_parser import PdfParser
from .excel_parser import ExcelParser

SUPPORTED = {".docx", ".pdf", ".xlsx", ".xlsm"}

def parser_for(path: Path):
    ext = path.suffix.lower()
    if ext == ".docx": return DocxParser()
    if ext == ".pdf": return PdfParser()
    if ext in {".xlsx", ".xlsm"}: return ExcelParser()
    raise ValueError(f"Unsupported file type: {ext}")
