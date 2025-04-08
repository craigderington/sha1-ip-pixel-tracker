# SHA1 IP ADDRESS Pixel Tracker

Simple implementation of an HTTP Pixel tracking using Flask, MongoDB, Redis and Celery.

# Install redis, mongo, and python-virtualenv
`apt-get install redis-server mongodb python-virtualenv`

# Optionally install python-dev for some tools
`apt-get install build-essential python-dev python-imaging`

# Setup pip requirements

`pip install -r requirements.txt`

# Launching Flask

`python pfpt/main.py`

# Launching Celery

`celery -A pfpt.main.celery worker --loglevel=INFO --concurrency=1`

# Usage

GET http://hostname/api/generate-pixel?job_number={}&client_id={}&campaign={}

this will return a SHA1 hash of the event record that you can pass to:

http://hostname/pixel.gif?sh=(open_hash_id)

which should be embedded as an image in your outbound email marketing to record opens.

