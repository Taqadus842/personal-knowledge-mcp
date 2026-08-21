from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TypedDict

REGISTRY_DIR = Path(__file__).parent / "data"
REGISTRY_FILE = REGISTRY_DIR / "registry.json"
FULLTEXT_DIR = REGISTRY_DIR / "fulltext"


class DocMeta(TypedDict):
    doc_id: str
    title: str
    source_path: str
    num_chunks: int
    ingested_at: str


def _load() -> dict[str, DocMeta]:
    if not REGISTRY_FILE.exists():
        return {}
    return json.loads(REGISTRY_FILE.read_text())


def _save(registry: dict[str, DocMeta]) -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2))


def make_doc_id(source_path: str) -> str:
    return hashlib.sha1(source_path.encode("utf-8")).hexdigest()[:16]


def register_document(source_path: str, title: str, full_text: str, num_chunks: int) -> str:
    doc_id = make_doc_id(source_path)
    FULLTEXT_DIR.mkdir(parents=True, exist_ok=True)
    (FULLTEXT_DIR / f"{doc_id}.txt").write_text(full_text)

    registry = _load()
    registry[doc_id] = DocMeta(
        doc_id=doc_id,
        title=title,
        source_path=source_path,
        num_chunks=num_chunks,
        ingested_at=datetime.now(timezone.utc).isoformat(),
    )
    _save(registry)
    return doc_id


def list_documents() -> list[DocMeta]:
    return list(_load().values())


def get_document_meta(doc_id: str) -> Optional[DocMeta]:
    return _load().get(doc_id)


def get_document_text(doc_id: str) -> Optional[str]:
    path = FULLTEXT_DIR / f"{doc_id}.txt"
    if not path.exists():
        return None
    return path.read_text()
