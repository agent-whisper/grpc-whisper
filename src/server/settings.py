import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.environ.get("GRPC_PORT", 50051))
THREADS = int(os.environ.get("GRPC_THREADS", 1))
SECURE_PORT = os.environ.get("GRPC_SECURE_PORT", "false").lower() == "true"
MODULE = os.environ.get("WHISPER_MODULE", "openai")
MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "small")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
