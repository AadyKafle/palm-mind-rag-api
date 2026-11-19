
from pathlib import Path
from pypdf import PdfReader


def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF document."""

    reader = PdfReader(file_path)

    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


def extract_txt_text(file_path: str) -> str:
    """Extract text from a TXT document."""

    path = Path(file_path)

    return path.read_text(encoding="utf-8")
