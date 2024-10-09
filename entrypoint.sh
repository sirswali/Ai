#!/bin/sh

# Load environment variables from .env file
set -a
. ./.env
set +a

# Execute the command passed to docker run
exec "$@"