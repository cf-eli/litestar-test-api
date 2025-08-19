#!/bin/bash
echo "Attempt to start server"


set -e


trap "echo Killing background tasks...; kill 0" EXIT





if [ "$1" = 'serve' ]; then
    exec uvicorn asgi:app --host $HOST --port $PORT
fi

exec "$@"