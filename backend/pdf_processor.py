from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


@dataclass(frozen=True)
class PDFPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    page_number: int
    text: str


def extract_pdf_pages(pdf_bytes: bytes) -> list[PDFPage]:
    """Extract selectable text from a PDF, keeping its original page numbers."""
    if not pdf_bytes:
        raise ValueError("The PDF file is empty.")

    reader = PdfReader(BytesIO(pdf_bytes))
    pages = [
        PDFPage(page_number=page_number, text=text)
        for page_number, page in enumerate(reader.pages, start=1)
        if (text := " ".join((page.extract_text() or "").split()))
    ]
    if not pages:
        raise ValueError(
            "No selectable text was found in this PDF. Scanned PDFs need OCR before indexing."
        )
    return pages


def chunk_pages(
    pages: list[PDFPage],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[TextChunk]:
    """Split page text into bounded, overlapping chunks with page provenance."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size.")

    chunks: list[TextChunk] = []
    chunk_index = 0
    for page in pages:
        text = " ".join(page.text.split())
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start, end)
                if boundary > start:
                    end = boundary

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    TextChunk(
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        text=chunk_text,
                    )
                )
                chunk_index += 1

            if end == len(text):
                break

            next_start = end - overlap
            while next_start > start and not text[next_start - 1].isspace():
                next_start -= 1
            start = next_start if next_start > start else end

    return chunks


def process_pdf(
    pdf_bytes: bytes,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[TextChunk]:
    """Extract a PDF's text and return page-tagged chunks ready for indexing."""
    return chunk_pages(extract_pdf_pages(pdf_bytes), chunk_size, overlap)
