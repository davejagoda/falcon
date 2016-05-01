Falcon
======

Falcon reads and writes Google Calendars

Installation
------------

`cd ~src/github`

`git clone git@github.com:davejagoda/falcon.git`

`cd falcon`

`virtualenv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

Resources
---------

https://developers.google.com/api-client-library/python/apis/calendar/v3

https://developers.google.com/google-apps/calendar/v3/reference/

https://developers.google.com/google-apps/calendar/v3/reference/events/insert

https://tools.ietf.org/html/rfc2445

Sample Invocations
------------------

`./mkCalendarEvent.py "ring in the new millennium" --start 1999-12-31T23:00:00 --token token.json -v`

If you set up a Procfile with a reference to the right token, you can do this:

`honcho start`
