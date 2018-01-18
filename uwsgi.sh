#!/bin/bash
cd /var/www/html/flask-pixel-tracker
source bin/activate
uwsgi -s /tmp/uwsgi.sock -w pfpt.main:app --chmod-socket=666