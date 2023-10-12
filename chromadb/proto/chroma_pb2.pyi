# type: ignore

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Operation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ADD: _ClassVar[Operation]
    UPDATE: _ClassVar[Operation]
    UPSERT: _ClassVar[Operation]
    DELETE: _ClassVar[Operation]

class ScalarEncoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    FLOAT32: _ClassVar[ScalarEncoding]
    INT32: _ClassVar[ScalarEncoding]

class SegmentScope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VECTOR: _ClassVar[SegmentScope]
    METADATA: _ClassVar[SegmentScope]

ADD: Operation
UPDATE: Operation
UPSERT: Operation
DELETE: Operation
FLOAT32: ScalarEncoding
INT32: ScalarEncoding
VECTOR: SegmentScope
METADATA: SegmentScope

class Vector(_message.Message):
    __slots__ = ["dimension", "vector", "encoding"]
    DIMENSION_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    dimension: int
    vector: bytes
    encoding: ScalarEncoding
    def __init__(
        self,
        dimension: _Optional[int] = ...,
        vector: _Optional[bytes] = ...,
        encoding: _Optional[_Union[ScalarEncoding, str]] = ...,
    ) -> None: ...

class Segment(_message.Message):
    __slots__ = ["id", "type", "scope", "topic", "collection", "metadata"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    scope: SegmentScope
    topic: str
    collection: str
    metadata: UpdateMetadata
    def __init__(
        self,
        id: _Optional[str] = ...,
        type: _Optional[str] = ...,
        scope: _Optional[_Union[SegmentScope, str]] = ...,
        topic: _Optional[str] = ...,
        collection: _Optional[str] = ...,
        metadata: _Optional[_Union[UpdateMetadata, _Mapping]] = ...,
    ) -> None: ...

class UpdateMetadataValue(_message.Message):
    __slots__ = ["string_value", "int_value", "float_value"]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    int_value: int
    float_value: float
    def __init__(
        self,
        string_value: _Optional[str] = ...,
        int_value: _Optional[int] = ...,
        float_value: _Optional[float] = ...,
    ) -> None: ...

class UpdateMetadata(_message.Message):
    __slots__ = ["metadata"]

    class MetadataEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UpdateMetadataValue
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[UpdateMetadataValue, _Mapping]] = ...,
        ) -> None: ...
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _containers.MessageMap[str, UpdateMetadataValue]
    def __init__(
        self, metadata: _Optional[_Mapping[str, UpdateMetadataValue]] = ...
    ) -> None: ...

class SubmitEmbeddingRecord(_message.Message):
    __slots__ = ["id", "vector", "metadata", "operation"]
    ID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    vector: Vector
    metadata: UpdateMetadata
    operation: Operation
    def __init__(
        self,
        id: _Optional[str] = ...,
        vector: _Optional[_Union[Vector, _Mapping]] = ...,
        metadata: _Optional[_Union[UpdateMetadata, _Mapping]] = ...,
        operation: _Optional[_Union[Operation, str]] = ...,
    ) -> None: ...

class VectorEmbeddingRecord(_message.Message):
    __slots__ = ["id", "seq_id", "vector"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_ID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    seq_id: bytes
    vector: Vector
    def __init__(
        self,
        id: _Optional[str] = ...,
        seq_id: _Optional[bytes] = ...,
        vector: _Optional[_Union[Vector, _Mapping]] = ...,
    ) -> None: ...

class VectorQueryResult(_message.Message):
    __slots__ = ["id", "seq_id", "distance", "vector"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_ID_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    seq_id: bytes
    distance: float
    vector: Vector
    def __init__(
        self,
        id: _Optional[str] = ...,
        seq_id: _Optional[bytes] = ...,
        distance: _Optional[float] = ...,
        vector: _Optional[_Union[Vector, _Mapping]] = ...,
    ) -> None: ...

class VectorQueryResults(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[VectorQueryResult]
    def __init__(
        self, results: _Optional[_Iterable[_Union[VectorQueryResult, _Mapping]]] = ...
    ) -> None: ...

class SegmentServerResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetVectorsRequest(_message.Message):
    __slots__ = ["ids", "segment_id"]
    IDS_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    segment_id: str
    def __init__(
        self, ids: _Optional[_Iterable[str]] = ..., segment_id: _Optional[str] = ...
    ) -> None: ...

class GetVectorsResponse(_message.Message):
    __slots__ = ["records"]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[VectorEmbeddingRecord]
    def __init__(
        self,
        records: _Optional[_Iterable[_Union[VectorEmbeddingRecord, _Mapping]]] = ...,
    ) -> None: ...

class QueryVectorsRequest(_message.Message):
    __slots__ = ["vectors", "k", "allowed_ids", "include_embeddings", "segment_id"]
    VECTORS_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_IDS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_ID_FIELD_NUMBER: _ClassVar[int]
    vectors: _containers.RepeatedCompositeFieldContainer[Vector]
    k: int
    allowed_ids: _containers.RepeatedScalarFieldContainer[str]
    include_embeddings: bool
    segment_id: str
    def __init__(
        self,
        vectors: _Optional[_Iterable[_Union[Vector, _Mapping]]] = ...,
        k: _Optional[int] = ...,
        allowed_ids: _Optional[_Iterable[str]] = ...,
        include_embeddings: bool = ...,
        segment_id: _Optional[str] = ...,
    ) -> None: ...

class QueryVectorsResponse(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[VectorQueryResults]
    def __init__(
        self, results: _Optional[_Iterable[_Union[VectorQueryResults, _Mapping]]] = ...
    ) -> None: ...
