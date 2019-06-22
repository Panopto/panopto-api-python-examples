#!python3
import sys
import argparse
import requests
import urllib3

from panopto_folders import PanoptoFolders

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', 'common')))
from panopto_oauth2 import PanoptoOAuth2

# Top level folder is represented by zero GUID.
# However, it is not the real folder and some API beahves differently than actual folder.
GUID_TOPLEVEL = '00000000-0000-0000-0000-000000000000'

def parse_argument():
    parser = argparse.ArgumentParser(description='Sample of Folders API')
    parser.add_argument('--server', dest='server', required=True, help='Server name as FQDN')
    parser.add_argument('--client-id', dest='client_id', required=True, help='Client ID of OAuth2 client')
    parser.add_argument('--client-secret', dest='client_secret', required=True, help='Client Secret of OAuth2 client')
    parser.add_argument('--skip-verify', dest='skip_verify', action='store_true', required=False, help='Skip SSL certificate verification. (Never apply to the production code)')
    return parser.parse_args()

def main():
    args = parse_argument()

    if args.skip_verify:
        # This line is needed to suppress annoying warning message.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Use requests module's Session object in this example.
    # ref. https://2.python-requests.org/en/master/user/advanced/#session-objects
    requests_session = requests.Session()
    requests_session.verify = not args.skip_verify
    
    # Load OAuth2 logic
    oauth2 = PanoptoOAuth2(args.server, args.client_id, args.client_secret, not args.skip_verify)

    # Load Folders API logic
    folders = PanoptoFolders(args.server, not args.skip_verify, oauth2)
    
    current_folder_id = GUID_TOPLEVEL
    
    while True:
        print('----------------------------')
        current_folder = get_and_display_folder(folders, current_folder_id)
        sub_folders = get_and_display_sub_folders(folders, current_folder_id)
        current_folder_id = process_selection(folders, current_folder, sub_folders)

    
def get_and_display_folder(folders, folder_id):
    '''
    Returning folder object that is returned by API.
    None if it is top level folder.
    '''
    print()
    print('Folder:')
    if folder_id == GUID_TOPLEVEL:
        print('  Top level folder (no detail informaiton is available)')
        return None

    folder = folders.get_folder(folder_id)
    print('  Name: {0}'. format(folder['Name']))
    print('  Id: {0}'. format(folder['Id']))
    if folder['ParentFolder'] is None:
        print('  Parent Folder: Top level folder')
    else:
        print('  Parent Folder: {0}'. format(folder['ParentFolder']['Name']))
    print('  Folder URL: {0}'. format(folder['Urls']['FolderUrl']))
    print('  Embed URL: {0}'. format(folder['Urls']['EmbedUrl']))
    print('  Share settings URL: {0}'. format(folder['Urls']['ShareSettingsUrl']))
    return folder

def get_and_display_sub_folders(folders, current_folder_id):
    print()
    print('Sub Folders:')
    children = folders.get_children(current_folder_id)

    # returning object is the dictionary, key (integer) and folder's ID (UUID)
    result = {}
    key = 0
    for entry in children:
        result[key] = entry['Id']
        print('  [{0}]: {1}'.format(key, entry['Name']))
        key += 1
    
    return result

def process_selection(folders, current_folder, sub_folders):
    if current_folder is None:
        new_folder_id = GUID_TOPLEVEL
        parent_folder_id = GUID_TOPLEVEL
    else:
        new_folder_id = current_folder['Id']
        if current_folder['ParentFolder'] is None:
            parent_folder_id = GUID_TOPLEVEL
        else:
            parent_folder_id = current_folder['ParentFolder']['Id']

    print()
    print('[P] Go to parent')
    print('[R] Rename this folder')
    print('[D] Delete this folder')
    print('[S] Search folders')
    print('[L] List sessions in the folder')
    print()
    selection = input('Enter the command (select number to move folder): ')

    try:
        key = int(selection)
        if sub_folders[key]:
            return sub_folders[key]
    except:
        pass # selection is not a number, fall through

    if selection.lower() == 'p':
        new_folder_id = parent_folder_id
    elif selection.lower() == 'r' and current_folder is not None:
        rename_folder(folders, current_folder)
    elif selection.lower() == 'd' and current_folder is not None:
        if delete_folder(folders, current_folder):
            new_folder_id = parent_folder_id
    elif selection.lower() == 's':
        result = search_folder(folders)
        if result is not None:
            new_folder_id = result
    elif selection.lower() == 'l' and current_folder is not None:
        list_sessions(folders, current_folder)
    else:
        print('Invalid command.')
    
    return new_folder_id

def rename_folder(folders, folder):
    new_name = input('Enter new name: ')
    return folders.update_folder_name(folder['Id'], new_name)
    
def delete_folder(folders, folder):
    return folders.delete_folder(folder['Id'])

def search_folder(folders):
    query = input('Enter search keyword: ')
    entries = folders.search_folders(query)

    if len(entries) == 0:
        print('  No hit.')
        return None

    for index in range(len(entries)):
        print('  [{0}]: {1}'.format(index, entries[index]['Name']))
    selection = input('Enter the number (or just enter to stay current): ')
    
    new_folder_id = None
    try:
        index = int(selection)
        if 0 <= index < len(entries):
            new_folder_id = entries[index]['Id']
    except:
        pass

    return new_folder_id

def list_sessions(folders, folder):
    print('Sessions in the folder:')
    for entry in folders.get_sessions(folder['Id']):
        print('  {0}: {1}'.format(entry['Id'], entry['Name']))
    
if __name__ == '__main__':
    main()
