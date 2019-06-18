#!/usr/bin/env python

import argparse
import pprint
import datetime
import utils

def recurrence_string_to_recurrence_rule(recurrence):
    s = 'RRULE:FREQ={}'.format(recurrence.upper())
    return(['RRULE:FREQ={}'.format(recurrence.upper())])

def attendees_string_to_list_of_dictionaries(attendees):
    list = []
    for attendee in attendees.split(','):
        list.append( { 'email': attendee } )
    return(list)

def make_event(calendar_service, name, startTime, endTime, allDay=False,
               recurrence=None, attendees=None, notifications=False,
               verbose=False):
    event = {
        'summary': name
    }
    if allDay:
        endTime = startTime + datetime.timedelta(days=1)
        event['start'] = {
            'date': startTime.strftime('%Y-%m-%d')
        }
        event['end'] = {
            'date': endTime.strftime('%Y-%m-%d')
        }
        event['transparency'] = 'transparent'
    else:
        tzOffSet = utils.getTimeZoneOffSet()
        tzName = utils.getTimeZoneName()
        event['start'] = {
            'dateTime': startTime.replace(microsecond=0).isoformat() + tzOffSet,
            'timeZone': tzName
        }
        event['end'] = {
            'dateTime': endTime.replace(microsecond=0).isoformat() + tzOffSet,
            'timeZone': tzName
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
    calendar_service = utils.get_calendar_service(args.tokenFile)
    allDay = False
    if args.start:
        if 'T' in args.start:
            startTime = datetime.datetime.strptime(args.start, '%Y-%m-%dT%H:%M:%S')
        else:
            # add all day events if the start date has no time stamp
            allDay = True
            startTime = datetime.datetime.strptime(args.start, '%Y-%m-%d')
    else:
        startTime = datetime.datetime.now() + datetime.timedelta(minutes=int(args.minutes))
    if args.verbose: print('start time: {} type:{}'.format(startTime, type(startTime)))
    if args.end:
        endTime = datetime.datetime.strptime(args.end, '%Y-%m-%dT%H:%M:%S')
    else:
        endTime = startTime + datetime.timedelta(minutes=int(args.duration))
    if args.verbose: print('end time: {} type:{}'.format(endTime, type(endTime)))
    print(make_event(calendar_service, args.name, startTime, endTime, allDay,
                     recurrence=args.recurrence, attendees=args.attendees,
                     notifications=args.notifications, verbose=args.verbose))
