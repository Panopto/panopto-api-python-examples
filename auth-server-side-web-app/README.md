# Authorization as Server-side Web Application
This sample demonstrates the authorization process as a Server-side Web Application.
It goes through authorization process, then calls 'get folder list' API as an example of accessing the Panopto REST API.

This is the most recommended way to get an access token for the Panopto API.
Most of authorization logic is in common code: [panopto_oauth2.py](../common/panopto_oauth2.py).

## Preparation
1. You need a Panopto user account. If you don't have one, ask your organization's Panopto administrator.
2. If you do not have Python 3 on your system, install the latest stable version from https://python.org
3. Install external modules for this application.
```
pip install requests oauthlib requests_oauthlib
```

## Setup API Client on Panopto server
1. Sign in to the Panopto web site
2. Click the System icon at the left-bottom corner.
3. Click API Clients
4. Click New
5. Enter arbitrary Client Name
6. Select Server-side Web Application type.
7. Enter ```https://localhost``` into CORS Origin URL.
8. Enter ```http://localhost:9127/redirect``` into Redirect URL.
9. The rest can be blank. Click "Create API Client" button.
10. Note the created Client ID and Client Secret.

## Run the sample
Type the following command.
```
python sample.py --server [Panopto server name] --client-id [Client ID] --client-secret [Client Secret]
```
This application brings up the sign-in screen on the browser for the first time. Go through the sign in process.
This application saves OAuth2 refresh token in a *.cache file, so later runs of this application do not require signing in.

This application displays the list of folders that are accessible by the user who signed in at the sign-in screen.
When this runs for more than an hour, which is the token expiration, it goes through the authorization again and retries.

## See also
Refer the top level [README.md](../README.md) for license, references, and additional notes.
