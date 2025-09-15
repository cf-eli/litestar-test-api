#!/bin/bash
echo "Starting server in production mode..."
set -e

# Trap for graceful shutdown
trap "echo Received shutdown signal, stopping server...; kill 0" EXIT

if [ "$1" = 'serve' ]; then
    # Activate the virtual environment created by uv
    source .venv/bin/activate
    
    # Run uvicorn directly with production settings
    uvicorn asgi:app \
        --host $HOST \
        --port $PORT \
        --workers ${WORKERS:-1} \
        # --worker-class uvicorn.workers.UvicornWorker \
        # --access-log \
        # --log-level ${LOG_LEVEL:-info} &
    
    PID=$!
    wait $PID
fi

exec "$@"