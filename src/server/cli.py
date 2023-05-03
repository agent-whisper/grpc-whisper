import click
import torch

from typing import List
from src.logger import set_logger_level, logger
from src.server.app import start_grpc
from src.whispers.enums import WhisperModelSizes, WhisperModules
from src.whispers.utils import verify_devices_exist


@click.command()
@click.option(
    "--module",
    required=True,
    type=click.Choice(list(WhisperModules)),
    help="Whisper module to use.",
)
@click.option(
    "--model-size",
    required=True,
    type=click.Choice(list(WhisperModelSizes)),
    help="Whisper model size to use. Will automatically download the model.",
)
@click.option(
    "--secure-port",
    default=False,
    is_flag=True,
    show_default=True,
    help="[NOT IMPLEMENTED YET] Whether to use secure or insecure port.",
)
@click.option(
    "--port",
    "-p",
    default=50051,
    show_default=True,
    help="The port the grpc server will be published to.",
)
@click.option(
    "--threads-count",
    "-tc",
    default=1,
    show_default=True,
    help="Number of grpc and engine threads.",
)
@click.option(
    "--devices",
    default=None,
    show_default=False,
    help='Comma separated torch devices ID to use (e.g. "cuda:0,cuda:1,cpu"). Each thread will be assigned to a device in round-robin fashion. Omitting this option will use the standard "cuda if available" behaviour.',
)
@click.option(
    "--debug",
    default=False,
    show_default=True,
    is_flag=True,
    help="Show debug logs.",
)
def run_server(
    module: WhisperModules,
    model_size: WhisperModelSizes,
    secure_port: bool,
    port: int,
    threads_count: int,
    devices: List[str],
    debug: bool,
):
    if devices:
        try:
            devices = devices.split(",")
            verify_devices_exist(devices=devices)
        except Exception as e:
            logger.error(f"Device(s) verification failed: {e}")
            exit(-1)
    else:
        devices = ["cuda"] if torch.cuda.is_available() else ["cpu"]

    if debug:
        set_logger_level("DEBUG")
    else:
        set_logger_level("INFO")

    start_grpc(
        module=module,
        model_size=model_size,
        devices=devices,
        secure_port=secure_port,
        port=port,
        threads_count=threads_count,
    )


if __name__ == "__main__":
    run_server()
