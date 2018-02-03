from datetime import datetime
import argparse
import config
import logging
import json
import pymongo
import requests

# set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] [%(threadName)s] (%(module)s:%(lineno)d) %(message)s',
    filename='logs/M1-Data-Log.log'
)

# set up request headers
hdr = {
    'user-agent': 'Mozilla/Linux 5.0',
    'content-type': 'application/json'
}


# main entry point
def main(radius, zip_code):

    # first, test the connection to the database
    try:
        client = pymongo.MongoClient(config.MONGO_SERVER, 27017)
        db = client[config.MONGO_DB]

        today = datetime.now().strftime('%c')
        dealer = 'DMS'
        client = 'DMS'
        sub_client = 'Diamond-CRMDev'
        product = 'earl'
        vendor_id = 'DMS'
        days_to_suppress = 0
        radius = radius
        zip_code = zip_code

        # query the sent collection for new IP's
        sent_collection = db['sent_collection']
        data = sent_collection.find({'processed': 0}, {'_id': 1, 'ip': 1, 'agent': 1, 'send_hash': 1,
                                                       'job_number': 1, 'client_id': 1})

        # we have new IP's to process, continue
        if data:

            for item in data:
                record_id = item['_id']
                client_id = item['client_id']
                job_number = item['job_number']
                ip = item['ip']

                # create the URL
                M1_URL = 'https://datamatchapi.com/DMSApi/GetDmsApiData?IP={}&Dealer=DMS&Client=DMS&SubClient=Diamond-CRMDev' \
                         '&product=earl&JobNumber={}&ClientID={}&VendorID=DMS&DaysToSuppress=0&Radius={}&ZipCode={}'.format(
                          ip, job_number, client_id, radius, zip_code)

                try:
                    # call M1
                    r = requests.get(M1_URL, headers=hdr)

                    # output to console for testing
                    print(r.status_code, r.content)

                    # if we get a valid response, continue processing
                    if r.status_code == 200:
                        if 'Invalid location' in r.content:
                            logging.warning('M1 API Returned No Data for IP: {}'.format(ip))
                        else:
                            logging.info('{} {} Appended Data: {}'.format(today, ip, json.dumps(r.content)))

                    # update the record and set processed = true
                    sent_collection.update_one({'_id': record_id}, {'$set': {'processed': 1}}, True)

                except requests.HTTPError as e:
                    logging.critical('The program encountered an HTTP error: {}'.format(e))

        else:

            logging.info('M1 automation did not find any new IPs on {}'.format(today))

    except pymongo.errors.ConnectionFailure as e:
        logging.critical('The connection to the MongoDB instance failed: {}'.format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pixel Tracker M1 API Implementation')
    parser.add_argument('-radius', type=int, default=0, help='Enter the radius...')
    parser.add_argument('-zip_code', type=str, default='29501', help='Enter the zip code...')
    args = parser.parse_args()

    if not args:
        print('This program requires two arguments, radius and zip_code.  Please retry with -r and -z args.')
    else:
        main(args.radius, args.zip_code)
