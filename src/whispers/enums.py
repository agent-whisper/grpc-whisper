from enum import Enum


class WhisperModules(str, Enum):
    openai = "openai"
    stable_ts = "stable_ts"


class WhisperModelSizes(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"
    large_v2 = "large-v2"
