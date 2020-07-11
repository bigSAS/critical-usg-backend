#!/usr/bin/env bash
(cd /opt/app; pipenv run flask db upgrade; pipenv run gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:app --daemon) &
nginx -g "daemon off;"