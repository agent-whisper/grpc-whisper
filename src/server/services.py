import time
import queue
import asyncio
import threading

from uuid import uuid4
from typing import Dict, List
from concurrent import futures
from src.logger import logger
from src.generated.result_pb2 import TranscriptionResult
from src.generated.service_pb2 import TranscriptionRequest, TranscriptionResponse
from src.generated.service_pb2_grpc import (
    TranscriptionService as GrpcTranscriptionService,
)
from src.whispers.enums import WhisperModules, WhisperModelSizes
from src.whispers.engine import WhisperEngine
from src.whispers.exceptions import EmptyAudioError


class TranscriptionService(GrpcTranscriptionService):
    pool: futures.ThreadPoolExecutor
    request_queue: queue.Queue
    stop_event: threading.Event
    engine: WhisperEngine
    workers: int
    result_dict: Dict

    def __init__(
        self,
        pool: futures.ThreadPoolExecutor,
        stop_event: threading.Event,
        module: WhisperModules,
        model_size: WhisperModelSizes,
        workers: int = 1,
        devices: List[str] = None,
        *args,
        **kwargs,
    ):
        self.pool = pool
        self.stop_event = stop_event
        self.request_queue = queue.Queue()
        self.result_dict = dict()
        self.workers = 1 if workers < 1 else workers

        @logger.catch
        def start_engine_threads(
            result_dict: Dict,
            pending_request: queue.Queue,
            ready_event: threading.Event,
            stop_event: threading.Event,
            engine_opt: Dict,
        ):
            loop = asyncio.new_event_loop()
            engine = WhisperEngine(**engine_opt, loop=loop)
            ready_event.set()
            while True:
                try:
                    if stop_event.is_set():
                        logger.debug(f"[{engine_opt['id']}] Stop signal received.")
                        break
                    request, request_id = pending_request.get(timeout=1)
                    result = loop.run_until_complete(
                        engine.transcribe(
                            request.data,
                            language=request.language,
                            initial_prompt=request.initialPrompt,
                        )
                    )
                    result_dict[request_id] = result
                except queue.Empty:
                    # Work around so we can catch the stop event.
                    logger.debug(f"[{engine_opt['id']}] Request queue empty.")

        ready_events = []
        device_idx = 0
        device_count = len(devices)
        device = None
        for i in range(workers):
            if isinstance(devices, list):
                device = devices[device_idx % device_count]
            ready = threading.Event()
            ready_events.append(ready)
            self.pool.submit(
                start_engine_threads,
                self.result_dict,
                self.request_queue,
                ready,
                self.stop_event,
                {
                    "id": f"engine-{i}",
                    "module": module,
                    "model_size": model_size,
                    "device": device,
                },
            )
        # We can make this into an option
        logger.info("Waiting until at least one engine is ready.")
        while not any([e.is_set() for e in ready_events]):
            time.sleep(0.1)
        super().__init__(*args, **kwargs)

    @logger.catch
    async def Transcribe(
        self, request: TranscriptionRequest, context
    ) -> TranscriptionResponse:
        start = time.perf_counter()
        response = None
        try:
            logger.debug(f"Received a new request.")
            if len(request.data) == 0:
                raise EmptyAudioError
            request_id = str(uuid4)
            self.request_queue.put((request, request_id))

            # Note that this is not usually thread-safe i.e. sharing dict between threads
            # has race-condition possibility.
            # But since it's almost guaranteed only one sub-thread will access the dict-key,
            # it should be fine.
            while request_id not in self.result_dict:
                await asyncio.sleep(0.05)
            result = self.result_dict[request_id]
            del self.result_dict[request_id]
            response = TranscriptionResponse(
                success=True,
                message="success",
                result=TranscriptionResult(
                    text=result.text,
                    language=result.language,
                    segments=[segment.to_dict() for segment in result.segments],
                ),
            )
        except EmptyAudioError as e:
            logger.debug(f"Received empty audio.")
            response = TranscriptionResponse(
                success=True,
                message=f"Empty audio received",
                result=TranscriptionResult(text="", language=None, segments=[]),
            )
        except Exception as e:
            logger.exception(f"Transcription failed: {e}.")
            response = TranscriptionResponse(
                success=False, message=f"Transcription failed {e}", result=None
            )
        finally:
            end = time.perf_counter()
            if response:
                logger.info(
                    f"Request finished with status '{'success' if response.success else 'failed'}' in {end-start:.2f}"
                )
            else:
                logger.warning(f"Empty response produced!")
            return response
