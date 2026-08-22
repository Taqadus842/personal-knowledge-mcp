from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from auth.dependencies import get_current_user
from database.models import User

from config import load_settings
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


settings = load_settings()

store = QdrantStore(settings)

embedder = GeminiEmbedder(settings)


@router.get("/")
def search_documents(
    q: str = Query(
        ...,
        min_length=1,
    ),

    top_k: int = Query(
        5,
        ge=1,
        le=20,
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    query_vector = embedder.embed_query(q)

    # Retrieve more candidates first.
    # This gives us enough chunks to apply
    # the confidence threshold afterwards.
    hits = store.search(
        query_vector=query_vector,
        top_k=top_k * 5,
        user_id=current_user.id,
    )

    confident = [
        hit
        for hit in hits
        if hit.score >= settings.similarity_threshold
    ]

    # Keep the best matching chunk from each
    # document so one document cannot dominate
    # the results with many chunks.
    best_by_document = {}

    for hit in confident:

        existing = best_by_document.get(
            hit.doc_id
        )

        if (
            existing is None
            or hit.score > existing.score
        ):
            best_by_document[hit.doc_id] = hit

    final_results = sorted(
        best_by_document.values(),
        key=lambda hit: hit.score,
        reverse=True,
    )[:top_k]

    return {
        "query": q,

        "results": [
            {
                "text": hit.text,

                "score": round(
                    hit.score,
                    4,
                ),

                "document_id": hit.doc_id,

                "document_name": hit.title,

                "source": hit.source,

                "page_number": hit.page_number,

                "chunk_index": hit.chunk_index,
            }

            for hit in final_results
        ],
    }