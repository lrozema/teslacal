#
# teslakmreg
#
# Have the rides using your Tesla registered to a Google sheet
# 
# (c) 2019 by Lourens Rozema
# 

from ConfigParser import RawConfigParser
from googlesheet import GoogleSheet
from geopy.geocoders import Nominatim

import teslajson
import string
import shelve
import time
import sys


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


# Load the configuration
config = RawConfigParser()
config.read('teslacal.cfg')

# Connect to the Tesla cloud
c = teslajson.Connection(config.get('tesla', 'username'), config.get('tesla', 'password'))

# Filter the vehicles list based on VIN if specified
va = c.vehicles
vin = config.get('tesla', 'vin')
if vin is not None:
    va = [ v for v in va if v['vin'] == vin ]

# Make sure we did find a vehicle and then select the first
if not len(va):
    raise Exception("Tesla not found!")
v = va[0]

print "Tesla "+v['display_name']+" found!"
v.wake_up()

vehicle_state = v.data_request('vehicle_state')
drive_state = v.data_request('drive_state')

if 0:
    import json
    print json.dumps({'vehicle_state': vehicle_state, 'drive_state': drive_state})

odometer = float(vehicle_state['odometer']) * 1.60934
in_motion = vehicle_state['is_user_present'] == '?'

# Allow to overwrite driving data so that we can test the script
if len(sys.argv) > 2:
    # Manual driving
    odometer = float(sys.argv[1])
    in_motion = sys.argv[2] == 'driving'

    # Remove arguments
    sys.argv = sys.argv[:1]

# Get the current state
data = shelve.open('kmreg.db')

# Are we driving?
if in_motion:
    sys.exit(0)

# Did we not move?
if odometer != data.get('Beginstand', None):
    latitude = drive_state['latitude']
    longitude = drive_state['longitude']

    # Lookup current address
    geolocator = Nominatim(user_agent='Tesla KM registration')
    address = geolocator.reverse((latitude, longitude)).address

    # We moved, make a record
    data['Eindtijd'] = now()
    data['Eindstand'] = odometer
    data['Eind adres'] = address

    # Get the spreadsheet id
    spreadsheet_id = config.get('google', 'spreadsheetId')

    # Name of the sheet to write to
    sheet_name = 'Rittenregistratie'

    gs = GoogleSheet()
    rows = iter(enumerate(gs.get_range(spreadsheet_id, sheet_name + '!A1:L20'), 1))

    # Find the row containing the header
    for idx, row in rows:
        if 'Begintijd' in row:
            break

    # Worst case number of columns per row
    number_of_columns = len(row)

    # Find positions for registration columns
    columns = {k: idx for idx, k in enumerate(row)}

    # Rest of the rows contain data, find the first empty row
    for idx, row in rows:
        if not row[columns['Beginstand']] and not row[columns['Eindstand']]:
            break

    gs.set_fields(spreadsheet_id, {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {
                'range': string.ascii_uppercase[columns[k]] + str(idx),
                'values': [[v]],
            } for k, v in data.items()
        ],
    })

    # We don't want to geolocate too often, so keep this here
    data['Begin adres'] = address

# Keep track of a new start time
data['Begintijd'] = now()
data['Beginstand'] = odometer

data.close()
