import json
import os
import threading
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from backend.pdf_processor import process_pdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
_STORE_LOCK = threading.Lock()


def _index_dir() -> Path:
    path = Path(os.getenv("FAISS_INDEX_DIR", "./data/faiss"))
    return path if path.is_absolute() else PROJECT_ROOT / path


def _embedding_model() -> str:
    model = os.getenv("OPENAI_EMBEDDING_MODEL")
    if not model:
        raise RuntimeError("Set OPENAI_EMBEDDING_MODEL in the project .env file.")
    return model


def _client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY in the project .env file.")
    return OpenAI()


class VectorStore:
    """Persist normalized OpenAI embeddings in a local FAISS index."""

    def __init__(self) -> None:
        self.index: faiss.Index | None = None
        self.records: list[dict[str, Any]] = []
        self.index_dir = _index_dir()
        self.index_path = self.index_dir / "documents.index"
        self.metadata_path = self.index_dir / "documents.json"

        index_exists = self.index_path.exists()
        metadata_exists = self.metadata_path.exists()
        if index_exists != metadata_exists:
            raise RuntimeError("FAISS index and metadata files are out of sync.")
        if index_exists:
            self.index = faiss.read_index(str(self.index_path))
            self.records = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            if not isinstance(self.records, list):
                raise RuntimeError("FAISS document metadata must be a JSON list.")
            if self.index.ntotal != len(self.records):
                raise RuntimeError("FAISS index and document metadata are out of sync.")

    @staticmethod
    def embed_text(text: str) -> np.ndarray:
        """Return one L2-normalized embedding vector."""
        if not text.strip():
            raise ValueError("Text must not be empty.")
        response = _client().embeddings.create(
            model=_embedding_model(),
            input=text,
        )
        vector = np.asarray(response.data[0].embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(vector)
        return vector

    def add_texts(
        self,
        texts: list[str],
        metadata: list[dict[str, Any]] | None = None,
    ) -> None:
        if not texts:
            return
        if any(not text.strip() for text in texts):
            raise ValueError("Texts must not be empty.")
        if metadata is not None and len(metadata) != len(texts):
            raise ValueError("Provide one metadata entry per text.")

        with _STORE_LOCK:
            response = _client().embeddings.create(
                model=_embedding_model(),
                input=texts,
            )
            embeddings = sorted(response.data, key=lambda item: item.index)
            vectors = np.asarray(
                [embedding.embedding for embedding in embeddings],
                dtype=np.float32,
            )
            if len(vectors) != len(texts):
                raise RuntimeError("Embedding response count did not match the input texts.")
            faiss.normalize_L2(vectors)

            if self.index is not None and vectors.shape[1] != self.index.d:
                raise ValueError("Embedding dimensions do not match the existing FAISS index.")

            next_index = (
                faiss.clone_index(self.index)
                if self.index is not None
                else faiss.IndexFlatIP(vectors.shape[1])
            )
            next_index.add(vectors)
            next_records = self.records + [
                {
                    "text": text,
                    "metadata": metadata[i] if metadata is not None else {},
                }
                for i, text in enumerate(texts)
            ]

            self.index_dir.mkdir(parents=True, exist_ok=True)
            next_index_path = self.index_path.with_suffix(".index.tmp")
            next_metadata_path = self.metadata_path.with_suffix(".json.tmp")
            try:
                faiss.write_index(next_index, str(next_index_path))
                next_metadata_path.write_text(
                    json.dumps(next_records, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                os.replace(next_index_path, self.index_path)
                os.replace(next_metadata_path, self.metadata_path)
            finally:
                next_index_path.unlink(missing_ok=True)
                next_metadata_path.unlink(missing_ok=True)

            self.index = next_index
            self.records = next_records

    def index_pdf(
        self,
        pdf_bytes: bytes,
        document_id: str,
        filename: str,
        chunk_size: int = 1000,
        overlap: int = 150,
    ) -> int:
        """Extract, chunk, and index a PDF; return the number of indexed chunks."""
        chunks = process_pdf(pdf_bytes, chunk_size=chunk_size, overlap=overlap)
        self.add_texts(
            [chunk.text for chunk in chunks],
            [
                {
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query must not be empty.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")
        if self.index is None:
            return []

        scores, positions = self.index.search(self.embed_text(query), top_k)
        return [
            {
                **self.records[position],
                "score": float(score),
            }
            for score, position in zip(scores[0], positions[0])
            if position >= 0
        ]
