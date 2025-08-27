# SHA1 IP Pixel Tracker

A Flask-based pixel tracker for email marketing using Hashlib, MongoDB, Redis, and Celery.

## Overview

This application provides a simple HTTP pixel tracking system to monitor email opens. It generates SHA1-hashed event records using Python's `hashlib`, stores data in MongoDB, and processes tasks asynchronously with Celery and Redis.

## Features

- Generates SHA1-hashed pixel URLs for tracking email opens
- Stores tracking data in MongoDB
- Asynchronous task processing with Celery and Redis
- Flask web server for API and pixel delivery
- Lightweight and easy to integrate into email marketing campaigns

## Getting Started

### Prerequisites

- Python 3.8+
- Redis Server
- MongoDB Server
- Python dependencies: `pip install -r requirements.txt`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/craigderington/sha1-ip-pixel-tracker.git
2. Navigate to the project directory:
   ```bash
   cd sha1-ip-pixel-tracker
3. Install system dependencies:
   ```bash
   sudo apt-get install redis-server mongodb python-virtualenv
4. Install Optional Tools
   ```bash
   sudo apt-get install build-essential python-dev python-imaging
5. Create and activate a virtual environment
   ```bash
   virtualenv .env --python=python3
   source .env/bin/activate
6. Install Python Dependencies
   ```bash
   pip install -r requirements.txt

#### Running the Application

1.  Start Redis and MongoDB Servers
    ```bash
    sudo service redis-server start
    sudo service mongodb start
2.  Launch the Celery worker
    ```bash
    celery -A pfpt.main.celery worker --loglevel=INFO --concurrency=1
3.  Run the Flasdk application
    ```bash
    python pfpt/main.py

#### Usage
1.  Generate a tracking pixel URL:
    ```bash
    curl "http://localhost:5000/api/generate-pixel?job_number=<job>&client_id=<client>&campaign=<campaign>"
2.  Embed the pixel in your email:
    ```bash
    <img src="http://<your-url-dot-com>/pixel.gif?sh=<open_hash_id>" />
3.  When the pixel is opened, the pixel request records the event in MongoDB.


#### Code Details
The application resides in the pfpt directory and includes:

- Flask App (main.py): Handles API endpoints for pixel generation and tracking.
- Celery Tasks: Processes tracking events asynchronously.
- MongoDB Storage: Stores event data with SHA1-hashed identifiers.
- Redis: Manages task queue for Celery.
- Hashlib: Generates SHA1 hashes for unique event tracking.

#### Contributing
Contributions are welcome! To contribute:

#### Fork the repository.
- Create a feature branch (git checkout -b feature/your-feature).
- Commit your changes (git commit -m "Add your feature").
- Push to the branch (git push origin feature/your-feature).
- Open a pull request.

#### License
This project is licensed under the MIT License - see the LICENSE file for details.

#### Contact
For questions or feedback, contact Craig Derington.
