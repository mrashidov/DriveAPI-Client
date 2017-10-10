#!/usr/bin/python
# -*- coding: utf-8 -*-

# The above encoding declaration is required and the file must be saved as UTF-8

from __future__ import print_function
from tabulate import tabulate
from apiclient import errors
from apiclient import http
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
import httplib2
import os
import re
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import io
try:
    import argparse
    flags = \
        argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class DError(Exception):
    pass

home_dir = ''
credentials_dir = ".credentials"
client_cred = 'drive-python-quickstart.json'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    try:
        home_dir = os.getcwd()
        credential_dir = os.path.join(home_dir, '.credentials')
        print("Credentials path", credential_dir)
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        print("Got from store: ",credentials)
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(os.path.join(credential_dir,CLIENT_SECRET_FILE),
                                                  SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:

                # Needed only for compatibility with Python 2.6

                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials
    except:
        raise DError("Cant get get_credentials")

def getMetaFromId(service, objid):
    """Returns name of given objid"""
    try:
        file = service.files().get(fileId=objid).execute()
        return file
    except:
        print("Meta N/A: ",objid)
        raise DError("Can't get meta from id")

def remove(service,fileId):
    try:
        if fileId:
            service.files().delete(fileId=fileId).execute()
        else:
            print("File doesn't exist")
    except Exception as ex:
        print(ex)
        raise DError("Removing error")

def replace(
        service,
        name,
        newParent,
):
    """ Replace file to another folder"""
    try:
        #Obtain id's of file and folder
        file_id = getId(service,name)
        folder_id = getId(service,newParent)
        if not file_id or not folder_id: #If any of id's is not found return (nothing to do)
            return
        # Retrieve the existing parents to remove
        file = service.files().get(fileId=file_id,
                                   fields='parents').execute();
        previous_parents = ",".join(file.get('parents'))
        # Move the file to the new folder
        file = service.files().update(fileId=file_id,
                                      addParents=folder_id,
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()
    except:
        raise DError("Replace Error")

def upload(service, localFile, currentFolderId):
    """Upload localFile to Drive"""
    try:
        cloudFile = os.path.basename(localFile) #Name of cloudFile will be same as local file's
        file_metadata = {'name': cloudFile} #Fulfill metadata for request
        media = MediaFileUpload(localFile) #Contents of file
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute() #Upload
        fileId = file.get('id')
        replace(service, cloudFile, currentFolderId)
    except:
        raise DError("Upload error")

def download(service, fileId, filename):
    """Download file with given fileId to filename"""
    try:
        #Request downloading
        request = service.files().get_media(fileId=fileId)
        fh = io.BytesIO() #Buffer
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            (status, done) = downloader.next_chunk()
        file = open(filename, 'wb') #Writing buffer to file
        file.write(fh.getvalue())
        fh.close()
        print('Download %d%%.' % int(status.progress() * 100))
    except:
        raise DError("Download error")
def getAllElements(service):
    """Returns list of records about files"""
    try:
        print("Getting all elements: ")
        results = service.files().list(q="not trashed",
                                 fields='nextPageToken, files(id, name,mimeType,parents)'
                                 ).execute()
        items = results.get('files', [])
        return items
    except Exception as ex:
        #raise DError("Error in getAllElements"+str(ex))
        raise ex
def filterFromField(collection,field,value):
    """Filtering collection with field = value criteria"""
    #print("Filtering....")
    result = []
    for x in collection:
        if field in x.keys() and value in x[field]:
            result.append(x)
    #print("From filtering: ",result)
    return result 

def getContentsOfFolder(service,collection,folderId):
    """List files in given folder"""
    try:
        if folderId=="root":
            folderId = getRootId(service)
        items = filterFromField(collection,'parents',folderId)
        return list(items)
    except Exception as ex:
        raise DError(ex)

def getTreeOfFolders(service,collection,name,folderId = 'root',node={}):
    """Returns tree of folders as a dictionary. (Exmple {'id':root, 'name'='root', 'hasDescendants':True, descendants':[{id...}]})"""
    print("Getting tree structure: ")
    node['id'] = folderId
    node['name'] = name
    node['descendants'] = []
    node['hasDescendants'] = False
    if folderId == 'root': #Resolving "root" alias
        folderId = getRootId(service)
    items = getContentsOfFolder(service,collection,folderId)  #get contents of current file
    for file in items:
        if file['mimeType']=='application/vnd.google-apps.folder': #if file type is google drive api, add to descendants
            node['hasDescendants'] = True
            node['descendants'].append(getTreeOfFolders(service,collection,file['name'],file['id'],{})) #do same with descendants
    return node

def getRootId(service):
    """Returns rootId for current session user"""
    about = getMetaFromId(service,'root')
    return about['id']
    
def getService():
    """Returns service object"""
    try:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)
        return service
    except:
        raise DError("Failed to get service")
