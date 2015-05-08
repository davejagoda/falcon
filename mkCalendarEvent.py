#!/usr/bin/env python

import argparse
import pprint
import httplib2
import apiclient.discovery
import oauth2client.client
import datetime
import time

def getTimeZoneOffSet():
    if time.localtime().tm_isdst:
        tzoffset = time.altzone
    else:
        tzoffset = time.timezone
    hh = tzoffset / -3600
    mm = tzoffset % 60
    if hh < 0:
        sign = '-'
        hh *= -1
    else:
        sign = '+'
    return('{}{:02d}:{:02d}'.format(sign,hh,mm))

def get_calendar_service():
    f = open('bearer_token_rw.json', 'r')
    credentials = oauth2client.client.Credentials.new_from_json(f.read())
    f.close()
    http = httplib2.Http()
    credentials.authorize(http)
    return(apiclient.discovery.build('calendar', 'v3', http=http))

def make_event(calendar_service, name, start=None, end=None):
    if None == start:
        startTime = datetime.datetime.now()
    else:
        startTime = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
    print(type(startTime))
    if None == end:
        endTime = startTime + datetime.timedelta(hours=1)
    else:
        endTime = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
    event = {
        'summary': name,
        'start': {
            'dateTime': startTime.replace(microsecond=0).isoformat()+getTimeZoneOffSet()
            },
        'end': {
            'dateTime': endTime.replace(microsecond=0).isoformat()+getTimeZoneOffSet()
            }
        }
    print(event)
    result = calendar_service.events().insert(calendarId='primary', body=event).execute()
    return(result['id'])
'''
    result = []
    page_token = None
    while True:
        events = calendar_service.events().list(calendarId='primary', pageToken=page_token).execute()
        result.extend(events['items'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return(result)
'''
if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('name', help='name of the event')
    parser.add_argument('--start', help='start time of the event: CCYY-MM-DDTHH:MM:SS')
    parser.add_argument('--end', help='end time of the event: CCYY-MM-DDTHH:MM:SS')
    args = parser.parse_args()
    calendar_service = get_calendar_service()
    if args.start:
        print(make_event(calendar_service, args.name, args.start, args.end))
    else:
        print(make_event(calendar_service, args.name))
