from __future__ import print_function
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from oauth2client.service_account import ServiceAccountCredentials

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


### Created from the sample Google Sheet API tutorial.
def main():
    
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # Use the Hackerdoor Service Account
    credentials = ServiceAccountCredentials.from_json_keyfile_name('./configs/hackerdoor-servicecredentials.json', scopes)
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http ,
        discoveryServiceUrl=discoveryUrl)

    # The Memberlist Google Doc
    spreadsheetId = '1sakXpA_H5vs3_addWkrPbccDVcoxFx13yDpudYlqInM'

    rangeName = 'MasterMemberList!B3:C'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Status:')
        for row in values:
            print('%s, %s' % (row[0], row[1]))


if __name__ == '__main__':
    main()