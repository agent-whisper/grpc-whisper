from enum import Enum


class WhisperModules(str, Enum):
    openai = "openai"
    stable_whisper = "stable_whisper"


class WhisperModelSizes(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"
    large_v2 = "large-v2"
