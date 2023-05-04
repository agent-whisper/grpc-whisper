import inspect

from .engine import WhisperModules, WhisperModelSizes
from .exceptions import WhisperEngineError, UnsupportedModelError
from dataclasses import dataclass
from typing import Dict, Union, List
from whisper.model import Whisper
from stable_whisper import WhisperResult

# Might refactor this into plugin architecture or something.


# If more dataclass usage comes up, might be worthed to
# use pydantic instead.
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
    def from_dict(cls, env: Dict):
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )

    @classmethod
    def from_obj(cls, obj: object):
        return cls(
            **{key: getattr(obj, key) for key in inspect.signature(cls).parameters}
        )

    def to_dict(self) -> Dict:
        return {
            key: getattr(self, key)
            for key in inspect.signature(self.__class__).parameters
        }


# If the dict conversion becomes an overhead, we might need to rework this module.
class WhisperResultWrapper:
    module: WhisperModules
    text: str
    language: str
    segments: List[Segment]

    def __init__(self, result: Union[Dict, WhisperResult], *, module: WhisperModules):
        if module == WhisperModules.openai:
            self._wrap_openai_result(result)
        elif module == WhisperModules.stable_ts:
            self._wrap_stable_whisper_result(result)
        else:
            raise UnsupportedModelError(f"Unsupported module: {module}")

    def _wrap_openai_result(self, result: Dict):
        self.text = result.get("text")
        self.language = result.get("language")
        self.segments = [
            Segment.from_dict(segment) for segment in result.get("segments", [])
        ]

    def _wrap_stable_whisper_result(self, result: WhisperResult):
        self.text = result.text
        self.language = result.language
        self.segments = [Segment.from_obj(segment) for segment in result.segments]


def get_model(
    module: WhisperModules, model_size: WhisperModelSizes, device: str = None
) -> Whisper:
    try:
        model_size = WhisperModelSizes(model_size)
    except ValueError:
        raise UnsupportedModelError(f"Invalid model size: {model_size}")

    try:
        module = WhisperModules(module)
    except ValueError:
        raise UnsupportedModelError(f"Unsupported module: {module}")

    model = None
    if module == WhisperModules.openai:
        import whisper

        model = whisper.load_model(model_size, device=device)

    elif module == WhisperModules.stable_ts:
        import stable_whisper

        model = stable_whisper.load_model(model_size, device=device)

    if model is None:
        raise WhisperEngineError(f"Failed to load {module}({model_size})!")

    return model
