from celery import Celery
from flask import Flask, make_response, redirect, request, Response, render_template, url_for, flash
from decorators import login_required
from forms import AddCampaignForm
from flask_paginate import Pagination, get_page_parameter
import argparse
import config
import base64
import copy
import datetime
import getpass
import hashlib
import json
import os
import pymongo
import random
import string
import time

debug = True

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['MONGO_SERVER'] = 'localhost'
app.config['MONGO_DB'] = 'earl-pixel-tracker'

mongo_client = pymongo.MongoClient(app.config['MONGO_SERVER'], 27017, connect=False)
mongo_db = mongo_client[app.config['MONGO_DB']]

celery = Celery('pfpt.main', broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def consume_open(event_record):
    send_hash = event_record['data']['sh'] if 'sh' in event_record['data'] else None

    event_collection = mongo_db['event_collection']
    event_id = event_collection.insert_one(event_record)

    sent_collection = mongo_db['sent_collection']
    campaign_collection = mongo_db['campaign_collection']
    open_collection = mongo_db['opens_collection']

    sent_collection.update_one({'send_hash': send_hash}, {'$inc': {'opens': 1}}, True)

    sent_email = sent_collection.find_one({'send_hash': send_hash})

    campaign_hash = sent_email['campaign_hash']
    open_hash = sent_email['open_hash']

    open_result = open_collection.update_one({'open_hash': open_hash}, {'$inc': {'opens': 1}}, True)

    if open_collection.find_one({'open_hash': open_hash})['opens'] == 1:
        campaign_collection.update_one({'campaign_hash': campaign_hash}, {'$inc': {'opens': 1}}, True)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return redirect('/campaigns', 302)


@app.route("/pixel.gif", methods=['GET'])
def pixel():
    pixel_data = base64.b64decode("R0lGODlhAQABAIAAAP8AAP8AACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==")
    event_record = dict(time=int(time.time()), data={}, headers={})

    event_record['data'] = copy.deepcopy(request.args)

    for header in request.headers:
        event_record['headers'][header[0]] = request.headers.get(header[0])

    consume_open.delay(event_record)

    return Response(pixel_data, mimetype="image/gif")


@app.route("/api/generate-pixel")
def generate_pixel():
    ip = request.environ['REMOTE_ADDR']
    agent = request.headers.get('User-Agent')
    referer = request.headers.get('Referer')
    current_time = datetime.datetime.now()

    event_record = {
        'ip': ip,
        'job_number': request.args.get('job_number', None),
        'client_id': request.args.get('client_id', None),
        'campaign': request.args.get('campaign', None),
        'opens': 0,
        'agent': agent,
        'referer': referer,
        'processed': 0,
        'num_visits': 1
    }

    send_hash = hashlib.sha1('{}'.format(event_record)).hexdigest()
    campaign_hash = hashlib.sha1(event_record['campaign']).hexdigest()
    open_hash = hashlib.sha1('{}:{}'.format(event_record['campaign'],
        event_record['job_number'])).hexdigest()

    event_record['send_hash'] = send_hash
    event_record['campaign_hash'] = campaign_hash
    event_record['open_hash'] = open_hash
    event_record['sent_date'] = datetime.datetime.now()

    sent_collection = mongo_db['sent_collection']

    # check to see if this IP and Send Hash are already in the collection
    visitor_exists = sent_collection.find_one({'ip': ip, 'send_hash': event_record['send_hash']})

    if visitor_exists is None:
        # this IP has not been seen recently, add it to the collection
        sent_collection.insert_one(event_record)
    else:
        sent_collection.update_one({'_id': visitor_exists['_id']}, {'$inc': {'num_visits': 1}}, True)

    campaign_collection = mongo_db['campaign_collection']
    open_collection = mongo_db['opens_collection']

    if campaign_collection.find_one({'campaign_hash': campaign_hash}) is None:
        campaign_collection.insert_one({
            'ip': ip,
            'campaign_hash': campaign_hash,
            'campaign': event_record['campaign'],
            'job_number': event_record['job_number'],
            'client_id': event_record['client_id'],
            'user_agent': event_record['agent'],
            'opens': 0,
            'sends': 1,
            'date_sent': datetime.datetime.now(),
        })
    else:
        campaign_collection.update_one({'campaign_hash': campaign_hash}, {'$inc': {'sends': 1}}, True)

    if open_collection.find_one({'open_hash': open_hash}) is None:
        open_collection.insert_one({
            'ip': ip,
            'open_hash': open_hash,
            'campaign_hash': campaign_hash,
            'campaign': event_record['campaign'],
            'opens': 0,
            'sends': 1,
            'date_sent': datetime.datetime.now(),
        })
    else:
        open_collection.update_one({'open_hash': open_hash}, {'$inc': {'sends': 1}}, True)

    return Response(json.dumps({'id': send_hash}), mimetype="application/json")


@app.route("/campaigns")
@login_required
def campaigns():
    campaign_collection = mongo_db['campaign_collection']

    output = []

    for campaign in campaign_collection.find({}, {'_id': False}):
        if campaign['opens'] != 0:
            campaign['open_percent'] = (float(campaign['opens']) / float(campaign['sends'])) * 100.00
        else:
            campaign['open_percent'] = 0

        output.append(campaign)

    return render_template(
        'campaigns.html',
        campaigns=output
    )


@app.route("/campaign/<string:campaign_hash>")
@login_required
def campaign_detail(campaign_hash):
    search = False
    q = request.args.get('q')

    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)
    campaign_collection = mongo_db['campaign_collection']
    open_collection = mongo_db['opens_collection']
    sent_collection = mongo_db['sent_collection']

    campaigns = campaign_collection.find_one({'campaign_hash': campaign_hash}, {'_id': False})
    sends = sent_collection.find({'campaign_hash': campaign_hash}, {'_id': False}).sort('sent_date', pymongo.DESCENDING)

    output = {}
    output['campaigns'] = campaigns
    output['sends'] = []

    for e in sends:
        output['sends'].append(e)

    pagination = Pagination(
        page=page,
        total=len(output['sends']),
        search=search,
        record_name=sends,
        css_framework='bootstrap',
        per_page_parameter=10
    )

    return render_template(
        'campaign_detail.html',
        campaigns=output,
        sends_count=len(output['sends']),
        pagination=pagination
    )


@app.route('/campaign/add', methods=['GET', 'POST'])
def add_campaign():
    form = AddCampaignForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():

        event_record = {
            'job_number': form.job_number.data,
            'client_id': form.client_id.data,
            'campaign': form.campaign.data,
            'date_sent': datetime.datetime.now(),
            'sends': 0,
            'ip': None,
            'opens': 0
        }

        # hash our data and create the campaign event record
        campaign_hash = hashlib.sha1(event_record['campaign']).hexdigest()
        event_record['campaign_hash'] = campaign_hash
        campaign_collection = mongo_db['campaign_collection']
        campaign_collection.insert_one(event_record)
        flash('Campaign {} created successfully for {}'.format(campaign_hash, event_record['campaign']),
              category='success')
        return redirect(url_for('campaigns'))

    return render_template(
        'add_campaign.html',
        form=form
    )


@app.route('/leads', methods=['GET'])
def leads():
    return render_template(
        'leads.html'
    )


@app.route('/reports', methods=['GET'])
def reports():
    return render_template(
        'reports.html'
    )


@app.route("/login")
def login():
    return redirect('/auth/login', 302)


@app.route("/auth/login", methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', None)
    password = request.form.get('password', None)

    user = get_user(username)

    if user and check_password(password, user['password']):
        token = hashlib.sha512(''.join([random.SystemRandom().choice(string.ascii_letters)
                                        for _ in xrange(1024)])).hexdigest()

        user_collection = mongo_db['auth_users']
        user_collection.update_one({'username': username}, {'$set': {'token': token, }})
        resp = make_response(redirect('/campaigns', 302))
        resp.set_cookie('token', token, 3600 * 24 * 30)

        return resp

    flash('Sorry, your login credentials have failed.  Please try again...', category='danger')
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect('/campaigns', 302))
    resp.set_cookie('token', expires=0)
    flash('You have been successfully logged out.  Thank you!', category='info')
    return resp


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


@app.template_filter('formatdate')
def format_date(value):
    dt = value
    return dt.strftime('%Y-%m-%d %H:%M')


def set_password(raw_password):
    algo = 'sha512'
    salt = os.urandom(128)
    encoded_salt = base64.b64encode(salt)
    hsh = hashlib.sha512('{}{}'.format(salt, raw_password)).hexdigest()
    return '{}:{}:{}'.format(algo, encoded_salt, hsh)


def check_password(raw_password, enc_password):
    algo, encoded_salt, hsh = enc_password.split(':')
    salt = base64.b64decode(encoded_salt)
    return hsh == hashlib.sha512('{}{}'.format(salt, raw_password)).hexdigest()


def get_user(username):
    user_collection = mongo_db['auth_users']
    return user_collection.find_one({'username': username})


def create_user(username, password):
    user_collection = mongo_db['auth_users']

    return user_collection.update_one({
            'username': username
        }, {
            '$set': {
                'password': set_password(password),
                'token': None,
            }
        }, True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python, Flask & Celery implementation of Pixel Tracking')

    parser.add_argument('command', nargs=1, choices=('run', 'create-admin-user', ))
    args = parser.parse_args()
    port = 5580

    if 'run' in args.command:
        app.run(debug=debug, port=port)
    elif 'create-admin-user' in args.command:
        username = raw_input("Username: ")
        password = getpass.getpass("Password: ")
        create_user(username, password)
        print('User {} has been created.'.format(username))
