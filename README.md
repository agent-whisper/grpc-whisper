# grpc-whisper

gRPC server for running OpenAI's Whisper Model and its other flavors.

# Features

- Uses gRPC protocol.
- **[Experimental]** Uses different subthread for each Whisper model instance. This allows a single server instance to load multiple instances of the model, allowing for parallel transcriptions (see the notes on deploying multiple model instances).
- Currently supports the following Whisper flavors:
  - [OpenAI](https://github.com/openai/whisper)
  - [stable-ts](https://github.com/jianfch/stable-ts)

# Backlogs

- Add the rest of whisper parameters (currently only accepts language and initialPrompt parameters).
- Add support for gRPC secure port.
- Docker deployment if possible.

# Installation

- Clone the repository and install the project with poetry.

# Starting the server

All python commands assume poetry shell has been activated. Run `python src/server/cli.py --help` to see all options.

## Single model instance

`python src/server/cli.py --module openai --model-size small -p 50051`

This will:

- Download the small OpenAi Whisper model (for first time run only).
- Load the model to the first gpu detected if available. Otherwise loads the model to CPU.
- Deploy the gRPC server on port 50051.

## Multiple model instances

`python src/server/cli.py --module openai --model-size small -p 50051 --devices cuda:0,cuda:1 --threads-count 2`

This will:

- Download the small OpenAi Whisper model (for first time run only).
- Spawn 2 engine-threads. The first thread will load the model into the first gpu identified by the torch module as `cuda:0`, while the second loads the model into the `cuda:1` gpu.
- Deploy the gRPC server on port 50051.

# Client Side

## Client repository

Client for this repository is availabe at https://github.com/agent-whisper/grpc-whisper-client

## Testing locally
The server request-response have the following structure:

```
message TranscriptionRequest {
  bytes data = 1;
  string language = 2;
  string initialPrompt = 3;
}

message TranscriptionResponse {
  bool success = 1;
  string message = 2;
  TranscriptionResult result = 3;  // The actual module output is in here.
}
```

All python commands assume poetry shell has been activated. Run `python src/client/cli.py --help` to see all options.

`python src/client/cli.py FILENAME --server localhost:50051 -o result.json`

This will:
- Reads FILENAME as binary.
- Blocks until the gRPC server at localhost:50051 is ready.
- Send the file.
- Writes the transcription result to result.json

# System Dependencies

- Python 3.8+
- poetry
- CUDA
- ffmpeg
- protoc

# Deploying Multiple Model Instance

While it's possible to load multiple models into a single GPU (provided it has enough VRAM), it would actually hurts the individual transcription performance since each process would fight for the same resource. So loading multiple model is not worthed unless we actually have multiple discrete GPUs for each instance. This haven't been fully verified however due to the lack of extra GPUs.
