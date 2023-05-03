import torch
import numpy as np
import ffmpeg

from typing import List
from whisper.audio import SAMPLE_RATE
from src.whispers.exceptions import (
    CudaNotAvailableError,
    DeviceNotFoundError,
    InvalidDeviceId,
)


async def convert_to_monowave_form(data: bytes, sr: int = SAMPLE_RATE):
    """Modified version of whisper.load_audio that accepts raw bytes as input."""
    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input("pipe:", threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(
                cmd=["ffmpeg"],
                capture_stdout=True,
                capture_stderr=True,
                input=data,
            )
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


def verify_devices_exist(devices: List[str]):
    cuda_is_available = torch.cuda.is_available()
    not_found = []
    for device in devices:
        device = device.strip()
        if device == "cpu":
            continue
        if not cuda_is_available:
            raise CudaNotAvailableError(
                "torch.cuda.is_available() returns False. Please verify CUDA is installed to use GPU devices."
            )
        # Assumes the device is either cuda:X or X
        try:
            device_ordinal = int(device.split(":")[-1])
        except ValueError:
            raise InvalidDeviceId(f"Invalid device '{device}'")
        try:
            torch.cuda.get_device_name(device_ordinal)
        except AssertionError:
            not_found.append(device)

    if not_found:
        raise DeviceNotFoundError(f"{not_found} were not detected by the torch module.")
