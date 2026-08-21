from __future__ import annotations

import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from config import Settings


@dataclass
class SearchHit:
    text: str
    score: float
    doc_id: str
    source: str
    title: str
    chunk_index: int


class QdrantStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )

    def ensure_collection(self) -> None:
        existing = [c.name for c in self.client.get_collections().collections]
        if self.settings.qdrant_collection in existing:
            return
        self.client.create_collection(
            collection_name=self.settings.qdrant_collection,
            vectors_config=qm.VectorParams(
                size=self.settings.embed_dim,
                distance=qm.Distance.COSINE,
            ),
        )

    @staticmethod
    def _point_id(doc_id: str, chunk_index: int) -> str:
        # Deterministic UUID so re-ingesting the same doc/chunk overwrites
        # cleanly instead of creating duplicate points.
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}:{chunk_index}"))

    def upsert_chunks(
        self,
        doc_id: str,
        title: str,
        source: str,
        chunk_texts: list[str],
        embeddings: list[list[float]],
    ) -> int:
        points = [
            qm.PointStruct(
                id=self._point_id(doc_id, i),
                vector=vec,
                payload={
                    "doc_id": doc_id,
                    "title": title,
                    "source": source,
                    "chunk_index": i,
                    "text": text,
                },
            )
            for i, (text, vec) in enumerate(zip(chunk_texts, embeddings))
        ]
        self.client.upsert(collection_name=self.settings.qdrant_collection, points=points)
        return len(points)

    def search(self, query_vector: list[float], top_k: int) -> list[SearchHit]:
        results = self.client.query_points(
            collection_name=self.settings.qdrant_collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        ).points
        return [
            SearchHit(
                text=r.payload["text"],
                score=r.score,
                doc_id=r.payload["doc_id"],
                source=r.payload["source"],
                title=r.payload["title"],
                chunk_index=r.payload["chunk_index"],
            )
            for r in results
        ]

    def delete_document(self, doc_id: str) -> None:
        self.client.delete(
            collection_name=self.settings.qdrant_collection,
            points_selector=qm.FilterSelector(
                filter=qm.Filter(
                    must=[qm.FieldCondition(key="doc_id", match=qm.MatchValue(value=doc_id))]
                )
            ),
        )
