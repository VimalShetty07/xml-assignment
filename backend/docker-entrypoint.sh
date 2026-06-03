#!/bin/sh
set -e

# Run migrations only for the API process (uvicorn), not the worker.
case "$1" in
  uvicorn)
    echo "Running database migrations..."
    alembic upgrade head
    ;;
esac

exec "$@"
