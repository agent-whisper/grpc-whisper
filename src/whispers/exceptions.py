class WhisperEngineError(Exception):
    pass


class UnsupportedModelError(WhisperEngineError):
    pass


class EmptyAudioError(WhisperEngineError):
    pass


class CudaNotAvailableError(WhisperEngineError):
    pass


class DeviceNotFoundError(WhisperEngineError):
    pass


class InvalidDeviceId(WhisperEngineError):
    pass
