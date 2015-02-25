#!/usr/bin/env python

import argparse
import pprint
import httplib2
import apiclient.discovery
import oauth2client.client

def get_calendar_service():
    f = open('bearer_token.json', 'r')
    credentials = oauth2client.client.Credentials.new_from_json(f.read())
    f.close()
    http = httplib2.Http()
    credentials.authorize(http)
    return(apiclient.discovery.build('calendar', 'v3', http=http))

def get_raw_result(calendar_service):
    result = []
    page_token = None
    while True:
        events = calendar_service.events().list(calendarId='primary', pageToken=page_token).execute()
        result.extend(events['items'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return(result)

def print_raw_result(result):
    print('total {}'.format(len(result)))
    for item in result:
        pprint.pprint(item)

def print_names_only(result):
    names = []
    for item in result:
        try:
            names.append(item['summary'])
        except:
            names.append('NO SUMMARY')
    names.sort()
    for name in names:
        print(name.encode('utf8'))

if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--raw', help='pretty print the raw output', action='store_true')
    args = parser.parse_args()
    calendar_service = get_calendar_service()
    result = get_raw_result(calendar_service)
    if (args.raw):
        print_raw_result(result)
    else:
        print_names_only(result)
