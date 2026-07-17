#!/bin/bash
set -e

CELERY_WORKER_PID=""
CELERY_BEAT_PID=""
GUNICORN_PID=""

start_worker() {
  echo "=== Starting Celery Worker ==="
  celery -A todoproject worker \
    --loglevel=info \
    --pool=solo &
  CELERY_WORKER_PID=$!
}

start_beat() {
  echo "=== Starting Celery Beat ==="
  celery -A todoproject beat \
    --loglevel=info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler &
  CELERY_BEAT_PID=$!
}

start_gunicorn() {
  echo "=== Starting Gunicorn ==="
  gunicorn todoproject.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-level info &
  GUNICORN_PID=$!
}

shutdown() {
  echo "=== Shutting down ==="
  kill "$CELERY_WORKER_PID" "$CELERY_BEAT_PID" "$GUNICORN_PID" 2>/dev/null || true
  wait
  exit 0
}
trap shutdown SIGTERM SIGINT

start_worker
sleep 5
start_beat
sleep 3
start_gunicorn

echo "=== Watchdog active: monitoring worker, beat, gunicorn every 30s ==="
while true; do
  sleep 30

  if ! kill -0 "$CELERY_WORKER_PID" 2>/dev/null; then
    echo "!!! Celery worker died (was pid $CELERY_WORKER_PID) — restarting !!!"
    start_worker
  fi

  if ! kill -0 "$CELERY_BEAT_PID" 2>/dev/null; then
    echo "!!! Celery beat died (was pid $CELERY_BEAT_PID) — restarting !!!"
    start_beat
  fi

  if ! kill -0 "$GUNICORN_PID" 2>/dev/null; then
    echo "!!! Gunicorn died (was pid $GUNICORN_PID) — restarting !!!"
    start_gunicorn
  fi
done