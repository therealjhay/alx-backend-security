#!/bin/bash

# 1. Start the Celery Worker in the background (&)
# We limit concurrency to 2 to save RAM on the free tier
celery -A alx_backend_security worker -l info --concurrency 2 &

# 2. Start the Gunicorn Web Server in the foreground
gunicorn alx_backend_security.wsgi:application