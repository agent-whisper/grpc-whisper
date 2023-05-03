from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Segment(_message.Message):
    __slots__ = ["avg_logprob", "compression_ratio", "end", "id", "no_speech_prob", "seek", "start", "temperature", "text", "tokens"]
    AVG_LOGPROB_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_RATIO_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NO_SPEECH_PROB_FIELD_NUMBER: _ClassVar[int]
    SEEK_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    avg_logprob: float
    compression_ratio: float
    end: float
    id: int
    no_speech_prob: float
    seek: float
    start: float
    temperature: float
    text: str
    tokens: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., seek: _Optional[float] = ..., start: _Optional[float] = ..., end: _Optional[float] = ..., text: _Optional[str] = ..., tokens: _Optional[_Iterable[int]] = ..., temperature: _Optional[float] = ..., avg_logprob: _Optional[float] = ..., compression_ratio: _Optional[float] = ..., no_speech_prob: _Optional[float] = ...) -> None: ...

class TranscriptionResult(_message.Message):
    __slots__ = ["language", "segments", "text"]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    language: str
    segments: _containers.RepeatedCompositeFieldContainer[Segment]
    text: str
    def __init__(self, text: _Optional[str] = ..., language: _Optional[str] = ..., segments: _Optional[_Iterable[_Union[Segment, _Mapping]]] = ...) -> None: ...
