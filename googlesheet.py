#from __future__ import print_function
import httplib2
import argparse

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

class GoogleSheet():
    def __init__(self):
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

        # Obtain Google credentials
        store = Storage('credential.json')
        try:
            credentials = store.get()
        except KeyError:
            credentials = None

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', 'https://www.googleapis.com/auth/spreadsheets.readonly')
            flow.user_agent = 'Tesla Gadget'
            credentials = tools.run_flow(flow, store, flags)

        # Make connection with the Google sheet
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
        self.service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    def get_range(self, spreadsheetId, rangeName):
        return self.service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute().get('values', [])
