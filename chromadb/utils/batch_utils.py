from typing import Optional, Tuple, List, TypedDict
from chromadb.api import BaseAPI
from chromadb.api.types import (
    Documents,
    Embeddings,
    IDs,
    Metadatas,
)


class Batch(TypedDict):
    ids: IDs
    embeddings: Optional[Embeddings]
    metadatas: Optional[Metadatas]
    documents: Optional[Documents]


def split_large_batch(
    api: BaseAPI,
    ids: IDs,
    embeddings: Optional[Embeddings] = None,
    metadatas: Optional[Metadatas] = None,
    documents: Optional[Documents] = None,
) -> List[Batch]:
    _batches: List[Batch] = []
    if len(ids) > api.max_batch_size:
        for i in range(0, len(ids), api.max_batch_size):
            _batches.append(
                Batch(
                    ids=ids[i : i + api.max_batch_size],
                    embeddings=embeddings[i : i + api.max_batch_size]
                    if embeddings
                    else None,
                    metadatas=metadatas[i : i + api.max_batch_size]
                    if metadatas
                    else None,
                    documents=documents[i : i + api.max_batch_size]
                    if documents
                    else None,
                )
            )
    else:
        _batches.append(
            Batch(
                ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents
            )
        )
    return _batches


def create_batches(
    api: BaseAPI,
    ids: IDs,
    embeddings: Optional[Embeddings] = None,
    metadatas: Optional[Metadatas] = None,
    documents: Optional[Documents] = None,
) -> List[Tuple[IDs, Embeddings, Optional[Metadatas], Optional[Documents]]]:
    _batches: List[
        Tuple[IDs, Embeddings, Optional[Metadatas], Optional[Documents]]
    ] = []
    _typed_batches = split_large_batch(api, ids, embeddings, metadatas, documents)
    for batch in _typed_batches:
        _batches.append(
            (
                batch["ids"],
                batch["embeddings"],
                batch["metadatas"],
                batch["documents"],
            )  # type: ignore
        )
    return _batches
