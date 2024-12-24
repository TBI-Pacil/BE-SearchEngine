ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN apt-get update -q \
    && apt-get install --no-install-recommends -qy python3-dev g++ gcc \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,source=Pipfile,target=Pipfile \
    --mount=type=bind,source=Pipfile.lock,target=Pipfile.lock \
    --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install pipenv && pipenv sync --system

COPY . .
RUN mkdir -p /tmp/downloads \
    && chown -R appuser:appuser /app /tmp/downloads

USER appuser
EXPOSE 8000

CMD ["fastapi", "run", "app/main.py"]