#!python3
import requests
import urllib.parse
import time

class PanoptoSessions:
    def __init__(self, server, ssl_verify, oauth2):
        '''
        Constructor of sessions API handler instance.
        This goes through authorization step of the target server.
        '''
        self.server = server
        self.ssl_verify = ssl_verify
        self.oauth2 = oauth2

        # Use requests module's Session object in this example.
        # ref. https://2.python-requests.org/en/master/user/advanced/#session-objects
        self.requests_session = requests.Session()
        self.requests_session.verify = self.ssl_verify

        self.__setup_or_refresh_access_token()

    def __setup_or_refresh_access_token(self):
        '''
        This method invokes OAuth2 Authorization Code Grant authorization flow.
        It goes through browser UI for the first time.
        It refreshes the access token after that and no user interfaction is requetsed.
        This is called at the initialization of the class, as well as when 401 (Unauthorized) is returend.
        '''
        access_token = self.oauth2.get_access_token_authorization_code_grant()
        self.requests_session.headers.update({'Authorization': 'Bearer ' + access_token})

    def __inspect_response_is_retry_needed(self, response):
        '''
        Inspect the response of a requets' call.
        True indicates the retry needed, False indicates success. Othrwise an exception is thrown.
        Reference: https://stackoverflow.com/a/24519419

        This method detects 401 (Unauthorized), refresh the access token, and returns as "is retry needed".
        This method also detects 429 (Too many request) which means API throttling by the server. Wait a sec and return as "is retry needed".
        Prodcution code should handle other failure cases and errors as appropriate.
        '''
        if response.status_code // 100 == 2:
            # Success on 2xx response.
            return False
            
        if response.status_code == 401:
            print('Unauthorized. Refresh access token.')
            self.__setup_or_refresh_access_token()
            return True

        if response.status_code == 429:
            print('Too many requests. Wait one sec, and retry.')
            time.sleep(1)
            return True

        # Throw unhandled cases.
        response.raise_for_status()

    def get_session(self, session_id):
        '''
        Call GET /api/v1/sessions/{id} API and return the response
        '''
        while True:
            url = 'https://{0}/Panopto/api/v1/sessions/{1}'.format(self.server, session_id)
            resp = self.requests_session.get(url = url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def update_session_name(self, session_id, new_name):
        '''
        Call PUT /api/v1/sessions/{id} API to update the name
        Return True if it succeeds, False if it fails.
        '''
        try:
            while True:
                url = 'https://{0}/Panopto/api/v1/sessions/{1}'.format(self.server, session_id)
                payload = {'Name': new_name}
                headers = {'content-type': 'application/json'}
                resp = self.requests_session.put(url = url, json = payload, headers = headers)
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print('Rename failed. {0}'.format(e))
            return False

    def delete_session(self, session_id):
        '''
        Call DELETE /api/v1/sessions/{id} API to delete a session
        Return True if it succeeds, False if it fails.
        '''
        try:
            while True:
                url = 'https://{0}/Panopto/api/v1/sessions/{1}'.format(self.server, session_id)
                resp = self.requests_session.delete(url = url)
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print('Deletion failed. {0}'.format(e))
            return False

    def search_sessions(self, query):
        '''
        Call GET /api/v1/sessions/search API and return the list of entries.
        '''
        result = []
        page_number = 0
        while True:
            url = 'https://{0}/Panopto/api/v1/sessions/search?searchQuery={1}&pageNumber={2}'.format(
                self.server, urllib.parse.quote_plus(query), page_number)
            resp = self.requests_session.get(url = url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            entries = data['Results']
            if len(entries) == 0:
                break
            for entry in entries:
                result.append(entry)
            page_number += 1
        return result
