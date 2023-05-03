import grpc
import json
import click
import asyncio

from src.logger import logger
from src.client.utils import convert_transcription_to_dict
from src.generated.service_pb2 import TranscriptionRequest, TranscriptionResponse
from src.generated.service_pb2_grpc import TranscriptionServiceStub


@click.command()
@click.argument("AUDIO_FILE")
@click.option(
    "--server", required=True, help='The gRPC Whisper server (e.g. "localhost:50051")'
)
@click.option(
    "--output-file",
    "-o",
    default=None,
    help="File location to save the output as json file. If omitted, will print the result in stdout instead.",
)
@click.option("--secure-port", is_flag=True, default=False)
def command(audio_file, server, output_file, secure_port):
    asyncio.run(send_file(audio_file, server, output_file, secure_port))


async def send_file(audio_file: str, server: str, output_file: str, secure_port: bool):
    if secure_port:
        channel = grpc.aio.secure_channel(server)
    else:
        channel = grpc.aio.insecure_channel(server)
    with open(audio_file, "rb") as f:
        request = TranscriptionRequest(data=f.read(), language="ja")

    logger.info(f"Waiting for channel({server}) to be ready")
    await channel.channel_ready()

    logger.info("Sending request")
    stub = TranscriptionServiceStub(channel)
    response: TranscriptionResponse = await stub.Transcribe(request)

    if output_file:
        with open(output_file, "w") as f:
            json.dump(convert_transcription_to_dict(response.result), f, indent=4, ensure_ascii=False)
        logger.info(f"Response saved to {output_file}.")
    else:
        logger.info(f"Response:\n{response}.")
    assert response.success


if __name__ == "__main__":
    command()
