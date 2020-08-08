#!/usr/bin/env bash
(
cd /opt/app;
python manage.py db upgrade;
gunicorn --bind 0.0.0.0:8000 --workers $CUSG_GUNICORN_WORKERS "cusg:create_app()"
) &
nginx -g "daemon off;"