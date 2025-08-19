FROM python:3.12-slim

# Environment vars
ENV PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8082

# Install uv (dependency manager)
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY . .

# Copy entrypoint and make executable
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install dependencies
RUN uv sync --frozen

# Expose the PORT
EXPOSE ${PORT}

# Use your entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command — calls 'serve' mode
CMD ["serve"]
