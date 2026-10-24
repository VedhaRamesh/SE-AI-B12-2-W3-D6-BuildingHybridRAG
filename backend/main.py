import asyncio
import os
import uuid
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status

# Load the project-root .env even when Uvicorn is started from another directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def project_path(variable: str, default: str) -> Path:
    """Resolve relative folder settings from the project root."""
    path = Path(os.getenv(variable, default))
    return path if path.is_absolute() else PROJECT_ROOT / path


UPLOAD_DIR = project_path("UPLOAD_DIR", "./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024

app = FastAPI(title="Hybrid RAG API", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: Annotated[UploadFile, File()]):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    try:
        # Read at most one byte past the limit so oversized files are rejected.
        contents = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
        )

    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    # Use a generated filename so user-provided paths can never control where files are saved.
    document_id = uuid.uuid4().hex
    saved_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        await asyncio.to_thread(saved_path.write_bytes, contents)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Could not save the uploaded PDF.") from exc

    return {
        "document_id": document_id,
        "filename": Path(file.filename).name,
        "size_bytes": len(contents),
        "status": "uploaded",
    }