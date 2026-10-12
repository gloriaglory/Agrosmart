#!/bin/sh
# Container start-up: prepare the database, then run the web server.
set -e

python manage.py migrate --noinput

# Optional admin account from DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput >/dev/null 2>&1 || true
fi

# Hosts like Hugging Face have no cron: refresh market prices in the background
# whenever they are more than 30 days old (each restart checks again).
(python manage.py refresh_prices --if-older-than 30 || echo "Price refresh failed; will retry on next start") &

# Threads let one worker stream chatbot answers while serving other requests.
# Each worker loads TensorFlow (~1.5 GB), so keep WEB_WORKERS low on small machines.
exec gunicorn crop_recommendation.wsgi \
  --bind "0.0.0.0:${WEB_PORT:-7860}" \
  --workers "${WEB_WORKERS:-2}" --threads 4 --timeout 120 \
  --access-logfile -
