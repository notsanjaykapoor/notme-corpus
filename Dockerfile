FROM python:3.12.3-slim AS runner

ENV PYTHONUNBUFFERED=1

RUN apt-get -y update && \
    apt-get install -y build-essential busybox curl dnsutils gcc gettext libffi-dev libpq-dev netcat-traditional postgresql-client tmux && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./

FROM runner AS base
ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION
WORKDIR /app
ADD . ./
RUN uv sync --no-dev --frozen
