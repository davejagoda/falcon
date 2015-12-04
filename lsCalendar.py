#!/usr/bin/env python

import argparse
import pprint
import httplib2
import apiclient.discovery
import oauth2client.client
from mkCalendarEvent import getTimeZoneOffSet

def get_calendar_service(tokenFile):
    with open(tokenFile, 'r') as f:
        credentials = oauth2client.client.Credentials.new_from_json(f.read())
    http = httplib2.Http()
    credentials.authorize(http)
    return(apiclient.discovery.build('calendar', 'v3', http=http))

def get_raw_result(calendar_service, timeMin=None, timeMax=None, verbose=False):
    if timeMin:
        if 3 == len(timeMin.split('-')):
            # a timezone offset was not provided
            timeMin += getTimeZoneOffSet()
    if timeMax:
        if 3 == len(timeMax.split('-')):
            # a timezone offset was not provided
            timeMax += getTimeZoneOffSet()
    result = []
    page_token = None
    while True:
        events = calendar_service.events().list(calendarId='primary', timeMin=timeMin, timeMax=timeMax, pageToken=page_token).execute()
        result.extend(events['items'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break
        else:
            if verbose: print('got a page_token')
    return(result)

def print_raw_result(result):
    print('total {}'.format(len(result)))
    for item in result:
        pprint.pprint(item)

def print_names_only(result):
    names = []
    for item in result:
        if 'start' in item:
            startDict = item['start']
        else:
            startDict = item['originalStartTime']
        if 'dateTime' in startDict:
            dateTime = startDict['dateTime']
        else:
            dateTime = startDict['date']
        if 'summary' in item:
            summary = item['summary']
        else:
            summary = 'NO SUMMARY'
        names.append(dateTime + summary)
    names.sort()
    for name in names:
        print(name.encode('utf8'))

if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-r', '--raw', help='pretty print the raw output', action='store_true')
    parser.add_argument('-t', '--tokenFile', action='store', required=True, help='file containing OAuth token in JSON format')
    parser.add_argument('-n', '--timeMin', help='filter by min time e.g. 1999-12-31T00:00:00 or 1999-12-31T00:00:00-07:00')
    parser.add_argument('-x', '--timeMax', help='filter by max time e.g. 2000-01-01T23:59:59 or 2000-01-01T23:59:59-07:00')
    args = parser.parse_args()
    calendar_service = get_calendar_service(args.tokenFile)
    result = get_raw_result(calendar_service, args.timeMin, args.timeMax, verbose=args.verbose)
    if (args.raw):
        print_raw_result(result)
    else:
        print_names_only(result)
