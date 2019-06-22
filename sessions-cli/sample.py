#!python3
import sys
import argparse
import requests
import urllib3

from panopto_sessions import PanoptoSessions

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', 'common')))
from panopto_oauth2 import PanoptoOAuth2

def parse_argument():
    parser = argparse.ArgumentParser(description='Sample of Folders API')
    parser.add_argument('--server', dest='server', required=True, help='Server name as FQDN')
    parser.add_argument('--client-id', dest='client_id', required=True, help='Client ID of OAuth2 client')
    parser.add_argument('--client-secret', dest='client_secret', required=True, help='Client Secret of OAuth2 client')
    parser.add_argument('--session-id', dest='session_id', required=False, help='The ID of the session to start with.')
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

    # Load Sessions API logic
    sessions = PanoptoSessions(args.server, not args.skip_verify, oauth2)
    
    if args.session_id is not None:
        current_session_id = args.session_id
    else:
        current_session_id = None
    
    # Load the initial session (if any) and display the options menu
    while True:
        print('----------------------------')
        if current_session_id is not None:
            session = get_and_display_session(sessions, current_session_id)
            
        current_session_id = process_selection(sessions, current_session_id)

    
def get_and_display_session(sessions, session_id):
    '''
    Returning session object that is returned by API.
    None if it is top level folder.
    '''
    print()
    print('Session:')
    session = sessions.get_session(session_id)
    
    print('  Name: {0}'. format(session['Name']))
    print('  Id: {0}'. format(session['Id']))
    print('  Folder Id: {0}'. format(session['Folder']))
    print('  ViewerUrl: {0}'. format(session['Urls']['ViewerUrl']))
    print('  EmbedUrl: {0}'. format(session['Urls']['EmbedUrl']))
    print('  ShareSettingsUrl: {0}'. format(session['Urls']['ShareSettingsUrl']))
    print('  DownloadUrl: {0}'. format(session['Urls']['DownloadUrl']))
    print('  CaptionDownloadUrl: {0}'. format(session['Urls']['CaptionDownloadUrl']))
    print('  EditorUrl: {0}'. format(session['Urls']['EditorUrl']))
    print('  CreatedBy: {0}'. format(session['CreatedBy']['Username']))
    print('  StartTime: {0}'. format(session['StartTime']))
    print('  Description: {0}'. format(session['Description']))
    return session

def process_selection(sessions, current_session_id):

    new_session_id = current_session_id
    print()
    if current_session_id is not None:
        print('[R] Rename this session')
        print('[D] Delete this session')
    print('[S] Search sessions')
    print()
    selection = input('Enter a command: ')

    if selection.lower() == 'r' and current_session_id is not None:
        rename_session(sessions, current_session_id)
    elif selection.lower() == 'd' and current_session_id is not None:
        if delete_session(sessions, current_session_id):
            new_session_id = None
    elif selection.lower() == 's':
        result = search_sessions(sessions)
        if result is not None:
            new_session_id = result
    else:
        print('Invalid command.')
    
    return new_session_id

def rename_session(sessions, session_id):
    new_name = input('Enter new name: ')
    return sessions.update_session_name(session_id, new_name)
    
def delete_session(sessions, session_id):
    return sessions.delete_session(session_id)

def search_sessions(sessions):
    query = input('Enter search keyword: ')
    entries = sessions.search_sessions(query)

    if len(entries) == 0:
        print('  No results.')
        return None

    for index in range(len(entries)):
        print('  [{0}]: {1}'.format(index, entries[index]['Name']))
    selection = input('Enter the number (or just enter to stay on the current session): ')
    
    new_session_id = None
    try:
        index = int(selection)
        if 0 <= index < len(entries):
            new_session_id = entries[index]['Id']
    except:
        pass

    return new_session_id
    
if __name__ == '__main__':
    main()
