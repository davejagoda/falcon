#!/usr/bin/env python

import argparse
import pprint
import httplib2
import apiclient.discovery
import oauth2client.client
import datetime
import time
import os
import re

def getTimeZoneName():
    tzlink = os.readlink('/etc/localtime')
    pattern = '^/usr/share/zoneinfo/(.*)$'
    match = re.search(pattern, tzlink)
    return(match.group(1))

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

def recurrence_string_to_recurrence_rule(recurrence):
    s = 'RRULE:FREQ={}'.format(recurrence.upper())
    return(['RRULE:FREQ={}'.format(recurrence.upper())])

def attendees_string_to_list_of_dictionaries(attendees):
    list = []
    for attendee in attendees.split(','):
        list.append( { 'email': attendee } )
    return(list)

def make_event(calendar_service, name, start, end, recurrence=None, attendees=None, notifications=False, verbose=False):
    event = {
        'summary': name,
        'start': {
            'dateTime': startTime.replace(microsecond=0).isoformat()+getTimeZoneOffSet(),
            'timeZone': getTimeZoneName()
            },
        'end': {
            'dateTime': endTime.replace(microsecond=0).isoformat()+getTimeZoneOffSet(),
            'timeZone': getTimeZoneName()
            }
        }
    if recurrence:
        event['recurrence'] = recurrence_string_to_recurrence_rule(recurrence)
    if attendees:
        event['attendees'] = attendees_string_to_list_of_dictionaries(attendees)
    if notifications:
        event['reminders'] = {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 10}]}
    if verbose: print(event)
    result = calendar_service.events().insert(calendarId='primary', body=event).execute()
    return(result['id'])

if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='name of the event')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--tokenFile', action='store', required=True, help='file containing OAuth token in JSON format')
    alpha = parser.add_mutually_exclusive_group(required=True)
    alpha.add_argument('-s', '--start', help='start time of the event: CCYY-MM-DDTHH:MM:SS')
    alpha.add_argument('-m', '--minutes', help='how many minutes from now to start the event')
    omega = parser.add_mutually_exclusive_group()
    omega.add_argument('-e', '--end', help='end time of the event: CCYY-MM-DDTHH:MM:SS')
    omega.add_argument('-d', '--duration', default='30', help='duration of the event in minutes')
    parser.add_argument('-a', '--attendees', help='comma separated list of additional attendee email addresses')
    parser.add_argument('-n', '--notifications', action='store_true', help='send a notification 10 minutes before the event')
    parser.add_argument('-r', '--recurrence', choices=['secondly', 'minutely', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'], help='make a recurring event')
    args = parser.parse_args()
    print(getTimeZoneName())
    calendar_service = get_calendar_service(args.tokenFile)
    if args.start:
        startTime = datetime.datetime.strptime(args.start, '%Y-%m-%dT%H:%M:%S')
    else:
        startTime = datetime.datetime.now() + datetime.timedelta(minutes=int(args.minutes))
    if args.verbose: print('start time: {} type:{}'.format(startTime, type(startTime)))
    if args.end:
        endTime = datetime.datetime.strptime(args.end, '%Y-%m-%dT%H:%M:%S')
    else:
        endTime = startTime + datetime.timedelta(minutes=int(args.duration))
    if args.verbose: print('end time: {} type:{}'.format(endTime, type(endTime)))
    print(make_event(calendar_service, args.name, startTime, endTime, recurrence=args.recurrence, attendees=args.attendees, notifications=args.notifications, verbose=args.verbose))
