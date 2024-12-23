ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN apt-get update -q \
    && apt-get install --no-install-recommends -qy python3-dev g++ gcc

RUN --mount=type=bind,source=Pipfile,target=Pipfile \
    --mount=type=bind,source=Pipfile.lock,target=Pipfile.lock \
    --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install pipenv && pipenv sync --system

USER appuser

COPY . .

RUN mkdir -p /tmp/downloads

EXPOSE 8000

# Run the application.
CMD ["fastapi", "run", "app/main.py"]
