# You will need to fix the generated file imports manually after running
# this command.

python -m grpc_tools.protoc \
    --proto_path src/proto/transcription \
    --grpc_python_out=src/generated/ \
    --python_out=src/generated/ \
    --pyi_out=src/generated/ \
    src/proto/transcription/*.proto
