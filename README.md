# teslacal
Have events in your Google Calendar execute commands on your Tesla car.

(c) 2016 by Lourens Rozema

## Description
This is a python program that checks your Google Calendar for events
and once the time passes an event it will execute the corresponding
command on your Tesla car. This allows amongst others to turning on 
the airconditioning before departing based on your calendar.

## Installation
0. Download the repository zip file and uncompress it.
0. Download and install https://github.com/gglockner/teslajson
0. Go to https://developers.google.com/google-apps/calendar/quickstart/python and
execute step 1, afterwards put the downloaded file as client_secret.json
in the same directory as teslacal.py. Also install google-api-python-client according 
to step 2: pip install --upgrade google-api-python-client
0. Finally create the file teslacal.cfg see below for details.
0. And then start adding events in your Google calendar.

## Configuration
```
[tesla]
username = email@email.com
password = abc123
vin = YOURVINNUMBER

[google]
calendarId = primary

[email]
smtp = localhost
from = email@email.com
to = email@email.com
```
You have to specify your Tesla account login for connecting to your car.
The VIN number is optional, if not specified the first car will be chosen.

When a command is succesfully executed the script will send you an e-mail
about it. If you don't want e-mail then remove the email section.

# Events
The following events are supported:
* Tesla honk horn
* Tesla flash lights
* Tesla airco
* Tesla start airco
* Tesla stop airco
* Tesla charge
* Tesla start charging
* Tesla stop charging

The event text should be in the summary of the event. Repeated events are not yet supported.
