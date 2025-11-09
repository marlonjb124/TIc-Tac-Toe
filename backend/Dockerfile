FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv for faster package management
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode for better performance
ENV UV_COMPILE_BYTECODE=1

# uv Cache configuration
ENV UV_LINK_MODE=copy

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ENV PYTHONPATH=/app

# Copy scripts for prestart checks
COPY ./scripts /app/scripts

# Copy project configuration files
COPY ./pyproject.toml ./alembic.ini /app/

# Copy application code
COPY ./app /app/app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Run database prestart check and then start the application
CMD ["sh", "-c", "python app/backend_pre_start.py && fastapi dev app/main.py --host 0.0.0.0 --port 8000 --reload"]

