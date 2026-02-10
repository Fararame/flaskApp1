# Build stage
FROM python:3.12-alpine3.22 AS build

# Set work directory
WORKDIR /flask_app

# Update system & install build dependencies + curl for uv installer
RUN apk update && apk --no-cache add git gcc libc-dev libffi-dev curl

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY ./requirements.txt /flask_app/
RUN --mount=type=cache,target=/root/.cache/uv \
   uv pip install --system --no-cache -r requirements.txt


# Application image
FROM python:3.12-alpine3.22
# Set work directory
WORKDIR /flask_app

# Prevent Python from writing pyc files & buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1 \
   PATH="/flask_app/bin:$PATH"

# Copy installed dependencies from the build stage
COPY --from=build \
   /usr/local/lib/python3.12/site-packages \
   /usr/local/lib/python3.12/site-packages

# copy console scripts
COPY --from=build /usr/local/bin /usr/local/bin

# Specify the entry point
ENTRYPOINT [ "./gunicorn_starter.sh" ]

# Keep the Docker process running even when crashes
CMD ["tail", "-f", "/dev/null"]