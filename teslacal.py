#
# teslacal
#
# Have events in your Google Calendar execute commands on your Tesla car.
# 
# (c) 2016 by Lourens Rozema
# 

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText
from ConfigParser import RawConfigParser

import smtplib
import datetime
import shelve
import teslajson
import sys
import httplib2
import os

# Load the configuration
config = RawConfigParser()
config.read('teslacal.cfg')

# Connect to the Tesla cloud
c = teslajson.Connection(config.get('tesla', 'username'), config.get('tesla', 'password'))

# Filter the vehicles list based on VIN if specified
va = c.vehicles
vin = config.get('tesla', 'vin')
if vin is None:
	va = [ v for v in va if v['vin'] == vin ]

# Make sure we did find a vehicle and then select the first
if not len(va):
	raise Exception("Tesla not found!")
v = va[0]

print "Tesla "+v['display_name']+" found!"

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar Tesla API'

# Obtain optional credentials flags
try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

# Obtain Google credentials
store = Storage('credential.json')
credentials = store.get()
if not credentials or credentials.invalid:
	flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
	flow.user_agent = APPLICATION_NAME
	if flags:
		credentials = tools.run_flow(flow, store, flags)
	else:
		credentials = tools.run(flow, store)

# Make connection with the Google calendar
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

# Acquire all events from the calendar that are currently active
minuteAgo = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).isoformat() + 'Z'
now = datetime.datetime.utcnow().isoformat() + 'Z'
print('Getting the current 10 events')
eventsResult = service.events().list(calendarId=config.get('google', 'calendarId'), timeMin=minuteAgo, timeMax=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
events = eventsResult.get('items', [])

# Get a list of all processed events from the shelve
oldEvents = shelve.open('old_events.db')

for event in events:
	# Obtain event start date and time, event unique index and event summary text
	start = event['start'].get('dateTime', event['start'].get('date'))
	idx = str(event['id'])
	text = event['summary'].lower()

	# Make sure we haven't already executed this event
	if idx in oldEvents and oldEvents[idx] == start:
		continue

	# Convert calendar keywords into Tesla API actions
	if 'tesla honk horn' in text:
		action = 'honk_horn'
	elif 'tesla flash lights' in text:
		action = 'flash_lights'
	elif 'tesla airco' in text or 'tesla start airco' in text:
		action = 'auto_conditioning_start'
	elif 'tesla stop airco' in text:
		action = 'auto_conditioning_stop'
	elif 'tesla charge' in text or 'tesla start charging' in text:
		action = 'charge_start'
	elif 'tesla stop charging' in text:
		action = 'charge_stop'
	else:
		continue;

	# Debug the event
	print(start, idx, action, text)

	# Wake up our car and execute the command
	v.wake_up()
	v.command(action)

	# Is email notification setup?
	smtp = config.get('email', 'smtp')
	if smtp is not None:
		frm = config.get('email', 'from')
		to = config.get('email', 'to')

		# Send us a message about the progress
		subject = 'Tesla action '+action+' executed because of '+text+' at '+start

		# Setup message header
		msg = MIMEText(subject)
		msg['Subject'] = subject
		msg['From'] = frm
		msg['To'] = to

		# Send the message via our SMTP server
		s = smtplib.SMTP(smtp)
		s.sendmail(frm, [to], msg.as_string())
		s.quit()

	# Mark the event processed
	oldEvents[idx] = start

# Store a list of used events onto the shelve
oldEvents.close()

