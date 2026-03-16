FROM ubuntu:22.04

# Set non-interactive to avoid apt-get prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install prerequisites: curl (for uv install), sudo (for our script)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (playwright deps often prefer this to avoid root complications)
RUN useradd -ms /bin/bash appuser && echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /app

# Switch to the new user
USER appuser

# Install uv using the official curl script
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to the path
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy everything, assigning ownership to appuser
COPY --chown=appuser:appuser . .

# Run the setup script which does `uv sync`, `install`, and `install-deps`
RUN chmod +x bin/setup.sh && ./bin/setup.sh

# Default command to run the application
CMD ["uv", "run", "python", "run.py", "--platform", "all"]
