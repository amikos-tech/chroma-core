import asyncio
from threading import Thread
from typing import Optional, Sequence, cast, List
from uuid import UUID

import aiohttp
from chromadb import Settings, Embeddings, Where, WhereDocument, Include, QueryResult, IDs, GetResult, Documents, CollectionMetadata, EmbeddingFunction, System, Telemetry, errors, Metadata
from chromadb.api import Metadatas, API
from chromadb.api.models.Collection import Collection
import chromadb.utils.embedding_functions as ef
from chromadb.api.types import OneOrMany, ID, Document, Embedding, validate_where, validate_where_document, validate_ids, maybe_cast_one_to_many, validate_include, validate_metadata, validate_n_results, validate_embeddings
from overrides import override
from pydantic import PrivateAttr

VERSION = "1"


class AsyncCollection(Collection):
    _client: "ChromaDBAsyncAPI" = PrivateAttr()

    async def count(self) -> int:
        """The total number of embeddings added to the database

        Returns:
            int: The total number of embeddings added to the database

        """
        return await self._client._count(collection_id=self.id)

    async def add(
            self,
            ids: OneOrMany[ID],
            embeddings: Optional[OneOrMany[Embedding]] = None,
            metadatas: Optional[OneOrMany[Metadata]] = None,
            documents: Optional[OneOrMany[Document]] = None,
    ) -> None:
        """Add embeddings to the data store.
        Args:
            ids: The ids of the embeddings you wish to add
            embeddings: The embeddings to add. If None, embeddings will be computed based on the documents using the embedding_function set for the Collection. Optional.
            metadatas: The metadata to associate with the embeddings. When querying, you can filter on this metadata. Optional.
            documents: The documents to associate with the embeddings. Optional.

        Returns:
            None

        Raises:
            ValueError: If you don't provide either embeddings or documents
            ValueError: If the length of ids, embeddings, metadatas, or documents don't match
            ValueError: If you don't provide an embedding function and don't provide embeddings
            ValueError: If you provide both embeddings and documents
            ValueError: If you provide an id that already exists

        """

        ids, embeddings, metadatas, documents = self._validate_embedding_set(
            ids, embeddings, metadatas, documents
        )

        await self._client._add(ids, self.id, embeddings, metadatas, documents)

    @override
    async def get(
            self,
            ids: Optional[OneOrMany[ID]] = None,
            where: Optional[Where] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            where_document: Optional[WhereDocument] = None,
            include: Include = ["metadatas", "documents"],
    ) -> GetResult:
        """Get embeddings and their associate data from the data store. If no ids or where filter is provided returns
        all embeddings up to limit starting at offset.

        Args:
            ids: The ids of the embeddings to get. Optional.
            where: A Where type dict used to filter results by. E.g. `{"$and": ["color" : "red", "price": {"$gte": 4.20}]}`. Optional.
            limit: The number of documents to return. Optional.
            offset: The offset to start returning results from. Useful for paging results with limit. Optional.
            where_document: A WhereDocument type dict used to filter by the documents. E.g. `{$contains: {"text": "hello"}}`. Optional.
            include: A list of what to include in the results. Can contain `"embeddings"`, `"metadatas"`, `"documents"`. Ids are always included. Defaults to `["metadatas", "documents"]`. Optional.

        Returns:
            GetResult: A GetResult object containing the results.

        """
        where = validate_where(where) if where else None
        where_document = (
            validate_where_document(where_document) if where_document else None
        )
        ids = validate_ids(maybe_cast_one_to_many(ids)) if ids else None
        include = validate_include(include, allow_distances=False)
        return await self._client._get(
            self.id,
            ids,
            where,
            None,
            limit,
            offset,
            where_document=where_document,
            include=include,
        )

    @override
    async def peek(self, limit: int = 10) -> GetResult:
        """Get the first few results in the database up to limit

        Args:
            limit: The number of results to return.

        Returns:
            GetResult: A GetResult object containing the results.
        """
        return await self._client._peek(self.id, limit)

    @override
    async def query(
            self,
            query_embeddings: Optional[OneOrMany[Embedding]] = None,
            query_texts: Optional[OneOrMany[Document]] = None,
            n_results: int = 10,
            where: Optional[Where] = None,
            where_document: Optional[WhereDocument] = None,
            include: Include = ["metadatas", "documents", "distances"],
    ) -> QueryResult:
        """Get the n_results nearest neighbor embeddings for provided query_embeddings or query_texts.

        Args:
            query_embeddings: The embeddings to get the closes neighbors of. Optional.
            query_texts: The document texts to get the closes neighbors of. Optional.
            n_results: The number of neighbors to return for each query_embedding or query_texts. Optional.
            where: A Where type dict used to filter results by. E.g. `{"$and": ["color" : "red", "price": {"$gte": 4.20}]}`. Optional.
            where_document: A WhereDocument type dict used to filter by the documents. E.g. `{$contains: {"text": "hello"}}`. Optional.
            include: A list of what to include in the results. Can contain `"embeddings"`, `"metadatas"`, `"documents"`, `"distances"`. Ids are always included. Defaults to `["metadatas", "documents", "distances"]`. Optional.

        Returns:
            QueryResult: A QueryResult object containing the results.

        Raises:
            ValueError: If you don't provide either query_embeddings or query_texts
            ValueError: If you provide both query_embeddings and query_texts

        """
        where = validate_where(where) if where else None
        where_document = (
            validate_where_document(where_document) if where_document else None
        )
        query_embeddings = (
            validate_embeddings(maybe_cast_one_to_many(query_embeddings))
            if query_embeddings is not None
            else None
        )
        query_texts = (
            maybe_cast_one_to_many(query_texts) if query_texts is not None else None
        )
        include = validate_include(include, allow_distances=True)
        n_results = validate_n_results(n_results)

        # If neither query_embeddings nor query_texts are provided, or both are provided, raise an error
        if (query_embeddings is None and query_texts is None) or (
                query_embeddings is not None and query_texts is not None
        ):
            raise ValueError(
                "You must provide either query embeddings or query texts, but not both"
            )

        # If query_embeddings are not provided, we need to compute them from the query_texts
        if query_embeddings is None:
            if self._embedding_function is None:
                raise ValueError(
                    "You must provide embeddings or a function to compute them"
                )
            # We know query texts is not None at this point, cast for the typechecker
            query_embeddings = self._embedding_function(
                cast(List[Document], query_texts)
            )

        if where is None:
            where = {}

        if where_document is None:
            where_document = {}

        return await self._client._query(
            collection_id=self.id,
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include,
        )

    async def modify(
            self, name: Optional[str] = None, metadata: Optional[CollectionMetadata] = None
    ) -> None:
        """Modify the collection name or metadata

        Args:
            name: The updated name for the collection. Optional.
            metadata: The updated metadata for the collection. Optional.

        Returns:
            None
        """
        if metadata is not None:
            validate_metadata(metadata)

        await self._client._modify(id=self.id, new_name=name, new_metadata=metadata)
        if name:
            self.name = name
        if metadata:
            self.metadata = metadata

    async def update(
            self,
            ids: OneOrMany[ID],
            embeddings: Optional[OneOrMany[Embedding]] = None,
            metadatas: Optional[OneOrMany[Metadata]] = None,
            documents: Optional[OneOrMany[Document]] = None,
    ) -> None:
        """Update the embeddings, metadatas or documents for provided ids.

        Args:
            ids: The ids of the embeddings to update
            embeddings: The embeddings to add. If None, embeddings will be computed based on the documents using the embedding_function set for the Collection. Optional.
            metadatas:  The metadata to associate with the embeddings. When querying, you can filter on this metadata. Optional.
            documents: The documents to associate with the embeddings. Optional.

        Returns:
            None
        """

        ids, embeddings, metadatas, documents = self._validate_embedding_set(
            ids, embeddings, metadatas, documents, require_embeddings_or_documents=False
        )

        await self._client._update(self.id, ids, embeddings, metadatas, documents)

    async def upsert(
            self,
            ids: OneOrMany[ID],
            embeddings: Optional[OneOrMany[Embedding]] = None,
            metadatas: Optional[OneOrMany[Metadata]] = None,
            documents: Optional[OneOrMany[Document]] = None,
    ) -> None:
        """Update the embeddings, metadatas or documents for provided ids, or create them if they don't exist.

        Args:
            ids: The ids of the embeddings to update
            embeddings: The embeddings to add. If None, embeddings will be computed based on the documents using the embedding_function set for the Collection. Optional.
            metadatas:  The metadata to associate with the embeddings. When querying, you can filter on this metadata. Optional.
            documents: The documents to associate with the embeddings. Optional.

        Returns:
            None
        """

        ids, embeddings, metadatas, documents = self._validate_embedding_set(
            ids, embeddings, metadatas, documents
        )

        await self._client._upsert(
            collection_id=self.id,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    async def delete(
            self,
            ids: Optional[IDs] = None,
            where: Optional[Where] = None,
            where_document: Optional[WhereDocument] = None,
    ) -> None:
        """Delete the embeddings based on ids and/or a where filter

        Args:
            ids: The ids of the embeddings to delete
            where: A Where type dict used to filter the delection by. E.g. `{"$and": ["color" : "red", "price": {"$gte": 4.20}]}`. Optional.
            where_document: A WhereDocument type dict used to filter the deletion by the document content. E.g. `{$contains: {"text": "hello"}}`. Optional.

        Returns:
            None

        Raises:
            ValueError: If you don't provide either ids, where, or where_document
        """
        ids = validate_ids(maybe_cast_one_to_many(ids)) if ids else None
        where = validate_where(where) if where else None
        where_document = (
            validate_where_document(where_document) if where_document else None
        )

        await self._client._delete(self.id, ids, where, where_document)


async def raise_chroma_error(resp: aiohttp.ClientResponse) -> None:
    """Raises an error if the response is not ok, using a ChromaError if possible"""
    if resp.ok:
        return

    chroma_error = None
    try:
        body = await resp.json()
        if "error" in body:
            if body["error"] in errors.error_types:
                chroma_error = errors.error_types[body["error"]](body["message"])

    except BaseException:
        pass

    if chroma_error:
        raise chroma_error

    try:
        resp.raise_for_status()
    except aiohttp.ClientError:
        raise (Exception(resp.text))


class ChromaDBAsyncAPI(API):
    _settings: Settings

    def __init__(self, system: System):
        super().__init__(system)
        url_prefix = "https" if system.settings.chroma_server_ssl_enabled else "http"
        system.settings.require("chroma_server_host")
        system.settings.require("chroma_server_http_port")

        self._telemetry_client = self.require(Telemetry)
        self._settings = system.settings

        port_suffix = (
            f":{system.settings.chroma_server_http_port}"
            if system.settings.chroma_server_http_port
            else ""
        )
        self._api_url = (
            f"{url_prefix}://{system.settings.chroma_server_host}{port_suffix}/api/v1"
        )

        self._header = system.settings.chroma_server_headers
        if system.settings.chroma_client_auth_provider and system.settings.chroma_client_auth_protocol_adapter:
            raise ValueError("Authentication is not yet supported!")
        else:
            self._session: aiohttp.ClientSession = aiohttp.ClientSession(raise_for_status=False)
        if self._header is not None:
            self._session.headers.update(self._header)

    def __del__(self):
        Thread(target=asyncio.run, args=(self._session.close(),)).start()

    @override
    async def heartbeat(self) -> int:
        async with self._session.get(self._api_url) as resp:
            await raise_chroma_error(resp)
            return int((await resp.json())["nanosecond heartbeat"])

    @override
    async def list_collections(self) -> Sequence[AsyncCollection]:
        async with self._session.get(self._api_url + "/collections") as resp:
            await raise_chroma_error(resp)
            json_collections = await resp.json()
            collections = []
            for json_collection in json_collections:
                collections.append(AsyncCollection(self, **json_collection))

            return collections

    @override
    async def create_collection(self, name: str, metadata: Optional[CollectionMetadata] = None, embedding_function: Optional[EmbeddingFunction] = ef.DefaultEmbeddingFunction(), get_or_create: bool = False) -> AsyncCollection:
        async with self._session.post(
                self._api_url + "/collections",
                json={"name": name, "metadata": metadata, "get_or_create": get_or_create}
        ) as resp:
            await raise_chroma_error(resp)
            resp_json = await resp.json()
            return AsyncCollection(
                client=self,
                id=resp_json["id"],
                name=resp_json["name"],
                embedding_function=embedding_function,
                metadata=resp_json["metadata"],
            )

    @override
    async def get_collection(self, name: str, embedding_function: Optional[EmbeddingFunction] = ef.DefaultEmbeddingFunction()) -> AsyncCollection:
        async with self._session.get(self._api_url + "/collections/" + name) as resp:
            await raise_chroma_error(resp)
            resp_json = await resp.json()
            return AsyncCollection(
                client=self,
                name=resp_json["name"],
                id=resp_json["id"],
                embedding_function=embedding_function,
                metadata=resp_json["metadata"],
            )

    @override
    async def get_or_create_collection(self, name: str, metadata: Optional[CollectionMetadata] = None, embedding_function: Optional[EmbeddingFunction] = ef.DefaultEmbeddingFunction()) -> AsyncCollection:
        return await self.create_collection(
            name, metadata, embedding_function, get_or_create=True
        )

    @override
    async def _modify(
            self,
            id: UUID,
            new_name: Optional[str] = None,
            new_metadata: Optional[CollectionMetadata] = None,
    ) -> None:
        async with self._session.put(
                self._api_url + "/collections/" + str(id),
                json={"new_metadata": new_metadata, "new_name": new_name}
        ) as resp:
            await raise_chroma_error(resp)

    @override
    async def delete_collection(self, name: str) -> None:
        async with self._session.delete(self._api_url + "/collections/" + name) as resp:
            await raise_chroma_error(resp)

    @override
    async def _add(self, ids: IDs, collection_id: UUID, embeddings: Embeddings, metadatas: Optional[Metadatas] = None, documents: Optional[Documents] = None) -> bool:
        async with self._session.post(
                self._api_url + "/collections/" + str(collection_id) + "/add",
                json={
                    "ids": ids,
                    "embeddings": embeddings,
                    "metadatas": metadatas,
                    "documents": documents,
                }
        ) as resp:
            await raise_chroma_error(resp)
            return True

    @override
    async def _update(self, collection_id: UUID, ids: IDs, embeddings: Optional[Embeddings] = None, metadatas: Optional[Metadatas] = None, documents: Optional[Documents] = None) -> bool:
        async with self._session.post(
                self._api_url + "/collections/" + str(collection_id) + "/update",
                json={
                    "ids": ids,
                    "embeddings": embeddings,
                    "metadatas": metadatas,
                    "documents": documents,
                }
        ) as resp:
            await raise_chroma_error(resp)
            return True

    @override
    async def _upsert(self, collection_id: UUID, ids: IDs, embeddings: Embeddings, metadatas: Optional[Metadatas] = None, documents: Optional[Documents] = None) -> bool:
        async with self._session.post(
                self._api_url + "/collections/" + str(collection_id) + "/upsert",
                json={
                    "ids": ids,
                    "embeddings": embeddings,
                    "metadatas": metadatas,
                    "documents": documents,
                }
        ) as resp:
            await raise_chroma_error(resp)
            return True

    @override
    async def _count(self, collection_id: UUID) -> int:
        async with self._session.get(
                self._api_url + "/collections/" + str(collection_id) + "/count"
        ) as resp:
            await raise_chroma_error(resp)
            return cast(int, await resp.json())

    @override
    async def _peek(self, collection_id: UUID, n: int = 10) -> GetResult:
        return await self._get(
            collection_id,
            limit=n,
            include=["embeddings", "documents", "metadatas"],
        )

    @override
    async def _get(self, collection_id: UUID, ids: Optional[IDs] = None, where: Optional[Where] = {}, sort: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None, page: Optional[int] = None, page_size: Optional[int] = None, where_document: Optional[WhereDocument] = {}, include: Include = ["embeddings", "metadatas", "documents"]) -> GetResult:
        if page and page_size:
            offset = (page - 1) * page_size
            limit = page_size

        async with self._session.post(
                self._api_url + "/collections/" + str(collection_id) + "/get",
                json={
                    "ids": ids,
                    "where": where,
                    "sort": sort,
                    "limit": limit,
                    "offset": offset,
                    "where_document": where_document,
                    "include": include,
                },
        ) as resp:
            await raise_chroma_error(resp)
            body = await resp.json()
            return GetResult(
                ids=body["ids"],
                embeddings=body.get("embeddings", None),
                metadatas=body.get("metadatas", None),
                documents=body.get("documents", None),
            )

    @override
    async def _delete(self, collection_id: UUID, ids: Optional[IDs] = None, where: Optional[Where] = {}, where_document: Optional[WhereDocument] = {}) -> IDs:
        async with self._session.post(
                self._api_url + "/collections/" + str(collection_id) + "/delete",
                json={"where": where, "ids": ids, "where_document": where_document}
        ) as resp:
            await raise_chroma_error(resp)
            return cast(IDs, await resp.json())

    @override
    async def _query(self, collection_id: UUID, query_embeddings: Embeddings, n_results: int = 10, where: Where = {}, where_document: WhereDocument = {}, include: Include = ["embeddings", "metadatas", "documents", "distances"]) -> QueryResult:
        async with self._session.post(
                self._api_url + "/collections/" + str(collection_id) + "/query",
                json={
                    "query_embeddings": query_embeddings,
                    "n_results": n_results,
                    "where": where,
                    "where_document": where_document,
                    "include": include,
                }
        ) as resp:
            await raise_chroma_error(resp)
            body = await resp.json()

            return QueryResult(
                ids=body["ids"],
                distances=body.get("distances", None),
                embeddings=body.get("embeddings", None),
                metadatas=body.get("metadatas", None),
                documents=body.get("documents", None),
            )

    @override
    async def reset(self) -> bool:
        async with self._session.post(self._api_url + "/reset") as resp:
            await raise_chroma_error(resp)
            return cast(bool, await resp.json())

    @override
    async def get_version(self) -> str:
        async with self._session.get(self._api_url + "/version") as resp:
            await raise_chroma_error(resp)
            return cast(str, await resp.json())

    @override
    async def get_settings(self) -> Settings:
        return self._settings
