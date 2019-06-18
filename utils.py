#!/usr/bin/env python

import httplib2
import apiclient.discovery
import oauth2client.client
import os
import re
import time

def get_calendar_service(tokenFile):
    with open(tokenFile, 'r') as f:
        credentials = oauth2client.client.Credentials.new_from_json(f.read())
    http = httplib2.Http()
    credentials.authorize(http)
    return(apiclient.discovery.build('calendar', 'v3', http=http))

def getTimeZoneName(verbose=0):
    tzlink = os.readlink('/etc/localtime')
    for pattern in [
            '^/usr/share/zoneinfo/(.*)$',
            '^/var/db/timezone/zoneinfo/(.*)$'
    ]:
        match = re.search(pattern, tzlink)
        if match:
            if verbose > 0:
                print('matched:{}'.format(pattern))
            return(match.group(1))
        else:
            if verbose > 0:
                print('failed to match pattern:{}'.format(pattern))

def getTimeZoneOffSet():
    if time.localtime().tm_isdst:
        tzoffset = time.altzone
    else:
        tzoffset = time.timezone
    hh = int(tzoffset / -3600)
    mm = tzoffset % 60
    if hh < 0:
        sign = '-'
        hh *= -1
    else:
        sign = '+'
    return('{}{:02d}:{:02d}'.format(sign,hh,mm))

def toRFC3339(date_str):
    if 'T' not in date_str:
        # if there's no T, you have just a date
        date_str += 'T00:00:00'
    if 3 == len(date_str.split('-')):
        # a timezone offset was not provided
        date_str += getTimeZoneOffSet()
    return(date_str)
