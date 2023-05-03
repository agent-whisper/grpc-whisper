import grpc
import signal
import asyncio
import threading

from typing import List
from concurrent import futures
from src.logger import logger
from src.generated.service_pb2_grpc import (
    add_TranscriptionServiceServicer_to_server,
)
from src.server.services import TranscriptionService
from src.whispers.enums import WhisperModules, WhisperModelSizes


def start_grpc(
    module: WhisperModules,
    model_size: WhisperModelSizes,
    devices: List[str],
    secure_port: bool = False,
    port: int = 50051,
    threads_count: int = 1,
):
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(
            serve(
                module=module,
                model_size=model_size,
                secure_port=secure_port,
                port=port,
                thread_count=threads_count,
                devices=devices,
            )
        )
    except KeyboardInterrupt:
        pending_tasks = asyncio.all_tasks(loop=loop)
        for task in pending_tasks:
            task.cancel()
        logger.info("Waiting for running tasks to finish.")
        loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
    finally:
        loop.close()


async def serve(
    module: WhisperModules,
    model_size: WhisperModelSizes,
    devices: List[str],
    secure_port: bool = False,
    port: int = 50051,
    thread_count: int = 1,
):
    server = grpc.aio.server()
    done = threading.Event()
    with futures.ThreadPoolExecutor(max_workers=thread_count) as engine_thread_pool:
        add_TranscriptionServiceServicer_to_server(
            TranscriptionService(
                pool=engine_thread_pool,
                stop_event=done,
                module=module,
                model_size=model_size,
                workers=thread_count,
                devices=devices,
            ),
            server,
        )

        if secure_port:
            # TODO: Handle server credentials
            server.add_secure_port(f"[::]:{port}")
        else:
            server.add_insecure_port(f"[::]:{port}")

        def on_done(signum, frame):
            logger.info(f"Got signal {signum}, {frame}")
            done.set()

        signal.signal(
            signal.SIGTERM, on_done
        )  # Might need to catch more signals for docker deployment
        try:
            await server.start()
            logger.info(
                f"Whisper gRPC({port=}, {secure_port=}, {thread_count=}) started."
            )
            await server.wait_for_termination()
        except asyncio.CancelledError:
            logger.info("Received cancel signal.")
            done.set()
            logger.info("Stopping RPC handlers.")
            await server.stop(None)
        logger.info(
            "Server stopped. Please wait a moment until all engines are shutdown."
        )
