#!python3
import sys
import argparse
import requests
import urllib3
import time
from hashlib import sha256
from base64 import b64encode

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', 'common')))
from panopto_oauth2 import PanoptoOAuth2

def parse_argument():
    parser = argparse.ArgumentParser(description='Sample of Authorization for ID provider integration')
    parser.add_argument('--server', dest='server', required=True, help='Server name as FQDN')
    parser.add_argument('--client-id', dest='client_id', required=True, help='Client ID of OAuth2 client')
    parser.add_argument('--client-secret', dest='client_secret', required=True, help='Client Secret of OAuth2 client')
    parser.add_argument('--application-key', dest='application_key', required=True, help='Application Key of ID provider')
    parser.add_argument('--username', dest='username', required=True, help='Username for OAuth2 Resource Owner Grant')
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

    # Initial authorization
    authorization(requests_session, oauth2, args.application_key, args.username)

    # Call Panopto API (getting sub-folders from top level folder) repeatedly
    folder_id = '00000000-0000-0000-0000-000000000000' # represent top level folder
    while True:
        print('Calling GET /api/v1/folders/{0}/children endpoint'.format(folder_id))
        url = 'https://{0}/Panopto/api/v1/folders/{1}/children'.format(args.server, folder_id)
        resp = requests_session.get(url = url)
        if inspect_response_is_unauthorized(resp):
            # Re-authorization
            authorization(requests_session, oauth2, args.application_key, args.username)
            # Re-try now
            continue
        data = resp.json() # parse JSON format response
        results = data['Results']
        print(results)
        for folder in results:
            print('  {0}: {1}'.format(folder['Id'], folder['Name']))
        time.sleep(60)

def authorization(requests_session, oauth2, application_key, username):
    # Generate authentication code
    authcode = b64encode(sha256((username.lower() + '|' + application_key.lower()).encode('utf-8')).digest())
    # Go through authorization
    access_token = oauth2.get_access_token_resource_owner_grant(username, authcode)
    # Set the token as the header of requests
    requests_session.headers.update({'Authorization': 'Bearer ' + access_token})

def inspect_response_is_unauthorized(response):
    '''
    Inspect the response of a requets' call, and return True if the response was Unauthorized.
    An exception is thrown at other error responses.
    Reference: https://stackoverflow.com/a/24519419
    '''
    if response.status_code // 100 == 2:
        # Success on 2xx response.
        return False
        
    if response.status_code == requests.codes.unauthorized:
        print('Unauthorized. Access token is invalid.')
        return True

    # Throw unhandled cases.
    response.raise_for_status()

if __name__ == '__main__':
    main()
