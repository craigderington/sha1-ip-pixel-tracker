#!/bin/bash
cd /var/www/html/python-flask-pixel-tracking
source bin/activate
celery -A pfpt.main.celery worker --loglevel=INFO --concurrency=1