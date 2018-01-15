import requests
import time

hdr = {
    'user-agent': 'PythonBot2.7',
    'content-type': 'PixelTracker'
}

url = "http://35.153.237.152/api/generate-pixel?job_number=apn982134u&client_id=xrnT9547398e&campaign=ORLANDO_LEXUS"

for i in range(520):
    try:
        r = requests.get(url, headers=hdr)
        if r.status_code == 200:
            print(r.text)
        else:
            print('HTTP Error')
    except requests.HTTPError:
        print('There was a problem communicating with the server.  Please try again...')

    time.sleep(1.256)

