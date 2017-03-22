# gdrive-backup.py
#
# 3/22/17 by Chris Boyke
#
#
# For downloading / exporting files, I mostly followed the download instructions located here, except that the
# Python code sample there didn't work (others have reported this error as well), so I'm following a slightly
# different approach.
#
# https://developers.google.com/drive/v3/web/manage-downloads
#
# And last, for a complete list of mime types, see here:
#
#    https://developers.google.com/drive/v3/web/mime-types
#
#

from __future__ import print_function
import httplib2
import os
import os.path
import re
import io
from datetime import datetime

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

# Root destination folder (MUST EXIST)
dest_root = '/Users/chris/backup/gdrive';

CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def download_file(item,mime_type,ext):

    name = item['name'].replace('/','_')
    print("Downloading " + item['name'] + ' to ' + os.getcwd())

    request = service.files().export_media(fileId=item['id'],mimeType=mime_type)
    response = request.execute()
    
    fh = io.FileIO(name+'.'+ext,mode='wb')
    fh.write(response);
    fh.close();
    
    #downloader = MediaIoBaseDownload(fh, request)
    #done = False
    #while done is False:
    #    status, done = downloader.next_chunk()
    #    print(status.progress() )
    return



def get_files_or_folders(items,indent,dest):
    for item in items:
        
    
        if not item['trashed']:
            name = item['name'].replace('/','_')
            #print(' ' * indent + item['name'])
            mime_type = item['mimeType']
            if mime_type == 'application/vnd.google-apps.folder':
                full_path=dest+'/'+name;
                if not os.path.isdir(full_path):
                    print("Creating: " + full_path)
                    os.mkdir(full_path)

                os.chdir(full_path)
                
                items = get_children(item['id'])
                get_files_or_folders(items,indent+4,full_path)


            elif item['modifiedTime'] > timestamp:
                
                    #print(name + ' has been modified since ' + timestamp + ' -- downloading')
                    if mime_type == 'application/vnd.google-apps.document':
                        #print(' ' * indent + item['name'] + ' is a Google Document')
                        download_file(item,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','docx')
                    
                    elif mime_type == 'application/vnd.google-apps.spreadsheet':
                        #print(' ' * indent + item['name'] + ' is a Google Spreadsheet')
                        download_file(item,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','xlsx')
                    else:
                        #print(' ' * indent + item['name'] + ' is a file')
                        if int(item['size']) < 100000000:
                            request = service.files().get_media(fileId=item['id'])
                            response = request.execute()
                            fh = io.FileIO(name,mode='wb')
                            fh.write(response);
                            fh.close();
                        else:
                            print(' ' * indent + item['name'] + ' --file too large' )

            else:
                x=1
                #print(' ' * indent + item['name'] + ' --not modified' )

    return

# Get a list of files with parent ID
def get_children(id):
    results = service.files().list(q="'" + id + "' in parents",fields="files(id, name, size, modifiedTime, trashed, mimeType)").execute()
    items = results.get('files', [])
    return items


def main():
    
    global timestamp
    global service
    dest=dest_root
    timestamp_filename = dest + '/backup-timestamp'
    if(os.path.isfile(timestamp_filename)):
        fh = open(dest + '/backup-timestamp','r')
        timestamp = fh.readline();
        print("Last run: " + timestamp);
        fh.close()
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    

    items = get_children('root')
    get_files_or_folders(items,0,dest)

    fh = open(dest + '/backup-timestamp','w')
    fh.write(datetime.utcnow().isoformat())
    fh.close()

if __name__ == '__main__':
    main()




