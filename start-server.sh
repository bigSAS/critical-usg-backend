#!/usr/bin/env bash
(
cd /opt/app;
flask db upgrade;
python setup_defaults.py;
gunicorn --bind 0.0.0.0:8000 --workers $CUSG_GUNICORN_WORKERS wsgi:app
) &
nginx -g "daemon off;"