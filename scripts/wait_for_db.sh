#!/bin/sh
# Waits for Postgres to accept connections before running the given command.
# Not strictly needed with docker-compose's `depends_on: condition:
# service_healthy`, but useful for Render.com's pre-deploy step or any
# environment without compose-level health checks.
#
# Usage: ./scripts/wait_for_db.sh <host> <port> -- <command...>

set -e

HOST="$1"
PORT="$2"
shift 2

if [ "$1" = "--" ]; then
  shift
fi

echo "Waiting for Postgres at $HOST:$PORT..."
until nc -z "$HOST" "$PORT"; do
  sleep 1
done
echo "Postgres is up — continuing."

exec "$@"
