#!/bin/bash
cd /var/www/html/python-flask-pixel-tracking
source bin/activate
uwsgi -s /tmp/uwsgi.sock -w pfpt.main:app --chmod-socket=666