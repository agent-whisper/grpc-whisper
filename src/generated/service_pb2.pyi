import result_pb2 as _result_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TranscriptionRequest(_message.Message):
    __slots__ = ["data", "initialPrompt", "language"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    INITIALPROMPT_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    initialPrompt: str
    language: str
    def __init__(self, data: _Optional[bytes] = ..., language: _Optional[str] = ..., initialPrompt: _Optional[str] = ...) -> None: ...

class TranscriptionResponse(_message.Message):
    __slots__ = ["message", "result", "success"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    result: _result_pb2.TranscriptionResult
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., result: _Optional[_Union[_result_pb2.TranscriptionResult, _Mapping]] = ...) -> None: ...
