#
# teslakmreg
#
# Have the rides using your Tesla registered to a Google sheet
# 
# (c) 2019 by Lourens Rozema
# 

from ConfigParser import RawConfigParser
from googlesheet import GoogleSheet

import teslajson
import string

# Load the configuration
config = RawConfigParser()
config.read('teslacal.cfg')

# Get the spreadsheet id
spreadsheet_id = config.get('google', 'spreadsheetId')

# Name of the sheet to write to
sheet_name = 'Rittenregistratie'

gs = GoogleSheet()
rows = iter(enumerate(gs.get_range(spreadsheet_id, sheet_name + '!A1:L20'), 1))

# Find the row containing the header
for idx, row in rows:
    if 'Begin tijd' in row:
        break

# Worst case number of columns per row
number_of_columns = len(row)

# Find positions for registration columns
columns = {k: idx for idx, k in enumerate(row)}

# Rest of the rows contain data, find the first empty row
for idx, row in rows:
    if not row[columns['Beginstand']] and not row[columns['Eindstand']]:
        break

# Data to write to the new row
data = {
    'Beginstand': 123,
    'Eindstand': 456,
}

gs.set_fields(spreadsheet_id, {
    'valueInputOption': 'USER_ENTERED',
    'data': [
        {
            'range': string.ascii_uppercase[columns[k]] + str(idx),
            'values': [[v]],
        } for k, v in data.items()
    ],
})

raise Exception()

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
import json
print json.dumps(v.data_request('vehicle_state'))


