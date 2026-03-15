FROM python:3.12-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install required system dependencies (Playwright needs these)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Create working directory
WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies via uv
RUN uv sync

# Copy the rest of the application code
COPY . .

# Install Playwright browser binaries and OS dependencies
RUN uv run playwright install chromium
RUN uv run playwright install-deps

# Default command to run the application
CMD ["uv", "run", "python", "run.py", "--platform", "all"]
