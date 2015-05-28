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

def get_calendar_service(tokenFile):
    with open(tokenFile, 'r') as f:
        credentials = oauth2client.client.Credentials.new_from_json(f.read())
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
    parser.add_argument('--hours', help='how many hours from now to start the event')
    parser.add_argument('--start', help='start time of the event: CCYY-MM-DDTHH:MM:SS')
    parser.add_argument('--end', help='end time of the event: CCYY-MM-DDTHH:MM:SS')
    parser.add_argument('-t', '--tokenFile', action='store', required=True, help='file containing OAuth token in JSON format')

    args = parser.parse_args()
    calendar_service = get_calendar_service(args.tokenFile)
    if args.hours:
        startTime = (datetime.datetime.now() + datetime.timedelta(hours=int(args.hours))).replace(microsecond=0).isoformat()
        print(startTime)
        print(make_event(calendar_service, args.name, startTime))
    else:
        if args.start:
            print(make_event(calendar_service, args.name, args.start, args.end))
        else:
            print(make_event(calendar_service, args.name))
