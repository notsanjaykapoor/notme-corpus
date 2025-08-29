FROM python:3.12.3-slim AS base

ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get -y update && \
    apt-get install -y build-essential busybox curl dnsutils gcc gettext git libffi-dev libpq-dev netcat-traditional postgresql-client tmux && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install uv and python packages
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# app add code
FROM base AS app
ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION
WORKDIR /app
COPY --from=builder /app /app
COPY . /app
