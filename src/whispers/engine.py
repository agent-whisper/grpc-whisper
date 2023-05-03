import time
import asyncio

from src.logger import logger
from src.whispers.enums import WhisperModules, WhisperModelSizes
from src.whispers.utils import convert_to_monowave_form
from src.whispers.exceptions import EmptyAudioError
from src.whispers.modules_wrapper import get_model, WhisperResultWrapper
from uuid import uuid4
from whisper.model import Whisper


class RunningModel:
    model: Whisper
    lock: asyncio.Lock

    def __init__(
        self,
        *,
        module: WhisperModules,
        model_size: WhisperModelSizes,
        loop: asyncio.AbstractEventLoop = None,
        device: str = None,
    ):
        self.model = get_model(module, model_size, device=device)
        loop = loop or asyncio.get_event_loop()
        self.lock = asyncio.Lock(loop=loop)

    @logger.catch
    async def transcribe(
        self, data: bytes, *, language="en", initial_prompt="str", **kwargs
    ):
        if len(data) == 0:
            raise EmptyAudioError
        waveform = await convert_to_monowave_form(data)
        async with self.lock:
            return self.model.transcribe(
                waveform, language=language, initial_prompt=initial_prompt, **kwargs
            )

    def busy(self) -> bool:
        return self.lock.locked()


class WhisperEngine:
    id: str
    loop: asyncio.AbstractEventLoop
    module: WhisperModules
    model: RunningModel

    def __init__(
        self,
        *,
        module: WhisperModules,
        model_size: WhisperModelSizes,
        id: str = None,
        loop: asyncio.AbstractEventLoop = None,
        device: str = None,
    ):
        self.id = id or str(uuid4())
        self.module = module
        self.loop = loop or asyncio.get_event_loop()
        self.model = RunningModel(
            module=module, model_size=model_size, loop=self.loop, device=device
        )
        logger.info(f"[{self.id}] Engine<{module}({model_size})> initialized.")

    @logger.catch
    async def transcribe(
        self, data: bytes, *, language="en", initial_prompt="str", **kwargs
    ) -> WhisperResultWrapper:
        logger.debug(f"[{self.id}] Beginning transcription")
        start = time.perf_counter()
        result = await self.model.transcribe(
            data, language=language, initial_prompt=initial_prompt, **kwargs
        )
        end = time.perf_counter()
        logger.debug(
            f"[{self.id}] Transcription finished transcription in {end-start:.2f} seconds"
        )
        return WhisperResultWrapper(result, module=self.module)
