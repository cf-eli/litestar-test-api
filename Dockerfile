FROM python:3.12-slim

# Install system dependencies
RUN apt-get update -qqy \
    && apt-get install -qqy --no-install-recommends \
        curl \
        libpq-dev \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir uv

# Setup non-root user
ENV HOME=/home/appuser
RUN mkdir -p $HOME \
    && groupadd -g 1000 appuser \
    && useradd -r -u 1000 -g appuser appuser \
    && chown -R appuser $HOME

ENV PATH="$HOME/.local/bin:$PATH"
USER appuser
WORKDIR $HOME

# Copy dependency files first (for better Docker layer caching)
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser asgi.py entrypoint.sh ./

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Set environment variables
ARG PORT=8085
ENV HOST=0.0.0.0
ENV PORT=${PORT}
ENV PYTHONPATH=/home/appuser/src

# # Health check (optional but recommended for production)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:$PORT/health || exit 1

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
CMD ["serve"]
EXPOSE ${PORT}