# pylint: disable=line-too-long
#!/usr/bin/python
"""
As readline_data.py provided by by Allen B. Downey, available from greenteapress.com become invalid.
Orlando, Ding use https://www.mbta.com/developers/v3-api to collect redline data,
For when this subline arrive at Kendall plate.
License: Apache-2.0 https://github.com/llv22/thinkbayes/blob/master/LICENSE
Reference:
    1. argparse - https://www.cnblogs.com/arkenstone/p/6250782.html and https://mkaz.blog/code/python-argparse-cookbook/
    2. urlopen - https://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python
    3. python 2/3 for Request - https://stackoverflow.com/questions/7933417/how-do-i-set-headers-using-pythons-urllib
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, date, time
import requests
import pandas as pd

TOKEN_ENV = 'API_KEY'
MBTA_V3_URL = 'https://api-v3.mbta.com'
SUBLINE_NAME = 'Red'
STOP_MBTA_URL = '{}/stops'
SCHEDULE_MBTA_URL = '{}/schedules'
COLUMNS = ['schedule_id', 'drop_off_type', 'pickup_type', 'date', 'arrival_time', 'departure_time']

def getStopId_urllib(token: str, stop_name: str):
    """
    using urllib to get stop id.
    Status: Deprecated
    """
    # load library for deprecated API
    try:
        from urllib.parse import urlencode
        from urllib.request import Request, urlopen  # Python 3
    except ImportError:
        from urllib import urlencode
        from urllib2 import Request, urlopen  # Python 2
    import json

    params = urlencode({'filter[route]': SUBLINE_NAME})
    q = Request(STOP_MBTA_URL.format(MBTA_V3_URL, params))
    q.add_header('x-api-key', token)
    raw_content = urlopen(q).read()
    json_content = json.loads(raw_content)
    for stop in json_content['data']:
        try:
            if stop['attributes']['name'] == stop_name:
                stopId_ = stop['id']
        except KeyError:
            pass
    return stopId_

def getStopId(token: str, stop_name: str):
    """
    get stop id in mbta system.
    """
    stopId_ = None
    url_ = STOP_MBTA_URL.format(MBTA_V3_URL)
    params_ = {'filter[route]': SUBLINE_NAME}
    headers_ = {'x-api-key': token}
    resp = requests.get(url=url_, params=params_, headers=headers_)
    raw_json = resp.json()
    for stop in raw_json['data']:
        try:
            if stop['attributes']['name'] == stop_name:
                stopId_ = stop['id']
        except KeyError:
            pass
    return stopId_

def getScheduleLine(token_: str, stopId_: str, date_: date, mintime_: time, maxtime_: time):
    """
    Using https://api-v3.mbta.com/schedules to query lines of data.
    """
    schedules = []
    url_ = SCHEDULE_MBTA_URL.format(MBTA_V3_URL)
    params_ = {'filter[stop]': stopId_, 'sort': 'arrival_time', 'filter[direction_id]': '0', 
               'filter[date]': date_.strftime('%Y-%m-%d'), 'filter[min_time]': mintime_.strftime('%H:%M'), 'filter[max_time]': maxtime_.strftime('%H:%M')}
    headers_ = {'x-api-key': token_}
    resp = requests.get(url=url_, params=params_, headers=headers_)
    raw_json = resp.json()
    for line in raw_json['data']:
        try:
            schedule_id = line['id']
            schedule = line['attributes']
            drop_off_type = schedule['drop_off_type']
            pickup_type = schedule['pickup_type']
            arrival_time = schedule['arrival_time']
            departure_time = schedule['departure_time']
            schedules.append((schedule_id, drop_off_type, pickup_type, date_, arrival_time, departure_time))
        except KeyError:
            pass
    return schedules

def main():
    """
    process RED line data from REST api https://api-v3.mbta.com/
    """
    try:
        token = os.environ[TOKEN_ENV]
    except KeyError:
        print("Fatal: Environment variable {} doesn't set".format(TOKEN_ENV))
        sys.exit(-1)
    if FLAGS.startdate > FLAGS.enddate:
        print("Fatal: startdate must be less than or equal with enddate")
        sys.exit(-1)
    if FLAGS.mintime >= FLAGS.maxtime:
        print("Fatal: mintime must be less than maxtime")
        sys.exit(-1)
    # validate FLAGS.stop and get stop Id
    stop_Id = getStopId(token, FLAGS.stop)
    if stop_Id == None:
        raise ValueError("invalid stop name:{} for querying".format(FLAGS.stop))
        sys.exit(-1)
    # print(FLAGS.outputfile, FLAGS.startdate, FLAGS.enddate, FLAGS.mintime, FLAGS.maxtime)
    dates_range = [FLAGS.startdate + timedelta(days=x) for x in range(0, (FLAGS.enddate - FLAGS.startdate).days)]
    total_schedules = []
    for date_ in dates_range:
        schedules = getScheduleLine(token, stop_Id, date_, FLAGS.mintime, FLAGS.maxtime)
        total_schedules.extend(schedules)
    df = pd.DataFrame(total_schedules, columns=COLUMNS)
    df.to_csv(FLAGS.outputfile, compression='gzip', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to read schedule data of Subline RED")
    parser.add_argument("--outputfile", type=str, default="redline.csv.gz")
    parser.add_argument("--startdate", default="2018-03-07", type=lambda d: datetime.strptime(d, '%Y-%m-%d').date())
    parser.add_argument("--enddate", default="2018-03-16", type=lambda d: datetime.strptime(d, '%Y-%m-%d').date())
    parser.add_argument("--mintime", default="16:00", type=lambda t: datetime.strptime(t, '%H:%M').time())
    parser.add_argument("--maxtime", default="18:00", type=lambda t: datetime.strptime(t, '%H:%M').time())
    parser.add_argument("--stop", type=str, default="Kendall/MIT")
    FLAGS, unparsed = parser.parse_known_args()
    main()
