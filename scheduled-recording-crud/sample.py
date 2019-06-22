#!python3
import sys
import argparse
import requests
import urllib3
from urllib.parse import quote
import time
import datetime
import json

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', 'common')))
from panopto_oauth2 import PanoptoOAuth2

def parse_argument():
    parser = argparse.ArgumentParser(description='Sample of Authorization as Server-side Web Application')
    parser.add_argument('--server', dest='server', required=True, help='Server name as FQDN')
    parser.add_argument('--client-id', dest='client_id', required=True, help='Client ID of OAuth2 client')
    parser.add_argument('--client-secret', dest='client_secret', required=True, help='Client Secret of OAuth2 client')
    parser.add_argument('--skip-verify', dest='skip_verify', action='store_true', required=False, help='Skip SSL certificate verification. (Never apply to the production code)')
    parser.add_argument('--recorder-name', dest='recorder_name', required=True, help='Name of recorder to use')
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
    authorization(requests_session, oauth2)

    base_url = 'https://{0}/Panopto/api/v1/'.format(args.server)

    # Search for the remote recorder
    url = base_url + "remoteRecorders/search?searchQuery={0}".format(quote(args.recorder_name))
    print('Calling GET {0}'.format(url))
    resp = requests_session.get(url = url).json()
    if 'Results' not in resp:
        print("Recorder not found:\n{0}".format(resp))
        exit(-1)
    recorder = [rr for rr in resp['Results'] if rr['Name'] == args.recorder_name]
    if len(recorder) != 1:
        print("Recorder '{0}' not found:\n{1}".format(args.recorder_name, resp))
        exit(-1)
    recorder = recorder[0]

    # Create a SR
    ref_date = datetime.datetime.now() + datetime.timedelta(days=30)
    sr = {
        "Name": "Test Scheduled Recording",
        "Description": "SR for CRUD test",
        "StartTime": datetime.datetime(ref_date.year, ref_date.month, ref_date.day, 12, 0, 0).isoformat(),
        "EndTime": datetime.datetime(ref_date.year, ref_date.month, ref_date.day, 13, 0, 0).isoformat(),
        "FolderId": recorder['DefaultRecordingFolder']['Id'],
        'Recorders': [
            {
                'RemoteRecorderId': recorder['Id'],
                'SuppressPrimary': False,
                'SuppressSecondary': False,
            }
        ],
        'IsBroadcast': True,
    }
    url = base_url + "scheduledRecordings?resolveConflicts=false"
    print('Calling POST {0}'.format(url))
    create_resp = requests_session.post(url=url, json=sr).json()
    print("POST returned:\n" + json.dumps(create_resp, indent=2))
    session_id = create_resp['Id']

    # Read the SR back
    url = base_url + "scheduledRecordings/{0}".format(session_id)
    print('Calling GET {0}'.format(url))
    read_resp = requests_session.get(url=url).json()
    print("GET returned:\n" + json.dumps(read_resp, indent=2))

    # Update the SR
    sr = {
        'StartTime': datetime.datetime(ref_date.year, ref_date.month, ref_date.day, 13, 0, 0).isoformat(),
        'EndTime': datetime.datetime(ref_date.year, ref_date.month, ref_date.day, 14, 0, 0).isoformat(),
    }
    url = base_url + "scheduledRecordings/{0}".format(session_id)
    print('Calling PUT {0}'.format(url))
    update_resp = requests_session.put(url=url, json=sr).json()
    print("PUT returned:\n" + json.dumps(update_resp, indent=2))

    # Read the SR back again
    url = base_url + "scheduledRecordings/{0}".format(session_id)
    print('Calling GET {0}'.format(url))
    read_resp = requests_session.get(url=url).json()
    print("GET returned:\n" + json.dumps(read_resp, indent=2))

    # Delete the SR
    url = base_url + "scheduledRecordings/{0}".format(session_id)
    print('Calling DELETE {0}'.format(url))
    read_resp = requests_session.delete(url=url).json()
    print("DELETE returned:\n" + json.dumps(read_resp, indent=2))

def authorization(requests_session, oauth2):
    # Go through authorization
    access_token = oauth2.get_access_token_authorization_code_grant()
    # Set the token as the header of requests
    requests_session.headers.update({'Authorization': 'Bearer ' + access_token})

if __name__ == '__main__':
    main()
