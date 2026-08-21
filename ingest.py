from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader
from tqdm import tqdm

from chunking import chunk_text
from config import load_settings
from doc_registry import register_document
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def iter_pdf_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix.lower() == ".pdf" else []
    return sorted(target.rglob("*.pdf"))


def ingest_file(path: Path, store: QdrantStore, embedder: GeminiEmbedder, settings) -> None:
    full_text = extract_pdf_text(path)
    if not full_text.strip():
        print(f"  ! {path.name}: no extractable text (scanned image PDF?), skipping")
        return

    chunks = chunk_text(full_text, settings.chunk_size_tokens, settings.chunk_overlap_tokens)
    if not chunks:
        print(f"  ! {path.name}: produced 0 chunks, skipping")
        return

    chunk_texts = [c.text for c in chunks]
    vectors = embedder.embed_documents(chunk_texts)

    title = path.stem.replace("_", " ").replace("-", " ")
    doc_id = register_document(
        source_path=str(path), title=title, full_text=full_text, num_chunks=len(chunks)
    )
    store.upsert_chunks(
        doc_id=doc_id,
        title=title,
        source=str(path),
        chunk_texts=chunk_texts,
        embeddings=vectors,
    )
    print(f"  + {path.name}: {len(chunks)} chunks -> doc_id={doc_id}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python ingest.py <path-to-pdf-or-folder>")
        sys.exit(1)

    target = Path(sys.argv[1]).expanduser().resolve()
    if not target.exists():
        print(f"Path does not exist: {target}")
        sys.exit(1)

    settings = load_settings()
    store = QdrantStore(settings)
    store.ensure_collection()
    embedder = GeminiEmbedder(settings)

    pdf_paths = iter_pdf_paths(target)
    if not pdf_paths:
        print(f"No PDF files found at {target}")
        sys.exit(1)

    print(f"Ingesting {len(pdf_paths)} PDF(s) into collection '{settings.qdrant_collection}'...")
    for path in tqdm(pdf_paths, desc="Ingesting", unit="doc"):
        try:
            ingest_file(path, store, embedder, settings)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {path.name}: failed - {e}")

    print("Done.")


if __name__ == "__main__":
    main()
