#!/bin/sh
set -e

# Heroku runs migrations in the release phase; local Docker runs them here.
if [ -z "${DYNO:-}" ]; then
  python manage.py migrate --noinput
fi

exec "$@"
