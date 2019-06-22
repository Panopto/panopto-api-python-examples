#!python3
import os
import time
import json
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient  # specific to Resource Owner Grant
import pickle
import pprint
import webbrowser
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingTCPServer

# This code uses this local URL as redirect target for Authorization Code Grant (Server-side Web Application)
REDIRECT_URL = 'http://localhost:9127/redirect'
REDIRECT_PORT = 9127

# Typical scope for accessing Panopto API.
DEFAULT_SCOPE = ('openid', 'api')

class PanoptoOAuth2():
    def __init__(self, server, client_id, client_secret, ssl_verify):
        self.client_id = client_id
        self.client_secret = client_secret
        self.ssl_verify = ssl_verify
        
        # Create URI from
        self.authorization_endpoint = 'https://{0}/Panopto/oauth2/connect/authorize'.format(server)
        self.access_token_endpoint = 'https://{0}/Panopto/oauth2/connect/token'.format(server)

        # Create cache file name to store the refresh token. Use server & client ID combination.
        self.cache_file = 'token_{0}_{1}.cache'.format(server, client_id)

        # Make oauthlib library accept non-HTTPS redirection.
        # This should not be applied if the redirect is hosted by actual server (not localhost).
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    def get_access_token_authorization_code_grant(self):
        '''
        Get OAuth2 access token by Authorization Code Grant (Server-side Web Application).
        
        This method initially tries to get a new access token from refresh token.
        
        If refresh token is not available or does not work, proceed to new authorization flow:
         1. To launch the browser to navigate authorization URL.
         2. To start temporary HTTP server at localhost:REDIRECT_PORT and block.
         3. When the redirect is received, HTTP server exits.
         4. To get access token and refresh token with given authentication code by redirection.
         5. Save the token object, which includes refersh_token, for later refrehsh operation.
        '''
        
        # First, try getting a new access token from refesh token.
        access_token = self.__get_refreshed_access_token()
        if access_token:
            return access_token

        # Then, fallback to the full autorization path. Offline access scope is needed to get refresh token.
        scope = list(DEFAULT_SCOPE) + ['offline_access']
        session = OAuth2Session(self.client_id, scope = scope, redirect_uri = REDIRECT_URL)
        session.verify = self.ssl_verify
        
        # Open the authorization page by the browser.
        authorization_url, state = session.authorization_url(self.authorization_endpoint)
        print()
        print('Opening the browser for authorization: {0}'.format(authorization_url))
        webbrowser.open_new_tab(authorization_url)

        # Launch HTTP server to receive the redirect after authorization.
        redirected_path = ''
        with RedirectTCPServer() as httpd:
            print('HTTP server started at port {0}. Waiting for redirect.'.format(REDIRECT_PORT))
            # Serve one request.
            httpd.handle_request()
            # The property may not be readable immediately. Wait until it becomes valid.
            while httpd.last_get_path is None:
                time.sleep(1)
            redirected_path = httpd.last_get_path

        print()
        print('Get a new access token with authorization code, which is provided as return path: {0}'.format(redirected_path))
        session.fetch_token(self.access_token_endpoint, client_secret = self.client_secret, authorization_response = redirected_path)
        self.__save_token_to_cache(session.token)

        return session.token['access_token']

    def __get_refreshed_access_token(self):
        '''
        Private method of the class.
        Get a new access token from refresh token.
        Save the updated token object, which includes refersh_token, for later refrehsh operation.
        Returning None if failing to get the new access token with any reason.
        '''
        try:
            print()
            print('Read cached token from {0}'.format(self.cache_file))
            with open(self.cache_file, 'rb') as fr:
                token = pickle.load(fr)

            session = OAuth2Session(self.client_id, token = token)
            session.verify = self.ssl_verify

            print()
            print('Get a new access token by using saved refresh token.')
            extra = {'client_id': self.client_id, 'client_secret': self.client_secret}
            session.refresh_token(self.access_token_endpoint, **extra)
            self.__save_token_to_cache(session.token)

            return session.token['access_token']

        # Catch any failures (exceptions) and return with None.
        except Exception as e:
            print('Failed to refresh access token: ' + str(e))
            return None

    def __save_token_to_cache(self, token):
        '''
        Private method of the class.
        Save entire token object from oauthlib (not just refresh token).
        '''
        with open(self.cache_file, 'wb') as fw:
            pickle.dump(token, fw)
        print('OAuth2 flow provided the token below. Cache it to {0}'.format(self.cache_file))
        pprint.pprint(token, indent = 4)

    def get_access_token_resource_owner_grant(self, username, password):
        '''
        Get OAuth2 access token by Resource Owner Grant (User Based Server Application).
        '''
        session = OAuth2Session(client = LegacyApplicationClient(client_id = self.client_id))
        session.verify = self.ssl_verify

        # Retrieve access token
        print()
        print('Get a new access token with username and password.')
        scope = DEFAULT_SCOPE
        session.fetch_token(
            token_url = self.access_token_endpoint, scope = scope,
            client_id = self.client_id, client_secret = self.client_secret,
            username = username, password = password)

        print('OAuth2 flow provided the token below.')
        pprint.pprint(session.token, indent = 4)
        return session.token['access_token']


class RedirectTCPServer(ThreadingTCPServer):
    '''
    A helper class for Authorization Code Grant.
    Custom class of ThreadingTCPServer with RedirectHandler class as handler.
    last_get_path property is set whenever GET method is called by the handler.
    '''
    def __init__(self):
        # Class property, representing the path of the most recent GET call.
        self.last_get_path = None
        # Create an instance at REDIRECT_PORT with RedirectHandler class.
        super().__init__(('', REDIRECT_PORT), RedirectHandler)
        # Override the attribute of the server.
        self.allow_reuse_address = True


class RedirectHandler(BaseHTTPRequestHandler):
    '''
    A helper class for Authorization Code Grant.
    '''
    def do_GET(self):
        '''
        Handle a GET request. Set the path to the server's property.
        '''
        self.server.last_get_path = self.path
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<html><body><p>Authorization redirect was received. You may close this page.</p></body></html>'.encode('utf-8'))
        self.wfile.flush()
