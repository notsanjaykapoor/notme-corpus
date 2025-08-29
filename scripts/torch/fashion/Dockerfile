FROM gcr.io/deeplearning-platform-release/pytorch-cu121.2-2.py310

WORKDIR /

COPY ./scripts/torch/fashion /trainer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv 

ENTRYPOINT ["./trainer/train"]
