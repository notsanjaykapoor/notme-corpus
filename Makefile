# venv created with 'uv venv --python /Users/sanjaykapoor/.pyenv/shims/python3.12'
VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3

.PHONY: build clean dev install test

build:
	./scripts/vps/vps-utils build

dev:
	supervisord -c supervisor/dev.conf

dev-server:
	. $(VENV)/bin/activate && ./bin/app-server --port 8005

install: pyproject.toml
	uv sync

prd:
	. $(VENV)/bin/activate && ./bin/app-server --port 8005

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)