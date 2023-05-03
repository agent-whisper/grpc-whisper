import inspect

from typing import Dict, List
from dataclasses import dataclass
from src.generated.result_pb2 import TranscriptionResult, Segment as SegmentPb


# Copied from src.whispers.module_wrappers to avoid circular import
@dataclass
class Segment:
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float

    @classmethod
    def from_proto(cls, obj: SegmentPb):
        return cls(
            id=obj.id,
            seek=obj.seek,
            start=obj.start,
            end=obj.end,
            text=obj.text,
            tokens=[token for token in obj.tokens],
            temperature=obj.temperature,
            avg_logprob=obj.avg_logprob,
            compression_ratio=obj.compression_ratio,
            no_speech_prob=obj.no_speech_prob,
        )

    def to_dict(self) -> Dict:
        return {
            key: getattr(self, key)
            for key in inspect.signature(self.__class__).parameters
        }


def convert_transcription_to_dict(transcription: TranscriptionResult) -> Dict:
    return {
        "text": transcription.text,
        "language": transcription.language,
        "segments": [
            Segment.from_proto(segment).to_dict() for segment in transcription.segments
        ],
    }
