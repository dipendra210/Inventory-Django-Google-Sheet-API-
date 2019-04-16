from pprint import pprint

from googleapiclient import discovery

from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

store = file.Storage('token.json')

creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)

