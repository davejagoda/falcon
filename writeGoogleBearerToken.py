#!/usr/bin/env python

import oauth2client.client
import webbrowser

OAUTH2_SCOPE = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRETS = 'client_secrets.json'

flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
authorize_url = flow.step1_get_authorize_url()
webbrowser.open(authorize_url)
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)
f = open('bearer_token.json', 'w')
f.write(credentials.to_json())
f.close()
