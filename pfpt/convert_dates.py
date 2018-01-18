import pymongo
import datetime

client = pymongo.MongoClient('localhost', 27017)
db = client['flask-pixel-tracker']

campaign_collection = db['campaign_collection']
sent_collection = db['sent_collection']
open_collection = db['opens_collection']

opens = open_collection.find({})
campaigns = campaign_collection.find({})
sends = sent_collection.find({})

for o in opens:
    if isinstance(o['date_sent'], int):
        dt = datetime.datetime.fromtimestamp(o['date_sent'])
        open_collection.update_one({'_id': o['_id']}, {'$set': {'date_sent': dt}})
        print('{} updated'.format(o['_id']))
    else:
        print('Open date is not an integer...')

for campaign in campaigns:
    if isinstance(campaign['date_sent'], int):
        dt = datetime.datetime.fromtimestamp(campaign['date_sent'])
        campaign_collection.update_one({'_id': campaign['_id']}, {'$set': {'date_sent': dt}})
        print('{} date changed to {}'.format(campaign['_id'], dt))
    else:
        print('Campaign date is not an integer...')

for sent in sends:
    if isinstance(sent['sent_date'], int):
        dt = datetime.datetime.fromtimestamp(sent['sent_date'])
        sent_collection.update_one({'_id': sent['_id']}, {'$set': {'sent_date': dt}})
        print('{} date changed to {}'.format(sent['_id'], dt))
    else:
        print('Sent date is not an integer...')

