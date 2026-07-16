#!/bin/bash
set -e

echo "=== Starting Celery Worker ==="
celery -A todoproject worker \
  --loglevel=info \
  --detach \
  --logfile=/tmp/celery-worker.log \
  --pidfile=/tmp/celery-worker.pid

echo "=== Starting Celery Beat ==="
celery -A todoproject beat \
  --loglevel=info \
  --detach \
  --logfile=/tmp/celery-beat.log \
  --pidfile=/tmp/celery-beat.pid \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler

echo "=== Starting Gunicorn ==="
exec gunicorn todoproject.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --timeout 120 \
  --log-level info